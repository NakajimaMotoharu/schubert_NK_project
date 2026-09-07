package dev.codex.schubert.nk.api.messaging.outbound;

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.ThreadLocalRandom;
import java.util.function.IntSupplier;

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
          + "o.lease_owner,o.lease_until";

  public long enqueue(Connection connection, OutboxRequest request) throws SQLException {
    requireTransaction(connection);
    Objects.requireNonNull(request, "request");
    String sql =
        "insert into schubert.mq_outbox(message_id,correlation_id,destination,layout_id,"
            + "layout_version,body,status,attempt_count,next_attempt_at,created_at) "
            + "values(?,?,?,?,?,?,'PENDING',0,?,?) returning id";
    try (PreparedStatement statement = connection.prepareStatement(sql)) {
      statement.setObject(1, request.messageId());
      statement.setObject(2, request.correlationId());
      statement.setString(3, request.destination().address());
      statement.setString(4, request.layoutId());
      statement.setString(5, request.layoutVersion());
      statement.setBytes(6, request.body());
      statement.setTimestamp(7, Timestamp.from(request.nextAttemptAt()));
      statement.setTimestamp(8, Timestamp.from(request.createdAt()));
      try (ResultSet result = statement.executeQuery()) {
        if (!result.next()) {
          throw new OutboxIntegrityException("outbox insert returned no identifier");
        }
        return result.getLong(1);
      }
    }
  }

  public List<OutboxEntry> claim(
      Connection connection, String leaseOwner, Instant now, int limit) throws SQLException {
    requireTransaction(connection);
    String owner = OutboxEntry.requireLeaseOwner(leaseOwner);
    Objects.requireNonNull(now, "now");
    if (limit < 1 || limit > 100) {
      throw new IllegalArgumentException("claim limit must be between 1 and 100");
    }
    Instant leaseUntil = now.plusSeconds(10);
    try (PreparedStatement statement = connection.prepareStatement(CLAIM_SQL)) {
      statement.setTimestamp(1, Timestamp.from(now));
      statement.setTimestamp(2, Timestamp.from(now));
      statement.setInt(3, limit);
      statement.setString(4, owner);
      statement.setTimestamp(5, Timestamp.from(leaseUntil));
      try (ResultSet result = statement.executeQuery()) {
        List<OutboxEntry> entries = new ArrayList<>();
        while (result.next()) {
          entries.add(read(result));
        }
        entries.sort(
            Comparator.comparing(OutboxEntry::nextAttemptAt).thenComparingLong(OutboxEntry::id));
        return List.copyOf(entries);
      }
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
    try (PreparedStatement statement = connection.prepareStatement(sql)) {
      statement.setTimestamp(1, Timestamp.from(sentAt));
      statement.setLong(2, entry.id());
      statement.setString(3, entry.leaseOwner());
      return statement.executeUpdate() == 1;
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
    try (PreparedStatement statement = connection.prepareStatement(sql)) {
      statement.setInt(1, nextAttempt);
      statement.setTimestamp(2, Timestamp.from(dueAt));
      statement.setString(3, code);
      statement.setString(4, detail);
      statement.setLong(5, entry.id());
      statement.setString(6, entry.leaseOwner());
      statement.setInt(7, entry.attemptCount());
      return statement.executeUpdate() == 1;
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
          result.getInt("attempt_count"),
          requireValue(result.getTimestamp("next_attempt_at")).toInstant(),
          requireValue(result.getTimestamp("created_at")).toInstant(),
          requireValue(result.getString("lease_owner")),
          requireValue(result.getTimestamp("lease_until")).toInstant());
    } catch (IllegalArgumentException exception) {
      throw new OutboxIntegrityException(
          "outbox row violates its bounded storage contract", exception);
    }
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
