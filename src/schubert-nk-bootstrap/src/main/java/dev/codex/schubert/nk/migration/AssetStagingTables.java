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
              statement ->
                  statement.executeUpdate(
                      "CREATE TEMP TABLE nk_mig_audio_files ON COMMIT DROP AS SELECT id, game_id, storage_relative_path, display_path, file_name, basename, audio_role, container, duration_ms, byte_size, sha256, created_at FROM schubert.audio_files WITH NO DATA"),
              statement -> statement.executeQuery("SELECT count(*) FROM schubert.audio_files"),
              statement ->
                  statement.executeQuery("SELECT count(*) FROM pg_temp.nk_mig_audio_files"),
              statement ->
                  statement.executeLargeUpdate(
                      "INSERT INTO schubert.audio_files (id, game_id, storage_relative_path, display_path, file_name, basename, audio_role, container, duration_ms, byte_size, sha256, created_at) SELECT id, game_id, storage_relative_path, display_path, file_name, basename, audio_role, container, duration_ms, byte_size, sha256, created_at FROM pg_temp.nk_mig_audio_files ORDER BY id")),
          new Table(
              statement ->
                  statement.executeUpdate(
                      "CREATE TEMP TABLE nk_mig_media_assets ON COMMIT DROP AS SELECT id, logical_id, media_type, title, category, section, storage_relative_path, display_path, file_name, byte_size, sha256, mime_type, parent_logical_id, pair_key, pair_role, display_order, created_at FROM schubert.media_assets WITH NO DATA"),
              statement -> statement.executeQuery("SELECT count(*) FROM schubert.media_assets"),
              statement ->
                  statement.executeQuery("SELECT count(*) FROM pg_temp.nk_mig_media_assets"),
              statement ->
                  statement.executeLargeUpdate(
                      "INSERT INTO schubert.media_assets (id, logical_id, media_type, title, category, section, storage_relative_path, display_path, file_name, byte_size, sha256, mime_type, parent_logical_id, pair_key, pair_role, display_order, created_at) SELECT id, logical_id, media_type, title, category, section, storage_relative_path, display_path, file_name, byte_size, sha256, mime_type, parent_logical_id, pair_key, pair_role, display_order, created_at FROM pg_temp.nk_mig_media_assets ORDER BY id")),
          new Table(
              statement ->
                  statement.executeUpdate(
                      "CREATE TEMP TABLE nk_mig_entry_audio_links ON COMMIT DROP AS SELECT entry_id, audio_file_id, game_id, link_type, display_order, created_at FROM schubert.entry_audio_links WITH NO DATA"),
              statement ->
                  statement.executeQuery("SELECT count(*) FROM schubert.entry_audio_links"),
              statement ->
                  statement.executeQuery("SELECT count(*) FROM pg_temp.nk_mig_entry_audio_links"),
              statement ->
                  statement.executeLargeUpdate(
                      "INSERT INTO schubert.entry_audio_links (entry_id, audio_file_id, game_id, link_type, display_order, created_at) SELECT entry_id, audio_file_id, game_id, link_type, display_order, created_at FROM pg_temp.nk_mig_entry_audio_links ORDER BY entry_id, link_type, display_order, audio_file_id")));

  public void prepare(@Nullable Connection connection) throws SQLException {
    if (connection == null) throw invalidInput();
    Statement statement = open(connection);
    @Nullable Throwable primary = null;
    try {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      for (var table : TABLES) if (table.prepareOperation.execute(statement) != 0) throw invalid();
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
      for (var table : TABLES) requireResult(table.targetCountOperation.execute(statement), 0);
      for (int index = 0; index < TABLES.size(); index++)
        requireResult(TABLES.get(index).stageCountOperation.execute(statement), expected[index]);
      for (int index = 0; index < TABLES.size(); index++)
        if (TABLES.get(index).insertOperation.execute(statement) != expected[index])
          throw invalid();
      for (int index = 0; index < TABLES.size(); index++)
        requireResult(TABLES.get(index).targetCountOperation.execute(statement), expected[index]);
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

  /** SSC450: fixed operations capture no resource and cannot accept external SQL. */
  private static final class Table {
    private final SqlMutation prepareOperation;
    private final SqlQuery targetCountOperation;
    private final SqlQuery stageCountOperation;
    private final SqlMutation insertOperation;

    private Table(
        SqlMutation prepareOperation,
        SqlQuery targetCountOperation,
        SqlQuery stageCountOperation,
        SqlMutation insertOperation) {
      this.prepareOperation = prepareOperation;
      this.targetCountOperation = targetCountOperation;
      this.stageCountOperation = stageCountOperation;
      this.insertOperation = insertOperation;
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

  @FunctionalInterface
  private interface SqlQuery {
    @Nullable ResultSet execute(Statement statement) throws SQLException;
  }

  @FunctionalInterface
  private interface SqlMutation {
    long execute(Statement statement) throws SQLException;
  }
}
