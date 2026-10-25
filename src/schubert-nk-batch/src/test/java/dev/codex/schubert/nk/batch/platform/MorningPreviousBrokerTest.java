package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SSC131 ISSSTOP001..004: independent full closed generation/anchor/byte oracle. */
final class MorningPreviousBrokerTest {
  static final String START =
      BrokerJournalEvidenceTest.row(
          "AMQ221001: Apache Artemis Message Broker version 2.56.0 [schubert-nk-broker, nodeID=public-fixture]",
          3);
  static final String STOP =
      BrokerJournalEvidenceTest.row(
              "AMQ221002: Apache Artemis Message Broker version 2.56.0 [schubert-nk-broker] stopped, uptime 2 hours",
              4)
          .replace("1234567", "1234568");
  static final String FULL = BrokerJournalEvidenceTest.GOLDEN + STOP;

  static InspectorUnitSnapshot cold() {
    return MorningBrokerUnitCycleTest.parse(
        MorningBrokerUnitCycleTest.LIVE
            .replace("ActiveState=active", "ActiveState=inactive")
            .replace("SubState=running", "SubState=dead")
            .replace("MainPID=43", "MainPID=0")
            .replace("InvocationID=" + "7".repeat(32), "InvocationID=")
            .replace(
                "ExecMainStartTimestampMonotonic=1234567", "ExecMainStartTimestampMonotonic=0"));
  }

  static InspectorUnitSnapshot stopped() {
    return MorningBrokerUnitCycleTest.parse(
        MorningBrokerUnitCycleTest.LIVE
            .replace("ActiveState=active", "ActiveState=inactive")
            .replace("SubState=running", "SubState=dead")
            .replace("MainPID=43", "MainPID=0")
            .replace("ExecMainCode=0", "ExecMainCode=1")
            .replace("ExecMainStatus=0", "ExecMainStatus=143")
            .replace("ExecMainExitTimestampMonotonic=0", "ExecMainExitTimestampMonotonic=1234568"));
  }

  static final class Fixture implements MorningPreviousBroker.Query {
    String last = STOP;
    String start = START;
    String full = FULL;
    String bootHex = "11111111111141118111111111111111";
    int calls;
    boolean drift;
    boolean nullBytes;
    final List<byte[]> delivered = new ArrayList<>();
    Throwable failure;

    public byte[] read(List<String> command, int limit, long nanos) throws IOException {
      calls++;
      assertEquals("/usr/bin/journalctl", command.getFirst());
      assertTrue(command.contains("_SYSTEMD_UNIT=artemis.service"));
      assertTrue(command.contains("_BOOT_ID=" + bootHex));
      assertTrue(nanos > 0);
      if (failure instanceof IOException known) throw known;
      if (failure instanceof RuntimeException unknown) throw unknown;
      if (failure instanceof Error fatal) throw fatal;
      if (nullBytes) return null;
      boolean anchor = command.contains("--reverse");
      assertEquals(anchor ? 65536 : 4 * 1024 * 1024, limit);
      String value =
          anchor ? (command.stream().anyMatch(s -> s.startsWith("--grep=")) ? start : last) : full;
      if (drift && calls == 4) value = value.replace("cursor-4", "cursor-5");
      value = value.replace("11111111111141118111111111111111", bootHex);
      byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
      delivered.add(bytes);
      return bytes;
    }

    void erased() {
      for (byte[] bytes : delivered) assertArrayEquals(new byte[bytes.length], bytes);
    }
  }

  @Test
  void issstop001ColdIsNotReceiptAndActualLatestClosedGenerationIsRetained() throws Exception {
    var f = new Fixture();
    var actual =
        MorningPreviousBroker.collect(
            BrokerJournalEvidenceTest.BOOT, cold(), f, () -> 1_000_000_000L);
    assertEquals("BOOT_JOURNAL", actual.source());
    assertEquals("7".repeat(32), actual.invocation());
    assertTrue(actual.nativeStart().isEmpty());
    assertTrue(actual.nativeEnd().isEmpty());
    assertEquals("1234568", actual.upper().toString());
    assertEquals(4, actual.journal().entries());
    assertEquals(
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256").digest(FULL.getBytes(StandardCharsets.UTF_8))),
        actual.journal().sha256());
    assertEquals(5, f.calls);
    actual.recheck();
    assertEquals(6, f.calls);
    assertEquals("PreviousBroker[actual=<redacted>]", actual.toString());
    f.erased();
    String rawHash = actual.journal().sha256();
    f.full =
        f.full
            .replace("\"PRIORITY\":\"6\",", "")
            .replace("{\"MESSAGE\"", "{\"PRIORITY\":\"6\",\"MESSAGE\"");
    actual.recheck();
    assertEquals(rawHash, actual.journal().sha256(), "original raw evidence is never rewritten");
    f.erased();
    f.full = f.full.replace("uptime 2 hours", "uptime 3 hours");
    assertThrows(IOException.class, actual::recheck);
    f.erased();
  }

  @Test
  void issstop002Native143UsesItsActualIntervalAndNeverHistoryFallback() throws Exception {
    var f = new Fixture();
    var actual =
        MorningPreviousBroker.collect(
            BrokerJournalEvidenceTest.BOOT, stopped(), f, () -> 1_000_000_000L);
    assertEquals("NATIVE_TERMINAL", actual.source());
    assertEquals("1234567", actual.nativeStart().orElseThrow().toString());
    assertEquals("1234568", actual.nativeEnd().orElseThrow().toString());
    assertEquals(1, f.calls);
    actual.recheck();
    assertEquals(2, f.calls);
    f.erased();
    f.full = BrokerJournalEvidenceTest.GOLDEN;
    assertThrows(
        IOException.class,
        () ->
            MorningPreviousBroker.collect(
                BrokerJournalEvidenceTest.BOOT, stopped(), f, () -> 1_000_000_000L));
    assertEquals(3, f.calls);
    f.erased();
  }

  @Test
  void issstop003LatestLiveForeignMalformedMissingAndAnchorDriftRefuse() {
    for (String fault :
        List.of(
            "live",
            "foreign",
            "priority",
            "error",
            "missing",
            "drift",
            "startMissing",
            "late",
            "duplicate",
            "anchorContent")) {
      var f = new Fixture();
      switch (fault) {
        case "live" -> {
          f.last = START;
          f.full = BrokerJournalEvidenceTest.GOLDEN;
        }
        case "foreign" -> f.start = START.replace("7".repeat(32), "6".repeat(32));
        case "priority" -> f.last = STOP.replace("\"PRIORITY\":\"6\"", "\"PRIORITY\":\"3\"");
        case "error" -> f.full = FULL.replace("Using NIO Journal", "ERROR NIO Journal");
        case "missing" -> f.last = "";
        case "drift" -> f.drift = true;
        case "startMissing" -> f.start = STOP;
        case "late" -> f.start = START.replace("1234567", "1234569");
        case "duplicate" -> f.full = FULL + STOP;
        case "anchorContent" -> f.full = FULL.replace("uptime 2 hours", "uptime 3 hours");
        default -> fail("closed fault enum");
      }
      assertThrows(
          IOException.class,
          () ->
              MorningPreviousBroker.collect(
                  BrokerJournalEvidenceTest.BOOT, cold(), f, () -> 1_000_000_000L),
          fault);
      f.erased();
    }
  }

  @Test
  void issstop004UnknownAndNullAreNotCleanStopOrProviderFallback() {
    for (Throwable failure :
        List.of(
            new NullPointerException("public fixture"),
            new IllegalStateException("public fixture"),
            new AssertionError("public fixture"))) {
      var f = new Fixture();
      f.failure = failure;
      assertSame(
          failure,
          assertThrows(
              Throwable.class,
              () ->
                  MorningPreviousBroker.collect(
                      BrokerJournalEvidenceTest.BOOT, cold(), f, () -> 1_000_000_000L)));
      assertEquals(1, f.calls);
    }
    var f = new Fixture();
    f.nullBytes = true;
    assertThrows(
        NullPointerException.class,
        () ->
            MorningPreviousBroker.collect(
                BrokerJournalEvidenceTest.BOOT, cold(), f, () -> 1_000_000_000L));
    assertThrows(
        IOException.class,
        () ->
            MorningPreviousBroker.collect(
                BrokerJournalEvidenceTest.BOOT,
                MorningBrokerUnitCycleTest.parse(MorningBrokerUnitCycleTest.LIVE),
                new Fixture(),
                () -> 1_000_000_000L));
  }
}
