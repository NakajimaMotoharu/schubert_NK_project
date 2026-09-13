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
    Process process;
    try {
      process =
          Objects.requireNonNull(
              start.execute(
                  List.of(
                      "/usr/bin/systemctl",
                      "--system",
                      "--no-pager",
                      "--no-ask-password",
                      "show",
                      "--property=Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID",
                      unit.serviceName())),
              "systemctl process");
    } catch (IOException failure) {
      throw new StopGateException(StopGateFailure.COMMAND_FAILURE);
    }
    byte[][] bytes = {new byte[0]};
    try {
      ProcessResourceScope.use(
          () -> {
            if (process.isAlive()) process.destroy();
          },
          () -> {
            // Preserve all-getters-before-null admission and each already-owned stream.
            var output = process.getInputStream();
            ProcessResourceScope.use(
                () -> finish(output),
                () -> {
                  var input = process.getOutputStream();
                  ProcessResourceScope.use(
                      () -> finish(input),
                      () -> {
                        var error = process.getErrorStream();
                        ProcessResourceScope.use(
                            () -> finish(error),
                            () -> {
                              Objects.requireNonNull(output, "systemctl stdout");
                              Objects.requireNonNull(input, "systemctl stdin");
                              Objects.requireNonNull(error, "systemctl stderr");
                              if (!process.waitFor(5, TimeUnit.SECONDS))
                                throw new StopGateException(StopGateFailure.TIMEOUT);
                              if (process.exitValue() != 0)
                                throw new StopGateException(StopGateFailure.COMMAND_FAILURE);
                              bytes[0] =
                                  Objects.requireNonNull(
                                      output.readNBytes(1025), "systemctl output");
                              if (bytes[0].length > 1024)
                                throw new StopGateException(StopGateFailure.MALFORMED_STATE);
                            });
                      });
                });
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
