package dev.codex.schubert.nk.batch.platform;

import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
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
  public interface ObservedWork {
    BackupUnitReceiptGate.TerminalReceipt execute() throws IOException;
  }

  @FunctionalInterface
  public interface Handoff {
    BackupUnitReceiptGate.TerminalReceipt execute(ObservedWork work) throws IOException;
  }

  @FunctionalInterface
  public interface ObservedCompletion {
    void complete(BackupUnitReceiptGate.TerminalReceipt receipt) throws IOException;
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

    default Optional<BackupUnitReceiptGate.TerminalReceipt> observed(Object baseline)
        throws IOException {
      return Optional.empty();
    }

    default void requirePresent(BackupUnitReceiptGate.TerminalReceipt receipt) throws IOException {
      throw new IOException("typed receipt unavailable");
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
  private final BackupUnitStartClient.Target target;
  private Optional<StartAttempt> outstanding = Optional.empty();
  private Optional<BackupUnitReceiptGate.TerminalReceipt> completed = Optional.empty();

  private static final class Unresolved extends RuntimeException {
    private static final long serialVersionUID = 1L;
  }

  public static MorningBackupUnitCycle create(
      RootStartupContext root, RootStartupContext.Snapshot expected, MorningParentBudget budget)
      throws IOException {
    return create(root, expected, budget, BackupUnitStartClient.Target.BACKUP);
  }

  public static MorningBackupUnitCycle create(
      RootStartupContext root,
      RootStartupContext.Snapshot expected,
      MorningParentBudget budget,
      BackupUnitStartClient.Target target)
      throws IOException {
    Objects.requireNonNull(root, "Morning root context");
    Objects.requireNonNull(expected, "Morning root snapshot");
    Objects.requireNonNull(budget, "existing parent budget");
    Objects.requireNonNull(target, "closed phase");
    if (!target.ownedBy(expected.service())) throw new IOException("Backup parent unavailable");
    budget.requireWithin();
    root.recheck(expected);
    var receipt = BackupUnitReceiptGate.create(root, expected, target);
    var start = BackupUnitStartClient.create(root, expected, target, budget);
    var stop =
        target == BackupUnitStartClient.Target.INSPECTOR
            ? MaintenanceUnitStopClient.createInspector(root, expected)
            : MaintenanceUnitStopClient.create(root, expected);
    var terminal = BackupUnitTermination.create(root, expected, target);
    return new MorningBackupUnitCycle(
        () -> root.recheck(expected),
        new Receipt() {
          private Optional<BackupUnitReceiptGate.TerminalReceipt> latest = Optional.empty();

          public Object capture() throws IOException {
            latest = Optional.empty();
            return receipt.capture();
          }

          public boolean freshZero(Object baseline) throws IOException {
            return receipt.observe((BackupUnitReceiptGate.Baseline) baseline).isPresent();
          }

          public Optional<Outcome> terminal(Object baseline) throws IOException {
            var before = (BackupUnitReceiptGate.Baseline) baseline;
            latest = receipt.observeResult(before);
            return latest.map(
                value ->
                    value.exitCode() == 0
                            || (target != BackupUnitStartClient.Target.BACKUP
                                && value.exitCode() == 10)
                        ? Outcome.SUCCESS
                        : Outcome.FAILED);
          }

          public Optional<BackupUnitReceiptGate.TerminalReceipt> observed(Object baseline)
              throws IOException {
            if (latest.isPresent()) receipt.requireStillPresent(latest.orElseThrow());
            return latest;
          }

          public void requirePresent(BackupUnitReceiptGate.TerminalReceipt value)
              throws IOException {
            receipt.requireStillPresent(value);
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
          var attempt = stop.stop(target.unit());
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
        budget,
        target);
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
    this(
        gate,
        receipt,
        start,
        stop,
        terminal,
        wait,
        retain,
        budget,
        BackupUnitStartClient.Target.BACKUP);
  }

  MorningBackupUnitCycle(
      Gate gate,
      Receipt receipt,
      Start start,
      Stop stop,
      Terminal terminal,
      Wait wait,
      Retain retain,
      MorningParentBudget budget,
      BackupUnitStartClient.Target target) {
    this.gate = Objects.requireNonNull(gate, "Morning root gate");
    this.receipt = Objects.requireNonNull(receipt, "fresh Backup receipt");
    this.start = Objects.requireNonNull(start, "fixed Backup start");
    this.stop = Objects.requireNonNull(stop, "fixed Backup stop");
    this.terminal = Objects.requireNonNull(terminal, "whole Backup terminal");
    this.wait = Objects.requireNonNull(wait, "bounded observation wait");
    this.retain = Objects.requireNonNull(retain, "unresolved parent retention");
    this.budget = Objects.requireNonNull(budget, "existing parent budget");
    this.target = Objects.requireNonNull(target, "closed phase");
  }

  /**
   * Caller still owns M/A, original, DB and request for this entire call and its proof callback.
   */
  public void execute(ParentProof originalAndRequest) throws IOException {
    execute(originalAndRequest, outcome -> {});
  }

  /** Result completion and request retirement occur under M/A BEFORE marker retirement. */
  public Outcome execute(ParentProof originalAndRequest, Completion completion) throws IOException {
    if (target != BackupUnitStartClient.Target.BACKUP)
      throw new IOException("Backup phase required");
    Objects.requireNonNull(originalAndRequest, "same original and request proof");
    Objects.requireNonNull(completion, "same-owner Backup completion");
    if (target != BackupUnitStartClient.Target.BACKUP)
      throw new IOException("Cleanup handoff required");
    budget.requireWithin();
    gate.recheck();
    Object baseline = Objects.requireNonNull(receipt.capture(), "pre-start Backup baseline");
    budget.requireWithin();
    gate.recheck();
    budget.requireWithin();
    try {
      // From this call onward the parent cannot prove that delivery did not occur. Even a null
      // attempt or an unknown unchecked failure must not unwind M/A and discard the marker.
      Started observed = startAndWait(baseline);
      StartAttempt attempt = observed.attempt();
      Outcome outcome = observed.outcome();
      // startAndWait has just rechecked the same parent budget/root after the terminal receipt.
      // Keep that one proof immediately adjacent to stop, not two indistinguishable observations.
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
      completed = observed.receipt();
      outstanding = Optional.empty();
      return outcome;
    } catch (IOException | RuntimeException | Error unresolved) {
      // No normal M/A unwind after possible start delivery, including null, unchecked failures,
      // receipt/retire uncertainty. The native retention does not return.
      return retain();
    }
  }

  /** Same controller engine, but Cleanup's handoff returns only after fresh whole termination. */
  public BackupUnitReceiptGate.TerminalReceipt executeHandoff(
      Handoff handoff, ObservedCompletion completion, ParentProof originalAndRequest)
      throws IOException {
    return executeHandoff(handoff, completion, originalAndRequest, false);
  }

  /** Inspector stops/reaps INSIDE the unlocked callback; only then may Cleanup reacquire. */
  public BackupUnitReceiptGate.TerminalReceipt executeInspectorHandoff(
      Handoff handoff, ObservedCompletion completion, ParentProof environmentAndOwnerRetirement)
      throws IOException {
    return executeHandoff(handoff, completion, environmentAndOwnerRetirement, true);
  }

  private BackupUnitReceiptGate.TerminalReceipt executeHandoff(
      Handoff handoff,
      ObservedCompletion completion,
      ParentProof originalAndRequest,
      boolean stopChild)
      throws IOException {
    Objects.requireNonNull(handoff, "one-shot parent advisory handoff");
    Objects.requireNonNull(completion, "post-reacquire DB readback");
    Objects.requireNonNull(originalAndRequest, "same original/request proof");
    if (target
        != (stopChild
            ? BackupUnitStartClient.Target.INSPECTOR
            : BackupUnitStartClient.Target.CLEANUP))
      throw new IOException("maintenance handoff phase required");
    budget.requireWithin();
    gate.recheck();
    Object baseline = Objects.requireNonNull(receipt.capture(), "pre-start Cleanup baseline");
    var startedOnce = new AtomicBoolean();
    var observedReceipt = new AtomicReference<BackupUnitReceiptGate.TerminalReceipt>();
    try {
      var actual =
          handoff.execute(
              () -> {
                try {
                  if (!startedOnce.compareAndSet(false, true)) throw new Unresolved();
                  var child = startAndWait(baseline);
                  var value =
                      child
                          .receipt()
                          .orElseThrow(() -> new IOException("typed receipt unavailable"));
                  if (child.outcome() != Outcome.SUCCESS
                      && !(target == BackupUnitStartClient.Target.CLEANUP
                          && !stopChild
                          && value.exitCode() == 30)) throw new Unresolved();
                  receipt.requirePresent(value);
                  if (stopChild) stopAndVerify();
                  budget.requireWithin();
                  gate.recheck();
                  observedReceipt.set(value);
                  return value;
                } catch (IOException | RuntimeException | Error unknownChild) {
                  return retain();
                }
              });
      Objects.requireNonNull(actual, "same child terminal receipt");
      if (actual != observedReceipt.get()) throw new Unresolved();
      budget.requireWithin();
      gate.recheck();
      requireHandoffTerminal(actual, stopChild);
      completion.complete(actual); // Parent advisory has been reacquired, never inside handoff.
      budget.requireWithin();
      gate.recheck();
      var attempt =
          outstanding.orElseThrow(() -> new IOException("retained Cleanup attempt unavailable"));
      attempt.retireAfter(
          () -> {
            budget.requireWithin();
            gate.recheck();
            requireHandoffTerminal(actual, stopChild);
            originalAndRequest.verify();
            requireHandoffTerminal(actual, stopChild);
            budget.requireWithin();
            gate.recheck();
          });
      completed = Optional.of(actual);
      outstanding = Optional.empty();
      return actual;
    } catch (IOException | RuntimeException | Error unknownCompletion) {
      return retain();
    }
  }

  private void requireHandoffTerminal(BackupUnitReceiptGate.TerminalReceipt actual, boolean stopped)
      throws IOException {
    if (stopped) {
      if (!terminal.quiescent()) throw new IOException("Inspector terminal unavailable");
    } else receipt.requirePresent(actual);
  }

  private void stopAndVerify() throws IOException {
    var stopping = Objects.requireNonNull(stop.execute(), "retained Inspector stop attempt");
    var stopped = Objects.requireNonNull(stopping.status(), "Inspector stop status");
    while (stopped == MaintenanceUnitStopClient.Status.UNKNOWN) {
      budget.requireWithin();
      wait.pause();
      stopped = Objects.requireNonNull(stopping.awaitClient(), "reaped Inspector stop status");
    }
    if (stopped != MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO) throw new Unresolved();
    budget.requireWithin();
    gate.recheck();
    if (!terminal.quiescent()) throw new Unresolved();
  }

  /** Claims are available only after this controller's verified completion/retirement. */
  public BackupUnitReceiptGate.TerminalReceipt completedReceipt() throws IOException {
    return completed.orElseThrow(() -> new IOException("completed typed receipt unavailable"));
  }

  private record Started(
      StartAttempt attempt,
      Outcome outcome,
      Optional<BackupUnitReceiptGate.TerminalReceipt> receipt) {}

  private Started startAndWait(Object baseline) throws IOException {
    StartAttempt attempt = Objects.requireNonNull(start.execute(), "retained phase start attempt");
    outstanding = Optional.of(attempt);
    budget.requireWithin();
    var started = Objects.requireNonNull(attempt.status(), "phase start status");
    while (started == BackupUnitStartClient.Status.UNKNOWN) {
      budget.requireWithin();
      wait.pause();
      started = Objects.requireNonNull(attempt.awaitClient(), "reaped phase start status");
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
    var observed = Objects.requireNonNull(receipt.terminal(baseline), "phase terminal");
    while (observed.isEmpty()) {
      budget.requireWithin();
      wait.pause();
      observed = Objects.requireNonNull(receipt.terminal(baseline), "phase terminal");
    }
    var actual = Objects.requireNonNull(receipt.observed(baseline), "typed phase receipt");
    if (actual.isPresent() && actual.orElseThrow().target() != target) throw new Unresolved();
    budget.requireWithin();
    gate.recheck();
    return new Started(attempt, observed.orElseThrow(), actual);
  }

  private <T> T retain() {
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
