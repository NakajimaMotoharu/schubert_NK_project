package dev.codex.schubert.nk.migration;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Three asset staging tables on a borrowed transaction; never an actual database/ETL witness.
 * NK-MIG-001; MIG-DAT-002/MIG-DAT-003/MIG-DAT-004/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004;
 * UI242/254; SS311/331/343 SSC362; PT-MIG-ASSETSTAGE001..030.
 */
@NullMarked
public final class AssetStagingTables {
  private static final int QUERY_TIMEOUT_SECONDS = 30;
  private static final List<Table> TABLES =
      List.of(
          new Table(
              "audio_files",
              "id, game_id, storage_relative_path, display_path, file_name, basename, audio_role, container, duration_ms, byte_size, sha256, created_at",
              "id"),
          new Table(
              "media_assets",
              "id, logical_id, media_type, title, category, section, storage_relative_path, display_path, file_name, byte_size, sha256, mime_type, parent_logical_id, pair_key, pair_role, display_order, created_at",
              "id"),
          new Table(
              "entry_audio_links",
              "entry_id, audio_file_id, game_id, link_type, display_order, created_at",
              "entry_id, link_type, display_order, audio_file_id"));

  public void prepare(@Nullable Connection connection) throws SQLException {
    if (connection == null) throw invalidInput();
    Statement statement = open(connection);
    @Nullable Throwable primary = null;
    try {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      for (var table : TABLES) {
        String sql =
            "CREATE TEMP TABLE nk_mig_"
                + table.name
                + " ON COMMIT DROP AS SELECT "
                + table.columns
                + " FROM schubert."
                + table.name
                + " WITH NO DATA";
        if (statement.executeUpdate(sql) != 0) throw invalid();
      }
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeStatement(statement, primary);
    }
  }

  /**
   * Caller owns exclusive loading, full constraints, commit and rollback/discard on any failure.
   */
  public void transfer(
      @Nullable Connection connection, long expectedAudio, long expectedMedia, long expectedLinks)
      throws SQLException {
    if (connection == null
        || expectedAudio < 0
        || expectedMedia < 0
        || expectedLinks < 0
        || expectedAudio == 0 && expectedLinks != 0) throw invalidInput();
    long[] expected = {expectedAudio, expectedMedia, expectedLinks};
    Statement statement = open(connection);
    @Nullable Throwable primary = null;
    try {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      for (var table : TABLES) requireCount(statement, "schubert." + table.name, 0);
      for (int index = 0; index < TABLES.size(); index++)
        requireCount(statement, "pg_temp.nk_mig_" + TABLES.get(index).name, expected[index]);
      for (int index = 0; index < TABLES.size(); index++) {
        var table = TABLES.get(index);
        String sql =
            "INSERT INTO schubert."
                + table.name
                + " ("
                + table.columns
                + ") SELECT "
                + table.columns
                + " FROM pg_temp.nk_mig_"
                + table.name
                + " ORDER BY "
                + table.order;
        if (statement.executeLargeUpdate(sql) != expected[index]) throw invalid();
      }
      for (int index = 0; index < TABLES.size(); index++)
        requireCount(statement, "schubert." + TABLES.get(index).name, expected[index]);
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeStatement(statement, primary);
    }
  }

  @Override
  public String toString() {
    return "AssetStagingTables[REDACTED]";
  }

  private static Statement open(Connection connection) throws SQLException {
    if (connection.getAutoCommit()) throw invalid();
    return requireStatement(connection.createStatement());
  }

  private static Statement requireStatement(@Nullable Statement created) throws SQLException {
    if (created == null) throw invalid();
    return created;
  }

  private static void requireCount(Statement statement, String table, long expected)
      throws SQLException {
    requireResult(statement.executeQuery("SELECT count(*) FROM " + table), expected);
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

  private static IllegalArgumentException invalidInput() {
    return new IllegalArgumentException("migration asset staging input is invalid");
  }

  private static SQLException invalid() {
    return new SQLException("migration asset staging preparation is invalid");
  }

  /** Fixed approved SQL identifiers only, never caller-supplied metadata. */
  private static final class Table {
    private final String name;
    private final String columns;
    private final String order;

    private Table(String name, String columns, String order) {
      this.name = name;
      this.columns = columns;
      this.order = order;
    }
  }

  // SSC366: nonnull ownership established before try; preserve Java primary/suppressed order.
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

  // SSC366: nonnull ownership established before try; preserve Java primary/suppressed order.
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
}
