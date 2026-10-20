package dev.codex.schubert.nk.batch.platform;

import java.io.Closeable;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Fixed trusted OS show command only; bounded wait/projection and owned stdio. No shell/service
 * mutation, inherited credentials, force kill or raw diagnostics. NK-OPS-001; OPS-009; UI251;
 * SS341/343; PG-D-148/173, SSC063/BUG195/YKT154; PT-OPS-STOP-009..016; 017051.
 */
@NullMarked
final class SystemctlStateSource implements ApplicationStopGate.StateSource {
  private static final int MAXIMUM_STATE_OUTPUT_BYTES = 1024;

  @FunctionalInterface
  interface Start {
    Process execute(List<String> command) throws IOException;
  }

  private final Start start;

  SystemctlStateSource() {
    this(command -> NativeProcess.builder(command).start());
  }

  SystemctlStateSource(Start start) {
    this.start = Objects.requireNonNull(start, "process start");
  }

  @Override
  public byte[] read(ApplicationUnit unit) {
    Objects.requireNonNull(unit, "unit");
    byte[][] bytes = {new byte[0]};
    try {
      ProcessResourceScope.acquire(
          () ->
              start.execute(
                  List.of(
                      "/usr/bin/systemctl",
                      "--system",
                      "--no-pager",
                      "--no-ask-password",
                      "show",
                      "--property=Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID",
                      unit.serviceName())),
          process -> {
            if (process.isAlive()) process.destroy();
          },
          process -> {
            // Preserve all-getters-before-null admission and each already-owned stream.
            ProcessResourceScope.acquire(
                () -> new StdIo<java.io.InputStream>(process::getInputStream),
                StdIo::finish,
                output ->
                    ProcessResourceScope.acquire(
                        () -> new StdIo<java.io.OutputStream>(process::getOutputStream),
                        StdIo::finish,
                        input ->
                            ProcessResourceScope.acquire(
                                () -> new StdIo<java.io.InputStream>(process::getErrorStream),
                                StdIo::finish,
                                error -> {
                                  var stdout = output.required("systemctl stdout");
                                  input.required("systemctl stdin");
                                  error.required("systemctl stderr");
                                  if (!process.waitFor(5, TimeUnit.SECONDS))
                                    throw new StopGateException(StopGateFailure.TIMEOUT);
                                  if (process.exitValue() != 0)
                                    throw new StopGateException(StopGateFailure.COMMAND_FAILURE);
                                  bytes[0] =
                                      Objects.requireNonNull(
                                          stdout.readNBytes(1025), "systemctl output");
                                  if (bytes[0].length > MAXIMUM_STATE_OUTPUT_BYTES)
                                    throw new StopGateException(StopGateFailure.MALFORMED_STATE);
                                })));
          });
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

  // Nullable getter is admitted only after acquisition of all stdio, matching STOP016.
  private static void finish(@Nullable Closeable resource) {
    if (resource == null) return;
    try {
      resource.close();
    } catch (IOException failure) {
      throw new StopGateException(StopGateFailure.COMMAND_FAILURE);
    }
  }

  /** Nullable getter admission belongs to the body after all three resources are protected. */
  private static final class StdIo<T extends Closeable> {
    private final @Nullable T resource;

    StdIo(dev.codex.schubert.nk.storage.ResourceScope.Acquire<T, IOException> acquire)
        throws IOException {
      resource = Objects.requireNonNull(acquire, "query stdio acquire").open();
    }

    T required(String name) {
      return Objects.requireNonNull(resource, name);
    }

    void finish() {
      SystemctlStateSource.finish(resource);
    }
  }

  static final class NativeProcess {
    private NativeProcess() {}

    static ProcessBuilder builder(List<String> command) {
      var builder = new ProcessBuilder(command).redirectError(ProcessBuilder.Redirect.DISCARD);
      var environment = builder.environment();
      environment.clear();
      environment.putAll(
          Map.of(
              "PATH",
              "/usr/bin:/bin",
              "LANG",
              "C",
              "LC_ALL",
              "C",
              "SYSTEMD_COLORS",
              "0",
              "TERM",
              "dumb"));
      return builder;
    }
  }
}
