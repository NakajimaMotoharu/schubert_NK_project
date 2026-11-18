package dev.codex.schubert.nk.api.bootstrap;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.SQLNonTransientConnectionException;
import java.util.Map;
import java.util.Objects;
import java.util.regex.Pattern;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Web/API startup DB identity check. It borrows an already connected JDBC handle and never stores
 * credentials or grants access by itself. NK-OPS-001; SYS-002/004, DAT-001; UI212/243/253;
 * SS342/343 §5.2, SSC-082; PG283/PT-OPS-DBADMIT-001..004.
 */
@NullMarked
public final class ServiceDatabaseAdmission {
  private static final Map<ServiceConfigFiles.Service, String> SERVICE_ROLES =
      Map.of(
          ServiceConfigFiles.Service.API, "schubert_app",
          ServiceConfigFiles.Service.WEB, "schubert_web_session");
  private static final Pattern URL =
      Pattern.compile(
          "jdbc:postgresql://127\\.0\\.0\\.1:([1-9][0-9]{0,4})/([a-z_][a-z0-9_]{0,62})");
  private static final String SQL =
      "select current_user::text as effective_role,session_user::text as login_role,"
          + "current_database()::text as database_name,pg_is_in_recovery() as recovery";

  private final String role;
  private final String database;

  public ServiceDatabaseAdmission(ServiceConfigFiles.Service service, String url) {
    role =
        Objects.requireNonNull(
            SERVICE_ROLES.get(Objects.requireNonNull(service, "service")), "service role");
    var match = URL.matcher(Objects.requireNonNull(url, "database URL"));
    if (!match.matches() || Integer.parseInt(Objects.requireNonNull(match.group(1))) > 65535)
      throw new IllegalArgumentException("service database URL is invalid");
    database = Objects.requireNonNull(match.group(2));
  }

  /** Caller owns and closes the borrowed connection on every success/failure path. */
  public void verify(Connection connection) throws SQLException {
    Objects.requireNonNull(connection, "database connection");
    try {
      if (!connection.getAutoCommit() || connection.isReadOnly()) throw unavailable();
      var statement = connection.prepareStatement(SQL);
      @Nullable Throwable primary = null;
      try {
        var rows = required(statement).executeQuery();
        @Nullable Throwable rowFailure = null;
        try {
          var values = required(rows);
          if (!values.next()
              || !role.equals(required(values.getString("effective_role")))
              || !role.equals(required(values.getString("login_role")))
              || !database.equals(required(values.getString("database_name")))
              || required(values.getObject("recovery", Boolean.class))
              || values.next()) throw unavailable();
        } catch (SQLException | RuntimeException | Error failure) {
          rowFailure = failure;
          throw failure;
        } finally {
          closeRows(rows, rowFailure);
        }
      } catch (SQLException | RuntimeException | Error failure) {
        primary = failure;
        throw failure;
      } finally {
        closeStatement(statement, primary);
      }
    } catch (SQLException failure) {
      JdbcFailureGraph.preserveFatal(failure);
      throw unavailable();
    }
  }

  String role() {
    return role;
  }

  // SSC-468: a single typed cleanup path preserves existing resource and failure ordering.
  private static void closeRows(@Nullable ResultSet rows, @Nullable Throwable primary)
      throws SQLException {
    if (rows != null) {
      try {
        rows.close();
      } catch (SQLException | RuntimeException | Error secondary) {
        if (JdbcAdmissionFailures.replace(primary, secondary)) throw secondary;
      }
    }
  }

  private static void closeStatement(
      @Nullable PreparedStatement statement, @Nullable Throwable primary) throws SQLException {
    if (statement != null) {
      try {
        statement.close();
      } catch (SQLException | RuntimeException | Error secondary) {
        if (JdbcAdmissionFailures.replace(primary, secondary)) throw secondary;
      }
    }
  }

  private static SQLException unavailable() {
    return new SQLNonTransientConnectionException(
        "service database connection unavailable", "08001");
  }

  private static <T> T required(@org.jspecify.annotations.Nullable T value) throws SQLException {
    if (value == null) throw unavailable();
    return value;
  }
}
