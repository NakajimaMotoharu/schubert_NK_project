package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.cleanup.StepCleanupSummary;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** NK-BAT-001/OPS009/DAT009/UI251/SS331 3.14/332/341; SSC057/PG164; BAT154..161. */
final class CleanupStepValuesTest {
  private static final String FIXTURE_CLEAN_BATCH_RUN_8E2C7ACA = "CLEAN_BATCH_RUN";
  static final BatchRun RUN = new BatchRun(new UUID(1, 2), Instant.parse("2026-09-12T15:00:00Z"));
  static final CleanupCounts ZERO = new CleanupCounts(0, 0, 0);

  static BatchStepAttempt attempt(CleanupKind kind) {
    return new BatchStepAttempt(
        1, RUN, kind.step(), 1, Instant.parse("2026-09-13T02:00:00Z"), false);
  }

  static CleanupStepChunk value(
      CleanupKind k,
      CleanupCounts delta,
      Optional<CleanupCounts> total,
      boolean end,
      CleanupStepChunk.Reason reason) {
    return new CleanupStepChunk(attempt(k), k, delta, total, end, reason);
  }

  @Test
  void kindStepMapping() {
    String[] expected = {
      "CLEAN_NOTIFICATION",
      "CLEAN_QUESTION",
      "CLEAN_SESSION",
      "CLEAN_INBOX_OUTBOX",
      "CLEAN_LOG",
      FIXTURE_CLEAN_BATCH_RUN_8E2C7ACA,
      FIXTURE_CLEAN_BATCH_RUN_8E2C7ACA,
      FIXTURE_CLEAN_BATCH_RUN_8E2C7ACA,
      FIXTURE_CLEAN_BATCH_RUN_8E2C7ACA
    };
    assertEquals(9, CleanupKind.values().length);
    for (int i = 0; i < expected.length; i++)
      assertEquals(expected[i], CleanupKind.values()[i].step().name());
    for (var k : CleanupKind.values()) {
      if (k == CleanupKind.LOGS)
        assertThrows(
            IllegalArgumentException.class, () -> CleanupStepChunk.requireMapping(attempt(k), k));
      else assertDoesNotThrow(() -> CleanupStepChunk.requireMapping(attempt(k), k));
    }
    var skipped = new BatchStepAttempt(1, RUN, BatchStep.CLEAN_LOG, 1, RUN.cutoff(), true);
    assertThrows(
        IllegalArgumentException.class,
        () -> CleanupStepChunk.requireMapping(skipped, CleanupKind.LOGS));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            CleanupStepChunk.requireMapping(
                attempt(CleanupKind.QUESTIONS), CleanupKind.NOTIFICATIONS));
  }

  @Test
  void successfulChunkContracts() {
    var result =
        value(
            CleanupKind.QUESTIONS,
            new CleanupCounts(2, 2, 0),
            Optional.of(new CleanupCounts(5, 5, 0)),
            false,
            CleanupStepChunk.Reason.OK);
    assertEquals(new CleanupCounts(2, 2, 0), result.counts());
    assertEquals(Optional.of(new CleanupCounts(5, 5, 0)), result.stepCounts());
    assertEquals(Optional.of(new CleanupCounts(3, 3, 0)), result.beforeCounts());
    assertFalse(result.complete());
    assertEquals(CleanupStepChunk.Reason.OK, result.reason());
    assertEquals(CleanupKind.QUESTIONS, result.kind());
    assertEquals(attempt(CleanupKind.QUESTIONS), result.attempt());
    assertTrue(
        value(
                CleanupKind.QUESTIONS,
                ZERO,
                Optional.of(new CleanupCounts(5, 5, 0)),
                true,
                CleanupStepChunk.Reason.OK)
            .complete());
    assertThrows(
        IllegalArgumentException.class,
        () ->
            value(
                CleanupKind.QUESTIONS, ZERO, Optional.of(ZERO), false, CleanupStepChunk.Reason.OK));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            value(
                CleanupKind.QUESTIONS,
                new CleanupCounts(1, 1, 0),
                Optional.of(new CleanupCounts(1, 1, 0)),
                true,
                CleanupStepChunk.Reason.OK));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            value(
                CleanupKind.QUESTIONS,
                new CleanupCounts(1, 0, 1),
                Optional.of(new CleanupCounts(1, 1, 0)),
                false,
                CleanupStepChunk.Reason.OK));
  }

  @Test
  void rejectionAndDeferredContracts() {
    assertEquals(
        List.of("OK", "LOCK_BUSY", "BACKUP_GATE", "FOREIGN_KEY_CONFLICT"),
        Arrays.stream(CleanupStepChunk.Reason.values()).map(Enum::name).toList());
    for (var reason :
        List.of(CleanupStepChunk.Reason.LOCK_BUSY, CleanupStepChunk.Reason.BACKUP_GATE)) {
      var value = value(CleanupKind.QUESTIONS, ZERO, Optional.empty(), false, reason);
      assertEquals(Optional.empty(), value.stepCounts());
      assertEquals(Optional.empty(), value.beforeCounts());
      assertFalse(value.complete());
      assertThrows(
          IllegalArgumentException.class,
          () -> value(CleanupKind.QUESTIONS, ZERO, Optional.of(ZERO), false, reason));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              value(
                  CleanupKind.QUESTIONS,
                  new CleanupCounts(1, 1, 0),
                  Optional.empty(),
                  false,
                  reason));
      assertThrows(
          IllegalArgumentException.class,
          () -> value(CleanupKind.QUESTIONS, ZERO, Optional.empty(), true, reason));
    }
    var fk =
        value(
            CleanupKind.QUESTIONS,
            ZERO,
            Optional.of(new CleanupCounts(5, 5, 0)),
            false,
            CleanupStepChunk.Reason.FOREIGN_KEY_CONFLICT);
    assertEquals(Optional.of(new CleanupCounts(5, 5, 0)), fk.stepCounts());
    assertFalse(fk.complete());
    assertThrows(
        IllegalArgumentException.class,
        () ->
            value(
                CleanupKind.NOTIFICATIONS,
                ZERO,
                Optional.of(ZERO),
                false,
                CleanupStepChunk.Reason.FOREIGN_KEY_CONFLICT));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            value(
                CleanupKind.QUESTIONS,
                ZERO,
                Optional.empty(),
                false,
                CleanupStepChunk.Reason.FOREIGN_KEY_CONFLICT));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            value(CleanupKind.QUESTIONS, ZERO, Optional.empty(), true, CleanupStepChunk.Reason.OK));
    assertThrows(IllegalArgumentException.class, () -> CleanupStepChunk.Reason.valueOf("UNKNOWN"));
    assertEquals(CleanupStepChunk.Reason.OK, CleanupStepChunk.Reason.valueOf("OK"));
  }

  @Test
  void summaryCountsAndCompletion() {
    for (boolean deferred : List.of(false, true)) {
      var summary =
          new StepCleanupSummary(
              attempt(CleanupKind.QUESTIONS),
              CleanupKind.QUESTIONS,
              new CleanupCounts(3, 3, 0),
              new CleanupCounts(5, 5, 0),
              deferred);
      assertEquals(attempt(CleanupKind.QUESTIONS), summary.attempt());
      assertEquals(CleanupKind.QUESTIONS, summary.kind());
      assertEquals(new CleanupCounts(3, 3, 0), summary.before());
      assertEquals(new CleanupCounts(5, 5, 0), summary.after());
      assertEquals(new CleanupCounts(2, 2, 0), summary.callCounts());
      assertEquals(!deferred, summary.complete());
      assertEquals(deferred, summary.deferred());
    }
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new StepCleanupSummary(
                attempt(CleanupKind.OUTBOX), CleanupKind.OUTBOX, ZERO, ZERO, true));
    assertEquals(
        ZERO,
        new StepCleanupSummary(attempt(CleanupKind.OUTBOX), CleanupKind.OUTBOX, ZERO, ZERO, false)
            .callCounts());
  }

  @Test
  void counterOverflowAndBounds() {
    var max = new CleanupCounts(Long.MAX_VALUE, Long.MAX_VALUE, 0);
    var all =
        value(CleanupKind.QUESTIONS, max, Optional.of(max), false, CleanupStepChunk.Reason.OK);
    assertEquals(Optional.of(ZERO), all.beforeCounts());
    assertEquals(
        max,
        new StepCleanupSummary(
                attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, ZERO, max, false)
            .callCounts());
    assertEquals(
        ZERO,
        new StepCleanupSummary(
                attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, max, max, false)
            .callCounts());
    assertThrows(
        IllegalArgumentException.class,
        () ->
            value(
                CleanupKind.QUESTIONS,
                new CleanupCounts(2, 2, 0),
                Optional.of(new CleanupCounts(1, 1, 0)),
                false,
                CleanupStepChunk.Reason.OK));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            value(
                CleanupKind.QUESTIONS,
                ZERO,
                Optional.of(new CleanupCounts(1, 0, 1)),
                true,
                CleanupStepChunk.Reason.OK));
    for (CleanupCounts[] pair :
        List.of(
            new CleanupCounts[] {new CleanupCounts(1, 0, 1), new CleanupCounts(1, 1, 0)},
            new CleanupCounts[] {ZERO, new CleanupCounts(1, 0, 1)},
            new CleanupCounts[] {new CleanupCounts(2, 2, 0), new CleanupCounts(1, 1, 0)}))
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new StepCleanupSummary(
                  attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, pair[0], pair[1], false));
    assertThrows(IllegalArgumentException.class, () -> new CleanupCounts(-1, -1, 0));
    assertThrows(IllegalArgumentException.class, () -> new CleanupCounts(1, 2, 0));
  }

  @Test
  void nullAndRedaction() {
    assertThrows(
        NullPointerException.class,
        () -> CleanupStepChunk.requireMapping(null, CleanupKind.QUESTIONS));
    assertThrows(
        NullPointerException.class,
        () -> CleanupStepChunk.requireMapping(attempt(CleanupKind.QUESTIONS), null));
    assertThrows(
        NullPointerException.class,
        () ->
            value(
                CleanupKind.QUESTIONS, null, Optional.of(ZERO), true, CleanupStepChunk.Reason.OK));
    assertThrows(
        NullPointerException.class,
        () -> value(CleanupKind.QUESTIONS, ZERO, null, true, CleanupStepChunk.Reason.OK));
    assertThrows(
        NullPointerException.class,
        () -> value(CleanupKind.QUESTIONS, ZERO, Optional.of(ZERO), true, null));
    assertThrows(
        NullPointerException.class,
        () ->
            new StepCleanupSummary(
                attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, null, ZERO, false));
    assertThrows(
        NullPointerException.class,
        () ->
            new StepCleanupSummary(
                attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, ZERO, null, false));
    assertEquals(
        "CleanupStepChunk[observation=<redacted>]",
        value(CleanupKind.QUESTIONS, ZERO, Optional.of(ZERO), true, CleanupStepChunk.Reason.OK)
            .toString());
    assertEquals(
        "StepCleanupSummary[observation=<redacted>]",
        new StepCleanupSummary(
                attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, ZERO, ZERO, true)
            .toString());
  }

  @Test
  void immutableValues() {
    var a = value(CleanupKind.QUESTIONS, ZERO, Optional.of(ZERO), true, CleanupStepChunk.Reason.OK);
    var b =
        value(
            CleanupKind.QUESTIONS,
            new CleanupCounts(0, 0, 0),
            Optional.of(new CleanupCounts(0, 0, 0)),
            true,
            CleanupStepChunk.Reason.OK);
    assertEquals(a, b);
    assertEquals(a.hashCode(), b.hashCode());
    assertNotEquals(
        a,
        value(
            CleanupKind.QUESTIONS,
            ZERO,
            Optional.of(ZERO),
            false,
            CleanupStepChunk.Reason.FOREIGN_KEY_CONFLICT));
    var s =
        new StepCleanupSummary(
            attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, ZERO, ZERO, false);
    var t =
        new StepCleanupSummary(
            attempt(CleanupKind.QUESTIONS),
            CleanupKind.QUESTIONS,
            new CleanupCounts(0, 0, 0),
            new CleanupCounts(0, 0, 0),
            false);
    assertEquals(s, t);
    assertEquals(s.hashCode(), t.hashCode());
    assertNotEquals(
        s,
        new StepCleanupSummary(
            attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, ZERO, ZERO, true));
  }

  @Test
  void concurrentValues() throws Exception {
    try (var pool = Executors.newVirtualThreadPerTaskExecutor()) {
      List<Future<CleanupStepChunk>> values = new ArrayList<>();
      for (int i = 0; i < 64; i++) {
        int n = i;
        values.add(
            pool.submit(
                () ->
                    value(
                        CleanupKind.QUESTIONS,
                        new CleanupCounts(n, n, 0),
                        Optional.of(new CleanupCounts(100, 100, 0)),
                        n == 0,
                        CleanupStepChunk.Reason.OK)));
      }
      for (int i = 0; i < 64; i++) {
        var v = values.get(i).get(5, TimeUnit.SECONDS);
        assertEquals(Optional.of(new CleanupCounts(100 - i, 100 - i, 0)), v.beforeCounts());
        assertEquals(new CleanupCounts(i, i, 0), v.counts());
        assertEquals(i == 0, v.complete());
      }
    }
  }
}
