package dev.codex.schubert.nk.migration;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Borrowed-owner identity/statistics finalization, never authorization or a DB migration receipt.
 * NK-MIG-001; MIG003005006/MIG-DAT005/FUN004/DAT004/TST; UI223242254; SS311/331/V002/343 SSC371;
 * PT-MIG-FINAL001..028. setval is not rolled back: partial failure requires caller recovery, no
 * retry.
 */
@NullMarked
public final class MigrationMasterFinalizer {
  private static final int QUERY_TIMEOUT_SECONDS = 30;
  private static final List<String> IDENTITY_TABLES =
      List.of("speakers", "script_files", "script_entries", "audio_files", "media_assets");
  private static final List<String> ANALYZE_TABLES =
      List.of(
          "speakers",
          "script_files",
          "script_entries",
          "audio_files",
          "media_assets",
          "entry_audio_links");

  public void finish(@Nullable Connection connection, @Nullable MigrationMasterCopyDataset declared)
      throws SQLException {
    if (connection == null || declared == null) throw invalidInput();
    var expected = maxima(declared);
    Statement statement = open(connection);
    @Nullable Throwable primary = null;
    try {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      // All five checks precede the first nontransactional setval or ANALYZE call.
      for (int index = 0; index < IDENTITY_TABLES.size(); index++)
        requireResult(
            statement.executeQuery(
                "SELECT COALESCE(MAX(id),0) FROM schubert." + IDENTITY_TABLES.get(index)),
            expected.get(index));
      for (int index = 0; index < IDENTITY_TABLES.size(); index++)
        synchronize(connection, IDENTITY_TABLES.get(index), expected.get(index));
      for (var table : ANALYZE_TABLES) {
        if (statement.executeUpdate("ANALYZE schubert." + table) != 0
            || statement.getWarnings() != null) throw invalid();
      }
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeStatement(statement, primary);
    }
  }

  private static List<Long> maxima(MigrationMasterCopyDataset declared) {
    var content = declared.content();
    return List.of(
        maximum(declared.speakers().rows().stream().map(SpeakerCopyRow::fields).toList()),
        maximum(content.scenario().files().rows()),
        maximum(
            content.scenario().entries().rows().stream()
                .map(ScenarioEntryCopyRow::fields)
                .toList()),
        maximum(content.audio().audioRows().stream().map(AudioFileCopyRow::fields).toList()),
        maximum(content.media().rows().stream().map(MediaAssetCopyRow::fields).toList()));
  }

  private static long maximum(List<List<@Nullable String>> rows) {
    long maximum = 0;
    for (var row : rows)
      maximum = Math.max(maximum, Long.parseLong(Objects.requireNonNull(row.get(0))));
    return maximum;
  }

  private static Statement open(Connection connection) throws SQLException {
    if (connection.getAutoCommit()) throw invalid();
    @Nullable Statement created = connection.createStatement();
    if (created == null) throw invalid();
    return created;
  }

  private static void synchronize(Connection connection, String table, long maximum)
      throws SQLException {
    PreparedStatement statement =
        requirePrepared(
            connection.prepareStatement(
                "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert."
                    + table
                    + "', 'id'), ?, ?)"));
    @Nullable Throwable primary = null;
    try {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      long value = maximum == 0 ? 1 : maximum;
      statement.setLong(1, value);
      statement.setBoolean(2, maximum > 0);
      requireResult(statement.executeQuery(), value);
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeStatement(statement, primary);
    }
  }

  private static PreparedStatement requirePrepared(@Nullable PreparedStatement created)
      throws SQLException {
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
    return "MigrationMasterFinalizer[REDACTED]";
  }

  private static IllegalArgumentException invalidInput() {
    return new IllegalArgumentException("migration master finalization input is invalid");
  }

  private static SQLException invalid() {
    return new SQLException("migration master finalization is invalid");
  }
}
