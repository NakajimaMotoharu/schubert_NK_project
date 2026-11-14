package dev.codex.schubert.nk.migration;

import java.sql.Connection;
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

  @Override
  public String toString() {
    return "ScenarioStagingTables[REDACTED]";
  }

  private static SQLException invalid() {
    return new SQLException("migration staging preparation is invalid");
  }
}
