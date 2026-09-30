package dev.codex.schubert.nk.batch.repository;

import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.cleanup.InspectorLockHandoff;
import dev.codex.schubert.nk.batch.file.BackupBundleCompletion;
import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
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
 * owns continuous M, original run, A and worker lifetimes. Backup begin requires the opaque fixed
 * root release admission and rechecks current BOM/platform/schema before any begin SQL. The legacy
 * constructor supports original-reference checks only and refuses backup begin. NK-BAT-001;
 * OPS009/DAT009/UI251/SS341/3436.15/SSC094095096/PG311314; PT-OPS-MDB001..008. Commit ambiguity
 * never returns usable backup handles.
 */
@NullMarked
public final class MorningDatabaseSession {
  @FunctionalInterface
  public interface Operation<T> {
    T execute(Session session) throws IOException;
  }

  @FunctionalInterface
  public interface CleanupHandoff<T> {
    T execute() throws IOException;
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

  public record BackupBegins(BatchStepAttempt database, BatchStepAttempt configuration) {
    public BackupBegins {
      Objects.requireNonNull(database, "database begin");
      Objects.requireNonNull(configuration, "configuration begin");
    }
  }

  /** Callback-scoped parent operations. The JDBC handle and lock never escape this capability. */
  public interface Access {
    void requireUnused(BatchRun run) throws IOException;

    void requireConsistent(BatchRun run) throws IOException;

    default void recheckConsistent(BatchRun run) throws IOException {
      Objects.requireNonNull(run, "same original run after begin");
      throw unavailable();
    }

    default void requireAbandonedRequest(
        dev.codex.schubert.nk.batch.platform.BackupWorkerRequest previous) throws IOException {
      Objects.requireNonNull(previous, "held retained request");
      throw unavailable();
    }

    BackupBegins beginBackup(BatchRun run, Instant now, boolean recoverAbandoned)
        throws IOException;

    /** No connection or arbitrary SQL escapes. Non-native test capabilities fail closed. */
    default Instant completeBackup(
        BackupBegins expected, BackupBundleCompletion verified, String name) throws IOException {
      throw unavailable();
    }

    default void failBackup(
        BackupBegins expected,
        Instant endedAt,
        BatchStepResult database,
        BatchStepResult configuration)
        throws IOException {
      throw unavailable();
    }

    <T> T handoffCleanup(CleanupHandoff<T> operation) throws IOException;
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

  public MorningDatabaseSession(
      String url, RootStartupContext context, RootStartupContext.Snapshot expected) {
    this(url, rootGate(context, expected), DriverManager::getConnection);
  }

  public MorningDatabaseSession(
      String url,
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      RootReleaseAdmission release) {
    this(
        url,
        rootGate(context, expected),
        DriverManager::getConnection,
        releaseGate(release, expected));
  }

  private static Schema releaseGate(
      RootReleaseAdmission release, RootStartupContext.Snapshot expected) {
    Objects.requireNonNull(release, "root release admission");
    return connection -> release.verifyMorning(connection, expected);
  }

  private static Gate rootGate(RootStartupContext context, RootStartupContext.Snapshot expected) {
    Objects.requireNonNull(context, "root context");
    Objects.requireNonNull(expected, "root context snapshot");
    if (expected.service() != RootStartupContext.Service.MORNING)
      throw new IllegalArgumentException("morning root required");
    return () -> context.recheck(expected);
  }

  MorningDatabaseSession(String url, Gate gate, Connect connect) {
    this(
        url,
        gate,
        connect,
        connection -> {
          throw unavailable();
        });
  }

  MorningDatabaseSession(String url, Gate gate, Connect connect, Schema schema) {
    var match = URL.matcher(Objects.requireNonNull(url, "batch database URL"));
    if (!match.matches() || Integer.parseInt(Objects.requireNonNull(match.group(1))) > 65535)
      throw new IllegalArgumentException("batch database URL refused");
    this.url = url;
    this.gate = Objects.requireNonNull(gate, "root gate");
    this.connect = Objects.requireNonNull(connect, "fixed batch connector");
    this.schema = Objects.requireNonNull(schema, "mandatory release/schema admission");
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
  public final class Session implements Access {
    private final Connection connection;
    private final long thread = Thread.currentThread().threadId();
    private volatile boolean active = true;
    private volatile boolean backupCommitted;
    private volatile boolean handoffStarted;
    private volatile boolean inHandoff;
    private @Nullable BackupBegins backupBegins;
    private volatile boolean backupFinished;

    private Session(Connection connection) {
      this.connection = connection;
    }

    private void guard() throws IOException {
      if (!active || inHandoff || thread != Thread.currentThread().threadId()) throw unavailable();
      check();
    }

    public void requireUnused(BatchRun run) throws IOException {
      Objects.requireNonNull(run, "new fixed run");
      guard();
      if (backupCommitted) throw unavailable();
      if (new RunReferenceRepository(connection).read(run).anyReference()) throw unavailable();
      guard();
    }

    /**
     * Explicit same-run resume may have references, but every projection must retain the original
     * cutoff.
     */
    public void requireConsistent(BatchRun run) throws IOException {
      Objects.requireNonNull(run, "resumed fixed run");
      guard();
      if (backupCommitted) throw unavailable();
      if (!new RunReferenceRepository(connection).read(run).identityConsistent())
        throw unavailable();
      guard();
    }

    public BackupBegins beginBackup(BatchRun run, Instant now, boolean recoverAbandoned)
        throws IOException {
      Objects.requireNonNull(run, "fixed run");
      Objects.requireNonNull(now, "backup begin time");
      guard();
      if (backupCommitted) throw unavailable();
      try {
        schema.verify(connection); // BEFORE repository construction or either backup begin.
        guard();
        var repository = new BatchRunRepository(connection);
        var database = repository.begin(run, BatchStep.BACKUP_DB, now, recoverAbandoned);
        var configuration = repository.begin(run, BatchStep.BACKUP_CONFIG, now, recoverAbandoned);
        guard();
        connection.commit();
        guard();
        connection.setAutoCommit(true); // Only a confirmed commit can enter session-lock handoff.
        guard();
        backupCommitted = true;
        var result = new BackupBegins(database, configuration);
        backupBegins = result;
        return result;
      } catch (SQLException failure) {
        throw unavailable();
      }
    }

    private void completionGuard(BackupBegins expected) throws IOException, SQLException {
      guard();
      if (!backupCommitted
          || backupFinished
          || handoffStarted
          || !expected.equals(backupBegins)
          || !connection.getAutoCommit()
          || connection.isReadOnly()
          || connection.getTransactionIsolation() != Connection.TRANSACTION_READ_COMMITTED
          || !scalar(connection, HELD)) throw unavailable();
      guard();
    }

    @Override
    public void recheckConsistent(BatchRun run) throws IOException {
      Objects.requireNonNull(run, "same original run after begin");
      guard();
      var expected = backupBegins;
      if (!backupCommitted || expected == null || !run.equals(expected.database().run()))
        throw unavailable();
      try {
        if (!connection.getAutoCommit() || connection.isReadOnly() || !scalar(connection, HELD))
          throw unavailable();
        connection.setAutoCommit(false);
        // The repository requires a borrowed RW-configured connection. The server transaction
        // itself is explicitly READ ONLY; no JDBC configured-readOnly flag is lied about/reset.
        try (var statement = connection.createStatement()) {
          statement.execute("SET TRANSACTION READ ONLY");
        }
        boolean consistent = new RunReferenceRepository(connection).read(run).identityConsistent();
        connection.rollback();
        connection.setAutoCommit(true);
        if (!consistent) throw unavailable();
        guard();
      } catch (SQLException failure) {
        throw unavailable();
      }
    }

    @Override
    public void requireAbandonedRequest(
        dev.codex.schubert.nk.batch.platform.BackupWorkerRequest previous) throws IOException {
      Objects.requireNonNull(previous, "held retained request");
      var expected = backupBegins;
      if (expected == null) throw unavailable();
      try {
        completionGuard(expected);
        BatchRun run = expected.database().run();
        if (!run.id().equals(previous.run())
            || previous.started().isBefore(run.cutoff())
            || !previous.started().isBefore(expected.database().startedAt())
            || !expected.database().startedAt().equals(expected.configuration().startedAt()))
          throw unavailable();
        connection.setReadOnly(true);
        connection.setAutoCommit(false);
        String sql =
            "select step,attempt,status,error_code,ended_at,business_date from schubert.batch_runs "
                + "where run_id=? and started_at=? and step in ('BACKUP_DB','BACKUP_CONFIG') order by step";
        try (var statement = connection.prepareStatement(sql)) {
          statement.setObject(1, previous.run());
          statement.setObject(
              2, java.time.OffsetDateTime.ofInstant(previous.started(), java.time.ZoneOffset.UTC));
          try (var rows = statement.executeQuery()) {
            for (var current : java.util.List.of(expected.configuration(), expected.database())) {
              if (!rows.next()) throw unavailable();
              var ended =
                  present(rows.getObject("ended_at", java.time.OffsetDateTime.class)).toInstant();
              if (!current.step().name().equals(present(rows.getString("step")))
                  || present(rows.getObject("attempt", Integer.class)) >= current.attempt()
                  || !"FAILED".equals(present(rows.getString("status")))
                  || !"ABANDONED".equals(present(rows.getString("error_code")))
                  || ended.isBefore(previous.started())
                  || ended.isAfter(current.startedAt())
                  || !run.cutoff()
                      .atZone(java.time.ZoneId.of("Asia/Tokyo"))
                      .toLocalDate()
                      .equals(present(rows.getObject("business_date", java.time.LocalDate.class))))
                throw unavailable();
            }
            if (rows.next()) throw unavailable();
          }
        }
        connection.rollback();
        connection.setAutoCommit(true);
        connection.setReadOnly(false);
        completionGuard(expected);
        recheckConsistent(run);
      } catch (SQLException failure) {
        throw unavailable();
      }
    }

    @Override
    public Instant completeBackup(
        BackupBegins expected, BackupBundleCompletion verified, String name) throws IOException {
      Objects.requireNonNull(expected, "committed backup handles");
      Objects.requireNonNull(verified, "root verified backup completion");
      Objects.requireNonNull(name, "fixed backup name");
      try {
        completionGuard(expected);
        Instant ended =
            verified.complete(connection, name, expected.database(), expected.configuration());
        completionGuard(expected);
        backupFinished = true;
        return ended;
      } catch (SQLException failure) {
        throw unavailable();
      }
    }

    @Override
    public void failBackup(
        BackupBegins expected,
        Instant endedAt,
        BatchStepResult database,
        BatchStepResult configuration)
        throws IOException {
      Objects.requireNonNull(expected, "committed backup handles");
      Objects.requireNonNull(endedAt, "actual backup end");
      Objects.requireNonNull(database, "observed database failure");
      Objects.requireNonNull(configuration, "observed configuration failure");
      if (database.status() != BatchStepResult.Status.FAILED
          || configuration.status() != BatchStepResult.Status.FAILED) throw unavailable();
      try {
        completionGuard(expected);
        connection.setAutoCommit(false);
        var repository = new BatchRunRepository(connection);
        repository.finish(expected.database(), endedAt, database);
        repository.finish(expected.configuration(), endedAt, configuration);
        guard();
        connection.commit();
        guard();
        connection.setAutoCommit(true);
        completionGuard(expected);
        connection.setAutoCommit(false);
        repository.verifyFinished(expected.database(), endedAt, database);
        repository.verifyFinished(expected.configuration(), endedAt, configuration);
        guard();
        connection.rollback(); // Independent readback has no writes.
        connection.setAutoCommit(true);
        completionGuard(expected);
        backupFinished = true;
      } catch (SQLException failure) {
        throw unavailable();
      }
    }

    /**
     * One synchronous lock transfer; caller still owns M/A, child terminal proof and backup files.
     */
    public <T> T handoffCleanup(CleanupHandoff<T> operation) throws IOException {
      Objects.requireNonNull(operation, "cleanup child operation");
      guard();
      if (!backupCommitted || handoffStarted) throw unavailable();
      try {
        if (!connection.getAutoCommit()) throw unavailable();
        handoffStarted = true;
        inHandoff = true;
        T result =
            InspectorLockHandoff.execute(
                connection,
                () -> {
                  check();
                  return operation.execute();
                });
        inHandoff = false;
        guard();
        return result;
      } catch (SQLException | InspectorLockHandoff.Failure failure) {
        throw unavailable();
      } finally {
        inHandoff = false;
      }
    }
  }
}
