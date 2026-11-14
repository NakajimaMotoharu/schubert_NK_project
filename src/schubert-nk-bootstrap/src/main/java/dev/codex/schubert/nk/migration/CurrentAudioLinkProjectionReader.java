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
 * Borrowed Current link snapshot projection, never a DB or target order/identity witness.
 * NK-MIG-001; MIG003005006/MIG-DAT001002005/FUN005/DAT004/TST; UI227242254; SS311331/V002/343
 * SSC399; PT-MIG-AUDIOLINKREAD001..020. Signed IDs and stored kind are retained without repair.
 */
@NullMarked
@Immutable
public final class CurrentAudioLinkProjectionReader {
  private static final int QUERY_TIMEOUT_SECONDS = 30;
  private static final int FETCH_ROWS = 1000;
  private static final int COLUMN_COUNT = 3;
  private static final String PROJECTION =
      "SELECT entry_id,audio_file_id,link_type FROM scenario.entry_audio_links ORDER BY entry_id,audio_file_id,link_type COLLATE \"C\"";

  public List<List<@Nullable String>> read(@Nullable Connection connection, int expectedRows)
      throws SQLException {
    if (connection == null || expectedRows < 0) {
      throw new IllegalArgumentException("migration audio link projection input is invalid");
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
    long entryId = result.getLong(1);
    if (result.wasNull()) throw invalid();
    long audioId = result.getLong(2);
    if (result.wasNull()) throw invalid();
    @Nullable String linkType = result.getString(3);
    if (linkType == null) throw invalid();
    var fields = new ArrayList<@Nullable String>(COLUMN_COUNT);
    fields.add(Long.toString(entryId));
    fields.add(Long.toString(audioId));
    fields.add(linkType);
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
    return new SQLException("migration audio link projection is invalid");
  }

  @Override
  public String toString() {
    return "CurrentAudioLinkProjectionReader[REDACTED]";
  }
}
