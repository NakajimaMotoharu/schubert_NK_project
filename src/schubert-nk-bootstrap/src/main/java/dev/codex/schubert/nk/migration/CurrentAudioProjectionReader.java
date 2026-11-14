package dev.codex.schubert.nk.migration;

import java.math.BigDecimal;
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
 * NK-MIG-001; MIG003005006/MIG-DAT005/FUN004/DAT004/TST; UI223242254; SS311/331/V002/343 SSC395;
 * PT-MIG-AUDIOREAD001..020. Source hash/size are untrusted metadata; target asset and COPY
 * qualification remain separate.
 */
@NullMarked
@Immutable
public final class CurrentAudioProjectionReader {
  private static final int SOURCE_PRECISION = 12;
  private static final int MINIMUM_SOURCE_SCALE = -8;
  private static final int MAXIMUM_SOURCE_SCALE = 3;
  private static final BigDecimal MAXIMUM_SOURCE_DURATION = new BigDecimal("999999999.999");
  private static final int QUERY_TIMEOUT_SECONDS = 30;
  private static final int FETCH_ROWS = 1000;
  private static final int COLUMN_COUNT = 10;
  private static final String PROJECTION =
      "SELECT id,game_id,relative_path,file_name,basename_upper,audio_role,container,duration_seconds,byte_size,sha256 FROM scenario.audio_files ORDER BY id";

  public List<List<@Nullable String>> read(@Nullable Connection connection, int expectedRows)
      throws SQLException {
    if (connection == null || expectedRows < 0) {
      throw new IllegalArgumentException("migration audio projection input is invalid");
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
    @Nullable String path = result.getString(3);
    @Nullable String fileName = result.getString(4);
    @Nullable String basename = result.getString(5);
    @Nullable String role = result.getString(6);
    if (path == null || fileName == null || basename == null || role == null) throw invalid();
    @Nullable String container = result.getString(7);
    @Nullable BigDecimal duration = result.getBigDecimal(8);
    long size = result.getLong(9);
    @Nullable String sizeValue = result.wasNull() ? null : Long.toString(size);
    @Nullable String digest = result.getString(10);
    var fields = new ArrayList<@Nullable String>(COLUMN_COUNT);
    fields.add(Long.toString(id));
    fields.add(Integer.toString(game));
    fields.add(path);
    fields.add(fileName);
    fields.add(basename);
    fields.add(role);
    fields.add(container);
    fields.add(duration(duration));
    fields.add(sizeValue);
    fields.add(digest);
    return Collections.unmodifiableList(fields);
  }

  private static @Nullable String duration(@Nullable BigDecimal value) throws SQLException {
    if (value == null) return null;
    // Check representation before plain rendering; do not expand an unbounded exponent or round.
    if (value.precision() > SOURCE_PRECISION
        || value.scale() < MINIMUM_SOURCE_SCALE
        || value.scale() > MAXIMUM_SOURCE_SCALE
        || value.abs().compareTo(MAXIMUM_SOURCE_DURATION) > 0) throw invalid();
    return value.toPlainString();
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
    return new SQLException("migration audio projection is invalid");
  }

  @Override
  public String toString() {
    return "CurrentAudioProjectionReader[REDACTED]";
  }
}
