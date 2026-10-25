package dev.codex.schubert.nk.batch.repository;

import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.attempt;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.locked;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.query;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.reset;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.sql;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.totals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Path;
import java.sql.SQLException;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** QA048/SSC175; RCPT004, independent physical-orphan and SQL counter oracle. */
class WebReceiptCleanupTest {
  static BatchDatabaseFixture db;

  @BeforeAll
  static void start(@TempDir Path root) throws Exception {
    db = new BatchDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void seed() throws Exception {
    reset(db);
    try (var c = db.admin()) {
      sql(c, "delete from schubert_web_session.web_receipt_references");
      sql(
          c,
          "insert into schubert_web_session.web_receipt_references values"
              + "('00000000000000000000000001',1,'2026-09-01Z'),"
              + "('00000000000000000000000002',2,'2026-09-01Z'),"
              + "('00000000000000000000000003',3,'2026-09-01Z')");
    }
  }

  @Test
  void rcpt004AtomicPhysicalOrphanAndRollbackSharedCounts() throws Exception {
    assertEquals(BatchStep.CLEAN_BATCH_RUN, CleanupKind.WEB_RECEIPTS.step());
    try (var c = locked(db, false)) {
      var repo = new CleanupStepRepository(c);
      var attempt = attempt(CleanupKind.WEB_RECEIPTS);
      var result = repo.execute(attempt, CleanupKind.WEB_RECEIPTS, 1);
      assertEquals(new CleanupCounts(1, 1, 0), result.counts());
      assertEquals("RUNNING|1|1|0|0|true", totals(c, 90014));
      c.rollback();
      assertEquals("RUNNING|0|0|0|0|true", totals(c, 90014));
      result = repo.execute(attempt, CleanupKind.WEB_RECEIPTS, 1000);
      assertEquals(new CleanupCounts(1, 1, 0), result.counts());
      c.commit();
      assertTrue(repo.execute(attempt, CleanupKind.WEB_RECEIPTS, 1000).complete());
      c.commit();
      assertEquals(
          new CleanupCounts(1, 1, 0), repo.execute(attempt, CleanupKind.BATCH_RUNS, 1000).counts());
      c.commit();
      assertEquals("RUNNING|2|2|0|0|true", totals(c, 90014));
    }
    try (var c = db.admin()) {
      assertEquals(
          "1,2",
          query(
              c,
              "select string_agg(question_id::text,',' order by question_id) from schubert_web_session.web_receipt_references"));
    }
  }

  @Test
  void rcpt004StandaloneNullBoundsIdentityAndBackupLock() throws Exception {
    String run = "'12345678-9abc-def0-8123-456789abcdef'::uuid";
    String cutoff = "'2026-09-12T15:00:00Z'::timestamptz";
    try (var c = db.open("schubert_batch");
        var s = c.createStatement()) {
      // Independent reproduction: a zone-less year10000 JST literal is still within UTC year9999.
      s.execute("set timezone='Asia/Tokyo'");
      assertEquals(
          "-32400.000000",
          query(
              c,
              "select extract(epoch from ('10000-01-01'::timestamptz-'10000-01-01 00:00:00+00'::timestamptz))::text"));
      for (String args :
          java.util.List.of(
              "NULL," + cutoff + ",1",
              run + ",NULL,1",
              run + ",'infinity'::timestamptz,1",
              run + ",'0001-01-01 00:00:00+00 BC'::timestamptz,1",
              run + ",'10000-01-01 00:00:00+00'::timestamptz,1",
              run + "," + cutoff + ",NULL",
              run + "," + cutoff + ",0",
              run + "," + cutoff + ",1001")) {
        var failure =
            assertThrows(
                SQLException.class,
                () ->
                    s.execute(
                        "select * from schubert.maintenance_cleanup_web_receipt_references("
                            + args
                            + ")"),
                args);
        assertEquals("22023", failure.getSQLState());
      }
    }
    try (var blocker = db.admin();
        var c = db.open("schubert_batch")) {
      sql(blocker, "select pg_advisory_lock(71419602)");
      assertEquals(
          "LOCK_BUSY|0",
          query(
              c,
              "select reason_code||'|'||deleted_count from schubert.maintenance_cleanup_web_receipt_references("
                  + run
                  + ","
                  + cutoff
                  + ",1000)"));
    }
    try (var c = db.admin()) {
      sql(c, "update schubert.batch_runs set business_date='2026-09-12' where id=90014");
    }
    try (var c = db.open("schubert_batch");
        var s = c.createStatement()) {
      var failure =
          assertThrows(
              SQLException.class,
              () ->
                  s.execute(
                      "select * from schubert.maintenance_cleanup_web_receipt_references("
                          + run
                          + ","
                          + cutoff
                          + ",1000)"));
      assertEquals("55000", failure.getSQLState());
    }
    try (var c = db.admin()) {
      assertEquals(
          "3", query(c, "select count(*)::text from schubert_web_session.web_receipt_references"));
    }
  }

  @Test
  void rcpt004BoundedThousandAndSameSharedStepResume() throws Exception {
    try (var c = db.admin()) {
      sql(c, "delete from schubert_web_session.web_receipt_references");
      sql(
          c,
          "insert into schubert_web_session.web_receipt_references "
              + "select lpad(i::text,26,'0'),i,'2026-09-01Z'::timestamptz from generate_series(3,1003) i");
    }
    try (var c = locked(db, false)) {
      var repo = new CleanupStepRepository(c);
      var a = attempt(CleanupKind.WEB_RECEIPTS);
      var first = repo.execute(a, CleanupKind.WEB_RECEIPTS, 1000);
      assertEquals(new CleanupCounts(1000, 1000, 0), first.counts());
      assertFalse(first.complete());
      c.commit();
      var last = repo.execute(a, CleanupKind.WEB_RECEIPTS, 1000);
      assertEquals(new CleanupCounts(1, 1, 0), last.counts());
      assertEquals("RUNNING|1001|1001|0|0|true", totals(c, 90014));
      c.commit();
      assertTrue(repo.execute(a, CleanupKind.WEB_RECEIPTS, 1000).complete());
      c.commit();
      assertEquals("RUNNING|1001|1001|0|0|true", totals(c, 90014));
    }
  }

  @Test
  void rcpt004LockedEligibleIsNotCompleteAndMissingBackupNeverDeletes() throws Exception {
    try (var blocker = db.admin();
        var c = locked(db, false)) {
      blocker.setAutoCommit(false);
      sql(
          blocker,
          "select receipt_id from schubert_web_session.web_receipt_references where question_id=3 for update");
      var result =
          new CleanupStepRepository(c)
              .execute(attempt(CleanupKind.WEB_RECEIPTS), CleanupKind.WEB_RECEIPTS, 1000);
      assertEquals(CleanupStepChunk.Reason.LOCK_BUSY, result.reason());
      assertFalse(result.complete());
      assertEquals(new CleanupCounts(0, 0, 0), result.counts());
      assertEquals("RUNNING|0|0|0|0|true", totals(c, 90014));
      c.rollback();
      blocker.rollback();
    }
    try (var admin = db.admin()) {
      sql(admin, "update schubert.batch_runs set status='FAILED' where id=90000");
    }
    try (var c = locked(db, false)) {
      var result =
          new CleanupStepRepository(c)
              .execute(attempt(CleanupKind.WEB_RECEIPTS), CleanupKind.WEB_RECEIPTS, 1000);
      assertEquals(CleanupStepChunk.Reason.BACKUP_GATE, result.reason());
      assertFalse(result.complete());
      c.rollback();
    }
    try (var c = db.admin()) {
      assertEquals(
          "3", query(c, "select count(*)::text from schubert_web_session.web_receipt_references"));
    }
  }
}
