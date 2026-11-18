package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import java.math.BigInteger;
import org.junit.jupiter.api.Test;

/** PT-P01810-CATALOG-065A/B. Public fixture values only, with no journal acquisition. */
final class BrokerJournalValueContractTest {
  @Test
  void summaryPreservesIndependentValuesWithoutRenderingThem() {
    String digest = "a".repeat(64);
    var original = new BrokerJournalEvidence.Summary(33, digest);
    var equal = new BrokerJournalEvidence.Summary(33, digest);
    assertEquals(33, original.entries());
    assertEquals(digest, original.sha256());
    assertEquals(equal, original);
    assertEquals(equal.hashCode(), original.hashCode());
    assertNotEquals(original, new BrokerJournalEvidence.Summary(34, digest));
    assertNotEquals(original, new BrokerJournalEvidence.Summary(33, "b".repeat(64)));
    assertEquals("BrokerJournalSummary[redacted]", original.toString());
    assertEquals(
        "BrokerJournalSummary[redacted]",
        new BrokerJournalEvidence.Summary(34, "b".repeat(64)).toString());
  }

  @Test
  void anchorPreservesAllWitnessValuesWithoutRenderingThem() {
    String invocation = "fixture-invocation";
    BigInteger timestamp = BigInteger.valueOf(141L);
    String cursor = "fixture-cursor";
    String digest = "c".repeat(64);
    var original = new BrokerJournalEvidence.Anchor(invocation, timestamp, cursor, digest);
    var equal = new BrokerJournalEvidence.Anchor(invocation, timestamp, cursor, digest);
    assertEquals(invocation, original.invocation());
    assertEquals(timestamp, original.monotonic());
    assertEquals(cursor, original.cursor());
    assertEquals(digest, original.contentSha256());
    assertEquals(equal, original);
    assertEquals(equal.hashCode(), original.hashCode());
    assertNotEquals(original, new BrokerJournalEvidence.Anchor("other", timestamp, cursor, digest));
    assertNotEquals(
        original, new BrokerJournalEvidence.Anchor(invocation, BigInteger.TWO, cursor, digest));
    assertNotEquals(
        original, new BrokerJournalEvidence.Anchor(invocation, timestamp, "other", digest));
    var changed = new BrokerJournalEvidence.Anchor(invocation, timestamp, cursor, "d".repeat(64));
    assertNotEquals(original, changed);
    assertEquals("BrokerJournalAnchor[redacted]", original.toString());
    assertEquals("BrokerJournalAnchor[redacted]", changed.toString());
  }
}
