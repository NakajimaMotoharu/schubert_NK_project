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
 * NK-MIG-001; MIG003005006/MIG-DAT005/FUN004/DAT004/TST; UI223242254; SS311/331/V002/343
 * SSC371/406; PT-MIG-FINAL001..030. setval is not rolled back: partial failure requires caller
 * recovery, no retry.
 */
@NullMarked
public final class MigrationMasterFinalizer {
  private static final int QUERY_TIMEOUT_SECONDS = 30;
  private static final List<SqlQuery> MAXIMUM_QUERIES =
      List.of(
          statement -> statement.executeQuery("SELECT COALESCE(MAX(id),0) FROM schubert.speakers"),
          statement ->
              statement.executeQuery("SELECT COALESCE(MAX(id),0) FROM schubert.script_files"),
          statement ->
              statement.executeQuery("SELECT COALESCE(MAX(id),0) FROM schubert.script_entries"),
          statement ->
              statement.executeQuery("SELECT COALESCE(MAX(id),0) FROM schubert.audio_files"),
          statement ->
              statement.executeQuery("SELECT COALESCE(MAX(id),0) FROM schubert.media_assets"));
  private static final List<SqlPrepare> SYNCHRONIZERS =
      List.of(
          connection ->
              connection.prepareStatement(
                  "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.speakers', 'id'), ?, ?)"),
          connection ->
              connection.prepareStatement(
                  "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.script_files', 'id'), ?, ?)"),
          connection ->
              connection.prepareStatement(
                  "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.script_entries', 'id'), ?, ?)"),
          connection ->
              connection.prepareStatement(
                  "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.audio_files', 'id'), ?, ?)"),
          connection ->
              connection.prepareStatement(
                  "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.media_assets', 'id'), ?, ?)"));
  private static final List<SqlMutation> ANALYZE_OPERATIONS =
      List.of(
          statement -> statement.executeUpdate("ANALYZE schubert.speakers"),
          statement -> statement.executeUpdate("ANALYZE schubert.script_files"),
          statement -> statement.executeUpdate("ANALYZE schubert.script_entries"),
          statement -> statement.executeUpdate("ANALYZE schubert.audio_files"),
          statement -> statement.executeUpdate("ANALYZE schubert.media_assets"),
          statement -> statement.executeUpdate("ANALYZE schubert.entry_audio_links"));

  public void finish(@Nullable Connection connection, @Nullable MigrationMasterCopyDataset declared)
      throws SQLException {
    if (connection == null || declared == null) throw invalidInput();
    var expected = maxima(declared);
    Statement statement = open(connection);
    @Nullable Throwable primary = null;
    try {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      if (statement.executeUpdate(
                  "SET CONSTRAINTS schubert.ck_entry_audio_links_entry_type_limit IMMEDIATE")
              != 0
          || statement.getWarnings() != null) throw invalid();
      // All five checks precede the first nontransactional setval or ANALYZE call.
      for (int index = 0; index < MAXIMUM_QUERIES.size(); index++)
        requireResult(MAXIMUM_QUERIES.get(index).execute(statement), expected.get(index));
      for (int index = 0; index < MAXIMUM_QUERIES.size(); index++)
        synchronize(connection, SYNCHRONIZERS.get(index), expected.get(index));
      for (var operation : ANALYZE_OPERATIONS) {
        if (operation.execute(statement) != 0 || statement.getWarnings() != null) throw invalid();
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

  private static void synchronize(Connection connection, SqlPrepare operation, long maximum)
      throws SQLException {
    PreparedStatement statement = requirePrepared(operation.create(connection));
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

  @FunctionalInterface
  private interface SqlQuery {
    @Nullable ResultSet execute(Statement statement) throws SQLException;
  }

  @FunctionalInterface
  private interface SqlMutation {
    long execute(Statement statement) throws SQLException;
  }

  @FunctionalInterface
  private interface SqlPrepare {
    @Nullable PreparedStatement create(Connection connection) throws SQLException;
  }
}
