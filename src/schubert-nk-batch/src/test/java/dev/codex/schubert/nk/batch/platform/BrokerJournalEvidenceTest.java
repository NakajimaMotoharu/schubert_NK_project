package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.Security;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SSC125 BROKERSTART003: hand-written vendor2.56 message oracle + independent JSON/metadata. */
@org.junit.jupiter.api.parallel.Isolated("PG2478 provider outage is confined to the test JVM")
final class BrokerJournalEvidenceTest {
  @Test
  void bj2478001AnchorMetadataAndExactByteBoundariesRejectForeignOrMissingEvidence()
      throws Exception {
    String start =
        row("AMQ221001: Apache Artemis Message Broker version 2.56.0 schubert-nk-broker", 3);
    byte[] literal = start.getBytes(StandardCharsets.UTF_8);
    var anchor = BrokerJournalEvidence.anchor(literal, BOOT, true);
    assertEquals(INV, anchor.invocation());
    assertEquals(BigInteger.valueOf(1234567), anchor.monotonic());
    assertEquals("cursor-3", anchor.cursor());
    assertEquals("BrokerJournalAnchor[redacted]", anchor.toString());
    for (String invalid :
        List.of(
            start.replace(INV, "0".repeat(32)),
            start.replace(INV, "Q".repeat(32)),
            start.replace("1234567", "0"),
            start.replace("1790780400000000", "0"),
            start.replace("cursor-3", ""),
            start.replace("\"PRIORITY\":\"6\"", "\"PRIORITY\":\"3\""),
            start.replace("schubert-nk-broker", "foreign"),
            start.replace("2.56.0", "2.55.0"),
            start.replace("AMQ221001", "AMQ224001"),
            start.replace("schubert-nk-broker", "FATAL"),
            start.stripTrailing(),
            start + start)) {
      assertThrows(
          IOException.class,
          () -> BrokerJournalEvidence.anchor(invalid.getBytes(StandardCharsets.UTF_8), BOOT, true));
    }
    String padded =
        start.replace(
            "schubert-nk-broker", "schubert-nk-broker" + " ".repeat(65536 - literal.length));
    assertEquals(65536, padded.getBytes(StandardCharsets.UTF_8).length);
    assertEquals(
        "cursor-3",
        BrokerJournalEvidence.anchor(padded.getBytes(StandardCharsets.UTF_8), BOOT, true).cursor());
    for (byte[] invalid : List.of(new byte[0], new byte[65537], new byte[] {(byte) 0xff, 10}))
      assertThrows(IOException.class, () -> BrokerJournalEvidence.anchor(invalid, BOOT, false));
    assertThrows(NullPointerException.class, () -> BrokerJournalEvidence.anchor(null, BOOT, false));
    assertThrows(
        NullPointerException.class, () -> BrokerJournalEvidence.anchor(literal, null, false));
  }

  @Test
  void bj2478002CanonicalAndStrictJsonBoundariesDoNotNormalizeUnavailableEvidence()
      throws Exception {
    for (byte[] invalid :
        List.of(
            new byte[0],
            new byte[4 * 1024 * 1024 + 1],
            GOLDEN.stripTrailing().getBytes(StandardCharsets.UTF_8),
            new byte[] {(byte) 0xff, 10},
            "[]\n".getBytes(StandardCharsets.UTF_8),
            row("literal\\ud800", 1).getBytes(StandardCharsets.UTF_8))) {
      IOException failure =
          assertThrows(IOException.class, () -> BrokerJournalEvidence.contentSha256(invalid));
      assertFalse(String.valueOf(failure.getMessage()).contains("literal"));
    }
    for (String text : List.of("[]\n", "{\"MESSAGE\":null}\n", "{} {}\n"))
      assertThrows(IOException.class, () -> read(text));
    for (String text :
        List.of(
            GOLDEN.replace("cursor-1", ""),
            GOLDEN.replace(
                "\"__MONOTONIC_TIMESTAMP\":\"1234567\"", "\"__MONOTONIC_TIMESTAMP\":\"0\"")))
      assertThrows(IOException.class, () -> read(text));
    assertThrows(NullPointerException.class, () -> BrokerJournalEvidence.contentSha256(null));
  }

  @Test
  void bj2478003ClosedHistoryRequiresIndependentCursorTimeAndCanonicalDigest() throws Exception {
    String last =
        row(
            "AMQ221002: Apache Artemis Message Broker version 2.56.0 [public-fixture] stopped,"
                + " uptime 2 hours",
            4);
    String history = GOLDEN + last;
    var fields = new TreeMap<String, String>();
    fields.put(
        "MESSAGE",
        "AMQ221002: Apache Artemis Message Broker version 2.56.0 [public-fixture] stopped,"
            + " uptime 2 hours");
    fields.put("PRIORITY", "6");
    fields.put("_SYSTEMD_INVOCATION_ID", INV);
    fields.put("_BOOT_ID", "11111111111141118111111111111111");
    fields.put("_SYSTEMD_UNIT", "artemis.service");
    fields.put("__CURSOR", "cursor-4");
    fields.put("__MONOTONIC_TIMESTAMP", "1234567");
    fields.put("__REALTIME_TIMESTAMP", "1790780400000000");
    var canonical = new StringBuilder("NKJOURNAL1\n");
    fields.forEach(
        (k, v) ->
            canonical
                .append("ROW|0|")
                .append(k)
                .append('|')
                .append(HexFormat.of().formatHex(v.getBytes(StandardCharsets.UTF_8)))
                .append('\n'));
    String digest =
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(canonical.toString().getBytes(StandardCharsets.US_ASCII)));
    var expectedAnchor =
        new BrokerJournalEvidence.Anchor(INV, BigInteger.valueOf(1234567), "cursor-4", digest);
    var actual =
        BrokerJournalEvidence.consumeClosedHistory(
            history.getBytes(StandardCharsets.UTF_8), BOOT, expectedAnchor);
    assertEquals(4, actual.entries());
    assertEquals(
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(history.getBytes(StandardCharsets.UTF_8))),
        actual.sha256());
    assertEquals(
        digest, BrokerJournalEvidence.contentSha256(last.getBytes(StandardCharsets.UTF_8)));
    for (var invalid :
        List.of(
            new BrokerJournalEvidence.Anchor(INV, BigInteger.valueOf(1234567), "foreign", digest),
            new BrokerJournalEvidence.Anchor(INV, BigInteger.valueOf(1234568), "cursor-4", digest),
            new BrokerJournalEvidence.Anchor(
                INV, BigInteger.valueOf(1234567), "cursor-4", "0".repeat(64))))
      assertThrows(
          IOException.class,
          () ->
              BrokerJournalEvidence.consumeClosedHistory(
                  history.getBytes(StandardCharsets.UTF_8), BOOT, invalid));
    assertThrows(
        NullPointerException.class,
        () ->
            BrokerJournalEvidence.consumeClosedHistory(
                history.getBytes(StandardCharsets.UTF_8), BOOT, null));
  }

  @Test
  void bj2478004CryptoProviderOutageIsRedactedAndRegistryRestored() throws Exception {
    var original = Security.getProviders();
    try {
      for (var provider : original) Security.removeProvider(provider.getName());
      for (boolean canonical : List.of(false, true)) {
        IOException failure =
            assertThrows(
                IOException.class,
                () -> {
                  if (canonical)
                    BrokerJournalEvidence.contentSha256(GOLDEN.getBytes(StandardCharsets.UTF_8));
                  else read(GOLDEN);
                });
        assertEquals("Broker journal evidence unavailable", failure.getMessage());
      }
    } finally {
      for (int i = 0; i < original.length; i++) Security.insertProviderAt(original[i], i + 1);
    }
    assertArrayEquals(original, Security.getProviders());
    assertEquals(
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest("abc".getBytes(StandardCharsets.US_ASCII))));
    assertEquals(3, read(GOLDEN).entries());
  }

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
