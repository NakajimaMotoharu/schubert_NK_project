package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import org.junit.jupiter.api.Test;

/** SSC125 BROKERSTART003: hand-written vendor2.56 message oracle + independent JSON/metadata. */
final class BrokerJournalEvidenceTest {
  @Test
  void issbrokerstop001ActualStopEventNeedsSameBootInvocationWholeIntervalAndExactBytes()
      throws Exception {
    String stopped =
        row(
            "AMQ221002: Apache Artemis Message Broker version 2.56.0 [public-fixture] stopped,"
                + " uptime 2 hours",
            4);
    byte[] bytes = stopped.getBytes(StandardCharsets.UTF_8);
    var actual =
        BrokerJournalEvidence.consumeStopped(
            bytes, BOOT, INV, BigInteger.valueOf(1234567), BigInteger.valueOf(1234568));
    assertEquals(1, actual.entries());
    assertEquals(
        HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes)),
        actual.sha256());
    for (String invalid :
        List.of(
            GOLDEN,
            stopped.replace("AMQ221002", "AMQ221001"),
            stopped.replace("stopped, uptime", "started, uptime"),
            stopped.replace("2.56.0", "2.55.0"),
            stopped.replace("1234567", "1234569"),
            stopped.replace(INV, "6".repeat(32)),
            stopped.replace("\"PRIORITY\":\"6\"", "\"PRIORITY\":\"3\""),
            stopped + stopped))
      assertThrows(
          IOException.class,
          () ->
              BrokerJournalEvidence.consumeStopped(
                  invalid.getBytes(StandardCharsets.UTF_8),
                  BOOT,
                  INV,
                  BigInteger.valueOf(1234567),
                  BigInteger.valueOf(1234568)));
    assertThrows(
        IOException.class,
        () ->
            BrokerJournalEvidence.consumeStopped(
                bytes, BOOT, INV, BigInteger.valueOf(1234567), BigInteger.valueOf(1234566)));
  }

  static final UUID BOOT = UUID.fromString("11111111-1111-4111-8111-111111111111");
  static final String INV = "7".repeat(32);

  static String row(String message, int cursor) {
    return "{\"MESSAGE\":\""
        + message
        + "\",\"PRIORITY\":\"6\",\"_SYSTEMD_INVOCATION_ID\":\""
        + INV
        + "\",\"_BOOT_ID\":\"11111111111141118111111111111111\",\"_SYSTEMD_UNIT\":\"artemis.service\","
        + "\"__CURSOR\":\"cursor-"
        + cursor
        + "\",\"__MONOTONIC_TIMESTAMP\":\"1234567\",\"__REALTIME_TIMESTAMP\":\"1790780400000000\"}\n";
  }

  static final String GOLDEN =
      row("AMQ221013: Using NIO Journal", 1)
          + row("AMQ221007: Server is now active", 2)
          + row(
              "AMQ221001: Apache Artemis Message Broker version 2.56.0 [schubert-nk-broker,"
                  + " nodeID=public-fixture]",
              3);

  static BrokerJournalEvidence.Summary read(String text) throws IOException {
    return BrokerJournalEvidence.consume(
        text.getBytes(StandardCharsets.UTF_8), BOOT, INV, BigInteger.valueOf(1234567));
  }

  @Test
  void allThreePrimaryVendorEventsBoundToActualGenerationAndExactBytes() throws Exception {
    var actual = read(GOLDEN);
    assertEquals(3, actual.entries());
    // Independent standard SHA-256 calculation over the hand-written fixture, no production method.
    assertEquals(
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(GOLDEN.getBytes(StandardCharsets.UTF_8))),
        actual.sha256());
    assertEquals("BrokerJournalSummary[redacted]", actual.toString());
    assertEquals(
        3,
        read(GOLDEN.replace(
                "\"__CURSOR\"", "\"__SEQNUM\":\"1\",\"__SEQNUM_ID\":\"public\",\"__CURSOR\""))
            .entries());
  }

  @Test
  void emptyOldMalformedDuplicatedOrErrorCannotProveRecovery() {
    for (var change :
        List.of(
            Map.entry(INV, "6".repeat(32)),
            Map.entry("11111111111141118111111111111111", "22222222222242228222222222222222"),
            Map.entry("artemis.service", "other.service"),
            Map.entry("\"PRIORITY\":\"6\"", "\"PRIORITY\":\"3\""),
            Map.entry("cursor-3", "cursor-2"),
            Map.entry("1234567", "1234566"),
            Map.entry("AMQ221013", "AMQ221014"),
            Map.entry("AMQ221007", "AMQ221008"),
            Map.entry("2.56.0", "2.55.0"),
            Map.entry("schubert-nk-broker", "different-broker"),
            Map.entry("Using NIO Journal", "ERROR journal load"),
            Map.entry("Server is now active", "AMQ224001: broken journal"),
            Map.entry("\"PRIORITY\":\"6\"", "\"PRIORITY\":\"6\",\"PRIORITY\":\"6\""),
            Map.entry("\"PRIORITY\":\"6\"", "\"PRIORITY\":6"),
            Map.entry("\"PRIORITY\":\"6\"", "\"unknown\":\"value\",\"PRIORITY\":\"6\"")))
      assertThrows(
          IOException.class,
          () -> read(GOLDEN.replace(change.getKey(), change.getValue())),
          change.toString());
    for (String bad : List.of("", GOLDEN.stripTrailing(), "{}\n", GOLDEN + "\n", "not json\n"))
      assertThrows(IOException.class, () -> read(bad));
    assertThrows(
        IOException.class,
        () ->
            BrokerJournalEvidence.consume(new byte[] {(byte) 0xff, 10}, BOOT, INV, BigInteger.ONE));
    assertThrows(
        IOException.class,
        () ->
            BrokerJournalEvidence.consume(
                new byte[4 * 1024 * 1024 + 1], BOOT, INV, BigInteger.ONE));
    assertThrows(
        NullPointerException.class,
        () -> BrokerJournalEvidence.consume(null, BOOT, INV, BigInteger.ONE));
  }
}
