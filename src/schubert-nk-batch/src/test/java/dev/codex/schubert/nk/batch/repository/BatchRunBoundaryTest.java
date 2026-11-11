package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** NK-BAT-001; OPS-009; UI251; SS341 sections3/7; PT-BAT-RUN-BND001/002. */
final class BatchRunBoundaryTest {
  private static final UUID ID = new UUID(0, 1);

  @Test
  void literalTimestampExtremesAndRedactedDisplayAreAccepted() {
    // Independent PostgreSQL timestamp contract constants; no expected from the SUT.
    for (String literal : new String[] {"0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z"}) {
      Instant expected = Instant.parse(literal);
      BatchRun actual = new BatchRun(ID, expected);
      assertEquals(ID, actual.id());
      assertEquals(expected, actual.cutoff());
      assertEquals("BatchRun[identity/cutoff=<redacted>]", actual.toString());
    }
  }

  @Test
  void nullOutsideRangeAndSubMicrosecondInputsAreRejected() {
    Instant ordinary = Instant.parse("2026-11-05T00:00:00.123456Z");
    assertThrows(NullPointerException.class, () -> new BatchRun(null, ordinary));
    assertThrows(NullPointerException.class, () -> new BatchRun(ID, null));
    // Three independent invalid causes: below min, above max, non-microsecond precision.
    for (String literal :
        new String[] {
          "0000-12-31T23:59:59.999999Z", "+10000-01-01T00:00:00Z", "2026-11-05T00:00:00.123456001Z"
        }) {
      Instant input = Instant.parse(literal);
      assertThrows(IllegalArgumentException.class, () -> new BatchRun(ID, input));
    }
  }
}
