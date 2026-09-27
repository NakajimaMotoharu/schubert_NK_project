package dev.codex.schubert.nk.batch.repository;

import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import java.io.IOException;
import java.sql.*;
import java.time.Instant;
import java.util.*;
import java.util.regex.Pattern;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Dedicated root morning session; no pool/role fallback/arbitrary SQL/connection export. Caller
 * owns continuous M, original run, A and worker lifetimes; schema/BOM admission remains a separate
 * mandatory assembly gate. NK-BAT-001/OPS009/DAT009/UI251/SS341/3436.15/SSC094/PG311;
 * PT-OPS-MDB001..008. Commit ambiguity never returns usable backup handles.
 */
@NullMarked
public final class MorningDatabaseSession {
  @FunctionalInterface
  public interface Operation<T> {
    T execute(Session session) throws IOException;
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
  private interface Rows<T> {
    T read(ResultSet rows) throws SQLException;
  }

  public record BackupBegins(BatchStepAttempt database, BatchStepAttempt configuration) {
    public BackupBegins {
      Objects.requireNonNull(database, "database begin");
      Objects.requireNonNull(configuration, "configuration begin");
    }
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

  public MorningDatabaseSession(
      String url, RootStartupContext context, RootStartupContext.Snapshot expected) {
    this(url, rootGate(context, expected), DriverManager::getConnection);
  }

  private static Gate rootGate(RootStartupContext context, RootStartupContext.Snapshot expected) {
    Objects.requireNonNull(context, "root context");
    Objects.requireNonNull(expected, "root context snapshot");
    if (expected.service() != RootStartupContext.Service.MORNING)
      throw new IllegalArgumentException("morning root required");
    return () -> context.recheck(expected);
  }

  MorningDatabaseSession(String url, Gate gate, Connect connect) {
    var match = URL.matcher(Objects.requireNonNull(url, "batch database URL"));
    if (!match.matches() || Integer.parseInt(Objects.requireNonNull(match.group(1))) > 65535)
      throw new IllegalArgumentException("batch database URL refused");
    this.url = url;
    this.gate = Objects.requireNonNull(gate, "root gate");
    this.connect = Objects.requireNonNull(connect, "fixed batch connector");
  }

  /** Consumes the password owner even on pre-connect rejection. Callback is synchronous only. */
  public <T> T execute(InspectorDbCredential owned, Operation<T> operation) throws IOException {
    Objects.requireNonNull(owned, "owned batch credential");
    @Nullable Connection connection = null;
    @Nullable Throwable primary = null;
    try {
      Objects.requireNonNull(operation, "morning operation");
      check();
      Properties properties = new Properties();
      char[] password = owned.copyPassword();
      try {
        properties.setProperty("user", "schubert_batch");
        properties.setProperty("password", new String(password));
        properties.setProperty("connectTimeout", "3");
        properties.setProperty("ApplicationName", "schubert-nk-morning-controller");
        Arrays.fill(password, '\0');
        connection = present(connect.open(url, properties));
      } finally {
        Arrays.fill(password, '\0');
        properties.clear();
      }
      admit(connection);
      require(scalar(connection, LOCK));
      require(scalar(connection, HELD));
      connection.setAutoCommit(false);
      var session = new Session(connection);
      try {
        check();
        T result = Objects.requireNonNull(operation.execute(session), "morning result");
        check();
        return result;
      } finally {
        session.active = false;
      }
    } catch (SQLException | IOException | BatchRepositoryException failure) {
      primary = failure;
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
          if (closeReplace(primary, secondary)) {
            throw secondary;
          }
        }
      }
    }
  }

  private void check() throws IOException {
    if (Thread.currentThread().isInterrupted()) throw unavailable();
    gate.check();
  }

  private static boolean closeReplace(@Nullable Throwable primary, Throwable secondary) {
    boolean known =
        primary instanceof SQLException
            || primary instanceof IOException
            || primary instanceof BatchRepositoryException;
    if (primary == null || (known && !(secondary instanceof SQLException))) return true;
    if (!known) primary.addSuppressed(new BatchRepositoryException());
    return false;
  }

  private static void admit(Connection connection) throws SQLException {
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

  private static boolean scalar(Connection connection, String sql) throws SQLException {
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

  private static <T> T query(Connection connection, String sql, Rows<T> operation)
      throws SQLException {
    var statement = connection.prepareStatement(sql);
    @Nullable Throwable failure = null;
    try {
      var checked = present(statement);
      checked.setQueryTimeout(5);
      var rows = checked.executeQuery();
      @Nullable Throwable rowFailure = null;
      try {
        return operation.read(present(rows));
      } catch (SQLException | RuntimeException | Error primary) {
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
    } catch (SQLException | RuntimeException | Error primary) {
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
    if (value == null) throw new SQLDataException("batch database projection unavailable");
    return value;
  }

  private static void require(boolean accepted) throws SQLException {
    if (!accepted) throw new SQLDataException("batch database admission refused");
  }

  private static IOException unavailable() {
    return new IOException("root batch database unavailable");
  }

  /** No DB handle escapes; methods enforce callback thread/lifetime before any JDBC use. */
  public final class Session {
    private final Connection connection;
    private final long thread = Thread.currentThread().threadId();
    private volatile boolean active = true;

    private Session(Connection connection) {
      this.connection = connection;
    }

    private void guard() throws IOException {
      if (!active || thread != Thread.currentThread().threadId()) throw unavailable();
      check();
    }

    public void requireUnused(BatchRun run) throws IOException {
      Objects.requireNonNull(run, "new fixed run");
      guard();
      if (new RunReferenceRepository(connection).read(run).anyReference()) throw unavailable();
      guard();
    }

    public BackupBegins beginBackup(BatchRun run, Instant now, boolean recoverAbandoned)
        throws IOException {
      Objects.requireNonNull(run, "fixed run");
      Objects.requireNonNull(now, "backup begin time");
      guard();
      try {
        var repository = new BatchRunRepository(connection);
        var database = repository.begin(run, BatchStep.BACKUP_DB, now, recoverAbandoned);
        var configuration = repository.begin(run, BatchStep.BACKUP_CONFIG, now, recoverAbandoned);
        guard();
        connection.commit();
        guard();
        return new BackupBegins(database, configuration);
      } catch (SQLException failure) {
        throw unavailable();
      }
    }
  }
}
