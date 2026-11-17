package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-SUM-RAW001..003 / SS332/341 / PG-D-1173. Independent literal value/hash vectors only. */
class InspectionSummaryValueContractTest {
  private static final Instant CUTOFF = Instant.parse("2026-11-05T00:00:00.123456Z");
  private static final UUID ID = new UUID(0, 1);

  @Test
  void raw001SummaryIdentityIncludesEachComponentAndDiagnosticStaysRedacted() {
    var value = new InspectionSummary(new BatchRun(ID, CUTOFF), new CleanupCounts(3, 2, 1), false);
    var equal =
        new InspectionSummary(
            new BatchRun(new UUID(0, 1), CUTOFF), new CleanupCounts(3, 2, 1), false);
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertEquals(688497394, value.hashCode());
    assertEquals(688497394, equal.hashCode());
    assertEquals("InspectionSummary[observation=<redacted>]", value.toString());
    assertEquals(ID, value.run().id());
    assertEquals(CUTOFF, value.run().cutoff());
    assertEquals(new CleanupCounts(3, 2, 1), value.counts());
    assertFalse(value.complete());
    assertFalse(value.equals(null));
    assertFalse(value.equals("other-type"));
    for (InspectionSummary other :
        List.of(
            new InspectionSummary(
                new BatchRun(new UUID(0, 2), CUTOFF), new CleanupCounts(3, 2, 1), false),
            new InspectionSummary(new BatchRun(ID, CUTOFF), new CleanupCounts(4, 3, 1), false),
            new InspectionSummary(new BatchRun(ID, CUTOFF), new CleanupCounts(3, 2, 1), true))) {
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
  }

  @Test
  void raw002RunIdentityIncludesBothFieldsWithIndependentJdkHashVector() {
    var value = new BatchRun(ID, CUTOFF);
    assertEquals(value, value);
    assertEquals(value, new BatchRun(new UUID(0, 1), CUTOFF));
    assertEquals(-499841761, value.hashCode());
    assertEquals("BatchRun[identity/cutoff=<redacted>]", value.toString());
    assertEquals(ID, value.id());
    assertEquals(CUTOFF, value.cutoff());
    assertFalse(value.equals(null));
    assertFalse(value.equals("other-type"));
    assertNotEquals(value, new BatchRun(new UUID(0, 2), CUTOFF));
    assertNotEquals(value, new BatchRun(ID, CUTOFF.plusNanos(1000)));
  }

  @Test
  void raw003CountsRetainAllFieldsAndLiteralDiagnosticWithoutMutableState() {
    var value = new CleanupCounts(3, 2, 1);
    assertEquals(value, value);
    assertEquals(value, new CleanupCounts(3, 2, 1));
    assertEquals(2946, value.hashCode());
    assertEquals("CleanupCounts[target=3, deleted=2, skipped=1]", value.toString());
    assertEquals(3, value.target());
    assertEquals(2, value.deleted());
    assertEquals(1, value.skipped());
    assertFalse(value.equals(null));
    assertFalse(value.equals("other-type"));
    assertNotEquals(value, new CleanupCounts(4, 3, 1));
    assertNotEquals(value, new CleanupCounts(3, 1, 2));
    assertNotEquals(value, new CleanupCounts(4, 2, 2));
  }
}
