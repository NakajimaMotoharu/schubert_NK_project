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
 * commit, rollback and close. Trace: NK-ADM-001; AUT001002/DAT009/MON004/OPS009; UI225226242;
 * SS314331332343§8.2/351352; SSC188; PT-ADM-BOOT001..008.
 */
@NullMarked
public final class BootstrapAdminService {
  public enum Outcome {
    CREATED,
    ALREADY_EXISTS
  }

  private final PasswordHasher passwords = new PasswordHasher();
  private final PasswordPolicy policy = new PasswordPolicy();

  /**
   * Consumes password on every path. CREATED is provisional until caller's commit and normal
   * resource return. No credential is retained, logged or returned.
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
      // SSC189: join the existing maintenance exclusion; never wait behind an exclusive owner.
      try (var statement =
              requirePrepared(
                  connection.prepareStatement(
                      "select pg_catalog.pg_try_advisory_xact_lock_shared(71419602)"));
          var row = requireResult(statement.executeQuery())) {
        require(row.next());
        boolean granted = row.getBoolean(1);
        require(!row.wasNull());
        require(granted);
        require(!row.next());
      }
      try (var statement =
              requirePrepared(
                  connection.prepareStatement("select pg_advisory_xact_lock(71419601)"));
          var row = requireResult(statement.executeQuery())) {
        require(row.next());
        require(!row.next());
      }
      // Unlike an advisory lock alone, blocks non-cooperating inserts too; held until TX ends.
      try (var statement = requireStatement(connection.createStatement())) {
        statement.execute("lock table schubert.app_users in share row exclusive mode");
      }
      boolean exists;
      try (var statement =
              requirePrepared(
                  connection.prepareStatement("select exists(select 1 from schubert.app_users)"));
          var row = requireResult(statement.executeQuery())) {
        require(row.next());
        exists = row.getBoolean(1);
        require(!row.wasNull());
        require(!row.next());
      }
      // Return only AFTER both resource closes have actually succeeded (same failure contract).
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
      try (var statement =
          requirePrepared(
              connection.prepareStatement(
                  """
              insert into schubert.app_users(username,username_key,password_hash,role,status,
                password_changed_at,created_at,updated_at)
              values (?,?,?,'ADMIN','ACTIVE',?,?,?) returning id
              """))) {
        statement.setString(1, name.value());
        statement.setString(2, name.key());
        statement.setString(3, hash);
        for (int i = 4; i <= 6; i++) statement.setObject(i, metadata.at().atOffset(ZoneOffset.UTC));
        try (var row = requireResult(statement.executeQuery())) {
          require(row.next());
          id = row.getLong(1);
          require(!row.wasNull());
          require(id >= 1 && id <= 999_999_999_999L);
          require(!row.next());
        }
      }
      audit(connection, id, metadata, "ACTION");
      audit(connection, id, metadata, "SECURITY");
      return Outcome.CREATED;
    } finally {
      Arrays.fill(password, '\0');
    }
  }

  private static void audit(
      Connection connection, long id, UserCommandMetadata metadata, String category)
      throws SQLException {
    try (var statement =
        requirePrepared(
            connection.prepareStatement(
                """
            insert into schubert.app_logs(logged_at,service,category,level,action,message,
              message_id,correlation_id,details)
            values (?,'API',?,'INFO','USER_CREATED','USER_CREATED',?,?,
              jsonb_build_object('outcome','SUCCESS','source','BOOTSTRAP','targetUserId',cast(? as bigint)))
            """))) {
      statement.setObject(1, metadata.at().atOffset(ZoneOffset.UTC));
      statement.setString(2, category);
      statement.setObject(3, metadata.messageId());
      statement.setObject(4, metadata.correlationId());
      statement.setLong(5, id);
      require(statement.executeUpdate() == 1);
    }
  }

  // SSC411/PT-ADM-BOOTBOUND011..013: fail closed before dereferencing JDBC boundary values.
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
    if (!condition) throw new SQLException("bootstrap account transaction is invalid");
  }
}
