package dev.codex.schubert.nk.api.maintenance;

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.api.messaging.outbound.SqlConnectionProvider;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.SQLNonTransientConnectionException;
import java.util.Arrays;
import java.util.Objects;
import java.util.Properties;
import java.util.regex.Pattern;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Fixed-role fresh connections for the private inspector; owns only its password copy. NK-DAT-001;
 * DAT-009/OPS-009; UI212/241/251; SS343 6.6/342/352; QA-046/SSC-049/PG-D-142; PT-DB-INBOX-202..208.
 * No caller-supplied property/role/SQL or pool.
 */
@NullMarked
public final class InspectorDatabaseConnections implements SqlConnectionProvider, AutoCloseable {
  private static final Pattern URL =
      Pattern.compile(
          "jdbc:postgresql://127\\.0\\.0\\.1:([1-9][0-9]{0,4})/([a-z_][a-z0-9_]{0,62})");
  private static final String ROLE = "schubert_inbox_inspector";
  private final Object stateLock = new Object();
  private final String url;
  private final String database;
  private final char[] password;
  private final Connector connector;
  private boolean closed;

  public InspectorDatabaseConnections(String url, InspectorDbCredential credential) {
    this(url, credential, DriverManager::getConnection);
  }

  InspectorDatabaseConnections(String url, InspectorDbCredential credential, Connector connector) {
    this.url = Objects.requireNonNull(url, "database URL");
    Objects.requireNonNull(credential, "database credential");
    this.connector = Objects.requireNonNull(connector, "database connector");
    var match = URL.matcher(url);
    if (!match.matches() || Integer.parseInt(Objects.requireNonNull(match.group(1))) > 65535)
      throw new IllegalArgumentException("inspector database URL is invalid");
    database = Objects.requireNonNull(match.group(2));
    password = credential.copyPassword();
  }

  @FunctionalInterface
  interface Connector {
    @Nullable Connection connect(String url, Properties properties) throws SQLException;
  }

  /**
   * Returns an admitted fresh connection owned by caller, never retained/closed by this provider.
   */
  @Override
  public Connection open() throws SQLException {
    synchronized (stateLock) {
      if (closed) throw unavailable();
      var properties = new Properties();
      properties.setProperty("user", ROLE);
      properties.setProperty("password", new String(password));
      properties.setProperty("connectTimeout", "3");
      properties.setProperty("ApplicationName", "schubert-nk-inbox-inspector");
      try {
        Connection connection = connector.connect(url, properties);
        if (connection == null) throw unavailable();
        boolean returned = false;
        try {
          admit(connection);
          returned = true;
          return connection;
        } finally {
          if (!returned) connection.close();
        }
      } catch (SQLException failure) {
        throw unavailable();
      } finally {
        properties.clear();
      }
    }
  }

  private void admit(Connection connection) throws SQLException {
    if (!connection.getAutoCommit() || connection.isReadOnly()) throw unavailable();
    try (var statement =
        connection.prepareStatement(
            "select current_user::text as effective_role,session_user::text as login_role,"
                + "current_database()::text as database_name,pg_is_in_recovery() as recovery")) {
      try (var row = statement.executeQuery()) {
        if (!row.next()
            || !ROLE.equals(requireValue(row.getString("effective_role")))
            || !ROLE.equals(requireValue(row.getString("login_role")))
            || !database.equals(requireValue(row.getString("database_name")))
            || requireValue(row.getObject("recovery", Boolean.class))
            || row.next()) throw unavailable();
      }
    }
  }

  private static SQLException unavailable() {
    return new SQLNonTransientConnectionException(
        "inspector database connection unavailable", "08001");
  }

  @Override
  public void close() {
    synchronized (stateLock) {
      if (!closed) {
        Arrays.fill(password, '\0');
        closed = true;
      }
    }
  }

  @Override
  public String toString() {
    return "InspectorDatabaseConnections[REDACTED]";
  }
}
