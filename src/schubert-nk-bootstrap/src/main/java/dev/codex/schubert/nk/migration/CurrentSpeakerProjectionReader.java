package dev.codex.schubert.nk.migration;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import javax.annotation.concurrent.Immutable;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Caller-owned Current snapshot projection; no authentication, transaction or data mutation.
 * NK-MIG-001; MIG003005006/MIG-DAT005/FUN004/DAT004/TST; UI223242254; SS311/331/V002/343 SSC376;
 * PT-MIG-SPEAKERREAD001..020. Target invariants belong to SpeakerMigrationMap and SpeakerCopyRow.
 */
@NullMarked
@Immutable
public final class CurrentSpeakerProjectionReader {
  private static final int QUERY_TIMEOUT_SECONDS = 30;
  private static final int FETCH_ROWS = 1000;
  private static final int COLUMN_COUNT = 6;
  private static final String PROJECTION =
      "SELECT id,game_id,name,normalized_name,is_protagonist,notes FROM scenario.speakers ORDER BY id";

  public List<List<@Nullable String>> read(@Nullable Connection connection, int expectedRows)
      throws SQLException {
    if (connection == null || expectedRows < 0) {
      throw new IllegalArgumentException("migration speaker projection input is invalid");
    }
    if (connection.getAutoCommit() || !connection.isReadOnly()) throw invalid();
    Statement statement = requireStatement(connection.createStatement());
    @Nullable Throwable primary = null;
    try {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      statement.setFetchSize(FETCH_ROWS);
      return rows(statement.executeQuery(PROJECTION), expectedRows);
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeStatement(statement, primary);
    }
  }

  private static Statement requireStatement(@Nullable Statement created) throws SQLException {
    if (created == null) throw invalid();
    return created;
  }

  private static List<List<@Nullable String>> rows(@Nullable ResultSet created, int expectedRows)
      throws SQLException {
    if (created == null) throw invalid();
    ResultSet result = created;
    @Nullable Throwable primary = null;
    try {
      var rows = new ArrayList<List<@Nullable String>>();
      while (result.next()) {
        if (rows.size() == expectedRows) throw invalid();
        rows.add(row(result));
      }
      if (rows.size() != expectedRows) throw invalid();
      return List.copyOf(rows);
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeResult(result, primary);
    }
  }

  private static List<@Nullable String> row(ResultSet result) throws SQLException {
    long id = result.getLong(1);
    if (result.wasNull()) throw invalid();
    int game = result.getInt(2);
    @Nullable String gameValue = result.wasNull() ? null : Integer.toString(game);
    @Nullable String name = result.getString(3);
    @Nullable String normalized = result.getString(4);
    if (name == null || normalized == null) throw invalid();
    boolean protagonist = result.getBoolean(5);
    if (result.wasNull()) throw invalid();
    @Nullable String notes = result.getString(6);
    var fields = new ArrayList<@Nullable String>(COLUMN_COUNT);
    fields.add(Long.toString(id));
    fields.add(gameValue);
    fields.add(name);
    fields.add(normalized);
    fields.add(Boolean.toString(protagonist));
    fields.add(notes);
    return Collections.unmodifiableList(fields);
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

  private static SQLException invalid() {
    return new SQLException("migration speaker projection is invalid");
  }

  @Override
  public String toString() {
    return "CurrentSpeakerProjectionReader[REDACTED]";
  }
}
