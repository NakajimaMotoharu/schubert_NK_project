package dev.codex.schubert.nk.batch.platform;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed trusted OS show command only; bounded wait/projection and owned stdio. No shell/service
 * mutation, inherited credentials, force kill or raw diagnostics. NK-OPS-001; OPS-009; UI251;
 * SS341/343; PG-D-148; PT-OPS-STOP-009..016.
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
    try {
      // BUG-157: acquire into ownership before any following getter can fail.
      try (var output = process.getInputStream();
          var input = process.getOutputStream();
          var error = process.getErrorStream()) {
        Objects.requireNonNull(output, "systemctl stdout");
        Objects.requireNonNull(input, "systemctl stdin");
        Objects.requireNonNull(error, "systemctl stderr");
        if (!process.waitFor(5, TimeUnit.SECONDS))
          throw new StopGateException(StopGateFailure.TIMEOUT);
        if (process.exitValue() != 0) throw new StopGateException(StopGateFailure.COMMAND_FAILURE);
        // Fixed trusted systemctl projection cannot spawn arbitrary writer descendants. An
        // oversized output filling the pipe cannot pass wait; timeout requests TERM below.
        byte[] bytes = output.readNBytes(1025);
        if (bytes.length > 1024) throw new StopGateException(StopGateFailure.MALFORMED_STATE);
        return bytes;
      }
    } catch (StopGateException failure) {
      // BUG-143/YKT-113: TWR may have attached raw close diagnostics to our fixed exception.
      throw new StopGateException(failure.reason());
    } catch (InterruptedException failure) {
      Thread.currentThread().interrupt();
      throw new StopGateException(StopGateFailure.INTERRUPTED);
    } catch (IOException failure) {
      throw new StopGateException(StopGateFailure.COMMAND_FAILURE);
    } finally {
      if (process.isAlive()) process.destroy(); // Only the show child, never SIGKILL or a service.
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
