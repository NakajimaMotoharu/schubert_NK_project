package dev.codex.schubert.nk.api.security;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.api.database.JdbcResourceCleanup;
import dev.codex.schubert.nk.api.domain.Role;
import java.net.InetAddress;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.Nullable;

/**
 * Persisted rate-limit rows, User -> IP lock order and caller transaction only. NK-AUT-001;
 * AUT-001; UI226 §4; SS312 §4/314 §5/331 §4/332 §5; PT-AUT-003-D01..05.
 */
public final class LoginAttemptRepository {
  private static final String ACTIVE_STATUS = "ACTIVE";
  private static final String DISABLED_STATUS = "DISABLED";
  private static final int EXPECTED_AFFECTED_ROWS = 1;

  private static final String USER =
      "select"
          + " id,username,role,status,password_hash,failed_count,failure_window_started_at,locked_until"
          + " from schubert.app_users where username_key=? for update";
  private static final String CREATE_IP =
      "insert into schubert.login_ip_attempts"
          + " (client_address,failed_count,window_started_at,updated_at) values(cast(? as"
          + " inet),0,?,?) on conflict(client_address) do nothing";
  private static final String IP =
      "select failed_count,window_started_at,locked_until from schubert.login_ip_attempts where"
          + " client_address=cast(? as inet) for update";
  private static final String UPDATE_USER =
      "update schubert.app_users set failed_count=?,failure_window_started_at=?,locked_until=?,"
          + "last_login_at=case when ? then ? else last_login_at end where id=?";
  private static final String UPDATE_IP =
      "update schubert.login_ip_attempts set"
          + " failed_count=?,window_started_at=?,locked_until=?,updated_at=? where"
          + " client_address=cast(? as inet)";

  /** Username key has already undergone the UI226 normalization; this layer owns no password. */
  public LockedLoginAttempt lockForAttempt(
      Connection connection, String usernameKey, InetAddress client, Instant now) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(usernameKey, "usernameKey");
    Objects.requireNonNull(client, "client");
    Objects.requireNonNull(now, "now");
    if (usernameKey.isEmpty()
        || !StandardCharsets.UTF_8.newEncoder().canEncode(usernameKey)
        || usernameKey.getBytes(StandardCharsets.UTF_8).length > 96)
      throw new IllegalArgumentException("username key length is invalid");
    try {
      requireTransaction(connection);
      Optional<LoginAccount> account = Optional.empty();
      {
        var statement = requireValue(connection.prepareStatement(USER));
        @Nullable Throwable jdbcFailure1 = null;
        try {
          statement.setString(1, usernameKey);
          {
            var row = requireValue(statement.executeQuery());
            @Nullable Throwable jdbcFailure2 = null;
            try {
              if (row.next()) {
                String persistedRole = requireValue(row.getString("role"));
                Role role;
                if (Role.USER.name().equals(persistedRole)) role = Role.USER;
                else if (Role.ADMIN.name().equals(persistedRole)) role = Role.ADMIN;
                else throw new SQLException("invalid persisted role", "22000");
                String persistedStatus = requireValue(row.getString("status"));
                boolean active;
                if (ACTIVE_STATUS.equals(persistedStatus)) active = true;
                else if (DISABLED_STATUS.equals(persistedStatus)) active = false;
                else throw new SQLException("invalid persisted status", "22000");
                account =
                    Optional.of(
                        new LoginAccount(
                            new AuthenticatedActor(
                                requireValue(row.getObject("id", Long.class)),
                                requireValue(row.getString("username")),
                                role),
                            active,
                            requireValue(row.getString("password_hash")),
                            new LoginAttemptState(
                                LoginAttemptKind.USER,
                                requireValue(row.getObject("failed_count", Integer.class)),
                                optionalInstant(row, "failure_window_started_at"),
                                optionalInstant(row, "locked_until"))));
              }
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
      {
        var statement = requireValue(connection.prepareStatement(CREATE_IP));
        @Nullable Throwable jdbcFailure3 = null;
        try {
          statement.setString(1, client.getHostAddress());
          statement.setObject(2, now.atOffset(java.time.ZoneOffset.UTC));
          statement.setObject(3, now.atOffset(java.time.ZoneOffset.UTC));
          statement.executeUpdate();
        } catch (SQLException | RuntimeException | Error failure) {
          jdbcFailure3 = failure;
          throw failure;
        } finally {
          JdbcResourceCleanup.closeStatement(jdbcFailure3, statement);
        }
      }
      {
        var statement = requireValue(connection.prepareStatement(IP));
        @Nullable Throwable jdbcFailure4 = null;
        try {
          statement.setString(1, client.getHostAddress());
          {
            var row = requireValue(statement.executeQuery());
            @Nullable Throwable jdbcFailure5 = null;
            try {
              if (!row.next()) throw new SQLException("login IP row is missing", "40001");
              var state =
                  new LoginAttemptState(
                      LoginAttemptKind.IP,
                      requireValue(row.getObject("failed_count", Integer.class)),
                      Optional.of(
                          requireValue(
                                  row.getObject(
                                      "window_started_at", java.time.OffsetDateTime.class))
                              .toInstant()),
                      optionalInstant(row, "locked_until"));
              return new LockedLoginAttempt(client.getHostAddress(), account, state);
            } catch (SQLException | RuntimeException | Error failure) {
              jdbcFailure5 = failure;
              throw failure;
            } finally {
              JdbcResourceCleanup.closeRows(jdbcFailure5, row);
            }
          }
        } catch (SQLException | RuntimeException | Error failure) {
          jdbcFailure4 = failure;
          throw failure;
        } finally {
          JdbcResourceCleanup.closeStatement(jdbcFailure4, statement);
        }
      }
    } catch (SQLException | IllegalArgumentException | java.time.DateTimeException failure) {
      AuthenticationInfrastructureException.preserveFatal(failure);
      throw new AuthenticationInfrastructureException();
    }
  }

  /** Use the locked snapshot once before committing; a later attempt must lock/read again. */
  public void recordFailure(Connection connection, LockedLoginAttempt locked, Instant now) {
    record(connection, locked, now, false);
  }

  /** Account/IP counters and Login time are part of the session/Inbox/audit transaction. */
  public void recordSuccess(Connection connection, LockedLoginAttempt locked, Instant now) {
    record(connection, locked, now, true);
  }

  private static void record(
      Connection connection, LockedLoginAttempt locked, Instant now, boolean success) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(locked, "locked");
    Objects.requireNonNull(now, "now");
    try {
      requireTransaction(connection);
      if (locked.account().isPresent()) {
        var account = locked.account().orElseThrow();
        var state =
            success ? account.attempts().afterSuccess() : account.attempts().afterFailure(now);
        {
          var statement = requireValue(connection.prepareStatement(UPDATE_USER));
          @Nullable Throwable jdbcFailure6 = null;
          try {
            statement.setInt(1, state.failedCount());
            setInstant(statement, 2, state.windowStartedAt());
            setInstant(statement, 3, state.lockedUntil());
            statement.setBoolean(4, success);
            statement.setObject(5, now.atOffset(java.time.ZoneOffset.UTC));
            statement.setLong(6, account.identity().userId());
            if (statement.executeUpdate() != EXPECTED_AFFECTED_ROWS)
              throw new SQLException("login user update count differs", "40001");
          } catch (SQLException | RuntimeException | Error failure) {
            jdbcFailure6 = failure;
            throw failure;
          } finally {
            JdbcResourceCleanup.closeStatement(jdbcFailure6, statement);
          }
        }
      }
      var state = success ? locked.ip().afterSuccess() : locked.ip().afterFailure(now);
      {
        var statement = requireValue(connection.prepareStatement(UPDATE_IP));
        @Nullable Throwable jdbcFailure7 = null;
        try {
          statement.setInt(1, state.failedCount());
          statement.setObject(
              2, state.windowStartedAt().orElse(now).atOffset(java.time.ZoneOffset.UTC));
          setInstant(statement, 3, state.lockedUntil());
          statement.setObject(4, now.atOffset(java.time.ZoneOffset.UTC));
          statement.setString(5, locked.clientAddress());
          if (statement.executeUpdate() != EXPECTED_AFFECTED_ROWS)
            throw new SQLException("login IP update count differs", "40001");
        } catch (SQLException | RuntimeException | Error failure) {
          jdbcFailure7 = failure;
          throw failure;
        } finally {
          JdbcResourceCleanup.closeStatement(jdbcFailure7, statement);
        }
      }
    } catch (SQLException | IllegalArgumentException | java.time.DateTimeException failure) {
      AuthenticationInfrastructureException.preserveFatal(failure);
      throw new AuthenticationInfrastructureException();
    }
  }

  private static void requireTransaction(Connection connection) throws SQLException {
    if (connection.getAutoCommit())
      throw new SQLException("login requires an explicit transaction", "25000");
  }

  private static Optional<Instant> optionalInstant(ResultSet row, String column)
      throws SQLException {
    java.time.OffsetDateTime value = row.getObject(column, java.time.OffsetDateTime.class);
    return value == null ? Optional.empty() : Optional.of(value.toInstant());
  }

  private static void setInstant(PreparedStatement statement, int index, Optional<Instant> value)
      throws SQLException {
    if (value.isPresent())
      statement.setObject(index, value.orElseThrow().atOffset(java.time.ZoneOffset.UTC));
    else statement.setNull(index, Types.TIMESTAMP_WITH_TIMEZONE);
  }
}
