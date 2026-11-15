package dev.codex.schubert.nk.api.application.admin;

import dev.codex.schubert.nk.api.security.LoginUsername;
import dev.codex.schubert.nk.api.security.PasswordHasher;
import dev.codex.schubert.nk.api.security.PasswordPolicy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Initial ADMIN only; not an authenticated HTTP/User CREATE bypass. Caller owns write transaction,
 * commit, rollback and close. NK-ADM-001; AUT001002/DAT009/MON004/OPS009; UI225226242;
 * SS3143313323438.2/351352 SSC188189411412; PT-ADM-BOOT001..008/BOOTBOUND001..018.
 */
@NullMarked
public final class BootstrapAdminService {
  public enum Outcome {
    CREATED,
    ALREADY_EXISTS
  }

  private static final int RESULT_VOID = 0;
  private static final int RESULT_GRANTED = 1;
  private static final int RESULT_EXISTS = 2;
  private static final int RESULT_ID = 3;
  private static final long MAXIMUM_USER_ID = 999_999_999_999L;
  private static final String SHARED_MAINTENANCE =
      "select pg_catalog.pg_try_advisory_xact_lock_shared(71419602)";
  private static final String MEMBERSHIP = "select pg_advisory_xact_lock(71419601)";
  private static final String ACCOUNT_EXISTS = "select exists(select 1 from schubert.app_users)";
  private final PasswordHasher passwords = new PasswordHasher();
  private final PasswordPolicy policy = new PasswordPolicy();

  /**
   * Consumes password on every path. CREATED is provisional until caller commit and normal close.
   */
  public Outcome create(
      Connection connection, String username, char[] password, UserCommandMetadata metadata)
      throws SQLException {
    Objects.requireNonNull(password, "password");
    try {
      Objects.requireNonNull(connection, "connection");
      Objects.requireNonNull(username, "username");
      Objects.requireNonNull(metadata, "metadata");
      require(
          !connection.getAutoCommit()
              && !connection.isReadOnly()
              && connection.getTransactionIsolation() == Connection.TRANSACTION_READ_COMMITTED);
      query(connection, SHARED_MAINTENANCE, RESULT_GRANTED);
      query(connection, MEMBERSHIP, RESULT_VOID);
      lockMembership(connection);
      boolean exists = query(connection, ACCOUNT_EXISTS, RESULT_EXISTS) == 1;
      // Query helpers return only after both owned closes have actually succeeded.
      if (exists) return Outcome.ALREADY_EXISTS;
      LoginUsername name = new LoginUsername(username);
      if (!name.value().matches("[A-Za-z0-9._-]+"))
        throw new IllegalArgumentException("bootstrap username is invalid");
      char[] normalized = policy.normalizeForCreation(password, name.value());
      String hash;
      try {
        hash = passwords.encode(normalized);
      } finally {
        Arrays.fill(normalized, '\0');
      }
      long id;
      PreparedStatement statement =
          requirePrepared(
              connection.prepareStatement(
                  """
          insert into schubert.app_users(username,username_key,password_hash,role,status,
            password_changed_at,created_at,updated_at)
          values (?,?,?,'ADMIN','ACTIVE',?,?,?) returning id
          """));
      @Nullable Throwable primary = null;
      try {
        statement.setString(1, name.value());
        statement.setString(2, name.key());
        statement.setString(3, hash);
        for (int index = 4; index <= 6; index++)
          statement.setObject(index, metadata.at().atOffset(ZoneOffset.UTC));
        id = read(statement, RESULT_ID);
      } catch (SQLException | RuntimeException | Error failure) {
        primary = failure;
        throw failure;
      } finally {
        closeStatement(statement, primary);
      }
      audit(connection, id, metadata, "ACTION");
      audit(connection, id, metadata, "SECURITY");
      return Outcome.CREATED;
    } finally {
      Arrays.fill(password, '\0');
    }
  }

  private static long query(Connection connection, String sql, int mode) throws SQLException {
    PreparedStatement statement = requirePrepared(connection.prepareStatement(sql));
    @Nullable Throwable primary = null;
    try {
      return read(statement, mode);
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeStatement(statement, primary);
    }
  }

  /** Four private fixed modes preserve the original next/get/wasNull/check/extra-row order. */
  private static long read(PreparedStatement statement, int mode) throws SQLException {
    ResultSet result = requireResult(statement.executeQuery());
    @Nullable Throwable primary = null;
    try {
      require(result.next());
      long actual = 0;
      if (mode != RESULT_VOID) {
        actual = mode == RESULT_ID ? result.getLong(1) : result.getBoolean(1) ? 1 : 0;
        require(!result.wasNull());
        if (mode == RESULT_ID) require(actual >= 1 && actual <= MAXIMUM_USER_ID);
        else if (mode == RESULT_GRANTED) require(actual == 1);
      }
      require(!result.next());
      return actual;
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeResult(result, primary);
    }
  }

  private static void lockMembership(Connection connection) throws SQLException {
    Statement statement = requireStatement(connection.createStatement());
    @Nullable Throwable primary = null;
    try {
      statement.execute("lock table schubert.app_users in share row exclusive mode");
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeStatement(statement, primary);
    }
  }

  private static void audit(
      Connection connection, long id, UserCommandMetadata metadata, String category)
      throws SQLException {
    PreparedStatement statement =
        requirePrepared(
            connection.prepareStatement(
                """
        insert into schubert.app_logs(logged_at,service,category,level,action,message,
          message_id,correlation_id,details)
        values (?,'API',?,'INFO','USER_CREATED','USER_CREATED',?,?,
          jsonb_build_object('outcome','SUCCESS','source','BOOTSTRAP','targetUserId',cast(? as bigint)))
        """));
    @Nullable Throwable primary = null;
    try {
      statement.setObject(1, metadata.at().atOffset(ZoneOffset.UTC));
      statement.setString(2, category);
      statement.setObject(3, metadata.messageId());
      statement.setObject(4, metadata.correlationId());
      statement.setLong(5, id);
      require(statement.executeUpdate() == 1);
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeStatement(statement, primary);
    }
  }

  private static void closeStatement(Statement statement, @Nullable Throwable primary)
      throws SQLException {
    try {
      statement.close();
    } catch (SQLException | RuntimeException | Error failure) {
      if (primary == null) throw failure;
      if (primary != failure) primary.addSuppressed(failure);
    }
  }

  private static void closeResult(ResultSet result, @Nullable Throwable primary)
      throws SQLException {
    try {
      result.close();
    } catch (SQLException | RuntimeException | Error failure) {
      if (primary == null) throw failure;
      if (primary != failure) primary.addSuppressed(failure);
    }
  }

  private static PreparedStatement requirePrepared(@Nullable PreparedStatement created)
      throws SQLException {
    if (created == null) throw invalidBoundary();
    return created;
  }

  private static Statement requireStatement(@Nullable Statement created) throws SQLException {
    if (created == null) throw invalidBoundary();
    return created;
  }

  private static ResultSet requireResult(@Nullable ResultSet created) throws SQLException {
    if (created == null) throw invalidBoundary();
    return created;
  }

  private static SQLException invalidBoundary() {
    return new SQLException("bootstrap account transaction is invalid");
  }

  private static void require(boolean condition) throws SQLException {
    if (!condition) throw invalidBoundary();
  }
}
