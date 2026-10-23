package dev.codex.schubert.nk.web.monitoring;

import dev.codex.schubert.nk.web.monitoring.WebOutboxMetricRecorder.Observation;
import dev.codex.schubert.nk.web.monitoring.WebOutboxMetricRecorder.Status;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.EnumMap;
import java.util.Objects;
import org.jspecify.annotations.Nullable;

/**
 * Borrowed explicit readonly Web technical-schema observation, not connection/transaction
 * authority.
 */
public final class WebOutboxObservationRepository {
  private static final String SQL =
      "SELECT status, COUNT(*) AS row_count, MIN(created_at) AS oldest_created_at"
          + " FROM schubert_web_session.web_log_outbox GROUP BY status";
  private static final String INVALID = "Web outbox metric source rejected";

  /**
   * All owned statement/result resources close before returning a complete immutable observation.
   */
  public Observation read(Connection connection, Instant asOf) throws SQLException {
    Objects.requireNonNull(connection, "borrowed Web metrics connection");
    Objects.requireNonNull(asOf, "Web outbox observation instant");
    if (connection.getAutoCommit()
        || !connection.isReadOnly()
        || connection.getTransactionIsolation() != Connection.TRANSACTION_READ_COMMITTED)
      throw new SQLException(INVALID);
    var counts = new EnumMap<Status, Long>(Status.class);
    var ages = new EnumMap<Status, Duration>(Status.class);
    @Nullable PreparedStatement statement = connection.prepareStatement(SQL);
    if (statement == null) throw new SQLException(INVALID);
    try (statement) {
      statement.setQueryTimeout(1);
      @Nullable ResultSet rows = statement.executeQuery();
      if (rows == null) throw new SQLException(INVALID);
      try (rows) {
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
      }
    }
    return new Observation(
        counts.getOrDefault(Status.PENDING, 0L),
        counts.getOrDefault(Status.SENT, 0L),
        counts.getOrDefault(Status.ERROR, 0L),
        ages.getOrDefault(Status.PENDING, Duration.ZERO),
        ages.getOrDefault(Status.SENT, Duration.ZERO),
        ages.getOrDefault(Status.ERROR, Duration.ZERO));
  }

  private static Status status(@Nullable String value) throws SQLException {
    if (value == null) throw new SQLException(INVALID);
    try {
      return Status.parse(value);
    } catch (IllegalArgumentException invalidStatus) {
      throw new SQLException(INVALID, invalidStatus);
    }
  }
}
