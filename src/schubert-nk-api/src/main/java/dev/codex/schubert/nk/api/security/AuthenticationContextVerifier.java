package dev.codex.schubert.nk.api.security;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Objects;
import java.util.UUID;

/**
 * DB-authoritative context verification in a caller-owned transaction, with User -> session locks.
 * Trace: NK-AUT-001, AUT-001..004/MQ-004; UI226 §5..7; SS312 §3/314 §6/332 §5; PT-AUT-007.
 */
public final class AuthenticationContextVerifier {
  private static final String LOCK_USER =
      "select u.id from schubert.app_users u join schubert.auth_sessions s on s.user_id=u.id where"
          + " s.context_hash=? for update of u";
  private static final String READ_SESSION =
      "select s.id,s.user_id,u.username,u.role,u.status,"
          + "s.revoked,s.expires_at from schubert.auth_sessions s "
          + "join schubert.app_users u on u.id=s.user_id where s.context_hash=?";
  private static final String LOCK_SESSION = READ_SESSION + " for update of s";
  private static final String TOUCH =
      "update schubert.auth_sessions "
          + "set last_accessed_at=greatest(last_accessed_at,?),"
          + "expires_at=greatest(expires_at,cast(? as timestamptz)+interval '8 hours') "
          + "where id=? and not revoked";
  private final ContextHash hashes;

  public AuthenticationContextVerifier(ContextHash hashes) {
    this.hashes = Objects.requireNonNull(hashes, "hashes");
  }

  /** Does not commit/rollback/close the caller connection; caller must rollback on any failure. */
  public AuthenticatedActor verify(Connection connection, AuthenticationContext raw, Instant now) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(raw, "raw");
    Objects.requireNonNull(now, "now");
    try {
      if (connection.getAutoCommit()) {
        throw new SQLException("authentication requires an explicit transaction", "25000");
      }
      String hash = hashes.calculate(raw);
      try (var statement = connection.prepareStatement(LOCK_USER)) {
        statement.setString(1, hash);
        try (ResultSet row = statement.executeQuery()) {
          if (!row.next()) {
            throw new AuthenticationContextException();
          }
        }
      }
      VerifiedSession session = readSession(connection, LOCK_SESSION, hash, now);
      try (var statement = connection.prepareStatement(TOUCH)) {
        statement.setObject(1, now.atOffset(java.time.ZoneOffset.UTC));
        statement.setObject(2, now.atOffset(java.time.ZoneOffset.UTC));
        statement.setObject(3, session.id());
        if (statement.executeUpdate() != 1) {
          throw new SQLException("authentication session changed during verification", "40001");
        }
      }
      return session.actor();
    } catch (SQLException failure) {
      throw new AuthenticationInfrastructureException();
    } catch (AuthenticationContextException failure) {
      // JDBC close errors suppressed by try-with-resources must not carry provider text outward.
      if (failure.getSuppressed().length != 0) {
        throw new AuthenticationInfrastructureException();
      }
      throw new AuthenticationContextException();
    }
  }

  /**
   * Snapshot preflight only: no locks, idle touch or caller transaction ownership. Requires
   * explicit read-only transaction; final write stage must reauthenticate with verify using a fresh
   * time. Trace: NK-AUT-001/NK-SCN-001, AUT-001..004; UI226/237; SS312 §3.3.1/332 §4.2;
   * SSC-023/PT-AUT-007-R01..R04. Not a reusable authorization grant.
   */
  public AuthenticatedActor inspectReadOnly(
      Connection connection, AuthenticationContext raw, Instant now) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(raw, "raw");
    Objects.requireNonNull(now, "now");
    try {
      if (connection.getAutoCommit() || !connection.isReadOnly()) {
        throw new SQLException("authentication preflight requires read-only transaction", "25000");
      }
      return readSession(connection, READ_SESSION, hashes.calculate(raw), now).actor();
    } catch (SQLException failure) {
      throw new AuthenticationInfrastructureException();
    } catch (AuthenticationContextException failure) {
      if (failure.getSuppressed().length != 0) {
        throw new AuthenticationInfrastructureException();
      }
      throw new AuthenticationContextException();
    }
  }

  private static VerifiedSession readSession(
      Connection connection, String sql, String hash, Instant now) throws SQLException {
    try (var statement = connection.prepareStatement(sql)) {
      statement.setString(1, hash);
      try (ResultSet row = statement.executeQuery()) {
        if (!row.next()) {
          throw new AuthenticationContextException();
        }
        boolean revoked = requireValue(row.getObject("revoked", Boolean.class));
        Instant expires =
            requireValue(row.getObject("expires_at", java.time.OffsetDateTime.class)).toInstant();
        String status = requireValue(row.getString("status"));
        if (revoked || !expires.isAfter(now) || !status.equals("ACTIVE")) {
          throw new AuthenticationContextException();
        }
        UUID sessionId = requireValue(row.getObject("id", UUID.class));
        AuthenticatedActor actor =
            new AuthenticatedActor(
                requireValue(row.getObject("user_id", Long.class)),
                requireValue(row.getString("username")),
                readRole(requireValue(row.getString("role"))));
        return new VerifiedSession(sessionId, actor);
      }
    }
  }

  private record VerifiedSession(UUID id, AuthenticatedActor actor) {}

  private static Role readRole(String role) throws SQLException {
    return switch (role) {
      case "USER" -> Role.USER;
      case "ADMIN" -> Role.ADMIN;
      default -> throw new SQLException("invalid persisted authentication role", "22000");
    };
  }
}
