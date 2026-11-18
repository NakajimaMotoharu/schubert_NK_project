package dev.codex.schubert.nk.api.monitoring.persistence;

import dev.codex.schubert.nk.api.monitoring.OutboxAgeMetricRecorder.Ages;
import dev.codex.schubert.nk.api.monitoring.OutboxRowsMetricRecorder;
import dev.codex.schubert.nk.api.monitoring.OutboxRowsMetricRecorder.Counts;
import dev.codex.schubert.nk.api.monitoring.OutboxRowsMetricRecorder.Status;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.EnumMap;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Borrowed readonly observation only; no real DB/runtime admission. PG-D547/OUTBOXDB001..010/1664.
 */
@NullMarked
public final class OutboxObservationRepository {
  private static final String SQL =
      "SELECT status, COUNT(*) AS row_count, MIN(created_at) AS oldest_created_at"
          + " FROM schubert.mq_outbox GROUP BY status";
  private static final String INVALID = "outbox metric source rejected";
  private static final int QUERY_TIMEOUT_SECONDS = 1;

  public record Snapshot(Counts counts, Ages ages) {
    public Snapshot {
      Objects.requireNonNull(counts, "outbox counts");
      Objects.requireNonNull(ages, "outbox ages");
    }
  }

  /** Caller owns connection/transaction/asOf source; all acquired resources close before return. */
  public Snapshot read(Connection connection, Instant asOf) throws SQLException {
    Objects.requireNonNull(connection, "borrowed metrics connection");
    Objects.requireNonNull(asOf, "outbox observation instant");
    if (connection.getAutoCommit()
        || !connection.isReadOnly()
        || connection.getTransactionIsolation() != Connection.TRANSACTION_READ_COMMITTED)
      throw new SQLException(INVALID);
    var counts = new EnumMap<Status, Long>(Status.class);
    var ages = new EnumMap<Status, Duration>(Status.class);
    @Nullable PreparedStatement statement = connection.prepareStatement(SQL);
    if (statement == null) throw new SQLException(INVALID);
    @Nullable Throwable statementFailure = null;
    try {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      @Nullable ResultSet rows = statement.executeQuery();
      if (rows == null) throw new SQLException(INVALID);
      @Nullable Throwable rowFailure = null;
      try {
        while (rows.next()) {
          Status status = status(rows.getString("status"));
          long count = rows.getLong("row_count");
          if (rows.wasNull() || count <= 0 || counts.containsKey(status))
            throw new SQLException(INVALID);
          @Nullable OffsetDateTime created =
              rows.getObject("oldest_created_at", OffsetDateTime.class);
          if (created == null || created.toInstant().isAfter(asOf)) throw new SQLException(INVALID);
          counts.put(status, count);
          ages.put(status, Duration.between(created.toInstant(), asOf));
        }
      } catch (Throwable failure) {
        rowFailure = failure;
        throw failure;
      } finally {
        closeRows(rows, rowFailure);
      }
    } catch (Throwable failure) {
      statementFailure = failure;
      throw failure;
    } finally {
      closeStatement(statement, statementFailure);
    }
    return new Snapshot(
        new Counts(
            counts.getOrDefault(Status.PENDING, 0L),
            counts.getOrDefault(Status.SENT, 0L),
            counts.getOrDefault(Status.ERROR, 0L)),
        new Ages(
            ages.getOrDefault(Status.PENDING, Duration.ZERO),
            ages.getOrDefault(Status.SENT, Duration.ZERO),
            ages.getOrDefault(Status.ERROR, Duration.ZERO)));
  }

  // SSC-470: preserve the exact try-with-resources primary and suppression rules.
  private static void closeRows(ResultSet rows, @Nullable Throwable primary) throws SQLException {
    try {
      rows.close();
    } catch (Throwable secondary) {
      if (primary == null) throw secondary;
      primary.addSuppressed(secondary);
    }
  }

  private static void closeStatement(PreparedStatement statement, @Nullable Throwable primary)
      throws SQLException {
    try {
      statement.close();
    } catch (Throwable secondary) {
      if (primary == null) throw secondary;
      primary.addSuppressed(secondary);
    }
  }

  private static Status status(@Nullable String value) throws SQLException {
    if (value == null) throw new SQLException(INVALID);
    try {
      return OutboxRowsMetricRecorder.status(value);
    } catch (IllegalArgumentException invalidStatus) {
      throw new SQLException(INVALID, invalidStatus);
    }
  }
}
