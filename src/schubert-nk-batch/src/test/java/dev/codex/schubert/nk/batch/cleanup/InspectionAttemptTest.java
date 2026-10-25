package dev.codex.schubert.nk.batch.cleanup;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.CleanupCounts;
import dev.codex.schubert.nk.batch.repository.InspectionSummary;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion.Outcome;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** NK-BAT-001; SS341 7.3/SSC049/PG162; PT-BAT-122..129. Independent fixed count oracle. */
final class InspectionAttemptTest {
  static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
          Instant.parse("2026-09-12T15:00:00.123456Z"));
  static final CleanupCounts ZERO = new CleanupCounts(0, 0, 0);

  static InspectionSummary value(long t, long d, long p, boolean end) {
    return new InspectionSummary(RUN, new CleanupCounts(t, d, p), end);
  }

  static InspectionAttempt reconcile(
      Optional<InspectionSummary> before, InspectionSummary after, int receipt) {
    return InspectionAttempt.reconcile(RUN, before, after, receipt);
  }

  static void rejected(Runnable task) {
    var error = assertThrows(IllegalArgumentException.class, task::run);
    assertEquals("inspection attempt mismatch", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  @Test
  void matchingSuccessAndWarning() {
    for (var after : List.of(value(7, 7, 0, true), value(7, 3, 4, true))) {
      int code = after.counts().skipped() == 0 ? 0 : 10;
      var actual = reconcile(Optional.empty(), after, code);
      assertEquals(RUN, actual.run());
      assertEquals(new CleanupCounts(7, code == 0 ? 7 : 3, code == 0 ? 0 : 4), actual.cumulative());
      assertEquals(actual.cumulative(), actual.attempt());
      assertEquals(code == 0 ? Outcome.SUCCESS : Outcome.WARNING, actual.outcome());
      assertEquals(code, actual.outcome().exitCode());
    }
  }

  @Test
  void zeroAndResumedAttemptCounts() {
    var zero = reconcile(Optional.empty(), value(0, 0, 0, true), 0);
    assertEquals(ZERO, zero.attempt());
    assertEquals(ZERO, zero.cumulative());
    assertEquals(Outcome.SUCCESS, zero.outcome());
    var resumed = reconcile(Optional.of(value(5, 2, 3, false)), value(9, 5, 4, true), 10);
    assertEquals(new CleanupCounts(4, 3, 1), resumed.attempt());
    assertEquals(new CleanupCounts(9, 5, 4), resumed.cumulative());
    var unchanged = reconcile(Optional.of(value(5, 2, 3, false)), value(5, 2, 3, true), 10);
    assertEquals(ZERO, unchanged.attempt());
    assertEquals(Outcome.WARNING, unchanged.outcome());
  }

  @Test
  void completedBaselineImmutability() {
    for (var baseline : List.of(value(0, 0, 0, true), value(5, 5, 0, true), value(5, 2, 3, true))) {
      int receipt = baseline.counts().skipped() == 0 ? 0 : 10;
      var result = reconcile(Optional.of(baseline), baseline, receipt);
      assertEquals(ZERO, result.attempt());
      assertEquals(baseline.counts(), result.cumulative());
      assertEquals(receipt, result.outcome().exitCode());
      rejected(
          () ->
              reconcile(
                  Optional.of(baseline),
                  new InspectionSummary(RUN, baseline.counts(), false),
                  receipt));
    }
    rejected(() -> reconcile(Optional.of(value(5, 2, 3, true)), value(6, 3, 3, true), 10));
    rejected(() -> reconcile(Optional.of(value(5, 2, 3, true)), value(5, 3, 2, true), 10));
  }

  @Test
  void countRegressionAndOverflow() {
    rejected(() -> reconcile(Optional.of(value(5, 2, 3, false)), value(4, 2, 2, true), 10));
    rejected(() -> reconcile(Optional.of(value(5, 2, 3, false)), value(6, 1, 5, true), 10));
    rejected(() -> reconcile(Optional.of(value(5, 2, 3, false)), value(6, 4, 2, true), 10));
    rejected(
        () ->
            new InspectionAttempt(
                RUN, new CleanupCounts(5, 2, 3), new CleanupCounts(6, 3, 3), Outcome.WARNING));
    rejected(
        () ->
            new InspectionAttempt(
                RUN, new CleanupCounts(5, 2, 3), new CleanupCounts(5, 3, 2), Outcome.WARNING));
    rejected(
        () ->
            new InspectionAttempt(
                RUN, new CleanupCounts(5, 2, 3), new CleanupCounts(5, 1, 4), Outcome.WARNING));
    var max = value(Long.MAX_VALUE, Long.MAX_VALUE - 1, 1, true);
    var result =
        reconcile(Optional.of(value(Long.MAX_VALUE - 1, Long.MAX_VALUE - 1, 0, false)), max, 10);
    assertEquals(new CleanupCounts(1, 0, 1), result.attempt());
    assertEquals(new CleanupCounts(Long.MAX_VALUE, Long.MAX_VALUE - 1, 1), result.cumulative());
    assertEquals(
        new CleanupCounts(Long.MAX_VALUE, 0, Long.MAX_VALUE),
        reconcile(Optional.empty(), value(Long.MAX_VALUE, 0, Long.MAX_VALUE, true), 10).attempt());
    assertEquals(
        new CleanupCounts(Long.MAX_VALUE, Long.MAX_VALUE, 0),
        reconcile(Optional.empty(), value(Long.MAX_VALUE, Long.MAX_VALUE, 0, true), 0).attempt());
  }

  @Test
  void runIdentityAndMissingEnd() {
    for (var wrong :
        List.of(
            new BatchRun(new UUID(0, 1), RUN.cutoff()),
            new BatchRun(RUN.id(), RUN.cutoff().plusNanos(1000)))) {
      var alien = new InspectionSummary(wrong, ZERO, true);
      rejected(() -> reconcile(Optional.empty(), alien, 0));
      rejected(() -> reconcile(Optional.of(alien), value(0, 0, 0, true), 0));
      rejected(() -> InspectionAttempt.reconcile(wrong, Optional.empty(), value(0, 0, 0, true), 0));
    }
    rejected(() -> reconcile(Optional.empty(), value(0, 0, 0, false), 0));
    var equal =
        new BatchRun(
            UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
            Instant.parse("2026-09-12T15:00:00.123456Z"));
    assertNotSame(RUN, equal);
    assertEquals(
        RUN, InspectionAttempt.reconcile(equal, Optional.empty(), value(0, 0, 0, true), 0).run());
  }

  @Test
  void receiptCodesAndNulls() {
    for (int bad : List.of(-1, 1, 20, 30, 50, 70, Integer.MIN_VALUE, Integer.MAX_VALUE)) {
      rejected(() -> reconcile(Optional.empty(), value(0, 0, 0, true), bad));
      rejected(() -> reconcile(Optional.empty(), value(1, 0, 1, true), bad));
    }
    rejected(() -> reconcile(Optional.empty(), value(0, 0, 0, true), 10));
    rejected(() -> reconcile(Optional.empty(), value(1, 0, 1, true), 0));
    assertThrows(
        NullPointerException.class,
        () -> InspectionAttempt.reconcile(null, Optional.empty(), value(0, 0, 0, true), 0));
    assertThrows(NullPointerException.class, () -> reconcile(null, value(0, 0, 0, true), 0));
    assertThrows(NullPointerException.class, () -> reconcile(Optional.empty(), null, 0));
    assertThrows(
        NullPointerException.class, () -> new InspectionAttempt(null, ZERO, ZERO, Outcome.SUCCESS));
    assertThrows(
        NullPointerException.class, () -> new InspectionAttempt(RUN, null, ZERO, Outcome.SUCCESS));
    assertThrows(
        NullPointerException.class, () -> new InspectionAttempt(RUN, ZERO, null, Outcome.SUCCESS));
    assertThrows(NullPointerException.class, () -> new InspectionAttempt(RUN, ZERO, ZERO, null));
  }

  @Test
  void redactionAndValueOwnership() {
    for (var outcome : Outcome.values()) {
      var counts =
          outcome == Outcome.SUCCESS ? new CleanupCounts(3, 3, 0) : new CleanupCounts(3, 1, 2);
      var first = new InspectionAttempt(RUN, counts, ZERO, outcome);
      var copy = new InspectionAttempt(new BatchRun(RUN.id(), RUN.cutoff()), counts, ZERO, outcome);
      assertEquals(first, copy);
      assertEquals(first.hashCode(), copy.hashCode());
      assertEquals("InspectionAttempt[observation=<redacted>]", first.toString());
      assertNotEquals(first, new InspectionAttempt(RUN, counts, counts, outcome));
      rejected(
          () ->
              new InspectionAttempt(
                  RUN,
                  counts,
                  ZERO,
                  outcome == Outcome.SUCCESS ? Outcome.WARNING : Outcome.SUCCESS));
    }
  }

  @Test
  void independentConcurrentObservations() throws Exception {
    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      List<Future<InspectionAttempt>> results = new ArrayList<>();
      for (int i = 0; i < 64; i++) {
        int index = i;
        results.add(
            executor.submit(
                () -> {
                  var run = new BatchRun(new UUID(0, index + 1), RUN.cutoff());
                  return InspectionAttempt.reconcile(
                      run,
                      Optional.of(new InspectionSummary(run, new CleanupCounts(5, 2, 3), false)),
                      new InspectionSummary(run, new CleanupCounts(index + 9, index + 5, 4), true),
                      10);
                }));
      }
      for (int i = 0; i < 64; i++) {
        var result = results.get(i).get(10, TimeUnit.SECONDS);
        assertEquals(new UUID(0, i + 1), result.run().id());
        assertEquals(new CleanupCounts(i + 4, i + 3, 1), result.attempt());
        assertEquals(new CleanupCounts(i + 9, i + 5, 4), result.cumulative());
        assertEquals(Outcome.WARNING, result.outcome());
      }
    }
  }
}
