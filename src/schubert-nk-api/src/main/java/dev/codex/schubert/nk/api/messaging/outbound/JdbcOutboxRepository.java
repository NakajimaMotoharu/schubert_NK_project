package dev.codex.schubert.nk.api.messaging.outbound;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ThreadLocalRandom;
import java.util.function.IntSupplier;
import javax.annotation.WillClose;
import org.jspecify.annotations.Nullable;

/**
 * PostgreSQL application-outbox repository using SS 332's SKIP LOCKED claim contract.
 *
 * <p>Every method requires a caller-owned transaction and never commits or rolls it back. Trace:
 * NK-MSG-002; RD ASY-001/MQ-006; UI 213/241/242; SS 324 section 8 and 332 section 7.
 */
public final class JdbcOutboxRepository {
  private final IntSupplier jitterPermille;

  /** Uses independently sampled application retry jitter in the inclusive range ±10%. */
  public JdbcOutboxRepository() {
    this(() -> ThreadLocalRandom.current().nextInt(-100, 101));
  }

  /** Injects retry jitter in permille for deterministic scheduling tests (SS 332 §7.2). */
  public JdbcOutboxRepository(IntSupplier jitterPermille) {
    this.jitterPermille = Objects.requireNonNull(jitterPermille, "jitterPermille");
  }

  private static final String CLAIM_SQL =
      "with due as (select id from schubert.mq_outbox "
          + "where status in ('PENDING','ERROR') and next_attempt_at<=? "
          + "and (lease_until is null or lease_until<?) order by next_attempt_at,id "
          + "for update skip locked limit ?) update schubert.mq_outbox o "
          + "set lease_owner=?,lease_until=? from due where o.id=due.id "
          + "returning o.id,o.message_id,o.correlation_id,o.destination,o.layout_id,"
          + "o.layout_version,o.body,o.attempt_count,o.next_attempt_at,o.created_at,"
          + "o.lease_owner,o.lease_until,o.dlq_original_message_id,o.dlq_original_transport_id,"
          + "o.dlq_delivery_count,o.dlq_error_code,o.dlq_detected_at";

  public long enqueue(Connection connection, OutboxRequest request) throws SQLException {
    requireTransaction(connection);
    Objects.requireNonNull(request, "request");
    String sql =
        "insert into schubert.mq_outbox(message_id,correlation_id,destination,layout_id,"
            + "layout_version,body,status,attempt_count,next_attempt_at,created_at,"
            + "dlq_original_message_id,dlq_original_transport_id,dlq_delivery_count,dlq_error_code,dlq_detected_at) "
            + "values(?,?,?,?,?,?,'PENDING',0,?,?,?,?,?,?,?) returning id";
    PreparedStatement statement = requireValue(connection.prepareStatement(sql));
    @Nullable Throwable statementFailure = null;
    try {
      statement.setObject(1, request.messageId());
      statement.setObject(2, request.correlationId());
      statement.setString(3, request.destination().address());
      statement.setString(4, request.layoutId());
      statement.setString(5, request.layoutVersion());
      statement.setBytes(6, request.body());
      statement.setObject(7, request.nextAttemptAt().atOffset(java.time.ZoneOffset.UTC));
      statement.setObject(8, request.createdAt().atOffset(java.time.ZoneOffset.UTC));
      if (request.dlqMetadata().isPresent()) {
        OutboxDlqMetadata metadata = request.dlqMetadata().orElseThrow();
        statement.setObject(9, metadata.originalMessageId());
        statement.setString(10, metadata.originalTransportId());
        statement.setInt(11, metadata.deliveryCount());
        statement.setString(12, metadata.errorCode());
        statement.setObject(13, metadata.detectedAt().atOffset(java.time.ZoneOffset.UTC));
      } else {
        statement.setNull(9, java.sql.Types.OTHER);
        statement.setNull(10, java.sql.Types.VARCHAR);
        statement.setNull(11, java.sql.Types.INTEGER);
        statement.setNull(12, java.sql.Types.VARCHAR);
        statement.setNull(13, java.sql.Types.TIMESTAMP_WITH_TIMEZONE);
      }
      ResultSet result = requireValue(statement.executeQuery());
      @Nullable Throwable resultFailure = null;
      try {
        if (!result.next()) {
          throw new OutboxIntegrityException("outbox insert returned no identifier");
        }
        // BUG2366/YKT2111: SQL NULL must not become a successful primitive zero.
        return requireValue(result.getObject(1, Long.class));
      } catch (Throwable failure) {
        resultFailure = failure;
        throw failure;
      } finally {
        closeRows(result, resultFailure);
      }
    } catch (Throwable failure) {
      statementFailure = failure;
      throw failure;
    } finally {
      closeStatement(statement, statementFailure);
    }
  }

  public List<OutboxEntry> claim(Connection connection, String leaseOwner, Instant now, int limit)
      throws SQLException {
    requireTransaction(connection);
    String owner = OutboxEntry.requireLeaseOwner(leaseOwner);
    Objects.requireNonNull(now, "now");
    if (limit < 1 || limit > 100) {
      throw new IllegalArgumentException("claim limit must be between 1 and 100");
    }
    Instant leaseUntil = now.plusSeconds(10);
    PreparedStatement statement = requireValue(connection.prepareStatement(CLAIM_SQL));
    @Nullable Throwable statementFailure = null;
    try {
      statement.setObject(1, now.atOffset(java.time.ZoneOffset.UTC));
      statement.setObject(2, now.atOffset(java.time.ZoneOffset.UTC));
      statement.setInt(3, limit);
      statement.setString(4, owner);
      statement.setObject(5, leaseUntil.atOffset(java.time.ZoneOffset.UTC));
      ResultSet result = requireValue(statement.executeQuery());
      @Nullable Throwable resultFailure = null;
      try {
        List<OutboxEntry> entries = new ArrayList<>();
        while (result.next()) {
          entries.add(read(result));
        }
        entries.sort(
            Comparator.comparing(OutboxEntry::nextAttemptAt).thenComparingLong(OutboxEntry::id));
        return List.copyOf(entries);
      } catch (Throwable failure) {
        resultFailure = failure;
        throw failure;
      } finally {
        closeRows(result, resultFailure);
      }
    } catch (Throwable failure) {
      statementFailure = failure;
      throw failure;
    } finally {
      closeStatement(statement, statementFailure);
    }
  }

  public boolean markSent(Connection connection, OutboxEntry entry, Instant sentAt)
      throws SQLException {
    requireTransaction(connection);
    Objects.requireNonNull(entry, "entry");
    Objects.requireNonNull(sentAt, "sentAt");
    String sql =
        "update schubert.mq_outbox set status='SENT',sent_at=?,lease_owner=null,"
            + "lease_until=null,last_error_code=null,last_error_detail=null "
            + "where id=? and lease_owner=? and status in ('PENDING','ERROR')";
    PreparedStatement statement = requireValue(connection.prepareStatement(sql));
    @Nullable Throwable statementFailure = null;
    try {
      statement.setObject(1, sentAt.atOffset(java.time.ZoneOffset.UTC));
      statement.setLong(2, entry.id());
      statement.setString(3, entry.leaseOwner());
      return statement.executeUpdate() == 1;
    } catch (Throwable failure) {
      statementFailure = failure;
      throw failure;
    } finally {
      closeStatement(statement, statementFailure);
    }
  }

  public boolean markFailure(
      Connection connection,
      OutboxEntry entry,
      Instant failedAt,
      String errorCode,
      String errorDetail)
      throws SQLException {
    requireTransaction(connection);
    Objects.requireNonNull(entry, "entry");
    Objects.requireNonNull(failedAt, "failedAt");
    String code = requireError(errorCode, 64, "errorCode");
    String detail = requireError(errorDetail, 256, "errorDetail");
    int nextAttempt = Math.min(entry.attemptCount() + 1, 100);
    Instant dueAt =
        OutboxRetrySchedule.INSTANCE.nextAttemptAt(
            failedAt, nextAttempt, jitterPermille.getAsInt());
    String sql =
        "update schubert.mq_outbox set status='ERROR',attempt_count=?,next_attempt_at=?,"
            + "lease_owner=null,lease_until=null,sent_at=null,last_error_code=?,"
            + "last_error_detail=? where id=? and lease_owner=? and attempt_count=? "
            + "and status in ('PENDING','ERROR')";
    PreparedStatement statement = requireValue(connection.prepareStatement(sql));
    @Nullable Throwable statementFailure = null;
    try {
      statement.setInt(1, nextAttempt);
      statement.setObject(2, dueAt.atOffset(java.time.ZoneOffset.UTC));
      statement.setString(3, code);
      statement.setString(4, detail);
      statement.setLong(5, entry.id());
      statement.setString(6, entry.leaseOwner());
      statement.setInt(7, entry.attemptCount());
      return statement.executeUpdate() == 1;
    } catch (Throwable failure) {
      statementFailure = failure;
      throw failure;
    } finally {
      closeStatement(statement, statementFailure);
    }
  }

  // SSC-471: preserve the exact try-with-resources primary and suppression rules.
  private static void closeRows(@WillClose ResultSet rows, @Nullable Throwable primary)
      throws SQLException {
    try {
      rows.close();
    } catch (Throwable secondary) {
      if (primary == null) throw secondary;
      primary.addSuppressed(secondary);
    }
  }

  private static void closeStatement(
      @WillClose PreparedStatement statement, @Nullable Throwable primary) throws SQLException {
    try {
      statement.close();
    } catch (Throwable secondary) {
      if (primary == null) throw secondary;
      primary.addSuppressed(secondary);
    }
  }

  static OutboxEntry read(ResultSet result) throws SQLException {
    try {
      return new OutboxEntry(
          result.getLong("id"),
          requireValue(result.getObject("message_id", UUID.class)),
          requireValue(result.getObject("correlation_id", UUID.class)),
          OutboxDestination.fromAddress(requireValue(result.getString("destination"))),
          requireValue(result.getString("layout_id")),
          requireValue(result.getString("layout_version")),
          requireValue(result.getBytes("body")),
          requireValue(result.getObject("attempt_count", Integer.class)),
          requireValue(result.getObject("next_attempt_at", java.time.OffsetDateTime.class))
              .toInstant(),
          requireValue(result.getObject("created_at", java.time.OffsetDateTime.class)).toInstant(),
          requireValue(result.getString("lease_owner")),
          requireValue(result.getObject("lease_until", java.time.OffsetDateTime.class)).toInstant(),
          readDlqMetadata(result));
    } catch (IllegalArgumentException exception) {
      throw new OutboxIntegrityException(
          "outbox row violates its bounded storage contract", exception);
    }
  }

  private static Optional<OutboxDlqMetadata> readDlqMetadata(ResultSet result) throws SQLException {
    UUID original = result.getObject("dlq_original_message_id", UUID.class);
    if (original == null) {
      if (result.getObject("dlq_original_transport_id") != null
          || result.getObject("dlq_delivery_count") != null
          || result.getObject("dlq_error_code") != null
          || result.getObject("dlq_detected_at") != null)
        throw new OutboxIntegrityException("outbox DLQ metadata is incomplete");
      return Optional.empty();
    }
    return Optional.of(
        new OutboxDlqMetadata(
            original,
            requireValue(result.getString("dlq_original_transport_id")),
            requireValue(result.getObject("dlq_delivery_count", Integer.class)),
            requireValue(result.getString("dlq_error_code")),
            requireValue(result.getObject("dlq_detected_at", java.time.OffsetDateTime.class))
                .toInstant()));
  }

  private static void requireTransaction(Connection connection) throws SQLException {
    Objects.requireNonNull(connection, "connection");
    if (connection.getAutoCommit()) {
      throw new IllegalStateException("outbox repository requires a caller-owned transaction");
    }
  }

  private static String requireError(String value, int maximum, String name) {
    Objects.requireNonNull(value, name);
    if (value.isBlank()
        || value.length() > maximum
        || value.chars().anyMatch(Character::isISOControl)) {
      throw new IllegalArgumentException(name + " is outside its bounded redacted contract");
    }
    return value;
  }
}
