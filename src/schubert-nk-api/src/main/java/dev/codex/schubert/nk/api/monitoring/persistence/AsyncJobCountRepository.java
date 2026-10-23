package dev.codex.schubert.nk.api.monitoring.persistence;

import dev.codex.schubert.nk.api.monitoring.AsyncJobMetricRecorder;
import dev.codex.schubert.nk.api.monitoring.AsyncJobMetricRecorder.Snapshot;
import dev.codex.schubert.nk.api.monitoring.AsyncJobMetricRecorder.State;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.EnumMap;
import java.util.EnumSet;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Borrowed caller-owned readonly transaction only, not real DB/role/runtime admission.
 * RD171/UI252/SS331332342351; PG-D540/ASYNCDB001..008/spec1627.
 */
@NullMarked
public final class AsyncJobCountRepository {
  private static final String SQL =
      "SELECT state, COUNT(*) AS job_count FROM schubert.async_jobs GROUP BY state";
  private static final String INVALID = "async metric source rejected";
  private static final int QUERY_TIMEOUT_SECONDS = 1;

  /**
   * No connection creation/config mutation/commit/rollback/close; RS/PS close before publication.
   */
  public Snapshot read(Connection connection) throws SQLException {
    Objects.requireNonNull(connection, "borrowed metrics connection");
    if (connection.getAutoCommit()
        || !connection.isReadOnly()
        || connection.getTransactionIsolation() != Connection.TRANSACTION_READ_COMMITTED)
      throw new SQLException(INVALID);
    var counts = new EnumMap<State, Long>(State.class);
    for (var state : State.values()) counts.put(state, 0L);
    var seen = EnumSet.noneOf(State.class);
    @Nullable PreparedStatement statement = connection.prepareStatement(SQL);
    if (statement == null) throw new SQLException(INVALID);
    try (statement) {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      @Nullable ResultSet rows = statement.executeQuery();
      if (rows == null) throw new SQLException(INVALID);
      try (rows) {
        while (rows.next()) {
          State state = state(rows.getString("state"));
          long count = rows.getLong("job_count");
          if (rows.wasNull() || count < 0 || !seen.add(state)) throw new SQLException(INVALID);
          counts.put(state, count);
        }
      }
    }
    try {
      return new Snapshot(counts);
    } catch (ArithmeticException overflow) {
      throw new SQLException(INVALID, overflow);
    }
  }

  private static State state(@Nullable String value) throws SQLException {
    if (value == null) throw new SQLException(INVALID);
    try {
      return AsyncJobMetricRecorder.state(value);
    } catch (IllegalArgumentException invalidState) {
      throw new SQLException(INVALID, invalidState);
    }
  }
}
