package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.Closeable;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

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
    private final java.util.function.LongSupplier nanoTime;

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
      this(start, target, System::nanoTime);
    }

    // Internal monotonic PT port only; native binding always fixes System.nanoTime, no config
    // override.
    NativeReader(
        Start start,
        InspectorUnitSnapshot.Target target,
        java.util.function.LongSupplier nanoTime) {
      this.start = Objects.requireNonNull(start, "query start");
      this.target = Objects.requireNonNull(target, "fixed Unit target");
      this.nanoTime = Objects.requireNonNull(nanoTime, "query monotonic clock");
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

    // SSC093: package-only reuse for the fixed backup placement projection, no public selector.
    /**
     * SSC125: bounded journal output is drained concurrently, never wait-before-read a full pipe.
     */
    byte[] executeStreaming(List<String> command, int limit, long remainingNanos) {
      interrupted();
      if (limit < 1 || remainingNanos <= 0) throw new StopGateException(StopGateFailure.TIMEOUT);
      byte[][] bytes = {new byte[0]};
      long began = nanoTime.getAsLong();
      long timeout = Math.min(TimeUnit.SECONDS.toNanos(5), remainingNanos);
      try {
        ProcessResourceScope.acquire(
            () -> new QueryProcess(() -> start.execute(command)),
            QueryProcess::close,
            owned -> {
              var process = owned.required();
              ProcessResourceScope.acquire(
                  () -> new SafeStream<java.io.InputStream>(process::getInputStream),
                  SafeStream::finish,
                  output -> {
                    var stdout = output.required();
                    ProcessResourceScope.acquire(
                        () -> new SafeStream<java.io.OutputStream>(process::getOutputStream),
                        SafeStream::finish,
                        input -> {
                          input.required();
                          ProcessResourceScope.acquire(
                              () -> new SafeStream<java.io.InputStream>(process::getErrorStream),
                              SafeStream::finish,
                              error -> {
                                error.required();
                                input.finish();
                                error.finish();
                                var drain =
                                    new java.util.concurrent.FutureTask<byte[]>(
                                        () -> {
                                          bytes[0] =
                                              Objects.requireNonNull(
                                                  stdout.readNBytes(limit + 1), "journal bytes");
                                          return bytes[0];
                                        });
                                var reader = Thread.startVirtualThread(drain);
                                try {
                                  long left = timeout - (nanoTime.getAsLong() - began);
                                  if (left <= 0 || !process.waitFor(left, TimeUnit.NANOSECONDS))
                                    throw new StopGateException(StopGateFailure.TIMEOUT);
                                  interrupted();
                                  if (process.exitValue() != 0)
                                    throw new StopGateException(StopGateFailure.COMMAND_FAILURE);
                                  left = timeout - (nanoTime.getAsLong() - began);
                                  if (left <= 0)
                                    throw new StopGateException(StopGateFailure.TIMEOUT);
                                  try {
                                    drain.get(left, TimeUnit.NANOSECONDS);
                                  } catch (java.util.concurrent.TimeoutException timeoutFailure) {
                                    throw new StopGateException(StopGateFailure.TIMEOUT);
                                  } catch (java.util.concurrent.ExecutionException readFailure) {
                                    throw queryFailure(readFailure);
                                  }
                                  if (bytes[0].length > limit)
                                    throw new StopGateException(StopGateFailure.MALFORMED_STATE);
                                } finally {
                                  drain.cancel(true);
                                  reader.interrupt();
                                }
                              });
                        });
                  });
            });
        interrupted();
        return bytes[0];
      } catch (InterruptedException interruptedFailure) {
        Arrays.fill(bytes[0], (byte) 0);
        Thread.currentThread().interrupt();
        throw new StopGateException(StopGateFailure.INTERRUPTED);
      } catch (IOException known) {
        Arrays.fill(bytes[0], (byte) 0);
        throw new StopGateException(StopGateFailure.COMMAND_FAILURE);
      } catch (RuntimeException | Error failure) {
        Arrays.fill(bytes[0], (byte) 0);
        throw failure;
      }
    }

    @edu.umd.cs.findbugs.annotations.SuppressFBWarnings(
        value = "THROWS_METHOD_THROWS_RUNTIMEEXCEPTION",
        matchType = edu.umd.cs.findbugs.annotations.SuppressMatchType.EXACT,
        justification =
            "SSC125: FutureTask wraps actual provider failures; preserve unknown RuntimeException/Error identity, never normalize as ordinary IO or success")
    private static StopGateException queryFailure(java.util.concurrent.ExecutionException failure) {
      Throwable cause = failure.getCause();
      if (cause instanceof RuntimeException unknown) throw unknown;
      if (cause instanceof Error unknown) throw unknown;
      return new StopGateException(StopGateFailure.COMMAND_FAILURE);
    }

    byte[] execute(List<String> command, int limit) {
      interrupted();
      // Keep the delivered array reachable even when a later scope close fails.
      byte[][] bytes = {new byte[0]};
      try {
        ProcessResourceScope.acquire(
            () -> new QueryProcess(() -> start.execute(command)),
            QueryProcess::close,
            owned -> {
              var process = owned.required();
              ProcessResourceScope.acquire(
                  () -> new SafeStream<java.io.InputStream>(process::getInputStream),
                  SafeStream::finish,
                  output -> {
                    var stdout = output.required();
                    ProcessResourceScope.acquire(
                        () -> new SafeStream<java.io.OutputStream>(process::getOutputStream),
                        SafeStream::finish,
                        input -> {
                          input.required();
                          ProcessResourceScope.acquire(
                              () -> new SafeStream<java.io.InputStream>(process::getErrorStream),
                              SafeStream::finish,
                              error -> {
                                error.required();
                                // Neither query accepts stdin. Signal EOF and close discarded
                                // stderr before waiting.
                                input.finish();
                                error.finish();
                                if (!process.waitFor(5, TimeUnit.SECONDS))
                                  throw new StopGateException(StopGateFailure.TIMEOUT);
                                interrupted();
                                if (process.exitValue() != 0)
                                  throw new StopGateException(StopGateFailure.COMMAND_FAILURE);
                                bytes[0] =
                                    Objects.requireNonNull(
                                        stdout.readNBytes(limit + 1), "query output");
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
    private final @Nullable T resource;
    private boolean closed;

    SafeStream(ResourceScope.Acquire<T, IOException> acquire) throws IOException {
      resource = Objects.requireNonNull(acquire, "query stream acquire").open();
    }

    T required() {
      return Objects.requireNonNull(resource, "query stream");
    }

    // BUG187/YKT147: explicit early EOF/discard; scope fallback shares the one-close state.
    void finish() {
      if (closed || resource == null) return;
      closed = true; // A failed native close is not retried against an uncertain descriptor.
      try {
        resource.close();
      } catch (IOException failure) {
        throw new StopGateException(StopGateFailure.COMMAND_FAILURE);
      }
    }
  }

  private static final class QueryProcess implements AutoCloseable {
    private final @Nullable Process process;

    QueryProcess(ResourceScope.Acquire<Process, IOException> acquire) throws IOException {
      process = Objects.requireNonNull(acquire, "query process acquire").open();
    }

    Process required() {
      return Objects.requireNonNull(process, "query process");
    }

    @Override
    public void close() {
      if (process != null && process.isAlive()) process.destroy();
    }
  }
}
