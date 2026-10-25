package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.database.MigrationInventory;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Types;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.regex.Pattern;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-DAT-001/PT-DB-INBOX-233..240; UI251 11/SS331 8.2; SSC-054/BUG-138/YKT-108. */
final class BackupRerunBoundaryTest {
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static final UUID RUN = new UUID(0, 200);
  private static final LocalDate DAY = LocalDate.of(2026, 9, 17);
  private static final Instant CUTOFF = Instant.parse("2026-09-17T00:00:00Z");
  private static final List<String> BACKUPS = List.of("BACKUP_DB", "BACKUP_CONFIG");
  private static final List<String> CLEANUPS =
      List.of(
          "notifications",
          "questions",
          "sessions",
          "message_stores",
          "logs",
          "batch_runs",
          "inbox_progress",
          "log_progress");

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
    try (var c = db.api()) {
      url = c.getMetaData().getURL();
    }
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = db.admin()) {
      for (String table :
          List.of("inbox_inspection_progress", "log_cleanup_progress", "batch_runs"))
        sql(c, "delete from schubert." + table);
    }
  }

  @Test
  void sameDayBackupReruns() throws Exception {
    try (var c = batch()) {
      for (String step : BACKUPS) {
        insert(c, RUN, DAY, step, 1, "SUCCESS");
        insert(c, RUN, DAY, step, 2, "SUCCESS");
        insert(c, new UUID(0, 201), DAY, step, 3, "SUCCESS");
      }
      assertEquals(
          "6", scalar(c, "select count(*) from schubert.batch_runs where status='SUCCESS'"));
      assertEquals(
          "BACKUP_CONFIG:1,BACKUP_CONFIG:2,BACKUP_CONFIG:3,BACKUP_DB:1,BACKUP_DB:2,BACKUP_DB:3",
          scalar(
              c,
              "select string_agg(step||':'||attempt,',' order by step,attempt) from schubert.batch_runs"));
    }
  }

  @Test
  void ordinarySuccessStillUnique() throws Exception {
    try (var c = batch()) {
      for (String step :
          List.of(
              "CLEAN_NOTIFICATION",
              "CLEAN_QUESTION",
              "CLEAN_SESSION",
              "CLEAN_INBOX_OUTBOX",
              "CLEAN_LOG",
              "CLEAN_BATCH_RUN",
              "CLEAN_TRANSFER",
              "CLEAN_EXPIRY",
              "READINESS",
              "backup_db",
              "BACKUP_D",
              "BACKUP_CONFIG_EXTRA")) {
        insert(c, RUN, DAY, step, 1, "SUCCESS");
        assertEquals(
            "23505",
            assertThrows(SQLException.class, () -> insert(c, RUN, DAY, step, 2, "SUCCESS"))
                .getSQLState());
        int attempt = 2;
        for (String status : List.of("RUNNING", "WARNING", "FAILED", "SKIPPED"))
          insert(c, RUN, DAY, step, attempt++, status);
      }
      assertEquals("60", scalar(c, "select count(*) from schubert.batch_runs"));
      assertEquals(
          "12", scalar(c, "select count(*) from schubert.batch_runs where status='SUCCESS'"));
    }
  }

  @Test
  void attemptAndDateBoundaries() throws Exception {
    try (var c = batch()) {
      for (String step : BACKUPS) {
        insert(c, RUN, DAY, step, 1, "SUCCESS");
        insert(c, RUN, DAY, step, 99, "SUCCESS");
        for (int n : List.of(0, 100))
          assertEquals(
              "23514",
              assertThrows(SQLException.class, () -> insert(c, RUN, DAY, step, n, "SUCCESS"))
                  .getSQLState());
        assertEquals(
            "23505",
            assertThrows(
                    SQLException.class, () -> insert(c, new UUID(0, 201), DAY, step, 1, "FAILED"))
                .getSQLState());
        insert(c, RUN, DAY.plusDays(1), step, 1, "SUCCESS");
      }
      assertEquals("6", scalar(c, "select count(*) from schubert.batch_runs"));
      for (String column :
          List.of("run_id", "business_date", "step", "attempt", "started_at", "status")) {
        assertEquals(
            "23502",
            assertThrows(
                    SQLException.class,
                    () ->
                        sql(
                            c,
                            "update schubert.batch_runs set "
                                + column
                                + "=null where step='BACKUP_DB' and attempt=99"))
                .getSQLState());
      }
      assertEquals(
          "23514",
          assertThrows(
                  SQLException.class,
                  () -> sql(c, "update schubert.batch_runs set status='UNKNOWN' where attempt=99"))
              .getSQLState());
    }
  }

  @Test
  void failureAndLatestSuccessHistory() throws Exception {
    try (var c = batch()) {
      for (String step : BACKUPS) {
        for (int n = 1; n <= 3; n++) insert(c, RUN, DAY, step, n, n == 3 ? "FAILED" : "SUCCESS");
        try (var statement =
            c.prepareStatement(
                "select attempt::integer from schubert.batch_runs where run_id=? and business_date=? and step=? and status='SUCCESS' and ended_at is not null order by ended_at desc,id desc limit 1")) {
          statement.setObject(1, RUN);
          statement.setObject(2, DAY);
          statement.setString(3, step);
          try (var row = statement.executeQuery()) {
            assertTrue(row.next());
            assertEquals(2, row.getInt(1));
            assertFalse(row.next());
          }
        }
      }
      assertEquals(
          "4", scalar(c, "select count(*) from schubert.batch_runs where status='SUCCESS'"));
      assertEquals(
          "2", scalar(c, "select count(*) from schubert.batch_runs where status='FAILED'"));
      assertEquals(
          "0", scalar(c, "select count(*) from schubert.batch_runs where status='SKIPPED'"));
    }
  }

  @Test
  void transactionRollbackAndMigration() throws Exception {
    try (var c = db.admin()) {
      c.setAutoCommit(false);
      String current =
          scalar(
              c,
              "select pg_get_indexdef('schubert.uq_batch_runs_business_step_success'::regclass)");
      var save = c.setSavepoint();
      sql(c, "drop index schubert.uq_batch_runs_business_step_success");
      var old =
          Pattern.compile(
                  "CREATE UNIQUE INDEX uq_batch_runs_business_step_success[^;]+;", Pattern.DOTALL)
              .matcher(
                  Files.readString(migrations().resolve("V004__indexes_and_initial_data.sql")));
      assertTrue(old.find());
      sql(c, old.group());
      insert(c, RUN, DAY, "BACKUP_DB", 1, "SUCCESS");
      assertEquals(
          "23505",
          assertThrows(SQLException.class, () -> insert(c, RUN, DAY, "BACKUP_DB", 2, "SUCCESS"))
              .getSQLState());
      c.rollback(save);
      assertEquals(
          current,
          scalar(
              c,
              "select pg_get_indexdef('schubert.uq_batch_runs_business_step_success'::regclass)"));
      insert(c, RUN, DAY, "BACKUP_DB", 1, "SUCCESS");
      insert(c, RUN, DAY, "BACKUP_DB", 2, "SUCCESS");
      assertEquals("2", scalar(c, "select count(*) from schubert.batch_runs"));
      c.rollback();
      assertEquals("0", scalar(c, "select count(*) from schubert.batch_runs"));
    }
    var flyway =
        Flyway.configure()
            .dataSource(url, "schubert_migration", "")
            .defaultSchema("schubert_meta")
            .schemas("schubert_meta")
            .initSql("SET ROLE nk_owner")
            .locations("filesystem:" + migrations())
            .cleanDisabled(true)
            .load();
    flyway.validate();
    assertEquals(0, flyway.migrate().migrationsExecuted);
  }

  @Test
  void concurrentSuccessAndAttemptConflicts() throws Exception {
    try (var pool = Executors.newFixedThreadPool(16)) {
      var barrier = new CyclicBarrier(16);
      var work = new ArrayList<Callable<String>>();
      for (int i = 1; i <= 16; i++) {
        final int attempt = i;
        work.add(
            () -> {
              try (var c = batch()) {
                barrier.await(10, TimeUnit.SECONDS);
                insert(c, RUN, DAY, "BACKUP_DB", attempt, "SUCCESS");
                return "OK";
              }
            });
      }
      for (var done : pool.invokeAll(work)) assertEquals("OK", done.get(10, TimeUnit.SECONDS));
      try (var c = batch()) {
        assertEquals("16", scalar(c, "select count(*) from schubert.batch_runs"));
      }
      for (String step : List.of("BACKUP_CONFIG", "CLEAN_LOG")) {
        var pair = new CyclicBarrier(2);
        var race = new ArrayList<Callable<String>>();
        for (int i = 1; i <= 2; i++) {
          final int attempt = step.equals("BACKUP_CONFIG") ? 1 : i;
          race.add(
              () -> {
                try (var c = batch()) {
                  pair.await(10, TimeUnit.SECONDS);
                  try {
                    insert(c, RUN, DAY, step, attempt, "SUCCESS");
                    return "OK";
                  } catch (SQLException failure) {
                    return failure.getSQLState();
                  }
                }
              });
        }
        var results = new ArrayList<String>();
        for (var done : pool.invokeAll(race)) results.add(done.get(10, TimeUnit.SECONDS));
        Collections.sort(results);
        assertEquals(List.of("23505", "OK"), results);
      }
    }
  }

  @Test
  void cleanupGatesWithRepeatedBackups() throws Exception {
    try (var c = batch()) {
      for (String step : BACKUPS)
        for (int i = 1; i <= 3; i++) insert(c, RUN, DAY, step, i, "SUCCESS");
      for (String name : CLEANUPS) assertEquals("OK", cleanup(c, name));
      assertEquals("6", scalar(c, "select count(*) from schubert.batch_runs"));
      for (String step : BACKUPS) {
        c.setAutoCommit(false);
        for (String change :
            List.of(
                "status='FAILED'",
                "ended_at=null",
                "business_date='2026-09-18'",
                "run_id='00000000-0000-0000-0000-000000000201'")) {
          var save = c.setSavepoint();
          sql(c, "update schubert.batch_runs set " + change + " where step='" + step + "'");
          for (String name : CLEANUPS) assertEquals("BACKUP_GATE", cleanup(c, name));
          c.rollback(save);
        }
        c.rollback();
        c.setAutoCommit(true);
      }
    }
    try (var c = db.admin()) {
      // Same helper is the private Inbox gate; test transaction holds and releases its lock.
      sql(
          c,
          "select schubert.maintenance_lock_inbox_backup('" + RUN + "','2026-09-17 00:00:00+00')");
      sql(c, "delete from schubert.batch_runs where step='BACKUP_CONFIG'");
      assertEquals(
          "55000",
          assertThrows(
                  SQLException.class,
                  () ->
                      sql(
                          c,
                          "select schubert.maintenance_lock_inbox_backup('"
                              + RUN
                              + "','2026-09-17 00:00:00+00')"))
              .getSQLState());
    }
  }

  @Test
  void catalogAndPrivileges() throws Exception {
    try (var c = db.admin()) {
      assertEquals(
          MigrationInventory.COUNT_TEXT,
          scalar(
              c,
              "select count(*) from schubert_meta.flyway_schema_history where success and version is not null"));
      assertEquals(
          "nk_owner",
          scalar(
              c,
              "select pg_get_userbyid(relowner) from pg_class where oid='schubert.uq_batch_runs_business_step_success'::regclass"));
      assertEquals(
          "true:true",
          scalar(
              c,
              "select indisunique||':'||indisvalid from pg_index where indexrelid='schubert.uq_batch_runs_business_step_success'::regclass"));
      String predicate =
          scalar(
              c,
              "select pg_get_expr(indpred,indrelid) from pg_index where indexrelid='schubert.uq_batch_runs_business_step_success'::regclass");
      for (String word : List.of("SUCCESS", "BACKUP_DB", "BACKUP_CONFIG"))
        assertTrue(predicate.contains(word));
      assertEquals(
          "1",
          scalar(
              c,
              "select count(*) from pg_constraint where conrelid='schubert.batch_runs'::regclass and conname='uq_batch_runs_business_step_attempt' and contype='u'"));
      assertEquals(
          "true:true:true:true",
          scalar(
              c,
              "select has_table_privilege('schubert_batch','schubert.batch_runs','SELECT')||':'||has_table_privilege('schubert_batch','schubert.batch_runs','INSERT')||':'||has_table_privilege('schubert_batch','schubert.batch_runs','UPDATE')||':'||has_table_privilege('schubert_batch','schubert.batch_runs','DELETE')"));
      for (String role :
          List.of("schubert_web_session", "schubert_backup", "schubert_inbox_inspector")) {
        try (var denied = DriverManager.getConnection(url, role, "")) {
          assertEquals(
              "42501",
              assertThrows(
                      SQLException.class, () -> insert(denied, RUN, DAY, "BACKUP_DB", 1, "SUCCESS"))
                  .getSQLState());
        }
      }
    }
  }

  private static Path migrations() {
    return Path.of(
        System.getProperty("nk.pt.repository"),
        "src/schubert-nk-api/src/main/resources/db/migration");
  }

  private static Connection batch() throws SQLException {
    return DriverManager.getConnection(url, "schubert_batch", "");
  }

  private static void insert(
      Connection c, UUID run, LocalDate day, String step, int attempt, String status)
      throws SQLException {
    try (var statement =
        c.prepareStatement(
            "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status,expiry_cutoff_at,expiry_before_count,expiry_after_count) values(?,?,?,?,?,?,?,?,?,?)")) {
      statement.setObject(1, run);
      statement.setObject(2, day);
      statement.setString(3, step);
      statement.setInt(4, attempt);
      statement.setObject(5, CUTOFF.atOffset(java.time.ZoneOffset.UTC));
      statement.setObject(6, CUTOFF.plusSeconds(attempt).atOffset(java.time.ZoneOffset.UTC));
      statement.setString(7, status);
      if (step.equals("CLEAN_EXPIRY") && status.equals("SUCCESS")) {
        statement.setObject(
            8, CUTOFF.minus(7, java.time.temporal.ChronoUnit.DAYS).atOffset(ZoneOffset.UTC));
        statement.setLong(9, 0);
        statement.setLong(10, 0);
      } else {
        statement.setNull(8, Types.TIMESTAMP_WITH_TIMEZONE);
        statement.setNull(9, Types.BIGINT);
        statement.setNull(10, Types.BIGINT);
      }
      assertEquals(1, statement.executeUpdate());
    }
  }

  private static String cleanup(Connection c, String name) throws SQLException {
    assertTrue(CLEANUPS.contains(name));
    try (var statement =
        c.prepareStatement(
            "select target_count,deleted_count,skipped_count,reason_code from schubert.maintenance_cleanup_"
                + name
                + "(?,?,?)")) {
      statement.setObject(1, RUN);
      statement.setObject(2, CUTOFF.atOffset(java.time.ZoneOffset.UTC));
      statement.setInt(3, 1);
      try (var row = statement.executeQuery()) {
        assertTrue(row.next());
        assertEquals(0, row.getLong(1));
        assertEquals(0, row.getLong(2));
        assertEquals(0, row.getLong(3));
        String reason = row.getString(4);
        assertFalse(row.next());
        return reason;
      }
    }
  }

  private static void sql(Connection c, String text) throws SQLException {
    try (var statement = c.createStatement()) {
      statement.execute(text);
    }
  }

  private static String scalar(Connection c, String text) throws SQLException {
    try (var statement = c.createStatement();
        var row = statement.executeQuery(text)) {
      assertTrue(row.next());
      String value = row.getString(1);
      assertNotNull(value);
      assertFalse(row.next());
      return value;
    }
  }
}
