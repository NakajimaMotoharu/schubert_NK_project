package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS341 7.4; PG167/SSC060; UNIT001..008, 018/021. */
final class InspectorUnitSnapshotTest {
  private static final String FIXTURE_RESULT_SUCCESS_C6F30111 = "Result=success";
  private static final String FIXTURE_RESULT_EXIT_CODE_009C3BFA = "Result=exit-code";
  private static final String FIXTURE_EXECMAINSTATUS_30_43AE239C = "ExecMainStatus=30";
  private static final String FIXTURE_EXECMAINSTATUS_0_226B574B = "ExecMainStatus=0";
  private static final String FIXTURE_EXECMAINSTARTTIMESTAMPMONOTONIC_0_502CCA16 =
      "ExecMainStartTimestampMonotonic=0";
  private static final String FIXTURE_123456789ABCDEF08123456789ABCDEF_8265AB15 =
      "123456789abcdef08123456789abcdef";
  private static final String FIXTURE_ACTIVESTATE_8ACAC4AA = "ActiveState";
  private static final String FIXTURE_SUBSTATE_39662EFC = "SubState";
  private static final String FIXTURE_MAINPID_D7C01CF7 = "MainPID";
  private static final String FIXTURE_CONTROLPID_32D1DE3E = "ControlPID";
  private static final String FIXTURE_JOB_F32F4C4D = "Job";
  private static final String FIXTURE_EXECMAINSTATUS_179A8E0B = "ExecMainStatus";
  private static final String FIXTURE_FAILED_33D04BD7 = "failed";
  static final String GOLDEN =
      "Id=schubert-nk-inbox-inspector.service\nLoadState=loaded\nActiveState=active\nSubState=exited\nJob=\nMainPID=0\nControlPID=0\nInvocationID=123456789abcdef08123456789abcdef\nExecMainCode=1\nExecMainStatus=10\nExecMainStartTimestampMonotonic=1234567\nExecMainExitTimestampMonotonic=2345678\nResult=success\nType=oneshot\nRestart=no\nRemainAfterExit=no\nKillMode=control-group\nSendSIGKILL=no\n";
  static final UUID ID = UUID.fromString("12345678-9abc-def0-8123-456789abcdef");

  @Test
  void rootrec002KnownThirtyIsDataNotSuccessfulReceiptAndUnknownNeverReconciles() {
    for (var target :
        List.of(
            InspectorUnitSnapshot.Target.MORNING,
            InspectorUnitSnapshot.Target.API,
            InspectorUnitSnapshot.Target.WEB)) {
      String text =
          GOLDEN
              .replace(InspectorUnitSnapshot.UNIT, target.unit())
              .replace("ActiveState=active", "ActiveState=failed")
              .replace("SubState=exited", "SubState=failed")
              .replace(FIXTURE_RESULT_SUCCESS_C6F30111, FIXTURE_RESULT_EXIT_CODE_009C3BFA)
              .replace("ExecMainStatus=10", FIXTURE_EXECMAINSTATUS_30_43AE239C);
      if (target != InspectorUnitSnapshot.Target.MORNING)
        text =
            text.replace("Type=oneshot", "Type=simple").replace("Restart=no", "Restart=on-failure");
      var before = InspectorUnitSnapshot.parse(text.getBytes(StandardCharsets.US_ASCII), target);
      assertTrue(before.failedRootGeneration(FIXTURE_123456789ABCDEF08123456789ABCDEF_8265AB15));
      assertTrue(before.receiptAfter(Optional.empty()).isEmpty());
      assertTrue(before.failedRootStillStoppedAfter(before));
      var stopped =
          InspectorUnitSnapshot.parse(
              text.replace("ActiveState=failed", "ActiveState=inactive")
                  .replace("SubState=failed", "SubState=dead")
                  .replace(FIXTURE_RESULT_EXIT_CODE_009C3BFA, FIXTURE_RESULT_SUCCESS_C6F30111)
                  .getBytes(StandardCharsets.US_ASCII),
              target);
      assertTrue(stopped.failedRootStillStoppedAfter(before));
      String cold =
          text.replace("ActiveState=failed", "ActiveState=inactive")
              .replace("SubState=failed", "SubState=dead")
              .replace(FIXTURE_RESULT_EXIT_CODE_009C3BFA, FIXTURE_RESULT_SUCCESS_C6F30111)
              .replace("ExecMainCode=1", "ExecMainCode=0")
              .replace(FIXTURE_EXECMAINSTATUS_30_43AE239C, FIXTURE_EXECMAINSTATUS_0_226B574B)
              .replace(
                  "ExecMainStartTimestampMonotonic=1234567",
                  FIXTURE_EXECMAINSTARTTIMESTAMPMONOTONIC_0_502CCA16)
              .replace("ExecMainExitTimestampMonotonic=2345678", "ExecMainExitTimestampMonotonic=0")
              .replace("InvocationID=123456789abcdef08123456789abcdef", "InvocationID=");
      var collected = InspectorUnitSnapshot.parse(cold.getBytes(StandardCharsets.US_ASCII), target);
      assertTrue(
          collected.failedRootStillStoppedAfter(before),
          "actual previously captured receipt required");
      assertFalse(collected.failedRootStillStoppedAfter(collected), "GC alone is no receipt");
      for (String partial :
          List.of(
              cold.replace(FIXTURE_EXECMAINSTATUS_0_226B574B, FIXTURE_EXECMAINSTATUS_30_43AE239C),
              cold.replace(
                  FIXTURE_EXECMAINSTARTTIMESTAMPMONOTONIC_0_502CCA16,
                  "ExecMainStartTimestampMonotonic=1"),
              cold.replace("ExecMainExitTimestampMonotonic=0", "ExecMainExitTimestampMonotonic=1"),
              cold.replace("ExecMainCode=0", "ExecMainCode=1"),
              cold.replace(FIXTURE_RESULT_SUCCESS_C6F30111, FIXTURE_RESULT_EXIT_CODE_009C3BFA),
              cold.replace("InvocationID=\n", "InvocationID=123456789abcdef08123456789abcdef\n")))
        assertFalse(
            InspectorUnitSnapshot.parse(partial.getBytes(StandardCharsets.US_ASCII), target)
                .failedRootStillStoppedAfter(before));
      assertFalse(stopped.failedRootGeneration(FIXTURE_123456789ABCDEF08123456789ABCDEF_8265AB15));
      for (var change :
          Map.ofEntries(
                  Map.entry(FIXTURE_EXECMAINSTATUS_30_43AE239C, FIXTURE_EXECMAINSTATUS_0_226B574B),
                  Map.entry("ExecMainCode=1", "ExecMainCode=2"),
                  Map.entry(FIXTURE_RESULT_EXIT_CODE_009C3BFA, "Result=timeout"),
                  Map.entry("MainPID=0", "MainPID=200"),
                  Map.entry("ControlPID=0", "ControlPID=200"),
                  Map.entry("Job=\n", "Job=1\n"),
                  Map.entry("InvocationID=123456789abcdef08123456789abcdef", "InvocationID="),
                  Map.entry(
                      "ExecMainStartTimestampMonotonic=1234567",
                      FIXTURE_EXECMAINSTARTTIMESTAMPMONOTONIC_0_502CCA16),
                  Map.entry(
                      "ExecMainExitTimestampMonotonic=2345678", "ExecMainExitTimestampMonotonic=1"))
              .entrySet()) {
        var bad =
            InspectorUnitSnapshot.parse(
                text.replace(change.getKey(), change.getValue())
                    .getBytes(StandardCharsets.US_ASCII),
                target);
        assertFalse(bad.failedRootGeneration(FIXTURE_123456789ABCDEF08123456789ABCDEF_8265AB15));
        assertFalse(bad.failedRootStillStoppedAfter(before));
      }
      assertFalse(before.failedRootGeneration("wrong"));
      assertFalse(
          before.failedRootStillStoppedAfter(
              InspectorUnitSnapshot.parse(GOLDEN.getBytes(StandardCharsets.US_ASCII))));
      assertThrows(NullPointerException.class, () -> before.failedRootGeneration(null));
      assertThrows(NullPointerException.class, () -> before.failedRootStillStoppedAfter(null));
    }
    assertFalse(
        InspectorUnitSnapshot.parse(GOLDEN.getBytes(StandardCharsets.US_ASCII))
            .failedRootGeneration(FIXTURE_123456789ABCDEF08123456789ABCDEF_8265AB15));
  }

  @Test
  void strictGolden() throws Exception {
    String backup =
        GOLDEN
            .replace(InspectorUnitSnapshot.UNIT, InspectorUnitSnapshot.Target.BACKUP.unit())
            .replace("RemainAfterExit=no", "RemainAfterExit=yes");
    assertEquals("schubert-nk-backup.service", InspectorUnitSnapshot.Target.BACKUP.unit());
    assertEquals(InspectorUnitSnapshot.UNIT, InspectorUnitSnapshot.Target.INSPECTOR.unit());
    var backupState =
        InspectorUnitSnapshot.parse(
            backup.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.BACKUP);
    assertTrue(backupState.quiescent());
    assertTrue(
        backupState.receiptAfter(Optional.empty()).isEmpty(),
        "backup status10 must never be successful");
    assertEquals(
        OptionalInt.of(0),
        InspectorUnitSnapshot.parse(
                backup
                    .replace("ExecMainStatus=10", FIXTURE_EXECMAINSTATUS_0_226B574B)
                    .getBytes(StandardCharsets.US_ASCII),
                InspectorUnitSnapshot.Target.BACKUP)
            .receiptAfter(Optional.empty()));
    assertThrows(
        StopGateException.class,
        () ->
            InspectorUnitSnapshot.parse(
                backup
                    .replace("RemainAfterExit=yes", "RemainAfterExit=no")
                    .getBytes(StandardCharsets.US_ASCII),
                InspectorUnitSnapshot.Target.BACKUP));
    assertThrows(NullPointerException.class, () -> InspectorUnitSnapshot.parse(new byte[1], null));
    String running =
        backup
            .replace("MainPID=0", "MainPID=123")
            .replace("ActiveState=active", "ActiveState=activating")
            .replace("SubState=exited", "SubState=start");
    String invocation = FIXTURE_123456789ABCDEF08123456789ABCDEF_8265AB15;
    assertTrue(
        InspectorUnitSnapshot.parse(
                running.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.BACKUP)
            .running(123, invocation));
    for (long pid : new long[] {1, 2147483648L, 124})
      assertFalse(
          InspectorUnitSnapshot.parse(
                  running.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.BACKUP)
              .running(pid, invocation));
    assertFalse(
        InspectorUnitSnapshot.parse(
                running.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.BACKUP)
            .running(123, "public_wrong"));
    assertThrows(NullPointerException.class, () -> backupState.running(123, null));
    for (var change :
        Map.of(
                "ControlPID=0",
                "ControlPID=1",
                "ExecMainStartTimestampMonotonic=1234567",
                FIXTURE_EXECMAINSTARTTIMESTAMPMONOTONIC_0_502CCA16,
                "ActiveState=activating",
                "ActiveState=active",
                "SubState=start",
                "SubState=exited")
            .entrySet())
      assertFalse(
          InspectorUnitSnapshot.parse(
                  running
                      .replace(change.getKey(), change.getValue())
                      .getBytes(StandardCharsets.US_ASCII),
                  InspectorUnitSnapshot.Target.BACKUP)
              .running(123, invocation));
    byte[] bytes = GOLDEN.getBytes(StandardCharsets.US_ASCII);
    assertEquals(373, bytes.length);
    assertEquals(
        "2170fc2e71a4ba50519bc2f123d0bf75fcc46adab033645b7b68b5c513c345f6",
        HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes)));
    try (var resource =
        Objects.requireNonNull(getClass().getResourceAsStream("/inspector/unit-golden.txt"))) {
      assertArrayEquals(bytes, resource.readAllBytes());
    }
    var state = InspectorUnitSnapshot.parse(bytes);
    assertTrue(state.quiescent());
    assertEquals(Optional.of(ID), state.invocationId());
    assertEquals(OptionalInt.of(10), state.receiptAfter(Optional.empty()));
    assertEquals(OptionalInt.empty(), state.receiptAfter(Optional.of(ID)));
    assertEquals("InspectorUnitSnapshot[redacted]", state.toString());
    Path target = Path.of("target", "inspector-unit-traces");
    Files.createDirectories(target);
    Files.writeString(
        target.resolve("PT-OPS-UNIT-001-state.txt"),
        "quiescent="
            + state.quiescent()
            + "\nreceipt="
            + state.receiptAfter(Optional.empty()).orElseThrow()
            + "\nsameInvocationReceipt="
            + (state.receiptAfter(Optional.of(ID)).isEmpty() ? "none" : "present")
            + "\n");
  }

  @Test
  void propertyInventory() {
    var lines = new ArrayList<>(List.of(GOLDEN.split("\n")));
    assertEquals(18, lines.size());
    for (int i = 0; i < 18; i++) {
      var missing = new ArrayList<>(lines);
      missing.remove(i);
      invalid(String.join("\n", missing) + "\n");
      var duplicate = new ArrayList<>(lines);
      duplicate.set(i, lines.get((i + 1) % 18));
      invalid(String.join("\n", duplicate) + "\n");
      var unknown = new ArrayList<>(lines);
      unknown.set(i, "Unknown=x");
      invalid(String.join("\n", unknown) + "\n");
    }
    Collections.reverse(lines);
    assertTrue(parse(GOLDEN).matches(parse(String.join("\n", lines) + "\n")));
    invalid(GOLDEN + "Unknown=x\n");
    invalid(GOLDEN + "trailing-without-newline");
    invalid(GOLDEN.replace("Job=", "=x"));
    invalid(GOLDEN.replace("Job=", "NoSeparator"));
    for (var change :
        Map.of(
                "Id",
                "other.service",
                "LoadState",
                "not-found",
                "Type",
                "simple",
                "Restart",
                "always",
                "KillMode",
                "process",
                "SendSIGKILL",
                "yes",
                "RemainAfterExit",
                "true")
            .entrySet()) invalid(with(change.getKey(), change.getValue()));
    for (String key : List.of(FIXTURE_ACTIVESTATE_8ACAC4AA, FIXTURE_SUBSTATE_39662EFC, "Result")) {
      for (String bad : List.of("", "A", "has space", "x=y", "_x", "-x", "x".repeat(65)))
        invalid(with(key, bad));
      assertDoesNotThrow(() -> parse(with(key, "x".repeat(64))));
    }
  }

  @Test
  void byteBoundaries() {
    byte[] original = GOLDEN.getBytes(StandardCharsets.US_ASCII);
    for (int position = 0; position < original.length; position++)
      for (byte bad : new byte[] {0, 13, (byte) 128}) {
        byte[] changed = original.clone();
        changed[position] = bad;
        malformed(() -> InspectorUnitSnapshot.parse(changed));
      }
    for (int size : new int[] {0, 1, 2047, 2048, 2049, 65536}) invalid("x".repeat(size));
    invalid(GOLDEN.substring(0, GOLDEN.length() - 1));
    invalid(GOLDEN + "\n");
    invalid(GOLDEN.replace("Job=\n", "Job=\t\n"));
    invalid(GOLDEN.replace("Job=\n", "Job=\u007f\n"));
  }

  @Test
  void scalarBounds() {
    for (String key :
        List.of(FIXTURE_MAINPID_D7C01CF7, FIXTURE_CONTROLPID_32D1DE3E, FIXTURE_JOB_F32F4C4D)) {
      for (String good : List.of("1", "4294967295"))
        assertDoesNotThrow(() -> parse(with(key, good)));
      for (String bad :
          List.of(
              "4294967296",
              "-1",
              "+1",
              "01",
              " 1",
              "1 ",
              "1e2",
              "1.0",
              "18446744073709551615",
              "9".repeat(21))) invalid(with(key, bad));
    }
    invalid(with(FIXTURE_JOB_F32F4C4D, "0"));
    for (String key : List.of(FIXTURE_MAINPID_D7C01CF7, FIXTURE_CONTROLPID_32D1DE3E))
      invalid(with(key, ""));
    for (String key :
        List.of("ExecMainStartTimestampMonotonic", "ExecMainExitTimestampMonotonic")) {
      for (String good : List.of("0", "1", "18446744073709551615"))
        assertDoesNotThrow(() -> parse(with(key, good)));
      for (String bad : List.of("", "-1", "01", "+1", "18446744073709551616", "1e2"))
        invalid(with(key, bad));
    }
    for (int code = 0; code <= 6; code++)
      for (int status = 0; status <= 255; status++) {
        var state =
            parse(
                with(
                    with("ExecMainCode", Integer.toString(code)),
                    FIXTURE_EXECMAINSTATUS_179A8E0B,
                    Integer.toString(status)));
        assertEquals(
            code == 1 && (status == 0 || status == 10),
            state.receiptAfter(Optional.empty()).isPresent());
      }
    for (String key : List.of("ExecMainCode", FIXTURE_EXECMAINSTATUS_179A8E0B)) {
      for (String bad : List.of("", "-1", "01", "+1", "256")) invalid(with(key, bad));
    }
    invalid(with("ExecMainCode", "7"));
    for (String id : List.of("", "f".repeat(32), "0".repeat(31) + "1"))
      assertDoesNotThrow(() -> parse(with("InvocationID", id)));
    for (String id :
        List.of(
            "0".repeat(32),
            "A".repeat(32),
            "f".repeat(31),
            "f".repeat(33),
            ID.toString(),
            "g".repeat(32))) invalid(with("InvocationID", id));
  }

  @Test
  void quiescentStates() {
    for (String active :
        List.of(
            "inactive", "active", FIXTURE_FAILED_33D04BD7, "activating", "deactivating", "unknown"))
      for (String sub :
          List.of("dead", "exited", FIXTURE_FAILED_33D04BD7, "running", "start", "unknown")) {
        String input =
            with(with(FIXTURE_ACTIVESTATE_8ACAC4AA, active), FIXTURE_SUBSTATE_39662EFC, sub);
        boolean expected =
            Set.of("inactive/dead", "active/exited", "failed/failed").contains(active + "/" + sub);
        assertEquals(expected, parse(input).quiescent(), active + "/" + sub);
      }
    for (String key :
        List.of(FIXTURE_MAINPID_D7C01CF7, FIXTURE_CONTROLPID_32D1DE3E, FIXTURE_JOB_F32F4C4D))
      assertFalse(parse(with(key, "1")).quiescent(), key);
    assertTrue(parse(with("RemainAfterExit", "yes")).quiescent());
    assertFalse(parse(with(FIXTURE_MAINPID_D7C01CF7, "4294967295")).quiescent());
  }

  @Test
  void freshReceipt() {
    assertEquals(OptionalInt.of(10), parse(GOLDEN).receiptAfter(Optional.of(new UUID(0, 1))));
    assertEquals(
        OptionalInt.of(0),
        parse(with(FIXTURE_EXECMAINSTATUS_179A8E0B, "0")).receiptAfter(Optional.empty()));
    assertTrue(parse(with("InvocationID", "")).receiptAfter(Optional.empty()).isEmpty());
    for (String key :
        List.of(FIXTURE_MAINPID_D7C01CF7, FIXTURE_CONTROLPID_32D1DE3E, FIXTURE_JOB_F32F4C4D))
      assertTrue(parse(with(key, "1")).receiptAfter(Optional.empty()).isEmpty());
    assertTrue(
        parse(
                with(
                    with(FIXTURE_ACTIVESTATE_8ACAC4AA, FIXTURE_FAILED_33D04BD7),
                    FIXTURE_SUBSTATE_39662EFC,
                    FIXTURE_FAILED_33D04BD7))
            .receiptAfter(Optional.empty())
            .isEmpty());
    assertEquals(
        OptionalInt.of(10),
        parse(
                with(
                    with(FIXTURE_ACTIVESTATE_8ACAC4AA, "inactive"),
                    FIXTURE_SUBSTATE_39662EFC,
                    "dead"))
            .receiptAfter(Optional.empty()));
    for (String result : List.of("timeout", "exit-code", "signal", "core-dump", "unknown"))
      assertTrue(parse(with("Result", result)).receiptAfter(Optional.empty()).isEmpty());
    for (String[] values :
        List.of(
            new String[] {"0", "0"},
            new String[] {"0", "1"},
            new String[] {"1", "0"},
            new String[] {"2", "1"}))
      assertTrue(
          parse(
                  with(
                      with("ExecMainStartTimestampMonotonic", values[0]),
                      "ExecMainExitTimestampMonotonic",
                      values[1]))
              .receiptAfter(Optional.empty())
              .isEmpty());
    for (String time : List.of("1", "18446744073709551615"))
      assertEquals(
          OptionalInt.of(10),
          parse(
                  with(
                      with("ExecMainStartTimestampMonotonic", time),
                      "ExecMainExitTimestampMonotonic",
                      time))
              .receiptAfter(Optional.empty()));
  }

  @Test
  void normalExitCodeIsLiteralOnlyAfterNormalMainCode() {
    // PT-SNAPSHOT-NORMAL-EXIT-001: SS341 7.4 manager data, not a genuine receipt.
    for (int status : new int[] {0, 1, 10, 30, 70, 143, 255}) {
      var state = parse(with(FIXTURE_EXECMAINSTATUS_179A8E0B, Integer.toString(status)));
      assertEquals(status, state.normalExitCode());
    }
    for (int code : new int[] {0, 2, 3, 4, 5, 6}) {
      var state = parse(with("ExecMainCode", Integer.toString(code)));
      malformed(state::normalExitCode);
    }
  }

  @Test
  void immutabilityAndNull() {
    byte[] input = GOLDEN.getBytes(StandardCharsets.US_ASCII);
    var state = InspectorUnitSnapshot.parse(input);
    Arrays.fill(input, (byte) 0);
    assertTrue(state.matches(parse(GOLDEN)));
    assertFalse(state.matches(parse(with(FIXTURE_EXECMAINSTATUS_179A8E0B, "0"))));
    assertEquals(Optional.of(ID), state.invocationId());
    assertThrows(NullPointerException.class, () -> InspectorUnitSnapshot.parse(null));
    assertThrows(NullPointerException.class, () -> state.matches(null));
    assertThrows(NullPointerException.class, () -> state.receiptAfter(null));
    assertFalse(state.toString().contains(ID.toString()));
    assertFalse(state.toString().contains("1234567"));
  }

  @Test
  void concurrentSnapshots() throws Exception {
    try (var pool = Executors.newFixedThreadPool(8)) {
      List<Future<InspectorUnitSnapshot>> tasks = new ArrayList<>();
      for (int i = 0; i < 64; i++) {
        final int status = i % 2 == 0 ? 0 : 10;
        tasks.add(
            pool.submit(
                () -> parse(with(FIXTURE_EXECMAINSTATUS_179A8E0B, Integer.toString(status)))));
      }
      for (int i = 0; i < 64; i++) {
        var state = tasks.get(i).get(10, TimeUnit.SECONDS);
        assertEquals(OptionalInt.of(i % 2 == 0 ? 0 : 10), state.receiptAfter(Optional.empty()));
        assertTrue(state.quiescent());
      }
    }
  }

  static InspectorUnitSnapshot parse(String value) {
    return InspectorUnitSnapshot.parse(value.getBytes(StandardCharsets.US_ASCII));
  }

  static String with(String key, String value) {
    return with(GOLDEN, key, value);
  }

  static String with(String source, String key, String value) {
    List<String> lines = new ArrayList<>(List.of(source.split("\n")));
    int at = -1;
    for (int i = 0; i < lines.size(); i++) if (lines.get(i).startsWith(key + "=")) at = i;
    assertTrue(at >= 0, "fixture field must exist");
    lines.set(at, key + "=" + value);
    return String.join("\n", lines) + "\n";
  }

  static void invalid(String input) {
    malformed(() -> parse(input));
  }

  static void malformed(org.junit.jupiter.api.function.Executable action) {
    var failure = assertThrows(StopGateException.class, action);
    assertEquals(StopGateFailure.MALFORMED_STATE, failure.reason());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
