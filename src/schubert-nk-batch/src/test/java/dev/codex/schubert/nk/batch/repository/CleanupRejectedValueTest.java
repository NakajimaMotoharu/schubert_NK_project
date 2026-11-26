package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.CleanupTerminalRepository.Entry;
import dev.codex.schubert.nk.batch.repository.CleanupTerminalRepository.RejectedEntry;
import dev.codex.schubert.nk.batch.repository.CleanupTerminalRepository.RejectedSnapshot;
import dev.codex.schubert.nk.batch.repository.CleanupTerminalRepository.Snapshot;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** PT-BAT-REJVAL001..011. Closed values only; the repository does not execute. */
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

  private static final List<BatchStep> TERMINAL_STEPS =
      List.of(
          BatchStep.CLEAN_NOTIFICATION,
          BatchStep.CLEAN_QUESTION,
          BatchStep.CLEAN_SESSION,
          BatchStep.CLEAN_INBOX_OUTBOX,
          BatchStep.CLEAN_LOG,
          BatchStep.CLEAN_BATCH_RUN,
          BatchStep.CLEAN_TRANSFER);

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

  @Test
  void equivalentReportsHaveValueIdentityAndRedactedDiagnostics() {
    var initial = terminal(attempt(21, RUN, BatchStep.CLEAN_NOTIFICATION, false), END, SUCCESS);
    var reconstructed =
        terminal(attempt(21, RUN, BatchStep.CLEAN_NOTIFICATION, false), END, SUCCESS);
    var later =
        terminal(
            attempt(21, RUN, BatchStep.CLEAN_NOTIFICATION, false), END.plusSeconds(1), SUCCESS);
    var first = sevenSlots();
    var second = sevenSlots();
    var changed = sevenSlots();
    first.set(0, Optional.of(initial));
    second.set(0, Optional.of(reconstructed));
    changed.set(0, Optional.of(later));

    var initialSnapshot = new RejectedSnapshot(RUN, first);
    var reconstructedSnapshot = new RejectedSnapshot(RUN, second);
    assertEquals(initial, reconstructed);
    assertNotEquals(initial, later);
    assertTrue(new HashSet<>(List.of(initial)).contains(reconstructed));
    assertEquals(initialSnapshot, reconstructedSnapshot);
    assertNotEquals(initialSnapshot, new RejectedSnapshot(RUN, changed));
    assertTrue(new HashSet<>(List.of(initialSnapshot)).contains(reconstructedSnapshot));

    var diagnostic = initial.toString();
    assertTrue(diagnostic.contains("observation=<redacted>"));
    assertFalse(diagnostic.contains(RUN.id().toString()));
    assertFalse(diagnostic.contains("135"));
  }

  @Test
  void terminalSnapshotDiagnosticsOmitBothRunsAndAllStoredObservations() {
    var successfulRows = new ArrayList<Entry>();
    var warningRows = new ArrayList<Entry>();
    var warning =
        new BatchStepResult(
            BatchStepResult.Status.WARNING,
            27,
            26,
            1,
            163,
            BatchStepResult.Reason.PROTECTED_RECORDS);
    for (int slot = 0; slot < TERMINAL_STEPS.size(); slot++) {
      BatchStep step = TERMINAL_STEPS.get(slot);
      successfulRows.add(new Entry(attempt(201 + slot, RUN, step, false), END, SUCCESS));
      warningRows.add(
          new Entry(
              attempt(401 + slot, OTHER_RUN, step, false), END, slot == 4 ? warning : SUCCESS));
    }

    var successful = new Snapshot(successfulRows);
    var protectedRecords = new Snapshot(warningRows);
    successfulRows.clear();
    warningRows.clear();

    assertEquals(0, successful.exitCode());
    assertEquals(10, protectedRecords.exitCode());
    assertEquals(7, successful.entries().size());
    assertEquals(7, protectedRecords.entries().size());
    assertEquals(135, successful.entries().getFirst().result().bytes());
    assertEquals(163, protectedRecords.entries().get(4).result().bytes());
    assertThrows(UnsupportedOperationException.class, () -> protectedRecords.entries().clear());
    String expectedDiagnostic = "CleanupTerminalSnapshot[data=<redacted>]";
    assertEquals(expectedDiagnostic, successful.toString());
    assertEquals(expectedDiagnostic, protectedRecords.toString());
  }

  @Test
  void terminalSnapshotRejectsWrongWidthStepOrderMixedRunAndDuplicateId() {
    var baseline = terminalRows();
    var extra = new ArrayList<>(baseline);
    extra.add(baseline.getLast());
    for (List<Entry> incorrectSize : List.of(List.<Entry>of(), extra)) {
      assertEquals(
          "Cleanup terminal incomplete",
          assertThrows(IllegalArgumentException.class, () -> new Snapshot(incorrectSize))
              .getMessage());
    }

    var wrongOrder = new ArrayList<>(baseline);
    Collections.swap(wrongOrder, 1, 2);
    var otherRun = new ArrayList<>(baseline);
    otherRun.set(
        1, new Entry(attempt(202, OTHER_RUN, BatchStep.CLEAN_QUESTION, false), END, SUCCESS));
    var duplicate = new ArrayList<>(baseline);
    duplicate.set(1, new Entry(attempt(201, RUN, BatchStep.CLEAN_QUESTION, false), END, SUCCESS));
    for (List<Entry> inconsistent : List.of(wrongOrder, otherRun, duplicate)) {
      assertEquals(
          "Cleanup terminal inconsistent",
          assertThrows(IllegalArgumentException.class, () -> new Snapshot(inconsistent))
              .getMessage());
    }
    assertThrows(NullPointerException.class, () -> new Snapshot(null));
    var missing = new ArrayList<>(baseline);
    missing.set(2, null);
    assertThrows(NullPointerException.class, () -> new Snapshot(missing));
  }

  @Test
  void terminalSnapshotKeysDistinguishAnIndependentlyChangedLastObservation() {
    var baseline = new Snapshot(terminalRows());
    var equivalent = new Snapshot(terminalRows());
    var alternative = terminalRows();
    var attempt = attempt(207, RUN, BatchStep.CLEAN_TRANSFER, false);
    alternative.set(6, new Entry(attempt, END.plusSeconds(1), SUCCESS));
    var changed = new Snapshot(alternative);

    assertEquals(baseline, equivalent);
    assertNotEquals(baseline, changed);
    assertNotEquals(baseline, null);
    assertNotEquals(baseline, baseline.entries());
    var retained = new HashSet<>(List.of(baseline));
    assertTrue(retained.contains(equivalent));
    assertFalse(retained.contains(changed));
  }

  @Test
  void terminalEntryAdmitsProgressEvidenceOnlyForSuccessfulLogAndInboxOutbox() {
    String observedDigest = "0123456789abcdef".repeat(4);
    var present = Optional.of(observedDigest);
    for (BatchStep step : List.of(BatchStep.CLEAN_LOG, BatchStep.CLEAN_INBOX_OUTBOX)) {
      var handle = attempt(301, RUN, step, false);
      var completed = new Entry(handle, END, SUCCESS, present);
      assertEquals(handle, completed.attempt());
      assertEquals(END, completed.endedAt());
      assertEquals(SUCCESS, completed.result());
      assertEquals(present, completed.progressSeal());
      assertTrue(new Entry(handle, END, SUCCESS).progressSeal().isEmpty());
    }

    var log = attempt(301, RUN, BatchStep.CLEAN_LOG, false);
    for (String malformed : List.of("", "a".repeat(63), "A".repeat(64), "g".repeat(64))) {
      var invalid =
          assertThrows(
              IllegalArgumentException.class,
              () -> new Entry(log, END, SUCCESS, Optional.of(malformed)));
      assertEquals("Cleanup progress seal invalid", invalid.getMessage());
    }
    var transfer = attempt(301, RUN, BatchStep.CLEAN_TRANSFER, false);
    var skippedLog = attempt(301, RUN, BatchStep.CLEAN_LOG, true);
    var warning =
        new BatchStepResult(
            BatchStepResult.Status.WARNING, 1, 0, 1, 0, BatchStepResult.Reason.PROTECTED_RECORDS);
    for (var candidate :
        List.<Executable>of(
            () -> new Entry(transfer, END, SUCCESS, present),
            () -> new Entry(skippedLog, END, SKIPPED, present),
            () -> new Entry(log, END, warning, present))) {
      assertEquals(
          "Cleanup progress seal invalid",
          assertThrows(IllegalArgumentException.class, candidate).getMessage());
    }
  }

  @Test
  void terminalEntryRejectsInvalidPhaseTimestampAndMissingFields() {
    var handle = attempt(301, RUN, BatchStep.CLEAN_LOG, false);
    var outOfScope = attempt(301, RUN, BatchStep.BACKUP_DB, false);
    var failed =
        new BatchStepResult(
            BatchStepResult.Status.FAILED, 1, 0, 1, 0, BatchStepResult.Reason.DATABASE_FAILURE);
    var greatest = Instant.parse("9999-12-31T23:59:59.999999Z");
    assertEquals(START, new Entry(handle, START, SUCCESS).endedAt());
    assertEquals(greatest, new Entry(handle, greatest, SUCCESS).endedAt());
    for (var candidate :
        List.<Executable>of(
            () -> new Entry(outOfScope, END, SUCCESS),
            () -> new Entry(handle, START.minusNanos(1_000), SUCCESS),
            () -> new Entry(handle, greatest.plusNanos(1_000), SUCCESS),
            () -> new Entry(handle, END.plusNanos(1), SUCCESS),
            () -> new Entry(handle, END, failed))) {
      assertEquals(
          "Cleanup terminal invalid",
          assertThrows(IllegalArgumentException.class, candidate).getMessage());
    }
    assertThrows(NullPointerException.class, () -> new Entry(null, END, SUCCESS));
    assertThrows(NullPointerException.class, () -> new Entry(handle, null, SUCCESS));
    assertThrows(NullPointerException.class, () -> new Entry(handle, END, null));
    assertThrows(NullPointerException.class, () -> new Entry(handle, END, SUCCESS, null));
  }

  @Test
  void terminalEntryKeyRetainsTheObservationAndNestedValuesStayRedacted() {
    var handle = attempt(301, RUN, BatchStep.CLEAN_LOG, false);
    var first = new Entry(handle, END, SUCCESS);
    var equal = new Entry(attempt(301, RUN, BatchStep.CLEAN_LOG, false), END, SUCCESS);
    assertEquals(first, equal);
    var retained = new HashSet<>(List.of(first));
    assertTrue(retained.contains(equal));
    assertFalse(retained.contains(new Entry(handle, END.plusSeconds(1), SUCCESS)));
    assertNotEquals(first, new Entry(handle, END, SUCCESS, Optional.of("b".repeat(64))));
    String diagnostic = first.toString();
    assertTrue(diagnostic.contains("BatchStepAttempt[identity/time=<redacted>]"));
    assertTrue(diagnostic.contains("BatchStepResult[observation=<redacted>]"));
    assertFalse(diagnostic.contains(RUN.id().toString()));
  }

  private static List<Entry> terminalRows() {
    var rows = new ArrayList<Entry>();
    for (int i = 0; i < TERMINAL_STEPS.size(); i++) {
      rows.add(new Entry(attempt(201 + i, RUN, TERMINAL_STEPS.get(i), false), END, SUCCESS));
    }
    return rows;
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
