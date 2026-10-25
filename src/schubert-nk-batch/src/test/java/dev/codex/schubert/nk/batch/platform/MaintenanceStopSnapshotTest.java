package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;

/** MSTOP001..007: independent 12field literal, not genuine root/kernel or stop acceptance. */
final class MaintenanceStopSnapshotTest {
  private static final List<String> NAMES =
      List.of(
          "caddy.service",
          "schubert-nk-web.service",
          "schubert-nk-api.service",
          "schubert-nk-cleanup.service",
          "schubert-nk-inbox-inspector.service",
          "schubert-nk-expiry-cleanup.service",
          "schubert-nk-backup.service",
          "artemis.service");
  private static final String COLD =
      "Id=caddy.service\nLoadState=loaded\nActiveState=inactive\nSubState=dead\nJob=\nMainPID=0\nControlPID=0\nSlice=system.slice\nDelegate=no\nControlGroup=\nInvocationID=\nStateChangeTimestampMonotonic=0\n";

  private static byte[] bytes(String value) {
    return value.getBytes(StandardCharsets.US_ASCII);
  }

  private static MaintenanceStopSnapshot parse(String value) {
    return MaintenanceStopSnapshot.parse(MaintenanceUnit.CADDY, bytes(value));
  }

  private static String replace(String key, String value) {
    String old = COLD.lines().filter(line -> line.startsWith(key + "=")).findFirst().orElseThrow();
    return COLD.replace(old + "\n", key + "=" + value + "\n");
  }

  private static void rejected(String value) {
    byte[] input = bytes(value);
    byte[] expected = input.clone();
    StopGateException failure =
        assertThrows(
            StopGateException.class,
            () -> MaintenanceStopSnapshot.parse(MaintenanceUnit.CADDY, input));
    assertEquals(StopGateFailure.MALFORMED_STATE, failure.reason());
    assertArrayEquals(expected, input, "caller retains its original byte ownership");
  }

  @Test
  void mstop001FixedNamesAndIndependentTerminalVectors() {
    assertEquals(8, MaintenanceUnit.values().length);
    for (int i = 0; i < 8; i++) {
      MaintenanceUnit unit = MaintenanceUnit.values()[i];
      assertEquals(NAMES.get(i), unit.serviceName());
      assertEquals("/system.slice/" + NAMES.get(i), unit.controlGroup());
      var snapshot =
          MaintenanceStopSnapshot.parse(unit, bytes(COLD.replace("caddy.service", NAMES.get(i))));
      assertSame(unit, snapshot.unit());
      assertEquals("", snapshot.controlGroup());
      assertTrue(snapshot.quiescent());
      assertEquals("MaintenanceStopSnapshot[redacted]", snapshot.toString());
    }
    assertTrue(parse(COLD.replace("inactive", "failed").replace("dead", "failed")).quiescent());
    assertEquals(
        "/system.slice/caddy.service",
        parse(replace("ControlGroup", "/system.slice/caddy.service")).controlGroup());
    var lines = new ArrayList<>(COLD.stripTrailing().lines().toList());
    for (int i = 0; i < 12; i++) {
      Collections.rotate(lines, 1);
      assertTrue(parse(String.join("\n", lines) + "\n").matches(parse(COLD)));
    }
  }

  @Test
  void mstop002MissingDuplicateUnknownAndSeparators() {
    for (String line : COLD.lines().toList()) {
      rejected(COLD.replace(line + "\n", ""));
      rejected(COLD + line + "\n");
      rejected(COLD.replace(line + "\n", "Unknown" + line + "\n"));
      rejected(COLD.replace(line + "\n", "no-equals\n"));
      rejected(COLD.replace(line + "\n", "=empty\n"));
      rejected(COLD.replace(line + "\n", line + "=extra\n"));
    }
    rejected(COLD.replace("Slice=system.slice", "Id=caddy.service"));
    rejected(COLD.stripTrailing());
    rejected(COLD + "x");
    rejected(COLD + "\n");
    rejected(COLD.replace("Job=\n", "Job=\nUnknown=\n"));
  }

  @Test
  void mstop003ByteBoundsNullAndOriginalOwnership() {
    rejected("");
    for (int position = 0; position < COLD.length(); position++) {
      for (int value : List.of(0, 13, 127, 128, 255)) {
        byte[] input = bytes(COLD);
        byte[] original;
        input[position] = (byte) value;
        original = input.clone();
        assertThrows(
            StopGateException.class,
            () -> MaintenanceStopSnapshot.parse(MaintenanceUnit.CADDY, input));
        assertArrayEquals(original, input);
      }
    }
    String longest = replace("SubState", "x".repeat(2048 - COLD.length() + 4));
    assertEquals(2048, longest.length());
    rejected(longest);
    rejected(longest + "x");
    assertThrows(
        NullPointerException.class, () -> MaintenanceStopSnapshot.parse(null, bytes(COLD)));
    assertThrows(
        NullPointerException.class,
        () -> MaintenanceStopSnapshot.parse(MaintenanceUnit.CADDY, null));
    byte[] input = bytes(COLD);
    var snapshot = MaintenanceStopSnapshot.parse(MaintenanceUnit.CADDY, input);
    Arrays.fill(input, (byte) 0);
    assertTrue(snapshot.matches(parse(COLD)));
  }

  @Test
  void mstop004FixedPlacementAndNonTerminalStates() {
    for (var entry :
        Map.of(
                "Id", List.of("", "other.service"),
                "LoadState", List.of("", "not-found", "masked", "error"),
                "Slice", List.of("", "other.slice"),
                "Delegate", List.of("", "yes"),
                "ControlGroup",
                    List.of("/", "/other.slice/caddy.service", "/system.slice/other.service"),
                "ActiveState", List.of("", "UP", "-active"),
                "SubState", List.of("", "UP", "x".repeat(65)),
                "Job", List.of("0", "00", "-1", "4294967296", "queued"),
                "MainPID", List.of("", "00", "-1", "4294967296"),
                "ControlPID", List.of("", "00", "-1", "4294967296"))
            .entrySet()) {
      for (String value : entry.getValue()) rejected(replace(entry.getKey(), value));
    }
    for (var entry :
        Map.of(
                "Job", List.of("1", "4294967295"),
                "MainPID", List.of("1", "4294967295"),
                "ControlPID", List.of("1", "4294967295"),
                "ActiveState", List.of("active", "activating", "unknown"),
                "SubState", List.of("running", "exited", "unknown"))
            .entrySet()) {
      for (String value : entry.getValue())
        assertFalse(parse(replace(entry.getKey(), value)).quiescent());
    }
    assertFalse(parse(COLD.replace("inactive", "active").replace("dead", "exited")).quiescent());
  }

  @Test
  void mstop005InvocationAndUnsignedTimestampDomains() {
    assertTrue(parse(replace("InvocationID", "0123456789abcdef0123456789abcdef")).quiescent());
    for (String value :
        List.of("0".repeat(32), "a".repeat(31), "a".repeat(33), "A".repeat(32), "g".repeat(32)))
      rejected(replace("InvocationID", value));
    for (String value : List.of("0", "1", "18446744073709551615"))
      assertTrue(parse(replace("StateChangeTimestampMonotonic", value)).quiescent());
    for (String value :
        List.of("", "00", "-1", "+1", "1.0", "18446744073709551616", "1".repeat(21)))
      rejected(replace("StateChangeTimestampMonotonic", value));
  }

  @Test
  void mstop006AbaAndAllFieldChangesStayUnmatched() {
    var original = parse(COLD);
    assertTrue(original.matches(parse(COLD)));
    assertFalse(original.matches(parse(replace("StateChangeTimestampMonotonic", "1"))));
    assertFalse(
        original.matches(parse(replace("InvocationID", "0123456789abcdef0123456789abcdef"))));
    assertFalse(original.matches(parse(replace("MainPID", "1"))));
    assertFalse(
        original.matches(
            MaintenanceStopSnapshot.parse(
                MaintenanceUnit.WEB,
                bytes(COLD.replace("caddy.service", "schubert-nk-web.service")))));
    assertTrue(original.quiescent());
    assertThrows(NullPointerException.class, () -> original.matches(null));
  }

  @Test
  void mstop007IndependentParallelAndNoAmbientAuthorization() throws Exception {
    try (var workers = Executors.newFixedThreadPool(8)) {
      var tasks = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 64; i++) {
        tasks.add(
            () -> {
              var snapshot = parse(COLD);
              assertEquals("MaintenanceStopSnapshot[redacted]", snapshot.toString());
              return snapshot.matches(parse(COLD)) && snapshot.quiescent();
            });
      }
      for (var result : workers.invokeAll(tasks)) assertTrue(result.get());
    }
    try {
      Thread.currentThread().interrupt();
      assertTrue(parse(COLD).quiescent(), "pure parsing makes no root/process/startup admission");
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
  }
}
