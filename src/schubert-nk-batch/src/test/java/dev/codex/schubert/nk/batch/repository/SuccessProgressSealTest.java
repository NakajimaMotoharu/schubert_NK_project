package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.HexFormat;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** REF201001..003 / OPS009 DAT009 UI251 SS331341343 SSC201 BUG788 YKT562. */
final class SuccessProgressSealTest {
  @TempDir static Path root;
  static BatchDatabaseFixture db;
  static final String RUN = "12345678-9abc-def0-8123-456789abcdef";
  static final String QUERY =
      "select proof_sha256 from schubert.maintenance_read_success_progress("
          + "'12345678-9abc-def0-8123-456789abcdef','2026-09-12T15:00:00Z',?,'2026-09-13T02:00:01Z')";
  static final String LOG_JSON =
      "{\"run_id\":\"12345678-9abc-def0-8123-456789abcdef\","
          + "\"cutoff\":\"2026-09-12T15:00:00+00:00\",\"after_logged_at\":\"2026-06-01T00:00:00+00:00\","
          + "\"after_id\":1,\"target_count\":1,\"deleted_count\":1,\"skipped_count\":0,"
          + "\"completed_at\":\"2026-09-13T02:00:01+00:00\"}";
  static final String INBOX_JSON =
      "{\"run_id\":\"12345678-9abc-def0-8123-456789abcdef\","
          + "\"cutoff\":\"2026-09-12T15:00:00+00:00\","
          + "\"after_message_id\":\"00000000-0000-4000-8000-000000000101\",\"inspected_count\":1,"
          + "\"deleted_count\":1,\"protected_count\":0,\"completed_at\":\"2026-09-13T02:00:01+00:00\"}";

  @BeforeAll
  static void start() throws Exception {
    db = new BatchDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void seed() throws Exception {
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute("delete from schubert.log_cleanup_progress");
      s.execute("delete from schubert.inbox_inspection_progress");
      s.execute(
          "insert into schubert.log_cleanup_progress values ('"
              + RUN
              + "','2026-09-12T15:00:00Z','2026-06-01T00:00:00Z',1,1,1,0,'2026-09-13T02:00:01Z')");
      s.execute(
          "insert into schubert.inbox_inspection_progress values ('"
              + RUN
              + "','2026-09-12T15:00:00Z','00000000-0000-4000-8000-000000000101',1,1,0,'2026-09-13T02:00:01Z')");
    }
  }

  static String hash(String literal) throws Exception {
    return HexFormat.of()
        .formatHex(
            MessageDigest.getInstance("SHA-256").digest(literal.getBytes(StandardCharsets.UTF_8)));
  }

  static String read(Connection c, String step) throws Exception {
    try (var s = c.prepareStatement(QUERY)) {
      s.setString(1, step);
      try (var r = s.executeQuery()) {
        assertEquals(1, r.getMetaData().getColumnCount());
        assertTrue(r.next());
        String result = r.getString(1);
        assertNotNull(result);
        assertTrue(result.matches("[0-9a-f]{64}"));
        assertFalse(r.next());
        return result;
      }
    }
  }

  static void sql(Connection c, String text) throws SQLException {
    try (var s = c.createStatement()) {
      s.execute(text);
    }
  }

  @Test
  void ref201001IndependentFullJsonShaAndCursorOnlyMutation() throws Exception {
    try (var c = db.open("schubert_batch")) {
      sql(c, "select pg_advisory_lock(71419602)");
      assertEquals(hash(LOG_JSON), read(c, "CLEAN_LOG"));
      assertEquals(hash(INBOX_JSON), read(c, "CLEAN_INBOX_OUTBOX"));
      try (var admin = db.admin()) {
        sql(admin, "update schubert.log_cleanup_progress set after_id=2");
        sql(
            admin,
            "update schubert.inbox_inspection_progress set after_message_id='00000000-0000-4000-8000-000000000102'");
      }
      assertEquals(
          hash(LOG_JSON.replace("\"after_id\":1", "\"after_id\":2")), read(c, "CLEAN_LOG"));
      assertNotEquals(hash(LOG_JSON), read(c, "CLEAN_LOG"));
      assertEquals(
          hash(INBOX_JSON.replace("000000000101", "000000000102")), read(c, "CLEAN_INBOX_OUTBOX"));
      assertNotEquals(hash(INBOX_JSON), read(c, "CLEAN_INBOX_OUTBOX"));
      assertTrue(c.getAutoCommit());
      assertFalse(c.isClosed());
    }
  }

  @Test
  void ref201002PermissionsLockAndArgumentsAreNotAuthority() throws Exception {
    for (String role :
        new String[] {
          "schubert_app",
          "schubert_web_session",
          "schubert_ops_ro",
          "schubert_backup",
          "schubert_inbox_inspector"
        }) {
      try (var c = db.open(role)) {
        assertEquals(
            "42501", assertThrows(SQLException.class, () -> read(c, "CLEAN_LOG")).getSQLState());
      }
    }
    try (var c = db.open("schubert_batch")) {
      assertEquals(
          "55000", assertThrows(SQLException.class, () -> read(c, "CLEAN_LOG")).getSQLState());
      sql(c, "select pg_advisory_lock_shared(71419602)");
      assertEquals(
          "55000", assertThrows(SQLException.class, () -> read(c, "CLEAN_LOG")).getSQLState());
      sql(c, "select pg_advisory_unlock_shared(71419602)");
      sql(c, "select pg_advisory_lock(71419602)");
      for (String step : new String[] {"CLEAN_TRANSFER", "", "CLEAN_LOG\n"})
        assertEquals("22023", assertThrows(SQLException.class, () -> read(c, step)).getSQLState());
      assertEquals("22023", assertThrows(SQLException.class, () -> read(c, null)).getSQLState());
      for (String bad :
          new String[] {
            QUERY.replace("'2026-09-12T15:00:00Z'", "null"),
            QUERY.replace("'2026-09-12T15:00:00Z'", "'infinity'"),
            QUERY.replace("'2026-09-13T02:00:01Z'", "null"),
            QUERY.replace("'2026-09-13T02:00:01Z'", "'2026-09-12T14:59:59Z'")
          }) {
        try (var s = c.prepareStatement(bad)) {
          s.setString(1, "CLEAN_LOG");
          assertEquals("22023", assertThrows(SQLException.class, s::executeQuery).getSQLState());
        }
      }
    }
  }

  @Test
  void ref201003MissingIncompleteFutureAndForeignCutoffAreRefusedWithoutRepair() throws Exception {
    try (var c = db.open("schubert_batch");
        var admin = db.admin()) {
      sql(c, "select pg_advisory_lock(71419602)");
      for (String table : new String[] {"log_cleanup_progress", "inbox_inspection_progress"}) {
        String step = table.startsWith("log") ? "CLEAN_LOG" : "CLEAN_INBOX_OUTBOX";
        for (String alteration :
            new String[] {
              "completed_at=null",
              "completed_at='2026-09-13T02:00:02Z'",
              "completed_at='2026-09-12T14:59:59Z'",
              "cutoff='2026-09-12T15:00:00.000001Z'"
            }) {
          admin.setAutoCommit(false);
          sql(admin, "update schubert." + table + " set " + alteration);
          admin.commit();
          assertEquals(
              "55000", assertThrows(SQLException.class, () -> read(c, step)).getSQLState());
          sql(
              admin,
              "update schubert."
                  + table
                  + " set cutoff='2026-09-12T15:00:00Z',completed_at='2026-09-13T02:00:01Z'");
          admin.commit();
        }
        sql(admin, "delete from schubert." + table);
        admin.commit();
        try (var s = c.prepareStatement(QUERY)) {
          s.setString(1, step);
          try (var r = s.executeQuery()) {
            assertFalse(r.next());
          }
        }
      }
    }
  }
}
