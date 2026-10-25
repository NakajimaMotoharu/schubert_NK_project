package dev.codex.schubert.nk.batch.cleanup;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.CleanupChunk;
import dev.codex.schubert.nk.batch.repository.CleanupCounts;
import dev.codex.schubert.nk.batch.repository.CleanupReason;
import dev.codex.schubert.nk.batch.repository.LogCleanupProgress;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/** NK-BAT-001/DAT-009/UI251/SS331,332,341; PT-BAT-CLEANVALUE003..006; spec1981. */
final class LogCleanupValueContractTest {
  private static final BatchRun RUN =
      new BatchRun(new UUID(0, 94), Instant.parse("2026-09-17T00:00:00Z"));
  private static final CleanupCounts ZERO = new CleanupCounts(0, 0, 0);

  @Test
  void summaryUsesFixedDeltasAndCumulativeWarning() {
    var counts = new CleanupCounts(10, 5, 5);
    var end = new LogCleanupProgress(RUN, counts, true);
    var before = new CleanupCounts(3, 1, 2);
    var summary = new LogCleanupSummary(RUN, before, end);
    assertEquals(new CleanupCounts(7, 4, 3), summary.attemptCounts());
    assertEquals(10, summary.exitCode());
    assertEquals(RUN, summary.run());
    assertEquals(before, summary.before());
    assertEquals(end, summary.after());
    assertEquals(
        "LogCleanupSummary[attempt=CleanupCounts[target=7, deleted=4, skipped=3],"
            + " cumulative=CleanupCounts[target=10, deleted=5, skipped=5], exitCode=10]",
        summary.toString());
    var repeated = new LogCleanupSummary(RUN, counts, end);
    assertEquals(ZERO, repeated.attemptCounts());
    assertEquals(10, repeated.exitCode());
    var empty = new LogCleanupSummary(RUN, ZERO, new LogCleanupProgress(RUN, ZERO, true));
    assertEquals(ZERO, empty.attemptCounts());
    assertEquals(0, empty.exitCode());
    var maximum =
        new LogCleanupSummary(
            RUN,
            ZERO,
            new LogCleanupProgress(
                RUN, new CleanupCounts(Long.MAX_VALUE, Long.MAX_VALUE, 0), true));
    assertEquals(new CleanupCounts(Long.MAX_VALUE, Long.MAX_VALUE, 0), maximum.attemptCounts());
    assertEquals(0, maximum.exitCode());
  }

  @Test
  void summaryRejectsEachInvalidComponent() {
    var end = new LogCleanupProgress(RUN, new CleanupCounts(10, 5, 5), true);
    assertThrows(NullPointerException.class, () -> new LogCleanupSummary(null, ZERO, end));
    assertThrows(NullPointerException.class, () -> new LogCleanupSummary(RUN, null, end));
    assertThrows(NullPointerException.class, () -> new LogCleanupSummary(RUN, ZERO, null));
    var other = new BatchRun(new UUID(0, 95), RUN.cutoff());
    assertThrows(IllegalArgumentException.class, () -> new LogCleanupSummary(other, ZERO, end));
    assertThrows(
        IllegalArgumentException.class,
        () -> new LogCleanupSummary(RUN, ZERO, new LogCleanupProgress(RUN, ZERO, false)));
    for (var before :
        List.of(
            new CleanupCounts(11, 6, 5),
            new CleanupCounts(10, 6, 4),
            new CleanupCounts(10, 4, 6))) {
      assertThrows(IllegalArgumentException.class, () -> new LogCleanupSummary(RUN, before, end));
    }
  }

  @Test
  void progressRetainsValuesAndRejectsNulls() {
    var counts = new CleanupCounts(10, 5, 5);
    var progress = new LogCleanupProgress(RUN, counts, false);
    assertEquals(RUN, progress.run());
    assertEquals(counts, progress.counts());
    assertFalse(progress.complete());
    assertTrue(new LogCleanupProgress(RUN, counts, true).complete());
    assertThrows(NullPointerException.class, () -> new LogCleanupProgress(null, counts, true));
    assertThrows(NullPointerException.class, () -> new LogCleanupProgress(RUN, null, true));
  }

  @Test
  void chunkRequiresZeroCountsForEveryRejectedReason() {
    assertEquals(
        Set.of("OK", "LOCK_BUSY", "BACKUP_GATE"),
        Arrays.stream(CleanupReason.values()).map(Enum::name).collect(Collectors.toSet()));
    for (var reason : CleanupReason.values()) {
      var zero = new CleanupChunk(ZERO, reason);
      assertEquals(ZERO, zero.counts());
      assertEquals(reason, zero.reason());
    }
    var changed = new CleanupCounts(1, 1, 0);
    assertEquals(changed, new CleanupChunk(changed, CleanupReason.OK).counts());
    for (var reason : List.of(CleanupReason.LOCK_BUSY, CleanupReason.BACKUP_GATE)) {
      assertThrows(IllegalArgumentException.class, () -> new CleanupChunk(changed, reason));
    }
    assertThrows(NullPointerException.class, () -> new CleanupChunk(null, CleanupReason.OK));
    assertThrows(NullPointerException.class, () -> new CleanupChunk(ZERO, null));
  }
}
