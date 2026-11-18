package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.maintenance.InspectionExecution.Status;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-OPS-INS-VALUE-005..009; SS324/341/351; YKT-2673. */
final class InspectionProgressExecutionValueContractTest {
  private static final InspectionRun RUN = new InspectionRun(new UUID(16, 7), Instant.EPOCH);
  private static final Optional<UUID> CURSOR = Optional.of(new UUID(2, 9));
  private static final Optional<UUID> NO_CURSOR = Optional.empty();
  private static final InspectionProgress COMPLETE =
      new InspectionProgress(RUN, NO_CURSOR, 0, 0, 0, true);
  private static final InspectionProgress PROTECTED =
      new InspectionProgress(RUN, CURSOR, 1, 0, 1, true);
  private static final InspectionProgress PARTIAL =
      new InspectionProgress(RUN, CURSOR, 2, 1, 1, false);

  @Test
  void progressKeepsAllCountsAndRejectsInconsistentArithmeticAndCursor() {
    var max = new InspectionProgress(RUN, CURSOR, Long.MAX_VALUE, 3, Long.MAX_VALUE - 3, false);
    assertEquals(RUN, max.run());
    assertEquals(CURSOR, max.cursor());
    assertEquals(Long.MAX_VALUE, max.inspected());
    assertEquals(3, max.deleted());
    assertEquals(9_223_372_036_854_775_804L, max.protectedRows());
    assertFalse(max.complete());
    assertEquals(
        "InspectionProgress[inspected=9223372036854775807, deleted=3, "
            + "protected=9223372036854775804, complete=false]",
        max.toString());
    assertEquals(NO_CURSOR, COMPLETE.cursor());
    assertEquals(0, COMPLETE.inspected());

    for (long[] invalid :
        new long[][] {
          {-1, 0, 0},
          {1, -1, 2},
          {1, 2, 0},
          {1, 0, -1},
          {1, 0, 0},
          {Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE}
        }) {
      assertThrows(
          IllegalArgumentException.class,
          () -> new InspectionProgress(RUN, CURSOR, invalid[0], invalid[1], invalid[2], false));
    }
    assertThrows(
        IllegalArgumentException.class, () -> new InspectionProgress(RUN, CURSOR, 0, 0, 0, false));
    assertThrows(
        IllegalArgumentException.class,
        () -> new InspectionProgress(RUN, NO_CURSOR, 1, 0, 1, false));
    assertThrows(
        NullPointerException.class, () -> new InspectionProgress(null, NO_CURSOR, 0, 0, 0, false));
    assertThrows(
        NullPointerException.class, () -> new InspectionProgress(RUN, null, 0, 0, 0, false));
  }

  @Test
  void progressSeparatesRunCursorCountsAndCompletionInValueKeys() {
    var recorded = new HashMap<InspectionProgress, String>();
    var entry = "confirmed observation";
    recorded.put(PARTIAL, entry);
    var equalRun = new InspectionRun(new UUID(16, 7), Instant.parse("1970-01-01T00:00:00Z"));
    var equal = new InspectionProgress(equalRun, Optional.of(new UUID(2, 9)), 2, 1, 1, false);
    assertEquals(PARTIAL, equal);
    assertEquals(entry, recorded.get(equal));
    assertFalse(recorded.containsKey(new InspectionProgress(RUN, CURSOR, 2, 1, 1, true)));
    assertFalse(recorded.containsKey(new InspectionProgress(RUN, CURSOR, 2, 0, 2, false)));
    assertFalse(
        recorded.containsKey(
            new InspectionProgress(RUN, Optional.of(new UUID(2, 8)), 2, 1, 1, false)));
    var other = new InspectionRun(new UUID(16, 8), Instant.EPOCH);
    assertFalse(recorded.containsKey(new InspectionProgress(other, CURSOR, 2, 1, 1, false)));
  }

  @Test
  void executionMapsTheFiveOutcomesAndKeepsOnlyTheSuppliedObservation() {
    var success = new InspectionExecution(Status.SUCCESS, Optional.of(COMPLETE));
    assertEquals(0, success.exitCode());
    assertEquals(Status.SUCCESS, success.status());
    assertEquals(Optional.of(COMPLETE), success.lastConfirmed());

    var warning = new InspectionExecution(Status.WARNING, Optional.of(PROTECTED));
    assertEquals(10, warning.exitCode());
    assertEquals(
        "InspectionExecution[status=WARNING, lastConfirmed="
            + "InspectionProgress[inspected=1, deleted=0, protected=1, complete=true]]",
        warning.toString());

    for (Status status : List.of(Status.TIME_LIMIT, Status.INTERRUPTED, Status.STORAGE_FAILURE)) {
      var withoutObservation = new InspectionExecution(status, Optional.empty());
      assertEquals(50, withoutObservation.exitCode());
      assertEquals(Optional.empty(), withoutObservation.lastConfirmed());
      var observed = new InspectionExecution(status, Optional.of(PARTIAL));
      assertEquals(50, observed.exitCode());
      assertEquals(Optional.of(PARTIAL), observed.lastConfirmed());
    }
    assertEquals(
        "InspectionExecution[status=TIME_LIMIT, lastConfirmed=unavailable]",
        new InspectionExecution(Status.TIME_LIMIT, Optional.empty()).toString());
  }

  @Test
  void completedExecutionRequiresMatchingCompletedProgress() {
    for (Status status : List.of(Status.SUCCESS, Status.WARNING)) {
      assertThrows(
          IllegalArgumentException.class, () -> new InspectionExecution(status, Optional.empty()));
      assertThrows(
          IllegalArgumentException.class,
          () -> new InspectionExecution(status, Optional.of(PARTIAL)));
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> new InspectionExecution(Status.SUCCESS, Optional.of(PROTECTED)));
    assertThrows(
        IllegalArgumentException.class,
        () -> new InspectionExecution(Status.WARNING, Optional.of(COMPLETE)));
    assertThrows(NullPointerException.class, () -> new InspectionExecution(null, Optional.empty()));
    assertThrows(
        NullPointerException.class, () -> new InspectionExecution(Status.TIME_LIMIT, null));
  }

  @Test
  void executionUsesBothValueComponentsAndTheFixedOutcomeVocabulary() {
    var first = new InspectionExecution(Status.TIME_LIMIT, Optional.of(PARTIAL));
    var sameProgress = new InspectionProgress(RUN, CURSOR, 2, 1, 1, false);
    var equal = new InspectionExecution(Status.TIME_LIMIT, Optional.of(sameProgress));
    var observations = new HashMap<InspectionExecution, String>();
    var label = "timed out observation";
    observations.put(first, label);

    assertEquals(first, equal);
    assertEquals(label, observations.get(equal));
    assertFalse(
        observations.containsKey(new InspectionExecution(Status.TIME_LIMIT, Optional.empty())));
    assertFalse(
        observations.containsKey(
            new InspectionExecution(Status.INTERRUPTED, Optional.of(PARTIAL))));

    Status[] expected = {
      Status.SUCCESS, Status.WARNING, Status.TIME_LIMIT, Status.INTERRUPTED, Status.STORAGE_FAILURE
    };
    assertArrayEquals(expected, Status.values());
    assertEquals(Status.SUCCESS, Status.valueOf("SUCCESS"));
    assertEquals(Status.WARNING, Status.valueOf("WARNING"));
    assertEquals(Status.TIME_LIMIT, Status.valueOf("TIME_LIMIT"));
    assertEquals(Status.INTERRUPTED, Status.valueOf("INTERRUPTED"));
    assertEquals(Status.STORAGE_FAILURE, Status.valueOf("STORAGE_FAILURE"));
    assertThrows(IllegalArgumentException.class, () -> Status.valueOf("UNKNOWN"));
    assertThrows(NullPointerException.class, () -> Status.valueOf(null));
  }
}
