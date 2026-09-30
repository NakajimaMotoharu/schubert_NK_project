package dev.codex.schubert.nk.batch.platform;

import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;

/** PT-only genuine gate sequencing with hand-written bus/kernel literals, NOT native authority. */
public final class ExpiryReceiptFixture {
  private ExpiryReceiptFixture() {}

  public static BackupUnitReceiptGate.TerminalReceipt receipt(int code) throws Exception {
    String base =
        "Id=schubert-nk-expiry-cleanup.service\nLoadState=loaded\nActiveState=inactive\nSubState=dead\nJob=\nMainPID=0\nControlPID=0\nInvocationID="
            + "6".repeat(32)
            + "\nExecMainCode=1\nExecMainStatus=0\nExecMainStartTimestampMonotonic=1000000\nExecMainExitTimestampMonotonic=2000000\nResult=success\nType=oneshot\nRestart=no\nRemainAfterExit=yes\nKillMode=control-group\nSendSIGKILL=no\n";
    var state =
        new AtomicReference<>(
            InspectorUnitSnapshot.parse(
                base.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.EXPIRY));
    var gate =
        new BackupUnitReceiptGate(
            () -> {},
            () -> Optional.of(state.get()),
            () -> Optional.of(state.get()),
            BackupUnitStartClient.Target.EXPIRY);
    var before = gate.capture();
    String actual =
        base.replace("6".repeat(32), "7".repeat(32))
            .replace(
                "ActiveState=inactive", code == 30 ? "ActiveState=failed" : "ActiveState=active")
            .replace("SubState=dead", code == 30 ? "SubState=failed" : "SubState=exited")
            .replace("ExecMainStatus=0", "ExecMainStatus=" + code)
            .replace("Result=success", code == 30 ? "Result=exit-code" : "Result=success");
    state.set(
        InspectorUnitSnapshot.parse(
            actual.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.EXPIRY));
    return gate.observeResult(before).orElseThrow();
  }
}
