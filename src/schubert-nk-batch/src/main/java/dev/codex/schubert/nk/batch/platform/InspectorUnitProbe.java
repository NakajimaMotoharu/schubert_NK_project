package dev.codex.schubert.nk.batch.platform;

import java.io.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed read-only systemd observations. Caller owns OS/run/config lifetime and startup correlation.
 * NK-OPS-001/OPS009/UI251/SS341 7.4/343; SSC060/PG167; UNIT009..016.
 */
@NullMarked
public final class InspectorUnitProbe {
  interface Reader {
    byte[] readState() throws IOException;

    byte[] readProcesses() throws IOException;
  }

  private final Reader reader;

  public InspectorUnitProbe() {
    this(new NativeReader());
  }

  InspectorUnitProbe(Reader reader) {
    this.reader = Objects.requireNonNull(reader, "unit reader");
  }

  public InspectorUnitSnapshot read() {
    interrupted();
    byte[] bytes;
    try {
      bytes = Objects.requireNonNull(reader.readState(), "unit bytes");
    } catch (IOException failure) {
      throw new StopGateException(StopGateFailure.COMMAND_FAILURE);
    }
    try {
      interrupted();
      return InspectorUnitSnapshot.parse(bytes);
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  public Optional<InspectorUnitSnapshot> quiescent() {
    var before = read();
    if (!before.quiescent()) return Optional.empty();
    interrupted();
    byte[] processes;
    try {
      processes = Objects.requireNonNull(reader.readProcesses(), "process bytes");
    } catch (IOException failure) {
      throw new StopGateException(StopGateFailure.COMMAND_FAILURE);
    }
    boolean empty;
    try {
      interrupted();
      empty = Arrays.equals(processes, new byte[] {'a', '(', 's', 'u', 's', ')', ' ', '0', '\n'});
    } finally {
      Arrays.fill(processes, (byte) 0);
    }
    if (!empty) return Optional.empty();
    var after = read();
    boolean stable = before.matches(after);
    interrupted();
    return stable ? Optional.of(after) : Optional.empty();
  }

  public OptionalInt completionAfter(Optional<UUID> previous) {
    Objects.requireNonNull(previous, "previous invocation");
    var state = quiescent();
    OptionalInt result =
        state.isPresent() ? state.orElseThrow().receiptAfter(previous) : OptionalInt.empty();
    interrupted();
    return result;
  }

  private static void interrupted() {
    if (Thread.currentThread().isInterrupted())
      throw new StopGateException(StopGateFailure.INTERRUPTED);
  }

  static final class NativeReader implements Reader {
    @FunctionalInterface
    interface Start {
      Process execute(List<String> command) throws IOException;
    }

    private final Start start;

    NativeReader() {
      this(command -> SystemctlStateSource.NativeProcess.builder(command).start());
    }

    NativeReader(Start start) {
      this.start = Objects.requireNonNull(start, "query start");
    }

    @Override
    public byte[] readState() {
      return execute(
          List.of(
              "/usr/bin/systemctl",
              "--system",
              "--no-pager",
              "--no-ask-password",
              "show",
              "--property=" + InspectorUnitSnapshot.PROPERTIES,
              InspectorUnitSnapshot.UNIT),
          2048);
    }

    @Override
    public byte[] readProcesses() {
      return execute(
          List.of(
              "/usr/bin/busctl",
              "--system",
              "--timeout=5s",
              "--no-pager",
              "call",
              "org.freedesktop.systemd1",
              "/org/freedesktop/systemd1",
              "org.freedesktop.systemd1.Manager",
              "GetUnitProcesses",
              "s",
              InspectorUnitSnapshot.UNIT),
          9);
    }

    private byte[] execute(List<String> command, int limit) {
      interrupted();
      // Keep the delivered array reachable even when a later scope close fails.
      byte[][] bytes = {new byte[0]};
      try {
        var owned =
            new QueryProcess(Objects.requireNonNull(start.execute(command), "query process"));
        scope(
            owned::close,
            () -> {
              var output = new SafeStream<>(owned.process.getInputStream());
              scope(
                  output::finish,
                  () -> {
                    var input = new SafeStream<>(owned.process.getOutputStream());
                    scope(
                        input::finish,
                        () -> {
                          var error = new SafeStream<>(owned.process.getErrorStream());
                          scope(
                              error::finish,
                              () -> {
                                // Neither query accepts stdin. Signal EOF and close discarded
                                // stderr before waiting.
                                input.finish();
                                error.finish();
                                if (!owned.process.waitFor(5, TimeUnit.SECONDS))
                                  throw new StopGateException(StopGateFailure.TIMEOUT);
                                interrupted();
                                if (owned.process.exitValue() != 0)
                                  throw new StopGateException(StopGateFailure.COMMAND_FAILURE);
                                bytes[0] =
                                    Objects.requireNonNull(
                                        output.resource.readNBytes(limit + 1), "query output");
                                if (bytes[0].length > limit)
                                  throw new StopGateException(StopGateFailure.MALFORMED_STATE);
                              });
                        });
                  });
            });
        interrupted();
        return bytes[0];
      } catch (StopGateException failure) {
        Arrays.fill(bytes[0], (byte) 0);
        throw new StopGateException(failure.reason());
      } catch (InterruptedException failure) {
        Arrays.fill(bytes[0], (byte) 0);
        Thread.currentThread().interrupt();
        throw new StopGateException(StopGateFailure.INTERRUPTED);
      } catch (IOException failure) {
        Arrays.fill(bytes[0], (byte) 0);
        throw new StopGateException(StopGateFailure.COMMAND_FAILURE);
      } catch (RuntimeException | Error failure) {
        Arrays.fill(bytes[0], (byte) 0);
        throw failure;
      }
    }
  }

  @FunctionalInterface
  private interface QueryWork {
    void run() throws IOException, InterruptedException;
  }

  // SSC063/BUG195: fixed stop diagnostics, not raw suppressed process/stream failures.
  private static void scope(Runnable release, QueryWork work)
      throws IOException, InterruptedException {
    try {
      work.run();
    } catch (IOException | InterruptedException | RuntimeException | Error primary) {
      try {
        release.run();
      } catch (RuntimeException | Error cleanup) {
        if ((primary instanceof IOException
                || primary instanceof InterruptedException
                || primary instanceof StopGateException)
            && !(cleanup instanceof StopGateException)) {
          // Preserve cancellation even when an unknown cleanup must take precedence.
          if (primary instanceof InterruptedException) Thread.currentThread().interrupt();
          throw cleanup;
        }
        primary.addSuppressed(new StopGateException(StopGateFailure.COMMAND_FAILURE));
      }
      throw primary;
    }
    release.run();
  }

  private static final class SafeStream<T extends Closeable> {
    private final T resource;
    private boolean closed;

    SafeStream(T resource) {
      this.resource = Objects.requireNonNull(resource, "query stream");
    }

    // BUG187/YKT147: explicit early EOF/discard; scope fallback shares the one-close state.
    void finish() {
      if (closed) return;
      closed = true; // A failed native close is not retried against an uncertain descriptor.
      try {
        resource.close();
      } catch (IOException failure) {
        throw new StopGateException(StopGateFailure.COMMAND_FAILURE);
      }
    }
  }

  private static final class QueryProcess implements AutoCloseable {
    private final Process process;

    QueryProcess(Process process) {
      this.process = process;
    }

    @Override
    public void close() {
      if (process.isAlive()) process.destroy();
    }
  }
}
