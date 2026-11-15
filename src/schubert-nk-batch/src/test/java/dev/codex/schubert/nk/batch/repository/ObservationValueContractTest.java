package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-BAT-OBSVAL001..003; DAT009/OPS009/UI251/SS331/341/343/354; pure observations only. */
final class ObservationValueContractTest {
  @Test
  void observation001InspectionComponentsNullContractAndFixedRedaction() {
    BatchRun run = new BatchRun(new UUID(0, 1), Instant.EPOCH);
    CleanupCounts counts = new CleanupCounts(2, 1, 1);
    InspectionSummary value = new InspectionSummary(run, counts, true);
    InspectionSummary equal =
        new InspectionSummary(
            new BatchRun(new UUID(0, 1), Instant.EPOCH), new CleanupCounts(2, 1, 1), true);
    assertEquals(run, value.run());
    assertEquals(counts, value.counts());
    assertEquals(true, value.complete());
    assertFalse(new InspectionSummary(run, counts, false).complete());
    assertEquals("InspectionSummary[observation=<redacted>]", value.toString());
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    // Independent Java record hash polynomial: UUID(0,1)=1, EPOCH=0 => run=31;
    // counts(2,1,1)=1954; true=1231; (31*31+1954)*31+1231=91596.
    assertEquals(91596, value.hashCode());
    assertEquals("inspection", Map.of(value, "inspection").get(equal));
    assertNotEquals(value, null);
    assertNotEquals(value, "other");
    for (InspectionSummary other :
        List.of(
            new InspectionSummary(new BatchRun(new UUID(0, 2), Instant.EPOCH), counts, true),
            new InspectionSummary(run, new CleanupCounts(2, 2, 0), true),
            new InspectionSummary(run, counts, false))) {
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
    assertEquals(
        "fixed run",
        assertThrows(NullPointerException.class, () -> new InspectionSummary(null, counts, true))
            .getMessage());
    assertEquals(
        "inspection counts",
        assertThrows(NullPointerException.class, () -> new InspectionSummary(run, null, true))
            .getMessage());
  }

  @Test
  void observation002RunReferenceLiteralSixteenRowsAndAllRecordComponents() {
    String[] rows = {
      "0000", "0001", "0010", "0011", "0100", "0101", "0110", "0111", "1000", "1001", "1010",
      "1011", "1100", "1101", "1110", "1111"
    };
    boolean[] expectedAny = {
      false, false, true, true, true, true, true, true, true, true, true, true, true, true, true,
      true
    };
    for (int i = 0; i < rows.length; i++) {
      String row = rows[i];
      boolean batch = row.charAt(0) == '1';
      boolean inbox = row.charAt(1) == '1';
      boolean log = row.charAt(2) == '1';
      boolean identity = row.charAt(3) == '1';
      if (i == 0) {
        assertEquals(
            "inconsistent run reference projection",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new RunReferences(batch, inbox, log, identity))
                .getMessage());
      } else {
        RunReferences value = new RunReferences(batch, inbox, log, identity);
        assertEquals(batch, value.hasBatchHistory());
        assertEquals(inbox, value.hasInboxProgress());
        assertEquals(log, value.hasLogProgress());
        assertEquals(identity, value.identityConsistent());
        assertEquals(expectedAny[i], value.anyReference(), row);
        assertEquals("RunReferences[observation=<redacted>]", value.toString());
      }
    }
    RunReferences value = new RunReferences(true, true, true, true);
    RunReferences equal = new RunReferences(true, true, true, true);
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    // true=1231; polynomial over four ordered components, computed independently.
    assertEquals(37895104, value.hashCode());
    assertEquals("references", Map.of(value, "references").get(equal));
    assertNotEquals(value, null);
    assertNotEquals(value, "other");
    for (RunReferences other :
        List.of(
            new RunReferences(false, true, true, true),
            new RunReferences(true, false, true, true),
            new RunReferences(true, true, false, true),
            new RunReferences(true, true, true, false))) {
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
  }

  @Test
  void observation003CleanupCountsIndependentLongBoundaryTriplesAndValueContract() {
    long[][] valid = {
      {0, 0, 0},
      {1, 0, 1},
      {1, 1, 0},
      {2, 1, 1},
      {Long.MAX_VALUE, 0, Long.MAX_VALUE},
      {Long.MAX_VALUE, Long.MAX_VALUE, 0},
      {Long.MAX_VALUE, Long.MAX_VALUE - 1, 1}
    };
    for (long[] row : valid) {
      CleanupCounts value = new CleanupCounts(row[0], row[1], row[2]);
      assertEquals(row[0], value.target());
      assertEquals(row[1], value.deleted());
      assertEquals(row[2], value.skipped());
    }
    long[][] invalid = {
      {-1, 0, 0},
      {Long.MIN_VALUE, 0, 0},
      {0, -1, 0},
      {0, Long.MIN_VALUE, 0},
      {0, 1, 0},
      {1, 2, 0},
      {0, Long.MAX_VALUE, 0},
      {0, 0, -1},
      {0, 0, Long.MIN_VALUE},
      {0, 0, 1},
      {1, 0, 0},
      {1, 1, 1},
      {Long.MAX_VALUE, 0, Long.MAX_VALUE - 1}
    };
    for (long[] row : invalid) {
      assertEquals(
          "cleanup counts are inconsistent",
          assertThrows(
                  IllegalArgumentException.class, () -> new CleanupCounts(row[0], row[1], row[2]))
              .getMessage());
    }
    CleanupCounts value = new CleanupCounts(2, 1, 1);
    CleanupCounts equal = new CleanupCounts(2, 1, 1);
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertEquals(1954, value.hashCode());
    assertEquals("counts", Map.of(value, "counts").get(equal));
    assertEquals("CleanupCounts[target=2, deleted=1, skipped=1]", value.toString());
    assertNotEquals(value, null);
    assertNotEquals(value, "other");
    for (CleanupCounts other :
        List.of(
            new CleanupCounts(3, 1, 2), new CleanupCounts(2, 0, 2), new CleanupCounts(2, 2, 0))) {
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
  }
}
