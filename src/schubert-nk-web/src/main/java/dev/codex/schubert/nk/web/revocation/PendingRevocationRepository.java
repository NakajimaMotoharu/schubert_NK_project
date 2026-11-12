package dev.codex.schubert.nk.web.revocation;

import dev.codex.schubert.nk.web.session.SessionStoreException;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.DateTimeException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.Nullable;

/**
 * Ciphertext-only caller-owned short SQL transaction. Never business DB, remote I/O or expiry GC.
 * NK-WEB-002/AUT004/UI226234/SS314331332/QA050/SSC171/PG-D360/RERUN004005. Initial API failure is
 * not a retry; enqueue schedules 5s, failures schedule 30s/300s/900s forever.
 */
public final class PendingRevocationRepository {
  private static final int EXPECTED_INSERT_ROWS = 1;
  private static final int MAXIMUM_LOADED_CIPHERTEXT_BYTES = 116;
  private static final int MINIMUM_STORED_CIPHERTEXT_BYTES = 29;

  public void enqueue(
      Connection connection,
      RevocationPayloadIdentity identity,
      EncryptedRevocationPayload payload,
      @Nullable Instant expiresAt,
      RevocationFailureCode failure)
      throws SQLException {
    transaction(connection);
    Objects.requireNonNull(identity, "revocation identity");
    Objects.requireNonNull(payload, "revocation payload");
    Objects.requireNonNull(failure, "revocation warning");
    if (expiresAt != null) {
      microseconds(expiresAt);
      if (!expiresAt.isAfter(identity.requestedAt()))
        throw new IllegalArgumentException("known revocation expiry is invalid");
    }
    Instant due = identity.requestedAt().plusSeconds(5);
    try (var statement =
        connection.prepareStatement(
            "insert into schubert_web_session.pending_context_revocations "
                + "(id,context_ciphertext,key_version,requested_at,attempt_count,next_attempt_at,expires_at,last_error_code) "
                + "values(?,?,?,?,0,?,?,?)")) {
      required(statement);
      statement.setObject(1, identity.id());
      statement.setBytes(2, payload.ciphertext());
      statement.setString(3, payload.keyVersion());
      statement.setObject(4, identity.requestedAt().atOffset(ZoneOffset.UTC));
      statement.setObject(5, due.atOffset(ZoneOffset.UTC));
      statement.setObject(6, expiresAt == null ? null : expiresAt.atOffset(ZoneOffset.UTC));
      statement.setString(7, failure.name());
      if (statement.executeUpdate() != EXPECTED_INSERT_ROWS)
        throw new SQLDataException("revocation insert not established", "22000");
    }
  }

  /** Unique lease UUID per invocation; commit and close before calling the remote service. */
  public List<ClaimedRevocation> claim(
      Connection connection, UUID leaseOwner, Instant now, Instant leaseUntil, int limit)
      throws SQLException {
    transaction(connection);
    Objects.requireNonNull(leaseOwner, "revocation lease");
    microseconds(now);
    microseconds(leaseUntil);
    if (limit < 1 || limit > 100 || !leaseUntil.isAfter(now))
      throw new IllegalArgumentException("revocation claim bound is invalid");
    try (var statement =
        connection.prepareStatement(
            "with due as (select id from schubert_web_session.pending_context_revocations "
                + "where next_attempt_at<=? and (lease_until is null or lease_until<=?) "
                + "order by next_attempt_at,requested_at,id for update skip locked limit ?) "
                + "update schubert_web_session.pending_context_revocations p set lease_owner=?,lease_until=? "
                + "from due where p.id=due.id returning p.id,octet_length(p.context_ciphertext) as ciphertext_length,"
                + "case when octet_length(p.context_ciphertext)<=116 then p.context_ciphertext else null end as context_ciphertext,"
                + "p.key_version,p.requested_at,"
                + "p.attempt_count,p.expires_at,p.lease_owner,p.lease_until")) {
      required(statement);
      statement.setObject(1, now.atOffset(ZoneOffset.UTC));
      statement.setObject(2, now.atOffset(ZoneOffset.UTC));
      statement.setInt(3, limit);
      statement.setString(4, leaseOwner.toString());
      statement.setObject(5, leaseUntil.atOffset(ZoneOffset.UTC));
      try (var result = statement.executeQuery()) {
        required(result);
        var rows = new ArrayList<ClaimedRevocation>();
        while (result.next()) rows.add(read(result));
        rows.sort(
            Comparator.comparing((ClaimedRevocation row) -> row.identity().requestedAt())
                .thenComparing(row -> row.identity().id()));
        return List.copyOf(rows);
      }
    }
  }

  public boolean markFailure(
      Connection connection, ClaimedRevocation row, Instant now, RevocationFailureCode failure)
      throws SQLException {
    transaction(connection);
    Objects.requireNonNull(row, "claimed revocation");
    Objects.requireNonNull(failure, "revocation warning");
    microseconds(now);
    if (now.isBefore(row.identity().requestedAt()))
      throw new IllegalArgumentException("revocation retry time is invalid");
    int attempt = Math.min(100, row.attemptCount() + 1);
    long delay =
        switch (attempt) {
          case 1 -> 30;
          case 2 -> 300;
          default -> 900;
        };
    try (var statement =
        connection.prepareStatement(
            "update schubert_web_session.pending_context_revocations set attempt_count=?,next_attempt_at=?,"
                + "last_error_code=?,lease_owner=null,lease_until=null "
                + "where id=? and lease_owner=? and lease_until=? and attempt_count=? and lease_until>?")) {
      required(statement);
      statement.setInt(1, attempt);
      statement.setObject(2, now.plusSeconds(delay).atOffset(ZoneOffset.UTC));
      statement.setString(3, failure.name());
      bindLease(statement, 4, row, now);
      return statement.executeUpdate() == 1;
    }
  }

  /** Package-only trusted coordinator calls this after genuine matching 0000/0200, never 0102. */
  boolean removeConfirmed(Connection connection, ClaimedRevocation row, Instant now)
      throws SQLException {
    transaction(connection);
    Objects.requireNonNull(row, "claimed revocation");
    microseconds(now);
    try (var statement =
        connection.prepareStatement(
            "delete from schubert_web_session.pending_context_revocations "
                + "where id=? and lease_owner=? and lease_until=? and attempt_count=? and lease_until>?")) {
      required(statement);
      bindLease(statement, 1, row, now);
      return statement.executeUpdate() == 1;
    }
  }

  private static void bindLease(
      java.sql.PreparedStatement statement, int first, ClaimedRevocation row, Instant now)
      throws SQLException {
    statement.setObject(first, row.identity().id());
    statement.setString(first + 1, row.leaseOwner().toString());
    statement.setObject(first + 2, row.leaseUntil().atOffset(ZoneOffset.UTC));
    statement.setInt(first + 3, row.attemptCount());
    statement.setObject(first + 4, now.atOffset(ZoneOffset.UTC));
  }

  private static ClaimedRevocation read(ResultSet result) throws SQLException {
    try {
      OffsetDateTime expiry = result.getObject("expires_at", OffsetDateTime.class);
      String lease = required(result.getString("lease_owner"));
      UUID owner = UUID.fromString(lease);
      if (!owner.toString().equals(lease)) throw new IllegalArgumentException("invalid lease");
      String keyVersion = required(result.getString("key_version"));
      int size = required(result.getObject("ciphertext_length", Integer.class));
      if (size < MINIMUM_STORED_CIPHERTEXT_BYTES)
        throw new IllegalArgumentException("invalid stored ciphertext length");
      @Nullable EncryptedRevocationPayload payload = null;
      if (size <= MAXIMUM_LOADED_CIPHERTEXT_BYTES) {
        byte[] stored = required(result.getBytes("context_ciphertext"));
        if (stored.length != size)
          throw new IllegalArgumentException("invalid stored ciphertext size");
        payload = new EncryptedRevocationPayload(keyVersion, stored);
      }
      return new ClaimedRevocation(
          new RevocationPayloadIdentity(
              required(result.getObject("id", UUID.class)),
              required(result.getObject("requested_at", OffsetDateTime.class)).toInstant()),
          payload,
          required(result.getObject("attempt_count", Integer.class)),
          expiry == null ? null : expiry.toInstant(),
          owner,
          required(result.getObject("lease_until", OffsetDateTime.class)).toInstant(),
          keyVersion);
    } catch (IllegalArgumentException | DateTimeException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new SQLDataException("stored revocation metadata is invalid", "22000");
    }
  }

  static void microseconds(Instant value) {
    Objects.requireNonNull(value, "revocation time");
    if (value.getNano() % 1000 != 0)
      throw new IllegalArgumentException("revocation time must fit database microseconds");
  }

  private static void transaction(Connection connection) throws SQLException {
    Objects.requireNonNull(connection, "revocation connection");
    if (connection.getAutoCommit())
      throw new IllegalStateException("revocation SQL requires caller transaction");
  }

  private static <T> T required(@Nullable T value) throws SQLDataException {
    if (value == null) throw new SQLDataException("required revocation SQL value absent", "22000");
    return value;
  }
}
