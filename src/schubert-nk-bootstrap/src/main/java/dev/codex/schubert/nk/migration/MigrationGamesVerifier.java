package dev.codex.schubert.nk.migration;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Verify V004's two immutable initial games before staging, never DB or migration admission.
 * NK-MIG-001; MIG003005006/MIG-DAT005/DAT006/TST; UI242254; SS311331343/V004 SSC403;
 * PT-MIG-GAMES001..020/TARGET033..034. Borrowed write transaction, no correction or authority.
 */
@NullMarked
public final class MigrationGamesVerifier {
  private static final int QUERY_TIMEOUT_SECONDS = 30;
  private static final int FETCH_ROWS = 1000;
  private static final String CREATED_AT = "2026-09-01T00:00:00Z";
  private static final List<List<String>> EXPECTED =
      List.of(
          List.of("1", "NUKITASHI1", "NUKITASHI", "1", CREATED_AT),
          List.of("2", "NUKITASHI2", "NUKITASHI2", "2", CREATED_AT));
  private static final String PROJECTION =
      "SELECT id,code,title,display_order,created_at FROM schubert.games ORDER BY id";

  public void verify(@Nullable Connection connection) throws SQLException {
    if (connection == null) throw new IllegalArgumentException("migration games input is invalid");
    if (connection.getAutoCommit()) throw invalid();
    Statement statement = requireStatement(connection.createStatement());
    @Nullable Throwable primary = null;
    try {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      statement.setFetchSize(FETCH_ROWS);
      rows(statement.executeQuery(PROJECTION));
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

  private static void rows(@Nullable ResultSet created) throws SQLException {
    if (created == null) throw invalid();
    ResultSet result = created;
    @Nullable Throwable primary = null;
    try {
      int index = 0;
      while (result.next()) {
        if (index == EXPECTED.size()) throw invalid();
        row(result, EXPECTED.get(index));
        index++;
      }
      if (index != EXPECTED.size()) throw invalid();
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeResult(result, primary);
    }
  }

  private static void row(ResultSet result, List<String> expected) throws SQLException {
    int id = result.getInt(1);
    if (result.wasNull()) throw invalid();
    @Nullable String code = result.getString(2);
    @Nullable String title = result.getString(3);
    int order = result.getInt(4);
    if (result.wasNull()) throw invalid();
    @Nullable OffsetDateTime stamp = result.getObject(5, OffsetDateTime.class);
    var actual = new ArrayList<@Nullable String>();
    actual.add(Integer.toString(id));
    actual.add(code);
    actual.add(title);
    actual.add(Integer.toString(order));
    actual.add(stamp == null ? null : stamp.toInstant().toString());
    if (!expected.equals(actual)) throw invalid();
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
    return new SQLException("migration games initial rows are invalid");
  }

  @Override
  public String toString() {
    return "MigrationGamesVerifier[REDACTED]";
  }
}
