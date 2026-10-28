package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.TreeMap;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * NK-DAT-001/NK-OPS-001; DAT009/OPS009; UI212/251; SS341 7.4/343/352; WBS-P004-04;
 * PT-SNAPSHOT-911001..009. Literal observations, never Unit/kernel/owner authority.
 */
final class InspectorHeldStateContractTest {
  private static final String FIXTURE_ACTIVESTATE_8ACAC4AA = "ActiveState";
  private static final String FIXTURE_INACTIVE_A5714161 = "inactive";
  private static final String FIXTURE_SUBSTATE_39662EFC = "SubState";
  private static final String FIXTURE_DEAD_0453462F = "dead";
  private static final String FIXTURE_RUNNING_79D116A0 = "running";
  private static final String FIXTURE_JOB_F32F4C4D = "Job";
  private static final String FIXTURE_MAINPID_D7C01CF7 = "MainPID";
  private static final String FIXTURE_CONTROLPID_32D1DE3E = "ControlPID";
  private static final String FIXTURE_REMAINAFTEREXIT_A99477E7 = "RemainAfterExit";
  private static final String FIXTURE_RESULT_37D8A404 = "Result";
  private static final String FIXTURE_SUCCESS_68E7A699 = "success";
  private static final String FIXTURE_FAILED_33D04BD7 = "failed";
  private static final String FIXTURE_EXIT_CODE_BC9E614D = "exit-code";
  private static final String FIXTURE_EXECMAINSTATUS_179A8E0B = "ExecMainStatus";
  private static final String FIXTURE_INVOCATIONID_0F13ED0E = "InvocationID";
  private static final String FIXTURE_EXECMAINCODE_02C974D2 = "ExecMainCode";
  private static final String FIXTURE_EXECMAINSTARTTIMESTAMPMONOTONIC_1FB48E62 =
      "ExecMainStartTimestampMonotonic";
  private static final String FIXTURE_EXECMAINEXITTIMESTAMPMONOTONIC_C1411C27 =
      "ExecMainExitTimestampMonotonic";
  private static final String FIXTURE_TIMEOUT_492BD020 = "timeout";
  private static final String FIXTURE_ACTIVE_DB0FB2BF = "active";
  private static final String FIXTURE_EXITED_3D0FE3B1 = "exited";
  private static final String INV = "11111111111111111111111111111111";
  private static final UUID SAME = UUID.fromString("11111111-1111-1111-1111-111111111111");
  private static final Map<InspectorUnitSnapshot.Target, String> NAMES =
      Map.of(
          InspectorUnitSnapshot.Target.INSPECTOR, "schubert-nk-inbox-inspector.service",
          InspectorUnitSnapshot.Target.BACKUP, "schubert-nk-backup.service",
          InspectorUnitSnapshot.Target.CLEANUP, "schubert-nk-cleanup.service",
          InspectorUnitSnapshot.Target.EXPIRY, "schubert-nk-expiry-cleanup.service",
          InspectorUnitSnapshot.Target.ARTEMIS, "artemis.service",
          InspectorUnitSnapshot.Target.MORNING, "schubert-nk-morning-controller.service",
          InspectorUnitSnapshot.Target.API, "schubert-nk-api.service",
          InspectorUnitSnapshot.Target.WEB, "schubert-nk-web.service");

  @Test
  void snapshot911001OnlyCleanupInspectorExpiryAreHeldMaintenanceData() {
    for (var target : NAMES.keySet()) {
      var observed = snapshot(target, Map.of());
      for (var expectedTarget : NAMES.keySet()) {
        assertEquals(target == expectedTarget, observed.isTarget(expectedTarget));
      }
      assertEquals(
          target == InspectorUnitSnapshot.Target.CLEANUP, observed.heldCleanup(), target.name());
      assertEquals(
          List.of(
                  InspectorUnitSnapshot.Target.CLEANUP,
                  InspectorUnitSnapshot.Target.INSPECTOR,
                  InspectorUnitSnapshot.Target.EXPIRY)
              .contains(target),
          observed.heldMaintenance(),
          target.name());
    }
  }

  @Test
  void snapshot911002EachLostStateOrOutstandingProcessJobRejectsHeldData() {
    for (var target :
        List.of(
            InspectorUnitSnapshot.Target.CLEANUP,
            InspectorUnitSnapshot.Target.INSPECTOR,
            InspectorUnitSnapshot.Target.EXPIRY)) {
      for (var change :
          List.of(
              Map.of(
                  FIXTURE_ACTIVESTATE_8ACAC4AA,
                  FIXTURE_INACTIVE_A5714161,
                  FIXTURE_SUBSTATE_39662EFC,
                  FIXTURE_DEAD_0453462F),
              Map.of(FIXTURE_SUBSTATE_39662EFC, FIXTURE_RUNNING_79D116A0),
              Map.of(FIXTURE_JOB_F32F4C4D, "7"),
              Map.of(FIXTURE_MAINPID_D7C01CF7, "17"),
              Map.of(FIXTURE_CONTROLPID_32D1DE3E, "18"))) {
        var observed = snapshot(target, change);
        assertFalse(observed.heldCleanup(), target + " " + change);
        assertFalse(observed.heldMaintenance(), target + " " + change);
      }
    }
    for (var target :
        List.of(InspectorUnitSnapshot.Target.INSPECTOR, InspectorUnitSnapshot.Target.EXPIRY)) {
      assertFalse(
          snapshot(target, Map.of(FIXTURE_REMAINAFTEREXIT_A99477E7, "no")).heldMaintenance());
    }
  }

  @Test
  void snapshot911003BrokerNormalTermRequiresCompleteOldStopProfile() {
    for (var terminal :
        List.of(
            Map.of(
                FIXTURE_ACTIVESTATE_8ACAC4AA,
                FIXTURE_INACTIVE_A5714161,
                FIXTURE_SUBSTATE_39662EFC,
                FIXTURE_DEAD_0453462F,
                FIXTURE_RESULT_37D8A404,
                FIXTURE_SUCCESS_68E7A699),
            Map.of(
                FIXTURE_ACTIVESTATE_8ACAC4AA,
                FIXTURE_FAILED_33D04BD7,
                FIXTURE_SUBSTATE_39662EFC,
                FIXTURE_FAILED_33D04BD7,
                FIXTURE_RESULT_37D8A404,
                FIXTURE_EXIT_CODE_BC9E614D))) {
      var input = new TreeMap<>(terminal);
      input.put(FIXTURE_EXECMAINSTATUS_179A8E0B, "143");
      assertTrue(snapshot(InspectorUnitSnapshot.Target.ARTEMIS, input).brokerStoppedNormally());
      for (var change :
          List.of(
              Map.of(FIXTURE_MAINPID_D7C01CF7, "17"),
              Map.of(FIXTURE_CONTROLPID_32D1DE3E, "18"),
              Map.of(FIXTURE_JOB_F32F4C4D, "7"),
              Map.of(FIXTURE_INVOCATIONID_0F13ED0E, ""),
              Map.of(FIXTURE_EXECMAINCODE_02C974D2, "2"),
              Map.of(FIXTURE_EXECMAINSTATUS_179A8E0B, "0"),
              Map.of(FIXTURE_EXECMAINSTARTTIMESTAMPMONOTONIC_1FB48E62, "0"),
              Map.of(FIXTURE_EXECMAINEXITTIMESTAMPMONOTONIC_C1411C27, "99"),
              Map.of(FIXTURE_RESULT_37D8A404, FIXTURE_TIMEOUT_492BD020),
              Map.of(FIXTURE_SUBSTATE_39662EFC, FIXTURE_RUNNING_79D116A0),
              Map.of(FIXTURE_ACTIVESTATE_8ACAC4AA, "activating"))) {
        var bad = new TreeMap<>(input);
        bad.putAll(change);
        assertFalse(
            snapshot(InspectorUnitSnapshot.Target.ARTEMIS, bad).brokerStoppedNormally(),
            change.toString());
      }
    }
    assertFalse(
        snapshot(
                InspectorUnitSnapshot.Target.CLEANUP,
                Map.of(FIXTURE_EXECMAINSTATUS_179A8E0B, "143"))
            .brokerStoppedNormally());
  }

  @Test
  void snapshot911004InactiveInspectorNeedsRemainYesAndNoOutstandingProcess() {
    var idle =
        Map.of(
            FIXTURE_ACTIVESTATE_8ACAC4AA,
            FIXTURE_INACTIVE_A5714161,
            FIXTURE_SUBSTATE_39662EFC,
            FIXTURE_DEAD_0453462F);
    for (var target : NAMES.keySet()) {
      assertTrue(snapshot(target, idle).inactiveBaseline(), target.name());
      assertFalse(snapshot(target, Map.of()).inactiveBaseline());
      assertFalse(
          snapshot(
                  target,
                  Map.of(
                      FIXTURE_ACTIVESTATE_8ACAC4AA,
                      FIXTURE_INACTIVE_A5714161,
                      FIXTURE_SUBSTATE_39662EFC,
                      FIXTURE_RUNNING_79D116A0))
              .inactiveBaseline());
      assertFalse(
          snapshot(
                  target,
                  Map.of(
                      FIXTURE_ACTIVESTATE_8ACAC4AA,
                      FIXTURE_INACTIVE_A5714161,
                      FIXTURE_SUBSTATE_39662EFC,
                      FIXTURE_DEAD_0453462F,
                      FIXTURE_JOB_F32F4C4D,
                      "1"))
              .inactiveBaseline());
    }
    assertFalse(
        snapshot(
                InspectorUnitSnapshot.Target.INSPECTOR,
                Map.of(
                    FIXTURE_ACTIVESTATE_8ACAC4AA,
                    FIXTURE_INACTIVE_A5714161,
                    FIXTURE_SUBSTATE_39662EFC,
                    FIXTURE_DEAD_0453462F,
                    FIXTURE_REMAINAFTEREXIT_A99477E7,
                    "no"))
            .inactiveBaseline());
  }

  @Test
  void snapshot911005BackupNormalTerminalIsNotUnknownOrDuplicateInvocation() {
    var target = InspectorUnitSnapshot.Target.BACKUP;
    assertEquals(
        Optional.of(MorningBackupUnitCycle.Outcome.SUCCESS),
        snapshot(target, Map.of()).backupTerminalAfter(Optional.empty()));
    var failure =
        Map.of(
            FIXTURE_ACTIVESTATE_8ACAC4AA,
            FIXTURE_FAILED_33D04BD7,
            FIXTURE_SUBSTATE_39662EFC,
            FIXTURE_FAILED_33D04BD7,
            FIXTURE_RESULT_37D8A404,
            FIXTURE_EXIT_CODE_BC9E614D,
            FIXTURE_EXECMAINSTATUS_179A8E0B,
            "70");
    assertEquals(
        Optional.of(MorningBackupUnitCycle.Outcome.FAILED),
        snapshot(target, failure).backupTerminalAfter(Optional.empty()));
    assertTrue(snapshot(target, failure).backupTerminalAfter(Optional.of(SAME)).isEmpty());
    for (var change :
        List.of(
            Map.of(FIXTURE_EXECMAINSTARTTIMESTAMPMONOTONIC_1FB48E62, "0"),
            Map.of(FIXTURE_EXECMAINEXITTIMESTAMPMONOTONIC_C1411C27, "99"),
            Map.of(FIXTURE_MAINPID_D7C01CF7, "17"),
            Map.of(FIXTURE_CONTROLPID_32D1DE3E, "18"),
            Map.of(FIXTURE_JOB_F32F4C4D, "7"),
            Map.of(FIXTURE_INVOCATIONID_0F13ED0E, ""),
            Map.of(FIXTURE_EXECMAINCODE_02C974D2, "2"),
            Map.of(FIXTURE_EXECMAINSTATUS_179A8E0B, "0"),
            Map.of(
                FIXTURE_ACTIVESTATE_8ACAC4AA,
                FIXTURE_INACTIVE_A5714161,
                FIXTURE_SUBSTATE_39662EFC,
                FIXTURE_DEAD_0453462F),
            Map.of(FIXTURE_RESULT_37D8A404, FIXTURE_TIMEOUT_492BD020))) {
      var bad = new TreeMap<>(failure);
      bad.putAll(change);
      assertTrue(
          snapshot(target, bad).backupTerminalAfter(Optional.empty()).isEmpty(), change.toString());
    }
  }

  @Test
  void snapshot911006KnownThirtyRejectsPartialHistoryAndBrokerRunningNeedsSamePid() {
    for (var target :
        List.of(InspectorUnitSnapshot.Target.CLEANUP, InspectorUnitSnapshot.Target.EXPIRY)) {
      var failure =
          Map.of(
              FIXTURE_ACTIVESTATE_8ACAC4AA,
              FIXTURE_FAILED_33D04BD7,
              FIXTURE_SUBSTATE_39662EFC,
              FIXTURE_FAILED_33D04BD7,
              FIXTURE_RESULT_37D8A404,
              FIXTURE_EXIT_CODE_BC9E614D,
              FIXTURE_EXECMAINSTATUS_179A8E0B,
              "30");
      var observed = snapshot(target, failure);
      assertEquals(
          target == InspectorUnitSnapshot.Target.CLEANUP,
          observed.cleanupRejectedAfter(Optional.empty()));
      assertEquals(
          target == InspectorUnitSnapshot.Target.EXPIRY,
          observed.expiryRejectedAfter(Optional.empty()));
      assertFalse(observed.cleanupRejectedAfter(Optional.of(SAME)));
      assertFalse(observed.expiryRejectedAfter(Optional.of(SAME)));
      if (target == InspectorUnitSnapshot.Target.EXPIRY) {
        var noRemain = new TreeMap<>(failure);
        noRemain.put(FIXTURE_REMAINAFTEREXIT_A99477E7, "no");
        var observedNoRemain = snapshot(target, noRemain);
        assertTrue(observedNoRemain.quiescent());
        assertFalse(observedNoRemain.expiryRejectedAfter(Optional.empty()));
      }
      for (var change :
          List.of(
              Map.of(FIXTURE_JOB_F32F4C4D, "7"),
              Map.of(FIXTURE_MAINPID_D7C01CF7, "17"),
              Map.of(FIXTURE_CONTROLPID_32D1DE3E, "18"),
              Map.of(FIXTURE_INVOCATIONID_0F13ED0E, ""),
              Map.of(FIXTURE_EXECMAINCODE_02C974D2, "2"),
              Map.of(FIXTURE_EXECMAINSTATUS_179A8E0B, "70"),
              Map.of(FIXTURE_RESULT_37D8A404, FIXTURE_TIMEOUT_492BD020),
              Map.of(FIXTURE_EXECMAINSTARTTIMESTAMPMONOTONIC_1FB48E62, "0"),
              Map.of(FIXTURE_EXECMAINEXITTIMESTAMPMONOTONIC_C1411C27, "99"))) {
        var bad = new TreeMap<>(failure);
        bad.putAll(change);
        assertFalse(snapshot(target, bad).cleanupRejectedAfter(Optional.empty()));
        assertFalse(snapshot(target, bad).expiryRejectedAfter(Optional.empty()));
      }
    }
    var broker =
        snapshot(
            InspectorUnitSnapshot.Target.ARTEMIS,
            Map.of(
                FIXTURE_ACTIVESTATE_8ACAC4AA, FIXTURE_ACTIVE_DB0FB2BF,
                FIXTURE_SUBSTATE_39662EFC, FIXTURE_RUNNING_79D116A0,
                FIXTURE_MAINPID_D7C01CF7, "17",
                FIXTURE_EXECMAINCODE_02C974D2, "0",
                FIXTURE_EXECMAINEXITTIMESTAMPMONOTONIC_C1411C27, "0"));
    assertTrue(broker.running(17, INV));
    assertFalse(broker.running(18, INV));
    assertFalse(broker.running(17, "22222222222222222222222222222222"));
    assertFalse(
        snapshot(
                InspectorUnitSnapshot.Target.ARTEMIS,
                Map.of(
                    FIXTURE_ACTIVESTATE_8ACAC4AA,
                    FIXTURE_ACTIVE_DB0FB2BF,
                    FIXTURE_SUBSTATE_39662EFC,
                    FIXTURE_RUNNING_79D116A0,
                    FIXTURE_MAINPID_D7C01CF7,
                    "17"))
            .running(17, INV),
        "A completed-execution default is not a live daemon; SS341 SSC125 start>0/end0");
  }

  @Test
  void snapshot911007IndependentStatePartitionPreservesAllTerminalPredicates() {
    for (String active :
        List.of(
            FIXTURE_INACTIVE_A5714161,
            FIXTURE_ACTIVE_DB0FB2BF,
            FIXTURE_FAILED_33D04BD7,
            "unknown-state")) {
      for (String sub :
          List.of(
              FIXTURE_DEAD_0453462F,
              FIXTURE_EXITED_3D0FE3B1,
              FIXTURE_FAILED_33D04BD7,
              FIXTURE_RUNNING_79D116A0,
              "unknown-substate")) {
        for (String result :
            List.of(FIXTURE_SUCCESS_68E7A699, FIXTURE_EXIT_CODE_BC9E614D, "unknown-result")) {
          boolean stopped =
              (active.equals(FIXTURE_INACTIVE_A5714161) && sub.equals(FIXTURE_DEAD_0453462F))
                  || (active.equals(FIXTURE_ACTIVE_DB0FB2BF) && sub.equals(FIXTURE_EXITED_3D0FE3B1))
                  || (active.equals(FIXTURE_FAILED_33D04BD7)
                      && sub.equals(FIXTURE_FAILED_33D04BD7));
          boolean failed =
              active.equals(FIXTURE_FAILED_33D04BD7)
                  && sub.equals(FIXTURE_FAILED_33D04BD7)
                  && result.equals(FIXTURE_EXIT_CODE_BC9E614D);
          var fields =
              Map.of(
                  FIXTURE_ACTIVESTATE_8ACAC4AA,
                  active,
                  FIXTURE_SUBSTATE_39662EFC,
                  sub,
                  FIXTURE_RESULT_37D8A404,
                  result);
          var backupFields = new TreeMap<>(fields);
          backupFields.put(FIXTURE_EXECMAINSTATUS_179A8E0B, "70");
          var backup = snapshot(InspectorUnitSnapshot.Target.BACKUP, backupFields);
          assertEquals(stopped, backup.quiescent(), fields.toString());
          assertEquals(
              failed ? Optional.of(MorningBackupUnitCycle.Outcome.FAILED) : Optional.empty(),
              backup.backupTerminalAfter(Optional.empty()),
              fields.toString());
          var rejectionFields = new TreeMap<>(fields);
          rejectionFields.put(FIXTURE_EXECMAINSTATUS_179A8E0B, "30");
          assertEquals(
              failed,
              snapshot(InspectorUnitSnapshot.Target.CLEANUP, rejectionFields)
                  .cleanupRejectedAfter(Optional.empty()),
              fields.toString());
          assertEquals(
              failed,
              snapshot(InspectorUnitSnapshot.Target.EXPIRY, rejectionFields)
                  .expiryRejectedAfter(Optional.empty()),
              fields.toString());
          var brokerFields = new TreeMap<>(fields);
          brokerFields.put(FIXTURE_EXECMAINSTATUS_179A8E0B, "143");
          assertEquals(
              failed
                  || (active.equals(FIXTURE_INACTIVE_A5714161)
                      && sub.equals(FIXTURE_DEAD_0453462F)
                      && result.equals(FIXTURE_SUCCESS_68E7A699)),
              snapshot(InspectorUnitSnapshot.Target.ARTEMIS, brokerFields).brokerStoppedNormally(),
              fields.toString());
        }
      }
    }
  }

  @Test
  void snapshot911008StoppedGenerationRequiresAllFiveOriginalExecutionValues() {
    var stopped =
        Map.of(
            FIXTURE_ACTIVESTATE_8ACAC4AA,
            FIXTURE_INACTIVE_A5714161,
            FIXTURE_SUBSTATE_39662EFC,
            FIXTURE_DEAD_0453462F);
    var before = snapshot(InspectorUnitSnapshot.Target.MORNING, stopped);
    assertTrue(before.sameStoppedExecution(before));
    for (var change :
        List.of(
            Map.of(FIXTURE_INVOCATIONID_0F13ED0E, "22222222222222222222222222222222"),
            Map.of(FIXTURE_EXECMAINSTATUS_179A8E0B, "30"),
            Map.of(FIXTURE_EXECMAINSTARTTIMESTAMPMONOTONIC_1FB48E62, "101"),
            Map.of(FIXTURE_EXECMAINEXITTIMESTAMPMONOTONIC_C1411C27, "201"),
            Map.of(FIXTURE_EXECMAINCODE_02C974D2, "2"),
            Map.of(FIXTURE_RESULT_37D8A404, FIXTURE_TIMEOUT_492BD020),
            Map.of(
                FIXTURE_ACTIVESTATE_8ACAC4AA,
                FIXTURE_ACTIVE_DB0FB2BF,
                FIXTURE_SUBSTATE_39662EFC,
                FIXTURE_EXITED_3D0FE3B1))) {
      var fields = new TreeMap<>(stopped);
      fields.putAll(change);
      assertFalse(
          snapshot(InspectorUnitSnapshot.Target.MORNING, fields).sameStoppedExecution(before),
          change.toString());
    }
  }

  @Test
  void snapshot911009StatusTenIsOnlyRecognizedForApprovedMaintenanceTargets() {
    for (var target : NAMES.keySet()) {
      for (String status : List.of("0", "10", "30")) {
        boolean worker =
            List.of(
                    InspectorUnitSnapshot.Target.INSPECTOR,
                    InspectorUnitSnapshot.Target.BACKUP,
                    InspectorUnitSnapshot.Target.CLEANUP,
                    InspectorUnitSnapshot.Target.EXPIRY)
                .contains(target);
        OptionalInt expected =
            worker && status.equals("0")
                ? OptionalInt.of(0)
                : worker && target != InspectorUnitSnapshot.Target.BACKUP && status.equals("10")
                    ? OptionalInt.of(10)
                    : OptionalInt.empty();
        assertEquals(
            expected,
            snapshot(target, Map.of(FIXTURE_EXECMAINSTATUS_179A8E0B, status))
                .receiptAfter(Optional.empty()),
            target + "/" + status);
      }
    }
  }

  private static InspectorUnitSnapshot snapshot(
      InspectorUnitSnapshot.Target target, Map<String, String> changes) {
    boolean simple =
        List.of(
                InspectorUnitSnapshot.Target.ARTEMIS,
                InspectorUnitSnapshot.Target.API,
                InspectorUnitSnapshot.Target.WEB)
            .contains(target);
    boolean remain =
        List.of(
                InspectorUnitSnapshot.Target.INSPECTOR,
                InspectorUnitSnapshot.Target.BACKUP,
                InspectorUnitSnapshot.Target.CLEANUP,
                InspectorUnitSnapshot.Target.EXPIRY)
            .contains(target);
    var fields =
        new TreeMap<>(
            Map.ofEntries(
                Map.entry("Id", NAMES.get(target)),
                Map.entry("LoadState", "loaded"),
                Map.entry(FIXTURE_ACTIVESTATE_8ACAC4AA, FIXTURE_ACTIVE_DB0FB2BF),
                Map.entry(FIXTURE_SUBSTATE_39662EFC, FIXTURE_EXITED_3D0FE3B1),
                Map.entry(FIXTURE_JOB_F32F4C4D, ""),
                Map.entry(FIXTURE_MAINPID_D7C01CF7, "0"),
                Map.entry(FIXTURE_CONTROLPID_32D1DE3E, "0"),
                Map.entry(FIXTURE_INVOCATIONID_0F13ED0E, INV),
                Map.entry(FIXTURE_EXECMAINCODE_02C974D2, "1"),
                Map.entry(FIXTURE_EXECMAINSTATUS_179A8E0B, "0"),
                Map.entry(FIXTURE_EXECMAINSTARTTIMESTAMPMONOTONIC_1FB48E62, "100"),
                Map.entry(FIXTURE_EXECMAINEXITTIMESTAMPMONOTONIC_C1411C27, "200"),
                Map.entry(FIXTURE_RESULT_37D8A404, FIXTURE_SUCCESS_68E7A699),
                Map.entry("Type", simple ? "simple" : "oneshot"),
                Map.entry("Restart", simple ? "on-failure" : "no"),
                Map.entry(FIXTURE_REMAINAFTEREXIT_A99477E7, remain ? "yes" : "no"),
                Map.entry("KillMode", "control-group"),
                Map.entry("SendSIGKILL", "no")));
    fields.putAll(changes);
    var bytes = new StringBuilder();
    fields.forEach((key, value) -> bytes.append(key).append('=').append(value).append('\n'));
    return InspectorUnitSnapshot.parse(
        bytes.toString().getBytes(StandardCharsets.US_ASCII), target);
  }
}
