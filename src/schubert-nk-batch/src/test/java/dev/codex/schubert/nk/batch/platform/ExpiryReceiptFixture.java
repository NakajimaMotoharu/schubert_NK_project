package dev.codex.schubert.nk.batch.platform;

import java.nio.charset.StandardCharsets;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;

/** PT-only genuine gate sequencing with hand-written bus/kernel literals, NOT native authority. */
public final class ExpiryReceiptFixture {
  private ExpiryReceiptFixture() {}

  public static BackupUnitReceiptGate.TerminalReceipt receipt(int code) throws Exception {
    return receipt(code, BackupUnitStartClient.Target.EXPIRY, InspectorUnitSnapshot.Target.EXPIRY);
  }

  public static BackupUnitReceiptGate.TerminalReceipt cleanupReceipt(int code) throws Exception {
    return receipt(
        code, BackupUnitStartClient.Target.CLEANUP, InspectorUnitSnapshot.Target.CLEANUP);
  }

  public static BackupUnitReceiptGate.TerminalReceipt backupReceipt(int code) throws Exception {
    return receipt(code, BackupUnitStartClient.Target.BACKUP, InspectorUnitSnapshot.Target.BACKUP);
  }

  public static BackupUnitReceiptGate.TerminalReceipt backupReceipt(int code, String invocation)
      throws Exception {
    return receipt(
        code, BackupUnitStartClient.Target.BACKUP, InspectorUnitSnapshot.Target.BACKUP, invocation);
  }

  public static BackupUnitReceiptGate.TerminalReceipt cleanupReceipt(int code, String invocation)
      throws Exception {
    return receipt(
        code,
        BackupUnitStartClient.Target.CLEANUP,
        InspectorUnitSnapshot.Target.CLEANUP,
        invocation);
  }

  public static BackupUnitReceiptGate.TerminalReceipt receipt(int code, String invocation)
      throws Exception {
    return receipt(
        code, BackupUnitStartClient.Target.EXPIRY, InspectorUnitSnapshot.Target.EXPIRY, invocation);
  }

  private static BackupUnitReceiptGate.TerminalReceipt receipt(
      int code, BackupUnitStartClient.Target target, InspectorUnitSnapshot.Target observedTarget)
      throws Exception {
    return receipt(code, target, observedTarget, "7".repeat(32));
  }

  private static BackupUnitReceiptGate.TerminalReceipt receipt(
      int code,
      BackupUnitStartClient.Target target,
      InspectorUnitSnapshot.Target observedTarget,
      String invocation)
      throws Exception {
    String base =
        "Id=schubert-nk-expiry-cleanup.service\n"
            + "LoadState=loaded\n"
            + "ActiveState=inactive\n"
            + "SubState=dead\n"
            + "Job=\n"
            + "MainPID=0\n"
            + "ControlPID=0\n"
            + "InvocationID="
            + "6".repeat(32)
            + "\n"
            + "ExecMainCode=1\n"
            + "ExecMainStatus=0\n"
            + "ExecMainStartTimestampMonotonic=1000000\n"
            + "ExecMainExitTimestampMonotonic=2000000\n"
            + "Result=success\n"
            + "Type=oneshot\n"
            + "Restart=no\n"
            + "RemainAfterExit=yes\n"
            + "KillMode=control-group\n"
            + "SendSIGKILL=no\n";
    if (target == BackupUnitStartClient.Target.CLEANUP)
      base = base.replace("schubert-nk-expiry-cleanup.service", "schubert-nk-cleanup.service");
    if (target == BackupUnitStartClient.Target.BACKUP)
      base = base.replace("schubert-nk-expiry-cleanup.service", "schubert-nk-backup.service");
    var state =
        new AtomicReference<>(
            InspectorUnitSnapshot.parse(base.getBytes(StandardCharsets.US_ASCII), observedTarget));
    var gate =
        new BackupUnitReceiptGate(
            () -> {}, () -> Optional.of(state.get()), () -> Optional.of(state.get()), target);
    var before = gate.capture();
    boolean rejected = code == 30 || (target == BackupUnitStartClient.Target.BACKUP && code != 0);
    String actual =
        base.replace("6".repeat(32), invocation)
            .replace("ActiveState=inactive", rejected ? "ActiveState=failed" : "ActiveState=active")
            .replace("SubState=dead", rejected ? "SubState=failed" : "SubState=exited")
            .replace("ExecMainStatus=0", "ExecMainStatus=" + code)
            .replace("Result=success", rejected ? "Result=exit-code" : "Result=success");
    state.set(
        InspectorUnitSnapshot.parse(
            (target == BackupUnitStartClient.Target.BACKUP
                    ? actual
                        .replace("ActiveState=active", "ActiveState=inactive")
                        .replace("SubState=exited", "SubState=dead")
                    : actual)
                .getBytes(StandardCharsets.US_ASCII),
            observedTarget));
    return gate.observeResult(before).orElseThrow();
  }
}
