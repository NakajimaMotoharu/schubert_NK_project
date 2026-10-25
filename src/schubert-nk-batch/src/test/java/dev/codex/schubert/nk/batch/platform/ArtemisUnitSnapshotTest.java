package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.OptionalInt;
import org.junit.jupiter.api.Test;

/** SS341/343 SSC125 BUG369/YKT290 BROKERLIVE001..004. Independent daemon literal, not authority. */
final class ArtemisUnitSnapshotTest {
  private static final String INVOCATION = "123456789abcdef08123456789abcdef";
  private static final String LIVE =
      """
      Id=artemis.service
      LoadState=loaded
      ActiveState=active
      SubState=running
      Job=
      MainPID=123
      ControlPID=0
      InvocationID=123456789abcdef08123456789abcdef
      ExecMainCode=0
      ExecMainStatus=0
      ExecMainStartTimestampMonotonic=1234567
      ExecMainExitTimestampMonotonic=0
      Result=success
      Type=simple
      Restart=on-failure
      RemainAfterExit=no
      KillMode=control-group
      SendSIGKILL=no
      """;

  private static InspectorUnitSnapshot parse(String literal) {
    return InspectorUnitSnapshot.parse(
        literal.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.ARTEMIS);
  }

  @Test
  void brokerlive001ExactLiveInvocationNeverBecomesOneshotCompletion() {
    var actual = parse(LIVE);
    assertTrue(actual.brokerRunningInvocation(INVOCATION));
    assertTrue(actual.runningInvocation(INVOCATION));
    assertTrue(actual.running(123, INVOCATION));
    assertFalse(actual.running(124, INVOCATION));
    assertFalse(actual.quiescent());
    assertTrue(actual.receiptAfter(Optional.empty()).isEmpty());
    assertTrue(actual.backupTerminalAfter(Optional.empty()).isEmpty());
    assertFalse(actual.cleanupRejectedAfter(Optional.empty()));
    assertFalse(actual.brokerRunningInvocation("123456789abcdef08123456789abcdee"));
    assertThrows(NullPointerException.class, () -> actual.brokerRunningInvocation(null));
    var stopped =
        parse(
            LIVE.replace("ActiveState=active", "ActiveState=inactive")
                .replace("SubState=running", "SubState=dead")
                .replace("MainPID=123", "MainPID=0")
                .replace("ExecMainCode=0", "ExecMainCode=1")
                .replace(
                    "ExecMainExitTimestampMonotonic=0", "ExecMainExitTimestampMonotonic=2345678"));
    assertTrue(stopped.quiescent());
    assertFalse(stopped.brokerRunningInvocation(INVOCATION));
    assertTrue(stopped.receiptAfter(Optional.empty()).isEmpty());
  }

  @Test
  void brokerlive002EveryLiveConditionAndDaemonContractRejectsIndependentMismatch() {
    for (var mismatch :
        List.of(
            Map.entry("ActiveState=active", "ActiveState=activating"),
            Map.entry("SubState=running", "SubState=start"),
            Map.entry("Job=\n", "Job=1\n"),
            Map.entry("MainPID=123", "MainPID=1"),
            Map.entry("ControlPID=0", "ControlPID=1"),
            Map.entry("InvocationID=" + INVOCATION, "InvocationID="),
            Map.entry("ExecMainCode=0", "ExecMainCode=2"),
            Map.entry("ExecMainStatus=0", "ExecMainStatus=30"),
            Map.entry(
                "ExecMainStartTimestampMonotonic=1234567", "ExecMainStartTimestampMonotonic=0"),
            Map.entry("ExecMainExitTimestampMonotonic=0", "ExecMainExitTimestampMonotonic=2345678"),
            Map.entry("Result=success", "Result=timeout"),
            Map.entry("MainPID=123", "MainPID=2147483648")))
      assertFalse(
          parse(LIVE.replace(mismatch.getKey(), mismatch.getValue()))
              .brokerRunningInvocation(INVOCATION));
    assertTrue(parse(LIVE.replace("MainPID=123", "MainPID=2")).running(2, INVOCATION));
    assertTrue(
        parse(LIVE.replace("MainPID=123", "MainPID=2147483647")).running(2147483647, INVOCATION));
    for (var mismatch :
        Map.of(
                "Type=simple",
                "Type=oneshot",
                "Restart=on-failure",
                "Restart=no",
                "RemainAfterExit=no",
                "RemainAfterExit=yes")
            .entrySet())
      assertThrows(
          StopGateException.class,
          () -> parse(LIVE.replace(mismatch.getKey(), mismatch.getValue())));
  }

  @Test
  void brokerlive003EveryWorkerRetainsOneshotNoPolicyAndCannotBeBroker() {
    for (var target :
        List.of(
            InspectorUnitSnapshot.Target.BACKUP,
            InspectorUnitSnapshot.Target.CLEANUP,
            InspectorUnitSnapshot.Target.INSPECTOR,
            InspectorUnitSnapshot.Target.EXPIRY)) {
      String worker =
          """
          Id=WORKER
          LoadState=loaded
          ActiveState=active
          SubState=exited
          Job=
          MainPID=0
          ControlPID=0
          InvocationID=123456789abcdef08123456789abcdef
          ExecMainCode=1
          ExecMainStatus=0
          ExecMainStartTimestampMonotonic=1234567
          ExecMainExitTimestampMonotonic=2345678
          Result=success
          Type=oneshot
          Restart=no
          RemainAfterExit=yes
          KillMode=control-group
          SendSIGKILL=no
          """;
      worker = worker.replace("WORKER", target.unit());
      var value = InspectorUnitSnapshot.parse(worker.getBytes(StandardCharsets.US_ASCII), target);
      assertEquals(OptionalInt.of(0), value.receiptAfter(Optional.empty()));
      assertFalse(value.brokerRunningInvocation(INVOCATION));
      var wrong = worker.replace("Type=oneshot", "Type=simple");
      assertThrows(
          StopGateException.class,
          () -> InspectorUnitSnapshot.parse(wrong.getBytes(StandardCharsets.US_ASCII), target));
    }
  }

  @Test
  void brokerlive004LiteralMatchesSourceUnitAndFixedProbeReadsWithoutProcessAuthority()
      throws Exception {
    String source =
        Files.readString(
            Path.of(
                System.getProperty("nk.pt.repository"), "src/deployment/systemd/artemis.service"));
    for (String directive : List.of("Type=simple", "Restart=on-failure"))
      assertEquals(1, source.lines().filter(directive::equals).count());
    var observed =
        new InspectorUnitProbe(
                new InspectorUnitProbe.Reader() {
                  public byte[] readState() {
                    return LIVE.getBytes(StandardCharsets.US_ASCII);
                  }

                  public byte[] readProcesses() {
                    fail("live data read is never empty-process authority");
                    return new byte[0];
                  }
                },
                InspectorUnitSnapshot.Target.ARTEMIS)
            .read();
    assertTrue(observed.brokerRunningInvocation(INVOCATION));
    assertEquals("InspectorUnitSnapshot[redacted]", observed.toString());
  }
}
