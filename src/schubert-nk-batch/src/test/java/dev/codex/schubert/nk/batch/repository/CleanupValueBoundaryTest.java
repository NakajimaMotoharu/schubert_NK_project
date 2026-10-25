package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

/** PT-BAT-CLEANVALUE001/002; SS331/332/341; independent counts and fixed SQL-name metadata. */
final class CleanupValueBoundaryTest {
  private static final long MAX = Long.MAX_VALUE;

  @Test
  void countsAcceptExactBoundsAndRejectEachInconsistentComponent() {
    long[][] valid = {
      {0, 0, 0}, {1, 0, 1}, {1, 1, 0}, {MAX, 0, MAX}, {MAX, MAX, 0}, {MAX, MAX - 1, 1}
    };
    for (long[] v : valid) {
      var counts = new CleanupCounts(v[0], v[1], v[2]);
      assertEquals(v[0], counts.target());
      assertEquals(v[1], counts.deleted());
      assertEquals(v[2], counts.skipped());
    }
    long[][] invalid = {
      {-1, 0, 0},
      {0, -1, 1},
      {0, 1, 0},
      {0, 0, -1},
      {1, 0, 0},
      {MAX, MAX, 1},
      {MAX, -1, 0},
      {MAX, 0, -1},
      {Long.MIN_VALUE, 0, 0}
    };
    for (long[] v : invalid)
      assertThrows(IllegalArgumentException.class, () -> new CleanupCounts(v[0], v[1], v[2]));
  }

  @Test
  void cleanupMetadataMatchesIndependentDdlNamesAndChunkLimits() {
    String[] kinds = {
      "NOTIFICATIONS",
      "QUESTIONS",
      "SESSIONS",
      "OUTBOX",
      "LOGS",
      "WEB_RECEIPTS",
      "BATCH_RUNS",
      "INBOX_PROGRESS",
      "LOG_PROGRESS"
    };
    // SS341 section 7 and DDL V005/V012/V014/V026; these strings never execute SQL.
    String[] functions = {
      "schubert.maintenance_cleanup_notifications",
      "schubert.maintenance_cleanup_questions",
      "schubert.maintenance_cleanup_sessions",
      "schubert.maintenance_cleanup_message_stores",
      "schubert.maintenance_cleanup_logs",
      "schubert.maintenance_cleanup_web_receipt_references",
      "schubert.maintenance_cleanup_batch_runs",
      "schubert.maintenance_cleanup_inbox_progress",
      "schubert.maintenance_cleanup_log_progress"
    };
    int[] limits = {1000, 1000, 1000, 1000, 10000, 1000, 1000, 1000, 1000};
    var actual = CleanupKind.values();
    assertEquals(9, actual.length);
    for (int i = 0; i < kinds.length; i++) {
      assertEquals(kinds[i], actual[i].name());
      assertEquals(functions[i], actual[i].function());
      assertEquals(limits[i], actual[i].maximumRows());
    }
  }
}
