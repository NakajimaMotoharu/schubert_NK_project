package dev.codex.schubert.nk.api.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-IDEM-013 / PT-DB-011. SS324/332/341 independent retention and NULL regression. */
final class MessageStoreCleanupTest {
  private static final UUID RUN = UUID.fromString("00000000-0000-0000-0000-000000000031");
  private static final Instant CUTOFF = Instant.parse("2026-09-07T00:00:00Z");
  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;

  @BeforeAll static void start() throws Exception { database = new ApiLogDatabaseFixture(root); }
  @AfterAll static void stop() throws Exception { database.stop(); }
  @BeforeEach void reset() throws SQLException {
    try (var connection = database.admin(); var statement = connection.createStatement()) {
      statement.executeUpdate("delete from schubert.request_inbox");
      statement.executeUpdate("delete from schubert.mq_outbox");
      statement.executeUpdate("delete from schubert_web_session.web_log_outbox");
      statement.executeUpdate("delete from schubert.batch_runs");
    }
  }

  @Test
  void cleanupNullLimitsAreAlwaysRejected() throws SQLException {
    for (String function : List.of("notifications", "questions", "sessions", "message_stores", "logs", "batch_runs")) {
      try (var connection = database.admin(); var role = connection.createStatement()) {
        role.execute("set role schubert_batch");
        try (var statement = connection.prepareStatement(
            "select reason_code from schubert.maintenance_cleanup_" + function + "(?,?,?)")) {
          statement.setObject(1, RUN); statement.setTimestamp(2, Timestamp.from(CUTOFF));
          statement.setNull(3, java.sql.Types.INTEGER);
          var failure = assertThrows(SQLException.class, statement::executeQuery, function);
          assertEquals("22023", failure.getSQLState(), function);
        }
      }
    }
  }

  @Test
  void sentRowsYoungerThanSevenDaysMustRemain() throws SQLException {
    try (var connection = database.admin()) {
      backup(connection);
      outbox(connection, false, 1, "SENT", CUTOFF.minusSeconds(172800), null);
      outbox(connection, true, 2, "SENT", CUTOFF.minusSeconds(172800), null);
      assertEquals("0|0|0|OK", cleanup(connection, 1000));
      assertEquals(2, rows(connection));
    }
  }

  private static void backup(Connection connection) throws SQLException {
    try (var statement = connection.prepareStatement(
        "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status) "
            + "values(?,'2026-09-07',?,1,?,?,'SUCCESS')")) {
      for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG")) {
        statement.setObject(1, RUN); statement.setString(2, step);
        statement.setTimestamp(3, Timestamp.from(CUTOFF)); statement.setTimestamp(4, Timestamp.from(CUTOFF));
        assertEquals(1, statement.executeUpdate());
      }
    }
  }

  private static void outbox(Connection connection, boolean web, long id, String status,
      Instant sent, Instant lease) throws SQLException {
    String table = web ? "schubert_web_session.web_log_outbox" : "schubert.mq_outbox";
    String columns = web ? "payload_ciphertext,key_version" : "body,destination";
    String values = web ? "decode(repeat('00',29),'hex'),'synthetic-key'" : "decode('00','hex'),'nk.async.work'";
    try (var statement = connection.prepareStatement("insert into " + table
        + " (id,message_id,correlation_id,layout_id,layout_version," + columns
        + ",status,next_attempt_at,created_at,sent_at,lease_owner,lease_until) values(?,?,?,?,'001',"
        + values + ",?,?,?,?,?,?)")) {
      statement.setLong(1, id); statement.setObject(2, new UUID(0, id)); statement.setObject(3, new UUID(1, id));
      statement.setString(4, web ? "WLGEVT01" : "QWKREQ01"); statement.setString(5, status);
      statement.setTimestamp(6, Timestamp.from(CUTOFF.minusSeconds(864000)));
      statement.setTimestamp(7, Timestamp.from(CUTOFF.minusSeconds(864000)));
      statement.setTimestamp(8, sent == null ? null : Timestamp.from(sent));
      statement.setString(9, lease == null ? null : "synthetic-worker");
      statement.setTimestamp(10, lease == null ? null : Timestamp.from(lease));
      assertEquals(1, statement.executeUpdate());
    }
  }

  private static String cleanup(Connection connection, int limit) throws SQLException {
    try (var role = connection.createStatement()) { role.execute("set role schubert_batch"); }
    try (var statement = connection.prepareStatement(
        "select target_count,deleted_count,skipped_count,reason_code from schubert.maintenance_cleanup_message_stores(?,?,?)")) {
      statement.setObject(1, RUN); statement.setTimestamp(2, Timestamp.from(CUTOFF)); statement.setInt(3, limit);
      try (var result = statement.executeQuery()) {
        assertTrue(result.next());
        return result.getLong(1) + "|" + result.getLong(2) + "|" + result.getLong(3) + "|" + result.getString(4);
      }
    } finally { try (var role = connection.createStatement()) { role.execute("reset role"); } }
  }

  private static int rows(Connection connection) throws SQLException {
    try (var statement = connection.createStatement(); var result = statement.executeQuery(
        "select (select count(*) from schubert.mq_outbox)+(select count(*) from schubert_web_session.web_log_outbox)")) {
      assertTrue(result.next()); return result.getInt(1);
    }
  }
}
