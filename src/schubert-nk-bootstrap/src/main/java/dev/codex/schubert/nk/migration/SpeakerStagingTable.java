package dev.codex.schubert.nk.migration;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Speaker parent staging on a borrowed transaction, never actual master/DB/ETL acceptance.
 * NK-MIG-001; MIG003005006/MIG-DAT005/FUN004/DAT004/TST; UI223242254; SS311/331/V002/343 SSC369;
 * PT-MIG-SPEAKERSTAGE001..024.
 */
@NullMarked
public final class SpeakerStagingTable {
  private static final int QUERY_TIMEOUT_SECONDS = 30;
  private static final String PREPARE_SQL =
      "CREATE TEMP TABLE nk_mig_speakers ON COMMIT DROP AS SELECT id, game_id, name, "
          + "normalized_name, is_protagonist, notes, created_at FROM schubert.speakers WITH NO DATA";
  private static final String TARGET_COUNT = "SELECT count(*) FROM schubert.speakers";
  private static final String STAGED_COUNT = "SELECT count(*) FROM pg_temp.nk_mig_speakers";
  private static final String INSERT_SQL =
      "INSERT INTO schubert.speakers (id, game_id, name, normalized_name, is_protagonist, notes, "
          + "created_at) SELECT id, game_id, name, normalized_name, is_protagonist, notes, created_at "
          + "FROM pg_temp.nk_mig_speakers ORDER BY id";

  public void prepare(@Nullable Connection connection) throws SQLException {
    if (connection == null) throw invalidInput();
    Statement statement = open(connection);
    @Nullable Throwable primary = null;
    try {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      if (statement.executeUpdate(PREPARE_SQL) != 0) throw invalid();
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeStatement(statement, primary);
    }
  }

  public void transfer(@Nullable Connection connection, long expectedSpeakers) throws SQLException {
    if (connection == null || expectedSpeakers < 0) throw invalidInput();
    Statement statement = open(connection);
    @Nullable Throwable primary = null;
    try {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      requireCount(statement, TARGET_COUNT, 0);
      requireCount(statement, STAGED_COUNT, expectedSpeakers);
      if (statement.executeLargeUpdate(INSERT_SQL) != expectedSpeakers) throw invalid();
      requireCount(statement, TARGET_COUNT, expectedSpeakers);
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeStatement(statement, primary);
    }
  }

  private static Statement open(Connection connection) throws SQLException {
    if (connection.getAutoCommit()) throw invalid();
    return requireStatement(connection.createStatement());
  }

  private static Statement requireStatement(@Nullable Statement created) throws SQLException {
    if (created == null) throw invalid();
    return created;
  }

  private static void requireCount(Statement statement, String sql, long expected)
      throws SQLException {
    requireResult(statement.executeQuery(sql), expected);
  }

  private static void requireResult(@Nullable ResultSet created, long expected)
      throws SQLException {
    if (created == null) throw invalid();
    ResultSet result = created;
    @Nullable Throwable primary = null;
    try {
      if (!result.next()) throw invalid();
      long actual = result.getLong(1);
      if (result.wasNull() || actual != expected || result.next()) throw invalid();
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeResult(result, primary);
    }
  }

  // SSC366/369: nonnull ownership, one close attempt and the original primary/suppressed order.
  private static void closeStatement(Statement resource, @Nullable Throwable primary)
      throws SQLException {
    if (primary == null) {
      resource.close();
      return;
    }
    try {
      resource.close();
    } catch (SQLException | RuntimeException | Error cleanup) {
      if (cleanup != primary) primary.addSuppressed(cleanup);
    }
  }

  private static void closeResult(ResultSet resource, @Nullable Throwable primary)
      throws SQLException {
    if (primary == null) {
      resource.close();
      return;
    }
    try {
      resource.close();
    } catch (SQLException | RuntimeException | Error cleanup) {
      if (cleanup != primary) primary.addSuppressed(cleanup);
    }
  }

  @Override
  public String toString() {
    return "SpeakerStagingTable[REDACTED]";
  }

  private static IllegalArgumentException invalidInput() {
    return new IllegalArgumentException("migration speaker staging input is invalid");
  }

  private static SQLException invalid() {
    return new SQLException("migration speaker staging preparation is invalid");
  }
}
