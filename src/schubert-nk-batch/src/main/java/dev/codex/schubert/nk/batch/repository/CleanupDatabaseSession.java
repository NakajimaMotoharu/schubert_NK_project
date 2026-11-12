package dev.codex.schubert.nk.batch.repository;

import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;
import java.util.Properties;
import java.util.regex.Pattern;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Cleanup child's own single-use fixed-role connection, never the parent's lock or release proof.
 * The borrowed connection is synchronous and is closed before success returns. Caller still owns
 * the M/A, original run, verified backup artifacts and genuine Unit lifecycle. NK-BAT-001;
 * OPS009/BAK001/UI251/SS341/343/SSC104/PG328; PT-OPS-CDB001..008.
 */
@NullMarked
public final class CleanupDatabaseSession {
  @FunctionalInterface
  public interface Operation<T> {
    T execute(Connection borrowed) throws IOException;
  }

  @FunctionalInterface
  interface Gate {
    void check() throws IOException;
  }

  @FunctionalInterface
  interface Connect {
    Connection open(String url, Properties properties) throws SQLException;
  }

  @FunctionalInterface
  interface Schema {
    void verify(Connection admitted) throws SQLException, IOException;
  }

  @FunctionalInterface
  private interface Rows<T> {
    T read(ResultSet rows) throws SQLException;
  }

  private static final Pattern URL =
      Pattern.compile("jdbc:postgresql://127\\.0\\.0\\.1:([1-9][0-9]{0,4})/schubert_nk");
  private static final String ROLE =
      "select current_user::text as effective_role,session_user::text as login_role,"
          + "current_database()::text as database_name,pg_is_in_recovery() as recovery";
  private static final String LOCK = "select pg_catalog.pg_try_advisory_lock(71419602) as value";
  private static final String HELD =
      "select exists(select 1 from pg_catalog.pg_locks where locktype='advisory'"
          + " and database=(select oid from pg_catalog.pg_database where datname=current_database())"
          + " and pid=pg_catalog.pg_backend_pid() and classid=0 and objid=71419602 and objsubid=1"
          + " and mode='ExclusiveLock' and granted) as value";

  private final String url;
  private final Gate gate;
  private final Connect connect;
  private final Schema schema;
  private final Optional<dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard> owner;

  public CleanupDatabaseSession(
      String url,
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      RootReleaseAdmission release) {
    this(
        url,
        rootGate(context, expected),
        DriverManager::getConnection,
        cleanupSchema(release, expected));
  }

  private static Gate rootGate(RootStartupContext context, RootStartupContext.Snapshot expected) {
    return rootGateFor(context, expected, RootStartupContext.Service.CLEANUP);
  }

  public static CleanupDatabaseSession forExpiry(
      String url,
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      RootReleaseAdmission release) {
    Objects.requireNonNull(release, "Expiry release admission");
    return new CleanupDatabaseSession(
        url,
        rootGateFor(context, expected, RootStartupContext.Service.EXPIRY),
        DriverManager::getConnection,
        connection -> release.verifyExpiry(connection, expected));
  }

  /** SSC125: the native Expiry admission borrows the authenticated Morning deadline throughout. */
  public static CleanupDatabaseSession forExpiry(
      String url,
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      RootReleaseAdmission release,
      dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner) {
    Objects.requireNonNull(release, "Expiry release admission");
    return new CleanupDatabaseSession(
        url,
        rootGateFor(context, expected, RootStartupContext.Service.EXPIRY),
        DriverManager::getConnection,
        connection -> release.verifyExpiry(connection, expected),
        Optional.of(Objects.requireNonNull(owner, "actual Morning deadline")));
  }

  private static Gate rootGateFor(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      RootStartupContext.Service service) {
    Objects.requireNonNull(context, "cleanup root context");
    Objects.requireNonNull(expected, "cleanup root snapshot");
    if (expected.service() != service) throw new IllegalArgumentException("cleanup root required");
    return () -> context.recheck(expected);
  }

  private static Schema cleanupSchema(
      RootReleaseAdmission release, RootStartupContext.Snapshot expected) {
    Objects.requireNonNull(release, "cleanup release admission");
    Objects.requireNonNull(expected, "cleanup root snapshot");
    return new CleanupSchema(release, expected);
  }

  private static final class CleanupSchema implements Schema {
    private final RootReleaseAdmission release;
    private final RootStartupContext.Snapshot expected;

    private CleanupSchema(RootReleaseAdmission release, RootStartupContext.Snapshot expected) {
      this.release = release;
      this.expected = expected;
    }

    @Override
    public void verify(Connection connection) throws SQLException, IOException {
      release.verifyCleanup(connection, expected);
    }
  }

  CleanupDatabaseSession(String url, Gate gate, Connect connect, Schema schema) {
    this(url, gate, connect, schema, Optional.empty());
  }

  CleanupDatabaseSession(
      String url,
      Gate gate,
      Connect connect,
      Schema schema,
      Optional<dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard> owner) {
    var match = URL.matcher(Objects.requireNonNull(url, "cleanup database URL"));
    if (!match.matches() || Integer.parseInt(Objects.requireNonNull(match.group(1))) > 65535)
      throw new IllegalArgumentException("cleanup database URL refused");
    this.url = url;
    this.gate = Objects.requireNonNull(gate, "cleanup root gate");
    this.connect = Objects.requireNonNull(connect, "cleanup fixed connector");
    this.schema = Objects.requireNonNull(schema, "cleanup release/schema gate");
    this.owner = Objects.requireNonNull(owner, "borrowed parent binding");
  }

  /** Consumes password owner, closes every JDBC owner, and never returns an open connection. */
  public <T> T execute(InspectorDbCredential owned, Operation<T> operation) throws IOException {
    Objects.requireNonNull(owned, "owned cleanup credential");
    @Nullable Connection connection = null;
    @Nullable Throwable primary = null;
    try {
      Objects.requireNonNull(operation, "cleanup operation");
      check();
      Properties properties = new Properties();
      char[] password = owned.copyPassword();
      try {
        properties.setProperty("user", "schubert_batch");
        properties.setProperty("password", new String(password));
        properties.setProperty("connectTimeout", Integer.toString(Math.min(3, queryTimeout())));
        if (owner.isPresent())
          properties.setProperty("socketTimeout", Integer.toString(queryTimeout()));
        properties.setProperty("ApplicationName", "schubert-nk-cleanup");
        Arrays.fill(password, '\0');
        connection = present(connect.open(url, properties));
      } finally {
        Arrays.fill(password, '\0');
        properties.clear();
      }
      admit(connection);
      schema.verify(connection); // Child's own release/schema, before acquiring deletion lock.
      check();
      require(scalar(connection, LOCK));
      require(scalar(connection, HELD));
      check();
      T result = Objects.requireNonNull(operation.execute(connection), "cleanup result");
      check();
      require(
          connection.getAutoCommit()
              && !connection.isReadOnly()
              && connection.getTransactionIsolation() == Connection.TRANSACTION_READ_COMMITTED);
      require(scalar(connection, HELD));
      return result;
    } catch (SQLException | IOException | BatchRepositoryException failure) {
      primary = failure;
      if (failure instanceof SQLException || failure instanceof BatchRepositoryException) {
        try {
          StorageIoException.preserveFatal(failure);
        } catch (Error fatal) {
          primary = fatal;
          throw fatal;
        }
      }
      throw unavailable();
    } catch (RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      owned.close();
      if (connection != null) {
        try {
          connection.close();
        } catch (SQLException secondary) {
          if (closeReplace(primary, secondary)) throw unavailable();
        } catch (RuntimeException | Error secondary) {
          if (closeReplace(primary, secondary)) throw secondary;
        }
      }
    }
  }

  private void check() throws IOException {
    if (Thread.currentThread().isInterrupted()) throw unavailable();
    gate.check();
    if (owner.isPresent()) owner.orElseThrow().check();
  }

  private int queryTimeout() throws IOException {
    return owner.isPresent() ? owner.orElseThrow().queryTimeoutSeconds() : 5;
  }

  private void admit(Connection connection) throws SQLException, IOException {
    require(
        connection.getAutoCommit()
            && !connection.isReadOnly()
            && connection.getTransactionIsolation() == Connection.TRANSACTION_READ_COMMITTED);
    query(
        connection,
        ROLE,
        rows -> {
          require(rows.next());
          require("schubert_batch".equals(present(rows.getString("effective_role"))));
          require("schubert_batch".equals(present(rows.getString("login_role"))));
          require("schubert_nk".equals(present(rows.getString("database_name"))));
          require(!present(rows.getObject("recovery", Boolean.class)));
          require(!rows.next());
          return Boolean.TRUE;
        });
  }

  private boolean scalar(Connection connection, String sql) throws SQLException, IOException {
    return query(
        connection,
        sql,
        rows -> {
          require(rows.next());
          boolean value = present(rows.getObject("value", Boolean.class));
          require(!rows.next());
          return value;
        });
  }

  private <T> T query(Connection connection, String sql, Rows<T> operation)
      throws SQLException, IOException {
    check();
    var statement = connection.prepareStatement(sql);
    @Nullable Throwable failure = null;
    try {
      var checked = present(statement);
      checked.setQueryTimeout(queryTimeout());
      var rows = checked.executeQuery();
      @Nullable Throwable rowFailure = null;
      try {
        T result = operation.read(present(rows));
        check();
        return result;
      } catch (SQLException | IOException | RuntimeException | Error primary) {
        rowFailure = primary;
        throw primary;
      } finally {
        if (rows != null)
          try {
            rows.close();
          } catch (SQLException | RuntimeException | Error secondary) {
            if (JdbcResourceFailures.replace(rowFailure, secondary)) throw secondary;
          }
      }
    } catch (SQLException | IOException | RuntimeException | Error primary) {
      failure = primary;
      throw primary;
    } finally {
      if (statement != null)
        try {
          statement.close();
        } catch (SQLException | RuntimeException | Error secondary) {
          if (JdbcResourceFailures.replace(failure, secondary)) throw secondary;
        }
    }
  }

  private static <T> T present(@Nullable T value) throws SQLException {
    if (value == null) throw new SQLDataException("cleanup database projection unavailable");
    return value;
  }

  private static void require(boolean accepted) throws SQLException {
    if (!accepted) throw new SQLDataException("cleanup database admission refused");
  }

  private static boolean closeReplace(@Nullable Throwable primary, Throwable secondary) {
    boolean known =
        primary instanceof SQLException
            || primary instanceof IOException
            || primary instanceof BatchRepositoryException;
    if (primary == null || (known && !(secondary instanceof SQLException))) return true;
    if (!known) primary.addSuppressed(new BatchRepositoryException());
    else {
      if (primary instanceof SQLException || primary instanceof BatchRepositoryException)
        StorageIoException.preserveFatal(primary);
      StorageIoException.preserveFatal(secondary);
    }
    return false;
  }

  private static IOException unavailable() {
    return new IOException("root cleanup database unavailable");
  }
}
