package dev.codex.schubert.nk.api.security;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.api.database.JdbcResourceCleanup;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.net.InetAddress;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.Nullable;

/**
 * Logout-specific verification and authorized administrative revocation. Caller owns transaction.
 * NK-AUT-001; AUT-001..004/MON-004; UI226/234; SS312 §4.2/314 §6.3/352 §12; SSC-010/011,
 * PT-AUT-008-R01..04. No active principal is produced by the Logout path.
 */
public final class AuthSessionRevocationService {
  private static final int EXPECTED_AFFECTED_ROWS = 1;

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
      Optional<InetAddress> client,
      UUID messageId,
      UUID correlationId,
      Instant now) {
    Objects.requireNonNull(raw, "raw");
    Instant at = arguments(connection, client, messageId, correlationId, now);
    return logoutCurrent(
        connection, raw, client, messageId, correlationId, Clock.fixed(at, ZoneOffset.UTC));
  }

  /**
   * PG-D358/QA050/SS314: clock is sampled after User/session locks; caller owns atomic Inbox TX.
   */
  public RevokedContext logoutCurrent(
      Connection connection,
      AuthenticationContext raw,
      Optional<InetAddress> client,
      UUID messageId,
      UUID correlationId,
      Clock clock) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(raw, "raw");
    Objects.requireNonNull(client, "client");
    Objects.requireNonNull(messageId, "messageId");
    Objects.requireNonNull(correlationId, "correlationId");
    Objects.requireNonNull(clock, "clock");
    try {
      requireTransaction(connection);
      String hash = hashes.calculate(raw);
      {
        var statement =
            requireValue(
                connection.prepareStatement(
                    "select u.id from schubert.app_users u join schubert.auth_sessions s on s.user_id=u.id "
                        + "where s.context_hash=? for update of u"));
        @Nullable Throwable jdbcFailure1 = null;
        try {
          statement.setString(1, hash);
          {
            var row = requireValue(statement.executeQuery());
            @Nullable Throwable jdbcFailure2 = null;
            try {
              if (!row.next()) throw new AuthenticationContextException();
            } catch (SQLException | RuntimeException | Error failure) {
              jdbcFailure2 = failure;
              throw failure;
            } finally {
              JdbcResourceCleanup.closeRows(jdbcFailure2, row);
            }
          }
        } catch (SQLException | RuntimeException | Error failure) {
          jdbcFailure1 = failure;
          throw failure;
        } finally {
          JdbcResourceCleanup.closeStatement(jdbcFailure1, statement);
        }
      }
      AuthContextIdentity identity;
      Instant at;
      Instant revokedAt;
      ResultCode result;
      {
        var statement =
            requireValue(
                connection.prepareStatement(
                    "select s.id,s.user_id,s.revoked,s.revoked_at,s.expires_at,u.status "
                        + "from schubert.auth_sessions s join schubert.app_users u on u.id=s.user_id "
                        + "where s.context_hash=? for update of s"));
        @Nullable Throwable jdbcFailure3 = null;
        try {
          statement.setString(1, hash);
          {
            var row = requireValue(statement.executeQuery());
            @Nullable Throwable jdbcFailure4 = null;
            try {
              if (!row.next()) throw new AuthenticationContextException();
              at = clock.instant().truncatedTo(ChronoUnit.MICROS);
              identity =
                  new AuthContextIdentity(
                      requireValue(row.getObject("id", UUID.class)),
                      requireValue(row.getObject("user_id", Long.class)));
              boolean revoked = requireValue(row.getObject("revoked", Boolean.class));
              if (revoked) {
                revokedAt =
                    requireValue(row.getObject("revoked_at", java.time.OffsetDateTime.class))
                        .toInstant();
                result = ResultCode.IDEMPOTENT_SUCCESS;
              } else {
                Instant expiry =
                    requireValue(row.getObject("expires_at", java.time.OffsetDateTime.class))
                        .toInstant();
                String status = requireValue(row.getString("status"));
                if (!expiry.isAfter(at)) {
                  update(connection, identity.sessionId(), at, SessionRevocationReason.EXPIRED);
                  audit.write(
                      connection,
                      identity.userId(),
                      identity.userId(),
                      client,
                      messageId,
                      correlationId,
                      at,
                      SessionRevocationReason.EXPIRED,
                      ResultCode.SESSION_INVALID);
                  throw new AuthenticationContextException();
                }
                if (!status.equals("ACTIVE")) throw new AuthenticationContextException();
                revokedAt = at;
                result = ResultCode.SUCCESS;
              }
            } catch (SQLException | RuntimeException | Error failure) {
              jdbcFailure4 = failure;
              throw failure;
            } finally {
              JdbcResourceCleanup.closeRows(jdbcFailure4, row);
            }
          }
        } catch (SQLException | RuntimeException | Error failure) {
          jdbcFailure3 = failure;
          throw failure;
        } finally {
          JdbcResourceCleanup.closeStatement(jdbcFailure3, statement);
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
    } catch (SQLException | IllegalArgumentException | java.time.DateTimeException failure) {
      AuthenticationInfrastructureException.preserveFatal(failure);
      throw new AuthenticationInfrastructureException();
    } catch (AuthenticationContextException failure) {
      AuthenticationInfrastructureException.preserveFatal(failure);
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
      Optional<InetAddress> client,
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
      {
        var statement =
            requireValue(
                connection.prepareStatement(
                    "select id from schubert.app_users where id=? for update"));
        @Nullable Throwable jdbcFailure5 = null;
        try {
          statement.setLong(1, targetUserId);
          {
            var row = requireValue(statement.executeQuery());
            @Nullable Throwable jdbcFailure6 = null;
            try {
              if (!row.next()) throw new AuthorizationException(ResultCode.NOT_FOUND);
            } catch (SQLException | RuntimeException | Error failure) {
              jdbcFailure6 = failure;
              throw failure;
            } finally {
              JdbcResourceCleanup.closeRows(jdbcFailure6, row);
            }
          }
        } catch (SQLException | RuntimeException | Error failure) {
          jdbcFailure5 = failure;
          throw failure;
        } finally {
          JdbcResourceCleanup.closeStatement(jdbcFailure5, statement);
        }
      }
      var ids = new ArrayList<UUID>();
      {
        var statement =
            requireValue(
                connection.prepareStatement(
                    "select id from schubert.auth_sessions where user_id=? and not revoked order by id for update"));
        @Nullable Throwable jdbcFailure7 = null;
        try {
          statement.setLong(1, targetUserId);
          {
            var row = requireValue(statement.executeQuery());
            @Nullable Throwable jdbcFailure8 = null;
            try {
              while (row.next()) ids.add(requireValue(row.getObject("id", UUID.class)));
            } catch (SQLException | RuntimeException | Error failure) {
              jdbcFailure8 = failure;
              throw failure;
            } finally {
              JdbcResourceCleanup.closeRows(jdbcFailure8, row);
            }
          }
        } catch (SQLException | RuntimeException | Error failure) {
          jdbcFailure7 = failure;
          throw failure;
        } finally {
          JdbcResourceCleanup.closeStatement(jdbcFailure7, statement);
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
      AuthenticationInfrastructureException.preserveFatal(failure);
      throw new AuthenticationInfrastructureException();
    } catch (AuthorizationException failure) {
      AuthenticationInfrastructureException.preserveFatal(failure);
      if (failure.getSuppressed().length != 0) throw new AuthenticationInfrastructureException();
      throw new AuthorizationException(ResultCode.NOT_FOUND);
    }
  }

  private static Instant arguments(
      Connection connection,
      Optional<InetAddress> client,
      UUID message,
      UUID correlation,
      Instant now) {
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
    {
      var statement =
          requireValue(
              connection.prepareStatement(
                  "update schubert.auth_sessions set revoked=true,revoked_at=?,revoke_reason=? where id=? and not revoked"));
      @Nullable Throwable jdbcFailure9 = null;
      try {
        statement.setObject(1, at.atOffset(java.time.ZoneOffset.UTC));
        statement.setString(2, reason.name());
        statement.setObject(3, id);
        if (statement.executeUpdate() != EXPECTED_AFFECTED_ROWS)
          throw new SQLException("session changed during revocation", "40001");
      } catch (SQLException | RuntimeException | Error failure) {
        jdbcFailure9 = failure;
        throw failure;
      } finally {
        JdbcResourceCleanup.closeStatement(jdbcFailure9, statement);
      }
    }
  }
}
