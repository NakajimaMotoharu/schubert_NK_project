package dev.codex.schubert.nk.api.security;

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.net.InetAddress;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Objects;
import java.util.UUID;

/**
 * Logout-specific verification and authorized administrative revocation. Caller owns transaction.
 * NK-AUT-001; AUT-001..004/MON-004; UI226/234; SS312 §4.2/314 §6.3/352 §12; SSC-010/011,
 * PT-AUT-008-R01..04. No active principal is produced by the Logout path.
 */
public final class AuthSessionRevocationService {
  private final ContextHash hashes;
  private final SessionAuditWriter audit = new SessionAuditWriter();

  public AuthSessionRevocationService(ContextHash hashes) {
    this.hashes = Objects.requireNonNull(hashes, "hashes");
  }

  /**
   * An Inbox NEW Logout request; repeated context is idempotent, repeated message uses Inbox
   * replay.
   */
  public RevokedContext logout(
      Connection connection,
      AuthenticationContext raw,
      InetAddress client,
      UUID messageId,
      UUID correlationId,
      Instant now) {
    Objects.requireNonNull(raw, "raw");
    Instant at = arguments(connection, client, messageId, correlationId, now);
    try {
      requireTransaction(connection);
      String hash = hashes.calculate(raw);
      try (var statement =
          connection.prepareStatement(
              "select u.id from schubert.app_users u join schubert.auth_sessions s on s.user_id=u.id "
                  + "where s.context_hash=? for update of u")) {
        statement.setString(1, hash);
        try (var row = statement.executeQuery()) {
          if (!row.next()) throw new AuthenticationContextException();
        }
      }
      AuthContextIdentity identity;
      Instant revokedAt;
      ResultCode result;
      try (var statement =
          connection.prepareStatement(
              "select s.id,s.user_id,s.revoked,s.revoked_at,s.expires_at,u.status "
                  + "from schubert.auth_sessions s join schubert.app_users u on u.id=s.user_id "
                  + "where s.context_hash=? for update of s")) {
        statement.setString(1, hash);
        try (var row = statement.executeQuery()) {
          if (!row.next()) throw new AuthenticationContextException();
          identity =
              new AuthContextIdentity(
                  requireValue(row.getObject("id", UUID.class)),
                  requireValue(row.getObject("user_id", Long.class)));
          boolean revoked = requireValue(row.getObject("revoked", Boolean.class));
          if (revoked) {
            revokedAt = requireValue(row.getTimestamp("revoked_at")).toInstant();
            result = ResultCode.IDEMPOTENT_SUCCESS;
          } else {
            Instant expiry = requireValue(row.getTimestamp("expires_at")).toInstant();
            String status = requireValue(row.getString("status"));
            if (!expiry.isAfter(at) || !status.equals("ACTIVE"))
              throw new AuthenticationContextException();
            revokedAt = at;
            result = ResultCode.SUCCESS;
          }
        }
      }
      if (result == ResultCode.SUCCESS)
        update(connection, identity.sessionId(), at, SessionRevocationReason.LOGOUT);
      audit.write(
          connection,
          identity.userId(),
          identity.userId(),
          client,
          messageId,
          correlationId,
          at,
          SessionRevocationReason.LOGOUT,
          result);
      return new RevokedContext(identity, revokedAt, result);
    } catch (SQLException | IllegalArgumentException failure) {
      throw new AuthenticationInfrastructureException();
    } catch (AuthenticationContextException failure) {
      if (failure.getSuppressed().length != 0) throw new AuthenticationInfrastructureException();
      throw new AuthenticationContextException();
    }
  }

  /**
   * Caller supplies a DB-authenticated ADMIN, not a wire role, and commits the account change
   * together.
   */
  public int revokeAll(
      Connection connection,
      AuthenticatedActor administrator,
      long targetUserId,
      SessionRevocationReason reason,
      InetAddress client,
      UUID messageId,
      UUID correlationId,
      Instant now) {
    new AuthorizationService().requireAdmin(administrator);
    Objects.requireNonNull(reason, "reason");
    if (targetUserId < 1 || targetUserId > 999_999_999_999L)
      throw new IllegalArgumentException("revocation target is outside N12");
    if (reason != SessionRevocationReason.DISABLED
        && reason != SessionRevocationReason.PASSWORD_RESET
        && reason != SessionRevocationReason.ADMIN)
      throw new IllegalArgumentException("invalid administrative revocation reason");
    Instant at = arguments(connection, client, messageId, correlationId, now);
    try {
      requireTransaction(connection);
      try (var statement =
          connection.prepareStatement("select id from schubert.app_users where id=? for update")) {
        statement.setLong(1, targetUserId);
        try (var row = statement.executeQuery()) {
          if (!row.next()) throw new AuthorizationException(ResultCode.NOT_FOUND);
        }
      }
      var ids = new ArrayList<UUID>();
      try (var statement =
          connection.prepareStatement(
              "select id from schubert.auth_sessions where user_id=? and not revoked order by id for update")) {
        statement.setLong(1, targetUserId);
        try (var row = statement.executeQuery()) {
          while (row.next()) ids.add(requireValue(row.getObject("id", UUID.class)));
        }
      }
      for (UUID id : ids) {
        update(connection, id, at, reason);
        audit.write(
            connection,
            administrator.userId(),
            targetUserId,
            client,
            messageId,
            correlationId,
            at,
            reason,
            ResultCode.SUCCESS);
      }
      return ids.size();
    } catch (SQLException failure) {
      throw new AuthenticationInfrastructureException();
    } catch (AuthorizationException failure) {
      if (failure.getSuppressed().length != 0) throw new AuthenticationInfrastructureException();
      throw new AuthorizationException(ResultCode.NOT_FOUND);
    }
  }

  private static Instant arguments(
      Connection connection, InetAddress client, UUID message, UUID correlation, Instant now) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(client, "client");
    Objects.requireNonNull(message, "message");
    Objects.requireNonNull(correlation, "correlation");
    return Objects.requireNonNull(now, "now").truncatedTo(ChronoUnit.MICROS);
  }

  private static void requireTransaction(Connection connection) throws SQLException {
    if (connection.getAutoCommit())
      throw new SQLException("revocation requires explicit transaction", "25000");
  }

  private static void update(
      Connection connection, UUID id, Instant at, SessionRevocationReason reason)
      throws SQLException {
    try (var statement =
        connection.prepareStatement(
            "update schubert.auth_sessions set revoked=true,revoked_at=?,revoke_reason=? where id=? and not revoked")) {
      statement.setTimestamp(1, Timestamp.from(at));
      statement.setString(2, reason.name());
      statement.setObject(3, id);
      if (statement.executeUpdate() != 1)
        throw new SQLException("session changed during revocation", "40001");
    }
  }
}
