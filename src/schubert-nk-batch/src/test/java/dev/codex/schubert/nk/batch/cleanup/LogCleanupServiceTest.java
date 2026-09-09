package dev.codex.schubert.nk.batch.cleanup;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.batch.repository.*;
import java.nio.file.Path;
import java.sql.*;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.LongSupplier;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.io.TempDir;

/** NK-BAT-001; UI251/SS341/SSC-051; PG-D-138; PT-BAT-018..029. */
final class LogCleanupServiceTest {
  @TempDir static Path root;
  private static BatchDatabaseFixture db;
  private static final BatchRun RUN =
      new BatchRun(new UUID(0, 94), Instant.parse("2026-09-17T00:00:00Z"));
  private static final CleanupCounts ZERO = new CleanupCounts(0, 0, 0);
  private static final long LIMIT = 1_800_000_000_000L;

  @BeforeAll
  static void start() throws Exception {
    db = new BatchDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = db.admin()) {
      sql(c, "delete from schubert.log_cleanup_progress");
      sql(c, "delete from schubert.app_logs");
      sql(c, "delete from schubert.batch_runs");
      for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG"))
        sql(
            c,
            "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status) values('"
                + RUN.id()
                + "','2026-09-17','"
                + step
                + "',1,'2026-09-17 00:00:00+00','2026-09-17 00:00:00+00','SUCCESS')");
    }
  }

  @Test
  void emptyAndCompletedRuns() throws Exception {
    try (var c = batch()) {
      var summary = new LogCleanupService().execute(c, RUN);
      assertEquals(ZERO, summary.before());
      assertEquals(ZERO, summary.attemptCounts());
      assertEquals(0, summary.exitCode());
      assertEquals(RUN, summary.run());
      assertTrue(summary.after().complete());
      assertTrue(c.getAutoCommit());
      assertFalse(c.isClosed());
      assertEquals(summary, new LogCleanupService(() -> 0).execute(c, RUN));
    }
    assertEquals("0|0|0|true", progress());
  }

  @Test
  void heldPrefixAndLargeChunks() throws Exception {
    logs(10000, 1);
    try (var c = batch()) {
      var probe = new ServiceJdbcProbe();
      var summary = new LogCleanupService(() -> 0).execute(probe.wrap(c), RUN);
      assertEquals(new CleanupCounts(10001, 1, 10000), summary.after().counts());
      assertEquals(new CleanupCounts(10001, 1, 10000), summary.attemptCounts());
      assertEquals(10, summary.exitCode());
      assertEquals(3, probe.commits);
      assertEquals(0, probe.rollbacks);
      assertEquals(0, probe.closes);
    }
    assertEquals("10000", countLogs());
    assertEquals("10001|1|10000|true", progress());
  }

  @Test
  void resumedAttemptCounts() throws Exception {
    logs(2, 1);
    try (var c = batch()) {
      c.setAutoCommit(false);
      assertEquals(
          new CleanupCounts(2, 0, 2),
          new CleanupRepository(c).execute(RUN, CleanupKind.LOGS, 2).counts());
      c.commit();
      c.setAutoCommit(true);
      var summary = new LogCleanupService(() -> 0).execute(c, RUN);
      assertEquals(new CleanupCounts(2, 0, 2), summary.before());
      assertEquals(new CleanupCounts(1, 1, 0), summary.attemptCounts());
      assertEquals(new CleanupCounts(3, 1, 2), summary.after().counts());
      assertEquals(10, summary.exitCode());
      var replay = new LogCleanupService(() -> 0).execute(c, RUN);
      assertEquals(ZERO, replay.attemptCounts());
      assertEquals(10, replay.exitCode());
    }
  }

  @Test
  void sessionLockOwnership() throws Exception {
    try (var parent = batch();
        var other = db.admin()) {
      assertEquals("true", scalar(parent, "select pg_try_advisory_lock(71419602)::text"));
      assertEquals(0, new LogCleanupService(() -> 0).execute(parent, RUN).exitCode());
      assertEquals("false", scalar(other, "select pg_try_advisory_lock(71419602)::text"));
      assertEquals("true", scalar(parent, "select pg_advisory_unlock(71419602)::text"));
      assertEquals("true", scalar(other, "select pg_try_advisory_lock(71419602)::text"));
      stopped(
          CleanupStopReason.LOCK_BUSY, () -> new LogCleanupService(() -> 0).execute(parent, RUN));
      assertEquals("true", scalar(other, "select pg_advisory_unlock(71419602)::text"));
      assertEquals(0, new LogCleanupService(() -> 0).execute(parent, RUN).exitCode());
      assertEquals("true", scalar(other, "select pg_try_advisory_lock(71419602)::text"));
      assertEquals("true", scalar(other, "select pg_advisory_unlock(71419602)::text"));
    }
  }

  @Test
  void backupAndRowLockStop() throws Exception {
    logs(2, 1);
    try (var c = batch();
        var admin = db.admin()) {
      sql(admin, "update schubert.batch_runs set status='FAILED' where step='BACKUP_CONFIG'");
      stopped(CleanupStopReason.BACKUP_GATE, () -> new LogCleanupService(() -> 0).execute(c, RUN));
      assertEquals("3", countLogs());
      assertTrue(c.getAutoCommit());
      sql(admin, "delete from schubert.batch_runs where step='BACKUP_CONFIG'");
      stopped(CleanupStopReason.BACKUP_GATE, () -> new LogCleanupService(() -> 0).execute(c, RUN));
      assertEquals("3", countLogs());
      sql(
          admin,
          "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status) select run_id,business_date,'BACKUP_CONFIG',attempt,started_at,ended_at,status from schubert.batch_runs where step='BACKUP_DB'");
      sql(admin, "update schubert.batch_runs set status='SUCCESS'");
      admin.setAutoCommit(false);
      assertEquals("1", scalar(admin, "select id from schubert.app_logs where id=1 for update"));
      stopped(CleanupStopReason.LOCK_BUSY, () -> new LogCleanupService(() -> 0).execute(c, RUN));
      admin.rollback();
      var probe = new ServiceJdbcProbe();
      probe.afterCommit =
          count -> {
            if (count == 1)
              try (var changed = db.admin()) {
                sql(
                    changed,
                    "update schubert.batch_runs set status='FAILED' where step='BACKUP_CONFIG'");
              }
          };
      stopped(
          CleanupStopReason.BACKUP_GATE,
          () -> new LogCleanupService(() -> 0).execute(probe.wrap(c), RUN));
      assertEquals("3|1|2|false", progress());
      assertEquals(1, probe.commits);
    }
  }

  @Test
  void timeBoundaryAndClockWrap() throws Exception {
    for (long[] times :
        List.of(
            new long[] {0, LIMIT},
            new long[] {0, LIMIT + 1},
            new long[] {10, 9},
            new long[] {0, 0, LIMIT})) {
      try (var c = batch()) {
        stopped(
            CleanupStopReason.TIME_LIMIT,
            () -> new LogCleanupService(clock(times)).execute(c, RUN));
      }
    }
    for (long[] times :
        List.of(new long[] {0, LIMIT - 1}, new long[] {Long.MAX_VALUE - 2, Long.MIN_VALUE + 2})) {
      try (var c = batch()) {
        assertEquals(0, new LogCleanupService(clock(times)).execute(c, RUN).exitCode());
      }
    }
    reset();
    logs(2, 1);
    try (var c = batch()) {
      stopped(
          CleanupStopReason.TIME_LIMIT,
          () -> new LogCleanupService(clock(0, 0, 0, LIMIT)).execute(c, RUN));
    }
    assertEquals("3|1|2|false", progress());
  }

  @Test
  void interruptsRemainSet() throws Exception {
    try (var c = batch()) {
      var probe = new ServiceJdbcProbe();
      Thread.currentThread().interrupt();
      try {
        stopped(
            CleanupStopReason.INTERRUPTED,
            () -> new LogCleanupService(() -> 0).execute(probe.wrap(c), RUN));
        assertTrue(Thread.currentThread().isInterrupted());
        assertEquals(0, probe.prepared);
      } finally {
        Thread.interrupted();
      }
    }
    logs(0, 1);
    try (var c = batch()) {
      var probe = new ServiceJdbcProbe();
      probe.afterCommit = count -> Thread.currentThread().interrupt();
      try {
        stopped(
            CleanupStopReason.INTERRUPTED,
            () -> new LogCleanupService(() -> 0).execute(probe.wrap(c), RUN));
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
    }
    assertEquals("1|1|0|false", progress());
    try (var c = batch()) {
      assertEquals(ZERO, new LogCleanupService(() -> 0).execute(c, RUN).attemptCounts());
    }
  }

  @Test
  void rollbackAndUncertainCommit() throws Exception {
    logs(0, 1);
    for (String fault : List.of("cleanup.executeQuery", "commitBefore")) {
      var probe = new ServiceJdbcProbe();
      probe.failAt.put(fault, 1);
      try (var c = batch()) {
        stopped(
            CleanupStopReason.DATABASE_FAILURE,
            () -> new LogCleanupService(() -> 0).execute(probe.wrap(c), RUN));
        assertEquals(1, probe.rollbacks);
        assertTrue(c.getAutoCommit());
      }
      assertEquals("1", countLogs());
    }
    var uncertain = new ServiceJdbcProbe();
    uncertain.failAt.put("commitAfter", 1);
    try (var c = batch()) {
      stopped(
          CleanupStopReason.DATABASE_FAILURE,
          () -> new LogCleanupService(() -> 0).execute(uncertain.wrap(c), RUN));
    }
    assertEquals(1, uncertain.commits);
    assertEquals("0", countLogs());
    assertEquals("1|1|0|false", progress());
    try (var c = batch()) {
      var resumed = new LogCleanupService(() -> 0).execute(c, RUN);
      assertEquals(new CleanupCounts(1, 1, 0), resumed.before());
      assertEquals(ZERO, resumed.attemptCounts());
      assertTrue(resumed.after().complete());
    }
  }

  @Test
  void restorationAndUnlockFailures() throws Exception {
    for (String fault :
        List.of(
            "restore",
            "unlock.prepareStatement",
            "unlock.executeQuery",
            "unlock.next",
            "unlock.getObject",
            "unlock.resultClose",
            "unlock.statementClose")) {
      var probe = new ServiceJdbcProbe();
      probe.failAt.put(fault, 1);
      try (var c = batch()) {
        stopped(
            CleanupStopReason.DATABASE_FAILURE,
            () -> new LogCleanupService(() -> 0).execute(probe.wrap(c), RUN));
        assertEquals(1, probe.failures);
      }
    }
    var closeCheck = new ServiceJdbcProbe();
    closeCheck.failAt.put("getAutoCommit", 4);
    try (var c = batch()) {
      stopped(
          CleanupStopReason.DATABASE_FAILURE,
          () -> new LogCleanupService(() -> 0).execute(closeCheck.wrap(c), RUN));
      assertEquals(1, closeCheck.failures);
    }
    reset();
    logs(0, 1);
    var rollback = new ServiceJdbcProbe();
    rollback.failAt.put("commitBefore", 1);
    rollback.failAt.put("rollback", 1);
    try (var c = batch()) {
      stopped(
          CleanupStopReason.DATABASE_FAILURE,
          () -> new LogCleanupService(() -> 0).execute(rollback.wrap(c), RUN));
      assertEquals(0, rollback.restores);
      assertFalse(c.getAutoCommit());
      assertEquals(2, rollback.failures);
    }
    assertEquals("1", countLogs());
    var restoreAfterRollback = new ServiceJdbcProbe();
    restoreAfterRollback.failAt.put("commitBefore", 1);
    restoreAfterRollback.failAt.put("restore", 1);
    try (var c = batch()) {
      stopped(
          CleanupStopReason.DATABASE_FAILURE,
          () -> new LogCleanupService(() -> 0).execute(restoreAfterRollback.wrap(c), RUN));
      assertEquals(1, restoreAfterRollback.rollbacks);
      assertEquals(2, restoreAfterRollback.failures);
    }
    assertEquals("1", countLogs());
  }

  @Test
  void invalidInputsAndProjections() throws Exception {
    assertThrows(NullPointerException.class, () -> new LogCleanupService(null));
    assertThrows(NullPointerException.class, () -> new LogCleanupService().execute(null, RUN));
    try (var c = batch()) {
      assertThrows(NullPointerException.class, () -> new LogCleanupService().execute(c, null));
      c.setAutoCommit(false);
      assertThrows(IllegalArgumentException.class, () -> new LogCleanupService().execute(c, RUN));
      c.rollback();
    }
    for (String stage : List.of("lock", "unlock")) {
      for (String kind : List.of("null", "false", "empty", "duplicate")) {
        var probe = new ServiceJdbcProbe();
        if (kind.equals("empty")) probe.empty.add(stage);
        else if (kind.equals("duplicate")) probe.duplicate.add(stage);
        else
          probe.columns.put(
              stage + "." + (stage.equals("lock") ? "held" : "released"),
              kind.equals("null") ? null : false);
        try (var c = batch()) {
          stopped(
              stage.equals("lock") && kind.equals("false")
                  ? CleanupStopReason.LOCK_BUSY
                  : CleanupStopReason.DATABASE_FAILURE,
              () -> new LogCleanupService(() -> 0).execute(probe.wrap(c), RUN));
        }
      }
    }
    reset();
    logs(0, 1);
    var inconsistent = new ServiceJdbcProbe();
    inconsistent.columns.put("progress.target_count", 0L);
    inconsistent.columns.put("progress.deleted_count", 0L);
    try (var c = batch()) {
      stopped(
          CleanupStopReason.DATABASE_FAILURE,
          () -> new LogCleanupService(() -> 0).execute(inconsistent.wrap(c), RUN));
    }
    assertEquals("1", countLogs());
  }

  @Test
  void summaryInvariants() {
    var end = new LogCleanupProgress(RUN, new CleanupCounts(10, 5, 5), true);
    var valid = new LogCleanupSummary(RUN, new CleanupCounts(3, 1, 2), end);
    assertEquals(new CleanupCounts(7, 4, 3), valid.attemptCounts());
    assertEquals(10, valid.exitCode());
    assertEquals(RUN, valid.run());
    assertEquals(end, valid.after());
    assertEquals(new CleanupCounts(3, 1, 2), valid.before());
    assertFalse(valid.toString().contains(RUN.id().toString()));
    assertFalse(valid.toString().contains("2026-09-17"));
    assertTrue(valid.toString().contains("target=7"));
    assertTrue(valid.toString().contains("exitCode=10"));
    assertEquals(
        Long.MAX_VALUE,
        new LogCleanupSummary(
                RUN,
                ZERO,
                new LogCleanupProgress(
                    RUN, new CleanupCounts(Long.MAX_VALUE, Long.MAX_VALUE, 0), true))
            .attemptCounts()
            .deleted());
    assertThrows(NullPointerException.class, () -> new LogCleanupSummary(null, ZERO, end));
    assertThrows(NullPointerException.class, () -> new LogCleanupSummary(RUN, null, end));
    assertThrows(NullPointerException.class, () -> new LogCleanupSummary(RUN, ZERO, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new LogCleanupSummary(new BatchRun(new UUID(0, 95), RUN.cutoff()), ZERO, end));
    assertThrows(
        IllegalArgumentException.class,
        () -> new LogCleanupSummary(RUN, ZERO, new LogCleanupProgress(RUN, ZERO, false)));
    for (var before :
        List.of(
            new CleanupCounts(11, 5, 6), new CleanupCounts(10, 6, 4), new CleanupCounts(10, 4, 6)))
      assertThrows(IllegalArgumentException.class, () -> new LogCleanupSummary(RUN, before, end));
    assertEquals(
        Set.of("LOCK_BUSY", "BACKUP_GATE", "TIME_LIMIT", "INTERRUPTED", "DATABASE_FAILURE"),
        new HashSet<>(Arrays.stream(CleanupStopReason.values()).map(Enum::name).toList()));
    assertThrows(NullPointerException.class, () -> new CleanupStoppedException(null));
  }

  @Test
  void failuresLeaveNoFalseSuccess() throws Exception {
    for (String fault :
        List.of(
            "getAutoCommit",
            "begin",
            "lock.prepareStatement",
            "lock.executeQuery",
            "lock.next",
            "lock.getObject",
            "lock.resultClose",
            "lock.statementClose",
            "cleanup.prepareStatement",
            "cleanup.setObject",
            "cleanup.setTimestamp",
            "cleanup.setInt",
            "cleanup.executeQuery",
            "cleanup.next",
            "cleanup.getObject",
            "cleanup.getString",
            "cleanup.resultClose",
            "cleanup.statementClose",
            "progress.prepareStatement",
            "progress.setObject",
            "progress.setTimestamp",
            "progress.executeQuery",
            "progress.next",
            "progress.getObject",
            "progress.resultClose",
            "progress.statementClose")) {
      var probe = new ServiceJdbcProbe();
      probe.failAt.put(fault, 1);
      try (var c = batch()) {
        stopped(
            CleanupStopReason.DATABASE_FAILURE,
            () -> new LogCleanupService(() -> 0).execute(probe.wrap(c), RUN));
        assertEquals(1, probe.failures);
        assertEquals(0, probe.closes);
      }
    }
    reset();
    logs(2, 1);
    var changed = new ServiceJdbcProbe();
    changed.afterCommit =
        count -> {
          if (count == 1) {
            changed.columns.put("progress.target_count", 4L);
            changed.columns.put("progress.skipped_count", 3L);
          }
        };
    try (var c = batch()) {
      stopped(
          CleanupStopReason.DATABASE_FAILURE,
          () -> new LogCleanupService(() -> 0).execute(changed.wrap(c), RUN));
    }
    assertEquals("3|1|2|false", progress());
    var runtime = new ServiceJdbcProbe();
    runtime.runtimeAt = "cleanup.executeQuery";
    try (var c = batch()) {
      var error =
          assertThrows(
              IllegalStateException.class,
              () -> new LogCleanupService(() -> 0).execute(runtime.wrap(c), RUN));
      assertEquals("public programming fault", error.getMessage());
      assertEquals(1, runtime.rollbacks);
      assertTrue(c.getAutoCommit());
    }
    var tick = new AtomicInteger();
    try (var c = batch()) {
      assertThrows(
          IllegalStateException.class,
          () ->
              new LogCleanupService(
                      () -> {
                        if (tick.incrementAndGet() == 3)
                          throw new IllegalStateException("public clock fault");
                        return 0;
                      })
                  .execute(c, RUN));
      assertTrue(c.getAutoCommit());
    }
  }

  private static LongSupplier clock(long... times) {
    var index = new AtomicInteger();
    return () -> times[Math.min(index.getAndIncrement(), times.length - 1)];
  }

  private static CleanupStoppedException stopped(CleanupStopReason reason, Runnable action) {
    var failure = assertThrows(CleanupStoppedException.class, action::run);
    assertEquals(reason, failure.reason());
    assertEquals("cleanup did not complete", failure.getMessage());
    assertNull(failure.getCause());
    for (var extra : failure.getSuppressed()) {
      assertInstanceOf(CleanupStoppedException.class, extra);
      assertNull(extra.getCause());
    }
    return failure;
  }

  private static Connection batch() throws SQLException {
    return db.open("schubert_batch");
  }

  private static void logs(int held, int deleted) throws SQLException {
    try (var c = db.admin()) {
      sql(
          c,
          "insert into schubert.app_logs(id,logged_at,service,category,level,action,message,security_hold_until) select i,'2026-01-01 00:00:00+00','API','SECURITY','INFO','PUBLIC_TEST','public fixture',case when i<="
              + held
              + " then '2027-01-01 00:00:00+00'::timestamptz else null end from generate_series(1,"
              + (held + deleted)
              + ") i");
    }
  }

  private static String progress() throws SQLException {
    try (var c = db.admin()) {
      return scalar(
          c,
          "select target_count||'|'||deleted_count||'|'||skipped_count||'|'||(completed_at is not null)::text from schubert.log_cleanup_progress where run_id='"
              + RUN.id()
              + "'");
    }
  }

  private static String countLogs() throws SQLException {
    try (var c = db.admin()) {
      return scalar(c, "select count(*) from schubert.app_logs");
    }
  }

  private static void sql(Connection c, String query) throws SQLException {
    try (var s = c.createStatement()) {
      s.execute(query);
    }
  }

  private static String scalar(Connection c, String query) throws SQLException {
    try (var s = c.createStatement();
        var r = s.executeQuery(query)) {
      assertTrue(r.next());
      String value = r.getString(1);
      assertNotNull(value);
      assertFalse(r.next());
      return value;
    }
  }
}
