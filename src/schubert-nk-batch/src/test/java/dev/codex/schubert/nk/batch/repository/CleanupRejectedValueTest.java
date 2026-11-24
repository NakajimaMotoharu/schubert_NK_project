package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.CleanupTerminalRepository.RejectedEntry;
import dev.codex.schubert.nk.batch.repository.CleanupTerminalRepository.RejectedSnapshot;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-BAT-REJVAL001..004. Closed values only; the repository does not execute. */
final class CleanupRejectedValueTest {
  private static final Instant CUTOFF = Instant.parse("2026-11-01T00:00:00Z");
  private static final Instant START = Instant.parse("2026-11-01T00:00:01Z");
  private static final Instant END = Instant.parse("2026-11-01T00:00:05Z");
  private static final BatchRun RUN = new BatchRun(new UUID(0, 30), CUTOFF);
  private static final BatchRun OTHER_RUN = new BatchRun(new UUID(0, 31), CUTOFF);
  private static final BatchStepResult SUCCESS =
      new BatchStepResult(
          BatchStepResult.Status.SUCCESS, 11, 11, 0, 135, BatchStepResult.Reason.NONE);
  private static final BatchStepResult SKIPPED =
      new BatchStepResult(
          BatchStepResult.Status.SKIPPED, 0, 0, 0, 0, BatchStepResult.Reason.BACKUP_UNAVAILABLE);
  private static final String INVALID_ROW = "Cleanup rejection row invalid";
  private static final String INVALID_IDENTITY = "Cleanup rejection identity invalid";

  @Test
  void keepsSuccessfulRunningSkippedAndAbsentSlotsDistinct() {
    var success = terminal(attempt(21, RUN, BatchStep.CLEAN_NOTIFICATION, false), END, SUCCESS);
    var running =
        new RejectedEntry(
            attempt(22, RUN, BatchStep.CLEAN_SESSION, false), Optional.empty(), Optional.empty());
    var skipped = terminal(attempt(23, RUN, BatchStep.CLEAN_BATCH_RUN, true), START, SKIPPED);
    var input = sevenSlots();
    input.set(0, Optional.of(success));
    input.set(2, Optional.of(running));
    input.set(5, Optional.of(skipped));

    var snapshot = new RejectedSnapshot(RUN, input);
    input.clear();

    assertEquals(RUN, snapshot.run());
    assertEquals(7, snapshot.entries().size());
    assertEquals(21, snapshot.entries().get(0).orElseThrow().attempt().id());
    assertEquals(135, snapshot.entries().get(0).orElseThrow().result().orElseThrow().bytes());
    assertEquals(Optional.of(END), snapshot.entries().get(0).orElseThrow().endedAt());
    assertEquals(22, snapshot.entries().get(2).orElseThrow().attempt().id());
    assertTrue(snapshot.entries().get(2).orElseThrow().result().isEmpty());
    assertTrue(snapshot.entries().get(2).orElseThrow().endedAt().isEmpty());
    assertEquals(Optional.of(SKIPPED), snapshot.entries().get(5).orElseThrow().result());
    for (int absent : List.of(1, 3, 4, 6)) assertTrue(snapshot.entries().get(absent).isEmpty());
    assertThrows(UnsupportedOperationException.class, () -> snapshot.entries().clear());
    assertEquals("CleanupRejectedSnapshot[data=<redacted>]", snapshot.toString());
  }

  @Test
  void rejectsWrongSlotForeignRunAndDuplicateIdIndependently() {
    var first = terminal(attempt(21, RUN, BatchStep.CLEAN_NOTIFICATION, false), END, SUCCESS);
    var wrongSlot = sevenSlots();
    wrongSlot.set(1, Optional.of(first));
    assertInvalidSnapshot(wrongSlot);

    var foreign = sevenSlots();
    foreign.set(
        0,
        Optional.of(
            terminal(attempt(21, OTHER_RUN, BatchStep.CLEAN_NOTIFICATION, false), END, SUCCESS)));
    assertInvalidSnapshot(foreign);

    var duplicate = sevenSlots();
    duplicate.set(0, Optional.of(first));
    duplicate.set(
        1, Optional.of(terminal(attempt(21, RUN, BatchStep.CLEAN_QUESTION, false), END, SUCCESS)));
    assertInvalidSnapshot(duplicate);
  }

  @Test
  void rejectsNonCleanupInconsistentPhaseAndTime() {
    var current = attempt(21, RUN, BatchStep.CLEAN_NOTIFICATION, false);
    var outside = attempt(22, RUN, BatchStep.BACKUP_DB, false);
    assertEquals(
        INVALID_ROW,
        assertThrows(
                IllegalArgumentException.class,
                () -> new RejectedEntry(outside, Optional.empty(), Optional.empty()))
            .getMessage());
    assertEquals(
        INVALID_ROW,
        assertThrows(
                IllegalArgumentException.class,
                () -> new RejectedEntry(current, Optional.of(END), Optional.empty()))
            .getMessage());
    assertEquals(
        "Cleanup rejection time invalid",
        assertThrows(IllegalArgumentException.class, () -> terminal(current, CUTOFF, SUCCESS))
            .getMessage());
    assertEquals(
        "Cleanup rejection skip invalid",
        assertThrows(IllegalArgumentException.class, () -> terminal(current, END, SKIPPED))
            .getMessage());
  }

  @Test
  void refusesWrongWidthAndMissingRequiredValues() {
    var attempt = attempt(21, RUN, BatchStep.CLEAN_NOTIFICATION, false);
    assertEquals(
        "Cleanup rejection slots invalid",
        assertThrows(IllegalArgumentException.class, () -> new RejectedSnapshot(RUN, List.of()))
            .getMessage());
    assertThrows(NullPointerException.class, () -> new RejectedSnapshot(null, sevenSlots()));
    var missing = sevenSlots();
    missing.set(4, null);
    assertThrows(NullPointerException.class, () -> new RejectedSnapshot(RUN, missing));
    assertThrows(
        NullPointerException.class, () -> new RejectedEntry(attempt, null, Optional.of(SUCCESS)));
  }

  private static BatchStepAttempt attempt(long id, BatchRun run, BatchStep step, boolean skipped) {
    return new BatchStepAttempt(id, run, step, 1, START, skipped);
  }

  private static RejectedEntry terminal(
      BatchStepAttempt attempt, Instant endedAt, BatchStepResult result) {
    return new RejectedEntry(attempt, Optional.of(endedAt), Optional.of(result));
  }

  private static List<Optional<RejectedEntry>> sevenSlots() {
    return new ArrayList<>(Collections.nCopies(7, Optional.empty()));
  }

  private static void assertInvalidSnapshot(List<Optional<RejectedEntry>> slots) {
    assertEquals(
        INVALID_IDENTITY,
        assertThrows(IllegalArgumentException.class, () -> new RejectedSnapshot(RUN, slots))
            .getMessage());
  }
}
