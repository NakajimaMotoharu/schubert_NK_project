package dev.codex.schubert.nk.api.bootstrap;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.SQLFeatureNotSupportedException;
import java.sql.SQLNonTransientConnectionException;
import java.util.Arrays;
import java.util.Objects;
import java.util.Properties;
import java.util.logging.Logger;
import javax.sql.DataSource;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Fixed-role physical JDBC source: every returned connection has passed identity admission.
 * Consumes and erases the supplied password copy even on constructor failure; caller closes this
 * source after its pool, and owns every returned connection. The password must already satisfy the
 * SS343 credential decoder contract. No JDBC/immutable String physical erasure is promised.
 * NK-OPS-001; SYS-002/004,DAT-001; UI212/243/253; SS342/343; SSC081/082/084;
 * PG287/PT-OPS-DBSOURCE-001..006; 471 D02.
 */
@NullMarked
public final class ServiceDatabaseSource implements DataSource, AutoCloseable {
  private static final int FIXED_LOGIN_TIMEOUT_SECONDS = 3;

  private final java.util.concurrent.locks.ReentrantLock stateLock =
      new java.util.concurrent.locks.ReentrantLock();
  private final String url;
  private final String role;
  private final String applicationName;
  private final ServiceDatabaseAdmission admission;
  private final char[] password;
  private final Connector connector;
  private boolean closed;

  @FunctionalInterface
  interface Connector {
    @Nullable Connection connect(String url, Properties properties) throws SQLException;
  }

  public ServiceDatabaseSource(
      ServiceConfigFiles.Service service, String url, char[] ownedPassword) {
    this(service, url, ownedPassword, DriverManager::getConnection);
  }

  ServiceDatabaseSource(
      ServiceConfigFiles.Service service, String url, char[] ownedPassword, Connector connector) {
    Objects.requireNonNull(ownedPassword, "owned password");
    try {
      Objects.requireNonNull(service, "service");
      this.url = Objects.requireNonNull(url, "database URL");
      this.connector = Objects.requireNonNull(connector, "database connector");
      admission = new ServiceDatabaseAdmission(service, url);
      if (ownedPassword.length < 1 || ownedPassword.length > 65536)
        throw new IllegalArgumentException("service database credential unavailable");
      role = service == ServiceConfigFiles.Service.API ? "schubert_app" : "schubert_web_session";
      applicationName =
          service == ServiceConfigFiles.Service.API ? "schubert-nk-api" : "schubert-nk-web";
      password = ownedPassword.clone();
    } finally {
      Arrays.fill(ownedPassword, '\0');
    }
  }

  @Override
  public Connection getConnection() throws SQLException {
    stateLock.lock();
    try {
      if (closed) throw unavailable();
      var properties = new Properties();
      properties.setProperty("user", role);
      properties.setProperty("password", new String(password));
      properties.setProperty("connectTimeout", "3");
      properties.setProperty("ApplicationName", applicationName);
      try {
        Connection connection = connector.connect(url, properties);
        if (connection == null) throw unavailable();
        try {
          admission.verify(connection);
          return connection;
        } catch (SQLException failure) {
          discard(connection, failure);
          JdbcFailureGraph.preserveFatal(failure);
          throw unavailable();
        } catch (RuntimeException | Error failure) {
          discard(connection, failure);
          throw failure;
        }
      } catch (SQLException failure) {
        JdbcFailureGraph.preserveFatal(failure);
        throw unavailable();
      } finally {
        properties.clear();
      }
    } finally {
      stateLock.unlock();
    }
  }

  private static void discard(Connection connection, Throwable primary) throws SQLException {
    try {
      connection.close();
    } catch (SQLException cleanup) {
      JdbcAdmissionFailures.beforeDiscard(primary, cleanup);
      if (!(primary instanceof SQLException)) primary.addSuppressed(unavailable());
    } catch (RuntimeException | Error cleanup) {
      JdbcAdmissionFailures.beforeDiscard(primary, cleanup);
      if (primary instanceof SQLException) throw cleanup;
      // Do not add raw provider data or self-suppression. Unknown primary keeps its identity.
      primary.addSuppressed(unavailable());
    }
  }

  @Override
  public Connection getConnection(String username, String suppliedPassword) throws SQLException {
    throw unsupported();
  }

  @Override
  public @Nullable PrintWriter getLogWriter() {
    return null;
  }

  @Override
  public void setLogWriter(@Nullable PrintWriter writer) throws SQLException {
    if (writer != null) throw unsupported();
  }

  @Override
  public void setLoginTimeout(int seconds) throws SQLException {
    if (seconds != FIXED_LOGIN_TIMEOUT_SECONDS) throw unsupported();
  }

  @Override
  public int getLoginTimeout() {
    return 3;
  }

  @Override
  public Logger getParentLogger() throws SQLFeatureNotSupportedException {
    throw unsupported();
  }

  @Override
  public <T> T unwrap(Class<T> type) throws SQLException {
    if (Objects.requireNonNull(type, "wrapper type").isInstance(this)) return type.cast(this);
    throw unsupported();
  }

  @Override
  public boolean isWrapperFor(Class<?> type) {
    return Objects.requireNonNull(type, "wrapper type").isInstance(this);
  }

  @Override
  public void close() {
    stateLock.lock();
    try {
      if (!closed) {
        Arrays.fill(password, '\0');
        closed = true;
      }
    } finally {
      stateLock.unlock();
    }
  }

  @Override
  public String toString() {
    return "ServiceDatabaseSource[REDACTED]";
  }

  private static SQLException unavailable() {
    return new SQLNonTransientConnectionException(
        "service database connection unavailable", "08001");
  }

  private static SQLFeatureNotSupportedException unsupported() {
    return new SQLFeatureNotSupportedException("service database option unavailable", "0A000");
  }
}
