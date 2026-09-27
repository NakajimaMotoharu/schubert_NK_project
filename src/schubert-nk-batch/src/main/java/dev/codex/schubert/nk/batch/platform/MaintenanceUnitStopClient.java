package dev.codex.schubert.nk.batch.platform;

import java.io.Closeable;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed root Morning stop-client owner. Client exit is not Unit/cgroup termination or Artemis
 * clean-journal proof. An unresolved Attempt retains its live Process; the parent must retain M/A
 * and this Attempt until a separate quarantine/reap decision. NK-OPS-001/UI251/253/SS341/343;
 * SSC100/101/102; PT-OPS-MCLIENT001..008.
 */
@NullMarked
public final class MaintenanceUnitStopClient {
  @FunctionalInterface
  interface Context {
    void recheck() throws IOException;
  }

  @FunctionalInterface
  interface Policy {
    void requireSafe(MaintenanceUnit unit);
  }

  @FunctionalInterface
  interface Start {
    Process execute(List<String> command) throws IOException;
  }

  public enum Status {
    CLIENT_EXITED_ZERO,
    CLIENT_EXITED_NONZERO,
    UNKNOWN
  }

  private final Context context;
  private final Policy policy;
  private final Start start;

  public static MaintenanceUnitStopClient create(
      RootStartupContext root, RootStartupContext.Snapshot expected) throws IOException {
    return create(
        root, expected, MaintenanceUnitStopPolicy.create()::requireSafe, new NativeStart());
  }

  static MaintenanceUnitStopClient create(
      RootStartupContext root, RootStartupContext.Snapshot expected, Policy policy, Start start)
      throws IOException {
    Objects.requireNonNull(root, "root context");
    Objects.requireNonNull(expected, "root identity");
    Objects.requireNonNull(policy, "fixed stop policy");
    Objects.requireNonNull(start, "fixed stop client");
    if (expected.service() != RootStartupContext.Service.MORNING)
      throw new IOException("fixed stop client unavailable");
    root.recheck(expected);
    return new MaintenanceUnitStopClient(() -> root.recheck(expected), policy, start);
  }

  MaintenanceUnitStopClient(Context context, Policy policy, Start start) {
    this.context = Objects.requireNonNull(context, "root context");
    this.policy = Objects.requireNonNull(policy, "fixed stop policy");
    this.start = Objects.requireNonNull(start, "fixed stop client");
  }

  /**
   * One fixed Unit only. Policy/root failures issue no stop. Caller must inspect returned status.
   */
  public Attempt stop(MaintenanceUnit unit) throws IOException {
    Objects.requireNonNull(unit, "fixed Unit");
    interrupted();
    context.recheck();
    policy.requireSafe(unit);
    context.recheck();
    interrupted();
    Process process =
        Objects.requireNonNull(
            start.execute(
                List.of(
                    "/usr/bin/systemctl",
                    "--system",
                    "--no-pager",
                    "--no-ask-password",
                    "stop",
                    unit.serviceName())),
            "fixed stop process");
    var attempt = new Attempt(unit, context, process);
    attempt.awaitClient();
    return attempt;
  }

  private static void interrupted() {
    if (Thread.currentThread().isInterrupted())
      throw new StopGateException(StopGateFailure.INTERRUPTED);
  }

  /** Opaque owner for a possibly live stop client. Never auto-destroys it. */
  public static final class Attempt {
    private final MaintenanceUnit unit;
    private final Context context;
    private final Process process;
    private Status status = Status.UNKNOWN;
    private boolean stdinClosed;
    private boolean streamsClosed;
    private boolean poisoned;

    private Attempt(MaintenanceUnit unit, Context context, Process process) {
      this.unit = unit;
      this.context = context;
      this.process = process;
    }

    public MaintenanceUnit unit() {
      return unit;
    }

    public synchronized Status status() {
      return status;
    }

    /** Reap under the still-held parent locks; UNKNOWN never grants an unlock or stop success. */
    public synchronized Status awaitClient() {
      if (status != Status.UNKNOWN || streamsClosed || poisoned) return status;
      try {
        context.recheck();
        if (Thread.currentThread().isInterrupted()) return Status.UNKNOWN;
        if (!stdinClosed) {
          stdinClosed = true; // A failed close is not retried against an uncertain descriptor.
          Objects.requireNonNull(process.getOutputStream(), "stop stdin").close();
        }
        if (!process.waitFor(120, TimeUnit.SECONDS)) return Status.UNKNOWN;
        if (Thread.currentThread().isInterrupted()) return Status.UNKNOWN;
        var stdout = Objects.requireNonNull(process.getInputStream(), "stop stdout");
        Closeable stderr;
        try {
          stderr = Objects.requireNonNull(process.getErrorStream(), "stop stderr");
        } catch (RuntimeException | Error failure) {
          closeOne(stdout);
          throw failure;
        }
        boolean closed = closeBoth(stdout, stderr);
        streamsClosed = true;
        if (!closed) return Status.UNKNOWN;
        context.recheck();
        status =
            process.exitValue() == 0 ? Status.CLIENT_EXITED_ZERO : Status.CLIENT_EXITED_NONZERO;
        return status;
      } catch (InterruptedException interrupted) {
        Thread.currentThread().interrupt();
        return Status.UNKNOWN;
      } catch (IOException | RuntimeException | Error failure) {
        poisoned = true;
        return Status.UNKNOWN;
      }
    }

    private static boolean closeBoth(Closeable stdout, Closeable stderr) {
      boolean clean = closeOne(stdout);
      return closeOne(stderr) && clean;
    }

    private static boolean closeOne(Closeable stream) {
      try {
        stream.close();
        return true;
      } catch (IOException | RuntimeException | Error failure) {
        return false;
      }
    }
  }

  static final class NativeStart implements Start {
    public Process execute(List<String> command) throws IOException {
      var builder =
          new ProcessBuilder(command)
              .redirectOutput(ProcessBuilder.Redirect.DISCARD)
              .redirectError(ProcessBuilder.Redirect.DISCARD);
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
      return builder.start();
    }
  }
}
