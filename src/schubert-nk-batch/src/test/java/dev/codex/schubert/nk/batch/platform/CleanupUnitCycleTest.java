package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** SSC117/CCYCLE001..003, literal state and ordered ports. Native acceptance is separate. */
final class CleanupUnitCycleTest {
  private static final String FIXTURE_RESULT_SUCCESS_C6F30111 = "Result=success";
  private static final String FIXTURE_RESULT_EXIT_CODE_009C3BFA = "Result=exit-code";
  private static final String FIXTURE_EXECMAINSTATUS_0_226B574B = "ExecMainStatus=0";
  private static final String FIXTURE_EXECMAINSTATUS_30_43AE239C = "ExecMainStatus=30";
  private static final String BASELINE =
      """
      Id=schubert-nk-cleanup.service
      LoadState=loaded
      ActiveState=inactive
      SubState=dead
      Job=
      MainPID=0
      ControlPID=0
      InvocationID=
      ExecMainCode=0
      ExecMainStatus=0
      ExecMainStartTimestampMonotonic=0
      ExecMainExitTimestampMonotonic=0
      Result=success
      Type=oneshot
      Restart=no
      RemainAfterExit=yes
      KillMode=control-group
      SendSIGKILL=no
      """;
  private static final String FRESH =
      """
      Id=schubert-nk-cleanup.service
      LoadState=loaded
      ActiveState=active
      SubState=exited
      Job=
      MainPID=0
      ControlPID=0
      InvocationID=11111111111111111111111111111111
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

  private static InspectorUnitSnapshot parse(String text) {
    return InspectorUnitSnapshot.parse(
        text.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.CLEANUP);
  }

  @Test
  void ccycle005PriorKnownThirtyIsBaselineOnlyWithWholeKernelAndFreshNewInvocation()
      throws Exception {
    String prior =
        FRESH
            .replace("ActiveState=active", "ActiveState=failed")
            .replace("SubState=exited", "SubState=failed")
            .replace(FIXTURE_RESULT_SUCCESS_C6F30111, FIXTURE_RESULT_EXIT_CODE_009C3BFA)
            .replace(FIXTURE_EXECMAINSTATUS_0_226B574B, FIXTURE_EXECMAINSTATUS_30_43AE239C);
    var state = new AtomicReference<>(parse(prior));
    var kernel = new AtomicReference<>(Optional.of(state.get()));
    var gate =
        new BackupUnitReceiptGate(
            () -> {},
            () -> Optional.of(state.get()),
            kernel::get,
            BackupUnitStartClient.Target.CLEANUP);
    var before = gate.capture();
    assertTrue(gate.observeResult(before).isEmpty()); // Old30 is NOT this attempt's failure.
    state.set(parse(FRESH));
    kernel.set(Optional.of(state.get()));
    assertTrue(gate.observeResult(before).isEmpty()); // Even old0 cannot be reused.
    state.set(
        parse(
            FRESH.replace("11111111111111111111111111111111", "22222222222222222222222222222222")));
    kernel.set(Optional.of(state.get()));
    assertEquals(0, gate.observeResult(before).orElseThrow().exitCode());
    for (String invalid :
        List.of(
            prior.replace(FIXTURE_EXECMAINSTATUS_30_43AE239C, "ExecMainStatus=1"),
            prior.replace(FIXTURE_EXECMAINSTATUS_30_43AE239C, "ExecMainStatus=70"),
            prior.replace("ExecMainCode=1", "ExecMainCode=2"),
            prior.replace(FIXTURE_RESULT_EXIT_CODE_009C3BFA, "Result=timeout"),
            prior.replace("MainPID=0", "MainPID=123"),
            prior.replace("Job=\n", "Job=1\n"),
            prior.replace("InvocationID=11111111111111111111111111111111", "InvocationID="),
            prior.replace(
                "ExecMainStartTimestampMonotonic=1234567", "ExecMainStartTimestampMonotonic=0"),
            prior.replace(
                "ExecMainExitTimestampMonotonic=2345678", "ExecMainExitTimestampMonotonic=1"))) {
      state.set(parse(invalid));
      kernel.set(Optional.of(state.get()));
      assertThrows(IOException.class, gate::capture);
    }
    state.set(parse(prior));
    kernel.set(Optional.empty());
    assertThrows(IOException.class, gate::capture);
    kernel.set(Optional.of(parse(BASELINE)));
    assertThrows(IOException.class, gate::capture);
  }

  @Test
  void ccycle001FreshNormalZeroAndWarningKeepActiveAndReadDbOnlyAfterReacquire() throws Exception {
    for (int code : List.of(0, 10, 30)) {
      var state = new AtomicReference<>(parse(BASELINE));
      var gate =
          new BackupUnitReceiptGate(
              () -> {},
              () -> Optional.of(state.get()),
              () -> Optional.of(state.get()),
              BackupUnitStartClient.Target.CLEANUP);
      var events = new ArrayList<String>();
      var original = new AtomicReference<BackupUnitReceiptGate.Baseline>();
      var cycle =
          new MorningBackupUnitCycle(
              () -> {},
              new MorningBackupUnitCycle.Receipt() {
                public Object capture() throws IOException {
                  events.add("baseline");
                  var before = gate.capture();
                  original.set(before);
                  return before;
                }

                public boolean freshZero(Object before) {
                  fail("observed receipt required");
                  return false;
                }

                public Optional<MorningBackupUnitCycle.Outcome> terminal(Object before)
                    throws IOException {
                  events.add("fresh-terminal");
                  return gate.observeResult((BackupUnitReceiptGate.Baseline) before)
                      .map(
                          v ->
                              v.exitCode() == 30
                                  ? MorningBackupUnitCycle.Outcome.FAILED
                                  : MorningBackupUnitCycle.Outcome.SUCCESS);
                }

                public Optional<BackupUnitReceiptGate.TerminalReceipt> observed(Object before)
                    throws IOException {
                  return gate.observeResult((BackupUnitReceiptGate.Baseline) before);
                }

                public void requirePresent(BackupUnitReceiptGate.TerminalReceipt value)
                    throws IOException {
                  gate.requireStillPresent(value);
                }
              },
              () -> {
                events.add("start");
                String observed =
                    FRESH.replace(FIXTURE_EXECMAINSTATUS_0_226B574B, "ExecMainStatus=" + code);
                if (code == 30)
                  observed =
                      observed
                          .replace("ActiveState=active", "ActiveState=failed")
                          .replace("SubState=exited", "SubState=failed")
                          .replace(
                              FIXTURE_RESULT_SUCCESS_C6F30111, FIXTURE_RESULT_EXIT_CODE_009C3BFA);
                state.set(parse(observed));
                return new MorningBackupUnitCycle.StartAttempt() {
                  public BackupUnitStartClient.Status status() {
                    return BackupUnitStartClient.Status.CLIENT_EXITED_ZERO;
                  }

                  public BackupUnitStartClient.Status awaitClient() {
                    fail("already reaped");
                    return BackupUnitStartClient.Status.UNKNOWN;
                  }

                  public void retireAfter(MorningBackupUnitCycle.ParentProof proof)
                      throws IOException {
                    proof.verify();
                    events.add("intent-retire");
                  }
                };
              },
              () -> fail("Cleanup must not stop/reexecute through Broker Requires"),
              () -> true,
              () -> fail("fresh result needs no wait"),
              () -> fail("positive must not retain"),
              MorningParentBudget.create(),
              BackupUnitStartClient.Target.CLEANUP);
      assertThrows(IOException.class, cycle::completedReceipt);
      var actual =
          cycle.executeHandoff(
              work -> {
                events.add("unlock");
                var result = work.execute();
                events.add("reacquire");
                return result;
              },
              observed -> {
                events.add("DB-readback");
                assertEquals(code, observed.exitCode());
              },
              () -> events.add("request-retire"));
      assertSame(actual, cycle.completedReceipt());
      assertEquals(BackupUnitStartClient.Target.CLEANUP, actual.target());
      assertEquals("11111111-1111-1111-1111-111111111111", actual.invocation().toString());
      assertEquals(new java.math.BigInteger("1234567"), actual.startedMonotonic());
      assertEquals(new java.math.BigInteger("2345678"), actual.endedMonotonic());
      assertEquals("TerminalReceipt[observations=<redacted>]", actual.toString());
      assertEquals(
          List.of(
              "baseline",
              "unlock",
              "start",
              "fresh-terminal",
              "reacquire",
              "DB-readback",
              "request-retire",
              "intent-retire"),
          events);
      state.set(parse(BASELINE));
      assertThrows(IOException.class, () -> gate.requireStillPresent(actual));
    }
  }

  @Test
  void ccycle004NarrowRejectedThirtyNeverSuccessOldSignalTimeoutOrUnknown() throws Exception {
    String failed =
        FRESH
            .replace("ActiveState=active", "ActiveState=failed")
            .replace("SubState=exited", "SubState=failed")
            .replace(FIXTURE_RESULT_SUCCESS_C6F30111, FIXTURE_RESULT_EXIT_CODE_009C3BFA)
            .replace(FIXTURE_EXECMAINSTATUS_0_226B574B, FIXTURE_EXECMAINSTATUS_30_43AE239C);
    var state = new AtomicReference<>(parse(BASELINE));
    var kernel = new AtomicReference<>(Optional.of(state.get()));
    var gate =
        new BackupUnitReceiptGate(
            () -> {},
            () -> Optional.of(state.get()),
            kernel::get,
            BackupUnitStartClient.Target.CLEANUP);
    var before = gate.capture();
    state.set(parse(failed));
    kernel.set(Optional.of(state.get()));
    assertTrue(gate.observe(before).isEmpty());
    assertTrue(state.get().receiptAfter(Optional.empty()).isEmpty());
    var rejected = gate.observeResult(before).orElseThrow();
    assertEquals(30, rejected.exitCode());
    gate.requireStillPresent(rejected);
    for (String invalid :
        List.of(
            failed.replace(FIXTURE_EXECMAINSTATUS_30_43AE239C, "ExecMainStatus=70"),
            failed.replace(FIXTURE_EXECMAINSTATUS_30_43AE239C, "ExecMainStatus=1"),
            failed.replace("ExecMainCode=1", "ExecMainCode=2"),
            failed.replace(FIXTURE_RESULT_EXIT_CODE_009C3BFA, "Result=timeout"),
            failed.replace("MainPID=0", "MainPID=123"),
            failed.replace(
                "ExecMainStartTimestampMonotonic=1234567", "ExecMainStartTimestampMonotonic=0"),
            failed.replace(
                "ExecMainExitTimestampMonotonic=2345678", "ExecMainExitTimestampMonotonic=1"))) {
      state.set(parse(invalid));
      kernel.set(Optional.of(state.get()));
      assertTrue(gate.observeResult(before).isEmpty());
    }
    assertThrows(
        StopGateException.class,
        () -> parse(failed.replace("RemainAfterExit=yes", "RemainAfterExit=no")));
    state.set(parse(failed));
    kernel.set(Optional.empty());
    assertTrue(gate.observeResult(before).isEmpty());
    kernel.set(Optional.of(parse(BASELINE)));
    assertTrue(gate.observeResult(before).isEmpty());
    assertFalse(state.get().cleanupRejectedAfter(state.get().invocationId()));
    assertThrows(NullPointerException.class, () -> state.get().cleanupRejectedAfter(null));
  }

  @Test
  void ccycle002OldActiveFailedSignalWrongTargetAndIncompleteKernelNeverIssueReceipt()
      throws Exception {
    var state = new AtomicReference<>(parse(BASELINE));
    var kernel = new AtomicReference<>(Optional.of(state.get()));
    var gate =
        new BackupUnitReceiptGate(
            () -> {},
            () -> Optional.of(state.get()),
            kernel::get,
            BackupUnitStartClient.Target.CLEANUP);
    var before = gate.capture();
    for (String invalid :
        List.of(
            FRESH.replace("ExecMainCode=1", "ExecMainCode=2"),
            FRESH.replace(FIXTURE_EXECMAINSTATUS_0_226B574B, FIXTURE_EXECMAINSTATUS_30_43AE239C),
            FRESH.replace("MainPID=0", "MainPID=123"),
            FRESH.replace(FIXTURE_RESULT_SUCCESS_C6F30111, "Result=timeout"))) {
      state.set(parse(invalid));
      kernel.set(Optional.of(state.get()));
      assertTrue(gate.observeResult(before).isEmpty());
    }
    state.set(parse(FRESH));
    kernel.set(Optional.empty());
    assertTrue(gate.observeResult(before).isEmpty());
    kernel.set(Optional.of(state.get()));
    var receipt = gate.observeResult(before).orElseThrow();
    assertThrows(IOException.class, gate::capture); // Old active/exited cannot be a new baseline.
    var other =
        new BackupUnitReceiptGate(
            () -> {},
            () -> Optional.of(state.get()),
            kernel::get,
            BackupUnitStartClient.Target.CLEANUP);
    assertThrows(IOException.class, () -> other.requireStillPresent(receipt));
    assertThrows(IOException.class, () -> other.observeResult(before));
    assertThrows(NullPointerException.class, () -> gate.requireStillPresent(null));
    state.set(
        InspectorUnitSnapshot.parse(
            FRESH
                .replace("schubert-nk-cleanup.service", "schubert-nk-backup.service")
                .getBytes(StandardCharsets.US_ASCII),
            InspectorUnitSnapshot.Target.BACKUP));
    kernel.set(Optional.of(state.get()));
    assertTrue(gate.observeResult(before).isEmpty());
    assertThrows(IOException.class, gate::capture);
  }
}
