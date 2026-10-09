package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.TreeMap;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * NK-DAT-001/NK-OPS-001; DAT009/OPS009; UI212/251; SS341 7.4/343/352; WBS-P004-04;
 * PT-SNAPSHOT-911001..007. Literal observations, never Unit/kernel/owner authority.
 */
final class InspectorHeldStateContractTest {
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
              Map.of("ActiveState", "inactive", "SubState", "dead"),
              Map.of("SubState", "running"),
              Map.of("Job", "7"),
              Map.of("MainPID", "17"),
              Map.of("ControlPID", "18"))) {
        var observed = snapshot(target, change);
        assertFalse(observed.heldCleanup(), target + " " + change);
        assertFalse(observed.heldMaintenance(), target + " " + change);
      }
    }
    for (var target :
        List.of(InspectorUnitSnapshot.Target.INSPECTOR, InspectorUnitSnapshot.Target.EXPIRY)) {
      assertFalse(snapshot(target, Map.of("RemainAfterExit", "no")).heldMaintenance());
    }
  }

  @Test
  void snapshot911003BrokerNormalTermRequiresCompleteOldStopProfile() {
    for (var terminal :
        List.of(
            Map.of("ActiveState", "inactive", "SubState", "dead", "Result", "success"),
            Map.of("ActiveState", "failed", "SubState", "failed", "Result", "exit-code"))) {
      var input = new TreeMap<>(terminal);
      input.put("ExecMainStatus", "143");
      assertTrue(snapshot(InspectorUnitSnapshot.Target.ARTEMIS, input).brokerStoppedNormally());
      for (var change :
          List.of(
              Map.of("MainPID", "17"),
              Map.of("ControlPID", "18"),
              Map.of("Job", "7"),
              Map.of("InvocationID", ""),
              Map.of("ExecMainCode", "2"),
              Map.of("ExecMainStatus", "0"),
              Map.of("ExecMainStartTimestampMonotonic", "0"),
              Map.of("ExecMainExitTimestampMonotonic", "99"),
              Map.of("Result", "timeout"),
              Map.of("SubState", "running"),
              Map.of("ActiveState", "activating"))) {
        var bad = new TreeMap<>(input);
        bad.putAll(change);
        assertFalse(
            snapshot(InspectorUnitSnapshot.Target.ARTEMIS, bad).brokerStoppedNormally(),
            change.toString());
      }
    }
    assertFalse(
        snapshot(InspectorUnitSnapshot.Target.CLEANUP, Map.of("ExecMainStatus", "143"))
            .brokerStoppedNormally());
  }

  @Test
  void snapshot911004InactiveInspectorNeedsRemainYesAndNoOutstandingProcess() {
    var idle = Map.of("ActiveState", "inactive", "SubState", "dead");
    for (var target : NAMES.keySet()) {
      assertTrue(snapshot(target, idle).inactiveBaseline(), target.name());
      assertFalse(snapshot(target, Map.of()).inactiveBaseline());
      assertFalse(
          snapshot(target, Map.of("ActiveState", "inactive", "SubState", "running"))
              .inactiveBaseline());
      assertFalse(
          snapshot(target, Map.of("ActiveState", "inactive", "SubState", "dead", "Job", "1"))
              .inactiveBaseline());
    }
    assertFalse(
        snapshot(
                InspectorUnitSnapshot.Target.INSPECTOR,
                Map.of("ActiveState", "inactive", "SubState", "dead", "RemainAfterExit", "no"))
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
            "ActiveState",
            "failed",
            "SubState",
            "failed",
            "Result",
            "exit-code",
            "ExecMainStatus",
            "70");
    assertEquals(
        Optional.of(MorningBackupUnitCycle.Outcome.FAILED),
        snapshot(target, failure).backupTerminalAfter(Optional.empty()));
    assertTrue(snapshot(target, failure).backupTerminalAfter(Optional.of(SAME)).isEmpty());
    for (var change :
        List.of(
            Map.of("ExecMainStartTimestampMonotonic", "0"),
            Map.of("ExecMainExitTimestampMonotonic", "99"),
            Map.of("MainPID", "17"),
            Map.of("ControlPID", "18"),
            Map.of("Job", "7"),
            Map.of("InvocationID", ""),
            Map.of("ExecMainCode", "2"),
            Map.of("ExecMainStatus", "0"),
            Map.of("ActiveState", "inactive", "SubState", "dead"),
            Map.of("Result", "timeout"))) {
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
              "ActiveState",
              "failed",
              "SubState",
              "failed",
              "Result",
              "exit-code",
              "ExecMainStatus",
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
        noRemain.put("RemainAfterExit", "no");
        var observedNoRemain = snapshot(target, noRemain);
        assertTrue(observedNoRemain.quiescent());
        assertFalse(observedNoRemain.expiryRejectedAfter(Optional.empty()));
      }
      for (var change :
          List.of(
              Map.of("ExecMainStartTimestampMonotonic", "0"),
              Map.of("ExecMainExitTimestampMonotonic", "99"))) {
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
                "ActiveState", "active",
                "SubState", "running",
                "MainPID", "17",
                "ExecMainCode", "0",
                "ExecMainExitTimestampMonotonic", "0"));
    assertTrue(broker.running(17, INV));
    assertFalse(broker.running(18, INV));
    assertFalse(broker.running(17, "22222222222222222222222222222222"));
    assertFalse(
        snapshot(
                InspectorUnitSnapshot.Target.ARTEMIS,
                Map.of("ActiveState", "active", "SubState", "running", "MainPID", "17"))
            .running(17, INV),
        "A completed-execution default is not a live daemon; SS341 SSC125 start>0/end0");
  }

  @Test
  void snapshot911007IndependentStatePartitionPreservesAllTerminalPredicates() {
    for (String active : List.of("inactive", "active", "failed", "unknown-state")) {
      for (String sub : List.of("dead", "exited", "failed", "running", "unknown-substate")) {
        for (String result : List.of("success", "exit-code", "unknown-result")) {
          boolean stopped =
              (active.equals("inactive") && sub.equals("dead"))
                  || (active.equals("active") && sub.equals("exited"))
                  || (active.equals("failed") && sub.equals("failed"));
          boolean failed =
              active.equals("failed") && sub.equals("failed") && result.equals("exit-code");
          var fields = Map.of("ActiveState", active, "SubState", sub, "Result", result);
          var backupFields = new TreeMap<>(fields);
          backupFields.put("ExecMainStatus", "70");
          var backup = snapshot(InspectorUnitSnapshot.Target.BACKUP, backupFields);
          assertEquals(stopped, backup.quiescent(), fields.toString());
          assertEquals(
              failed ? Optional.of(MorningBackupUnitCycle.Outcome.FAILED) : Optional.empty(),
              backup.backupTerminalAfter(Optional.empty()),
              fields.toString());
          var rejectionFields = new TreeMap<>(fields);
          rejectionFields.put("ExecMainStatus", "30");
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
          brokerFields.put("ExecMainStatus", "143");
          assertEquals(
              failed
                  || (active.equals("inactive") && sub.equals("dead") && result.equals("success")),
              snapshot(InspectorUnitSnapshot.Target.ARTEMIS, brokerFields).brokerStoppedNormally(),
              fields.toString());
        }
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
                Map.entry("ActiveState", "active"),
                Map.entry("SubState", "exited"),
                Map.entry("Job", ""),
                Map.entry("MainPID", "0"),
                Map.entry("ControlPID", "0"),
                Map.entry("InvocationID", INV),
                Map.entry("ExecMainCode", "1"),
                Map.entry("ExecMainStatus", "0"),
                Map.entry("ExecMainStartTimestampMonotonic", "100"),
                Map.entry("ExecMainExitTimestampMonotonic", "200"),
                Map.entry("Result", "success"),
                Map.entry("Type", simple ? "simple" : "oneshot"),
                Map.entry("Restart", simple ? "on-failure" : "no"),
                Map.entry("RemainAfterExit", remain ? "yes" : "no"),
                Map.entry("KillMode", "control-group"),
                Map.entry("SendSIGKILL", "no")));
    fields.putAll(changes);
    var bytes = new StringBuilder();
    fields.forEach((key, value) -> bytes.append(key).append('=').append(value).append('\n'));
    return InspectorUnitSnapshot.parse(
        bytes.toString().getBytes(StandardCharsets.US_ASCII), target);
  }
}
