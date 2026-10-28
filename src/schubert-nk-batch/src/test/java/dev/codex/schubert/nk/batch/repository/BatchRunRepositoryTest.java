package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-BAT-001/OPS009/DAT009/UI251/SS331 8.3/332/341; SSC055/PG163; BAT138..153. */
final class BatchRunRepositoryTest {
  private static final String FIXTURE_ATTEMPT_7FD8A755 = "attempt";
  private static final String FIXTURE_STATUS_CFC31BCC = "status";
  private static final String FIXTURE_DELETE_FROM_SCHUBERT_BATCH_RUNS_0A02FC69 =
      "delete from schubert.batch_runs";
  private static final String FIXTURE_FAILED_7E8A57FE = "FAILED";
  private static final String FIXTURE_2026_09_13_8B08300C = "2026-09-13";
  private static final String FIXTURE_2026_09_13T01_00_00Z_FE4F9CBB = "2026-09-13T01:00:00Z";
  private static final String FIXTURE_2026_09_13T01_00_01Z_7D588561 = "2026-09-13T01:00:01Z";
  private static final String FIXTURE_RUNNING_294BDBF9 = "RUNNING";
  private static final String FIXTURE_ABANDON_5A676BA9 = "abandon";
  private static final String FIXTURE_FINISH_91A2F12C = "finish";
  private static final String FIXTURE_EMPTY_E6845188 = "empty";
  private static final String FIXTURE_NULLSTATEMENT_5A17BE38 = "nullStatement";
  private static final String FIXTURE_NULLROWS_D5C4412B = "nullRows";
  private static final String FIXTURE_REPLAY_2AA31058 = "replay";
  private static final String FIXTURE_SUCCESS_10855C7F = "SUCCESS";
  private static final String FIXTURE_SCHUBERT_BATCH_F9C88479 = "schubert_batch";
  private static final String FIXTURE_HISTORY_BB36CCAE = "history";
  private static final String FIXTURE_INSERT_A0C28A2E = "insert";
  private static final String FIXTURE_RECOVER_DE33FD76 = "recover";
  private static final String FIXTURE_ROW_CLOSE_F197F129 = "row.close";
  private static final String FIXTURE_STATEMENT_CLOSE_FE807BAF = "statement.close";
  private static final String FIXTURE_STATEMENT_EXECUTEQUERY_67733F33 = "statement.executeQuery";
  @TempDir static Path root;
  static BatchDatabaseFixture db;
  static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
          Instant.parse("2026-09-12T15:00:00Z"));
  static final Instant NOW = Instant.parse("2026-09-13T02:00:00Z");
  static final Instant END = NOW.plusSeconds(1);
  static final BatchStep STEP = BatchStep.CLEAN_LOG;
  static final BatchStepResult SUCCESS =
      new BatchStepResult(BatchStepResult.Status.SUCCESS, 5, 3, 0, 9, BatchStepResult.Reason.NONE);
  static final List<String> COLS =
      List.of(
          "id",
          "run_id",
          "business_date",
          "step",
          FIXTURE_ATTEMPT_7FD8A755,
          "started_at",
          "ended_at",
          FIXTURE_STATUS_CFC31BCC,
          "target_count",
          "success_count",
          "failure_count",
          "byte_count");

  @BeforeAll
  static void start() throws Exception {
    db = new BatchDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = db.admin()) {
      sql(c, FIXTURE_DELETE_FROM_SCHUBERT_BATCH_RUNS_0A02FC69);
      sql(c, "delete from schubert.inbox_inspection_progress");
      sql(c, "delete from schubert.log_cleanup_progress");
    }
  }

  @Test
  void ordinaryResumeWithoutPriorSuccessCreatesRunningAttempt() throws Exception {
    // PT-BAT-RUN1405001 / SS331: morning-resume does not make an ordinary step a Backup.
    try (var c = locked()) {
      var repository = new BatchRunRepository(c);
      var attempt = repository.beginMorningResume(RUN, STEP, NOW, false);
      assertFalse(attempt.skipped());
      assertEquals(1, attempt.attempt());
      assertEquals("RUNNING|0|0|0|0|NULL|NULL", terminal(c, attempt.id()));
      repository.finish(attempt, END, SUCCESS);
      assertEquals("SUCCESS|5|3|0|9|NULL|NULL", terminal(c, attempt.id()));
      String beforeReadback = snapshot(c);
      repository.verifyFinished(attempt, END, SUCCESS);
      assertEquals(beforeReadback, snapshot(c));
      c.rollback();
    }
  }

  @Test
  void invalidFinishedObservationRejectsBeforeAnyJdbcReadOrWrite() throws Exception {
    // PT-BAT-RUN1405002 / SS331: skipped handles and end-before-start are not observations.
    try (var c = locked()) {
      var attempt = new BatchRunRepository(c).begin(RUN, STEP, NOW, false);
      var skipped = new BatchStepAttempt(attempt.id(), RUN, STEP, attempt.attempt(), NOW, true);
      String before = snapshot(c);
      Probe probe = new Probe();
      var repository = new BatchRunRepository(probe.wrap(c));
      assertThrows(
          IllegalArgumentException.class, () -> repository.verifyFinished(skipped, END, SUCCESS));
      assertThrows(
          IllegalArgumentException.class,
          () -> repository.verifyFinished(attempt, NOW.minusSeconds(1), SUCCESS));
      assertTrue(probe.kinds.isEmpty());
      probe.closed();
      assertEquals(before, snapshot(c));
      assertEquals("RUNNING|0|0|0|0|NULL|NULL", terminal(c, attempt.id()));
      c.rollback();
    }
  }

  @Test
  void firstAttemptAndTerminalStates() throws Exception {
    StringBuilder trace = new StringBuilder();
    try (var c = locked()) {
      var repo = new BatchRunRepository(c);
      int i = 0;
      for (var step : BatchStep.values()) {
        var a = repo.begin(RUN, step, NOW, false);
        assertEquals(1, a.attempt());
        assertFalse(a.skipped());
        assertEquals(RUN, a.run());
        assertEquals(
            "RUNNING|0|0|0|0|true|true|true",
            query(
                c,
                "select status||'|'||target_count||'|'||success_count||'|'||failure_count||'|'||byte_count||'|'||(ended_at is null)||'|'||(error_code is null)||'|'||(error_summary is null) from schubert.batch_runs where id="
                    + a.id()));
        BatchStepResult r =
            switch (i++ % 4) {
              case 0 -> SUCCESS;
              case 1 ->
                  new BatchStepResult(
                      BatchStepResult.Status.WARNING,
                      5,
                      2,
                      0,
                      8,
                      BatchStepResult.Reason.PROTECTED_RECORDS);
              case 2 ->
                  new BatchStepResult(
                      BatchStepResult.Status.FAILED,
                      6,
                      2,
                      4,
                      0,
                      BatchStepResult.Reason.DATABASE_FAILURE);
              default ->
                  new BatchStepResult(
                      BatchStepResult.Status.SKIPPED,
                      0,
                      0,
                      0,
                      0,
                      BatchStepResult.Reason.BACKUP_UNAVAILABLE);
            };
        repo.finish(a, END, r);
        String expected =
            switch ((i - 1) % 4) {
              case 0 -> "SUCCESS|5|3|0|9|NULL|NULL";
              case 1 -> "WARNING|5|2|0|8|PROTECTED_RECORDS|protected records retained";
              case 2 -> "FAILED|6|2|4|0|DATABASE_FAILURE|batch database operation failed";
              default -> "SKIPPED|0|0|0|0|BACKUP_UNAVAILABLE|verified backup unavailable";
            };
        String actual = terminal(c, a.id());
        assertEquals(expected, actual);
        trace.append(step.name()).append('=').append(actual).append('\n');
        assertEquals(
            "2026-09-13|2026-09-13 02:00:00+00|2026-09-13 02:00:01+00",
            query(
                c,
                "select business_date||'|'||started_at||'|'||ended_at from schubert.batch_runs where id="
                    + a.id()));
      }
      c.commit();
      assertEquals("10", query(c, "select count(*) from schubert.batch_runs"));
    }
    trace("PT-BAT-138-terminals.txt", trace.toString());
  }

  @Test
  void failedBackupCreatesRealSixSkipsEvenWithOldSuccessfulDeletion() throws Exception {
    try (var c = locked()) {
      var repository = new BatchRunRepository(c);
      for (var step :
          List.of(
              BatchStep.CLEAN_NOTIFICATION,
              BatchStep.CLEAN_QUESTION,
              BatchStep.CLEAN_SESSION,
              BatchStep.CLEAN_INBOX_OUTBOX,
              BatchStep.CLEAN_LOG,
              BatchStep.CLEAN_BATCH_RUN)) {
        var old = repository.begin(RUN, step, NOW, false);
        repository.finish(old, END, SUCCESS);
        c.commit();
        var saved = terminal(c, old.id());
        var current = repository.beginBackupUnavailable(RUN, step, END.plusSeconds(1), true);
        c.commit();
        assertTrue(current.skipped());
        assertEquals(2, current.attempt());
        assertNotEquals(old.id(), current.id());
        assertEquals(
            "SKIPPED|0|0|0|0|BACKUP_UNAVAILABLE|verified backup unavailable",
            terminal(c, current.id()));
        assertEquals(saved, terminal(c, old.id()));
        assertEquals(
            "true",
            query(
                c,
                "select (started_at=ended_at)::text from schubert.batch_runs where id="
                    + current.id()));
        repository.verifyBackupUnavailable(current);
        assertThrows(
            BatchRepositoryException.class, () -> repository.verifyAlreadySuccessful(current));
        sql(c, "update schubert.batch_runs set byte_count=1 where id=" + current.id());
        assertThrows(
            BatchRepositoryException.class, () -> repository.verifyBackupUnavailable(current));
        c.rollback();
      }
      for (var step :
          List.of(
              BatchStep.BACKUP_DB,
              BatchStep.BACKUP_CONFIG,
              BatchStep.CLEAN_TRANSFER,
              BatchStep.CLEAN_EXPIRY))
        assertThrows(
            IllegalArgumentException.class,
            () -> repository.beginBackupUnavailable(RUN, step, NOW, false));
      assertThrows(
          NullPointerException.class,
          () -> repository.beginBackupUnavailable(RUN, null, NOW, false));
      assertThrows(NullPointerException.class, () -> repository.verifyBackupUnavailable(null));
      var transfer = repository.begin(RUN, BatchStep.CLEAN_TRANSFER, END.plusSeconds(2), false);
      assertFalse(transfer.skipped());
      assertThrows(
          IllegalArgumentException.class, () -> repository.verifyBackupUnavailable(transfer));
      c.rollback();
    }
  }

  @Test
  void normalBackupResumeSkipsButManualRegeneratesAndReadbackIsIndependent() throws Exception {
    try (var c = locked()) {
      var repository = new BatchRunRepository(c);
      for (var step : List.of(BatchStep.BACKUP_DB, BatchStep.BACKUP_CONFIG)) {
        var old = repository.begin(RUN, step, NOW, false);
        repository.finish(old, END, SUCCESS);
        c.commit();
        String saved = terminal(c, old.id());
        var skipped = repository.beginMorningResume(RUN, step, END.plusSeconds(1), true);
        c.commit();
        assertTrue(skipped.skipped());
        assertEquals(2, skipped.attempt());
        assertEquals(
            "SKIPPED|0|0|0|0|ALREADY_SUCCESSFUL|step already successful for business date",
            terminal(c, skipped.id()));
        assertEquals(saved, terminal(c, old.id()));
        repository.verifyAlreadySuccessful(skipped);
        sql(c, "update schubert.batch_runs set byte_count=1 where id=" + skipped.id());
        assertThrows(
            BatchRepositoryException.class, () -> repository.verifyAlreadySuccessful(skipped));
        c.rollback();
        var manual = repository.begin(RUN, step, END.plusSeconds(2), false);
        assertFalse(manual.skipped());
        assertEquals(3, manual.attempt());
        assertEquals("RUNNING|0|0|0|0|NULL|NULL", terminal(c, manual.id()));
        assertThrows(
            IllegalArgumentException.class, () -> repository.verifyAlreadySuccessful(manual));
        c.rollback();
        var other = new BatchRun(new UUID(0, 77), RUN.cutoff());
        assertFalse(
            repository.beginMorningResume(other, step, END.plusSeconds(3), false).skipped());
        c.rollback();
      }
      assertThrows(NullPointerException.class, () -> repository.verifyAlreadySuccessful(null));
    }
  }

  @Test
  void ordinarySuccessSkipsByBusinessDate() throws Exception {
    try (var c = locked()) {
      var repo = new BatchRunRepository(c);
      var a = repo.begin(RUN, STEP, NOW, false);
      repo.finish(a, END, SUCCESS);
      c.commit();
      var sameDay = new BatchRun(new UUID(0, 8), RUN.cutoff().plusSeconds(30));
      var skip = repo.begin(sameDay, STEP, END.plusSeconds(1), false);
      assertTrue(skip.skipped());
      assertEquals(2, skip.attempt());
      assertEquals(
          "SKIPPED|0|0|0|0|ALREADY_SUCCESSFUL|step already successful for business date",
          terminal(c, skip.id()));
      assertEquals(
          "true",
          query(
              c,
              "select (started_at=ended_at)::text from schubert.batch_runs where id=" + skip.id()));
      var nextDay = new BatchRun(new UUID(0, 9), RUN.cutoff().plusSeconds(86400));
      var fresh = repo.begin(nextDay, STEP, NOW.plusSeconds(86400), false);
      assertFalse(fresh.skipped());
      assertEquals(1, fresh.attempt());
      assertEquals("SUCCESS|5|3|0|9|NULL|NULL", terminal(c, a.id()));
    }
  }

  @Test
  void backupAlwaysRunsAndAttemptLimit() throws Exception {
    try (var c = locked()) {
      var repo = new BatchRunRepository(c);
      for (var step : List.of(BatchStep.BACKUP_DB, BatchStep.BACKUP_CONFIG)) {
        for (int n = 1; n <= 2; n++) {
          var a = repo.begin(RUN, step, NOW.plusSeconds(n * 2), false);
          assertFalse(a.skipped());
          assertEquals(n, a.attempt());
          repo.finish(a, NOW.plusSeconds(n * 2 + 1), SUCCESS);
        }
      }
      c.commit();
      assertEquals(
          "4", query(c, "select count(*) from schubert.batch_runs where status='SUCCESS'"));
      seed(
          c,
          98,
          FIXTURE_FAILED_7E8A57FE,
          RUN.id(),
          FIXTURE_2026_09_13_8B08300C,
          FIXTURE_2026_09_13T01_00_00Z_FE4F9CBB,
          FIXTURE_2026_09_13T01_00_01Z_7D588561);
      var last = repo.begin(RUN, STEP, NOW, false);
      assertEquals(99, last.attempt());
      String before = snapshot(c);
      redacted(() -> repo.begin(RUN, STEP, END, true));
      assertEquals(before, snapshot(c));
      c.rollback();
    }
  }

  @Test
  void explicitAbandonedRecovery() throws Exception {
    try (var c = locked()) {
      seed(
          c,
          1,
          FIXTURE_RUNNING_294BDBF9,
          RUN.id(),
          FIXTURE_2026_09_13_8B08300C,
          FIXTURE_2026_09_13T01_00_00Z_FE4F9CBB,
          null);
      seed(
          c,
          2,
          "WARNING",
          RUN.id(),
          FIXTURE_2026_09_13_8B08300C,
          "2026-09-13T01:10:00Z",
          "2026-09-13T01:10:01Z");
      seed(
          c,
          3,
          FIXTURE_RUNNING_294BDBF9,
          RUN.id(),
          FIXTURE_2026_09_13_8B08300C,
          "2026-09-13T01:20:00Z",
          null);
      c.commit();
      var repo = new BatchRunRepository(c);
      String before = snapshot(c);
      redacted(() -> repo.begin(RUN, STEP, NOW, false));
      assertEquals(before, snapshot(c));
      var a = repo.begin(RUN, STEP, NOW, true);
      assertEquals(4, a.attempt());
      assertEquals(
          "FAILED:1,WARNING:2,FAILED:3,RUNNING:4",
          query(
              c,
              "select string_agg(status||':'||attempt,',' order by attempt) from schubert.batch_runs"));
      assertEquals(
          "2",
          query(
              c,
              "select count(*) from schubert.batch_runs where error_code='ABANDONED' and error_summary='previous same-run attempt abandoned' and target_count=9 and success_count=3 and failure_count=2 and byte_count=8 and ended_at=timestamptz '2026-09-13T02:00:00Z'"));
      c.rollback();
      assertEquals(before, snapshot(c));
      Probe wrong = new Probe();
      wrong.changeKind = FIXTURE_ABANDON_5A676BA9;
      wrong.changed = 0;
      redacted(() -> new BatchRunRepository(wrong.wrap(c)).begin(RUN, STEP, NOW, true));
      wrong.closed();
      c.rollback();
    }
  }

  @Test
  void foreignRunningAndRootIdentity() throws Exception {
    try (var c = locked()) {
      seed(
          c,
          1,
          FIXTURE_RUNNING_294BDBF9,
          new UUID(0, 7),
          FIXTURE_2026_09_13_8B08300C,
          FIXTURE_2026_09_13T01_00_00Z_FE4F9CBB,
          null);
      c.commit();
      String before = snapshot(c);
      redacted(() -> new BatchRunRepository(c).begin(RUN, STEP, NOW, true));
      assertEquals(before, snapshot(c));
      c.rollback();
      sql(c, FIXTURE_DELETE_FROM_SCHUBERT_BATCH_RUNS_0A02FC69);
      seed(
          c,
          1,
          FIXTURE_FAILED_7E8A57FE,
          RUN.id(),
          "2026-09-12",
          "2026-09-12T01:00:00Z",
          "2026-09-12T01:00:01Z");
      c.commit();
      redacted(() -> new BatchRunRepository(c).begin(RUN, STEP, NOW, false));
      c.rollback();
      sql(c, FIXTURE_DELETE_FROM_SCHUBERT_BATCH_RUNS_0A02FC69);
      c.commit();
      try (var admin = db.admin()) {
        sql(
            admin,
            "insert into schubert.inbox_inspection_progress(run_id,cutoff) values('"
                + RUN.id()
                + "','2026-09-12T15:00:01Z')");
      }
      redacted(() -> new BatchRunRepository(c).begin(RUN, STEP, NOW, false));
      assertEquals("0", query(c, "select count(*) from schubert.batch_runs"));
    }
  }

  @Test
  void exactFinishReplay() throws Exception {
    try (var c = locked()) {
      var repo = new BatchRunRepository(c);
      var a = repo.begin(RUN, STEP, NOW, false);
      repo.finish(a, END, SUCCESS);
      repo.finish(a, END, SUCCESS);
      c.commit();
      repo.finish(a, END, SUCCESS);
      String saved = snapshot(c);
      redacted(() -> repo.finish(a, END.plusNanos(1000), SUCCESS));
      for (var r :
          List.of(
              new BatchStepResult(
                  BatchStepResult.Status.SUCCESS, 6, 3, 0, 9, BatchStepResult.Reason.NONE),
              new BatchStepResult(
                  BatchStepResult.Status.SUCCESS, 5, 4, 0, 9, BatchStepResult.Reason.NONE),
              new BatchStepResult(
                  BatchStepResult.Status.SUCCESS, 5, 3, 0, 10, BatchStepResult.Reason.NONE),
              new BatchStepResult(
                  BatchStepResult.Status.WARNING, 5, 3, 1, 9, BatchStepResult.Reason.IO_FAILURE)))
        redacted(() -> repo.finish(a, END, r));
      assertEquals(saved, snapshot(c));
      sql(
          c,
          "update schubert.batch_runs set error_summary='public legacy diagnostic' where id="
              + a.id());
      c.commit();
      redacted(() -> repo.finish(a, END, SUCCESS));
      assertEquals(
          "public legacy diagnostic",
          query(c, "select error_summary from schubert.batch_runs where id=" + a.id()));
    }
  }

  @Test
  void handleIdentityAndMissingRows() throws Exception {
    try (var c = locked()) {
      var repo = new BatchRunRepository(c);
      var a = repo.begin(RUN, STEP, NOW, false);
      c.commit();
      for (var bad :
          List.of(
              new BatchStepAttempt(999999999999L, RUN, STEP, 1, NOW, false),
              new BatchStepAttempt(
                  a.id(), new BatchRun(new UUID(0, 9), RUN.cutoff()), STEP, 1, NOW, false),
              new BatchStepAttempt(
                  a.id(),
                  new BatchRun(new UUID(0, 10), RUN.cutoff().minusSeconds(86400)),
                  STEP,
                  1,
                  NOW,
                  false),
              new BatchStepAttempt(a.id(), RUN, BatchStep.CLEAN_SESSION, 1, NOW, false),
              new BatchStepAttempt(a.id(), RUN, STEP, 2, NOW, false),
              new BatchStepAttempt(a.id(), RUN, STEP, 1, NOW.plusNanos(1000), false))) {
        String before = snapshot(c);
        redacted(() -> repo.finish(bad, END, SUCCESS));
        assertEquals(before, snapshot(c));
      }
      assertThrows(
          IllegalArgumentException.class,
          () -> repo.finish(new BatchStepAttempt(a.id(), RUN, STEP, 1, NOW, true), END, SUCCESS));
      for (int changed : List.of(-1, 2)) {
        Probe p = new Probe();
        p.changeKind = FIXTURE_FINISH_91A2F12C;
        p.changed = changed;
        redacted(() -> new BatchRunRepository(p.wrap(c)).finish(a, END, SUCCESS));
        p.closed();
        c.rollback();
        assertEquals(
            FIXTURE_RUNNING_294BDBF9,
            query(c, "select status from schubert.batch_runs where id=" + a.id()));
      }
      repo.finish(a, END, SUCCESS);
      for (String bad :
          List.of(
              FIXTURE_EMPTY_E6845188,
              "extra",
              "matches",
              FIXTURE_NULLSTATEMENT_5A17BE38,
              FIXTURE_NULLROWS_D5C4412B)) {
        Probe p = new Probe();
        p.kind = FIXTURE_REPLAY_2AA31058;
        p.anomaly = bad;
        redacted(() -> new BatchRunRepository(p.wrap(c)).finish(a, END, SUCCESS));
        p.closed();
      }
    }
  }

  @Test
  void rollbackAndUnknownCommit() throws Exception {
    try (var c = locked();
        var observer = db.admin()) {
      var repo = new BatchRunRepository(c);
      var a = repo.begin(RUN, STEP, NOW, false);
      assertEquals("0", query(observer, "select count(*) from schubert.batch_runs"));
      c.rollback();
      assertEquals("0", query(c, "select count(*) from schubert.batch_runs"));
      var b = repo.begin(RUN, STEP, NOW, false);
      c.commit();
      redacted(() -> repo.finish(a, END, SUCCESS));
      repo.finish(b, END, SUCCESS);
      c.rollback();
      assertEquals(
          FIXTURE_RUNNING_294BDBF9,
          query(c, "select status from schubert.batch_runs where id=" + b.id()));
      repo.finish(b, END, SUCCESS);
      c.commit();
      // Simulated lost commit acknowledgement: state is independently observed committed,
      // same-value retry only.
      assertEquals(
          FIXTURE_SUCCESS_10855C7F,
          query(observer, "select status from schubert.batch_runs where id=" + b.id()));
      repo.finish(b, END, SUCCESS);
      var skip = repo.begin(RUN, STEP, END.plusSeconds(1), false);
      assertTrue(skip.skipped());
    }
  }

  @Test
  void historicalUtcAndFixedRunDay() throws Exception {
    String[][] vectors = {
      {"0001-01-01T00:00:00Z", "0001-01-01"},
      {"1582-10-04T00:00:00Z", "1582-10-04"},
      {"1582-10-04T14:50:00Z", "1582-10-05"},
      {"1582-10-10T00:00:00Z", "1582-10-10"},
      {"1582-10-15T00:00:00Z", "1582-10-15"},
      {"1900-03-01T00:00:00Z", "1900-03-01"},
      {"1970-01-01T00:00:00Z", "1970-01-01"},
      {"2026-09-12T14:59:59.999999Z", "2026-09-12"},
      {"2026-09-12T15:00:00Z", FIXTURE_2026_09_13_8B08300C},
      {"9999-12-31T23:59:59.999999Z", "10000-01-01"}
    };
    try (var c = locked()) {
      for (String zone : List.of("UTC", "Asia/Tokyo", "America/New_York")) {
        sql(c, "set timezone='" + zone + "'");
        for (String[] v : vectors) {
          sql(c, FIXTURE_DELETE_FROM_SCHUBERT_BATCH_RUNS_0A02FC69);
          var run = new BatchRun(RUN.id(), Instant.parse(v[0]));
          var repo = new BatchRunRepository(c);
          var a = repo.begin(run, STEP, run.cutoff(), false);
          repo.finish(a, run.cutoff(), SUCCESS);
          assertEquals(
              "true|true|true",
              query(
                  c,
                  "select (business_date=date '"
                      + v[1]
                      + "')||'|'||(started_at=timestamptz '"
                      + v[0]
                      + "')||'|'||(ended_at=timestamptz '"
                      + v[0]
                      + "') from schubert.batch_runs"));
          // Read the stored historical values through the opposite JDBC direction.
          var b = repo.begin(run, STEP, run.cutoff(), false);
          assertTrue(b.skipped());
          assertEquals(2, b.attempt());
        }
      }
      sql(c, FIXTURE_DELETE_FROM_SCHUBERT_BATCH_RUNS_0A02FC69);
      var a = new BatchRunRepository(c).begin(RUN, STEP, NOW.plusSeconds(86400), false);
      assertEquals(
          FIXTURE_2026_09_13_8B08300C,
          query(c, "select business_date from schubert.batch_runs where id=" + a.id()));
    }
  }

  @Test
  void clockRegressionPreservesRows() throws Exception {
    try (var c = locked()) {
      var repo = new BatchRunRepository(c);
      for (Instant bad :
          List.of(
              RUN.cutoff().minusNanos(1000),
              NOW.plusNanos(1),
              Instant.parse("+10000-01-01T00:00:00Z")))
        assertThrows(IllegalArgumentException.class, () -> repo.begin(RUN, STEP, bad, false));
      var a = repo.begin(RUN, STEP, NOW, false);
      c.commit();
      String before = snapshot(c);
      redacted(() -> repo.begin(RUN, STEP, NOW.minusNanos(1000), true));
      assertThrows(
          IllegalArgumentException.class, () -> repo.finish(a, NOW.minusNanos(1000), SUCCESS));
      assertEquals(before, snapshot(c));
      repo.finish(a, END, SUCCESS);
      c.commit();
      before = snapshot(c);
      redacted(() -> repo.begin(RUN, STEP, END.minusNanos(1000), false));
      assertEquals(before, snapshot(c));
      assertThrows(NullPointerException.class, () -> new BatchRunRepository(null));
      assertThrows(NullPointerException.class, () -> repo.begin(null, STEP, NOW, false));
      assertThrows(NullPointerException.class, () -> repo.begin(RUN, null, NOW, false));
      assertThrows(NullPointerException.class, () -> repo.begin(RUN, STEP, null, false));
      assertThrows(NullPointerException.class, () -> repo.finish(null, END, SUCCESS));
      assertThrows(NullPointerException.class, () -> repo.finish(a, null, SUCCESS));
      assertThrows(NullPointerException.class, () -> repo.finish(a, END, null));
      assertThrows(IllegalArgumentException.class, () -> repo.finish(a, END.plusNanos(1), SUCCESS));
    }
  }

  @Test
  void parentTransactionAndLock() throws Exception {
    try (var c = db.open(FIXTURE_SCHUBERT_BATCH_F9C88479)) {
      redacted(() -> new BatchRunRepository(c).begin(RUN, STEP, NOW, false));
      c.setAutoCommit(false);
      for (String command :
          List.of(
              "",
              "select pg_advisory_lock_shared(71419602)",
              "select pg_advisory_lock(0,71419602)")) {
        if (!command.isEmpty()) sql(c, command);
        redacted(() -> new BatchRunRepository(c).begin(RUN, STEP, NOW, false));
        c.rollback();
        sql(c, "select pg_advisory_unlock_all()");
        c.commit();
      }
      sql(c, "select pg_advisory_lock(71419602)");
      c.commit();
      c.setReadOnly(true);
      redacted(() -> new BatchRunRepository(c).begin(RUN, STEP, NOW, false));
      c.rollback();
      c.setReadOnly(false);
      for (int level :
          List.of(
              Connection.TRANSACTION_SERIALIZABLE,
              Connection.TRANSACTION_REPEATABLE_READ,
              Connection.TRANSACTION_READ_UNCOMMITTED)) {
        c.setTransactionIsolation(level);
        redacted(() -> new BatchRunRepository(c).begin(RUN, STEP, NOW, false));
        c.rollback();
      }
      c.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
      var a = new BatchRunRepository(c).begin(RUN, STEP, NOW, false);
      assertFalse(a.skipped());
      assertFalse(c.isClosed());
      assertFalse(c.getAutoCommit());
      assertFalse(c.isReadOnly());
      assertEquals(Connection.TRANSACTION_READ_COMMITTED, c.getTransactionIsolation());
      try (var other = db.open(FIXTURE_SCHUBERT_BATCH_F9C88479)) {
        other.setAutoCommit(false);
        redacted(() -> new BatchRunRepository(other).begin(RUN, STEP, NOW, false));
      }
    }
  }

  @Test
  void historyProjectionAndNulls() throws Exception {
    try (var c = locked()) {
      seed(
          c,
          1,
          FIXTURE_FAILED_7E8A57FE,
          RUN.id(),
          FIXTURE_2026_09_13_8B08300C,
          FIXTURE_2026_09_13T01_00_00Z_FE4F9CBB,
          FIXTURE_2026_09_13T01_00_01Z_7D588561);
      c.commit();
      List<String> anomalies = new ArrayList<>(COLS);
      anomalies.addAll(
          List.of(
              FIXTURE_NULLSTATEMENT_5A17BE38,
              FIXTURE_NULLROWS_D5C4412B,
              "badIdLow",
              "badIdHigh",
              "badDate",
              "badStep",
              "badAttemptLow",
              "badAttemptHigh",
              "unknown",
              "negativeTarget",
              "negativeSuccess",
              "negativeFailure",
              "negativeBytes",
              "earlyStart",
              "oldStart",
              "fineStart",
              "futureStart",
              "earlyEnd",
              "oldEnd",
              "fineEnd",
              "futureEnd",
              "runningEnd",
              "duplicateId",
              "duplicateAttempt",
              "tooMany",
              "doubleSuccess"));
      for (String bad : anomalies) {
        Probe p = new Probe();
        p.kind = FIXTURE_HISTORY_BB36CCAE;
        p.anomaly = bad;
        try {
          redacted(() -> new BatchRunRepository(p.wrap(c)).begin(RUN, STEP, NOW, true));
        } catch (AssertionError failure) {
          throw new AssertionError("history anomaly: " + bad, failure);
        }
        p.closed();
        c.rollback();
        assertEquals("1", query(c, "select count(*) from schubert.batch_runs"));
      }
      sql(c, FIXTURE_DELETE_FROM_SCHUBERT_BATCH_RUNS_0A02FC69);
      c.commit();
      for (String bad :
          List.of(
              FIXTURE_NULLSTATEMENT_5A17BE38,
              FIXTURE_NULLROWS_D5C4412B,
              FIXTURE_EMPTY_E6845188,
              "extra",
              "id",
              "badIdLow",
              "badIdHigh")) {
        Probe p = new Probe();
        p.kind = FIXTURE_INSERT_A0C28A2E;
        p.anomaly = bad;
        redacted(() -> new BatchRunRepository(p.wrap(c)).begin(RUN, STEP, NOW, false));
        p.closed();
        c.rollback();
        assertEquals("0", query(c, "select count(*) from schubert.batch_runs"));
      }
    }
  }

  @Test
  void jdbcFailurePositions() throws Exception {
    StringBuilder trace = new StringBuilder();
    assertEquals(
        57, inventory(FIXTURE_EMPTY_E6845188).values().stream().mapToInt(Integer::intValue).sum());
    assertEquals(
        70,
        inventory(FIXTURE_HISTORY_BB36CCAE).values().stream().mapToInt(Integer::intValue).sum());
    assertEquals(
        80,
        inventory(FIXTURE_RECOVER_DE33FD76).values().stream().mapToInt(Integer::intValue).sum());
    assertEquals(
        50, inventory(FIXTURE_FINISH_91A2F12C).values().stream().mapToInt(Integer::intValue).sum());
    assertEquals(
        72, inventory(FIXTURE_REPLAY_2AA31058).values().stream().mapToInt(Integer::intValue).sum());
    try (var c = locked()) {
      for (String path :
          List.of(
              FIXTURE_EMPTY_E6845188,
              FIXTURE_HISTORY_BB36CCAE,
              "skip",
              FIXTURE_RECOVER_DE33FD76,
              FIXTURE_FINISH_91A2F12C,
              FIXTURE_REPLAY_2AA31058)) {
        sql(c, FIXTURE_DELETE_FROM_SCHUBERT_BATCH_RUNS_0A02FC69);
        c.commit();
        BatchStepAttempt handle = null;
        if (Set.of(FIXTURE_HISTORY_BB36CCAE, "skip", FIXTURE_RECOVER_DE33FD76).contains(path)) {
          String status =
              path.equals("skip")
                  ? FIXTURE_SUCCESS_10855C7F
                  : path.equals(FIXTURE_RECOVER_DE33FD76)
                      ? FIXTURE_RUNNING_294BDBF9
                      : FIXTURE_FAILED_7E8A57FE;
          seed(
              c,
              1,
              status,
              RUN.id(),
              FIXTURE_2026_09_13_8B08300C,
              FIXTURE_2026_09_13T01_00_00Z_FE4F9CBB,
              status.equals(FIXTURE_RUNNING_294BDBF9)
                  ? null
                  : FIXTURE_2026_09_13T01_00_01Z_7D588561);
        }
        if (Set.of(FIXTURE_FINISH_91A2F12C, FIXTURE_REPLAY_2AA31058).contains(path)) {
          handle = new BatchRunRepository(c).begin(RUN, STEP, NOW, false);
          if (path.equals(FIXTURE_REPLAY_2AA31058))
            new BatchRunRepository(c).finish(handle, END, SUCCESS);
        }
        c.commit();
        String before = snapshot(c);
        Probe ok = new Probe();
        operate(new BatchRunRepository(ok.wrap(c)), path, handle);
        assertEquals(inventory(path), ok.seen, path);
        int faultCount = 0;
        ok.closed();
        c.rollback();
        for (var entry : inventory(path).entrySet())
          for (int pos = 1; pos <= entry.getValue(); pos++) {
            Probe p = new Probe();
            p.failAt.put(entry.getKey(), pos);
            BatchStepAttempt fixed = handle;
            redacted(() -> operate(new BatchRunRepository(p.wrap(c)), path, fixed));
            assertEquals(1, p.failures, path + "/" + entry + "/" + pos);
            faultCount += p.failures;
            p.closed();
            c.rollback();
            assertEquals(before, snapshot(c));
            assertFalse(c.isClosed());
          }
        Probe both = new Probe();
        both.failAt.put(FIXTURE_ROW_CLOSE_F197F129, 1);
        both.failAt.put(FIXTURE_STATEMENT_CLOSE_FE807BAF, 1);
        BatchStepAttempt fixed = handle;
        redacted(() -> operate(new BatchRunRepository(both.wrap(c)), path, fixed));
        assertEquals(2, both.failures);
        trace
            .append(path)
            .append('=')
            .append(ok.seen.values().stream().mapToInt(Integer::intValue).sum())
            .append('/')
            .append(faultCount)
            .append('/')
            .append(both.failures)
            .append('\n');
        both.closed();
        c.rollback();
        assertEquals(before, snapshot(c));
      }
    }
    trace("PT-BAT-150-jdbc.txt", trace.toString());
  }

  @Test
  void interruptionAndRuntime() throws Exception {
    resourceCompounds();
    assertAll(() -> originalResourceFailure(false), () -> originalResourceFailure(true));
    try (var c = locked()) {
      Probe p = new Probe();
      try {
        Thread.currentThread().interrupt();
        redacted(() -> new BatchRunRepository(p.wrap(c)).begin(RUN, STEP, NOW, false));
        assertTrue(Thread.currentThread().isInterrupted());
        assertTrue(p.seen.isEmpty());
      } finally {
        Thread.interrupted();
      }
      for (String path : List.of(FIXTURE_EMPTY_E6845188, FIXTURE_FINISH_91A2F12C)) {
        sql(c, FIXTURE_DELETE_FROM_SCHUBERT_BATCH_RUNS_0A02FC69);
        BatchStepAttempt a =
            path.equals(FIXTURE_FINISH_91A2F12C)
                ? new BatchRunRepository(c).begin(RUN, STEP, NOW, false)
                : null;
        c.commit();
        Probe last = new Probe();
        last.interruptAt = FIXTURE_STATEMENT_CLOSE_FE807BAF;
        last.interruptPosition = path.equals(FIXTURE_FINISH_91A2F12C) ? 3 : 4;
        try {
          redacted(() -> operate(new BatchRunRepository(last.wrap(c)), path, a));
          assertTrue(Thread.currentThread().isInterrupted());
          last.closed();
        } finally {
          Thread.interrupted();
          c.rollback();
        }
      }
      for (Throwable runtime :
          List.of(
              new IllegalStateException("public-runtime"),
              new NullPointerException("public-null"),
              new AssertionError("public-error"))) {
        Probe fault = new Probe();
        fault.runtime = runtime;
        assertSame(
            runtime,
            assertThrows(
                Throwable.class,
                () -> new BatchRunRepository(fault.wrap(c)).begin(RUN, STEP, NOW, false)));
        fault.closed();
        c.rollback();
      }
      Probe argument = new Probe();
      argument.runtime = new IllegalArgumentException("public-invalid");
      // PG183/SSC063/BUG206: a provider failure is not a malformed projected value.
      assertSame(
          argument.runtime,
          assertThrows(
              Throwable.class,
              () -> new BatchRunRepository(argument.wrap(c)).begin(RUN, STEP, NOW, false)));
      argument.closed();
    }
  }

  private void originalResourceFailure(boolean compound) throws Exception {
    try (var c = locked()) {
      Probe p = new Probe();
      Throwable original =
          compound
              ? new IllegalStateException("public same run fixture")
              : new IllegalArgumentException("public provider fixture");
      p.scopedFaults.put(
          compound ? "history.row.next" : "history.statement.executeQuery", original);
      if (compound) p.scopedFaults.put("history.row.close", original);
      try {
        assertSame(
            original,
            assertThrows(
                Throwable.class,
                () -> new BatchRunRepository(p.wrap(c)).begin(RUN, STEP, NOW, false)));
        assertEquals(compound ? 2 : 1, p.scopedInjected);
        p.closed();
      } finally {
        c.rollback();
      }
    }
  }

  private void resourceCompounds() throws Exception {
    int cases = 0;
    try (var c = locked()) {
      for (String kind :
          List.of(
              FIXTURE_HISTORY_BB36CCAE,
              FIXTURE_INSERT_A0C28A2E,
              FIXTURE_ABANDON_5A676BA9,
              FIXTURE_FINISH_91A2F12C,
              FIXTURE_REPLAY_2AA31058)) {
        sql(c, FIXTURE_DELETE_FROM_SCHUBERT_BATCH_RUNS_0A02FC69);
        c.commit();
        String path =
            kind.equals(FIXTURE_ABANDON_5A676BA9)
                ? FIXTURE_RECOVER_DE33FD76
                : Set.of(FIXTURE_FINISH_91A2F12C, FIXTURE_REPLAY_2AA31058).contains(kind)
                    ? kind
                    : FIXTURE_EMPTY_E6845188;
        BatchStepAttempt handle = null;
        if (kind.equals(FIXTURE_ABANDON_5A676BA9))
          seed(
              c,
              1,
              FIXTURE_RUNNING_294BDBF9,
              RUN.id(),
              FIXTURE_2026_09_13_8B08300C,
              FIXTURE_2026_09_13T01_00_00Z_FE4F9CBB,
              null);
        if (Set.of(FIXTURE_FINISH_91A2F12C, FIXTURE_REPLAY_2AA31058).contains(kind)) {
          handle = new BatchRunRepository(c).begin(RUN, STEP, NOW, false);
          if (kind.equals(FIXTURE_REPLAY_2AA31058))
            new BatchRunRepository(c).finish(handle, END, SUCCESS);
        }
        c.commit();
        String before = snapshot(c);
        c.rollback();
        BatchStepAttempt fixed = handle;
        boolean update = Set.of(FIXTURE_ABANDON_5A676BA9, FIXTURE_FINISH_91A2F12C).contains(kind);
        int stageCases = 0;
        for (var sample : JdbcResourceCases.all()) {
          if (update && sample.body().startsWith("row.")) continue;
          String body = update ? "statement.executeUpdate" : sample.body();
          Probe p = new Probe();
          if (sample.primary() != null) p.scopedFaults.put(kind + "." + body, sample.primary());
          p.scopedFaults.put(kind + "." + sample.close(), sample.secondary());
          sample.verify(
              assertThrows(
                  Throwable.class, () -> operate(new BatchRunRepository(p.wrap(c)), path, fixed)));
          assertEquals(sample.primary() == null ? 1 : 2, p.scopedInjected);
          assertEquals(1, p.scopedSeen.get(kind + ".statement.close"));
          assertEquals(
              update
                      || (body.equals(FIXTURE_STATEMENT_EXECUTEQUERY_67733F33)
                          && sample.primary() != null)
                  ? 0
                  : 1,
              p.scopedSeen.getOrDefault(kind + ".row.close", 0));
          p.closed();
          for (String key :
              List.of(
                  "connection.commit",
                  "connection.rollback",
                  "connection.close",
                  "connection.setAutoCommit")) assertFalse(p.seen.containsKey(key));
          assertFalse(c.getAutoCommit());
          c.rollback();
          assertEquals(before, snapshot(c));
          c.rollback();
          stageCases++;
          cases++;
        }
        assertEquals(update ? 34 : 68, stageCases);
        if (update) {
          Probe absent = new Probe();
          absent.kind = kind;
          absent.anomaly = FIXTURE_NULLSTATEMENT_5A17BE38;
          redacted(() -> operate(new BatchRunRepository(absent.wrap(c)), path, fixed));
          assertEquals(0, absent.scopedSeen.getOrDefault(kind + ".statement.close", 0));
          absent.closed();
          c.rollback();
          assertEquals(before, snapshot(c));
          c.rollback();
        }
      }
    }
    assertEquals(272, cases);
  }

  @Test
  void concurrentOwnersAndRowLocks() throws Exception {
    try (var owner = locked();
        var other = db.open(FIXTURE_SCHUBERT_BATCH_F9C88479);
        var pool = Executors.newVirtualThreadPerTaskExecutor()) {
      other.setAutoCommit(false);
      assertEquals("false", query(other, "select pg_try_advisory_lock(71419602)::text"));
      other.rollback();
      var repo = new BatchRunRepository(owner);
      var a = repo.begin(RUN, STEP, NOW, false);
      assertEquals("0", query(other, "select count(*) from schubert.batch_runs"));
      other.rollback();
      repo.finish(a, END, SUCCESS);
      owner.commit();
      // Existing row lock blocks a competing UPDATE; server returns 55P03 using fixed lock_timeout.
      repo.begin(RUN, STEP, END.plusSeconds(1), false);
      var blocked =
          pool.submit(
              () -> {
                sql(other, "set local lock_timeout='100ms'");
                var e =
                    assertThrows(
                        SQLException.class,
                        () ->
                            sql(
                                other,
                                "update schubert.batch_runs set byte_count=7 where id=" + a.id()));
                assertEquals("55P03", e.getSQLState());
                other.rollback();
                return true;
              });
      assertTrue(blocked.get(5, TimeUnit.SECONDS));
      owner.commit();
      sql(owner, "select pg_advisory_unlock(71419602)");
      owner.commit();
      assertEquals("true", query(other, "select pg_try_advisory_lock(71419602)::text"));
      other.commit();
      var after = new BatchRunRepository(other).begin(RUN, STEP, END.plusSeconds(2), false);
      assertEquals(3, after.attempt());
      assertTrue(after.skipped());
      other.commit();
      assertEquals(
          "1,2,3",
          query(
              other,
              "select string_agg(attempt::text,',' order by attempt) from schubert.batch_runs"));
    }
  }

  @Test
  void independentSqlInventoryAndGrants() throws Exception {
    try (var c = locked();
        var admin = db.admin()) {
      assertEquals(
          "28",
          query(
              admin,
              "select count(*) from schubert_meta.flyway_schema_history where success and version is not null and type='SQL'"));
      assertEquals(
          "1",
          query(
              admin,
              "select count(*) from schubert_meta.flyway_schema_history where success and type='SCHEMA' and version is null"));
      assertEquals(
          "true|true|true|false",
          query(
              admin,
              "select has_table_privilege('schubert_batch','schubert.batch_runs','SELECT')||'|'||has_table_privilege('schubert_batch','schubert.batch_runs','INSERT')||'|'||has_table_privilege('schubert_batch','schubert.batch_runs','UPDATE')||'|'||has_table_privilege('schubert_batch','schubert.questions','SELECT')"));
      seed(
          c,
          1,
          FIXTURE_FAILED_7E8A57FE,
          RUN.id(),
          FIXTURE_2026_09_13_8B08300C,
          FIXTURE_2026_09_13T01_00_00Z_FE4F9CBB,
          FIXTURE_2026_09_13T01_00_01Z_7D588561);
      sql(c, "update schubert.batch_runs set error_summary='public historical diagnostic'");
      c.commit();
      Probe p = new Probe();
      var repo = new BatchRunRepository(p.wrap(c));
      var a = repo.begin(RUN, STEP, NOW, false);
      repo.finish(a, END, SUCCESS);
      repo.finish(a, END, SUCCESS);
      p.closed();
      assertEquals(
          Set.of(
              "refs",
              FIXTURE_HISTORY_BB36CCAE,
              FIXTURE_INSERT_A0C28A2E,
              FIXTURE_FINISH_91A2F12C,
              FIXTURE_REPLAY_2AA31058),
          p.kinds);
      assertEquals(
          "public historical diagnostic",
          query(c, "select error_summary from schubert.batch_runs where attempt=1"));
      assertFalse(p.projected.contains("error_code"));
      assertFalse(p.projected.contains("error_summary"));
      assertTrue(p.projected.containsAll(COLS));
    }
    Path repo = Path.of(System.getProperty("nk.pt.repository"));
    String source =
        Files.readString(
            repo.resolve(
                "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/BatchRunRepository.java"));
    assertFalse(source.contains("DriverManager"));
    assertFalse(source.contains(".commit("));
    assertFalse(source.contains(".rollback("));
    assertFalse(source.contains("getTimestamp"));
    assertFalse(source.contains("setTimestamp"));
  }

  static Map<String, Integer> inventory(String path) {
    Map<String, Integer> m = new TreeMap<>();
    // Independently specified in 023 before source: two reference reads = 32.
    for (var e :
        Map.ofEntries(
                Map.entry("connection.getAutoCommit", 2),
                Map.entry("connection.isReadOnly", 2),
                Map.entry("connection.getTransactionIsolation", 2),
                Map.entry("connection.prepareStatement", 2),
                Map.entry("statement.setQueryTimeout", 2),
                Map.entry("statement.setObject", 4),
                Map.entry(FIXTURE_STATEMENT_EXECUTEQUERY_67733F33, 2),
                Map.entry(FIXTURE_STATEMENT_CLOSE_FE807BAF, 2),
                Map.entry("row.next", 4),
                Map.entry("row.getObject", 8),
                Map.entry(FIXTURE_ROW_CLOSE_F197F129, 2))
            .entrySet()) m.put(e.getKey(), e.getValue());
    if (path.equals(FIXTURE_FINISH_91A2F12C) || path.equals(FIXTURE_REPLAY_2AA31058)) {
      add(m, "connection.prepareStatement", 1);
      add(m, "statement.setQueryTimeout", 1);
      add(m, "statement.setObject", 4);
      add(m, "statement.setString", 4);
      add(m, "statement.setLong", 5);
      add(m, "statement.setInt", 1);
      add(m, "statement.executeUpdate", 1);
      add(m, FIXTURE_STATEMENT_CLOSE_FE807BAF, 1);
      if (path.equals(FIXTURE_REPLAY_2AA31058)) {
        add(m, "connection.prepareStatement", 1);
        add(m, "statement.setQueryTimeout", 1);
        add(m, "statement.setObject", 4);
        add(m, "statement.setString", 4);
        add(m, "statement.setLong", 5);
        add(m, "statement.setInt", 1);
        add(m, FIXTURE_STATEMENT_EXECUTEQUERY_67733F33, 1);
        add(m, FIXTURE_STATEMENT_CLOSE_FE807BAF, 1);
        add(m, "row.next", 2);
        add(m, "row.getObject", 1);
        add(m, FIXTURE_ROW_CLOSE_F197F129, 1);
      }
    } else {
      add(m, "connection.prepareStatement", 2);
      add(m, "statement.setQueryTimeout", 2);
      add(m, "statement.setObject", 5);
      add(m, "statement.setString", 5);
      add(m, "statement.setInt", 1);
      add(m, FIXTURE_STATEMENT_EXECUTEQUERY_67733F33, 2);
      add(m, FIXTURE_STATEMENT_CLOSE_FE807BAF, 2);
      add(m, "row.next", 3);
      add(m, "row.getObject", 1);
      add(m, FIXTURE_ROW_CLOSE_F197F129, 2);
      if (!path.equals(FIXTURE_EMPTY_E6845188)) {
        add(m, "row.next", 1);
        add(m, "row.getObject", 10);
        add(m, "row.getString", 2);
      }
      if (path.equals(FIXTURE_RECOVER_DE33FD76)) {
        add(m, "connection.prepareStatement", 1);
        add(m, "statement.setQueryTimeout", 1);
        add(m, "statement.setObject", 3);
        add(m, "statement.setString", 2);
        add(m, "statement.setLong", 1);
        add(m, "statement.executeUpdate", 1);
        add(m, FIXTURE_STATEMENT_CLOSE_FE807BAF, 1);
      }
    }
    return m;
  }

  static void trace(String name, String value) throws Exception {
    Path dir = Path.of("target/batch-step-traces");
    Files.createDirectories(dir);
    Files.writeString(dir.resolve(name), value);
  }

  static void add(Map<String, Integer> m, String key, int n) {
    m.merge(key, n, Integer::sum);
  }

  static void operate(BatchRunRepository repo, String path, BatchStepAttempt a) {
    if (path.equals(FIXTURE_FINISH_91A2F12C) || path.equals(FIXTURE_REPLAY_2AA31058))
      repo.finish(Objects.requireNonNull(a), END, SUCCESS);
    else repo.begin(RUN, STEP, NOW, path.equals(FIXTURE_RECOVER_DE33FD76));
  }

  static Connection locked() throws SQLException {
    var c = db.open(FIXTURE_SCHUBERT_BATCH_F9C88479);
    sql(c, "set timezone='UTC'");
    sql(c, "select pg_advisory_lock(71419602)");
    c.setAutoCommit(false);
    return c;
  }

  static void seed(
      Connection c, int attempt, String status, UUID run, String day, String start, String end)
      throws SQLException {
    sql(
        c,
        "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count) values('"
            + run
            + "','"
            + day
            + "','CLEAN_LOG',"
            + attempt
            + ",'"
            + start
            + "',"
            + (end == null ? "null" : "'" + end + "'")
            + ",'"
            + status
            + "',9,3,2,8)");
  }

  static void sql(Connection c, String text) throws SQLException {
    try (var s = c.createStatement()) {
      s.execute(text);
    }
  }

  static String query(Connection c, String text) throws SQLException {
    try (var s = c.createStatement();
        var r = s.executeQuery(text)) {
      assertTrue(r.next());
      String v = r.getString(1);
      assertFalse(r.next());
      return v;
    }
  }

  static String terminal(Connection c, long id) throws SQLException {
    return query(
        c,
        "select status||'|'||target_count||'|'||success_count||'|'||failure_count||'|'||byte_count||'|'||coalesce(error_code,'NULL')||'|'||coalesce(error_summary,'NULL') from schubert.batch_runs where id="
            + id);
  }

  static String snapshot(Connection c) throws SQLException {
    return query(
        c,
        "select coalesce(string_agg(row_to_json(b)::text,';' order by id),'EMPTY') from schubert.batch_runs b");
  }

  static void redacted(Runnable r) {
    var e = assertThrows(BatchRepositoryException.class, r::run);
    assertEquals("batch repository operation failed", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }

  static final class Probe {
    final Map<String, Integer> seen = new TreeMap<>();
    final Map<String, Integer> failAt = new HashMap<>();
    final Map<String, Integer> scopedSeen = new TreeMap<>();
    final Map<String, Throwable> scopedFaults = new HashMap<>();
    int scopedInjected;
    final Set<String> kinds = new HashSet<>();
    final Set<String> projected = new HashSet<>();
    String kind = "";
    String anomaly = "";
    String changeKind = "";
    String interruptAt = "";
    int changed;
    int interruptPosition;
    int failures;
    int statements;
    int rows;
    Throwable runtime;

    void hit(String key) throws SQLException {
      int n = seen.merge(key, 1, Integer::sum);
      if (key.equals(interruptAt) && n == interruptPosition) Thread.currentThread().interrupt();
      if (Objects.equals(failAt.get(key), n)) {
        failures++;
        throw new SQLException("public provider fixture", "08006");
      }
    }

    void scopedHit(String kind, String key) throws Throwable {
      String scoped = kind + "." + key;
      int n = scopedSeen.merge(scoped, 1, Integer::sum);
      if (n == 1 && scopedFaults.containsKey(scoped)) {
        scopedInjected++;
        throw scopedFaults.get(scoped);
      }
    }

    Connection wrap(Connection c) {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (p, m, a) -> {
                hit("connection." + m.getName());
                if (m.getName().equals("prepareStatement")) {
                  String sql = (String) a[0];
                  String k = classify(sql);
                  kinds.add(k);
                  if (k.equals(kind) && anomaly.equals(FIXTURE_NULLSTATEMENT_5A17BE38)) return null;
                  var s = (PreparedStatement) invoke(c, m, a);
                  statements++;
                  return statement(s, k);
                }
                assertTrue(
                    Set.of("getAutoCommit", "isReadOnly", "getTransactionIsolation")
                        .contains(m.getName()),
                    "borrowed configuration changed: " + m.getName());
                return invoke(c, m, a);
              });
    }

    PreparedStatement statement(PreparedStatement s, String k) {
      Map<Integer, Object> binds = new TreeMap<>();
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (p, m, a) -> {
                String name = m.getName();
                if (name.equals("close")) {
                  Object v = invoke(s, m, a);
                  statements--;
                  hit(FIXTURE_STATEMENT_CLOSE_FE807BAF);
                  scopedHit(k, FIXTURE_STATEMENT_CLOSE_FE807BAF);
                  return v;
                }
                hit("statement." + name);
                scopedHit(k, "statement." + name);
                if (name.equals("setQueryTimeout")) assertEquals(5, a[0]);
                if (Set.of("setObject", "setString", "setInt", "setLong").contains(name)) {
                  binds.put((Integer) a[0], a[1]);
                  if (name.equals("setObject") && a[1] instanceof OffsetDateTime time)
                    assertEquals(ZoneOffset.UTC, time.getOffset());
                }
                if (name.equals("executeQuery") || name.equals("executeUpdate")) {
                  if (runtime != null) throw runtime;
                  assertBinds(k, binds);
                  if (k.equals(kind) && anomaly.equals(FIXTURE_NULLROWS_D5C4412B)) return null;
                  Object v = invoke(s, m, a);
                  if (name.equals("executeUpdate")) return k.equals(changeKind) ? changed : v;
                  rows++;
                  return row((ResultSet) v, k);
                }
                return invoke(s, m, a);
              });
    }

    ResultSet row(ResultSet r, String k) {
      int[] pos = {0};
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (p, m, a) -> {
                String name = m.getName();
                if (name.equals("close")) {
                  Object v = invoke(r, m, a);
                  rows--;
                  hit(FIXTURE_ROW_CLOSE_F197F129);
                  scopedHit(k, FIXTURE_ROW_CLOSE_F197F129);
                  return v;
                }
                hit("row." + name);
                scopedHit(k, "row." + name);
                boolean broken = k.equals(kind);
                if (name.equals("next")) {
                  pos[0]++;
                  if (broken && anomaly.equals(FIXTURE_EMPTY_E6845188)) return false;
                  if (broken
                      && Set.of("extra", "duplicateId", "duplicateAttempt", "doubleSuccess")
                          .contains(anomaly)
                      && pos[0] == 2) return true;
                  if (broken && anomaly.equals("tooMany")) return pos[0] <= 100;
                }
                if (name.equals("getObject") || name.equals("getString")) {
                  String col = (String) a[0];
                  projected.add(col);
                  if (broken) {
                    if (anomaly.equals(col)) return null;
                    if (anomaly.equals("tooMany")) return synthetic(col, pos[0]);
                    if (anomaly.equals("duplicateId")) {
                      if (col.equals(FIXTURE_ATTEMPT_7FD8A755)) return pos[0];
                      return synthetic(col, 1);
                    }
                    if (anomaly.equals("duplicateAttempt") && pos[0] == 2) {
                      if (col.equals(FIXTURE_ATTEMPT_7FD8A755)) return 1;
                      return synthetic(col, 2);
                    }
                    if (anomaly.equals("doubleSuccess")) {
                      if (col.equals(FIXTURE_STATUS_CFC31BCC)) return FIXTURE_SUCCESS_10855C7F;
                      return synthetic(col, pos[0]);
                    }
                    Object override = override(col, anomaly);
                    if (override != NO_OVERRIDE) return override;
                  }
                }
                return invoke(r, m, a);
              });
    }

    static final Object NO_OVERRIDE = new Object();

    static Object override(String col, String anomaly) {
      if (col.equals("id")) {
        if (anomaly.equals("badIdLow")) return 0L;
        if (anomaly.equals("badIdHigh")) return 1000000000000L;
      }
      if (col.equals("business_date") && anomaly.equals("badDate"))
        return LocalDate.of(2026, 9, 14);
      if (col.equals("step") && anomaly.equals("badStep")) return "CLEAN_SESSION";
      if (col.equals(FIXTURE_ATTEMPT_7FD8A755)) {
        if (anomaly.equals("badAttemptLow")) return 0;
        if (anomaly.equals("badAttemptHigh")) return 100;
      }
      if (col.equals(FIXTURE_STATUS_CFC31BCC)) {
        if (anomaly.equals("unknown")) return "UNKNOWN";
        if (anomaly.equals("runningEnd")) return FIXTURE_RUNNING_294BDBF9;
      }
      if (col.equals("target_count") && anomaly.equals("negativeTarget")) return -1L;
      if (col.equals("success_count") && anomaly.equals("negativeSuccess")) return -1L;
      if (col.equals("failure_count") && anomaly.equals("negativeFailure")) return -1L;
      if (col.equals("byte_count") && anomaly.equals("negativeBytes")) return -1L;
      if (col.equals("started_at")) {
        if (anomaly.equals("earlyStart"))
          return OffsetDateTime.parse("2026-09-12T14:59:59.999999Z");
        if (anomaly.equals("oldStart")) return OffsetDateTime.parse("0000-12-31T23:59:59Z");
        if (anomaly.equals("fineStart"))
          return OffsetDateTime.parse("2026-09-13T01:00:00.000000001Z");
        if (anomaly.equals("futureStart")) return OffsetDateTime.parse("2026-09-13T02:00:01Z");
      }
      if (col.equals("ended_at")) {
        if (anomaly.equals("earlyEnd")) return OffsetDateTime.parse("2026-09-13T00:59:59.999999Z");
        if (anomaly.equals("oldEnd")) return OffsetDateTime.parse("0000-12-31T23:59:59Z");
        if (anomaly.equals("fineEnd"))
          return OffsetDateTime.parse("2026-09-13T01:00:01.000000001Z");
        if (anomaly.equals("futureEnd")) return OffsetDateTime.parse("2026-09-13T02:00:01Z");
      }
      return NO_OVERRIDE;
    }

    static Object synthetic(String col, int n) {
      return switch (col) {
        case "id" -> (long) n;
        case "run_id" -> RUN.id();
        case "business_date" -> LocalDate.of(2026, 9, 13);
        case "step" -> "CLEAN_LOG";
        case FIXTURE_ATTEMPT_7FD8A755 -> n;
        case "started_at" -> OffsetDateTime.parse(FIXTURE_2026_09_13T01_00_00Z_FE4F9CBB);
        case "ended_at" -> OffsetDateTime.parse(FIXTURE_2026_09_13T01_00_01Z_7D588561);
        case FIXTURE_STATUS_CFC31BCC -> FIXTURE_FAILED_7E8A57FE;
        case "target_count", "success_count", "failure_count", "byte_count" -> 0L;
        default -> throw new AssertionError(col);
      };
    }

    static String classify(String sql) {
      String handle =
          "id=? and run_id=? and business_date=? and step=? and attempt=? and started_at=?";
      Map<String, String> allowed =
          Map.of(
              "refs",
              "select has_batch_history,has_inbox_progress,has_log_progress,identity_consistent from schubert.maintenance_read_run_references(?,?)",
              FIXTURE_HISTORY_BB36CCAE,
              "select id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count from schubert.batch_runs where business_date=? and step=? order by attempt limit 100 for update",
              FIXTURE_INSERT_A0C28A2E,
              "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary) values(?,?,?,?,?,?,?,0,0,0,0,?,?) returning id",
              FIXTURE_ABANDON_5A676BA9,
              "update schubert.batch_runs set status='FAILED',ended_at=?,error_code=?,error_summary=? where id=? and run_id=? and started_at=? and status='RUNNING' and ended_at is null",
              FIXTURE_FINISH_91A2F12C,
              "update schubert.batch_runs set ended_at=?,status=?,target_count=?,success_count=?,failure_count=?,byte_count=?,error_code=?,error_summary=? where "
                  + handle
                  + " and status='RUNNING' and ended_at is null",
              FIXTURE_REPLAY_2AA31058,
              "select exists(select 1 from schubert.batch_runs where ended_at=? and status=? and target_count=? and success_count=? and failure_count=? and byte_count=? and error_code is not distinct from ? and error_summary is not distinct from ? and "
                  + handle
                  + ") as matches");
      return allowed.entrySet().stream()
          .filter(e -> e.getValue().equals(sql))
          .map(Map.Entry::getKey)
          .findFirst()
          .orElseThrow(() -> new AssertionError("SQL outside fixed inventory"));
    }

    static void assertBinds(String k, Map<Integer, Object> b) {
      int count =
          switch (k) {
            case "refs", FIXTURE_HISTORY_BB36CCAE -> 2;
            case FIXTURE_INSERT_A0C28A2E -> 9;
            case FIXTURE_ABANDON_5A676BA9 -> 6;
            default -> 14;
          };
      assertEquals(count, b.size());
      for (int i = 1; i <= count; i++) assertTrue(b.containsKey(i));
      if (k.equals("refs")) {
        assertEquals(RUN.id(), b.get(1));
        assertEquals(OffsetDateTime.parse("2026-09-12T15:00:00Z"), b.get(2));
      }
      if (k.equals(FIXTURE_HISTORY_BB36CCAE)) {
        assertEquals(LocalDate.of(2026, 9, 13), b.get(1));
        assertEquals("CLEAN_LOG", b.get(2));
      }
      if (k.equals(FIXTURE_INSERT_A0C28A2E)) {
        assertEquals(RUN.id(), b.get(1));
        assertEquals(LocalDate.of(2026, 9, 13), b.get(2));
        assertEquals("CLEAN_LOG", b.get(3));
      }
      if (k.equals(FIXTURE_ABANDON_5A676BA9)) {
        assertEquals("ABANDONED", b.get(2));
        assertEquals("previous same-run attempt abandoned", b.get(3));
      }
      if (k.equals(FIXTURE_FINISH_91A2F12C) || k.equals(FIXTURE_REPLAY_2AA31058)) {
        assertEquals(OffsetDateTime.parse("2026-09-13T02:00:01Z"), b.get(1));
        assertEquals(FIXTURE_SUCCESS_10855C7F, b.get(2));
        assertEquals(5L, b.get(3));
        assertEquals(3L, b.get(4));
        assertEquals(0L, b.get(5));
        assertEquals(9L, b.get(6));
        assertNull(b.get(7));
        assertNull(b.get(8));
      }
    }

    void closed() {
      assertEquals(0, statements);
      assertEquals(0, rows);
    }

    static Object invoke(Object target, Method m, Object[] a) throws Throwable {
      try {
        return m.invoke(target, a);
      } catch (InvocationTargetException e) {
        throw e.getCause();
      }
    }
  }
}
