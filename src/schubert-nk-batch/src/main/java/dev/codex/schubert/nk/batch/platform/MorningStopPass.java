package dev.codex.schubert.nk.batch.platform;

import java.io.IOException;
import java.util.Objects;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.NullMarked;

/**
 * Parent's fixed eight stop pass, to be called only inside continuous Morning M ownership. A
 * CLIENT_EXITED_ZERO is not a Unit stop: each whole Unit and then the complete set are freshly
 * observed. An UNKNOWN client attempt is retained in this stack and cannot normally return to the
 * caller while M is held; interruption is preserved while retrying its real terminal observation.
 * This pass does not acquire A, invalidate or issue a permit, prove Artemis clean journal, or
 * execute backup/Cleanup. Those are mandatory parent continuation gates. NK-OPS-001; OPS009/UI251;
 * SS341§4-5/343/SSC100-102; PG338/PT-OPS-MPASS001-009.
 */
@NullMarked
public final class MorningStopPass {
  interface Attempt {
    MaintenanceUnitStopClient.Status status();

    MaintenanceUnitStopClient.Status awaitClient();
  }

  interface Stop {
    void preflight() throws IOException;

    Attempt stop(MaintenanceUnit unit) throws IOException;
  }

  interface Terminals {
    void require(MaintenanceUnit unit) throws IOException;

    void requireAll() throws IOException;
  }

  @FunctionalInterface
  interface Gate {
    void recheck() throws IOException;
  }

  private final Gate gate;
  private final Stop stop;
  private final Terminals terminals;

  public static MorningStopPass create(
      RootStartupContext context, RootStartupContext.Snapshot expected) throws IOException {
    Objects.requireNonNull(context, "Morning root context");
    Objects.requireNonNull(expected, "Morning root snapshot");
    if (expected.service() != RootStartupContext.Service.MORNING) throw unavailable();
    context.recheck(expected);
    MaintenanceUnitStopClient client = MaintenanceUnitStopClient.create(context, expected);
    return new MorningStopPass(
        () -> context.recheck(expected),
        new Stop() {
          @Override
          public void preflight() throws IOException {
            client.preflightAll();
          }

          @Override
          public Attempt stop(MaintenanceUnit unit) throws IOException {
            var attempt = client.stop(unit);
            return new Attempt() {
              public MaintenanceUnitStopClient.Status status() {
                return attempt.status();
              }

              public MaintenanceUnitStopClient.Status awaitClient() {
                return attempt.awaitClient();
              }
            };
          }
        },
        new Terminals() {
          @Override
          public void require(MaintenanceUnit unit) throws IOException {
            if (MaintenanceUnitTermination.create(context, expected, unit).quiescent().isEmpty())
              throw unavailable();
          }

          @Override
          public void requireAll() throws IOException {
            MorningUnitTerminals.requireQuiescent(context, expected);
          }
        });
  }

  MorningStopPass(Gate gate, Stop stop, Terminals terminals) {
    this.gate = Objects.requireNonNull(gate, "Morning root gate");
    this.stop = Objects.requireNonNull(stop, "fixed stop client");
    this.terminals = Objects.requireNonNull(terminals, "fixed whole-Unit observer");
  }

  public void execute() throws IOException {
    gate.recheck();
    stop.preflight();
    for (MaintenanceUnit unit : MaintenanceUnit.values()) {
      gate.recheck();
      Attempt attempt = Objects.requireNonNull(stop.stop(unit), "owned stop attempt");
      MaintenanceUnitStopClient.Status status =
          Objects.requireNonNull(attempt.status(), "stop status");
      while (status == MaintenanceUnitStopClient.Status.UNKNOWN) {
        pausePreservingInterrupt();
        status = Objects.requireNonNull(awaitPreservingInterrupt(attempt), "reaped stop status");
      }
      if (status != MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO) throw unavailable();
      gate.recheck();
      terminals.require(unit);
    }
    terminals.requireAll();
    gate.recheck();
  }

  private static MaintenanceUnitStopClient.Status awaitPreservingInterrupt(Attempt attempt) {
    boolean interrupted = Thread.interrupted();
    try {
      return attempt.awaitClient();
    } finally {
      if (interrupted) Thread.currentThread().interrupt();
    }
  }

  private static void pausePreservingInterrupt() {
    boolean interrupted = Thread.interrupted();
    try {
      TimeUnit.MILLISECONDS.sleep(100);
    } catch (InterruptedException newInterrupt) {
      interrupted = true;
    } finally {
      if (interrupted) Thread.currentThread().interrupt();
    }
  }

  private static IOException unavailable() {
    return new IOException("Morning stop pass unavailable");
  }
}
