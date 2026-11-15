package dev.codex.schubert.nk.api.security;

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.api.database.JdbcResourceCleanup;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Objects;
import java.util.OptionalLong;
import org.jspecify.annotations.Nullable;

/**
 * Ordered prelude for User mutations, before normal authentication and Inbox. Caller owns the write
 * transaction throughout. NK-ADM-001/NK-AUT-001; FUN-009/AUT-002/003; UI225/226/236; SS312/314/332;
 * SSC-031/PG-D-082/PT-ADM-008..013. Candidate lookup never grants authority.
 */
public final class AdminCommandAuthenticator {
  public enum Mutation {
    CREATE,
    ENABLE,
    DISABLE,
    PROMOTE,
    DEMOTE,
    RESET_PASSWORD,
    UNLOCK;

    boolean reducesMembership() {
      return this == DISABLE || this == DEMOTE;
    }
  }

  private final ContextHash hashes;
  private final AuthenticationContextVerifier authentication;

  public AdminCommandAuthenticator(ContextHash hashes) {
    this.hashes = Objects.requireNonNull(hashes, "hashes");
    authentication = new AuthenticationContextVerifier(hashes);
  }

  /** Returns only the current DB-authenticated ADMIN; caller rolls back any failure. */
  public AuthenticatedActor verify(
      Connection connection,
      AuthenticationContext context,
      Mutation mutation,
      OptionalLong target,
      Instant now) {
    AuthenticatedActor actor = verifyIdentity(connection, context, mutation, target, now);
    new AuthorizationService().requireAdmin(actor);
    return actor;
  }

  /**
   * Latest authenticated identity for caller ADMIN check/critical denial audit, never an ADMIN
   * grant. All SSC-031 locks and normal context verification still precede this return.
   * SSC-034/PG-D-087/PT-ADM-034/036/039. Caller owns transaction and must gate Inbox/commands.
   */
  public AuthenticatedActor verifyIdentity(
      Connection connection,
      AuthenticationContext context,
      Mutation mutation,
      OptionalLong target,
      Instant now) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(context, "context");
    Objects.requireNonNull(mutation, "mutation");
    Objects.requireNonNull(target, "target");
    Objects.requireNonNull(now, "now");
    if ((mutation == Mutation.CREATE) != target.isEmpty())
      throw new IllegalArgumentException("user mutation target presence is invalid");
    if (target.isPresent() && (target.getAsLong() < 1 || target.getAsLong() > 999_999_999_999L))
      throw new IllegalArgumentException("user mutation target is outside N12");
    try {
      require(!connection.getAutoCommit() && !connection.isReadOnly());
      String hash = hashes.calculate(context);
      long candidate = owner(connection, hash, false);
      if (mutation.reducesMembership()) {
        {
          var statement =
              requireValue(connection.prepareStatement("select pg_advisory_xact_lock(71419601)"));
          @Nullable Throwable jdbcFailure1 = null;
          try {
            {
              var row = requireValue(statement.executeQuery());
              @Nullable Throwable jdbcFailure2 = null;
              try {
                require(row.next());
                require(!row.next());
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
      }
      lockUsers(connection, candidate, target.orElse(candidate), mutation.reducesMembership());
      if (owner(connection, hash, true) != candidate) throw new AuthenticationContextException();
      AuthenticatedActor actor = authentication.verify(connection, context, now);
      require(actor.userId() == candidate);
      return actor;
    } catch (AuthenticationContextException failure) {
      AuthenticationInfrastructureException.preserveFatal(failure);
      if (failure.getSuppressed().length != 0) throw new AuthenticationInfrastructureException();
      throw new AuthenticationContextException();
    } catch (SQLException | IllegalArgumentException | java.time.DateTimeException failure) {
      AuthenticationInfrastructureException.preserveFatal(failure);
      throw new AuthenticationInfrastructureException();
    }
  }

  private static long owner(Connection connection, String hash, boolean lock) throws SQLException {
    String sql =
        "select user_id from schubert.auth_sessions where context_hash=?"
            + (lock ? " for update" : "");
    {
      var statement = requireValue(connection.prepareStatement(sql));
      @Nullable Throwable jdbcFailure3 = null;
      try {
        statement.setString(1, hash);
        {
          var row = requireValue(statement.executeQuery());
          @Nullable Throwable jdbcFailure4 = null;
          try {
            if (!row.next()) throw new AuthenticationContextException();
            long id = number(row);
            require(id >= 1 && id <= 999_999_999_999L);
            require(!row.next());
            return id;
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
  }

  private static void lockUsers(
      Connection connection, long candidate, long target, boolean reducing) throws SQLException {
    {
      var statement =
          requireValue(
              connection.prepareStatement(
                  """
        select id from schubert.app_users
         where id=? or id=? or (? and role='ADMIN' and status='ACTIVE')
         order by id for update
        """));
      @Nullable Throwable jdbcFailure5 = null;
      try {
        statement.setLong(1, candidate);
        statement.setLong(2, target);
        statement.setBoolean(3, reducing);
        {
          var rows = requireValue(statement.executeQuery());
          @Nullable Throwable jdbcFailure6 = null;
          try {
            boolean found = false;
            long previous = 0;
            while (rows.next()) {
              long id = number(rows);
              require(id > previous);
              previous = id;
              found |= id == candidate;
            }
            require(found);
          } catch (SQLException | RuntimeException | Error failure) {
            jdbcFailure6 = failure;
            throw failure;
          } finally {
            JdbcResourceCleanup.closeRows(jdbcFailure6, rows);
          }
        }
      } catch (SQLException | RuntimeException | Error failure) {
        jdbcFailure5 = failure;
        throw failure;
      } finally {
        JdbcResourceCleanup.closeStatement(jdbcFailure5, statement);
      }
    }
  }

  private static long number(ResultSet row) throws SQLException {
    long number = row.getLong(1);
    require(!row.wasNull());
    return number;
  }

  private static void require(boolean valid) throws SQLException {
    if (!valid) throw new SQLException("administrative authentication invariant failed");
  }
}
