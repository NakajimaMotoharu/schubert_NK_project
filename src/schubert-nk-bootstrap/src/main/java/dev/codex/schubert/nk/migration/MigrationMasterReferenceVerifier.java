package dev.codex.schubert.nk.migration;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Read-only count/reference/order checks, never full catalog/data/migration acceptance. NK-MIG-001;
 * MIG003005006/MIG-DAT005/FUN004/DAT004/TST; UI223242254; SS311/331/V002/343 SSC372;
 * PT-MIG-REF001..020. Caller retains authentication, exclusive loading and the transaction.
 */
@NullMarked
public final class MigrationMasterReferenceVerifier {
  private static final int QUERY_TIMEOUT_SECONDS = 30;
  private static final List<String> COUNTS =
      List.of(
          "SELECT count(*) FROM schubert.speakers",
          "SELECT count(*) FROM schubert.script_files",
          "SELECT count(*) FROM schubert.script_entries",
          "SELECT count(*) FROM schubert.audio_files",
          "SELECT count(*) FROM schubert.media_assets",
          "SELECT count(*) FROM schubert.entry_audio_links");
  private static final List<String> INSPECTIONS =
      List.of(
          "SELECT count(*) FROM schubert.script_files c LEFT JOIN schubert.games p ON p.id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.speakers c LEFT JOIN schubert.games p ON p.id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.script_entries c LEFT JOIN schubert.games p ON p.id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.audio_files c LEFT JOIN schubert.games p ON p.id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.script_entries c LEFT JOIN schubert.script_files p ON p.id=c.script_file_id AND p.game_id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.script_entries c LEFT JOIN schubert.speakers p ON p.id=c.speaker_id AND p.game_id=c.game_id WHERE c.speaker_id IS NOT NULL AND p.id IS NULL",
          "SELECT count(*) FROM schubert.entry_audio_links c LEFT JOIN schubert.script_entries p ON p.id=c.entry_id AND p.game_id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.entry_audio_links c LEFT JOIN schubert.audio_files p ON p.id=c.audio_file_id AND p.game_id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.media_assets c LEFT JOIN schubert.media_assets p ON p.logical_id=c.parent_logical_id WHERE c.parent_logical_id IS NOT NULL AND p.logical_id IS NULL",
          "SELECT count(*) FROM (SELECT entry_id,link_type FROM schubert.entry_audio_links GROUP BY entry_id,link_type HAVING count(*)>999 OR min(display_order)<1 OR max(display_order)>999 OR count(DISTINCT display_order)<>count(*)) violations");

  public void verify(@Nullable Connection connection, @Nullable MigrationMasterCopyDataset declared)
      throws SQLException {
    if (connection == null || declared == null) throw invalidInput();
    var content = declared.content();
    var expected =
        List.of(
            (long) declared.speakers().rows().size(),
            (long) content.scenario().files().rows().size(),
            (long) content.scenario().entries().rows().size(),
            (long) content.audio().audioRows().size(),
            (long) content.media().rows().size(),
            (long) content.audio().linkRows().size());
    Statement statement = open(connection);
    @Nullable Throwable primary = null;
    try {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      for (int index = 0; index < COUNTS.size(); index++)
        requireResult(statement.executeQuery(COUNTS.get(index)), expected.get(index));
      for (var query : INSPECTIONS) requireResult(statement.executeQuery(query), 0);
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
    return "MigrationMasterReferenceVerifier[REDACTED]";
  }

  private static IllegalArgumentException invalidInput() {
    return new IllegalArgumentException("migration master reference input is invalid");
  }

  private static SQLException invalid() {
    return new SQLException("migration master reference verification is invalid");
  }
}
