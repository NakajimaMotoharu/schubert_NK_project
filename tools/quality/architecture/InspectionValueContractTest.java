package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SS324 12.6/12.7 immutable values only; no inspection executor, SQL or process gate. */
final class InspectionValueContractTest {
  private static final UUID ID = new UUID(0, 77);
  private static final Instant AT = Instant.parse("2026-11-01T00:00:00.123456Z");
  private static final InspectionRun RUN = new InspectionRun(ID, AT);

  @Test
  void inspectionValue001RunRetainsExactMicrosecondBoundsAndRedactsIdentity() {
    for (Instant cutoff : List.of(Instant.parse("0001-01-01T00:00:00Z"), AT,
        Instant.parse("9999-12-31T23:59:59.999999Z"))) {
      var run = new InspectionRun(ID, cutoff);
      assertSame(ID, run.id());
      assertSame(cutoff, run.cutoff());
      assertEquals("InspectionRun[identity/cutoff=<redacted>]", run.toString());
    }
  }

  @Test
  void inspectionValue002RunRejectsNullAndEveryTimestampViolation() {
    assertThrows(NullPointerException.class, () -> new InspectionRun(null, AT));
    assertThrows(NullPointerException.class, () -> new InspectionRun(ID, null));
    for (String text : List.of("0000-12-31T23:59:59.999999Z",
        "+10000-01-01T00:00:00Z", "2026-11-01T00:00:00.000000001Z")) {
      var failure = assertThrows(IllegalArgumentException.class,
          () -> new InspectionRun(ID, Instant.parse(text)));
      assertEquals("inspection cutoff is outside the timestamp contract", failure.getMessage());
    }
  }

  @Test
  void inspectionValue003StepHasExactEndCursorEquivalenceAndRedaction() {
    var cursor = Optional.of(ID);
    for (InspectionStep.Outcome outcome :
        List.of(InspectionStep.Outcome.DELETED, InspectionStep.Outcome.PROTECTED)) {
      var step = new InspectionStep(outcome, cursor);
      assertSame(outcome, step.outcome());
      assertSame(cursor, step.cursor());
      assertEquals("InspectionStep[outcome=" + outcome + ", cursor=<redacted>]", step.toString());
    }
    var end = new InspectionStep(InspectionStep.Outcome.END, Optional.empty());
    assertEquals(InspectionStep.Outcome.END, end.outcome());
    assertEquals(Optional.empty(), end.cursor());
    assertEquals("InspectionStep[outcome=END, cursor=<redacted>]", end.toString());
  }

  @Test
  void inspectionValue004StepRejectsNullAndBothInconsistentCursorDirections() {
    assertThrows(NullPointerException.class, () -> new InspectionStep(null, Optional.empty()));
    assertThrows(NullPointerException.class, () -> new InspectionStep(InspectionStep.Outcome.END, null));
    for (InspectionStep.Outcome outcome :
        List.of(InspectionStep.Outcome.DELETED, InspectionStep.Outcome.PROTECTED)) {
      assertEquals("inspection outcome and cursor disagree",
          assertThrows(IllegalArgumentException.class,
              () -> new InspectionStep(outcome, Optional.empty())).getMessage());
    }
    assertEquals("inspection outcome and cursor disagree",
        assertThrows(IllegalArgumentException.class,
            () -> new InspectionStep(InspectionStep.Outcome.END, Optional.of(ID))).getMessage());
  }

  @Test
  void inspectionValue005ProgressRetainsExactCountsAtZeroAndLongMaxWithoutOverflow() {
    long[][] rows = {{0, 0, 0}, {1, 1, 0}, {1, 0, 1},
        {Long.MAX_VALUE, 0, Long.MAX_VALUE}, {Long.MAX_VALUE, Long.MAX_VALUE, 0}};
    for (long[] row : rows) {
      for (boolean complete : new boolean[] {false, true}) {
        Optional<UUID> cursor = row[0] == 0 ? Optional.empty() : Optional.of(ID);
        var value = new InspectionProgress(RUN, cursor, row[0], row[1], row[2], complete);
        assertSame(RUN, value.run());
        assertSame(cursor, value.cursor());
        assertEquals(row[0], value.inspected());
        assertEquals(row[1], value.deleted());
        assertEquals(row[2], value.protectedRows());
        assertEquals(complete, value.complete());
        assertEquals("InspectionProgress[inspected=" + row[0] + ", deleted=" + row[1]
            + ", protected=" + row[2] + ", complete=" + complete + "]", value.toString());
      }
    }
  }

  @Test
  void inspectionValue006ProgressRejectsEachIndependentCountAndCursorViolation() {
    assertThrows(NullPointerException.class,
        () -> new InspectionProgress(null, Optional.empty(), 0, 0, 0, false));
    assertThrows(NullPointerException.class,
        () -> new InspectionProgress(RUN, null, 0, 0, 0, false));
    long[][] bad = {{-1, 0, 0}, {1, -1, 2}, {1, 2, 0}, {1, 0, -1}, {2, 1, 0}};
    for (long[] row : bad) {
      assertEquals("inspection progress is inconsistent",
          assertThrows(IllegalArgumentException.class,
              () -> new InspectionProgress(RUN, Optional.of(ID),
                  row[0], row[1], row[2], false)).getMessage());
    }
    assertThrows(IllegalArgumentException.class,
        () -> new InspectionProgress(RUN, Optional.of(ID), 0, 0, 0, false));
    assertThrows(IllegalArgumentException.class,
        () -> new InspectionProgress(RUN, Optional.empty(), 1, 1, 0, false));
  }

  @Test
  void inspectionValue007ExecutionUsesOnlyLiteralExitEquivalentAndLastConfirmedValues() {
    var clean = new InspectionProgress(RUN, Optional.empty(), 0, 0, 0, true);
    var protectedOne = new InspectionProgress(RUN, Optional.of(ID), 1, 0, 1, true);
    var success = new InspectionExecution(InspectionExecution.Status.SUCCESS, Optional.of(clean));
    assertEquals(0, success.exitCode());
    assertEquals(InspectionExecution.Status.SUCCESS, success.status());
    assertSame(clean, success.lastConfirmed().orElseThrow());
    assertEquals("InspectionExecution[status=SUCCESS, lastConfirmed=InspectionProgress[inspected=0, deleted=0, protected=0, complete=true]]",
        success.toString());
    var warning = new InspectionExecution(InspectionExecution.Status.WARNING, Optional.of(protectedOne));
    assertEquals(10, warning.exitCode());
    assertEquals(InspectionExecution.Status.WARNING, warning.status());
    assertSame(protectedOne, warning.lastConfirmed().orElseThrow());
    for (InspectionExecution.Status status : List.of(InspectionExecution.Status.TIME_LIMIT,
        InspectionExecution.Status.INTERRUPTED, InspectionExecution.Status.STORAGE_FAILURE)) {
      var unknown = new InspectionExecution(status, Optional.empty());
      assertEquals(50, unknown.exitCode());
      assertSame(status, unknown.status());
      assertEquals(Optional.empty(), unknown.lastConfirmed());
      assertEquals("InspectionExecution[status=" + status + ", lastConfirmed=unavailable]",
          unknown.toString());
      var partial = new InspectionProgress(RUN, Optional.of(ID), 1, 0, 1, false);
      var failed = new InspectionExecution(status, Optional.of(partial));
      assertEquals(50, failed.exitCode());
      assertSame(partial, failed.lastConfirmed().orElseThrow());
    }
  }

  @Test
  void inspectionValue008ExecutionRejectsNullMissingOrInconsistentCompletion() {
    assertThrows(NullPointerException.class, () -> new InspectionExecution(null, Optional.empty()));
    assertThrows(NullPointerException.class,
        () -> new InspectionExecution(InspectionExecution.Status.SUCCESS, null));
    for (InspectionExecution.Status status :
        List.of(InspectionExecution.Status.SUCCESS, InspectionExecution.Status.WARNING)) {
      assertEquals("completed execution requires confirmed progress",
          assertThrows(IllegalArgumentException.class,
              () -> new InspectionExecution(status, Optional.empty())).getMessage());
      var unfinished = new InspectionProgress(RUN, Optional.empty(), 0, 0, 0, false);
      assertEquals("execution status does not match confirmed progress",
          assertThrows(IllegalArgumentException.class,
              () -> new InspectionExecution(status, Optional.of(unfinished))).getMessage());
    }
    var clean = new InspectionProgress(RUN, Optional.empty(), 0, 0, 0, true);
    var protectedOne = new InspectionProgress(RUN, Optional.of(ID), 1, 0, 1, true);
    assertThrows(IllegalArgumentException.class,
        () -> new InspectionExecution(InspectionExecution.Status.WARNING, Optional.of(clean)));
    assertThrows(IllegalArgumentException.class,
        () -> new InspectionExecution(InspectionExecution.Status.SUCCESS, Optional.of(protectedOne)));
  }
}
