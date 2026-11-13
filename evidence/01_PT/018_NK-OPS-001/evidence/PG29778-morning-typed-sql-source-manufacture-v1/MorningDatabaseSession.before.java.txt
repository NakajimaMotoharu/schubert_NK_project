package dev.codex.schubert.nk.batch.repository;

import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.cleanup.InspectorLockHandoff;
import dev.codex.schubert.nk.batch.file.BackupBundleCompletion;
import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Properties;
import java.util.Set;
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
  private static final java.lang.String LITERAL_ENDED_AT = "ended_at";

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

    default RootReleaseAdmission.DatabaseInspection inspect(Connection admitted)
        throws SQLException, IOException {
      Objects.requireNonNull(admitted);
      throw unavailable(); // A legacy/synthetic verification callback cannot mint issuer facts.
    }
  }

  /** SSC129 data only; the live Access, original M/A and full prestart proof remain necessary. */
  public record DatabaseObservation(
      String loginRole,
      String effectiveRole,
      String database,
      boolean autoCommit,
      boolean jdbcReadOnly,
      int isolation,
      boolean recovery,
      boolean advisoryHeld,
      RootReleaseAdmission.DatabaseInspection release) {
    public DatabaseObservation {
      Objects.requireNonNull(loginRole);
      Objects.requireNonNull(effectiveRole);
      Objects.requireNonNull(database);
      Objects.requireNonNull(release);
    }

    @Override
    public String toString() {
      return "MorningDatabaseObservation[actual=<redacted>]";
    }
  }

  @FunctionalInterface
  private interface Rows<T> {
    T read(ResultSet rows) throws SQLException, IOException;
  }

  public record BackupBegins(BatchStepAttempt database, BatchStepAttempt configuration) {
    public BackupBegins {
      Objects.requireNonNull(database, "database begin");
      Objects.requireNonNull(configuration, "configuration begin");
    }
  }

  /** SSC134 data only: current full rows and separately retained original SUCCESS rows. */
  public record BackupObservation(
      List<BackupStepRepository.Terminal> current, List<BackupStepRepository.Terminal> prior) {
    public BackupObservation {
      current = List.copyOf(current);
      prior = List.copyOf(prior);
      if (current.size() != 2 || (!prior.isEmpty() && prior.size() != 2))
        throw new IllegalArgumentException("Backup observation pair incomplete");
      if (current.get(0).attempt().id() == current.get(1).attempt().id()
          || !current.get(0).attempt().startedAt().equals(current.get(1).attempt().startedAt())
          || !current.get(0).ended().equals(current.get(1).ended())
          || current.get(0).result().status() != current.get(1).result().status())
        throw new IllegalArgumentException("Backup observation pair inconsistent");
      for (int index = 0; index < 2; index++) {
        var row = current.get(index);
        if (row.attempt().step() != (index == 0 ? BatchStep.BACKUP_DB : BatchStep.BACKUP_CONFIG)
            || !row.attempt().run().equals(current.getFirst().attempt().run())
            || row.attempt().skipped() != !prior.isEmpty())
          throw new IllegalArgumentException("Backup observation binding invalid");
        if (!prior.isEmpty()) {
          var original = prior.get(index);
          if (row.result().reason() != BatchStepResult.Reason.ALREADY_SUCCESSFUL
              || !row.ended().equals(row.attempt().startedAt())
              || original.result().status() != BatchStepResult.Status.SUCCESS
              || original.attempt().step() != row.attempt().step()
              || !original.attempt().run().equals(row.attempt().run())
              || original.attempt().id() == row.attempt().id()
              || original.attempt().attempt() >= row.attempt().attempt()
              || original.ended().isAfter(row.attempt().startedAt()))
            throw new IllegalArgumentException("Backup original reference invalid");
        }
      }
    }

    @Override
    public String toString() {
      return "BackupObservation[actual=<redacted>]";
    }
  }

  /** Current committed attempt and separate original audit. Claims confer no callback authority. */
  public record ExpiryBegins(
      BatchStepAttempt current, Optional<ExpiryAuditRepository.Prior> prior) {
    public ExpiryBegins {
      Objects.requireNonNull(current);
      Objects.requireNonNull(prior);
      if (current.step() != BatchStep.CLEAN_EXPIRY || current.skipped() != prior.isPresent())
        throw new IllegalArgumentException("invalid current Expiry begin");
    }
  }

  /**
   * SSC126/ISSSTEP002: current terminal and genuine current receipt, with a separately named audit
   * and original reference. Data only; the guarded Access remains the authority for every reread.
   */
  public record ExpiryObservation(
      ExpiryBegins begins,
      Instant ended,
      BatchStepResult result,
      ExpiryAuditRepository.Snapshot audit,
      dev.codex.schubert.nk.batch.platform.BackupUnitReceiptGate.TerminalReceipt receipt) {
    public ExpiryObservation {
      Objects.requireNonNull(begins);
      Objects.requireNonNull(ended);
      Objects.requireNonNull(result);
      Objects.requireNonNull(audit);
      Objects.requireNonNull(receipt);
      BatchStepAttempt.time(begins.current().run(), ended);
      if (ended.isBefore(begins.current().startedAt())
          || receipt.target()
              != dev.codex.schubert.nk.batch.platform.BackupUnitStartClient.Target.EXPIRY)
        throw new IllegalArgumentException("invalid actual Expiry observation");
      if (begins.current().skipped()) {
        if (!ended.equals(begins.current().startedAt())
            || !result.equals(
                new BatchStepResult(
                    BatchStepResult.Status.SKIPPED,
                    0,
                    0,
                    0,
                    0,
                    BatchStepResult.Reason.ALREADY_SUCCESSFUL))
            || !audit.equals(begins.prior().orElseThrow().audit())
            || receipt.exitCode() != 0)
          throw new IllegalArgumentException("invalid actual Expiry skip observation");
      } else if (result.status() == BatchStepResult.Status.SKIPPED
          || !ended.equals(audit.ended())
          || !result.status().name().equals(audit.status())
          || result.target() != audit.target()
          || result.success() != audit.success()
          || result.failure() != audit.failure()
          || result.bytes() != audit.estimatedBytes())
        throw new IllegalArgumentException("invalid actual Expiry terminal observation");
    }

    @Override
    public String toString() {
      return "ExpiryObservation[actual=<redacted>]";
    }
  }

  /** Callback-scoped parent operations. The JDBC handle and lock never escape this capability. */
  public interface Access {
    /** SSC133: actual pair admission, never a Connection/SQL/claim authority export. */
    default boolean retainedBackupSuccessful(BackupManifest manifest, Instant now)
        throws IOException {
      throw unavailable();
    }

    default DatabaseObservation inspectPermitDatabase(
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner) throws IOException {
      Objects.requireNonNull(owner);
      throw unavailable();
    }

    default void recheckPermitDatabase(
        DatabaseObservation expected,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      Objects.requireNonNull(expected);
      Objects.requireNonNull(owner);
      if (!expected.equals(inspectPermitDatabase(owner))) throw unavailable();
    }

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

    default Optional<BackupBegins> successfulBackup(BatchRun run, Instant now) throws IOException {
      throw unavailable();
    }

    default BackupBegins beginResumeBackup(BackupManifest original, Instant now)
        throws IOException {
      throw unavailable();
    }

    default void completeReusedBackup(BackupBegins expected, BackupManifest original, Instant now)
        throws IOException {
      throw unavailable();
    }

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

    default BackupObservation observeBackup(
        BackupBegins expected,
        Optional<BackupManifest> actual,
        Instant now,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      throw unavailable();
    }

    <T> T handoffCleanup(CleanupHandoff<T> operation) throws IOException;

    default ExpiryBegins beginExpiry(
        BatchRun run,
        Instant now,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      Objects.requireNonNull(run);
      Objects.requireNonNull(now);
      Objects.requireNonNull(owner);
      throw unavailable();
    }

    default <T> T handoffExpiry(CleanupHandoff<T> operation) throws IOException {
      Objects.requireNonNull(operation);
      throw unavailable();
    }

    /** SSC200: data-only lookup remains bound to the live original owner. */
    default ExpiryBegins beginExpiry(
        BatchRun run,
        Instant now,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner,
        SuccessRunLookup originals)
        throws IOException {
      Objects.requireNonNull(originals);
      return beginExpiry(run, now, owner);
    }

    default ExpiryObservation observeExpiry(
        ExpiryBegins begins,
        dev.codex.schubert.nk.batch.platform.BackupUnitReceiptGate.TerminalReceipt receipt,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      Objects.requireNonNull(begins);
      Objects.requireNonNull(receipt);
      Objects.requireNonNull(owner);
      throw unavailable();
    }

    default void recheckExpiry(
        ExpiryObservation expected,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      Objects.requireNonNull(expected);
      Objects.requireNonNull(owner);
      if (!expected.equals(observeExpiry(expected.begins(), expected.receipt(), owner)))
        throw unavailable();
    }

    default BackupFailureSnapshot failedBackupSnapshot(
        BackupBegins expected, dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      Objects.requireNonNull(expected);
      Objects.requireNonNull(owner);
      throw unavailable();
    }

    default CleanupTerminalRepository.Snapshot observeCleanupBackupUnavailable(
        BatchRun run,
        int receipt,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      Objects.requireNonNull(run);
      Objects.requireNonNull(owner);
      throw unavailable();
    }

    default CleanupTerminalRepository.Snapshot observeCleanup(
        BatchRun run,
        int receipt,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      Objects.requireNonNull(run, "original Cleanup run");
      Objects.requireNonNull(owner, "same parent deadline");
      throw unavailable();
    }

    default java.util.List<Optional<CleanupTerminalRepository.Entry>> cleanupReferences(
        CleanupTerminalRepository.Snapshot expected,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      Objects.requireNonNull(expected);
      Objects.requireNonNull(owner);
      throw unavailable();
    }

    /** SSC200: retained original lookup belongs to the still-owned parent, not DB row claims. */
    default java.util.List<Optional<CleanupTerminalRepository.Entry>> cleanupReferences(
        CleanupTerminalRepository.Snapshot expected,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner,
        SuccessRunLookup originals)
        throws IOException {
      Objects.requireNonNull(originals);
      return cleanupReferences(expected, owner);
    }

    default CleanupTerminalRepository.RejectedSnapshot observeCleanupRejected(
        BatchRun run,
        dev.codex.schubert.nk.batch.platform.BackupUnitReceiptGate.TerminalReceipt receipt,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      Objects.requireNonNull(run);
      Objects.requireNonNull(receipt);
      Objects.requireNonNull(owner);
      throw unavailable();
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
    return new Schema() {
      @Override
      public void verify(Connection connection) throws SQLException, IOException {
        release.verifyMorning(connection, expected);
      }

      @Override
      public RootReleaseAdmission.DatabaseInspection inspect(Connection connection)
          throws SQLException, IOException {
        return release.inspectMorningDatabase(connection, expected);
      }
    };
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

  private record RoleObservation(
      String login,
      String effective,
      String database,
      boolean autoCommit,
      boolean jdbcReadOnly,
      int isolation,
      boolean recovery) {}

  private static void admit(Connection connection) throws SQLException, IOException {
    admitObservation(connection);
  }

  private static RoleObservation admitObservation(Connection connection)
      throws SQLException, IOException {
    boolean autoCommit = connection.getAutoCommit();
    boolean readOnly = connection.isReadOnly();
    int isolation = connection.getTransactionIsolation();
    require(autoCommit && !readOnly && isolation == Connection.TRANSACTION_READ_COMMITTED);
    return query(
        connection,
        ROLE,
        rows -> {
          require(rows.next());
          String effective = present(rows.getString("effective_role"));
          String login = present(rows.getString("login_role"));
          String database = present(rows.getString("database_name"));
          boolean recovery = present(rows.getObject("recovery", Boolean.class));
          require(
              "schubert_batch".equals(effective)
                  && "schubert_batch".equals(login)
                  && "schubert_nk".equals(database)
                  && !recovery);
          require(!rows.next());
          return new RoleObservation(
              login, effective, database, autoCommit, readOnly, isolation, recovery);
        });
  }

  private static boolean scalar(Connection connection, String sql)
      throws SQLException, IOException {
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

  @FunctionalInterface
  private interface Bind {
    void apply(PreparedStatement statement) throws SQLException;
  }

  private static <T> T query(Connection connection, String sql, Rows<T> operation)
      throws SQLException, IOException {
    return query(connection, sql, statement -> {}, operation);
  }

  private static <T> T query(Connection connection, String sql, Bind bind, Rows<T> operation)
      throws SQLException, IOException {
    var statement = connection.prepareStatement(sql);
    @Nullable Throwable failure = null;
    try {
      var checked = present(statement);
      checked.setQueryTimeout(5);
      bind.apply(checked);
      var rows = checked.executeQuery();
      @Nullable Throwable rowFailure = null;
      try {
        return operation.read(present(rows));
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
    private @Nullable Instant backupFailureEnded;
    private @Nullable BackupManifest reusedManifest;
    private volatile boolean cleanupVerified;
    private volatile boolean expiryHandoffStarted;
    private @Nullable ExpiryBegins expiryBegins;

    @Override
    public BackupObservation observeBackup(
        BackupBegins expected,
        Optional<BackupManifest> actual,
        Instant now,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      Objects.requireNonNull(expected);
      Objects.requireNonNull(actual);
      Objects.requireNonNull(now);
      Objects.requireNonNull(owner);
      guard();
      if (!backupFinished || !expected.equals(backupBegins) || inHandoff) throw unavailable();
      try {
        if (!connection.getAutoCommit() || connection.isReadOnly() || !scalar(connection, HELD))
          throw unavailable();
        connection.setAutoCommit(false);
        new dev.codex.schubert.nk.batch.cleanup.MaintenanceMutationGuard(owner).bind(connection);
        var current = observeBackupPair(expected, now);
        List<BackupStepRepository.Terminal> prior = List.of();
        if (expected.database().skipped()) {
          var manifest = actual.orElseThrow(() -> unavailable());
          if (!manifest.equals(reusedManifest)
              || new BackupStepRepository(connection).inspect(manifest, now).isEmpty())
            throw unavailable();
          prior =
              observeBackupPair(
                  new BackupBegins(manifest.databaseStep(), manifest.configurationStep()), now);
        } else if (actual.isPresent()) {
          var manifest = actual.orElseThrow();
          if (!manifest.databaseStep().equals(expected.database())
              || !manifest.configurationStep().equals(expected.configuration())
              || new BackupStepRepository(connection).inspect(manifest, now).isEmpty())
            throw unavailable();
        } else {
          var failed =
              new BatchStepResult(
                  BatchStepResult.Status.FAILED,
                  1,
                  0,
                  1,
                  0,
                  BatchStepResult.Reason.COMMAND_FAILURE);
          if (backupFailureEnded == null
              || current.stream()
                  .anyMatch(
                      row ->
                          !row.result().equals(failed) || !row.ended().equals(backupFailureEnded)))
            throw unavailable();
        }
        var observed = new BackupObservation(current, prior);
        guard();
        connection.rollback();
        connection.setAutoCommit(true);
        guard();
        if (!scalar(connection, HELD)) throw unavailable();
        return observed;
      } catch (SQLException | dev.codex.schubert.nk.batch.cleanup.CleanupStoppedException known) {
        throw unavailable();
      }
    }

    private List<BackupStepRepository.Terminal> observeBackupPair(
        BackupBegins expected, Instant now) throws SQLException, IOException {
      require(expected.database().id() != expected.configuration().id());
      boolean databaseFirst = expected.database().id() < expected.configuration().id();
      return query(
          connection,
          "select id,run_id,business_date,step,attempt,started_at,ended_at,status,"
              + "target_count,success_count,failure_count,byte_count,error_code,error_summary"
              + " from schubert.batch_runs where id in (?,?) order by id for update",
          statement -> {
            statement.setLong(1, expected.database().id());
            statement.setLong(2, expected.configuration().id());
          },
          rows -> {
            require(rows.next());
            var first =
                BackupStepRepository.readTerminal(
                    rows, databaseFirst ? expected.database() : expected.configuration(), now);
            require(rows.next());
            var second =
                BackupStepRepository.readTerminal(
                    rows, databaseFirst ? expected.configuration() : expected.database(), now);
            require(!rows.next());
            return databaseFirst ? List.of(first, second) : List.of(second, first);
          });
    }

    private Session(Connection connection) {
      this.connection = connection;
    }

    @Override
    public boolean retainedBackupSuccessful(BackupManifest manifest, Instant now)
        throws IOException {
      Objects.requireNonNull(manifest, "retained backup claim");
      Objects.requireNonNull(now, "retention observation time");
      guard();
      if (!backupFinished || now.isBefore(manifest.contentFinishedAt())) throw unavailable();
      try {
        if (!connection.getAutoCommit() || connection.isReadOnly() || !scalar(connection, HELD))
          throw unavailable();
        schema.verify(connection);
        connection.setAutoCommit(false);
        boolean eligible =
            query(
                connection,
                "select id,status from schubert.batch_runs where id in (?,?) order by id for update",
                statement -> {
                  statement.setLong(1, manifest.databaseStep().id());
                  statement.setLong(2, manifest.configurationStep().id());
                },
                rows -> {
                  Set<Long> seen = new HashSet<>();
                  boolean successful = true;
                  while (rows.next()) {
                    long id = present(rows.getObject("id", Long.class));
                    String status = present(rows.getString("status"));
                    require(
                        (id == manifest.databaseStep().id()
                                || id == manifest.configurationStep().id())
                            && seen.add(id));
                    require(
                        Set.of("RUNNING", "SUCCESS", "FAILED", "WARNING", "SKIPPED")
                            .contains(status));
                    successful &= status.equals("SUCCESS");
                  }
                  return seen.size() == 2 && successful;
                });
        if (eligible && new BackupStepRepository(connection).inspect(manifest, now).isEmpty())
          throw unavailable();
        connection.rollback();
        connection.setAutoCommit(true);
        guard();
        if (!scalar(connection, HELD)) throw unavailable();
        return eligible;
      } catch (SQLException | BatchRepositoryException failure) {
        throw unavailable();
      }
    }

    private void guard() throws IOException {
      if (!active || inHandoff || thread != Thread.currentThread().threadId()) throw unavailable();
      check();
    }

    @Override
    public DatabaseObservation inspectPermitDatabase(
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner) throws IOException {
      Objects.requireNonNull(owner);
      guard();
      owner.check();
      if (!cleanupVerified || !expiryHandoffStarted) throw unavailable();
      try {
        var role = admitObservation(connection);
        boolean held = scalar(connection, HELD);
        if (!held) throw unavailable();
        var actual =
            Objects.requireNonNull(schema.inspect(connection), "actual root schema inspection");
        guard();
        owner.check();
        if (!role.equals(admitObservation(connection)) || !scalar(connection, HELD))
          throw unavailable();
        guard();
        owner.check();
        return new DatabaseObservation(
            role.login(),
            role.effective(),
            role.database(),
            role.autoCommit(),
            role.jdbcReadOnly(),
            role.isolation(),
            role.recovery(),
            held,
            actual);
      } catch (SQLException known) {
        throw unavailable();
      }
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

    /** Latest two SUCCESS rows must be one genuine bundle, never two independent successes. */
    @Override
    public Optional<BackupBegins> successfulBackup(BatchRun run, Instant now) throws IOException {
      Objects.requireNonNull(run, "original run");
      Objects.requireNonNull(now, "observation time");
      BatchStepAttempt.time(run, now);
      guard();
      if (backupCommitted) throw unavailable();
      try {
        schema.verify(connection);
        if (!new RunReferenceRepository(connection).read(run).identityConsistent())
          throw unavailable();
        String sql =
            "select id,business_date,step,attempt,started_at,ended_at,target_count,"
                + "success_count,failure_count,byte_count,error_code,error_summary from schubert.batch_runs "
                + "where run_id=? and step in ('BACKUP_DB','BACKUP_CONFIG') and status='SUCCESS' "
                + "order by started_at desc,id desc limit 2 for update";
        // BUG1251/YKT1017: provider resource null is SQL unavailable, never a leaked NPE.
        Optional<BackupBegins> observed =
            query(
                connection,
                sql,
                statement -> statement.setObject(1, run.id()),
                rows -> {
                  if (!rows.next()) {
                    guard();
                    return Optional.empty();
                  }
                  var first = successfulHandle(rows, run, now);
                  var ended =
                      present(rows.getObject(LITERAL_ENDED_AT, OffsetDateTime.class)).toInstant();
                  if (!rows.next()) throw unavailable();
                  var second = successfulHandle(rows, run, now);
                  var secondEnd =
                      present(rows.getObject(LITERAL_ENDED_AT, OffsetDateTime.class)).toInstant();
                  if (rows.next()
                      || first.step() == second.step()
                      || first.attempt() != second.attempt()
                      || !first.startedAt().equals(second.startedAt())
                      || !ended.equals(secondEnd)) throw unavailable();
                  guard();
                  var pair =
                      first.step() == BatchStep.BACKUP_DB
                          ? new BackupBegins(first, second)
                          : new BackupBegins(second, first);
                  guard();
                  return Optional.of(pair);
                });
        guard(); // Close every JDBC resource before allowing an observed pair to escape.
        return observed;
      } catch (SQLException failure) {
        throw unavailable();
      }
    }

    private BatchStepAttempt successfulHandle(ResultSet rows, BatchRun run, Instant now)
        throws SQLException, IOException {
      var step = BatchStep.valueOf(present(rows.getString("step")));
      if (!step.backup()) throw unavailable();
      Instant started = present(rows.getObject("started_at", OffsetDateTime.class)).toInstant();
      Instant ended = present(rows.getObject(LITERAL_ENDED_AT, OffsetDateTime.class)).toInstant();
      long count = step == BatchStep.BACKUP_DB ? 1 : 2;
      if (!present(rows.getObject("business_date", LocalDate.class))
              .equals(run.cutoff().atZone(ZoneId.of("Asia/Tokyo")).toLocalDate())
          || started.isAfter(ended)
          || ended.isAfter(now)
          || ended.getNano() % 1000 != 0
          || present(rows.getObject("target_count", Long.class)) != count
          || present(rows.getObject("success_count", Long.class)) != count
          || present(rows.getObject("failure_count", Long.class)) != 0
          || present(rows.getObject("byte_count", Long.class)) <= 0
          || rows.getString("error_code") != null
          || rows.getString("error_summary") != null) throw unavailable();
      return new BatchStepAttempt(
          present(rows.getObject("id", Long.class)),
          run,
          step,
          present(rows.getObject("attempt", Integer.class)),
          started,
          false);
    }

    @Override
    public BackupBegins beginResumeBackup(BackupManifest original, Instant now) throws IOException {
      Objects.requireNonNull(original, "root verified prior manifest");
      Objects.requireNonNull(now, "current skip time");
      var prior = new BackupBegins(original.databaseStep(), original.configurationStep());
      if (!successfulBackup(original.run(), now).equals(Optional.of(prior))) throw unavailable();
      try {
        if (new BackupStepRepository(connection).inspect(original, now).isEmpty())
          throw unavailable();
        var repository = new BatchRunRepository(connection);
        var db = repository.beginMorningResume(original.run(), BatchStep.BACKUP_DB, now, true);
        var config =
            repository.beginMorningResume(original.run(), BatchStep.BACKUP_CONFIG, now, true);
        if (!db.skipped() || !config.skipped()) throw unavailable();
        guard();
        connection.commit();
        guard();
        connection.setAutoCommit(true);
        guard();
        var result = new BackupBegins(db, config);
        backupBegins = result;
        reusedManifest = original;
        backupCommitted = true;
        return result;
      } catch (SQLException failure) {
        throw unavailable();
      }
    }

    @Override
    public void completeReusedBackup(BackupBegins expected, BackupManifest original, Instant now)
        throws IOException {
      Objects.requireNonNull(expected, "current skipped pair");
      Objects.requireNonNull(original, "same reverified original manifest");
      Objects.requireNonNull(now, "fresh observation time");
      if (!original.equals(reusedManifest)
          || !expected.database().skipped()
          || !expected.configuration().skipped()) throw unavailable();
      try {
        completionGuard(expected);
        connection.setAutoCommit(false);
        var repository = new BatchRunRepository(connection);
        repository.verifyAlreadySuccessful(expected.database());
        repository.verifyAlreadySuccessful(expected.configuration());
        if (new BackupStepRepository(connection).inspect(original, now).isEmpty())
          throw unavailable();
        guard();
        connection.rollback();
        connection.setAutoCommit(true);
        completionGuard(expected);
        backupFinished = true;
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
        var statement = connection.createStatement();
        @Nullable Throwable failure = null;
        try {
          present(statement).execute("SET TRANSACTION READ ONLY");
        } catch (SQLException | RuntimeException | Error primary) {
          failure = primary;
          throw primary;
        } finally {
          if (statement != null) {
            try {
              statement.close();
            } catch (SQLException | RuntimeException | Error secondary) {
              if (JdbcResourceFailures.replace(failure, secondary)) throw secondary;
            }
          }
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
        query(
            connection,
            sql,
            statement -> {
              statement.setObject(1, previous.run());
              statement.setObject(
                  2,
                  java.time.OffsetDateTime.ofInstant(previous.started(), java.time.ZoneOffset.UTC));
            },
            rows -> {
              for (var current : java.util.List.of(expected.configuration(), expected.database())) {
                if (!rows.next()) throw unavailable();
                var ended =
                    present(rows.getObject(LITERAL_ENDED_AT, java.time.OffsetDateTime.class))
                        .toInstant();
                if (!current.step().name().equals(present(rows.getString("step")))
                    || present(rows.getObject("attempt", Integer.class)) >= current.attempt()
                    || !"FAILED".equals(present(rows.getString("status")))
                    || !"ABANDONED".equals(present(rows.getString("error_code")))
                    || ended.isBefore(previous.started())
                    || ended.isAfter(current.startedAt())
                    || !run.cutoff()
                        .atZone(java.time.ZoneId.of("Asia/Tokyo"))
                        .toLocalDate()
                        .equals(
                            present(rows.getObject("business_date", java.time.LocalDate.class))))
                  throw unavailable();
              }
              if (rows.next()) throw unavailable();
              return Boolean.TRUE;
            });
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
        if (database.equals(
                new BatchStepResult(
                    BatchStepResult.Status.FAILED,
                    1,
                    0,
                    1,
                    0,
                    BatchStepResult.Reason.COMMAND_FAILURE))
            && configuration.equals(database)) backupFailureEnded = endedAt;
      } catch (SQLException failure) {
        throw unavailable();
      }
    }

    /**
     * One synchronous lock transfer; caller still owns M/A, child terminal proof and backup files.
     */
    @Override
    public BackupFailureSnapshot failedBackupSnapshot(
        BackupBegins expected, dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      Objects.requireNonNull(expected);
      Objects.requireNonNull(owner);
      Instant ended = backupFailureEnded;
      if (!backupFinished || ended == null || handoffStarted) throw unavailable();
      var snapshot =
          new BackupFailureSnapshot(expected.database(), expected.configuration(), ended);
      try {
        failedObservationGuard(expected);
        owner.check();
        if (!connection.getAutoCommit() || connection.isReadOnly()) throw unavailable();
        connection.setAutoCommit(false);
        new dev.codex.schubert.nk.batch.cleanup.MaintenanceMutationGuard(owner).bind(connection);
        snapshot.verifyLatest(connection, owner);
        guard();
        connection.rollback();
        connection.setAutoCommit(true);
        failedObservationGuard(expected);
        owner.check();
        return snapshot;
      } catch (SQLException
          | BatchRepositoryException
          | dev.codex.schubert.nk.batch.cleanup.CleanupStoppedException known) {
        throw unavailable();
      }
    }

    private void failedObservationGuard(BackupBegins expected) throws IOException, SQLException {
      guard();
      if (!backupCommitted
          || !backupFinished
          || backupFailureEnded == null
          || handoffStarted
          || !expected.equals(backupBegins)
          || !connection.getAutoCommit()
          || connection.isReadOnly()
          || connection.getTransactionIsolation() != Connection.TRANSACTION_READ_COMMITTED
          || !scalar(connection, HELD)) throw unavailable();
      guard();
    }

    public <T> T handoffCleanup(CleanupHandoff<T> operation) throws IOException {
      Objects.requireNonNull(operation, "cleanup child operation");
      guard();
      if (!backupFinished || handoffStarted) throw unavailable();
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

    @Override
    public ExpiryBegins beginExpiry(
        BatchRun run,
        Instant now,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      Objects.requireNonNull(run);
      return beginExpiry(
          run,
          now,
          owner,
          (id, time) -> {
            if (!id.equals(run.id())) throw unavailable();
            return run;
          });
    }

    @Override
    public ExpiryBegins beginExpiry(
        BatchRun run,
        Instant now,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner,
        SuccessRunLookup originals)
        throws IOException {
      Objects.requireNonNull(run);
      Objects.requireNonNull(now);
      Objects.requireNonNull(owner);
      Objects.requireNonNull(originals);
      guard();
      if (!cleanupVerified
          || expiryHandoffStarted
          || expiryBegins != null
          || backupBegins == null
          || !run.equals(backupBegins.database().run())) throw unavailable();
      try {
        owner.check();
        if (!connection.getAutoCommit() || connection.isReadOnly()) throw unavailable();
        connection.setAutoCommit(false);
        new dev.codex.schubert.nk.batch.cleanup.MaintenanceMutationGuard(owner).bind(connection);
        var prior = new ExpiryAuditRepository(connection).successful(run, now, owner, originals);
        var repository = new BatchRunRepository(connection);
        var current = repository.begin(run, BatchStep.CLEAN_EXPIRY, now, true);
        if (current.skipped() != prior.isPresent()) throw unavailable();
        var begins = new ExpiryBegins(current, prior);
        guard();
        owner.check();
        connection.commit();
        guard();
        owner.check();
        connection.setAutoCommit(true);
        connection.setAutoCommit(false);
        new dev.codex.schubert.nk.batch.cleanup.MaintenanceMutationGuard(owner).bind(connection);
        if (current.skipped()) {
          repository.verifyAlreadySuccessful(current);
          var original = prior.orElseThrow();
          if (!new ExpiryAuditRepository(connection)
              .read(original.handle())
              .equals(Optional.of(original.audit()))) throw unavailable();
        } else {
          var initial =
              new ExpiryAuditRepository.Snapshot(
                  "RUNNING", null, null, null, 0, 0, 0, 0, null, null, null);
          if (!new ExpiryAuditRepository(connection).read(current).equals(Optional.of(initial)))
            throw unavailable();
        }
        guard();
        owner.check();
        connection.rollback();
        connection.setAutoCommit(true);
        guard();
        owner.check();
        expiryBegins = begins;
        return begins;
      } catch (SQLException
          | BatchRepositoryException
          | dev.codex.schubert.nk.batch.cleanup.CleanupStoppedException known) {
        throw unavailable();
      }
    }

    @Override
    public <T> T handoffExpiry(CleanupHandoff<T> operation) throws IOException {
      Objects.requireNonNull(operation);
      guard();
      if (!cleanupVerified || expiryBegins == null || expiryHandoffStarted) throw unavailable();
      try {
        if (!connection.getAutoCommit()) throw unavailable();
        expiryHandoffStarted = true;
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
      } catch (SQLException | InspectorLockHandoff.Failure known) {
        throw unavailable();
      } finally {
        inHandoff = false;
      }
    }

    @Override
    public ExpiryObservation observeExpiry(
        ExpiryBegins begins,
        dev.codex.schubert.nk.batch.platform.BackupUnitReceiptGate.TerminalReceipt receipt,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      Objects.requireNonNull(begins);
      Objects.requireNonNull(receipt);
      Objects.requireNonNull(owner);
      guard();
      if (!cleanupVerified
          || !expiryHandoffStarted
          || !begins.equals(expiryBegins)
          || receipt.target()
              != dev.codex.schubert.nk.batch.platform.BackupUnitStartClient.Target.EXPIRY)
        throw unavailable();
      try {
        owner.check();
        if (!connection.getAutoCommit() || connection.isReadOnly()) throw unavailable();
        connection.setAutoCommit(false);
        new dev.codex.schubert.nk.batch.cleanup.MaintenanceMutationGuard(owner).bind(connection);
        var audit = new ExpiryAuditRepository(connection);
        ExpiryAuditRepository.Snapshot actual;
        Instant ended;
        BatchStepResult result;
        if (begins.current().skipped()) {
          if (receipt.exitCode() != 0) throw unavailable();
          new BatchRunRepository(connection).verifyAlreadySuccessful(begins.current());
          var prior = begins.prior().orElseThrow();
          actual = audit.read(prior.handle()).orElseThrow(BatchRepositoryException::new);
          if (!actual.equals(prior.audit())) throw unavailable();
          ended = begins.current().startedAt();
          result =
              new BatchStepResult(
                  BatchStepResult.Status.SKIPPED,
                  0,
                  0,
                  0,
                  0,
                  BatchStepResult.Reason.ALREADY_SUCCESSFUL);
        } else {
          actual = audit.read(begins.current()).orElseThrow(BatchRepositoryException::new);
          int code =
              "SUCCESS".equals(actual.status())
                  ? 0
                  : "WARNING".equals(actual.status())
                      ? 10
                      : "FAILED".equals(actual.status()) ? 30 : -1;
          if (code != receipt.exitCode() || actual.ended() == null) throw unavailable();
          ended = Objects.requireNonNull(actual.ended());
          result =
              new BatchStepResult(
                  BatchStepResult.Status.valueOf(actual.status()),
                  actual.target(),
                  actual.success(),
                  actual.failure(),
                  actual.estimatedBytes(),
                  actual.errorCode() == null
                      ? BatchStepResult.Reason.NONE
                      : switch (Objects.requireNonNull(actual.errorCode())) {
                        case "COMMAND_FAILURE" -> BatchStepResult.Reason.COMMAND_FAILURE;
                        case "SAFETY_FAILURE" -> BatchStepResult.Reason.SAFETY_FAILURE;
                        default -> throw unavailable();
                      });
          new BatchRunRepository(connection).verifyFinished(begins.current(), ended, result);
        }
        guard();
        owner.check();
        connection.rollback();
        connection.setAutoCommit(true);
        guard();
        owner.check();
        return new ExpiryObservation(begins, ended, result, actual, receipt);
      } catch (SQLException
          | BatchRepositoryException
          | dev.codex.schubert.nk.batch.cleanup.CleanupStoppedException known) {
        throw unavailable();
      }
    }

    /** Narrow typed30, partial data only, never a successful completion or new DB attempt. */
    @Override
    public CleanupTerminalRepository.RejectedSnapshot observeCleanupRejected(
        BatchRun run,
        dev.codex.schubert.nk.batch.platform.BackupUnitReceiptGate.TerminalReceipt receipt,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      Objects.requireNonNull(run);
      Objects.requireNonNull(receipt);
      Objects.requireNonNull(owner);
      guard();
      if (!backupFinished
          || !handoffStarted
          || receipt.target()
              != dev.codex.schubert.nk.batch.platform.BackupUnitStartClient.Target.CLEANUP
          || receipt.exitCode() != 30) throw unavailable();
      try {
        owner.check();
        if (!connection.getAutoCommit() || connection.isReadOnly()) throw unavailable();
        connection.setAutoCommit(false);
        new dev.codex.schubert.nk.batch.cleanup.MaintenanceMutationGuard(owner).bind(connection);
        var repository = new CleanupTerminalRepository(connection, owner);
        var observed =
            repository.readRejected(
                run, Instant.now().truncatedTo(java.time.temporal.ChronoUnit.MICROS));
        if (!observed.equals(
            repository.readRejected(
                run, Instant.now().truncatedTo(java.time.temporal.ChronoUnit.MICROS))))
          throw unavailable();
        guard();
        owner.check();
        connection.rollback();
        connection.setAutoCommit(true);
        guard();
        owner.check();
        return observed;
      } catch (SQLException
          | BatchRepositoryException
          | dev.codex.schubert.nk.batch.cleanup.CleanupStoppedException known) {
        throw unavailable();
      }
    }

    /**
     * SSC126: current full rows are rechecked under A before reading distinct original references.
     */
    @Override
    public java.util.List<Optional<CleanupTerminalRepository.Entry>> cleanupReferences(
        CleanupTerminalRepository.Snapshot expected,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      Objects.requireNonNull(expected);
      var run = expected.entries().getFirst().attempt().run();
      return cleanupReferences(expected, owner, currentRunReference(run));
    }

    @Override
    public java.util.List<Optional<CleanupTerminalRepository.Entry>> cleanupReferences(
        CleanupTerminalRepository.Snapshot expected,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner,
        SuccessRunLookup originals)
        throws IOException {
      Objects.requireNonNull(expected);
      Objects.requireNonNull(owner);
      Objects.requireNonNull(originals);
      guard();
      if (!cleanupVerified || !handoffStarted) throw unavailable();
      var run = expected.entries().getFirst().attempt().run();
      try {
        owner.check();
        if (!connection.getAutoCommit() || connection.isReadOnly()) throw unavailable();
        connection.setAutoCommit(false);
        new dev.codex.schubert.nk.batch.cleanup.MaintenanceMutationGuard(owner).bind(connection);
        var repository = new CleanupTerminalRepository(connection, owner);
        var now = Instant.now().truncatedTo(java.time.temporal.ChronoUnit.MICROS);
        var actual =
            backupFailureEnded == null
                ? repository.read(run, now)
                : repository.readBackupUnavailable(run, now);
        if (!expected.equals(actual)) throw unavailable();
        var references = repository.references(actual, originals);
        guard();
        owner.check();
        connection.rollback();
        connection.setAutoCommit(true);
        guard();
        owner.check();
        return references;
      } catch (SQLException
          | BatchRepositoryException
          | dev.codex.schubert.nk.batch.cleanup.CleanupStoppedException known) {
        throw unavailable();
      }
    }

    /** Exact current results only after the sole child handoff has returned/reacquired. */
    @Override
    public CleanupTerminalRepository.Snapshot observeCleanup(
        BatchRun run,
        int receipt,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      return observeCleanup(run, receipt, owner, false);
    }

    @Override
    public CleanupTerminalRepository.Snapshot observeCleanupBackupUnavailable(
        BatchRun run,
        int receipt,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
        throws IOException {
      return observeCleanup(run, receipt, owner, true);
    }

    private CleanupTerminalRepository.Snapshot observeCleanup(
        BatchRun run,
        int receipt,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner,
        boolean failedBackup)
        throws IOException {
      Objects.requireNonNull(run, "original Cleanup run");
      Objects.requireNonNull(owner, "same parent deadline");
      guard();
      if (!backupFinished
          || !handoffStarted
          || (receipt != 0 && receipt != 10)
          || failedBackup != (backupFailureEnded != null)) throw unavailable();
      try {
        owner.check();
        if (!connection.getAutoCommit() || connection.isReadOnly()) throw unavailable();
        connection.setAutoCommit(false);
        new dev.codex.schubert.nk.batch.cleanup.MaintenanceMutationGuard(owner).bind(connection);
        var terminal = new CleanupTerminalRepository(connection, owner);
        var observedAt = Instant.now().truncatedTo(java.time.temporal.ChronoUnit.MICROS);
        var observed =
            failedBackup
                ? terminal.readBackupUnavailable(run, observedAt)
                : terminal.read(run, observedAt);
        if (observed.exitCode() != receipt) throw unavailable();
        var repository = new BatchRunRepository(connection);
        for (var row : observed.entries()) {
          if (row.result().reason() == BatchStepResult.Reason.BACKUP_UNAVAILABLE)
            repository.verifyBackupUnavailable(row.attempt());
          else if (row.attempt().skipped()) repository.verifyAlreadySuccessful(row.attempt());
          else repository.verifyFinished(row.attempt(), row.endedAt(), row.result());
        }
        guard();
        owner.check();
        connection.rollback();
        connection.setAutoCommit(true);
        guard();
        owner.check();
        cleanupVerified = true;
        return observed;
      } catch (SQLException
          | BatchRepositoryException
          | dev.codex.schubert.nk.batch.cleanup.CleanupStoppedException known) {
        throw unavailable();
      }
    }
  }

  /** Data-only default reference; not an original-session capability or administrative lookup. */
  static SuccessRunLookup currentRunReference(BatchRun run) {
    Objects.requireNonNull(run, "current run reference");
    return (id, observed) -> {
      if (!id.equals(run.id())) throw unavailable();
      return run;
    };
  }
}
