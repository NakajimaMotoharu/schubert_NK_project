package dev.codex.schubert.nk.batch.platform;

import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.NullMarked;

/**
 * Parent-owned Backup Unit cycle inside the same Morning M/A/original/DB/request callback. A
 * systemctl exit is not worker success: only a new receipt0, explicit stop, fresh whole-Unit
 * termination and original/request proof can retire the start-intent marker. Once a start was
 * issued, unresolved delivery is retained under the caller's locks instead of normally returning.
 * The native retention is deliberately process-lifetime. The candidate Morning Type=oneshot Unit
 * has not yet proven hard-timeout quarantine (BUG-322/SSC-107); the caller must supply one
 * parent-entry monotonic budget, never a fresh per-Backup clock. Do not connect this cycle to the
 * external parent until those conditions are resolved. Real archives remain a separate unmet gate.
 * NK-OPS-001; OPS009/BAK001/BKO001; UI251/253; SS341§5-6/343§6.15; SSC092/093/105/106;
 * PG363/PT-OPS-BUCYCLE-001..004.
 */
@NullMarked
public final class MorningBackupUnitCycle {
  public enum Outcome {
    SUCCESS,
    FAILED
  }

  @FunctionalInterface
  public interface Completion {
    void complete(Outcome outcome) throws IOException;
  }

  @FunctionalInterface
  public interface ParentProof {
    void verify() throws IOException;
  }

  @FunctionalInterface
  interface Gate {
    void recheck() throws IOException;
  }

  interface Receipt {
    Object capture() throws IOException;

    boolean freshZero(Object baseline) throws IOException;

    default Optional<Outcome> terminal(Object baseline) throws IOException {
      return freshZero(baseline) ? Optional.of(Outcome.SUCCESS) : Optional.empty();
    }
  }

  interface StartAttempt {
    BackupUnitStartClient.Status status();

    BackupUnitStartClient.Status awaitClient();

    void retireAfter(ParentProof proof) throws IOException;
  }

  @FunctionalInterface
  interface Start {
    StartAttempt execute() throws IOException;
  }

  interface StopAttempt {
    MaintenanceUnitStopClient.Status status();

    MaintenanceUnitStopClient.Status awaitClient();
  }

  @FunctionalInterface
  interface Stop {
    StopAttempt execute() throws IOException;
  }

  @FunctionalInterface
  interface Terminal {
    boolean quiescent() throws IOException;
  }

  @FunctionalInterface
  interface Wait {
    void pause();
  }

  /** Native implementation never returns; a PT port may throw a sentinel after recording entry. */
  @FunctionalInterface
  interface Retain {
    void indefinitely();
  }

  private final Gate gate;
  private final Receipt receipt;
  private final Start start;
  private final Stop stop;
  private final Terminal terminal;
  private final Wait wait;
  private final Retain retain;
  private final MorningParentBudget budget;

  private static final class Unresolved extends RuntimeException {
    private static final long serialVersionUID = 1L;
  }

  public static MorningBackupUnitCycle create(
      RootStartupContext root, RootStartupContext.Snapshot expected, MorningParentBudget budget)
      throws IOException {
    Objects.requireNonNull(root, "Morning root context");
    Objects.requireNonNull(expected, "Morning root snapshot");
    Objects.requireNonNull(budget, "existing parent budget");
    if (expected.service() != RootStartupContext.Service.MORNING)
      throw new IOException("Backup parent unavailable");
    budget.requireWithin();
    root.recheck(expected);
    var receipt = BackupUnitReceiptGate.create(root, expected);
    var start = BackupUnitStartClient.create(root, expected);
    var stop = MaintenanceUnitStopClient.create(root, expected);
    var terminal = BackupUnitTermination.create(root, expected);
    return new MorningBackupUnitCycle(
        () -> root.recheck(expected),
        new Receipt() {
          public Object capture() throws IOException {
            return receipt.capture();
          }

          public boolean freshZero(Object baseline) throws IOException {
            return receipt.observe((BackupUnitReceiptGate.Baseline) baseline).isPresent();
          }

          public Optional<Outcome> terminal(Object baseline) throws IOException {
            var before = (BackupUnitReceiptGate.Baseline) baseline;
            return receipt
                .observeTerminal(before)
                .flatMap(value -> value.backupTerminalAfter(Optional.empty()));
          }
        },
        () -> {
          var attempt = start.start();
          return new StartAttempt() {
            public BackupUnitStartClient.Status status() {
              return attempt.status();
            }

            public BackupUnitStartClient.Status awaitClient() {
              return attempt.awaitClient();
            }

            public void retireAfter(ParentProof proof) throws IOException {
              attempt.retireAfter(proof::verify);
            }
          };
        },
        () -> {
          var attempt = stop.stop(MaintenanceUnit.BACKUP);
          return new StopAttempt() {
            public MaintenanceUnitStopClient.Status status() {
              return attempt.status();
            }

            public MaintenanceUnitStopClient.Status awaitClient() {
              return attempt.awaitClient();
            }
          };
        },
        () -> terminal.quiescent().isPresent(),
        MorningBackupUnitCycle::pausePreservingInterrupt,
        MorningBackupUnitCycle::retainIndefinitely,
        budget);
  }

  MorningBackupUnitCycle(
      Gate gate,
      Receipt receipt,
      Start start,
      Stop stop,
      Terminal terminal,
      Wait wait,
      Retain retain,
      MorningParentBudget budget) {
    this.gate = Objects.requireNonNull(gate, "Morning root gate");
    this.receipt = Objects.requireNonNull(receipt, "fresh Backup receipt");
    this.start = Objects.requireNonNull(start, "fixed Backup start");
    this.stop = Objects.requireNonNull(stop, "fixed Backup stop");
    this.terminal = Objects.requireNonNull(terminal, "whole Backup terminal");
    this.wait = Objects.requireNonNull(wait, "bounded observation wait");
    this.retain = Objects.requireNonNull(retain, "unresolved parent retention");
    this.budget = Objects.requireNonNull(budget, "existing parent budget");
  }

  /**
   * Caller still owns M/A, original, DB and request for this entire call and its proof callback.
   */
  public void execute(ParentProof originalAndRequest) throws IOException {
    execute(originalAndRequest, outcome -> {});
  }

  /** Result completion and request retirement occur under M/A BEFORE marker retirement. */
  public Outcome execute(ParentProof originalAndRequest, Completion completion) throws IOException {
    Objects.requireNonNull(originalAndRequest, "same original and request proof");
    Objects.requireNonNull(completion, "same-owner Backup completion");
    budget.requireWithin();
    gate.recheck();
    Object baseline = Objects.requireNonNull(receipt.capture(), "pre-start Backup baseline");
    budget.requireWithin();
    gate.recheck();
    budget.requireWithin();
    try {
      // From this call onward the parent cannot prove that delivery did not occur. Even a null
      // attempt or an unknown unchecked failure must not unwind M/A and discard the marker.
      StartAttempt attempt =
          Objects.requireNonNull(start.execute(), "retained Backup start attempt");
      budget.requireWithin();
      BackupUnitStartClient.Status started =
          Objects.requireNonNull(attempt.status(), "Backup start status");
      while (started == BackupUnitStartClient.Status.UNKNOWN) {
        budget.requireWithin();
        wait.pause();
        started = Objects.requireNonNull(attempt.awaitClient(), "reaped Backup start status");
      }
      if (started != BackupUnitStartClient.Status.CLIENT_EXITED_ZERO) {
        while (!terminal.quiescent()) {
          budget.requireWithin();
          wait.pause();
        }
        throw new Unresolved();
      }
      budget.requireWithin();
      gate.recheck();
      Optional<Outcome> observed =
          Objects.requireNonNull(receipt.terminal(baseline), "Backup result");
      while (observed.isEmpty()) {
        budget.requireWithin();
        wait.pause();
        observed = Objects.requireNonNull(receipt.terminal(baseline), "Backup result");
      }
      Outcome outcome = observed.orElseThrow();
      budget.requireWithin();
      gate.recheck();
      StopAttempt stopping = Objects.requireNonNull(stop.execute(), "retained Backup stop attempt");
      MaintenanceUnitStopClient.Status stopped =
          Objects.requireNonNull(stopping.status(), "Backup stop status");
      while (stopped == MaintenanceUnitStopClient.Status.UNKNOWN) {
        budget.requireWithin();
        wait.pause();
        stopped = Objects.requireNonNull(stopping.awaitClient(), "reaped Backup stop status");
      }
      if (stopped != MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO) throw new Unresolved();
      budget.requireWithin();
      gate.recheck();
      if (!terminal.quiescent()) throw new Unresolved();
      completion.complete(outcome);
      budget.requireWithin();
      gate.recheck();
      attempt.retireAfter(
          () -> {
            budget.requireWithin();
            gate.recheck();
            originalAndRequest.verify();
            if (!terminal.quiescent()) throw new IOException("Backup terminal unavailable");
            budget.requireWithin();
            gate.recheck();
          });
      budget.requireWithin();
      gate.recheck();
      return outcome;
    } catch (IOException | RuntimeException | Error unresolved) {
      // No normal M/A unwind after possible start delivery, including null, unchecked failures,
      // receipt/retire uncertainty. The native retention does not return.
      return retain();
    }
  }

  private Outcome retain() {
    retain.indefinitely();
    throw new AssertionError("unresolved Backup retention returned");
  }

  private static void retainIndefinitely() {
    for (; ; ) pausePreservingInterrupt();
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
}
