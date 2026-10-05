package dev.codex.schubert.nk.batch.platform;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;

/**
 * PT-OPS-STOPCOMP: hand-written manager/kernel states, never native authority or an oracle call.
 */
public final class StoppedBackupFixture {
  public static final String COLD =
      "Id=schubert-nk-backup.service\nLoadState=loaded\nActiveState=inactive\nSubState=dead\nJob=\nMainPID=0\nControlPID=0\nInvocationID=\nExecMainCode=0\nExecMainStatus=0\nExecMainStartTimestampMonotonic=0\nExecMainExitTimestampMonotonic=0\nResult=success\nType=oneshot\nRestart=no\nRemainAfterExit=yes\nKillMode=control-group\nSendSIGKILL=no\n";
  public final AtomicReference<String> current = new AtomicReference<>(COLD);
  public final AtomicBoolean kernelEmpty = new AtomicBoolean(true);
  public final AtomicBoolean ownerValid = new AtomicBoolean(true);
  public final AtomicLong nanos = new AtomicLong();
  public final List<String> events = new ArrayList<>();
  public final MorningBackupUnitCycle cycle;
  public final BackupUnitReceiptGate.TerminalReceipt receipt;
  public final String stopped;

  public StoppedBackupFixture(int code, boolean complete) throws Exception {
    String fresh =
        COLD.replace("InvocationID=\n", "InvocationID=77777777777777777777777777777777\n")
            .replace("ExecMainCode=0", "ExecMainCode=1")
            .replace("ExecMainStatus=0", "ExecMainStatus=" + code)
            .replace("ExecMainStartTimestampMonotonic=0", "ExecMainStartTimestampMonotonic=1000000")
            .replace("ExecMainExitTimestampMonotonic=0", "ExecMainExitTimestampMonotonic=2000000")
            .replace(
                "ActiveState=inactive", code == 0 ? "ActiveState=active" : "ActiveState=failed")
            .replace("SubState=dead", code == 0 ? "SubState=exited" : "SubState=failed")
            .replace("Result=success", code == 0 ? "Result=success" : "Result=exit-code");
    stopped =
        fresh
            .replace("ActiveState=active", "ActiveState=inactive")
            .replace("SubState=exited", "SubState=dead");
    BackupUnitReceiptGate.Context owner =
        () -> {
          if (!ownerValid.get()) throw new IOException("fixture owner rejected");
        };
    var gate =
        new BackupUnitReceiptGate(
            owner,
            () -> Optional.of(snapshot()),
            () -> kernelEmpty.get() ? Optional.of(snapshot()) : Optional.empty());
    cycle =
        new MorningBackupUnitCycle(
            owner::recheck,
            new MorningBackupUnitCycle.Receipt() {
              public Object capture() throws IOException {
                return gate.capture();
              }

              public boolean freshZero(Object before) {
                throw new AssertionError("typed receipt only");
              }

              public Optional<MorningBackupUnitCycle.Outcome> terminal(Object before)
                  throws IOException {
                current.set(fresh);
                return gate.observeResult((BackupUnitReceiptGate.Baseline) before)
                    .map(
                        value ->
                            value.exitCode() == 0
                                ? MorningBackupUnitCycle.Outcome.SUCCESS
                                : MorningBackupUnitCycle.Outcome.FAILED);
              }

              public Optional<BackupUnitReceiptGate.TerminalReceipt> observed(Object before)
                  throws IOException {
                events.add("fresh-receipt");
                return gate.observeResult((BackupUnitReceiptGate.Baseline) before);
              }

              public BackupUnitReceiptGate.TerminalReceipt stopped(
                  Object before, BackupUnitReceiptGate.TerminalReceipt actual) throws IOException {
                events.add("stopped-readback");
                gate.requireStoppedResult((BackupUnitReceiptGate.Baseline) before, actual);
                return actual;
              }
            },
            () ->
                new MorningBackupUnitCycle.StartAttempt() {
                  public BackupUnitStartClient.Status status() {
                    return BackupUnitStartClient.Status.CLIENT_EXITED_ZERO;
                  }

                  public BackupUnitStartClient.Status awaitClient() {
                    throw new AssertionError("no wait");
                  }

                  public void retireAfter(MorningBackupUnitCycle.ParentProof proof)
                      throws IOException {
                    proof.verify();
                    events.add("intent-retired");
                  }
                },
            () -> {
              events.add("explicit-stop");
              current.set(stopped);
              return new MorningBackupUnitCycle.StopAttempt() {
                public MaintenanceUnitStopClient.Status status() {
                  return MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO;
                }

                public MaintenanceUnitStopClient.Status awaitClient() {
                  throw new AssertionError("no wait");
                }
              };
            },
            kernelEmpty::get,
            () -> {
              throw new AssertionError("no wait");
            },
            () -> {
              throw new AssertionError("unexpected UNKNOWN");
            },
            new MorningParentBudget(nanos::get));
    if (complete) {
      cycle.executeObserved(
          () -> events.add("original-request"),
          (result, actual) -> events.add("actual-completion"));
      receipt = cycle.completedReceipt();
    } else receipt = ExpiryReceiptFixture.backupReceipt(code);
  }

  private InspectorUnitSnapshot snapshot() {
    return InspectorUnitSnapshot.parse(
        current.get().getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.BACKUP);
  }
}
