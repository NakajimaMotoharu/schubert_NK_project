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
 * NK-MIG-001; MIG003005006/MIG-DAT005/FUN004/DAT004/TST; UI223242254; SS311/331/V002/343 SSC389;
 * PT-MIG-ENTRYREAD001..020. Target ID mapping, fields and COPY assembly remain separate.
 */
@NullMarked
@Immutable
public final class CurrentScenarioEntryProjectionReader {
  private static final int QUERY_TIMEOUT_SECONDS = 30;
  private static final int FETCH_ROWS = 1000;
  private static final int COLUMN_COUNT = 10;
  private static final String PROJECTION =
      "SELECT id,game_id,script_file_id,entry_index,line_number,entry_type,speaker_id,speaker_label,body,raw_block FROM scenario.script_entries ORDER BY id";

  public List<List<@Nullable String>> read(@Nullable Connection connection, int expectedRows)
      throws SQLException {
    if (connection == null || expectedRows < 0) {
      throw new IllegalArgumentException("migration entry projection input is invalid");
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
    if (result.wasNull()) throw invalid();
    long file = result.getLong(3);
    if (result.wasNull()) throw invalid();
    int entryIndex = result.getInt(4);
    if (result.wasNull()) throw invalid();
    int lineNumber = result.getInt(5);
    if (result.wasNull()) throw invalid();
    @Nullable String type = result.getString(6);
    if (type == null) throw invalid();
    long speaker = result.getLong(7);
    @Nullable String speakerValue = result.wasNull() ? null : Long.toString(speaker);
    @Nullable String label = result.getString(8);
    @Nullable String body = result.getString(9);
    if (body == null) throw invalid();
    @Nullable String raw = result.getString(10);
    var fields = new ArrayList<@Nullable String>(COLUMN_COUNT);
    fields.add(Long.toString(id));
    fields.add(Integer.toString(game));
    fields.add(Long.toString(file));
    fields.add(Integer.toString(entryIndex));
    fields.add(Integer.toString(lineNumber));
    fields.add(type);
    fields.add(speakerValue);
    fields.add(label);
    fields.add(body);
    fields.add(raw);
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
    return new SQLException("migration entry projection is invalid");
  }

  @Override
  public String toString() {
    return "CurrentScenarioEntryProjectionReader[REDACTED]";
  }
}
