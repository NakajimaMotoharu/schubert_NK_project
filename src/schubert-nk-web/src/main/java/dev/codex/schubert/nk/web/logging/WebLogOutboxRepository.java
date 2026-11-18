package dev.codex.schubert.nk.web.logging;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.ThreadLocalRandom;
import java.util.function.IntSupplier;
import javax.annotation.WillClose;
import org.jspecify.annotations.Nullable;

/**
 * Web technical-schema persistence, with all transaction decisions owned by the caller. Trace:
 * NK-MSG-002; RD MON-003/MQ-008; UI 242; SS 324 section 9/332 section 7; PT-IDEM-012. Never
 * accesses schubert business tables or accepts plaintext for storage.
 */
public final class WebLogOutboxRepository {
  private final IntSupplier jitterPermille;

  public WebLogOutboxRepository() {
    this(() -> ThreadLocalRandom.current().nextInt(-100, 101));
  }

  public WebLogOutboxRepository(IntSupplier jitterPermille) {
    this.jitterPermille = Objects.requireNonNull(jitterPermille, "jitterPermille");
  }

  /** Inserts an already authenticated local event once; duplicate IDs retain the first row. */
  public boolean enqueue(
      Connection connection,
      WebLogPayloadIdentity identity,
      EncryptedWebLogPayload payload,
      Instant now)
      throws SQLException {
    requireTransaction(connection);
    Objects.requireNonNull(identity, "identity");
    Objects.requireNonNull(payload, "payload");
    Objects.requireNonNull(now, "now");
    @Nullable PreparedStatement acquiredStatement =
        connection.prepareStatement(
            "insert into schubert_web_session.web_log_outbox "
                + "(message_id,correlation_id,layout_id,layout_version,payload_ciphertext,key_version,"
                + "status,attempt_count,next_attempt_at,created_at) "
                + "values(?,?,'WLGEVT01','001',?,?,'PENDING',0,?,?) "
                + "on conflict(message_id) do nothing");
    @Nullable Throwable statementFailure = null;
    try {
      PreparedStatement statement = required(acquiredStatement);
      statement.setObject(1, identity.messageId());
      statement.setObject(2, identity.correlationId());
      statement.setBytes(3, payload.ciphertext());
      statement.setString(4, payload.keyVersion());
      statement.setObject(5, now.atOffset(java.time.ZoneOffset.UTC));
      statement.setObject(6, now.atOffset(java.time.ZoneOffset.UTC));
      return statement.executeUpdate() == 1;
    } catch (Throwable failure) {
      statementFailure = failure;
      throw failure;
    } finally {
      closeStatement(acquiredStatement, statementFailure);
    }
  }

  /** Claims up to 100 due rows with a 10-second lease; commit before any remote I/O. */
  public List<ClaimedWebLog> claim(Connection connection, String worker, Instant now, int limit)
      throws SQLException {
    requireTransaction(connection);
    ClaimedWebLog.requireWorker(worker);
    Objects.requireNonNull(now, "now");
    if (limit < 1 || limit > 100) {
      throw new IllegalArgumentException("web log claim limit is outside 1..100");
    }
    String sql =
        "with due as (select id from schubert_web_session.web_log_outbox "
            + "where status in ('PENDING','ERROR') and next_attempt_at<=? "
            + "and (lease_until is null or lease_until<?) order by next_attempt_at,id "
            + "for update skip locked limit ?) update schubert_web_session.web_log_outbox o "
            + "set lease_owner=?,lease_until=? from due where o.id=due.id "
            + "returning o.id,o.message_id,o.correlation_id,o.layout_id,o.layout_version,"
            + "o.payload_ciphertext,o.key_version,o.attempt_count,o.next_attempt_at,o.created_at,"
            + "o.lease_owner,o.lease_until";
    @Nullable PreparedStatement acquiredStatement = connection.prepareStatement(sql);
    @Nullable Throwable statementFailure = null;
    try {
      PreparedStatement statement = required(acquiredStatement);
      statement.setObject(1, now.atOffset(java.time.ZoneOffset.UTC));
      statement.setObject(2, now.atOffset(java.time.ZoneOffset.UTC));
      statement.setInt(3, limit);
      statement.setString(4, worker);
      statement.setObject(5, now.plusSeconds(10).atOffset(java.time.ZoneOffset.UTC));
      @Nullable ResultSet acquiredRows = statement.executeQuery();
      @Nullable Throwable rowFailure = null;
      try {
        ResultSet result = required(acquiredRows);
        List<ClaimedWebLog> rows = new ArrayList<>();
        while (result.next()) {
          rows.add(read(result));
        }
        rows.sort(
            Comparator.comparing(ClaimedWebLog::nextAttemptAt)
                .thenComparingLong(ClaimedWebLog::id));
        return List.copyOf(rows);
      } catch (Throwable failure) {
        rowFailure = failure;
        throw failure;
      } finally {
        closeRows(acquiredRows, rowFailure);
      }
    } catch (Throwable failure) {
      statementFailure = failure;
      throw failure;
    } finally {
      closeStatement(acquiredStatement, statementFailure);
    }
  }

  /** Records the observed JMS confirmation only if this worker still owns the row. */
  public boolean markSent(Connection connection, ClaimedWebLog row, Instant confirmedAt)
      throws SQLException {
    requireTransaction(connection);
    Objects.requireNonNull(row, "row");
    Objects.requireNonNull(confirmedAt, "confirmedAt");
    @Nullable PreparedStatement acquiredStatement =
        connection.prepareStatement(
            "update schubert_web_session.web_log_outbox set status='SENT',sent_at=?,"
                + "lease_owner=null,lease_until=null,last_error_code=null "
                + "where id=? and lease_owner=? and status in ('PENDING','ERROR')");
    @Nullable Throwable statementFailure = null;
    try {
      PreparedStatement statement = required(acquiredStatement);
      statement.setObject(1, confirmedAt.atOffset(java.time.ZoneOffset.UTC));
      statement.setLong(2, row.id());
      statement.setString(3, row.leaseOwner());
      return statement.executeUpdate() == 1;
    } catch (Throwable failure) {
      statementFailure = failure;
      throw failure;
    } finally {
      closeStatement(acquiredStatement, statementFailure);
    }
  }

  /** Keeps failed events indefinitely retryable; only bounded internal error codes are stored. */
  public boolean markFailure(
      Connection connection, ClaimedWebLog row, Instant failedAt, String errorCode)
      throws SQLException {
    requireTransaction(connection);
    Objects.requireNonNull(row, "row");
    Objects.requireNonNull(failedAt, "failedAt");
    Objects.requireNonNull(errorCode, "errorCode");
    if (!errorCode.matches("[A-Z0-9_]{1,64}")) {
      throw new IllegalArgumentException("web log error code is invalid");
    }
    int attempt = Math.min(100, row.attemptCount() + 1);
    int jitter = jitterPermille.getAsInt();
    if (jitter < -100 || jitter > 100) {
      throw new IllegalArgumentException("web log retry jitter is outside +/-10 percent");
    }
    long baseMillis =
        switch (attempt) {
          case 1 -> 1_000L;
          case 2 -> 5_000L;
          case 3 -> 30_000L;
          case 4 -> 60_000L;
          default -> 300_000L;
        };
    Instant due = failedAt.plusMillis(baseMillis + baseMillis * jitter / 1_000);
    @Nullable PreparedStatement acquiredStatement =
        connection.prepareStatement(
            "update schubert_web_session.web_log_outbox set status='ERROR',attempt_count=?,"
                + "next_attempt_at=?,sent_at=null,lease_owner=null,lease_until=null,last_error_code=? "
                + "where id=? and lease_owner=? and attempt_count=? and status in ('PENDING','ERROR')");
    @Nullable Throwable statementFailure = null;
    try {
      PreparedStatement statement = required(acquiredStatement);
      statement.setInt(1, attempt);
      statement.setObject(2, due.atOffset(java.time.ZoneOffset.UTC));
      statement.setString(3, errorCode);
      statement.setLong(4, row.id());
      statement.setString(5, row.leaseOwner());
      statement.setInt(6, row.attemptCount());
      return statement.executeUpdate() == 1;
    } catch (Throwable failure) {
      statementFailure = failure;
      throw failure;
    } finally {
      closeStatement(acquiredStatement, statementFailure);
    }
  }

  // SSC-472: preserve the exact try-with-resources primary and suppression rules.
  private static void closeRows(@WillClose @Nullable ResultSet rows, @Nullable Throwable primary)
      throws SQLException {
    if (rows == null) return;
    try {
      rows.close();
    } catch (Throwable secondary) {
      if (primary == null) throw secondary;
      primary.addSuppressed(secondary);
    }
  }

  private static void closeStatement(
      @WillClose @Nullable PreparedStatement statement, @Nullable Throwable primary)
      throws SQLException {
    if (statement == null) return;
    try {
      statement.close();
    } catch (Throwable secondary) {
      if (primary == null) throw secondary;
      primary.addSuppressed(secondary);
    }
  }

  static ClaimedWebLog read(ResultSet result) throws SQLException {
    if (!"WLGEVT01".equals(result.getString("layout_id"))
        || !"001".equals(result.getString("layout_version"))) {
      throw new SQLDataException("web log stored layout is invalid", "22000");
    }
    return new ClaimedWebLog(
        required(result.getObject("id", Long.class)),
        new WebLogPayloadIdentity(
            required(result.getObject("message_id", UUID.class)),
            required(result.getObject("correlation_id", UUID.class))),
        new EncryptedWebLogPayload(
            required(result.getString("key_version")),
            required(result.getBytes("payload_ciphertext"))),
        required(result.getObject("attempt_count", Integer.class)),
        required(result.getObject("next_attempt_at", java.time.OffsetDateTime.class)).toInstant(),
        required(result.getObject("created_at", java.time.OffsetDateTime.class)).toInstant(),
        required(result.getString("lease_owner")),
        required(result.getObject("lease_until", java.time.OffsetDateTime.class)).toInstant());
  }

  private static <T> T required(@Nullable T value) throws SQLDataException {
    if (value == null) {
      throw new SQLDataException("web log required database value is missing", "22004");
    }
    return value;
  }

  private static void requireTransaction(Connection connection) throws SQLException {
    Objects.requireNonNull(connection, "connection");
    if (connection.getAutoCommit()) {
      throw new IllegalStateException("web log outbox requires a caller-owned transaction");
    }
  }
}
