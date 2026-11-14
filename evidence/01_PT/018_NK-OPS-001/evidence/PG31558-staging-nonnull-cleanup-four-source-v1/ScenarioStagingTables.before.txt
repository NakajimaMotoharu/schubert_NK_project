package dev.codex.schubert.nk.migration;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Prepares typed, empty temporary relations on a caller-owned migration transaction.
 * NK-MIG-001/MIG003005006/DAT004; UI254; SS311/331/343 section10 SSC352; PT-MIG-STAGE001..018.
 * Never a database, transaction or complete ETL acceptance witness.
 */
@NullMarked
public final class ScenarioStagingTables {
  private static final int QUERY_TIMEOUT_SECONDS = 30;
  private static final String FILES_SQL =
      "CREATE TEMP TABLE nk_mig_script_files ON COMMIT DROP AS SELECT "
          + "id, game_id, display_order, storage_relative_path, display_path, file_name, "
          + "section_code, chapter_title, sha256, byte_size, created_at "
          + "FROM schubert.script_files WITH NO DATA";
  private static final String ENTRIES_SQL =
      "CREATE TEMP TABLE nk_mig_script_entries ON COMMIT DROP AS SELECT "
          + "id, game_id, script_file_id, display_order, entry_index, line_number, entry_type, "
          + "speaker_id, speaker_label, body, raw_block, created_at "
          + "FROM schubert.script_entries WITH NO DATA";
  private static final String TARGET_FILES_COUNT = "SELECT count(*) FROM schubert.script_files";
  private static final String TARGET_ENTRIES_COUNT = "SELECT count(*) FROM schubert.script_entries";
  private static final String STAGED_FILES_COUNT =
      "SELECT count(*) FROM pg_temp.nk_mig_script_files";
  private static final String STAGED_ENTRIES_COUNT =
      "SELECT count(*) FROM pg_temp.nk_mig_script_entries";
  private static final String INSERT_FILES =
      "INSERT INTO schubert.script_files (id, game_id, display_order, storage_relative_path, "
          + "display_path, file_name, section_code, chapter_title, sha256, byte_size, created_at) "
          + "SELECT id, game_id, display_order, storage_relative_path, display_path, file_name, "
          + "section_code, chapter_title, sha256, byte_size, created_at "
          + "FROM pg_temp.nk_mig_script_files ORDER BY game_id, display_order";
  private static final String INSERT_ENTRIES =
      "INSERT INTO schubert.script_entries (id, game_id, script_file_id, display_order,"
          + " entry_index, line_number, entry_type, speaker_id, speaker_label, body, raw_block,"
          + " created_at) SELECT id, game_id, script_file_id, display_order, entry_index,"
          + " line_number, entry_type, speaker_id, speaker_label, body, raw_block, created_at FROM"
          + " pg_temp.nk_mig_script_entries ORDER BY display_order";

  /**
   * Caller owns connection, transaction, authentication, deadline and rollback/discard on failure.
   */
  public void prepare(@Nullable Connection connection) throws SQLException {
    if (connection == null)
      throw new IllegalArgumentException("migration staging input is invalid");
    if (connection.getAutoCommit()) throw invalid();
    @Nullable Statement created = connection.createStatement();
    if (created == null) throw invalid();
    try (Statement statement = created) {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      if (statement.executeUpdate(FILES_SQL) != 0) throw invalid();
      if (statement.executeUpdate(ENTRIES_SQL) != 0) throw invalid();
    }
  }

  /**
   * SSC353/PT-MIG-TRANSFER001..020: caller has authenticated and exclusively loaded/validated
   * staging. Success covers only these two table counts inside the borrowed, still uncommitted
   * transaction.
   */
  public void transfer(@Nullable Connection connection, int expectedFiles, int expectedEntries)
      throws SQLException {
    if (connection == null
        || expectedFiles < 0
        || expectedEntries < 0
        || expectedFiles == 0 && expectedEntries != 0) {
      throw new IllegalArgumentException("migration staging input is invalid");
    }
    if (connection.getAutoCommit()) throw invalid();
    @Nullable Statement created = connection.createStatement();
    if (created == null) throw invalid();
    try (Statement statement = created) {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      requireCount(statement, TARGET_FILES_COUNT, 0);
      requireCount(statement, TARGET_ENTRIES_COUNT, 0);
      requireCount(statement, STAGED_FILES_COUNT, expectedFiles);
      requireCount(statement, STAGED_ENTRIES_COUNT, expectedEntries);
      if (statement.executeUpdate(INSERT_FILES) != expectedFiles) throw invalid();
      if (statement.executeUpdate(INSERT_ENTRIES) != expectedEntries) throw invalid();
      requireCount(statement, TARGET_FILES_COUNT, expectedFiles);
      requireCount(statement, TARGET_ENTRIES_COUNT, expectedEntries);
    }
  }

  private static void requireCount(Statement statement, String sql, int expected)
      throws SQLException {
    requireResult(statement.executeQuery(sql), expected);
  }

  // SSC353/BUG2889: preserve the nullable vendor boundary independently of JDBC's declared
  // contract.
  private static void requireResult(@Nullable ResultSet created, int expected) throws SQLException {
    if (created == null) throw invalid();
    try (ResultSet result = created) {
      if (!result.next()) throw invalid();
      long actual = result.getLong(1);
      if (result.wasNull() || actual != expected || result.next()) throw invalid();
    }
  }

  @Override
  public String toString() {
    return "ScenarioStagingTables[REDACTED]";
  }

  private static SQLException invalid() {
    return new SQLException("migration staging preparation is invalid");
  }
}
