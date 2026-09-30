package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.sql.*;
import java.time.*;
import java.util.*;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.io.TempDir;

/**
 * EXPARENT001/003/004/005: real isolated PG advisory handoffs, independent SQL/audit oracle.
 * Provider counters are fixed input here; genuine native MQ/Unit evidence is separate in 294.
 */
final class MorningExpirySessionTest {
  @TempDir static Path root;
  static BatchDatabaseFixture db;
  static String url;
  static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("39100000-2222-4333-8444-555555555555"),
          Instant.parse("2026-09-12T15:00:00Z"));
  static final Instant NOW = Instant.parse("2026-09-13T02:00:00Z");
  static final MaintenanceOwnerFrame.Guard OWNER = () -> 30_000_000_000L;

  @BeforeAll
  static void start() throws Exception {
    db = new BatchDatabaseFixture(root);
    try (var c = db.admin();
        var s = c.createStatement()) {
      url = c.getMetaData().getURL().replace("/postgres", "/schubert_nk");
      s.execute("create database schubert_nk");
    }
    Path resources =
        Path.of(
            System.getProperty("nk.pt.repository"), "src/schubert-nk-api/src/main/resources/db");
    try (var c = DriverManager.getConnection(url, "pgpt_admin", "");
        var s = c.createStatement()) {
      s.execute(Files.readString(resources.resolve("provisioning/001_roles.sql")));
    }
    Flyway.configure()
        .dataSource(url, "schubert_migration", "")
        .defaultSchema("schubert_meta")
        .schemas("schubert_meta")
        .createSchemas(true)
        .initSql("SET ROLE nk_owner")
        .locations("filesystem:" + resources.resolve("migration"))
        .validateOnMigrate(true)
        .cleanDisabled(true)
        .load()
        .migrate();
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = DriverManager.getConnection(url, "pgpt_admin", "");
        var s = c.createStatement()) {
      s.execute("delete from schubert.batch_runs");
    }
  }

  static InspectorDbCredential credential() {
    return InspectorDbCredential.consume("PUBLIC_PASSWORD".getBytes(StandardCharsets.US_ASCII));
  }

  static MorningDatabaseSession subject() {
    return new MorningDatabaseSession(url, () -> {}, DriverManager::getConnection, c -> {});
  }

  static void sql(Connection c, String text) throws SQLException {
    try (var s = c.createStatement()) {
      s.execute(text);
    }
  }

  static boolean held(Connection c) throws SQLException {
    try (var s = c.createStatement();
        var r =
            s.executeQuery(
                "select exists(select 1 from pg_locks where locktype='advisory' and pid=pg_backend_pid() and classid=0 and objid=71419602 and granted)")) {
      assertTrue(r.next());
      return r.getBoolean(1);
    }
  }

  static void ready(MorningDatabaseSession.Session session, int attempt) throws IOException {
    var start = NOW.plusSeconds(attempt * 10L);
    var backup = session.beginBackup(RUN, start, true);
    var failed =
        new BatchStepResult(
            BatchStepResult.Status.FAILED, 1, 0, 1, 0, BatchStepResult.Reason.COMMAND_FAILURE);
    session.failBackup(backup, start.plusSeconds(1), failed, failed);
    session.handoffCleanup(
        () -> {
          try (var c = DriverManager.getConnection(url, "schubert_batch", "")) {
            sql(c, "select pg_advisory_lock(71419602)");
            assertTrue(held(c));
            for (String step :
                List.of(
                    "CLEAN_NOTIFICATION",
                    "CLEAN_QUESTION",
                    "CLEAN_SESSION",
                    "CLEAN_INBOX_OUTBOX",
                    "CLEAN_LOG",
                    "CLEAN_BATCH_RUN"))
              sql(
                  c,
                  "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary) values('"
                      + RUN.id()
                      + "','2026-09-13','"
                      + step
                      + "',"
                      + attempt
                      + ",'"
                      + start.plusSeconds(2)
                      + "','"
                      + start.plusSeconds(2)
                      + "','SKIPPED',0,0,0,0,'BACKUP_UNAVAILABLE','verified backup unavailable')");
            sql(
                c,
                "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count"
                    + (attempt == 1 ? "" : ",error_code,error_summary")
                    + ") values('"
                    + RUN.id()
                    + "','2026-09-13','CLEAN_TRANSFER',"
                    + attempt
                    + ",'"
                    + start.plusSeconds(2)
                    + "','"
                    + start.plusSeconds(attempt == 1 ? 3 : 2)
                    + "','"
                    + (attempt == 1 ? "SUCCESS" : "SKIPPED")
                    + "',0,0,0,0"
                    + (attempt == 1
                        ? ""
                        : ",'ALREADY_SUCCESSFUL','step already successful for business date'")
                    + ")");
          } catch (SQLException known) {
            throw new IOException(known);
          }
          return true;
        });
    assertEquals(0, session.observeCleanupBackupUnavailable(RUN, 0, OWNER).exitCode());
  }

  @Test
  void actualFreshThenNormalSkipKeepOriginalAuditAndEachHandoffIsOneShot() throws Exception {
    for (int attempt = 1; attempt <= 2; attempt++) {
      final int current = attempt;
      var receipt = ExpiryReceiptFixture.receipt(0);
      subject()
          .execute(
              credential(),
              s -> {
                assertThrows(IOException.class, () -> s.beginExpiry(RUN, NOW, OWNER));
                assertThrows(
                    IOException.class,
                    () -> s.handoffExpiry(() -> fail("no child before Cleanup")));
                ready(s, current);
                var begins = s.beginExpiry(RUN, NOW.plusSeconds(current * 10L + 4), OWNER);
                assertEquals(current == 2, begins.current().skipped());
                assertEquals(current, begins.current().attempt());
                assertEquals(current == 2, begins.prior().isPresent());
                assertThrows(
                    IOException.class, () -> s.beginExpiry(RUN, NOW.plusSeconds(60), OWNER));
                s.handoffExpiry(
                    () -> {
                      try (var c = DriverManager.getConnection(url, "schubert_batch", "")) {
                        sql(c, "select pg_advisory_lock(71419602)");
                        assertTrue(held(c));
                        c.setAutoCommit(false);
                        if (current == 1) {
                          var audit = new ExpiryAuditRepository(c);
                          var stage = audit.stage(begins.current(), 3, 2, 200);
                          c.commit();
                          audit.finish(
                              begins.current(),
                              stage,
                              NOW.plusSeconds(15),
                              1L,
                              new BatchStepResult(
                                  BatchStepResult.Status.SUCCESS,
                                  2,
                                  2,
                                  0,
                                  200,
                                  BatchStepResult.Reason.NONE));
                          c.commit();
                        } else new BatchRunRepository(c).verifyAlreadySuccessful(begins.current());
                      } catch (SQLException known) {
                        throw new IOException(known);
                      }
                      return true;
                    });
                var observed = s.observeExpiry(begins, receipt, OWNER);
                assertEquals(
                    new ExpiryAuditRepository.Snapshot(
                        "SUCCESS",
                        Instant.parse("2026-09-05T15:00:00Z"),
                        3L,
                        1L,
                        2,
                        2,
                        0,
                        200,
                        NOW.plusSeconds(15),
                        null,
                        null),
                    observed);
                assertThrows(
                    IOException.class,
                    () -> s.handoffExpiry(() -> fail("cannot reacquire a second handoff")));
                return true;
              });
    }
    try (var c = DriverManager.getConnection(url, "pgpt_admin", "");
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select attempt,status,target_count,success_count,failure_count,byte_count,error_code,started_at=ended_at as same_time,expiry_before_count,expiry_after_count from schubert.batch_runs where step='CLEAN_EXPIRY' order by attempt")) {
      assertTrue(r.next());
      assertEquals(1, r.getInt("attempt"));
      assertEquals("SUCCESS", r.getString("status"));
      assertEquals(2, r.getLong("target_count"));
      assertEquals(2, r.getLong("success_count"));
      assertEquals(0, r.getLong("failure_count"));
      assertEquals(200, r.getLong("byte_count"));
      assertEquals(3, r.getLong("expiry_before_count"));
      assertEquals(1, r.getLong("expiry_after_count"));
      assertNull(r.getString("error_code"));
      assertFalse(r.getBoolean("same_time"));
      assertTrue(r.next());
      assertEquals(2, r.getInt("attempt"));
      assertEquals("SKIPPED", r.getString("status"));
      for (String field : List.of("target_count", "success_count", "failure_count", "byte_count"))
        assertEquals(0, r.getLong(field));
      assertEquals("ALREADY_SUCCESSFUL", r.getString("error_code"));
      assertTrue(r.getBoolean("same_time"));
      assertNull(r.getObject("expiry_before_count"));
      assertNull(r.getObject("expiry_after_count"));
      assertFalse(r.next());
    }
  }

  @Test
  void expiredOwnerNeverCommitsExpiryBeginAndDefaultCapabilityDoesNotGrantOperation()
      throws Exception {
    subject()
        .execute(
            credential(),
            s -> {
              ready(s, 1);
              assertThrows(
                  IOException.class, () -> s.beginExpiry(RUN, NOW.plusSeconds(14), () -> 0));
              assertThrows(NullPointerException.class, () -> s.beginExpiry(null, NOW, OWNER));
              assertThrows(NullPointerException.class, () -> s.beginExpiry(RUN, null, OWNER));
              assertThrows(NullPointerException.class, () -> s.beginExpiry(RUN, NOW, null));
              return true;
            });
    try (var c = DriverManager.getConnection(url, "pgpt_admin", "");
        var s = c.createStatement();
        var r =
            s.executeQuery("select count(*) from schubert.batch_runs where step='CLEAN_EXPIRY'")) {
      assertTrue(r.next());
      assertEquals(0, r.getLong(1));
    }
  }
}
