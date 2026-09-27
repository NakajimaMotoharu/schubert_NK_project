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
  private final InspectorUnitSnapshot.Target target;

  public InspectorUnitProbe() {
    this(new NativeReader(), InspectorUnitSnapshot.Target.INSPECTOR);
  }

  public static InspectorUnitProbe forTarget(InspectorUnitSnapshot.Target target) {
    return new InspectorUnitProbe(NativeReader.forTarget(target), target);
  }

  InspectorUnitProbe(Reader reader) {
    this(reader, InspectorUnitSnapshot.Target.INSPECTOR);
  }

  InspectorUnitProbe(Reader reader, InspectorUnitSnapshot.Target target) {
    this.reader = Objects.requireNonNull(reader, "unit reader");
    this.target = Objects.requireNonNull(target, "fixed Unit target");
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
      return InspectorUnitSnapshot.parse(bytes, target);
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
    private final InspectorUnitSnapshot.Target target;

    NativeReader() {
      this(
          command -> SystemctlStateSource.NativeProcess.builder(command).start(),
          InspectorUnitSnapshot.Target.INSPECTOR);
    }

    static NativeReader forTarget(InspectorUnitSnapshot.Target target) {
      return new NativeReader(
          command -> SystemctlStateSource.NativeProcess.builder(command).start(), target);
    }

    NativeReader(Start start) {
      this(start, InspectorUnitSnapshot.Target.INSPECTOR);
    }

    NativeReader(Start start, InspectorUnitSnapshot.Target target) {
      this.start = Objects.requireNonNull(start, "query start");
      this.target = Objects.requireNonNull(target, "fixed Unit target");
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
              target.unit()),
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
              target.unit()),
          9);
    }

    private byte[] execute(List<String> command, int limit) {
      interrupted();
      // Keep the delivered array reachable even when a later scope close fails.
      byte[][] bytes = {new byte[0]};
      try {
        var owned =
            new QueryProcess(Objects.requireNonNull(start.execute(command), "query process"));
        ProcessResourceScope.use(
            owned::close,
            () -> {
              var output = new SafeStream<>(owned.process.getInputStream());
              ProcessResourceScope.use(
                  output::finish,
                  () -> {
                    var input = new SafeStream<>(owned.process.getOutputStream());
                    ProcessResourceScope.use(
                        input::finish,
                        () -> {
                          var error = new SafeStream<>(owned.process.getErrorStream());
                          ProcessResourceScope.use(
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
