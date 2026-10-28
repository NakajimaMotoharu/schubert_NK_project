package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.backup.BackupFileDigest;
import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.backup.BackupVersions;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Properties;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** MDB001..011. Literal role/lock oracle; actual isolated DB transaction/lock in MDB007..011. */
final class MorningDatabaseSessionTest {
  private static final String FIXTURE_012D_02D3076F = "%012d";
  private static final String FIXTURE_ID_BUSINESS_DATE_STEP_ATTEMPT_STARTED_AT_F3540697 =
      " id,business_date,step,attempt,started_at,ended_at,target_count,";
  private static final String FIXTURE_GETAUTOCOMMIT_C0200BDE = "getAutoCommit";
  private static final String FIXTURE_GETTRANSACTIONISOLATION_6ED78CE6 = "getTransactionIsolation";
  private static final String FIXTURE_RUNNING_294BDBF9 = "RUNNING";
  private static final String FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891 =
      "root batch database unavailable";
  private static final String FIXTURE_NONE_C44E6DD7 = "NONE";
  private static final String FIXTURE_SQL_5B7E398D = "SQL";
  private static final String FIXTURE_IAE_C355C351 = "IAE";
  private static final String FIXTURE_CLOSE_3CA44CAE = "CLOSE";
  private static final String FIXTURE_STATE_053339C0 = "STATE";
  private static final String FIXTURE_ERROR_F717E7D8 = "ERROR";
  private static final String FIXTURE_PRIMARY_9466F7E5 = "PRIMARY";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  private static final String FIXTURE_FAILED_7E8A57FE = "FAILED";
  private static final String FIXTURE_STATEMENT_8A602677 = "STATEMENT";
  private static final String FIXTURE_PREPARESTATEMENT_CB987D1F = "prepareStatement";
  private static final String FIXTURE_SELECT_8DAC6259 = "select";
  private static final String FIXTURE_EXECUTEQUERY_85C8C423 = "executeQuery";
  private static final String FIXTURE_GETOBJECT_B6112877 = "getObject";
  private static final String FIXTURE_FAILURE_COUNT_C7E67F21 = "failure_count";
  private static final String FIXTURE_PGPT_ADMIN_F5D1227C = "pgpt_admin";
  private static final String FIXTURE_BACKUP_CONFIG_8386D7E7 = "BACKUP_CONFIG";
  private static final String FIXTURE_BACKUP_DB_6C03A087 = "BACKUP_DB";
  private static final String FIXTURE_STARTED_AT_D1210657 = "started_at";
  private static final String FIXTURE_ENDED_AT_E151E393 = "ended_at";
  private static final String FIXTURE_COMMIT_5EA9C586 = "commit";
  private static final String FIXTURE_NEXT_CA1733B5 = "next";
  private static final String FIXTURE_BEGIN_RESUME_CA1CD26C = "BEGIN_RESUME";
  private static final String FIXTURE_SKIPPED_OBSERVE_FB5C359C = "SKIPPED_OBSERVE";
  private static final String FIXTURE_SUCCESS_10855C7F = "SUCCESS";
  private static final String FIXTURE_GETSTRING_B3B802ED = "getString";
  private static final String FIXTURE_STATUS_CFC31BCC = "status";
  private static final String FIXTURE_ERROR_CODE_B886CCEF = "error_code";
  private static final String FIXTURE_ERROR_SUMMARY_3F58BF23 = "error_summary";
  private static final String FIXTURE_TARGET_COUNT_5B6567D4 = "target_count";
  private static final String FIXTURE_SUCCESS_COUNT_716E5185 = "success_count";
  private static final String FIXTURE_BYTE_COUNT_6D76E237 = "byte_count";
  static final String URL = "jdbc:postgresql://127.0.0.1:5432/schubert_nk";
  static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("31100000-2222-4333-8444-555555555555"),
          Instant.parse("2026-09-27T15:00:00Z"));
  static final Instant NOW = Instant.parse("2026-09-28T02:00:00Z");
  @TempDir static Path directory;
  static BatchDatabaseFixture db;
  static String actualUrl;

  /** PT-MDB-3256-001: a failed DB completion guard cannot reach any backup-file work. */
  @Test
  void mdb3256001CompletionGuardSqlFailurePreservesCommittedBeginsAndEmptyBackupRoot()
      throws Exception {
    int ordinal = 0;
    for (String methodFault :
        List.of(FIXTURE_GETAUTOCOMMIT_C0200BDE, FIXTURE_GETTRANSACTIONISOLATION_6ED78CE6)) {
      int n = ++ordinal;
      var run =
          new BatchRun(
              UUID.fromString("32560001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
              Instant.parse("2058-04-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      Instant started = run.cutoff().plusSeconds(11 * 3600);
      var armed = new AtomicBoolean();
      var injected = new AtomicInteger();
      var retained = new AtomicReference<Connection>();
      Path empty = java.nio.file.Files.createDirectory(directory.resolve("mdb3256-empty-" + n));
      long uid = ((Number) java.nio.file.Files.getAttribute(empty, "unix:uid")).longValue();
      long gid = ((Number) java.nio.file.Files.getAttribute(empty, "unix:gid")).longValue();
      assertTrue(
          uid > 0 && gid > 0); // Existing isolated nonroot PT toolchain, never root authority.
      try (var root =
          dev.codex.schubert.nk.storage.OwnedTransferDirectory.open(
              dev.codex.schubert.nk.storage.LinuxDirectoryCalls.create(), empty)) {
        var completion =
            new dev.codex.schubert.nk.batch.file.BackupBundleCompletion(
                root, dev.codex.schubert.nk.storage.LinuxInodeSecurity.create(), uid, gid);
        var subject =
            new MorningDatabaseSession(
                actualUrl,
                () -> {},
                (url, properties) -> {
                  var actual = DriverManager.getConnection(url, properties);
                  retained.set(actual);
                  return (Connection)
                      Proxy.newProxyInstance(
                          Connection.class.getClassLoader(),
                          new Class<?>[] {Connection.class},
                          (unused, method, args) -> {
                            if (armed.get() && method.getName().equals(methodFault)) {
                              injected.incrementAndGet();
                              throw new SQLException("PT3256_COMPLETION_GUARD", "XX000");
                            }
                            return mdb2292Invoke(method, actual, args);
                          });
                },
                connection -> {});
        var failure =
            assertThrows(
                IOException.class,
                () ->
                    subject.execute(
                        credential(),
                        session -> {
                          var begins = session.beginBackup(run, started, false);
                          mdb2292Rows(run, FIXTURE_RUNNING_294BDBF9, started, Optional.empty());
                          armed.set(true);
                          session.completeBackup(begins, completion, "no-file-work-authorized");
                          fail("failed DB guard cannot authorize completion or file lookup");
                          return Boolean.TRUE;
                        }));
        assertEquals(FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, failure.getMessage());
        assertNull(failure.getCause());
        assertEquals(0, failure.getSuppressed().length);
        assertEquals(1, injected.get());
        assertNotNull(retained.get());
        assertTrue(retained.get().isClosed());
        try (var entries = java.nio.file.Files.list(empty)) {
          assertEquals(0, entries.count());
        }
        mdb2292Rows(run, FIXTURE_RUNNING_294BDBF9, started, Optional.empty());
        mdb2292NoOwnerResources();
      }
    }
  }

  /** PT-MDB-3254-001/SS332 SSC063: real read-only statement, independent fixed priority table. */
  @Test
  void mdb3254001ReadOnlyStatementCompoundFailuresKeepRowsAndCloseEveryOwner() throws Exception {
    // Primary / close / public winner / sanitized secondary count / optional SAME.
    // Literal SS priority oracle; never call JdbcResourceFailures for expected.
    String[][] vectors = {
      {FIXTURE_NONE_C44E6DD7, FIXTURE_SQL_5B7E398D, "IO", "0"},
      {FIXTURE_NONE_C44E6DD7, FIXTURE_IAE_C355C351, FIXTURE_CLOSE_3CA44CAE, "0"},
      {FIXTURE_NONE_C44E6DD7, FIXTURE_STATE_053339C0, FIXTURE_CLOSE_3CA44CAE, "0"},
      {FIXTURE_NONE_C44E6DD7, FIXTURE_ERROR_F717E7D8, FIXTURE_CLOSE_3CA44CAE, "0"},
      {FIXTURE_SQL_5B7E398D, FIXTURE_NONE_C44E6DD7, "IO", "0"},
      {FIXTURE_SQL_5B7E398D, FIXTURE_SQL_5B7E398D, "IO", "0"},
      {FIXTURE_SQL_5B7E398D, FIXTURE_IAE_C355C351, FIXTURE_CLOSE_3CA44CAE, "0"},
      {FIXTURE_SQL_5B7E398D, FIXTURE_STATE_053339C0, FIXTURE_CLOSE_3CA44CAE, "0"},
      {FIXTURE_SQL_5B7E398D, FIXTURE_ERROR_F717E7D8, FIXTURE_CLOSE_3CA44CAE, "0"},
      {FIXTURE_IAE_C355C351, FIXTURE_NONE_C44E6DD7, FIXTURE_PRIMARY_9466F7E5, "0"},
      {FIXTURE_IAE_C355C351, FIXTURE_SQL_5B7E398D, FIXTURE_PRIMARY_9466F7E5, "1"},
      {FIXTURE_IAE_C355C351, FIXTURE_IAE_C355C351, FIXTURE_PRIMARY_9466F7E5, "1"},
      {FIXTURE_IAE_C355C351, FIXTURE_STATE_053339C0, FIXTURE_PRIMARY_9466F7E5, "1"},
      {FIXTURE_IAE_C355C351, FIXTURE_ERROR_F717E7D8, FIXTURE_PRIMARY_9466F7E5, "1"},
      {FIXTURE_STATE_053339C0, FIXTURE_NONE_C44E6DD7, FIXTURE_PRIMARY_9466F7E5, "0"},
      {FIXTURE_STATE_053339C0, FIXTURE_SQL_5B7E398D, FIXTURE_PRIMARY_9466F7E5, "1"},
      {FIXTURE_STATE_053339C0, FIXTURE_IAE_C355C351, FIXTURE_PRIMARY_9466F7E5, "1"},
      {FIXTURE_STATE_053339C0, FIXTURE_STATE_053339C0, FIXTURE_PRIMARY_9466F7E5, "1"},
      {FIXTURE_STATE_053339C0, FIXTURE_ERROR_F717E7D8, FIXTURE_PRIMARY_9466F7E5, "1"},
      {FIXTURE_ERROR_F717E7D8, FIXTURE_NONE_C44E6DD7, FIXTURE_PRIMARY_9466F7E5, "0"},
      {FIXTURE_ERROR_F717E7D8, FIXTURE_SQL_5B7E398D, FIXTURE_PRIMARY_9466F7E5, "1"},
      {FIXTURE_ERROR_F717E7D8, FIXTURE_IAE_C355C351, FIXTURE_PRIMARY_9466F7E5, "1"},
      {FIXTURE_ERROR_F717E7D8, FIXTURE_STATE_053339C0, FIXTURE_PRIMARY_9466F7E5, "1"},
      {FIXTURE_ERROR_F717E7D8, FIXTURE_ERROR_F717E7D8, FIXTURE_PRIMARY_9466F7E5, "1"},
      {FIXTURE_SQL_5B7E398D, FIXTURE_SQL_5B7E398D, "IO", "0", "SAME"},
      {FIXTURE_STATE_053339C0, FIXTURE_STATE_053339C0, FIXTURE_PRIMARY_9466F7E5, "1", "SAME"},
      {FIXTURE_ERROR_F717E7D8, FIXTURE_ERROR_F717E7D8, FIXTURE_PRIMARY_9466F7E5, "1", "SAME"}
    };
    assertEquals(27, vectors.length);
    int ordinal = 0;
    for (String[] vector : vectors) {
      int n = ++ordinal;
      var run =
          new BatchRun(
              UUID.fromString("32540001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
              Instant.parse("2057-04-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      Instant started = run.cutoff().plusSeconds(11 * 3600);
      Instant ended = started.plusSeconds(2);
      var failed =
          new BatchStepResult(
              BatchStepResult.Status.FAILED, 1, 0, 1, 0, BatchStepResult.Reason.COMMAND_FAILURE);
      var primary = mdb3254Fault(vector[0]);
      var closing = vector.length == 5 ? primary : mdb3254Fault(vector[1]);
      var expected = vector[2].equals(FIXTURE_PRIMARY_9466F7E5) ? primary : closing;
      Class<? extends Throwable> expectedType =
          vector[2].equals("IO") ? IOException.class : expected.orElseThrow().getClass();
      var armed = new AtomicBoolean();
      var retained = new AtomicReference<Connection>();
      var borrowed = new AtomicReference<MorningDatabaseSession.Access>();
      var executes = new AtomicInteger();
      var readOnlyProofs = new AtomicInteger();
      var statementCloses = new AtomicInteger();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var actual = DriverManager.getConnection(url, properties);
                retained.set(actual);
                return (Connection)
                    Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          Object result = mdb2292Invoke(method, actual, args);
                          if (!armed.get() || !method.getName().equals("createStatement"))
                            return result;
                          var statement = (Statement) result;
                          return Proxy.newProxyInstance(
                              Statement.class.getClassLoader(),
                              new Class<?>[] {Statement.class},
                              (unusedStatement, called, values) -> {
                                Object value = mdb2292Invoke(called, statement, values);
                                if (called.getName().equals("execute")) {
                                  assertEquals("SET TRANSACTION READ ONLY", values[0]);
                                  executes.incrementAndGet();
                                  // A separate real-driver observer proves the server flag;
                                  // JDBC configured-readOnly remains false by design.
                                  try (var observer = actual.createStatement();
                                      var rows =
                                          observer.executeQuery("SHOW transaction_read_only")) {
                                    assertTrue(rows.next());
                                    assertEquals("on", rows.getString(1));
                                    assertFalse(rows.next());
                                  }
                                  readOnlyProofs.incrementAndGet();
                                  if (primary.isPresent()) throw primary.orElseThrow();
                                }
                                if (called.getName().equals(FIXTURE_CLOSE_97959247)) {
                                  assertTrue(statement.isClosed());
                                  statementCloses.incrementAndGet();
                                  if (closing.isPresent()) throw closing.orElseThrow();
                                }
                                return value;
                              });
                        });
              },
              connection -> {});
      try {
        var actual =
            assertThrows(
                expectedType,
                () ->
                    subject.execute(
                        credential(),
                        session -> {
                          borrowed.set(session);
                          var begins = session.beginBackup(run, started, false);
                          session.failBackup(begins, ended, failed, failed);
                          mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(ended));
                          armed.set(true);
                          session.recheckConsistent(run);
                          fail("execute/close fault must never return a consistent proof");
                          return Boolean.TRUE;
                        }));
        assertEquals(expectedType, actual.getClass());
        if (vector[2].equals("IO")) {
          assertEquals(FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, actual.getMessage());
          assertNull(actual.getCause());
        } else assertSame(expected.orElseThrow(), actual);
        assertEquals(Integer.parseInt(vector[3]), actual.getSuppressed().length);
        for (Throwable safe : actual.getSuppressed()) {
          assertEquals(BatchRepositoryException.class, safe.getClass());
          assertEquals("batch repository operation failed", safe.getMessage());
          assertNull(safe.getCause());
          assertEquals(0, safe.getSuppressed().length);
        }
      } finally {
        assertEquals(1, executes.get());
        assertEquals(1, readOnlyProofs.get());
        assertEquals(1, statementCloses.get());
        assertNotNull(retained.get());
        assertTrue(retained.get().isClosed());
        assertNotNull(borrowed.get());
        assertThrows(IOException.class, () -> borrowed.get().recheckConsistent(run));
        mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(ended));
        mdb2292NoOwnerResources();
      }
    }
  }

  private static Optional<Throwable> mdb3254Fault(String kind) {
    return switch (kind) {
      case FIXTURE_NONE_C44E6DD7 -> Optional.empty();
      case FIXTURE_SQL_5B7E398D -> Optional.of(new SQLException("PT3254_SQL_DRIVER", "XX000"));
      case FIXTURE_IAE_C355C351 -> Optional.of(new IllegalArgumentException("PT3254_IAE_DRIVER"));
      case FIXTURE_STATE_053339C0 -> Optional.of(new IllegalStateException("PT3254_STATE_DRIVER"));
      case FIXTURE_ERROR_F717E7D8 -> Optional.of(new AssertionError("PT3254_ERROR_DRIVER"));
      default -> throw new AssertionError("fixed independent fault kind required");
    };
  }

  /** PT-MDB-2804-001: checked IO owns precedence; SQL close details never escape. */
  @Test
  void mdb2804001CheckedCallbackAndCompoundJdbcClosePreserveRowsAndRedactSecondary()
      throws Exception {
    int ordinal = 0;
    for (String fault : List.of("ROWS", FIXTURE_STATEMENT_8A602677, "BOTH")) {
      int n = ++ordinal;
      var run =
          new BatchRun(
              UUID.fromString("28040001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
              Instant.parse("2052-03-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = run.cutoff().plusSeconds(11 * 3600);
      long id = 28040010L + n * 10;
      mdb2480Seed(run, started, id);
      var retained = new AtomicReference<Connection>();
      var projected = new AtomicInteger();
      var rowCloses = new AtomicInteger();
      var statementCloses = new AtomicInteger();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var real = DriverManager.getConnection(url, properties);
                retained.set(real);
                return (Connection)
                    Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          Object value = mdb2292Invoke(method, real, args);
                          if (!method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                              || !((String) args[0])
                                  .startsWith(
                                      FIXTURE_SELECT_8DAC6259
                                          + FIXTURE_ID_BUSINESS_DATE_STEP_ATTEMPT_STARTED_AT_F3540697))
                            return value;
                          var statement = (PreparedStatement) value;
                          return Proxy.newProxyInstance(
                              PreparedStatement.class.getClassLoader(),
                              new Class<?>[] {PreparedStatement.class},
                              (unusedStatement, called, input) -> {
                                Object actual = mdb2292Invoke(called, statement, input);
                                if (called.getName().equals(FIXTURE_CLOSE_97959247)) {
                                  statementCloses.incrementAndGet();
                                  if (!fault.equals("ROWS"))
                                    throw new SQLException("PRIVATE_STATEMENT_CLOSE");
                                }
                                if (!called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423))
                                  return actual;
                                var rows = (ResultSet) actual;
                                return Proxy.newProxyInstance(
                                    ResultSet.class.getClassLoader(),
                                    new Class<?>[] {ResultSet.class},
                                    (unusedRows, read, values) -> {
                                      Object observed = mdb2292Invoke(read, rows, values);
                                      if (read.getName().equals(FIXTURE_GETOBJECT_B6112877)
                                          && values.length == 2
                                          && values[0].equals(FIXTURE_FAILURE_COUNT_C7E67F21)) {
                                        projected.incrementAndGet();
                                        return 1L; // Independent invalid projection; committed
                                        // count stays zero.
                                      }
                                      if (read.getName().equals(FIXTURE_CLOSE_97959247)) {
                                        rowCloses.incrementAndGet();
                                        if (!fault.equals(FIXTURE_STATEMENT_8A602677))
                                          throw new SQLException("PRIVATE_ROW_CLOSE");
                                      }
                                      return observed;
                                    });
                              });
                        });
              },
              c -> {});
      try {
        var failure =
            assertThrows(
                IOException.class,
                () ->
                    subject.execute(
                        credential(),
                        session -> {
                          try {
                            session.successfulBackup(run, started.plusSeconds(3600));
                            fail("invalid projected failure count must refuse pair");
                            return Boolean.TRUE;
                          } catch (IOException primary) {
                            assertEquals(
                                FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891,
                                primary.getMessage());
                            assertNull(primary.getCause());
                            assertEquals(
                                fault.equals("BOTH") ? 2 : 1, primary.getSuppressed().length);
                            for (Throwable bounded : primary.getSuppressed()) {
                              assertEquals(BatchRepositoryException.class, bounded.getClass());
                              assertEquals(
                                  "batch repository operation failed", bounded.getMessage());
                              assertNull(bounded.getCause());
                              assertEquals(0, bounded.getSuppressed().length);
                            }
                            throw primary;
                          }
                        }));
        assertEquals(FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, failure.getMessage());
        assertNull(failure.getCause());
        assertEquals(0, failure.getSuppressed().length);
      } finally {
        assertEquals(1, projected.get());
        assertEquals(1, rowCloses.get());
        assertEquals(1, statementCloses.get());
        assertTrue(retained.get().isClosed());
        mdb2480SqlRows(run, started, id);
        mdb2292NoOwnerResources();
      }
    }
  }

  /** PT-MDB-2796-001: all remaining same-class Statement/ResultSet boundaries reject null. */
  @Test
  void mdb2796001ReadOnlyAndAbandonedNullResourcesPreserveAllCommittedRows() throws Exception {
    int ordinal = 0;
    for (String fault : List.of("READONLY_STATEMENT", "ABANDONED_STATEMENT", "ABANDONED_ROWS")) {
      int n = ++ordinal;
      var run =
          new BatchRun(
              UUID.fromString("27960001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
              Instant.parse("2052-02-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = run.cutoff().plusSeconds(11 * 3600);
      var currentStart = started.plusSeconds(10);
      var armed = new AtomicBoolean();
      var injected = new AtomicInteger();
      var retained = new AtomicReference<Connection>();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var real = DriverManager.getConnection(url, properties);
                retained.set(real);
                return (Connection)
                    Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          Object value = mdb2292Invoke(method, real, args);
                          if (armed.get()
                              && fault.equals("READONLY_STATEMENT")
                              && method.getName().equals("createStatement")) {
                            ((Statement) value).close();
                            injected.incrementAndGet();
                            return null;
                          }
                          if (!armed.get()
                              || !method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                              || !((String) args[0])
                                  .startsWith(
                                      "select step,attempt,status,error_code,ended_at,business_date"
                                          + " from schubert.batch_runs")) return value;
                          var statement = (PreparedStatement) value;
                          if (fault.equals("ABANDONED_STATEMENT")) {
                            statement.close();
                            injected.incrementAndGet();
                            return null;
                          }
                          return Proxy.newProxyInstance(
                              PreparedStatement.class.getClassLoader(),
                              new Class<?>[] {PreparedStatement.class},
                              (unusedStatement, called, input) -> {
                                Object actual = mdb2292Invoke(called, statement, input);
                                if (called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423)) {
                                  ((ResultSet) actual).close();
                                  injected.incrementAndGet();
                                  return null;
                                }
                                return actual;
                              });
                        });
              },
              c -> {});
      assertEquals(
          Boolean.TRUE,
          subject.execute(
              credential(),
              s -> {
                s.beginBackup(run, started, false);
                return Boolean.TRUE;
              }));
      try {
        var failure =
            assertThrows(
                IOException.class,
                () ->
                    subject.execute(
                        credential(),
                        s -> {
                          s.beginBackup(run, currentStart, true);
                          armed.set(true);
                          if (fault.equals("READONLY_STATEMENT")) s.recheckConsistent(run);
                          else
                            s.requireAbandonedRequest(
                                new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(
                                    run.id(), started));
                          fail("null JDBC boundary must not return authority");
                          return Boolean.TRUE;
                        }));
        assertEquals(FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, failure.getMessage());
        assertNull(failure.getCause());
        assertEquals(0, failure.getSuppressed().length);
      } finally {
        assertEquals(1, injected.get());
        assertTrue(retained.get().isClosed());
        try (var c = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
            var s =
                c.prepareStatement(
                    FIXTURE_SELECT_8DAC6259
                        + " step,attempt,status,started_at,ended_at,target_count,success_count,failure_count,byte_count,error_code"
                        + " from schubert.batch_runs where run_id=? order by step,attempt")) {
          s.setObject(1, run.id());
          try (var rows = s.executeQuery()) {
            for (String step : List.of(FIXTURE_BACKUP_CONFIG_8386D7E7, FIXTURE_BACKUP_DB_6C03A087))
              for (int attempt = 1; attempt <= 2; attempt++) {
                assertTrue(rows.next());
                assertEquals(step, rows.getString(1));
                assertEquals(attempt, rows.getInt(2));
                assertEquals(
                    attempt == 1 ? FIXTURE_FAILED_7E8A57FE : FIXTURE_RUNNING_294BDBF9,
                    rows.getString(3));
                assertEquals(
                    attempt == 1 ? started : currentStart, rows.getTimestamp(4).toInstant());
                if (attempt == 1) assertEquals(currentStart, rows.getTimestamp(5).toInstant());
                else assertNull(rows.getTimestamp(5));
                for (int column = 6; column <= 9; column++) assertEquals(0, rows.getLong(column));
                assertEquals(attempt == 1 ? "ABANDONED" : null, rows.getString(10));
              }
            assertFalse(rows.next());
          }
        }
        mdb2292NoOwnerResources();
      }
    }
  }

  /** PT-MDB-2792-001: null JDBC resources are known unavailable data, never leaked NPE. */
  @Test
  void mdb2792001SuccessfulBackupRejectsNullJdbcResourcesWithoutNpe() throws Exception {
    int ordinal = 0;
    for (String fault : List.of(FIXTURE_STATEMENT_8A602677, "ROWS")) {
      int n = ++ordinal;
      var run =
          new BatchRun(
              UUID.fromString("27920001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
              Instant.parse("2052-01-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = run.cutoff().plusSeconds(11 * 3600);
      long id = 27920010L + n * 10;
      mdb2480Seed(run, started, id);
      var retained = new AtomicReference<Connection>();
      var injected = new AtomicInteger();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var real = DriverManager.getConnection(url, properties);
                retained.set(real);
                return (Connection)
                    Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          Object value = mdb2292Invoke(method, real, args);
                          if (!method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                              || !((String) args[0])
                                  .startsWith(
                                      FIXTURE_SELECT_8DAC6259
                                          + FIXTURE_ID_BUSINESS_DATE_STEP_ATTEMPT_STARTED_AT_F3540697))
                            return value;
                          var statement = (PreparedStatement) value;
                          if (fault.equals(FIXTURE_STATEMENT_8A602677)) {
                            statement.close();
                            injected.incrementAndGet();
                            return null;
                          }
                          return Proxy.newProxyInstance(
                              PreparedStatement.class.getClassLoader(),
                              new Class<?>[] {PreparedStatement.class},
                              (unusedStatement, called, input) -> {
                                Object actual = mdb2292Invoke(called, statement, input);
                                if (called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423)) {
                                  ((ResultSet) actual).close();
                                  injected.incrementAndGet();
                                  return null;
                                }
                                return actual;
                              });
                        });
              },
              c -> {});
      try {
        var failure =
            assertThrows(
                IOException.class,
                () ->
                    subject.execute(
                        credential(), s -> s.successfulBackup(run, started.plusSeconds(3600))));
        assertEquals(FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, failure.getMessage());
        assertNull(failure.getCause());
        assertEquals(0, failure.getSuppressed().length);
      } finally {
        assertEquals(1, injected.get());
        assertTrue(retained.get().isClosed());
        mdb2480SqlRows(run, started, id);
        mdb2292NoOwnerResources();
      }
    }
  }

  /** PT-MDB-2788-001: individually valid timestamps must still describe one complete pair. */
  @Test
  void mdb2788001SuccessfulPairRejectsDifferentStartAndEndWithinValidBounds() throws Exception {
    int ordinal = 0;
    for (String fault : List.of(FIXTURE_STARTED_AT_D1210657, FIXTURE_ENDED_AT_E151E393)) {
      int n = ++ordinal;
      var run =
          new BatchRun(
              UUID.fromString("27880001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
              Instant.parse("2051-04-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = run.cutoff().plusSeconds(11 * 3600);
      var observed = started.plusSeconds(3600);
      long id = 27880010L + n * 10;
      mdb2480Seed(run, started, id);
      var retained = new AtomicReference<Connection>();
      var injected = new AtomicInteger();
      var commits = new AtomicInteger();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var real = DriverManager.getConnection(url, properties);
                retained.set(real);
                return (Connection)
                    Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          if (method.getName().equals(FIXTURE_COMMIT_5EA9C586))
                            commits.incrementAndGet();
                          Object value = mdb2292Invoke(method, real, args);
                          if (!method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                              || !((String) args[0])
                                  .startsWith(
                                      FIXTURE_SELECT_8DAC6259
                                          + FIXTURE_ID_BUSINESS_DATE_STEP_ATTEMPT_STARTED_AT_F3540697))
                            return value;
                          var statement = (PreparedStatement) value;
                          return Proxy.newProxyInstance(
                              PreparedStatement.class.getClassLoader(),
                              new Class<?>[] {PreparedStatement.class},
                              (unusedStatement, called, input) -> {
                                Object actual = mdb2292Invoke(called, statement, input);
                                if (!called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423))
                                  return actual;
                                var rows = (ResultSet) actual;
                                var ordinalRow = new AtomicInteger();
                                return Proxy.newProxyInstance(
                                    ResultSet.class.getClassLoader(),
                                    new Class<?>[] {ResultSet.class},
                                    (unusedRow, read, columns) -> {
                                      Object realValue = mdb2292Invoke(read, rows, columns);
                                      if (read.getName().equals(FIXTURE_NEXT_CA1733B5)
                                          && Boolean.TRUE.equals(realValue))
                                        ordinalRow.incrementAndGet();
                                      if (ordinalRow.get() == 2
                                          && read.getName().equals(FIXTURE_GETOBJECT_B6112877)
                                          && columns[0].equals(fault)) {
                                        injected.incrementAndGet();
                                        return ((java.time.OffsetDateTime) realValue)
                                            .plusSeconds(1);
                                      }
                                      return realValue;
                                    });
                              });
                        });
              },
              c -> {});
      var failure =
          assertThrows(
              IOException.class,
              () -> subject.execute(credential(), s -> s.successfulBackup(run, observed)));
      assertEquals(FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, failure.getMessage());
      assertEquals(fault.equals(FIXTURE_STARTED_AT_D1210657) ? 1 : 2, injected.get());
      assertEquals(0, commits.get());
      assertTrue(retained.get().isClosed());
      mdb2480SqlRows(run, started, id);
      mdb2292NoOwnerResources();
    }
  }

  /** PT-MDB-2784-001: reinspection of a complete bundle must never silently become RUNNING. */
  @Test
  void mdb2784001EmptyBackupReinspectionCannotAuthorizeResumeOrObservation() throws Exception {
    int ordinal = 0;
    for (String mode :
        List.of(
            FIXTURE_BEGIN_RESUME_CA1CD26C, FIXTURE_SKIPPED_OBSERVE_FB5C359C, "FAILED_OBSERVE")) {
      int n = ++ordinal;
      var run =
          new BatchRun(
              UUID.fromString("27840001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
              Instant.parse("2051-03-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = run.cutoff().plusSeconds(11 * 3600);
      var observed = started.plusSeconds(3600);
      long id = 27840010L + n * 10;
      var armed = new AtomicBoolean();
      var pairReads = new AtomicInteger();
      var statuses = new AtomicInteger();
      var retained = new AtomicReference<Connection>();
      var commits = new AtomicInteger();
      int projectAt = mode.equals(FIXTURE_BEGIN_RESUME_CA1CD26C) ? 1 : 2;
      var subject = mdb2784Subject(armed, pairReads, statuses, retained, commits, projectAt);
      if (!mode.equals("FAILED_OBSERVE")) mdb2480Seed(run, started, id, true);
      var original =
          mdb2482Manifest(
              new MorningDatabaseSession.BackupBegins(
                  new BatchStepAttempt(id + 1, run, BatchStep.BACKUP_DB, 1, started, false),
                  new BatchStepAttempt(id, run, BatchStep.BACKUP_CONFIG, 1, started, false)),
              started);
      assertThrows(
          IOException.class,
          () ->
              subject.execute(
                  credential(),
                  session -> {
                    if (mode.equals(FIXTURE_BEGIN_RESUME_CA1CD26C)) {
                      armed.set(true);
                      session.beginResumeBackup(original, observed);
                    } else if (mode.equals(FIXTURE_SKIPPED_OBSERVE_FB5C359C)) {
                      var current = session.beginResumeBackup(original, observed);
                      session.completeReusedBackup(current, original, observed);
                      armed.set(true);
                      session.observeBackup(
                          current, Optional.of(original), observed, () -> 10_000_000_000L);
                    } else {
                      var current = session.beginBackup(run, started, false);
                      var failed =
                          new BatchStepResult(
                              BatchStepResult.Status.FAILED,
                              1,
                              0,
                              1,
                              0,
                              BatchStepResult.Reason.COMMAND_FAILURE);
                      session.failBackup(current, started.plusSeconds(3), failed, failed);
                      armed.set(true);
                      session.observeBackup(
                          current,
                          Optional.of(mdb2482Manifest(current, started)),
                          observed,
                          () -> 10_000_000_000L);
                    }
                    fail("empty independent reinspection must never authorize this operation");
                    return Boolean.TRUE;
                  }));
      assertTrue(retained.get().isClosed());
      assertEquals(projectAt, pairReads.get());
      assertEquals(2, statuses.get());
      assertEquals(
          mode.equals(FIXTURE_BEGIN_RESUME_CA1CD26C)
              ? 0
              : mode.equals(FIXTURE_SKIPPED_OBSERVE_FB5C359C) ? 1 : 2,
          commits.get());
      if (mode.equals(FIXTURE_BEGIN_RESUME_CA1CD26C)) {
        // Independent reverse-ID oracle; no current attempt was committed.
        try (var c = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
            var s =
                c.prepareStatement(
                    "select id,step,status,target_count,success_count,failure_count,byte_count"
                        + " from schubert.batch_runs where run_id=? order by id")) {
          s.setObject(1, run.id());
          try (var rows = s.executeQuery()) {
            for (int index = 0; index < 2; index++) {
              assertTrue(rows.next());
              assertEquals(id + index, rows.getLong(1));
              assertEquals(
                  index == 0 ? FIXTURE_BACKUP_CONFIG_8386D7E7 : FIXTURE_BACKUP_DB_6C03A087,
                  rows.getString(2));
              assertEquals(FIXTURE_SUCCESS_10855C7F, rows.getString(3));
              assertEquals(index == 0 ? 2 : 1, rows.getLong(4));
              assertEquals(index == 0 ? 2 : 1, rows.getLong(5));
              assertEquals(0, rows.getLong(6));
              assertEquals(index == 0 ? 67 : 26, rows.getLong(7));
            }
            assertFalse(rows.next());
          }
        }
      } else if (mode.equals(FIXTURE_SKIPPED_OBSERVE_FB5C359C)) {
        mdb2490SqlRows(run, started, observed, id);
      } else {
        mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(started.plusSeconds(3)));
      }
      mdb2292NoOwnerResources();
    }
  }

  private static MorningDatabaseSession mdb2784Subject(
      AtomicBoolean armed,
      AtomicInteger reads,
      AtomicInteger statuses,
      AtomicReference<Connection> retained,
      AtomicInteger commits,
      int projectAt) {
    return new MorningDatabaseSession(
        actualUrl,
        () -> {},
        (url, properties) -> {
          var real = DriverManager.getConnection(url, properties);
          retained.set(real);
          return (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (unused, method, args) -> {
                    if (method.getName().equals(FIXTURE_COMMIT_5EA9C586)) commits.incrementAndGet();
                    Object value = mdb2292Invoke(method, real, args);
                    if (!method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                        || !((String) args[0]).contains("where id in (?,?) order by id for update"))
                      return value;
                    var statement = (PreparedStatement) value;
                    return Proxy.newProxyInstance(
                        PreparedStatement.class.getClassLoader(),
                        new Class<?>[] {PreparedStatement.class},
                        (unusedStatement, called, input) -> {
                          Object actual = mdb2292Invoke(called, statement, input);
                          if (!called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423))
                            return actual;
                          boolean project = armed.get() && reads.incrementAndGet() == projectAt;
                          var rows = (ResultSet) actual;
                          return Proxy.newProxyInstance(
                              ResultSet.class.getClassLoader(),
                              new Class<?>[] {ResultSet.class},
                              (unusedRow, read, columns) -> {
                                Object observedValue = mdb2292Invoke(read, rows, columns);
                                if (!project
                                    || !(read.getName().equals(FIXTURE_GETOBJECT_B6112877)
                                        || read.getName().equals(FIXTURE_GETSTRING_B3B802ED)))
                                  return observedValue;
                                String field = (String) columns[0];
                                if (field.equals(FIXTURE_STATUS_CFC31BCC)) {
                                  statuses.incrementAndGet();
                                  return FIXTURE_RUNNING_294BDBF9;
                                }
                                if (Set.of(
                                        FIXTURE_ENDED_AT_E151E393,
                                        FIXTURE_ERROR_CODE_B886CCEF,
                                        FIXTURE_ERROR_SUMMARY_3F58BF23)
                                    .contains(field)) return null;
                                if (Set.of(
                                        FIXTURE_TARGET_COUNT_5B6567D4,
                                        FIXTURE_SUCCESS_COUNT_716E5185,
                                        FIXTURE_FAILURE_COUNT_C7E67F21,
                                        FIXTURE_BYTE_COUNT_6D76E237)
                                    .contains(field)) return 0L;
                                return observedValue;
                              });
                        });
                  });
        },
        c -> {});
  }

  /** PT-MDB-2780-001: both resume attempts must be SKIPPED, not a foreign history projection. */
  @Test
  void mdb2780001ResumeRejectsEitherNonSkippedAttemptBeforeCommit() throws Exception {
    int ordinal = 0;
    for (String fault : List.of(FIXTURE_BACKUP_DB_6C03A087, FIXTURE_BACKUP_CONFIG_8386D7E7)) {
      int n = ++ordinal;
      var run =
          new BatchRun(
              UUID.fromString("27800001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
              Instant.parse("2051-02-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = run.cutoff().plusSeconds(11 * 3600);
      var observed = started.plusSeconds(3600);
      long id = 27800010L + n * 10;
      mdb2480Seed(run, started, id);
      var original =
          mdb2482Manifest(
              new MorningDatabaseSession.BackupBegins(
                  new BatchStepAttempt(id, run, BatchStep.BACKUP_DB, 1, started, false),
                  new BatchStepAttempt(id + 1, run, BatchStep.BACKUP_CONFIG, 1, started, false)),
              started);
      var retained = new AtomicReference<Connection>();
      var injected = new AtomicInteger();
      var commits = new AtomicInteger();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var real = DriverManager.getConnection(url, properties);
                retained.set(real);
                return (Connection)
                    Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          if (method.getName().equals(FIXTURE_COMMIT_5EA9C586))
                            commits.incrementAndGet();
                          Object value = mdb2292Invoke(method, real, args);
                          if (!method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                              || !((String) args[0])
                                  .contains("where business_date=? and step=? order by attempt"))
                            return value;
                          var statement = (PreparedStatement) value;
                          var step = new AtomicReference<String>();
                          return Proxy.newProxyInstance(
                              PreparedStatement.class.getClassLoader(),
                              new Class<?>[] {PreparedStatement.class},
                              (unusedStatement, called, input) -> {
                                if (called.getName().equals("setString")
                                    && Integer.valueOf(2).equals(input[0]))
                                  step.set((String) input[1]);
                                Object actual = mdb2292Invoke(called, statement, input);
                                if (!called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423))
                                  return actual;
                                var rows = (ResultSet) actual;
                                return Proxy.newProxyInstance(
                                    ResultSet.class.getClassLoader(),
                                    new Class<?>[] {ResultSet.class},
                                    (unusedRow, read, columns) -> {
                                      Object observedValue = mdb2292Invoke(read, rows, columns);
                                      if (read.getName().equals(FIXTURE_GETOBJECT_B6112877)
                                          && columns[0].equals("run_id")
                                          && fault.equals(step.get())) {
                                        injected.incrementAndGet();
                                        return UUID.fromString(
                                            "27800002-2222-4333-8444-555555555555");
                                      }
                                      return observedValue;
                                    });
                              });
                        });
              },
              c -> {});
      var failure =
          assertThrows(
              IOException.class,
              () -> subject.execute(credential(), s -> s.beginResumeBackup(original, observed)));
      assertEquals(FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, failure.getMessage());
      assertEquals(1, injected.get());
      assertEquals(0, commits.get());
      assertTrue(retained.get().isClosed());
      mdb2480SqlRows(run, started, id);
      mdb2292NoOwnerResources();
    }
  }

  /** PT-MDB-2762-001: original run identity is proved again from actual committed references. */
  @Test
  void mdb2762001PostBeginRejectsForeignRunAndActualLogCutoffDrift() throws Exception {
    int ordinal = 0;
    for (String fault : List.of("FOREIGN_RUN", "LOG_CUTOFF")) {
      int n = ++ordinal;
      var run =
          new BatchRun(
              UUID.fromString("27620001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
              Instant.parse("2050-04-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = run.cutoff().plusSeconds(11 * 3600);
      var ended = started.plusSeconds(3);
      var failed =
          new BatchStepResult(
              BatchStepResult.Status.FAILED, 1, 0, 1, 0, BatchStepResult.Reason.COMMAND_FAILURE);
      var retained = new AtomicReference<Connection>();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var c = DriverManager.getConnection(url, properties);
                retained.set(c);
                return c;
              },
              c -> {});
      assertEquals(
          Boolean.TRUE,
          subject.execute(
              credential(),
              session -> {
                var begins = session.beginBackup(run, started, false);
                session.failBackup(begins, ended, failed, failed);
                session.recheckConsistent(run);
                var offered =
                    fault.equals("FOREIGN_RUN")
                        ? new BatchRun(
                            UUID.fromString("27620002-2222-4333-8444-555555555555"), run.cutoff())
                        : run;
                if (fault.equals("LOG_CUTOFF")) {
                  try (var c =
                          DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
                      var s =
                          c.prepareStatement(
                              "insert into schubert.log_cleanup_progress(run_id,cutoff)"
                                  + " values(?,?)")) {
                    s.setObject(1, run.id());
                    s.setObject(2, run.cutoff().plusSeconds(1).atOffset(java.time.ZoneOffset.UTC));
                    assertEquals(1, s.executeUpdate());
                  } catch (SQLException failure) {
                    throw new IOException("isolated reference fixture", failure);
                  }
                }
                var refusal =
                    assertThrows(IOException.class, () -> session.recheckConsistent(offered));
                assertEquals(
                    FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, refusal.getMessage());
                mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(ended));
                return Boolean.TRUE;
              }));
      assertTrue(retained.get().isClosed());
      mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(ended));
      try (var c = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
          var s =
              c.prepareStatement(
                  "select cutoff,target_count,deleted_count,completed_at"
                      + " from schubert.log_cleanup_progress where run_id=?")) {
        s.setObject(1, run.id());
        try (var rows = s.executeQuery()) {
          if (fault.equals("LOG_CUTOFF")) {
            assertTrue(rows.next());
            assertEquals(run.cutoff().plusSeconds(1), rows.getTimestamp(1).toInstant());
            assertEquals(0, rows.getLong(2));
            assertEquals(0, rows.getLong(3));
            assertNull(rows.getTimestamp(4));
          }
          assertFalse(rows.next());
        }
      }
      mdb2292NoOwnerResources();
    }
  }

  /** PT-MDB-2758-001: JDBC completion failure never authorizes retained-backup continuation. */
  @Test
  void mdb2758001ReusedBackupSqlCompletionFailuresPreserveOriginalAndSkippedRows()
      throws Exception {
    int ordinal = 0;
    for (String fault : List.of("ROLLBACK", "AUTOCOMMIT")) {
      int n = ++ordinal;
      var run =
          new BatchRun(
              UUID.fromString("27580001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
              Instant.parse("2050-03-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = run.cutoff().plusSeconds(11 * 3600);
      var observed = started.plusSeconds(3600);
      long id = 27580010L + n * 10;
      mdb2480Seed(run, started, id, true);
      var original =
          mdb2482Manifest(
              new MorningDatabaseSession.BackupBegins(
                  new BatchStepAttempt(id + 1, run, BatchStep.BACKUP_DB, 1, started, false),
                  new BatchStepAttempt(id, run, BatchStep.BACKUP_CONFIG, 1, started, false)),
              started);
      var armed = new AtomicBoolean();
      var intercepted = new AtomicInteger();
      var retained = new AtomicReference<Connection>();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var real = DriverManager.getConnection(url, properties);
                retained.set(real);
                return (Connection)
                    Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          boolean boundary =
                              fault.equals("ROLLBACK")
                                  ? method.getName().equals("rollback")
                                  : method.getName().equals("setAutoCommit")
                                      && Boolean.TRUE.equals(args[0]);
                          if (boundary && armed.compareAndSet(true, false)) {
                            intercepted.incrementAndGet();
                            throw new SQLException("isolated completion boundary");
                          }
                          return mdb2292Invoke(method, real, args);
                        });
              },
              c -> {});
      IOException failure =
          assertThrows(
              IOException.class,
              () ->
                  subject.execute(
                      credential(),
                      session -> {
                        var current = session.beginResumeBackup(original, observed);
                        mdb2490SqlRows(run, started, observed, id);
                        armed.set(true);
                        session.completeReusedBackup(current, original, observed);
                        fail("JDBC failure must prevent completion");
                        return Boolean.TRUE;
                      }));
      assertEquals(FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, failure.getMessage());
      assertEquals(1, intercepted.get());
      assertTrue(retained.get().isClosed());
      mdb2490SqlRows(run, started, observed, id);
      mdb2292NoOwnerResources();
    }
  }

  /** PT-MDB-2754-001: retained SUCCESS cannot authorize observation before current completion. */
  @Test
  void mdb2754001RetainedBackupRequiresCurrentCompletionAndPreservesOriginalRows()
      throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("27540001-2222-4333-8444-555555555555"),
            Instant.parse("2050-02-09T15:00:00Z"));
    var started = Instant.parse("2050-02-10T02:00:00Z");
    var observed = started.plusSeconds(3600);
    long id = 27540010;
    mdb2480Seed(run, started, id, true);
    var original =
        mdb2482Manifest(
            new MorningDatabaseSession.BackupBegins(
                new BatchStepAttempt(id + 1, run, BatchStep.BACKUP_DB, 1, started, false),
                new BatchStepAttempt(id, run, BatchStep.BACKUP_CONFIG, 1, started, false)),
            started);
    var retained = new AtomicReference<Connection>();
    var prepared = new AtomicInteger();
    var subject =
        new MorningDatabaseSession(
            actualUrl,
            () -> {},
            (url, properties) -> {
              var real = DriverManager.getConnection(url, properties);
              retained.set(real);
              return (Connection)
                  Proxy.newProxyInstance(
                      Connection.class.getClassLoader(),
                      new Class<?>[] {Connection.class},
                      (unused, method, args) -> {
                        if (method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F))
                          prepared.incrementAndGet();
                        return mdb2292Invoke(method, real, args);
                      });
            },
            c -> {});
    assertEquals(
        Boolean.TRUE,
        subject.execute(
            credential(),
            session -> {
              int before = prepared.get();
              assertThrows(
                  IOException.class, () -> session.retainedBackupSuccessful(original, observed));
              assertEquals(before, prepared.get());
              var current = session.beginResumeBackup(original, observed);
              before = prepared.get();
              assertThrows(
                  IOException.class, () -> session.retainedBackupSuccessful(original, observed));
              assertEquals(before, prepared.get());
              mdb2490SqlRows(run, started, observed, id);
              session.completeReusedBackup(current, original, observed);
              assertTrue(session.retainedBackupSuccessful(original, observed));
              mdb2490SqlRows(run, started, observed, id);
              return Boolean.TRUE;
            }));
    assertTrue(retained.get().isClosed());
    mdb2490SqlRows(run, started, observed, id);
    mdb2292NoOwnerResources();
  }

  /** PT-MDB-2750-001: same callback cannot observe a pair during advisory handoff. */
  @Test
  void mdb2750001BackupObservationRejectsInHandoffBeforeJdbcAndPreservesFailedPair()
      throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("27500001-2222-4333-8444-555555555555"),
            Instant.parse("2050-01-09T15:00:00Z"));
    var started = Instant.parse("2050-01-10T02:00:00Z");
    var ended = started.plusSeconds(3);
    var failed =
        new BatchStepResult(
            BatchStepResult.Status.FAILED, 1, 0, 1, 0, BatchStepResult.Reason.COMMAND_FAILURE);
    var retained = new AtomicReference<Connection>();
    var prepared = new AtomicInteger();
    var subject =
        new MorningDatabaseSession(
            actualUrl,
            () -> {},
            (url, properties) -> {
              var real = DriverManager.getConnection(url, properties);
              retained.set(real);
              return (Connection)
                  Proxy.newProxyInstance(
                      Connection.class.getClassLoader(),
                      new Class<?>[] {Connection.class},
                      (unused, method, args) -> {
                        if (method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F))
                          prepared.incrementAndGet();
                        return mdb2292Invoke(method, real, args);
                      });
            },
            c -> {});
    subject.execute(
        credential(),
        session -> {
          var begins = session.beginBackup(run, started, false);
          session.failBackup(begins, ended, failed, failed);
          var observed =
              session.observeBackup(begins, Optional.empty(), ended, () -> 10_000_000_000L);
          assertEquals(2, observed.current().size());
          assertTrue(observed.prior().isEmpty());
          for (var row : observed.current()) {
            assertEquals(failed, row.result());
            assertEquals(ended, row.ended());
          }
          assertEquals(
              Boolean.TRUE,
              session.handoffCleanup(
                  () -> {
                    int before = prepared.get();
                    assertThrows(
                        IOException.class,
                        () ->
                            session.observeBackup(
                                begins, Optional.empty(), ended, () -> 10_000_000_000L));
                    assertEquals(before, prepared.get());
                    return Boolean.TRUE;
                  }));
          return Boolean.TRUE;
        });
    assertTrue(retained.get().isClosed());
    try (var c = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var s =
            c.prepareStatement(
                "select step,status,target_count,success_count,failure_count,byte_count,ended_at"
                    + " from schubert.batch_runs where run_id=? order by step")) {
      s.setObject(1, run.id());
      try (var rows = s.executeQuery()) {
        for (String step : List.of(FIXTURE_BACKUP_CONFIG_8386D7E7, FIXTURE_BACKUP_DB_6C03A087)) {
          assertTrue(rows.next());
          assertEquals(step, rows.getString(1));
          assertEquals(FIXTURE_FAILED_7E8A57FE, rows.getString(2));
          assertEquals(1, rows.getLong(3));
          assertEquals(0, rows.getLong(4));
          assertEquals(1, rows.getLong(5));
          assertEquals(0, rows.getLong(6));
          assertEquals(ended, rows.getTimestamp(7).toInstant());
        }
        assertFalse(rows.next());
      }
    }
    mdb2292NoOwnerResources();
  }

  /** PT-MDB2594-001: original identity/content and transaction commit are mandatory. */
  @Test
  void mdb2594001ResumeAdmissionRejectsForeignManifestContentAndCommitWithoutPublishing()
      throws Exception {
    int ordinal = 0;
    for (String fault : List.of("ID", "CONTENT", "COMMIT")) {
      int n = ++ordinal;
      var run =
          new BatchRun(
              UUID.fromString("25940001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
              Instant.parse("2047-01-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = run.cutoff().plusSeconds(11 * 3600);
      var observed = started.plusSeconds(3600);
      long id = 25940010L + n * 10;
      mdb2480Seed(run, started, id);
      var begins =
          new MorningDatabaseSession.BackupBegins(
              new BatchStepAttempt(
                  fault.equals("ID") ? id + 999 : id, run, BatchStep.BACKUP_DB, 1, started, false),
              new BatchStepAttempt(id + 1, run, BatchStep.BACKUP_CONFIG, 1, started, false));
      var trustedShape = mdb2482Manifest(begins, started);
      var original =
          fault.equals("CONTENT")
              ? new BackupManifest(
                  begins.database(),
                  begins.configuration(),
                  started,
                  started.plusSeconds(2),
                  trustedShape.versions(),
                  "0".repeat(64),
                  new BackupFileDigest(27, "1".repeat(64)),
                  new BackupFileDigest(35, "2".repeat(64)),
                  new BackupFileDigest(32, "3".repeat(64)))
              : trustedShape;
      var retained = new AtomicReference<Connection>();
      var commits = new AtomicInteger();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var connection = DriverManager.getConnection(url, properties);
                retained.set(connection);
                return (Connection)
                    Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          if (fault.equals("COMMIT")
                              && method.getName().equals(FIXTURE_COMMIT_5EA9C586)
                              && commits.incrementAndGet() == 1)
                            throw new SQLException("isolated resume commit refusal", "08006");
                          return mdb2292Invoke(method, connection, args);
                        });
              },
              c -> {});
      assertThrows(
          IOException.class,
          () -> subject.execute(credential(), s -> s.beginResumeBackup(original, observed)),
          fault);
      assertTrue(retained.get().isClosed());
      mdb2480SqlRows(run, started, id);
      mdb2292NoOwnerResources();
    }
  }

  /** PT-MDB2592-001: untrusted prior pair projections cannot mint resume authority. */
  @Test
  void mdb2592001SuccessfulPairRejectsIdentityExtraDuplicateAndSqlWithoutMutation()
      throws Exception {
    int ordinal = 0;
    for (String fault : List.of("VALID", "IDENTITY", "EXTRA", "SAME_STEP", FIXTURE_SQL_5B7E398D)) {
      int n = ++ordinal;
      var run =
          new BatchRun(
              UUID.fromString("25920001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
              Instant.parse("2046-01-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = run.cutoff().plusSeconds(11 * 3600);
      var observed = started.plusSeconds(3600);
      long id = 25920010L + n * 10;
      mdb2480Seed(run, started, id, true);
      var retained = new AtomicReference<Connection>();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var connection = DriverManager.getConnection(url, properties);
                retained.set(connection);
                return (Connection)
                    Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          boolean pair =
                              method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                                  && ((String) args[0])
                                      .startsWith(
                                          FIXTURE_SELECT_8DAC6259
                                              + FIXTURE_ID_BUSINESS_DATE_STEP_ATTEMPT_STARTED_AT_F3540697);
                          boolean identity =
                              method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                                  && ((String) args[0]).contains("maintenance_read_run_references");
                          if (pair && fault.equals(FIXTURE_SQL_5B7E398D))
                            throw new SQLException("isolated selected pair refusal", "08006");
                          Object value = mdb2292Invoke(method, connection, args);
                          if (!pair && !identity) return value;
                          var statement = (PreparedStatement) value;
                          return Proxy.newProxyInstance(
                              PreparedStatement.class.getClassLoader(),
                              new Class<?>[] {PreparedStatement.class},
                              (ignored, called, input) -> {
                                Object actual = mdb2292Invoke(called, statement, input);
                                if (!called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423))
                                  return actual;
                                var rows = (ResultSet) actual;
                                var nextCalls = new AtomicInteger();
                                return Proxy.newProxyInstance(
                                    ResultSet.class.getClassLoader(),
                                    new Class<?>[] {ResultSet.class},
                                    (ignoredRow, read, columns) -> {
                                      if (pair
                                          && fault.equals("EXTRA")
                                          && read.getName().equals(FIXTURE_NEXT_CA1733B5)
                                          && nextCalls.incrementAndGet() == 3) return true;
                                      if (pair
                                          && fault.equals("SAME_STEP")
                                          && read.getName().equals(FIXTURE_GETSTRING_B3B802ED)
                                          && columns[0].equals("step"))
                                        return FIXTURE_BACKUP_DB_6C03A087;
                                      if (pair
                                          && fault.equals("SAME_STEP")
                                          && read.getName().equals(FIXTURE_GETOBJECT_B6112877)
                                          && (columns[0].equals(FIXTURE_TARGET_COUNT_5B6567D4)
                                              || columns[0].equals(FIXTURE_SUCCESS_COUNT_716E5185)))
                                        return 1L;
                                      if (identity
                                          && fault.equals("IDENTITY")
                                          && read.getName().equals(FIXTURE_GETOBJECT_B6112877)
                                          && columns[0].equals("identity_consistent")) return false;
                                      return mdb2292Invoke(read, rows, columns);
                                    });
                              });
                        });
              },
              c -> {});
      if (fault.equals("VALID")) {
        var pair =
            subject.execute(credential(), s -> s.successfulBackup(run, observed)).orElseThrow();
        assertEquals(id + 1, pair.database().id());
        assertEquals(id, pair.configuration().id());
        assertEquals(1, pair.database().attempt());
        assertEquals(1, pair.configuration().attempt());
      } else
        assertThrows(
            IOException.class,
            () -> subject.execute(credential(), s -> s.successfulBackup(run, observed)),
            fault);
      assertTrue(retained.get().isClosed());
      try (var observer = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
          var statement =
              observer.prepareStatement(
                  FIXTURE_SELECT_8DAC6259
                      + " id,step,attempt,status,started_at,ended_at,target_count,success_count,failure_count,byte_count"
                      + " from schubert.batch_runs where run_id=? order by id")) {
        statement.setObject(1, run.id());
        try (var rows = statement.executeQuery()) {
          for (int i = 0; i < 2; i++) {
            assertTrue(rows.next());
            assertEquals(id + i, rows.getLong("id"));
            assertEquals(
                i == 0 ? FIXTURE_BACKUP_CONFIG_8386D7E7 : FIXTURE_BACKUP_DB_6C03A087,
                rows.getString("step"));
            assertEquals(1, rows.getInt("attempt"));
            assertEquals(FIXTURE_SUCCESS_10855C7F, rows.getString(FIXTURE_STATUS_CFC31BCC));
            assertEquals(started, rows.getTimestamp(FIXTURE_STARTED_AT_D1210657).toInstant());
            assertEquals(
                started.plusSeconds(3), rows.getTimestamp(FIXTURE_ENDED_AT_E151E393).toInstant());
            assertEquals(i == 0 ? 2 : 1, rows.getLong(FIXTURE_TARGET_COUNT_5B6567D4));
            assertEquals(i == 0 ? 2 : 1, rows.getLong(FIXTURE_SUCCESS_COUNT_716E5185));
            assertEquals(0, rows.getLong(FIXTURE_FAILURE_COUNT_C7E67F21));
            assertEquals(i == 0 ? 67 : 26, rows.getLong(FIXTURE_BYTE_COUNT_6D76E237));
          }
          assertFalse(rows.next());
        }
      }
      mdb2292NoOwnerResources();
    }
  }

  /** PT-MDB2590-001: actual original-row drift defeats a stale successful eligibility view. */
  @Test
  void mdb2590001OriginalPairMustBeReinspectedBeforeReuseOrRetention() throws Exception {
    int ordinal = 0;
    for (String operation : List.of("COMPLETE", "RETENTION")) {
      for (String drift : List.of(FIXTURE_RUNNING_294BDBF9, "BYTE")) {
        int n = ++ordinal;
        var run =
            new BatchRun(
                UUID.fromString(
                    "25900001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
                Instant.parse("2045-01-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
        var started = run.cutoff().plusSeconds(11 * 3600);
        var observed = started.plusSeconds(3600);
        long id = 25900010L + n * 10;
        mdb2480Seed(run, started, id, true);
        var original =
            mdb2482Manifest(
                new MorningDatabaseSession.BackupBegins(
                    new BatchStepAttempt(id + 1, run, BatchStep.BACKUP_DB, 1, started, false),
                    new BatchStepAttempt(id, run, BatchStep.BACKUP_CONFIG, 1, started, false)),
                started);
        var armed = new AtomicBoolean();
        var cachedReads = new AtomicInteger();
        var retained = new AtomicReference<Connection>();
        var subject =
            new MorningDatabaseSession(
                actualUrl,
                () -> {},
                (url, properties) -> {
                  var connection = DriverManager.getConnection(url, properties);
                  retained.set(connection);
                  return (Connection)
                      Proxy.newProxyInstance(
                          Connection.class.getClassLoader(),
                          new Class<?>[] {Connection.class},
                          (unused, method, args) -> {
                            Object value = mdb2292Invoke(method, connection, args);
                            if (!armed.get()
                                || !method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                                || !((String) args[0])
                                    .startsWith("select id,status from schubert.batch_runs"))
                              return value;
                            var statement = (PreparedStatement) value;
                            return Proxy.newProxyInstance(
                                PreparedStatement.class.getClassLoader(),
                                new Class<?>[] {PreparedStatement.class},
                                (unusedStatement, called, input) -> {
                                  Object actual = mdb2292Invoke(called, statement, input);
                                  if (!called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423))
                                    return actual;
                                  var rows = (ResultSet) actual;
                                  return Proxy.newProxyInstance(
                                      ResultSet.class.getClassLoader(),
                                      new Class<?>[] {ResultSet.class},
                                      (unusedRow, read, columns) -> {
                                        Object real = mdb2292Invoke(read, rows, columns);
                                        if (read.getName().equals(FIXTURE_GETSTRING_B3B802ED)
                                            && columns[0].equals(FIXTURE_STATUS_CFC31BCC)) {
                                          cachedReads.incrementAndGet();
                                          return FIXTURE_SUCCESS_10855C7F;
                                        }
                                        return real;
                                      });
                                });
                          });
                },
                c -> {});
        assertThrows(
            IOException.class,
            () ->
                subject.execute(
                    credential(),
                    session -> {
                      var current = session.beginResumeBackup(original, observed);
                      if (operation.equals("RETENTION"))
                        session.completeReusedBackup(current, original, observed);
                      try (var connection =
                              DriverManager.getConnection(
                                  actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
                          var statement =
                              connection.prepareStatement(
                                  drift.equals(FIXTURE_RUNNING_294BDBF9)
                                      ? "update schubert.batch_runs set"
                                          + " status='RUNNING',ended_at=null,target_count=0,success_count=0,failure_count=0,byte_count=0"
                                          + " where run_id=? and attempt=1"
                                      : "update schubert.batch_runs set byte_count=byte_count+1"
                                          + " where run_id=? and attempt=1")) {
                        statement.setObject(1, run.id());
                        assertEquals(2, statement.executeUpdate());
                      } catch (SQLException failure) {
                        throw new IOException("isolated original-row mutation failed", failure);
                      }
                      armed.set(true);
                      if (operation.equals("COMPLETE"))
                        session.completeReusedBackup(current, original, observed);
                      else session.retainedBackupSuccessful(original, observed);
                      return Boolean.TRUE;
                    }),
            operation + ":" + drift);
        assertTrue(retained.get().isClosed());
        if (operation.equals("RETENTION")) assertEquals(2, cachedReads.get());
        else assertEquals(0, cachedReads.get());
        try (var connection =
                DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
            var statement =
                connection.prepareStatement(
                    FIXTURE_SELECT_8DAC6259
                        + " step,attempt,status,started_at,ended_at,target_count,success_count,failure_count,byte_count,error_code"
                        + " from schubert.batch_runs where run_id=? order by attempt,step")) {
          statement.setObject(1, run.id());
          try (var rows = statement.executeQuery()) {
            for (int attempt = 1; attempt <= 2; attempt++) {
              for (String step :
                  List.of(FIXTURE_BACKUP_CONFIG_8386D7E7, FIXTURE_BACKUP_DB_6C03A087)) {
                assertTrue(rows.next());
                boolean skipped = attempt == 2;
                boolean running = !skipped && drift.equals(FIXTURE_RUNNING_294BDBF9);
                long count =
                    skipped || running ? 0 : step.equals(FIXTURE_BACKUP_DB_6C03A087) ? 1 : 2;
                assertEquals(step, rows.getString("step"));
                assertEquals(attempt, rows.getInt("attempt"));
                assertEquals(
                    skipped
                        ? "SKIPPED"
                        : running ? FIXTURE_RUNNING_294BDBF9 : FIXTURE_SUCCESS_10855C7F,
                    rows.getString(FIXTURE_STATUS_CFC31BCC));
                assertEquals(
                    skipped ? observed : started,
                    rows.getTimestamp(FIXTURE_STARTED_AT_D1210657).toInstant());
                assertEquals(
                    running ? null : skipped ? observed : started.plusSeconds(3),
                    Optional.ofNullable(rows.getTimestamp(FIXTURE_ENDED_AT_E151E393))
                        .map(Timestamp::toInstant)
                        .orElse(null));
                assertEquals(count, rows.getLong(FIXTURE_TARGET_COUNT_5B6567D4));
                assertEquals(count, rows.getLong(FIXTURE_SUCCESS_COUNT_716E5185));
                assertEquals(0, rows.getLong(FIXTURE_FAILURE_COUNT_C7E67F21));
                assertEquals(
                    skipped || running ? 0 : step.equals(FIXTURE_BACKUP_DB_6C03A087) ? 27 : 68,
                    rows.getLong(FIXTURE_BYTE_COUNT_6D76E237));
                assertEquals(
                    skipped ? "ALREADY_SUCCESSFUL" : null,
                    rows.getString(FIXTURE_ERROR_CODE_B886CCEF));
              }
            }
            assertFalse(rows.next());
          }
        }
        mdb2292NoOwnerResources();
      }
    }
    assertEquals(4, ordinal);
  }

  /** PT-MDB2588-001: archive eligibility never trusts foreign/duplicate/null terminal claims. */
  @Test
  void mdb2588001RetentionEligibilityRequiresExactDistinctIdsAndKnownStatuses() throws Exception {
    int ordinal = 0;
    for (String fault :
        List.of(
            "VALID",
            "MISSING",
            "ONE_ROW",
            "FOREIGN_ID",
            "DUPLICATE_ID",
            "NULL_ID",
            "NULL_STATUS",
            "UNKNOWN_STATUS",
            FIXTURE_RUNNING_294BDBF9,
            FIXTURE_FAILED_7E8A57FE,
            "WARNING",
            "SKIPPED")) {
      int n = ++ordinal;
      var run =
          new BatchRun(
              UUID.fromString("25880001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
              Instant.parse("2044-01-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = run.cutoff().plusSeconds(11 * 3600);
      var observed = started.plusSeconds(3600);
      long id = 25880010L + n * 10;
      mdb2480Seed(run, started, id, true);
      var original =
          mdb2482Manifest(
              new MorningDatabaseSession.BackupBegins(
                  new BatchStepAttempt(id + 1, run, BatchStep.BACKUP_DB, 1, started, false),
                  new BatchStepAttempt(id, run, BatchStep.BACKUP_CONFIG, 1, started, false)),
              started);
      var armed = new AtomicBoolean();
      var observedRows = new AtomicInteger();
      var retained = new AtomicReference<Connection>();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var connection = DriverManager.getConnection(url, properties);
                retained.set(connection);
                return (Connection)
                    Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          Object actual = mdb2292Invoke(method, connection, args);
                          if (!armed.get()
                              || !method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                              || !((String) args[0])
                                  .startsWith("select id,status from schubert.batch_runs"))
                            return actual;
                          var statement = (PreparedStatement) actual;
                          return Proxy.newProxyInstance(
                              PreparedStatement.class.getClassLoader(),
                              new Class<?>[] {PreparedStatement.class},
                              (unusedStatement, called, input) -> {
                                Object real = mdb2292Invoke(called, statement, input);
                                if (!called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423))
                                  return real;
                                var rows = (ResultSet) real;
                                var row = new AtomicInteger();
                                return Proxy.newProxyInstance(
                                    ResultSet.class.getClassLoader(),
                                    new Class<?>[] {ResultSet.class},
                                    (unusedRow, read, columns) -> {
                                      Object value = mdb2292Invoke(read, rows, columns);
                                      observedRows.incrementAndGet();
                                      if (read.getName().equals(FIXTURE_NEXT_CA1733B5)) {
                                        int index = row.incrementAndGet();
                                        if (fault.equals("MISSING") && index == 1
                                            || fault.equals("ONE_ROW") && index == 2) return false;
                                        return value;
                                      }
                                      if (read.getName().equals(FIXTURE_GETOBJECT_B6112877)
                                          && columns[0].equals("id")) {
                                        if (fault.equals("NULL_ID") && row.get() == 1) return null;
                                        if (fault.equals("FOREIGN_ID") && row.get() == 1)
                                          return id + 100000L;
                                        if (fault.equals("DUPLICATE_ID") && row.get() == 2)
                                          return id;
                                      }
                                      if (read.getName().equals(FIXTURE_GETSTRING_B3B802ED)
                                          && columns[0].equals(FIXTURE_STATUS_CFC31BCC)
                                          && row.get() == 1) {
                                        if (fault.equals("NULL_STATUS")) return null;
                                        if (fault.equals("UNKNOWN_STATUS")) return "UNKNOWN";
                                        if (Set.of(
                                                FIXTURE_RUNNING_294BDBF9,
                                                FIXTURE_FAILED_7E8A57FE,
                                                "WARNING",
                                                "SKIPPED")
                                            .contains(fault)) return fault;
                                      }
                                      return value;
                                    });
                              });
                        });
              },
              c -> {});
      Boolean result =
          subject.execute(
              credential(),
              session -> {
                var current = session.beginResumeBackup(original, observed);
                session.completeReusedBackup(current, original, observed);
                mdb2490SqlRows(run, started, observed, id);
                armed.set(true);
                if (Set.of("FOREIGN_ID", "DUPLICATE_ID", "NULL_ID", "NULL_STATUS", "UNKNOWN_STATUS")
                    .contains(fault)) {
                  assertThrows(
                      IOException.class,
                      () -> session.retainedBackupSuccessful(original, observed),
                      fault);
                } else {
                  assertEquals(
                      fault.equals("VALID"),
                      session.retainedBackupSuccessful(original, observed),
                      fault);
                }
                armed.set(false);
                mdb2490SqlRows(run, started, observed, id);
                return Boolean.TRUE;
              });
      assertEquals(Boolean.TRUE, result);
      assertTrue(observedRows.get() > 0, fault);
      assertTrue(retained.get().isClosed());
      mdb2490SqlRows(run, started, observed, id);
      mdb2292NoOwnerResources();
    }
    assertEquals(12, ordinal);
  }

  /** PT-MDB2572-001: a forged data-only pair cannot consume the held original proof. */
  @Test
  void mdb2572001ReusedBackupRequiresExactManifestSkippedPairAndFreshTime() throws Exception {
    int ordinal = 0;
    for (String fault :
        List.of("VALID", "MANIFEST", "DATABASE_NOT_SKIPPED", "CONFIG_NOT_SKIPPED", "STALE_TIME")) {
      int n = ++ordinal;
      var run =
          new BatchRun(
              UUID.fromString("25720001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
              Instant.parse("2043-01-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = run.cutoff().plusSeconds(11 * 3600);
      var observed = started.plusSeconds(3600);
      long id = 25720010L + n * 10;
      mdb2480Seed(run, started, id, true);
      var original =
          mdb2482Manifest(
              new MorningDatabaseSession.BackupBegins(
                  new BatchStepAttempt(id + 1, run, BatchStep.BACKUP_DB, 1, started, false),
                  new BatchStepAttempt(id, run, BatchStep.BACKUP_CONFIG, 1, started, false)),
              started);
      var retained = new AtomicReference<Connection>();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var connection = DriverManager.getConnection(url, properties);
                retained.set(connection);
                return connection;
              },
              c -> {});
      subject.execute(
          credential(),
          session -> {
            var current = session.beginResumeBackup(original, observed);
            mdb2490SqlRows(run, started, observed, id);
            var offeredManifest =
                fault.equals("MANIFEST")
                    ? new BackupManifest(
                        original.databaseStep(),
                        original.configurationStep(),
                        original.startedAt(),
                        original.contentFinishedAt(),
                        original.versions(),
                        "4".repeat(64),
                        original.dump(),
                        original.configuration(),
                        original.credentials())
                    : original;
            var offeredDatabase =
                fault.equals("DATABASE_NOT_SKIPPED")
                    ? new BatchStepAttempt(
                        current.database().id(), run, BatchStep.BACKUP_DB, 2, observed, false)
                    : current.database();
            var offeredConfiguration =
                fault.equals("CONFIG_NOT_SKIPPED")
                    ? new BatchStepAttempt(
                        current.configuration().id(),
                        run,
                        BatchStep.BACKUP_CONFIG,
                        2,
                        observed,
                        false)
                    : current.configuration();
            var offered =
                new MorningDatabaseSession.BackupBegins(offeredDatabase, offeredConfiguration);
            if (fault.equals("VALID")) {
              session.completeReusedBackup(offered, offeredManifest, observed);
              assertEquals(
                  2,
                  session
                      .observeBackup(
                          current, Optional.of(original), observed, () -> 10_000_000_000L)
                      .prior()
                      .size());
            } else {
              Throwable rejected =
                  assertThrows(
                      Throwable.class,
                      () ->
                          session.completeReusedBackup(
                              offered,
                              offeredManifest,
                              fault.equals("STALE_TIME") ? started.minusSeconds(1) : observed),
                      fault);
              if (fault.equals("STALE_TIME")) {
                assertInstanceOf(IllegalArgumentException.class, rejected);
                assertEquals("invalid backup observation time", rejected.getMessage());
              } else {
                assertInstanceOf(IOException.class, rejected);
              }
            }
            mdb2490SqlRows(run, started, observed, id);
            return Boolean.TRUE;
          });
      assertTrue(retained.get().isClosed());
      mdb2490SqlRows(run, started, observed, id);
      mdb2292NoOwnerResources();
    }
    assertEquals(5, ordinal);
  }

  /** PT-MDB2570-001: finished-pair proof still needs fresh JDBC and owner admission. */
  @Test
  void mdb2570001FailedBackupFinalGuardsRejectDriverAndOwnerDriftWithoutChangingPair()
      throws Exception {
    int ordinal = 0;
    for (String operation : List.of("SNAPSHOT", "OBSERVE", "RECHECK")) {
      for (String fault :
          List.of(
              "AUTOCOMMIT",
              "READONLY",
              "ISOLATION",
              FIXTURE_SQL_5B7E398D,
              "OWNER",
              "HELD",
              "FINAL_HELD")) {
        if (!operation.equals("SNAPSHOT") && fault.equals("ISOLATION")) continue;
        if (operation.equals("RECHECK") && fault.equals("OWNER")) continue;
        if (operation.equals("RECHECK") && fault.equals("FINAL_HELD")) continue;
        int n = ++ordinal;
        var run =
            new BatchRun(
                UUID.fromString(
                    "25700001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
                Instant.parse("2042-01-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
        var started = run.cutoff().plusSeconds(11 * 3600);
        var ended = started.plusSeconds(3);
        var armed = new AtomicBoolean();
        var injected = new AtomicBoolean();
        var heldReads = new AtomicInteger();
        var retained = new AtomicReference<Connection>();
        var subject =
            new MorningDatabaseSession(
                actualUrl,
                () -> {},
                (url, properties) -> {
                  var connection = DriverManager.getConnection(url, properties);
                  retained.set(connection);
                  return (Connection)
                      Proxy.newProxyInstance(
                          Connection.class.getClassLoader(),
                          new Class<?>[] {Connection.class},
                          (unused, method, args) -> {
                            if (armed.get()) {
                              String name = method.getName();
                              if (fault.equals("AUTOCOMMIT")
                                  && name.equals(FIXTURE_GETAUTOCOMMIT_C0200BDE)) {
                                injected.set(true);
                                return false;
                              }
                              if (fault.equals("READONLY") && name.equals("isReadOnly")) {
                                injected.set(true);
                                return true;
                              }
                              if (fault.equals("ISOLATION")
                                  && name.equals(FIXTURE_GETTRANSACTIONISOLATION_6ED78CE6)) {
                                injected.set(true);
                                return Connection.TRANSACTION_SERIALIZABLE;
                              }
                              if (fault.equals(FIXTURE_SQL_5B7E398D)
                                  && name.equals(FIXTURE_GETAUTOCOMMIT_C0200BDE)) {
                                injected.set(true);
                                throw new SQLException("public final guard unavailable", "08006");
                              }
                            }
                            Object actual = mdb2292Invoke(method, connection, args);
                            if (!armed.get()
                                || !(fault.equals("HELD") || fault.equals("FINAL_HELD"))
                                || !method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                                || !((String) args[0])
                                    .contains("select exists(select 1 from pg_catalog.pg_locks"))
                              return actual;
                            var statement = (PreparedStatement) actual;
                            return Proxy.newProxyInstance(
                                PreparedStatement.class.getClassLoader(),
                                new Class<?>[] {PreparedStatement.class},
                                (unusedStatement, called, input) -> {
                                  Object real = mdb2292Invoke(called, statement, input);
                                  if (!called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423))
                                    return real;
                                  var rows = (ResultSet) real;
                                  return Proxy.newProxyInstance(
                                      ResultSet.class.getClassLoader(),
                                      new Class<?>[] {ResultSet.class},
                                      (unusedRow, read, columns) -> {
                                        Object observed = mdb2292Invoke(read, rows, columns);
                                        if (read.getName().equals(FIXTURE_GETOBJECT_B6112877)
                                            && columns[0].equals("value")) {
                                          int index = heldReads.incrementAndGet();
                                          if (fault.equals("HELD") || index == 2) {
                                            injected.set(true);
                                            return false;
                                          }
                                        }
                                        return observed;
                                      });
                                });
                          });
                },
                c -> {});
        subject.execute(
            credential(),
            session -> {
              var begins = session.beginBackup(run, started, false);
              var failure =
                  new BatchStepResult(
                      BatchStepResult.Status.FAILED,
                      1,
                      0,
                      1,
                      0,
                      BatchStepResult.Reason.COMMAND_FAILURE);
              session.failBackup(begins, ended, failure, failure);
              var baseline = session.failedBackupSnapshot(begins, () -> 10_000_000_000L);
              assertEquals(begins.database(), baseline.database());
              assertEquals(begins.configuration(), baseline.configuration());
              assertEquals(ended, baseline.endedAt());
              armed.set(true);
              dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner =
                  () -> {
                    if (fault.equals("OWNER")) {
                      injected.set(true);
                      throw new IOException("public owner deadline unavailable");
                    }
                    return 10_000_000_000L;
                  };
              try {
                assertThrows(
                    IOException.class,
                    () -> {
                      switch (operation) {
                        case "SNAPSHOT" -> session.failedBackupSnapshot(begins, owner);
                        case "OBSERVE" ->
                            session.observeBackup(begins, Optional.empty(), ended, owner);
                        default -> session.recheckConsistent(run);
                      }
                    },
                    operation + ":" + fault);
              } finally {
                armed.set(false);
              }
              assertTrue(injected.get(), operation + ":" + fault);
              // Independent actual SQL must still expose the same committed terminal pair.
              mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(ended));
              // Failed callbacks may leave a transaction pending; do not mint renewed authority.
              // The outer execute closes it, and independent SQL/resource post is mandatory.
              return Boolean.TRUE;
            });
        assertTrue(retained.get().isClosed());
        mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(ended));
        mdb2292NoOwnerResources();
      }
    }
    assertEquals(17, ordinal);
  }

  /** PT-MDB2568-001: actual abandoned rows, independent per-component readback refusal. */
  @Test
  void mdb2568001AbandonedRequestRejectsEveryUntrustedPairComponentWithoutMutation()
      throws Exception {
    int ordinal = 0;
    for (String fault :
        List.of(
            "VALID",
            "FIRST_MISSING",
            "SECOND_MISSING",
            "EXTRA",
            FIXTURE_SQL_5B7E398D,
            "STEP",
            "ATTEMPT",
            "STATUS",
            FIXTURE_ERROR_F717E7D8,
            "END_BEFORE",
            "END_AFTER",
            "DATE",
            "NULL_END")) {
      int n = ++ordinal;
      var run =
          new BatchRun(
              UUID.fromString("25680001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, n)),
              Instant.parse("2041-01-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var oldStart = run.cutoff().plusSeconds(11 * 3600);
      var freshStart = oldStart.plusSeconds(10);
      var previous =
          new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(run.id(), oldStart);
      var plain =
          new MorningDatabaseSession(actualUrl, () -> {}, DriverManager::getConnection, c -> {});
      assertTrue(
          plain.<Boolean>execute(
              credential(),
              s -> {
                s.beginBackup(run, oldStart, false);
                return true;
              }));
      var retained = new AtomicReference<Connection>();
      var readCount = new AtomicInteger();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var connection = DriverManager.getConnection(url, properties);
                retained.set(connection);
                return (Connection)
                    Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          Object value = mdb2292Invoke(method, connection, args);
                          if (!method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                              || !((String) args[0])
                                  .contains(
                                      FIXTURE_SELECT_8DAC6259
                                          + " step,attempt,status,error_code,ended_at,business_date"))
                            return value;
                          var statement = (PreparedStatement) value;
                          return Proxy.newProxyInstance(
                              PreparedStatement.class.getClassLoader(),
                              new Class<?>[] {PreparedStatement.class},
                              (ignored, called, input) -> {
                                if (called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423)
                                    && fault.equals(FIXTURE_SQL_5B7E398D))
                                  throw new SQLException(
                                      "public abandoned fixture unavailable", "08006");
                                Object actual = mdb2292Invoke(called, statement, input);
                                if (!called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423))
                                  return actual;
                                var rows = (ResultSet) actual;
                                var row = new AtomicInteger();
                                return Proxy.newProxyInstance(
                                    ResultSet.class.getClassLoader(),
                                    new Class<?>[] {ResultSet.class},
                                    (ignoredRow, read, columns) -> {
                                      Object real = mdb2292Invoke(read, rows, columns);
                                      readCount.incrementAndGet();
                                      if (read.getName().equals(FIXTURE_NEXT_CA1733B5)) {
                                        int index = row.incrementAndGet();
                                        if (fault.equals("FIRST_MISSING") && index == 1
                                            || fault.equals("SECOND_MISSING") && index == 2)
                                          return false;
                                        if (fault.equals("EXTRA") && index == 3) return true;
                                        return real;
                                      }
                                      if (row.get() != 1
                                          || !(read.getName().equals(FIXTURE_GETOBJECT_B6112877)
                                              || read.getName().equals(FIXTURE_GETSTRING_B3B802ED)))
                                        return real;
                                      String key = (String) columns[0];
                                      if (fault.equals("STEP") && key.equals("step"))
                                        return FIXTURE_BACKUP_DB_6C03A087;
                                      if (fault.equals("ATTEMPT") && key.equals("attempt"))
                                        return 2;
                                      if (fault.equals("STATUS")
                                          && key.equals(FIXTURE_STATUS_CFC31BCC))
                                        return FIXTURE_SUCCESS_10855C7F;
                                      if (fault.equals(FIXTURE_ERROR_F717E7D8)
                                          && key.equals(FIXTURE_ERROR_CODE_B886CCEF))
                                        return "COMMAND_FAILURE";
                                      if (fault.equals("END_BEFORE")
                                          && key.equals(FIXTURE_ENDED_AT_E151E393))
                                        return oldStart
                                            .minusSeconds(1)
                                            .atOffset(java.time.ZoneOffset.UTC);
                                      if (fault.equals("END_AFTER")
                                          && key.equals(FIXTURE_ENDED_AT_E151E393))
                                        return freshStart
                                            .plusSeconds(1)
                                            .atOffset(java.time.ZoneOffset.UTC);
                                      if (fault.equals("DATE") && key.equals("business_date"))
                                        return run.cutoff()
                                            .atZone(java.time.ZoneId.of("Asia/Tokyo"))
                                            .toLocalDate()
                                            .plusDays(1);
                                      if (fault.equals("NULL_END")
                                          && key.equals(FIXTURE_ENDED_AT_E151E393)) return null;
                                      return real;
                                    });
                              });
                        });
              },
              c -> {});
      MorningDatabaseSession.Operation<Boolean> operation =
          s -> {
            var begun = s.beginBackup(run, freshStart, true);
            assertEquals(2, begun.database().attempt());
            assertEquals(2, begun.configuration().attempt());
            s.requireAbandonedRequest(previous);
            return true;
          };
      if (fault.equals("VALID")) assertTrue(subject.execute(credential(), operation));
      else assertThrows(IOException.class, () -> subject.execute(credential(), operation), fault);
      assertTrue(retained.get().isClosed(), fault);
      if (!fault.equals(FIXTURE_SQL_5B7E398D)) assertTrue(readCount.get() > 0, fault);
      try (var connection =
              DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
          var statement =
              connection.prepareStatement(
                  "select step,attempt,status,error_code,started_at,ended_at from"
                      + " schubert.batch_runs where run_id=? order by step,attempt")) {
        statement.setObject(1, run.id());
        try (var rows = statement.executeQuery()) {
          for (String step : List.of(FIXTURE_BACKUP_CONFIG_8386D7E7, FIXTURE_BACKUP_DB_6C03A087)) {
            for (int attempt = 1; attempt <= 2; attempt++) {
              assertTrue(rows.next(), fault);
              assertEquals(step, rows.getString("step"));
              assertEquals(attempt, rows.getInt("attempt"));
              assertEquals(
                  attempt == 1 ? FIXTURE_FAILED_7E8A57FE : FIXTURE_RUNNING_294BDBF9,
                  rows.getString(FIXTURE_STATUS_CFC31BCC));
              assertEquals(
                  attempt == 1 ? "ABANDONED" : null, rows.getString(FIXTURE_ERROR_CODE_B886CCEF));
              assertEquals(
                  attempt == 1 ? oldStart : freshStart,
                  rows.getTimestamp(FIXTURE_STARTED_AT_D1210657).toInstant());
              assertEquals(
                  attempt == 1 ? freshStart : null,
                  Optional.ofNullable(rows.getTimestamp(FIXTURE_ENDED_AT_E151E393))
                      .map(Timestamp::toInstant)
                      .orElse(null));
            }
          }
          assertFalse(rows.next());
        }
      }
      mdb2292NoOwnerResources();
    }
  }

  /** PT-MDB2504-001: default lookup binds only the supplied run, not time or authority claims. */
  @Test
  void mdb2504001CurrentRunReferencePreservesExactIdentityAndRejectsForeignUuid() throws Exception {
    var expected =
        new BatchRun(
            UUID.fromString("25040001-2222-4333-8444-555555555555"),
            Instant.parse("2037-01-09T15:00:00Z"));
    var lookup = MorningDatabaseSession.currentRunReference(expected);
    assertSame(
        expected,
        lookup.resolve(
            UUID.fromString("25040001-2222-4333-8444-555555555555"),
            Instant.parse("2037-01-10T02:00:00Z")));
    assertSame(
        expected,
        lookup.resolve(
            UUID.fromString("25040001-2222-4333-8444-555555555555"),
            Instant.parse("2040-01-10T02:00:00Z")));
    IOException rejected =
        assertThrows(
            IOException.class,
            () ->
                lookup.resolve(
                    UUID.fromString("25040002-2222-4333-8444-555555555555"),
                    Instant.parse("2037-01-10T02:00:00Z")));
    assertEquals(FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, rejected.getMessage());
    assertFalse(rejected.getMessage().contains("25040002"));
    assertThrows(
        NullPointerException.class, () -> MorningDatabaseSession.currentRunReference(null));
    assertThrows(
        NullPointerException.class,
        () -> lookup.resolve(null, Instant.parse("2037-01-10T02:00:00Z")));
  }

  /** PT-MDB2490-001: reverse original IDs remain ordered by role; claims never replace facts. */
  @Test
  void mdb2490001SkippedBackupRequiresOriginalManifestAndActualReverseOrderedPair()
      throws Exception {
    int n = 0;
    for (String mode : List.of("VALID", "MISSING", "DRIFT", "ORIGINAL_EMPTY")) {
      var run =
          new BatchRun(
              UUID.fromString(
                  "24900001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, ++n)),
              Instant.parse("2036-01-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = Instant.parse("2036-01-10T02:00:00Z").plusSeconds((n - 1L) * 86400);
      long id = 24900010L + n * 10;
      mdb2480Seed(run, started, id, true);
      var original =
          mdb2482Manifest(
              new MorningDatabaseSession.BackupBegins(
                  new BatchStepAttempt(id + 1, run, BatchStep.BACKUP_DB, 1, started, false),
                  new BatchStepAttempt(id, run, BatchStep.BACKUP_CONFIG, 1, started, false)),
              started);
      var retained = new AtomicReference<Connection>();
      var armed = new AtomicBoolean();
      var observed = started.plusSeconds(3600);
      var subject = mdb2490Subject(mode, retained, armed);
      MorningDatabaseSession.Operation<Boolean> operation =
          session -> {
            var current = session.beginResumeBackup(original, observed);
            session.completeReusedBackup(current, original, observed);
            armed.set(true);
            var offered =
                mode.equals("MISSING") ? Optional.<BackupManifest>empty() : Optional.of(original);
            if (mode.equals("DRIFT"))
              offered =
                  Optional.of(
                      new BackupManifest(
                          original.databaseStep(),
                          original.configurationStep(),
                          original.startedAt(),
                          original.contentFinishedAt(),
                          original.versions(),
                          "4".repeat(64),
                          original.dump(),
                          original.configuration(),
                          original.credentials()));
            var result = session.observeBackup(current, offered, observed, () -> 10_000_000_000L);
            var physicalCurrent = mdb2490SqlRows(run, started, observed, id);
            assertEquals(2, result.current().size());
            assertEquals(2, result.prior().size());
            for (int i = 0; i < 2; i++) {
              String step = i == 0 ? FIXTURE_BACKUP_DB_6C03A087 : FIXTURE_BACKUP_CONFIG_8386D7E7;
              var fresh = result.current().get(i);
              var prior = result.prior().get(i);
              assertEquals(physicalCurrent.get(step).longValue(), fresh.attempt().id());
              assertEquals(step, fresh.attempt().step().name());
              assertTrue(fresh.attempt().skipped());
              assertEquals(2, fresh.attempt().attempt());
              assertEquals(observed, fresh.attempt().startedAt());
              assertEquals(observed, fresh.ended());
              assertEquals(BatchStepResult.Status.SKIPPED, fresh.result().status());
              assertEquals(BatchStepResult.Reason.ALREADY_SUCCESSFUL, fresh.result().reason());
              assertEquals(0, fresh.result().target());
              assertEquals(0, fresh.result().bytes());
              assertEquals(i == 0 ? id + 1 : id, prior.attempt().id());
              assertEquals(step, prior.attempt().step().name());
              assertFalse(prior.attempt().skipped());
              assertEquals(started, prior.attempt().startedAt());
              assertEquals(started.plusSeconds(3), prior.ended());
              assertEquals(BatchStepResult.Status.SUCCESS, prior.result().status());
              assertEquals(i + 1, prior.result().target());
              assertEquals(i + 1, prior.result().success());
              assertEquals(i == 0 ? 26 : 67, prior.result().bytes());
            }
            return Boolean.TRUE;
          };
      if (mode.equals("VALID")) assertTrue(subject.execute(credential(), operation));
      else assertThrows(IOException.class, () -> subject.execute(credential(), operation));
      assertTrue(retained.get().isClosed());
      mdb2490SqlRows(run, started, observed, id);
      mdb2292NoOwnerResources();
    }
  }

  /** PT-MDB2490-002: both rows and exact cardinality must be present at terminal readback. */
  @Test
  void mdb2490002TerminalPairRejectsMissingAndExtraDriverRows() throws Exception {
    int n = 0;
    for (String mode : List.of("FIRST_MISSING", "SECOND_MISSING", "EXTRA")) {
      var run =
          new BatchRun(
              UUID.fromString(
                  "24900002-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, ++n)),
              Instant.parse("2036-02-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = Instant.parse("2036-02-10T02:00:00Z").plusSeconds((n - 1L) * 86400);
      var retained = new AtomicReference<Connection>();
      var armed = new AtomicBoolean();
      assertThrows(
          IOException.class,
          () ->
              mdb2490Subject(mode, retained, armed)
                  .execute(
                      credential(),
                      session -> {
                        var current = session.beginBackup(run, started, false);
                        var failed =
                            new BatchStepResult(
                                BatchStepResult.Status.FAILED,
                                1,
                                0,
                                1,
                                0,
                                BatchStepResult.Reason.COMMAND_FAILURE);
                        session.failBackup(current, started.plusSeconds(3), failed, failed);
                        armed.set(true);
                        session.observeBackup(
                            current,
                            Optional.empty(),
                            started.plusSeconds(5),
                            () -> 10_000_000_000L);
                        return Boolean.TRUE;
                      }));
      assertTrue(retained.get().isClosed());
      mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(started.plusSeconds(3)));
      mdb2292NoOwnerResources();
    }
  }

  private static Map<String, Long> mdb2490SqlRows(
      BatchRun run, Instant started, Instant observed, long id) throws IOException {
    var current = new HashMap<String, Long>();
    try (var c = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var s =
            c.prepareStatement(
                FIXTURE_SELECT_8DAC6259
                    + " id,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary"
                    + " from schubert.batch_runs where run_id=? order by attempt,step")) {
      s.setObject(1, run.id());
      try (var r = s.executeQuery()) {
        for (int attempt = 1; attempt <= 2; attempt++)
          for (String step : List.of(FIXTURE_BACKUP_CONFIG_8386D7E7, FIXTURE_BACKUP_DB_6C03A087)) {
            assertTrue(r.next());
            assertEquals(step, r.getString("step"));
            assertEquals(attempt, r.getInt("attempt"));
            assertEquals(
                attempt == 1 ? started : observed,
                r.getTimestamp(FIXTURE_STARTED_AT_D1210657).toInstant());
            assertEquals(
                attempt == 1 ? started.plusSeconds(3) : observed,
                r.getTimestamp(FIXTURE_ENDED_AT_E151E393).toInstant());
            assertEquals(
                attempt == 1 ? FIXTURE_SUCCESS_10855C7F : "SKIPPED",
                r.getString(FIXTURE_STATUS_CFC31BCC));
            long count = attempt == 2 ? 0 : step.equals(FIXTURE_BACKUP_DB_6C03A087) ? 1 : 2;
            assertEquals(count, r.getLong(FIXTURE_TARGET_COUNT_5B6567D4));
            assertEquals(count, r.getLong(FIXTURE_SUCCESS_COUNT_716E5185));
            assertEquals(0, r.getLong(FIXTURE_FAILURE_COUNT_C7E67F21));
            assertEquals(
                attempt == 2 ? 0 : step.equals(FIXTURE_BACKUP_DB_6C03A087) ? 26 : 67,
                r.getLong(FIXTURE_BYTE_COUNT_6D76E237));
            assertEquals(
                attempt == 1 ? null : "ALREADY_SUCCESSFUL",
                r.getString(FIXTURE_ERROR_CODE_B886CCEF));
            assertEquals(
                attempt == 1 ? null : "step already successful for business date",
                r.getString(FIXTURE_ERROR_SUMMARY_3F58BF23));
            if (attempt == 1)
              assertEquals(step.equals(FIXTURE_BACKUP_DB_6C03A087) ? id + 1 : id, r.getLong("id"));
            else current.put(step, r.getLong("id"));
          }
        assertFalse(r.next());
      }
    } catch (SQLException failure) {
      throw new IOException("independent isolated SQL postcondition unavailable", failure);
    }
    return current;
  }

  private static MorningDatabaseSession mdb2490Subject(
      String mode, AtomicReference<Connection> retained, AtomicBoolean armed) {
    var queries = new AtomicInteger();
    return new MorningDatabaseSession(
        actualUrl,
        () -> {},
        (url, properties) -> {
          var c = DriverManager.getConnection(url, properties);
          retained.set(c);
          return (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (ignored, method, args) -> {
                    Object result = mdb2292Invoke(method, c, args);
                    if (!armed.get()
                        || !method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                        || !((String) args[0]).contains("order by id for update")
                        || !((String) args[0]).contains("from schubert.batch_runs")) return result;
                    var statement = (PreparedStatement) result;
                    return Proxy.newProxyInstance(
                        PreparedStatement.class.getClassLoader(),
                        new Class<?>[] {PreparedStatement.class},
                        (unused, called, input) -> {
                          Object value = mdb2292Invoke(called, statement, input);
                          if (!called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423)) return value;
                          int query = queries.incrementAndGet();
                          var rows = (ResultSet) value;
                          var ordinal = new AtomicInteger();
                          return Proxy.newProxyInstance(
                              ResultSet.class.getClassLoader(),
                              new Class<?>[] {ResultSet.class},
                              (unusedRows, read, columns) -> {
                                Object real = mdb2292Invoke(read, rows, columns);
                                if (!read.getName().equals(FIXTURE_NEXT_CA1733B5)) return real;
                                int row = ordinal.incrementAndGet();
                                if (mode.equals("ORIGINAL_EMPTY") && query == 2 && row == 1)
                                  return false;
                                if (query == 1) {
                                  if (mode.equals("FIRST_MISSING") && row == 1
                                      || mode.equals("SECOND_MISSING") && row == 2) return false;
                                  if (mode.equals("EXTRA") && row == 3) return true;
                                }
                                return real;
                              });
                        });
                  });
        },
        c -> {});
  }

  /** PT-MDB2486-001: a lost final advisory observation rejects otherwise valid readback. */
  @Test
  void mdb2486001FinalAdvisoryObservationCannotReuseInitialAdmission() throws Exception {
    int n = 0;
    for (String operation : List.of("OBSERVE", "RETENTION")) {
      var run =
          new BatchRun(
              UUID.fromString(
                  "24860001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, ++n)),
              Instant.parse("2035-01-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = Instant.parse("2035-01-10T02:00:00Z").plusSeconds((n - 1L) * 86400);
      var retained = new AtomicReference<Connection>();
      var armed = new AtomicBoolean();
      var observations = new AtomicInteger();
      assertThrows(
          IOException.class,
          () ->
              mdb2486Subject("HELD", retained, armed, observations)
                  .execute(
                      credential(),
                      session -> {
                        var begins = session.beginBackup(run, started, false);
                        var failed =
                            new BatchStepResult(
                                BatchStepResult.Status.FAILED,
                                1,
                                0,
                                1,
                                0,
                                BatchStepResult.Reason.COMMAND_FAILURE);
                        session.failBackup(begins, started.plusSeconds(3), failed, failed);
                        armed.set(true);
                        if (operation.equals("OBSERVE"))
                          session.observeBackup(
                              begins,
                              Optional.empty(),
                              started.plusSeconds(5),
                              () -> 10_000_000_000L);
                        else
                          session.retainedBackupSuccessful(
                              mdb2482Manifest(begins, started), started.plusSeconds(5));
                        return Boolean.TRUE;
                      }));
      assertEquals(2, observations.get());
      assertTrue(retained.get().isClosed());
      mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(started.plusSeconds(3)));
      mdb2292NoOwnerResources();
    }
  }

  /** PT-MDB2486-002: observed terminal contents must match the actual committed failure. */
  @Test
  void mdb2486002TerminalResultTimeAndFailureReasonCannotBeReinterpreted() throws Exception {
    int n = 0;
    for (String fault : List.of(FIXTURE_SUCCESS_10855C7F, "END", "REASON")) {
      var run =
          new BatchRun(
              UUID.fromString(
                  "24860002-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, ++n)),
              Instant.parse("2035-02-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = Instant.parse("2035-02-10T02:00:00Z").plusSeconds((n - 1L) * 86400);
      var retained = new AtomicReference<Connection>();
      var armed = new AtomicBoolean();
      assertThrows(
          IOException.class,
          () ->
              mdb2486Subject(fault, retained, armed, new AtomicInteger())
                  .execute(
                      credential(),
                      session -> {
                        var begins = session.beginBackup(run, started, false);
                        var failed =
                            new BatchStepResult(
                                BatchStepResult.Status.FAILED,
                                1,
                                0,
                                1,
                                0,
                                fault.equals("REASON")
                                    ? BatchStepResult.Reason.IO_FAILURE
                                    : BatchStepResult.Reason.COMMAND_FAILURE);
                        session.failBackup(begins, started.plusSeconds(3), failed, failed);
                        armed.set(true);
                        session.observeBackup(
                            begins,
                            Optional.empty(),
                            started.plusSeconds(5),
                            () -> 10_000_000_000L);
                        return Boolean.TRUE;
                      }));
      assertTrue(retained.get().isClosed());
      mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(started.plusSeconds(3)));
      try (var c = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
          var s =
              c.prepareStatement(
                  "select error_code,error_summary from schubert.batch_runs where run_id=? order by"
                      + " id")) {
        s.setObject(1, run.id());
        try (var r = s.executeQuery()) {
          for (int i = 0; i < 2; i++) {
            assertTrue(r.next());
            assertEquals(fault.equals("REASON") ? "IO_FAILURE" : "COMMAND_FAILURE", r.getString(1));
            assertEquals(
                fault.equals("REASON") ? "batch file operation failed" : "batch command failed",
                r.getString(2));
          }
          assertFalse(r.next());
        }
      }
      mdb2292NoOwnerResources();
    }
  }

  private static MorningDatabaseSession mdb2486Subject(
      String fault,
      AtomicReference<Connection> retained,
      AtomicBoolean armed,
      AtomicInteger observations) {
    return new MorningDatabaseSession(
        actualUrl,
        () -> {},
        (url, properties) -> {
          var c = DriverManager.getConnection(url, properties);
          retained.set(c);
          return (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (ignored, method, args) -> {
                    Object result = mdb2292Invoke(method, c, args);
                    if (!armed.get() || !method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F))
                      return result;
                    String sql = (String) args[0];
                    boolean held = fault.equals("HELD") && sql.contains("pg_locks");
                    boolean terminal =
                        !fault.equals("HELD")
                            && sql.contains("order by id for update")
                            && sql.contains("schubert.batch_runs");
                    if (!held && !terminal) return result;
                    var statement = (PreparedStatement) result;
                    return Proxy.newProxyInstance(
                        PreparedStatement.class.getClassLoader(),
                        new Class<?>[] {PreparedStatement.class},
                        (unused, called, input) -> {
                          Object value = mdb2292Invoke(called, statement, input);
                          if (!called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423)) return value;
                          int observation = held ? observations.incrementAndGet() : 0;
                          var rows = (ResultSet) value;
                          return Proxy.newProxyInstance(
                              ResultSet.class.getClassLoader(),
                              new Class<?>[] {ResultSet.class},
                              (unusedRows, read, columns) -> {
                                Object real = mdb2292Invoke(read, rows, columns);
                                if (held
                                    && observation == 2
                                    && (read.getName().equals("getBoolean")
                                        || (read.getName().equals(FIXTURE_GETOBJECT_B6112877)
                                            && columns[0].equals("value")))) return false;
                                if (!terminal
                                    || !(read.getName().equals(FIXTURE_GETOBJECT_B6112877)
                                        || read.getName().equals(FIXTURE_GETSTRING_B3B802ED)))
                                  return real;
                                String key = (String) columns[0];
                                if (fault.equals("END") && key.equals(FIXTURE_ENDED_AT_E151E393))
                                  return ((java.time.OffsetDateTime) real).plusSeconds(1);
                                if (fault.equals(FIXTURE_SUCCESS_10855C7F)) {
                                  return switch (key) {
                                    case FIXTURE_STATUS_CFC31BCC -> FIXTURE_SUCCESS_10855C7F;
                                    case FIXTURE_SUCCESS_COUNT_716E5185,
                                        FIXTURE_BYTE_COUNT_6D76E237 ->
                                        1L;
                                    case FIXTURE_FAILURE_COUNT_C7E67F21 -> 0L;
                                    case FIXTURE_ERROR_CODE_B886CCEF,
                                        FIXTURE_ERROR_SUMMARY_3F58BF23 ->
                                        null;
                                    default -> real;
                                  };
                                }
                                return real;
                              });
                        });
                  });
        },
        c -> {});
  }

  /** PT-MDB2482-001: real committed rows survive SQL refusal and expired owner admission. */
  @Test
  void mdb2482001BackupSqlRefusalAndExpiredOwnerPreserveCommittedRows() throws Exception {
    int n = 0;
    for (String operation :
        List.of("OBSERVE_SQL", "RETENTION_SQL", "FAIL_SQL", "ABANDON_SQL", "EXPIRED")) {
      var run =
          new BatchRun(
              UUID.fromString(
                  "24820001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, ++n)),
              Instant.parse("2034-01-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = Instant.parse("2034-01-10T02:00:00Z").plusSeconds((n - 1L) * 86400);
      var ended = started.plusSeconds(3);
      var fault = new AtomicReference<String>("");
      var retained = new AtomicReference<Connection>();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var c = DriverManager.getConnection(url, properties);
                retained.set(c);
                return (Connection)
                    Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (ignored, method, args) -> {
                          if (method.getName().equals(FIXTURE_GETAUTOCOMMIT_C0200BDE)
                              && fault.compareAndSet(FIXTURE_SQL_5B7E398D, ""))
                            throw new SQLException("public fixture admission unavailable", "08006");
                          return mdb2292Invoke(method, c, args);
                        });
              },
              c -> {});
      boolean unfinished = operation.equals("FAIL_SQL") || operation.equals("ABANDON_SQL");
      assertThrows(
          IOException.class,
          () ->
              subject.execute(
                  credential(),
                  session -> {
                    var begins = session.beginBackup(run, started, false);
                    var failed =
                        new BatchStepResult(
                            BatchStepResult.Status.FAILED,
                            1,
                            0,
                            1,
                            0,
                            BatchStepResult.Reason.COMMAND_FAILURE);
                    if (!unfinished) session.failBackup(begins, ended, failed, failed);
                    fault.set(operation.equals("EXPIRED") ? "" : FIXTURE_SQL_5B7E398D);
                    switch (operation) {
                      case "OBSERVE_SQL" ->
                          session.observeBackup(
                              begins, Optional.empty(), ended, () -> 10_000_000_000L);
                      case "RETENTION_SQL" ->
                          session.retainedBackupSuccessful(
                              mdb2482Manifest(begins, started), ended.plusSeconds(1));
                      case "FAIL_SQL" -> session.failBackup(begins, ended, failed, failed);
                      case "ABANDON_SQL" ->
                          session.requireAbandonedRequest(
                              new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(
                                  run.id(), started.minusSeconds(1)));
                      case "EXPIRED" ->
                          session.observeBackup(
                              begins,
                              Optional.empty(),
                              ended,
                              () -> {
                                throw new IOException("public fixture expired owner");
                              });
                      default -> throw new AssertionError("unregistered fixture operation");
                    }
                    return Boolean.TRUE;
                  }));
      assertEquals("", fault.get());
      assertTrue(retained.get().isClosed());
      mdb2292Rows(
          run,
          unfinished ? FIXTURE_RUNNING_294BDBF9 : FIXTURE_FAILED_7E8A57FE,
          started,
          unfinished ? Optional.empty() : Optional.of(ended));
      mdb2292NoOwnerResources();
    }
  }

  /** PT-MDB2482-002: a supplied manifest cannot replace the current actual committed pair. */
  @Test
  void mdb2482002ActualBackupManifestMismatchRejectsEveryPairComponent() throws Exception {
    int n = 0;
    for (String fault : List.of("DATABASE", "CONFIGURATION", "FAILED_PAIR")) {
      var run =
          new BatchRun(
              UUID.fromString(
                  "24820002-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, ++n)),
              Instant.parse("2034-02-09T15:00:00Z").plusSeconds((n - 1L) * 86400));
      var started = Instant.parse("2034-02-10T02:00:00Z").plusSeconds((n - 1L) * 86400);
      var ended = started.plusSeconds(3);
      var retained = new AtomicReference<Connection>();
      assertThrows(
          IOException.class,
          () ->
              mdb2292Subject(new AtomicReference<>(""), retained)
                  .execute(
                      credential(),
                      session -> {
                        var begins = session.beginBackup(run, started, false);
                        var failed =
                            new BatchStepResult(
                                BatchStepResult.Status.FAILED,
                                1,
                                0,
                                1,
                                0,
                                BatchStepResult.Reason.COMMAND_FAILURE);
                        session.failBackup(begins, ended, failed, failed);
                        var database = begins.database();
                        var configuration = begins.configuration();
                        if (fault.equals("DATABASE"))
                          database =
                              new BatchStepAttempt(
                                  database.id() + 100000,
                                  run,
                                  BatchStep.BACKUP_DB,
                                  1,
                                  started,
                                  false);
                        if (fault.equals("CONFIGURATION"))
                          configuration =
                              new BatchStepAttempt(
                                  configuration.id() + 100000,
                                  run,
                                  BatchStep.BACKUP_CONFIG,
                                  1,
                                  started,
                                  false);
                        session.observeBackup(
                            begins,
                            Optional.of(
                                mdb2482Manifest(
                                    new MorningDatabaseSession.BackupBegins(
                                        database, configuration),
                                    started)),
                            ended,
                            () -> 10_000_000_000L);
                        return Boolean.TRUE;
                      }));
      assertTrue(retained.get().isClosed());
      mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(ended));
      mdb2292NoOwnerResources();
    }
  }

  private static BackupManifest mdb2482Manifest(
      MorningDatabaseSession.BackupBegins begins, Instant started) {
    return new BackupManifest(
        begins.database(),
        begins.configuration(),
        started,
        started.plusSeconds(2),
        new BackupVersions(
            "public-host", "1.0", "023", "ubuntu-26.04", "25.0.4", "18.6", "2.56.0", "1.2.1"),
        "0".repeat(64),
        new BackupFileDigest(26, "1".repeat(64)),
        new BackupFileDigest(35, "2".repeat(64)),
        new BackupFileDigest(32, "3".repeat(64)));
  }

  /** PT-MDB2480-001: actual DB rows remain unchanged when JDBC projections are invalid. */
  @Test
  void mdb2480001SuccessfulBackupRejectsUntrustedProjectionAndPreservesSqlRows() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("24800001-2222-4333-8444-555555555555"),
            Instant.parse("2033-01-09T15:00:00Z"));
    var started = Instant.parse("2033-01-10T02:00:00Z");
    mdb2480Seed(run, started, 24800010);
    for (String fault :
        List.of(
            "DATE",
            "START",
            "FUTURE",
            "NANO",
            "TARGET",
            FIXTURE_SUCCESS_10855C7F,
            "FAILURE",
            "BYTE",
            "ERROR_CODE",
            "ERROR_SUMMARY",
            "NULL_ID",
            "NULL_STEP",
            "NULL_END")) {
      var retained = new AtomicReference<Connection>();
      IOException failure =
          assertThrows(
              IOException.class,
              () ->
                  mdb2480Subject(fault, retained)
                      .execute(
                          credential(),
                          session -> session.successfulBackup(run, started.plusSeconds(10))));
      assertEquals(FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, failure.getMessage());
      assertTrue(retained.get().isClosed());
      mdb2480SqlRows(run, started, 24800010);
      mdb2292NoOwnerResources();
    }
    mdb2480Positive(run, started, 24800010);
  }

  /** PT-MDB2480-002: incomplete/contradictory pairs or SQL failure cannot authorize reuse. */
  @Test
  void mdb2480002SuccessfulBackupRejectsPairDriftAndSqlFailureWithoutMutation() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("24800002-2222-4333-8444-555555555555"),
            Instant.parse("2033-02-09T15:00:00Z"));
    var started = Instant.parse("2033-02-10T02:00:00Z");
    mdb2480Seed(run, started, 24800020);
    for (String fault :
        List.of(
            "SECOND_MISSING",
            "EXTRA",
            "PAIR_STEP",
            "PAIR_ATTEMPT",
            "PAIR_START",
            "PAIR_END",
            FIXTURE_SQL_5B7E398D)) {
      var retained = new AtomicReference<Connection>();
      assertThrows(
          IOException.class,
          () ->
              mdb2480Subject(fault, retained)
                  .execute(
                      credential(),
                      session -> session.successfulBackup(run, started.plusSeconds(10))));
      assertTrue(retained.get().isClosed());
      mdb2480SqlRows(run, started, 24800020);
      mdb2292NoOwnerResources();
    }
    var retained = new AtomicReference<Connection>();
    assertEquals(
        Optional.empty(),
        mdb2480Subject("FIRST_MISSING", retained)
            .execute(
                credential(), session -> session.successfulBackup(run, started.plusSeconds(10))));
    assertTrue(retained.get().isClosed());
    mdb2480SqlRows(run, started, 24800020);
    mdb2292NoOwnerResources();
    mdb2480Positive(run, started, 24800020);
  }

  private static void mdb2480Seed(BatchRun run, Instant started, long id) throws SQLException {
    mdb2480Seed(run, started, id, false);
  }

  private static void mdb2480Seed(BatchRun run, Instant started, long id, boolean reverse)
      throws SQLException {
    try (var c = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var s =
            c.prepareStatement(
                "insert into schubert.batch_runs"
                    + "(id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,byte_count)"
                    + " values(?,?,?, ?,1,?,?,'SUCCESS',?,?,?)")) {
      for (int n = 0; n < 2; n++) {
        s.setLong(1, id + (reverse ? 1 - n : n));
        s.setObject(2, run.id());
        s.setObject(3, started.atZone(java.time.ZoneOffset.UTC).toLocalDate());
        s.setString(4, n == 0 ? FIXTURE_BACKUP_DB_6C03A087 : FIXTURE_BACKUP_CONFIG_8386D7E7);
        s.setTimestamp(5, Timestamp.from(started));
        s.setTimestamp(6, Timestamp.from(started.plusSeconds(3)));
        s.setLong(7, n + 1);
        s.setLong(8, n + 1);
        s.setLong(9, n == 0 ? 26 : 67);
        assertEquals(1, s.executeUpdate());
      }
    }
  }

  private static void mdb2480SqlRows(BatchRun run, Instant started, long id) throws SQLException {
    try (var c = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var s =
            c.prepareStatement(
                FIXTURE_SELECT_8DAC6259
                    + " id,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary"
                    + " from schubert.batch_runs where run_id=? order by id")) {
      s.setObject(1, run.id());
      try (var r = s.executeQuery()) {
        for (int n = 0; n < 2; n++) {
          assertTrue(r.next());
          assertEquals(id + n, r.getLong("id"));
          assertEquals(
              n == 0 ? FIXTURE_BACKUP_DB_6C03A087 : FIXTURE_BACKUP_CONFIG_8386D7E7,
              r.getString("step"));
          assertEquals(1, r.getInt("attempt"));
          assertEquals(started, r.getTimestamp(FIXTURE_STARTED_AT_D1210657).toInstant());
          assertEquals(
              started.plusSeconds(3), r.getTimestamp(FIXTURE_ENDED_AT_E151E393).toInstant());
          assertEquals(FIXTURE_SUCCESS_10855C7F, r.getString(FIXTURE_STATUS_CFC31BCC));
          assertEquals(n + 1, r.getLong(FIXTURE_TARGET_COUNT_5B6567D4));
          assertEquals(n + 1, r.getLong(FIXTURE_SUCCESS_COUNT_716E5185));
          assertEquals(0, r.getLong(FIXTURE_FAILURE_COUNT_C7E67F21));
          assertEquals(n == 0 ? 26 : 67, r.getLong(FIXTURE_BYTE_COUNT_6D76E237));
          assertNull(r.getString(FIXTURE_ERROR_CODE_B886CCEF));
          assertNull(r.getString(FIXTURE_ERROR_SUMMARY_3F58BF23));
        }
        assertFalse(r.next());
      }
    }
  }

  private static void mdb2480Positive(BatchRun run, Instant started, long id) throws Exception {
    var retained = new AtomicReference<Connection>();
    var expected =
        new MorningDatabaseSession.BackupBegins(
            new BatchStepAttempt(id, run, BatchStep.BACKUP_DB, 1, started, false),
            new BatchStepAttempt(id + 1, run, BatchStep.BACKUP_CONFIG, 1, started, false));
    assertEquals(
        Optional.of(expected),
        mdb2480Subject("", retained)
            .execute(
                credential(), session -> session.successfulBackup(run, started.plusSeconds(10))));
    assertTrue(retained.get().isClosed());
    mdb2480SqlRows(run, started, id);
    mdb2292NoOwnerResources();
  }

  private static MorningDatabaseSession mdb2480Subject(
      String fault, AtomicReference<Connection> retained) {
    return new MorningDatabaseSession(
        actualUrl,
        () -> {},
        (url, properties) -> {
          var c = DriverManager.getConnection(url, properties);
          retained.set(c);
          return (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (proxy, method, args) -> {
                    Object result = mdb2292Invoke(method, c, args);
                    if (!method.getName().equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                        || !((String) args[0]).contains("status='SUCCESS'")) return result;
                    var statement = (PreparedStatement) result;
                    return Proxy.newProxyInstance(
                        PreparedStatement.class.getClassLoader(),
                        new Class<?>[] {PreparedStatement.class},
                        (unused, called, input) -> {
                          if (called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423)
                              && fault.equals(FIXTURE_SQL_5B7E398D))
                            throw new SQLException(
                                "public fixture projection unavailable", "08006");
                          Object value = mdb2292Invoke(called, statement, input);
                          if (!called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423)) return value;
                          var rows = (ResultSet) value;
                          var ordinal = new AtomicInteger();
                          return Proxy.newProxyInstance(
                              ResultSet.class.getClassLoader(),
                              new Class<?>[] {ResultSet.class},
                              (ignored, read, columns) -> {
                                String name = read.getName();
                                if (name.equals(FIXTURE_NEXT_CA1733B5)) {
                                  int n = ordinal.incrementAndGet();
                                  boolean real = rows.next();
                                  if (fault.equals("FIRST_MISSING") && n == 1
                                      || fault.equals("SECOND_MISSING") && n == 2) return false;
                                  if (fault.equals("EXTRA") && n == 3) return true;
                                  return real;
                                }
                                Object real = mdb2292Invoke(read, rows, columns);
                                if (!(name.equals(FIXTURE_GETOBJECT_B6112877)
                                    || name.equals(FIXTURE_GETSTRING_B3B802ED))) return real;
                                String key = (String) columns[0];
                                if (ordinal.get() == 1) {
                                  if (fault.equals("DATE") && key.equals("business_date"))
                                    return ((java.time.LocalDate) real).plusDays(1);
                                  if (fault.equals("START")
                                      && key.equals(FIXTURE_STARTED_AT_D1210657))
                                    return ((java.time.OffsetDateTime) real).plusSeconds(4);
                                  if (fault.equals("FUTURE")
                                      && key.equals(FIXTURE_ENDED_AT_E151E393))
                                    return ((java.time.OffsetDateTime) real).plusSeconds(100);
                                  if (fault.equals("NANO") && key.equals(FIXTURE_ENDED_AT_E151E393))
                                    return ((java.time.OffsetDateTime) real).plusNanos(1);
                                  if ((fault.equals("TARGET")
                                          && key.equals(FIXTURE_TARGET_COUNT_5B6567D4))
                                      || (fault.equals(FIXTURE_SUCCESS_10855C7F)
                                          && key.equals(FIXTURE_SUCCESS_COUNT_716E5185))
                                      || (fault.equals("BYTE")
                                          && key.equals(FIXTURE_BYTE_COUNT_6D76E237))) return 0L;
                                  if (fault.equals("FAILURE")
                                      && key.equals(FIXTURE_FAILURE_COUNT_C7E67F21)) return 1L;
                                  if (fault.equals("ERROR_CODE")
                                          && key.equals(FIXTURE_ERROR_CODE_B886CCEF)
                                      || fault.equals("ERROR_SUMMARY")
                                          && key.equals(FIXTURE_ERROR_SUMMARY_3F58BF23))
                                    return "public fixture";
                                  if (fault.equals("NULL_ID") && key.equals("id")
                                      || fault.equals("NULL_STEP") && key.equals("step")
                                      || fault.equals("NULL_END")
                                          && key.equals(FIXTURE_ENDED_AT_E151E393)) return null;
                                }
                                if (ordinal.get() == 2) {
                                  if (fault.equals("PAIR_STEP") && key.equals("step"))
                                    return FIXTURE_BACKUP_CONFIG_8386D7E7;
                                  if (fault.equals("PAIR_ATTEMPT") && key.equals("attempt"))
                                    return 2;
                                  if (fault.equals("PAIR_START")
                                      && key.equals(FIXTURE_STARTED_AT_D1210657))
                                    return ((java.time.OffsetDateTime) real).plusSeconds(1);
                                  if (fault.equals("PAIR_END")
                                      && key.equals(FIXTURE_ENDED_AT_E151E393))
                                    return ((java.time.OffsetDateTime) real).plusSeconds(1);
                                }
                                return real;
                              });
                        });
                  });
        },
        connection -> {});
  }

  /** PT-MDB2292-001: each completion guard rejects JDBC drift before business mutation. */
  @Test
  void mdb2292001AbandonedRequestRejectsEveryJdbcInvariantBeforeMutation() throws Exception {
    int index = 0;
    for (String fault : List.of("AUTO", "READONLY", "ISOLATION", "HELD")) {
      var run =
          new BatchRun(
              UUID.fromString(
                  "22920001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, ++index)),
              Instant.parse("2031-01-09T15:00:00Z").plusSeconds((index - 1L) * 86400));
      var started = Instant.parse("2031-01-10T02:00:00Z").plusSeconds((index - 1L) * 86400);
      var drift = new AtomicReference<String>("");
      var retained = new AtomicReference<Connection>();
      var subject = mdb2292Subject(drift, retained);
      subject.execute(
          credential(),
          session -> {
            System.err.println("PT-MDB2292-001 phase=ENTER");
            session.beginBackup(run, started, false);
            System.err.println("PT-MDB2292-001 phase=BEGIN_OK");
            drift.set(fault);
            try {
              assertThrows(
                  IOException.class,
                  () ->
                      session.requireAbandonedRequest(
                          new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(
                              run.id(), started)));
            } finally {
              drift.set("");
            }
            mdb2292Rows(run, FIXTURE_RUNNING_294BDBF9, started, Optional.empty());
            return Boolean.TRUE;
          });
      assertTrue(retained.get().isClosed());
      mdb2292Rows(run, FIXTURE_RUNNING_294BDBF9, started, Optional.empty());
      mdb2292NoOwnerResources();
    }
  }

  /** PT-MDB2292-002: completed FAILED rows never become eligible or change on JDBC refusal. */
  @Test
  void mdb2292002RetentionRejectsJdbcDriftAndPreservesBothFailedRows() throws Exception {
    int index = 0;
    for (String fault : List.of("AUTO", "READONLY", "HELD")) {
      var run =
          new BatchRun(
              UUID.fromString(
                  "22920002-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, ++index)),
              Instant.parse("2031-02-02T15:00:00Z").plusSeconds((index - 1L) * 86400));
      var started = Instant.parse("2031-02-03T02:00:00Z").plusSeconds((index - 1L) * 86400);
      var ended = started.plusSeconds(3);
      var drift = new AtomicReference<String>("");
      var retained = new AtomicReference<Connection>();
      var subject = mdb2292Subject(drift, retained);
      subject.execute(
          credential(),
          session -> {
            System.err.println("PT-MDB2292-002 phase=ENTER");
            var begins = session.beginBackup(run, started, false);
            System.err.println("PT-MDB2292-002 phase=BEGIN_OK");
            var failed =
                new BatchStepResult(
                    BatchStepResult.Status.FAILED,
                    1,
                    0,
                    1,
                    0,
                    BatchStepResult.Reason.COMMAND_FAILURE);
            session.failBackup(begins, ended, failed, failed);
            var manifest =
                new BackupManifest(
                    begins.database(),
                    begins.configuration(),
                    started,
                    started.plusSeconds(2),
                    new BackupVersions(
                        "public-host",
                        "1.0",
                        "028",
                        "ubuntu-26.04",
                        "25.0.4",
                        "18.6",
                        "2.56.0",
                        "1.2.1"),
                    "0".repeat(64),
                    new BackupFileDigest(26, "1".repeat(64)),
                    new BackupFileDigest(35, "2".repeat(64)),
                    new BackupFileDigest(32, "3".repeat(64)));
            drift.set(fault);
            try {
              assertThrows(
                  IOException.class,
                  () -> session.retainedBackupSuccessful(manifest, ended.plusSeconds(1)));
            } finally {
              drift.set("");
            }
            assertFalse(session.retainedBackupSuccessful(manifest, ended.plusSeconds(1)));
            mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(ended));
            return Boolean.TRUE;
          });
      assertTrue(retained.get().isClosed());
      mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(ended));
      mdb2292NoOwnerResources();
    }
  }

  /** PT-MDB2402-001: observation cannot relax an owned JDBC invariant or mutate failed rows. */
  @Test
  void mdb2402001ObservationRejectsJdbcDriftBeforeMutation() throws Exception {
    int index = 0;
    for (String fault : List.of("AUTO", "READONLY", "HELD")) {
      var run =
          new BatchRun(
              UUID.fromString(
                  "24020001-2222-4333-8444-" + String.format(FIXTURE_012D_02D3076F, ++index)),
              Instant.parse("2032-01-09T15:00:00Z").plusSeconds((index - 1L) * 86400));
      var started = Instant.parse("2032-01-10T02:00:00Z").plusSeconds((index - 1L) * 86400);
      var ended = started.plusSeconds(3);
      var drift = new AtomicReference<String>("");
      var retained = new AtomicReference<Connection>();
      mdb2292Subject(drift, retained)
          .execute(
              credential(),
              session -> {
                var begins = session.beginBackup(run, started, false);
                var failed =
                    new BatchStepResult(
                        BatchStepResult.Status.FAILED,
                        1,
                        0,
                        1,
                        0,
                        BatchStepResult.Reason.COMMAND_FAILURE);
                session.failBackup(begins, ended, failed, failed);
                drift.set(fault);
                try {
                  assertThrows(
                      IOException.class,
                      () ->
                          session.observeBackup(
                              begins, Optional.empty(), ended, () -> 10_000_000_000L));
                } finally {
                  drift.set("");
                }
                var observed =
                    session.observeBackup(begins, Optional.empty(), ended, () -> 10_000_000_000L);
                assertTrue(observed.prior().isEmpty());
                assertEquals(2, observed.current().size());
                for (var row : observed.current()) {
                  assertEquals(ended, row.ended());
                  assertEquals(failed, row.result());
                  assertEquals(Optional.of("COMMAND_FAILURE"), row.errorCode());
                  assertEquals(Optional.of("batch command failed"), row.errorSummary());
                }
                mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(ended));
                return Boolean.TRUE;
              });
      assertTrue(retained.get().isClosed());
      mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(ended));
      mdb2292NoOwnerResources();
    }
  }

  /** PT-MDB2402-002: no terminal observation before completion or while a handoff is active. */
  @Test
  void mdb2402002ObservationRejectsUnfinishedAndActiveHandoff() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("24020002-2222-4333-8444-555555555555"),
            Instant.parse("2032-02-09T15:00:00Z"));
    var started = Instant.parse("2032-02-10T02:00:00Z");
    var ended = started.plusSeconds(3);
    var retained = new AtomicReference<Connection>();
    mdb2292Subject(new AtomicReference<>(""), retained)
        .execute(
            credential(),
            session -> {
              var begins = session.beginBackup(run, started, false);
              assertThrows(
                  IOException.class,
                  () ->
                      session.observeBackup(
                          begins, Optional.empty(), ended, () -> 10_000_000_000L));
              mdb2292Rows(run, FIXTURE_RUNNING_294BDBF9, started, Optional.empty());
              var failed =
                  new BatchStepResult(
                      BatchStepResult.Status.FAILED,
                      1,
                      0,
                      1,
                      0,
                      BatchStepResult.Reason.COMMAND_FAILURE);
              session.failBackup(begins, ended, failed, failed);
              assertEquals(
                  30,
                  session.handoffCleanup(
                      () -> {
                        assertThrows(
                            IOException.class,
                            () ->
                                session.observeBackup(
                                    begins, Optional.empty(), ended, () -> 10_000_000_000L));
                        mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(ended));
                        return 30;
                      }));
              mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(ended));
              return Boolean.TRUE;
            });
    assertTrue(retained.get().isClosed());
    mdb2292Rows(run, FIXTURE_FAILED_7E8A57FE, started, Optional.of(ended));
    mdb2292NoOwnerResources();
  }

  private static MorningDatabaseSession mdb2292Subject(
      AtomicReference<String> drift, AtomicReference<Connection> retained) {
    return new MorningDatabaseSession(
        actualUrl,
        () -> {},
        (url, properties) -> {
          var actual = DriverManager.getConnection(url, properties);
          retained.set(actual);
          assertTrue(actual.getAutoCommit());
          assertFalse(actual.isReadOnly());
          assertEquals(Connection.TRANSACTION_READ_COMMITTED, actual.getTransactionIsolation());
          try (var check = actual.createStatement();
              var values =
                  check.executeQuery(
                      "select session_user,current_user,current_database(),pg_is_in_recovery()")) {
            assertTrue(values.next());
            assertEquals("schubert_batch", values.getString(1));
            assertEquals("schubert_batch", values.getString(2));
            assertEquals("schubert_nk", values.getString(3));
            assertFalse(values.getBoolean(4));
            assertFalse(values.next());
          }
          System.err.println("PT-MDB2292 phase=RAW_CONNECTION_PRECONDITIONS_OK");
          return (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (proxy, method, arguments) -> {
                    String name = method.getName();
                    if (drift.get().equals("AUTO") && name.equals(FIXTURE_GETAUTOCOMMIT_C0200BDE))
                      return false;
                    if (drift.get().equals("READONLY") && name.equals("isReadOnly")) return true;
                    if (drift.get().equals("ISOLATION")
                        && name.equals(FIXTURE_GETTRANSACTIONISOLATION_6ED78CE6))
                      return Connection.TRANSACTION_SERIALIZABLE;
                    Object result = mdb2292Invoke(method, actual, arguments);
                    if (drift.get().equals("HELD")
                        && name.equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
                        && ((String) arguments[0]).contains("pg_locks")) {
                      var statement = (PreparedStatement) result;
                      return Proxy.newProxyInstance(
                          PreparedStatement.class.getClassLoader(),
                          new Class<?>[] {PreparedStatement.class},
                          (ignored, called, inputs) -> {
                            Object returned = mdb2292Invoke(called, statement, inputs);
                            if (!called.getName().equals(FIXTURE_EXECUTEQUERY_85C8C423))
                              return returned;
                            var rows = (ResultSet) returned;
                            return Proxy.newProxyInstance(
                                ResultSet.class.getClassLoader(),
                                new Class<?>[] {ResultSet.class},
                                (unused, read, values) -> {
                                  if (read.getName().equals(FIXTURE_GETOBJECT_B6112877)
                                      || read.getName().equals("getBoolean")) return false;
                                  return mdb2292Invoke(read, rows, values);
                                });
                          });
                    }
                    return result;
                  });
        },
        connection -> {});
  }

  private static Object mdb2292Invoke(Method method, Object target, Object[] arguments)
      throws Throwable {
    try {
      return method.invoke(target, arguments);
    } catch (InvocationTargetException failure) {
      if (failure.getCause() instanceof SQLException sql)
        System.err.println(
            "PT-MDB2292_SQL method=" + method.getName() + " state=" + mdb2292State(sql));
      throw failure.getCause();
    }
  }

  private static void mdb2292Rows(
      BatchRun run, String status, Instant started, Optional<Instant> ended) throws IOException {
    try (var observer = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var statement =
            observer.prepareStatement(
                FIXTURE_SELECT_8DAC6259
                    + " step,status,attempt,started_at,ended_at,target_count,success_count,failure_count,byte_count"
                    + " from schubert.batch_runs where run_id=? order by step")) {
      statement.setObject(1, run.id());
      try (var rows = statement.executeQuery()) {
        for (String step : List.of(FIXTURE_BACKUP_CONFIG_8386D7E7, FIXTURE_BACKUP_DB_6C03A087)) {
          assertTrue(rows.next());
          assertEquals(step, rows.getString("step"));
          assertEquals(status, rows.getString(FIXTURE_STATUS_CFC31BCC));
          assertEquals(1, rows.getInt("attempt"));
          assertEquals(started, rows.getTimestamp(FIXTURE_STARTED_AT_D1210657).toInstant());
          assertEquals(
              ended,
              Optional.ofNullable(rows.getTimestamp(FIXTURE_ENDED_AT_E151E393))
                  .map(Timestamp::toInstant));
          assertEquals(
              status.equals(FIXTURE_FAILED_7E8A57FE) ? 1 : 0,
              rows.getLong(FIXTURE_TARGET_COUNT_5B6567D4));
          assertEquals(0, rows.getLong(FIXTURE_SUCCESS_COUNT_716E5185));
          assertEquals(
              status.equals(FIXTURE_FAILED_7E8A57FE) ? 1 : 0,
              rows.getLong(FIXTURE_FAILURE_COUNT_C7E67F21));
          assertEquals(0, rows.getLong(FIXTURE_BYTE_COUNT_6D76E237));
        }
        assertFalse(rows.next());
      }
    } catch (SQLException failure) {
      System.err.println("PT-MDB2292_SQL method=independentRows state=" + mdb2292State(failure));
      throw new IOException("independent isolated SQL postcondition unavailable", failure);
    }
  }

  private static String mdb2292State(SQLException failure) {
    String state = failure.getSQLState();
    return state != null && state.matches("[0-9A-Z]{5}") ? state : "UNKNOWN";
  }

  private static void mdb2292NoOwnerResources() throws SQLException {
    try (var observer = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var statement = observer.createStatement();
        var rows =
            statement.executeQuery(
                "select (select count(*) from pg_stat_activity where datname=current_database() and"
                    + " application_name='schubert-nk-morning-controller'),(select count(*) from"
                    + " pg_locks where locktype='advisory' and classid=0 and objid=71419602 and"
                    + " granted)")) {
      assertTrue(rows.next());
      assertEquals(0, rows.getLong(1));
      assertEquals(0, rows.getLong(2));
      assertFalse(rows.next());
    }
  }

  @Test
  void mdb019VerificationOnlySchemaCannotMintPermitFactsAndDataCannotEscapeOwner()
      throws Exception {
    MorningDatabaseSession.Schema legacy =
        connection -> fail("inspection must not use a void gate");
    try (var connection = db.open("schubert_batch")) {
      assertThrows(IOException.class, () -> legacy.inspect(connection));
      assertThrows(NullPointerException.class, () -> legacy.inspect(null));
    }
    var probe = new Probe();
    var retained = new AtomicReference<MorningDatabaseSession.Access>();
    probe
        .subject()
        .execute(
            credential(),
            session -> {
              retained.set(session);
              assertThrows(NullPointerException.class, () -> session.inspectPermitDatabase(null));
              assertThrows(
                  IOException.class, () -> session.inspectPermitDatabase(() -> 5_000_000_000L));
              assertThrows(
                  NullPointerException.class,
                  () -> session.recheckPermitDatabase(null, () -> 5_000_000_000L));
              return true;
            });
    assertThrows(
        IOException.class, () -> retained.get().inspectPermitDatabase(() -> 5_000_000_000L));
    var failure = new NullPointerException("PUBLIC_PROGRAMMING");
    var fresh = new Probe();
    assertSame(
        failure,
        assertThrows(
            NullPointerException.class,
            () ->
                fresh
                    .subject()
                    .execute(
                        credential(),
                        session ->
                            session.inspectPermitDatabase(
                                () -> {
                                  throw failure;
                                }))));
    assertEquals(0, fresh.connections);
    assertEquals(0, fresh.statements);
  }

  @BeforeAll
  static void database() throws Exception {
    db = new BatchDatabaseFixture(directory);
    try (var c = db.admin();
        var s = c.createStatement()) {
      actualUrl = c.getMetaData().getURL().replace("/postgres", "/schubert_nk");
      s.execute("create database schubert_nk");
    }
    try (var c = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var s = c.createStatement()) {
      s.execute(
          java.nio.file.Files.readString(
              Path.of(System.getProperty("nk.pt.repository"))
                  .resolve(
                      "src/schubert-nk-api/src/main/resources/db/provisioning/001_roles.sql")));
    }
    Flyway.configure()
        .dataSource(actualUrl, "schubert_migration", "")
        .defaultSchema("schubert_meta")
        .schemas("schubert_meta")
        .createSchemas(true)
        .initSql("SET ROLE nk_owner")
        .locations(
            "filesystem:"
                + Path.of(System.getProperty("nk.pt.repository"))
                    .resolve("src/schubert-nk-api/src/main/resources/db/migration"))
        .validateOnMigrate(true)
        .cleanDisabled(true)
        .load()
        .migrate();
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  static InspectorDbCredential credential() {
    return InspectorDbCredential.consume(
        "PUBLIC_PASSWORD".getBytes(java.nio.charset.StandardCharsets.US_ASCII));
  }

  /** MDB707001: absent/failed retained rows must not acquire a reusable Backup claim. */
  @Test
  void mdb707001FailedAndMissingRetentionRowsStayIneligibleWithIndependentSqlPostcondition()
      throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("70700000-2222-4333-8444-555555555555"),
            Instant.parse("2026-12-01T15:00:00Z"));
    var started = Instant.parse("2026-12-02T02:00:00Z");
    var ended = started.plusSeconds(3);
    var failed =
        new BatchStepResult(
            BatchStepResult.Status.FAILED, 1, 0, 1, 0, BatchStepResult.Reason.COMMAND_FAILURE);
    var subject =
        new MorningDatabaseSession(
            actualUrl, () -> {}, DriverManager::getConnection, connection -> {});
    subject.execute(
        credential(),
        session -> {
          var begins = session.beginBackup(run, started, false);
          session.failBackup(begins, ended, failed, failed);
          var manifest =
              new BackupManifest(
                  begins.database(),
                  begins.configuration(),
                  started,
                  started.plusSeconds(2),
                  new BackupVersions(
                      "public-host",
                      "1.0",
                      "023",
                      "ubuntu-26.04",
                      "25.0.4",
                      "18.6",
                      "2.56.0",
                      "1.2.1"),
                  "0".repeat(64),
                  new BackupFileDigest(26, "1".repeat(64)),
                  new BackupFileDigest(35, "2".repeat(64)),
                  new BackupFileDigest(32, "3".repeat(64)));
          assertThrows(
              IOException.class, () -> session.retainedBackupSuccessful(manifest, started));
          assertThrows(
              NullPointerException.class, () -> session.retainedBackupSuccessful(manifest, null));
          try (var observer =
                  DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
              var sql = observer.createStatement()) {
            // This is the isolated host fixture only. No VM/current database is changed.
            for (int expectedRows : new int[] {2, 1, 0}) {
              assertFalse(session.retainedBackupSuccessful(manifest, ended.plusSeconds(1)));
              try (var rows =
                  sql.executeQuery(
                      "select count(*),coalesce(string_agg(status,',' order by step),'') from"
                          + " schubert.batch_runs where"
                          + " run_id='70700000-2222-4333-8444-555555555555'")) {
                assertTrue(rows.next());
                assertEquals(expectedRows, rows.getInt(1));
                assertEquals(
                    expectedRows == 2
                        ? "FAILED,FAILED"
                        : expectedRows == 1 ? FIXTURE_FAILED_7E8A57FE : "",
                    rows.getString(2));
                assertFalse(rows.next());
              }
              if (expectedRows > 0)
                assertEquals(
                    1,
                    sql.executeUpdate(
                        "delete from schubert.batch_runs where id=(select min(id) from"
                            + " schubert.batch_runs where"
                            + " run_id='70700000-2222-4333-8444-555555555555')"));
            }
          } catch (SQLException failure) {
            throw new IOException("isolated retention fixture", failure);
          }
          return true;
        });
  }

  private static String mdb588Audit(Connection observer, BatchRun run) throws SQLException {
    try (var query = observer.createStatement();
        var role =
            query.executeQuery("select current_database(),session_user::text,current_user::text")) {
      assertTrue(role.next());
      assertEquals("schubert_nk", role.getString(1));
      assertEquals(FIXTURE_PGPT_ADMIN_F5D1227C, role.getString(2));
      assertEquals(FIXTURE_PGPT_ADMIN_F5D1227C, role.getString(3));
      assertFalse(role.next());
    }
    try (var statement =
        observer.prepareStatement(
            "select coalesce(jsonb_agg(to_jsonb(t) order by id),'[]'::jsonb)::text from"
                + " schubert.batch_runs t where run_id=?")) {
      statement.setObject(1, run.id());
      try (var rows = statement.executeQuery()) {
        assertTrue(rows.next());
        String value = rows.getString(1);
        assertNotNull(value);
        assertFalse(rows.next());
        return value;
      }
    }
  }

  @Test
  void mdb590001FailedBackupCleanupSkipAndExpiryTerminalReceiptsMatchIndependentSql()
      throws Exception {
    mdb590Scenarios(0, "", "");
  }

  @Test
  void mdb592001SixReadbackTransitionsRejectEverySqlPortFailureAndPreserveRows() throws Exception {
    int seed = 1;
    for (String phase :
        List.of(
            "failedBackupSnapshot",
            "observeBackup",
            "observeCleanup",
            "cleanupReferences",
            "beginExpiry",
            "observeExpiry")) {
      for (String method :
          List.of(
              FIXTURE_GETAUTOCOMMIT_C0200BDE,
              "isReadOnly",
              FIXTURE_PREPARESTATEMENT_CB987D1F,
              "rollback")) {
        mdb590Scenarios(seed++, phase, method);
      }
    }
    assertEquals(25, seed);
  }

  private void mdb590Scenarios(int seed, String faultPhase, String faultMethod) throws Exception {
    mdb590Scenarios(seed, faultPhase, faultMethod, false);
  }

  @Test
  void mdb594001ActualAutocommitAndReadonlyDriftRefusesSixTransitionsBeforeMutation()
      throws Exception {
    int seed = 25;
    for (String phase :
        List.of(
            "failedBackupSnapshot",
            "observeBackup",
            "observeCleanup",
            "cleanupReferences",
            "beginExpiry",
            "observeExpiry")) {
      for (String method : List.of(FIXTURE_GETAUTOCOMMIT_C0200BDE, "isReadOnly")) {
        mdb590Scenarios(seed++, phase, method, true);
      }
    }
    assertEquals(37, seed);
  }

  private void mdb590Scenarios(int seed, String faultPhase, String faultMethod, boolean drift)
      throws Exception {
    mdb590Scenarios(seed, faultPhase, faultMethod, drift, -1);
  }

  @Test
  void mdb595001RetainedExpiryUsesExactOriginalAnchorAndRejectsWrongMissingNullLookup()
      throws Exception {
    for (int mode = 0; mode < 5; mode++) mdb590Scenarios(37 + mode, "", "", false, mode);
  }

  private void mdb590Scenarios(
      int seed, String faultPhase, String faultMethod, boolean drift, int priorMode)
      throws Exception {
    var zero = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.receipt(0);
    var ten = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.receipt(10);
    var thirty = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.receipt(30);
    var cleanupReceipt =
        dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.cleanupReceipt(0);
    var receipts = List.of(zero, ten, thirty);
    var names =
        List.of(
            "CLEAN_NOTIFICATION",
            "CLEAN_QUESTION",
            "CLEAN_SESSION",
            "CLEAN_INBOX_OUTBOX",
            "CLEAN_LOG",
            "CLEAN_BATCH_RUN",
            "CLEAN_TRANSFER");
    for (int index = 0; index < (priorMode >= 0 ? 1 : seed == 0 ? 6 : 3); index++) {
      int scenario = seed * 6 + index;
      int terminal = index % 3;
      boolean matchingReceipt = index < 3;
      var fixtureDate =
          seed == 0
              ? java.time.LocalDate.of(2026, 9, 20).plusDays(index)
              : java.time.LocalDate.of(2010, 1, 1).plusDays(scenario);
      Instant began = fixtureDate.atStartOfDay(java.time.ZoneOffset.UTC).toInstant();
      var run = new BatchRun(new UUID(590001, scenario + 1), began.minusSeconds(32400));
      var priorRun = new BatchRun(new UUID(595001, scenario + 1), run.cutoff().plusSeconds(1));
      var priorBefore = new AtomicReference<String>();
      var originalCalls = new AtomicInteger();
      var retained = new AtomicReference<Connection>();
      var readBefore = new AtomicReference<String>();
      var phase = new AtomicReference<>("");
      var lastSqlState = new AtomicReference<>("");
      var injected = new AtomicBoolean();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var actual = DriverManager.getConnection(url, properties);
                retained.set(actual);
                if (!faultPhase.isEmpty()) {
                  return (Connection)
                      Proxy.newProxyInstance(
                          Connection.class.getClassLoader(),
                          new Class<?>[] {Connection.class},
                          (proxy, method, args) -> {
                            if (phase.get().equals(faultPhase)
                                && method.getName().equals(faultMethod)
                                && injected.compareAndSet(false, true)) {
                              try (var audit =
                                  DriverManager.getConnection(
                                      actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "")) {
                                readBefore.set(mdb588Audit(audit, run));
                              }
                              if (!drift) throw new SQLException("PRIVATE_TRANSITION_SQL_FAULT");
                              if (faultMethod.equals(FIXTURE_GETAUTOCOMMIT_C0200BDE))
                                actual.setAutoCommit(false);
                              else actual.setReadOnly(true);
                            }
                            try {
                              return method.invoke(actual, args);
                            } catch (InvocationTargetException failure) {
                              if (failure.getCause() instanceof SQLException sql)
                                lastSqlState.set(sql.getSQLState());
                              throw failure.getCause();
                            }
                          });
                }
                return actual;
              },
              c -> {});
      dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner = () -> 5_000_000_000L;
      try (var observer = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "")) {
        MorningDatabaseSession.Operation<Boolean> operation =
            session -> {
              assertThrows(IOException.class, () -> session.beginExpiry(run, began, owner));
              assertThrows(IOException.class, () -> session.handoffExpiry(() -> 0));
              var backup = session.beginBackup(run, began, false);
              confirmActualFailedPair(session, backup);
              phase.set("failedBackupSnapshot");
              var failedSnapshot = session.failedBackupSnapshot(backup, owner);
              assertEquals(began.plusSeconds(1), failedSnapshot.endedAt());
              phase.set("observeBackup");
              var backupRows =
                  session.observeBackup(backup, Optional.empty(), began.plusSeconds(1), owner);
              assertEquals(2, backupRows.current().size());
              for (var row : backupRows.current()) {
                assertEquals(BatchStepResult.Status.FAILED, row.result().status());
                assertEquals(BatchStepResult.Reason.COMMAND_FAILURE, row.result().reason());
                assertEquals(began.plusSeconds(1), row.ended());
              }
              phase.set("");
              assertEquals(
                  0,
                  session.handoffCleanup(
                      () -> {
                        try (var child =
                                DriverManager.getConnection(actualUrl, "schubert_batch", "");
                            var sql =
                                child.prepareStatement(
                                    "insert into"
                                        + " schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary)"
                                        + " values(?,?,?,?,1,?,?,?,0,0,0,0,?,?)")) {
                          assertTrue(advisory(child));
                          child.setAutoCommit(false);
                          for (int step = 0; step < names.size(); step++) {
                            boolean transfer = step == 6;
                            sql.setLong(1, 590000000L + scenario * 100 + step);
                            sql.setObject(2, run.id());
                            sql.setObject(3, fixtureDate);
                            sql.setString(4, names.get(step));
                            sql.setObject(
                                5, began.plusSeconds(2).atOffset(java.time.ZoneOffset.UTC));
                            sql.setObject(
                                6,
                                began
                                    .plusSeconds(transfer ? 3 : 2)
                                    .atOffset(java.time.ZoneOffset.UTC));
                            sql.setString(7, transfer ? FIXTURE_SUCCESS_10855C7F : "SKIPPED");
                            sql.setString(8, transfer ? null : "BACKUP_UNAVAILABLE");
                            sql.setString(9, transfer ? null : "verified backup unavailable");
                            assertEquals(1, sql.executeUpdate());
                          }
                          child.commit();
                          releaseAdvisory(child);
                        } catch (SQLException failure) {
                          throw new IOException("fixture cleanup", failure);
                        }
                        return 0;
                      }));
              phase.set("observeCleanup");
              var cleanup = session.observeCleanupBackupUnavailable(run, 0, owner);
              assertEquals(7, cleanup.entries().size());
              for (int step = 0; step < 7; step++) {
                var entry = cleanup.entries().get(step);
                assertEquals(names.get(step), entry.attempt().step().name());
                assertEquals(590000000L + scenario * 100 + step, entry.attempt().id());
                assertEquals(step < 6, entry.attempt().skipped());
                assertEquals(
                    step < 6 ? BatchStepResult.Status.SKIPPED : BatchStepResult.Status.SUCCESS,
                    entry.result().status());
                assertEquals(
                    step < 6
                        ? BatchStepResult.Reason.BACKUP_UNAVAILABLE
                        : BatchStepResult.Reason.NONE,
                    entry.result().reason());
                assertEquals(began.plusSeconds(step < 6 ? 2 : 3), entry.endedAt());
                assertEquals(0, entry.result().target());
                assertEquals(0, entry.result().success());
                assertEquals(0, entry.result().failure());
                assertEquals(0, entry.result().bytes());
              }
              phase.set("cleanupReferences");
              assertEquals(
                  Collections.nCopies(7, Optional.empty()),
                  session.cleanupReferences(cleanup, owner));
              phase.set("");
              assertThrows(NullPointerException.class, () -> session.beginExpiry(run, null, owner));
              assertThrows(NullPointerException.class, () -> session.beginExpiry(run, began, null));
              if (priorMode >= 0) {
                phase.set("priorInsert");
                long priorId = 595000000L + scenario;
                try (var sql =
                    observer.prepareStatement(
                        "insert into"
                            + " schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary,expiry_cutoff_at,expiry_before_count,expiry_after_count)"
                            + " values(?,?,?,'CLEAN_EXPIRY',1,?,?,'SUCCESS',1,1,0,17,null,null,?,2,1)")) {
                  sql.setLong(1, priorId);
                  sql.setObject(2, priorRun.id());
                  sql.setObject(3, fixtureDate);
                  sql.setObject(4, began.minusSeconds(10).atOffset(java.time.ZoneOffset.UTC));
                  sql.setObject(5, began.minusSeconds(9).atOffset(java.time.ZoneOffset.UTC));
                  sql.setObject(
                      6, priorRun.cutoff().minusSeconds(604800).atOffset(java.time.ZoneOffset.UTC));
                  assertEquals(1, sql.executeUpdate());
                  priorBefore.set(mdb588Audit(observer, priorRun));
                  readBefore.set(mdb588Audit(observer, run));
                } catch (SQLException failure) {
                  lastSqlState.set(String.valueOf(failure.getSQLState()));
                  throw new IOException("fixture retained expiry", failure);
                }
                phase.set("priorBegin");
                var reused =
                    session.beginExpiry(
                        run,
                        began.plusSeconds(4),
                        owner,
                        (id, at) -> {
                          originalCalls.incrementAndGet();
                          assertEquals(priorRun.id(), id);
                          assertEquals(began.plusSeconds(4), at);
                          if (priorMode == 1)
                            return new BatchRun(
                                priorRun.id(), priorRun.cutoff().plusSeconds(86400));
                          if (priorMode == 2) throw new IOException("PUBLIC_ORIGINAL_REFUSAL");
                          if (priorMode == 3) return null;
                          return priorRun;
                        });
                assertTrue(reused.current().skipped());
                assertEquals(2, reused.current().attempt());
                assertEquals(run, reused.current().run());
                assertEquals(began.plusSeconds(4), reused.current().startedAt());
                var literalHandle =
                    new BatchStepAttempt(
                        priorId,
                        priorRun,
                        BatchStep.CLEAN_EXPIRY,
                        1,
                        began.minusSeconds(10),
                        false);
                var literalAudit =
                    new ExpiryAuditRepository.Snapshot(
                        FIXTURE_SUCCESS_10855C7F,
                        priorRun.cutoff().minusSeconds(604800),
                        2L,
                        1L,
                        1,
                        1,
                        0,
                        17,
                        began.minusSeconds(9),
                        null,
                        null);
                assertEquals(
                    Optional.of(new ExpiryAuditRepository.Prior(literalHandle, literalAudit)),
                    reused.prior());
                phase.set("priorHandoff");
                assertEquals(
                    0,
                    session.handoffExpiry(
                        () -> {
                          try (var child =
                              DriverManager.getConnection(actualUrl, "schubert_batch", "")) {
                            assertTrue(advisory(child));
                            releaseAdvisory(child);
                          } catch (SQLException failure) {
                            throw new IOException("fixture retained handoff", failure);
                          }
                          return 0;
                        }));
                try {
                  readBefore.set(mdb588Audit(observer, run));
                } catch (SQLException failure) {
                  throw new IOException("fixture retained current audit", failure);
                }
                phase.set("priorObserve");
                var observed = session.observeExpiry(reused, priorMode == 4 ? thirty : zero, owner);
                assertEquals(reused, observed.begins());
                assertEquals(began.plusSeconds(4), observed.ended());
                assertEquals(
                    new BatchStepResult(
                        BatchStepResult.Status.SKIPPED,
                        0,
                        0,
                        0,
                        0,
                        BatchStepResult.Reason.ALREADY_SUCCESSFUL),
                    observed.result());
                assertEquals(literalAudit, observed.audit());
                return Boolean.TRUE;
              }
              phase.set("beginExpiry");
              var expiry = session.beginExpiry(run, began.plusSeconds(4), owner);
              phase.set("");
              assertFalse(expiry.current().skipped());
              assertEquals(Optional.empty(), expiry.prior());
              assertThrows(
                  IOException.class,
                  () -> session.observeExpiry(expiry, receipts.get(terminal), owner));
              assertEquals(
                  receipts.get(terminal).exitCode(),
                  session.handoffExpiry(
                      () -> {
                        try (var child =
                                DriverManager.getConnection(actualUrl, "schubert_batch", "");
                            var sql =
                                child.prepareStatement(
                                    "update schubert.batch_runs set"
                                        + " status=?,ended_at=?,target_count=1,success_count=?,failure_count=?,byte_count=25,error_code=?,error_summary=?,expiry_cutoff_at=?,expiry_before_count=1,expiry_after_count=?"
                                        + " where id=? and run_id=? and step='CLEAN_EXPIRY' and"
                                        + " status='RUNNING'")) {
                          assertTrue(advisory(child));
                          sql.setString(
                              1,
                              List.of(FIXTURE_SUCCESS_10855C7F, "WARNING", FIXTURE_FAILED_7E8A57FE)
                                  .get(terminal));
                          sql.setObject(2, began.plusSeconds(5).atOffset(java.time.ZoneOffset.UTC));
                          sql.setLong(3, terminal == 0 ? 1 : 0);
                          sql.setLong(4, terminal == 0 ? 0 : 1);
                          sql.setString(
                              5,
                              terminal == 0
                                  ? null
                                  : terminal == 1 ? "COMMAND_FAILURE" : "SAFETY_FAILURE");
                          sql.setString(
                              6,
                              terminal == 0
                                  ? null
                                  : terminal == 1
                                      ? "batch command failed"
                                      : "batch safety check failed");
                          sql.setObject(
                              7,
                              run.cutoff().minusSeconds(604800).atOffset(java.time.ZoneOffset.UTC));
                          sql.setLong(8, terminal == 0 ? 0 : 1);
                          sql.setLong(9, expiry.current().id());
                          sql.setObject(10, run.id());
                          assertEquals(1, sql.executeUpdate());
                          releaseAdvisory(child);
                        } catch (SQLException failure) {
                          throw new IOException("fixture expiry", failure);
                        }
                        return receipts.get(terminal).exitCode();
                      }));
              try {
                readBefore.set(mdb588Audit(observer, run));
              } catch (SQLException failure) {
                throw new IOException("fixture audit", failure);
              }
              assertThrows(
                  IOException.class, () -> session.observeExpiry(expiry, cleanupReceipt, owner));
              phase.set("observeExpiry");
              var actual =
                  session.observeExpiry(
                      expiry,
                      matchingReceipt ? receipts.get(terminal) : terminal == 0 ? thirty : zero,
                      owner);
              assertEquals(expiry, actual.begins());
              assertEquals(began.plusSeconds(5), actual.ended());
              assertEquals(
                  List.of(
                          BatchStepResult.Status.SUCCESS,
                          BatchStepResult.Status.WARNING,
                          BatchStepResult.Status.FAILED)
                      .get(terminal),
                  actual.result().status());
              assertEquals(1, actual.result().target());
              assertEquals(terminal == 0 ? 1 : 0, actual.result().success());
              assertEquals(terminal == 0 ? 0 : 1, actual.result().failure());
              assertEquals(25, actual.result().bytes());
              assertEquals(run.cutoff().minusSeconds(604800), actual.audit().cutoff());
              assertEquals(Long.valueOf(1), actual.audit().before());
              assertEquals(Long.valueOf(terminal == 0 ? 0 : 1), actual.audit().after());
              return Boolean.TRUE;
            };
        if ((seed == 0 && index < 3) || priorMode == 0) {
          try {
            assertEquals(Boolean.TRUE, subject.execute(credential(), operation));
          } catch (IOException failure) {
            throw new AssertionError(
                "fixture phase="
                    + phase.get()
                    + " scenario="
                    + scenario
                    + " sqlstate="
                    + lastSqlState.get(),
                failure);
          }
        } else if (priorMode == 3) {
          assertThrows(NullPointerException.class, () -> subject.execute(credential(), operation));
        } else
          assertEquals(
              FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891,
              assertThrows(IOException.class, () -> subject.execute(credential(), operation))
                  .getMessage());
        if (seed != 0 && priorMode < 0)
          assertTrue(
              injected.get(),
              faultPhase
                  + ":"
                  + faultMethod
                  + " actualPhase="
                  + phase.get()
                  + " scenario="
                  + scenario
                  + " sqlstate="
                  + lastSqlState.get());
        assertEquals(readBefore.get(), mdb588Audit(observer, run));
        if (priorMode >= 0) {
          assertEquals(1, originalCalls.get());
          assertEquals(priorBefore.get(), mdb588Audit(observer, priorRun));
        }
        assertTrue(retained.get().isClosed());
        awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
      }
    }
  }

  @Test
  void mdb589001ActualReadbackSqlFailuresCloseConnectionWithoutChangingCommittedRows()
      throws Exception {
    var receipt = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.cleanupReceipt(30);
    var points =
        List.of(
            FIXTURE_GETAUTOCOMMIT_C0200BDE,
            "isReadOnly",
            "setAutoCommitFalse",
            FIXTURE_PREPARESTATEMENT_CB987D1F,
            "rollback",
            "setAutoCommitTrue",
            "ownerBind");
    for (int index = 0; index < points.size(); index++) {
      String point = points.get(index);
      Instant began = Instant.parse("2026-09-10T00:00:00Z").plusSeconds(index * 86400L);
      var run = new BatchRun(new UUID(589001, index + 1), began.minusSeconds(32400));
      var enabled = new AtomicBoolean();
      var injected = new AtomicInteger();
      var retained = new AtomicReference<Connection>();
      var ownerChecks = new AtomicInteger();
      var before = new AtomicReference<String>();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, properties) -> {
                var actual = DriverManager.getConnection(url, properties);
                retained.set(actual);
                return (Connection)
                    Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (proxy, method, args) -> {
                          String name = method.getName();
                          boolean hit =
                              name.equals(point)
                                  || (name.equals("setAutoCommit")
                                      && point.equals(
                                          "setAutoCommit"
                                              + ((boolean) args[0] ? "True" : "False")));
                          if (enabled.get() && hit && injected.getAndIncrement() == 0)
                            throw new SQLException("PRIVATE_SQL_FAULT");
                          try {
                            return method.invoke(actual, args);
                          } catch (InvocationTargetException failure) {
                            throw failure.getCause();
                          }
                        });
              },
              c -> {});
      try (var observer = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "")) {
        var failure =
            assertThrows(
                IOException.class,
                () ->
                    subject.execute(
                        credential(),
                        session -> {
                          var pair = session.beginBackup(run, began, false);
                          confirmActualFailedPair(session, pair);
                          assertEquals(30, session.handoffCleanup(() -> 30));
                          try {
                            before.set(mdb588Audit(observer, run));
                          } catch (SQLException known) {
                            throw new IOException("fixture audit", known);
                          }
                          enabled.set(true);
                          session.observeCleanupRejected(
                              run,
                              receipt,
                              () -> {
                                if (point.equals("ownerBind")
                                    && ownerChecks.incrementAndGet() == 2) {
                                  injected.incrementAndGet();
                                  throw new IOException("PRIVATE_OWNER_FAULT");
                                }
                                return 5_000_000_000L;
                              });
                          fail("fault must reject readback");
                          return Boolean.TRUE;
                        }),
                point);
        assertEquals(FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, failure.getMessage(), point);
        assertNull(failure.getCause(), point);
        assertEquals(0, failure.getSuppressed().length, point);
        assertTrue(injected.get() >= 1, point);
        assertTrue(retained.get().isClosed(), point);
        assertEquals(before.get(), mdb588Audit(observer, run), point);
        awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
      }
    }
  }

  @Test
  void mdb589002ActualCloseFaultPriorityStillReleasesOwnedAdvisory() throws Exception {
    for (boolean bodyFailed : List.of(false, true)) {
      for (Throwable secondary :
          List.of(
              new SQLException("PRIVATE_CLOSE"),
              new IllegalStateException("PRIVATE_CLOSE"),
              new AssertionError("PRIVATE_CLOSE"))) {
        var retained = new AtomicReference<Connection>();
        var closeCount = new AtomicInteger();
        var subject =
            new MorningDatabaseSession(
                actualUrl,
                () -> {},
                (url, properties) -> {
                  var actual = DriverManager.getConnection(url, properties);
                  retained.set(actual);
                  return (Connection)
                      Proxy.newProxyInstance(
                          Connection.class.getClassLoader(),
                          new Class<?>[] {Connection.class},
                          (proxy, method, args) -> {
                            if (method.getName().equals(FIXTURE_CLOSE_97959247)) {
                              closeCount.incrementAndGet();
                              actual.close();
                              throw secondary;
                            }
                            try {
                              return method.invoke(actual, args);
                            } catch (InvocationTargetException failure) {
                              throw failure.getCause();
                            }
                          });
                },
                c -> {});
        Throwable actualFailure =
            assertThrows(
                Throwable.class,
                () ->
                    subject.execute(
                        credential(),
                        session -> {
                          session.requireUnused(
                              new BatchRun(
                                  new UUID(589002, 1), Instant.parse("2026-09-01T15:00:00Z")));
                          if (bodyFailed) throw new IOException("PRIVATE_BODY");
                          return Boolean.TRUE;
                        }));
        if (secondary instanceof SQLException) {
          assertInstanceOf(IOException.class, actualFailure);
          assertEquals(
              FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, actualFailure.getMessage());
          assertNull(actualFailure.getCause());
          assertEquals(0, actualFailure.getSuppressed().length);
        } else assertSame(secondary, actualFailure);
        assertEquals(1, closeCount.get());
        assertTrue(retained.get().isClosed());
        try (var observer =
            DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "")) {
          awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
        }
      }
    }
  }

  /** MDB588001..003 / P017-01.03 / OPS009,DAT009/UI251/SS341343/SSC199200. */
  @Test
  void mdb588001TypedCleanup30EmptyReadbackDoesNotFabricateRowsOrReleaseParent() throws Exception {
    var receipt = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.cleanupReceipt(30);
    var foreign = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.receipt(30);
    var normal = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.cleanupReceipt(0);
    var run =
        new BatchRun(
            UUID.fromString("58800000-2222-4333-8444-555555555551"),
            Instant.parse("2026-10-07T15:00:00Z"));
    Instant began = Instant.parse("2026-10-08T00:00:00Z");
    var connection = new AtomicReference<Connection>();
    var retained = new AtomicReference<MorningDatabaseSession.Access>();
    var subject =
        new MorningDatabaseSession(
            actualUrl,
            () -> {},
            (url, properties) -> {
              var value = DriverManager.getConnection(url, properties);
              connection.set(value);
              return value;
            },
            c -> {});
    try (var observer = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "")) {
      subject.execute(
          credential(),
          session -> {
            retained.set(session);
            dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner =
                () -> 5_000_000_000L;
            assertThrows(
                IOException.class, () -> session.observeCleanupRejected(run, receipt, owner));
            var pair = session.beginBackup(run, began, false);
            assertThrows(
                IOException.class, () -> session.observeCleanupRejected(run, receipt, owner));
            confirmActualFailedPair(session, pair);
            assertThrows(
                IOException.class, () -> session.observeCleanupRejected(run, receipt, owner));
            assertEquals(30, session.handoffCleanup(() -> 30));
            try {
              String before = mdb588Audit(observer, run);
              var actual = session.observeCleanupRejected(run, receipt, owner);
              assertEquals(run, actual.run());
              assertEquals(
                  List.of(
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty()),
                  actual.entries());
              assertEquals("CleanupRejectedSnapshot[data=<redacted>]", actual.toString());
              assertEquals(before, mdb588Audit(observer, run));
              assertNotNull(connection.get());
              assertTrue(connection.get().getAutoCommit());
              assertFalse(connection.get().isReadOnly());
              assertFalse(advisory(observer));
              assertThrows(
                  IOException.class, () -> session.observeCleanupRejected(run, foreign, owner));
              assertThrows(
                  IOException.class, () -> session.observeCleanupRejected(run, normal, owner));
              var failure = new IOException("PUBLIC_OWNER_DEADLINE");
              assertSame(
                  failure,
                  assertThrows(
                      IOException.class,
                      () ->
                          session.observeCleanupRejected(
                              run,
                              receipt,
                              () -> {
                                throw failure;
                              })));
              assertEquals(before, mdb588Audit(observer, run));
            } catch (SQLException failure) {
              throw new IOException("isolated DB assertion", failure);
            }
            return Boolean.TRUE;
          });
      awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
      assertTrue(connection.get().isClosed());
      assertThrows(
          IOException.class,
          () -> retained.get().observeCleanupRejected(run, receipt, () -> 5_000_000_000L));
    }
  }

  @Test
  void mdb588002Typed30PartialRunningAndFailedSlotsStayExactAndUnmodified() throws Exception {
    var receipt = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.cleanupReceipt(30);
    var run =
        new BatchRun(
            UUID.fromString("58800000-2222-4333-8444-555555555552"),
            Instant.parse("2026-10-06T15:00:00Z"));
    Instant began = Instant.parse("2026-10-07T00:00:10Z");
    var subject =
        new MorningDatabaseSession(actualUrl, () -> {}, DriverManager::getConnection, c -> {});
    try (var observer = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "")) {
      subject.execute(
          credential(),
          session -> {
            var pair = session.beginBackup(run, began, false);
            confirmActualFailedPair(session, pair);
            assertEquals(
                30,
                session.handoffCleanup(
                    () -> {
                      try (var child =
                              DriverManager.getConnection(actualUrl, "schubert_batch", "");
                          var statement =
                              child.prepareStatement(
                                  "insert into"
                                      + " schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary)"
                                      + " values"
                                      + " (588201,?,'2026-10-07','CLEAN_NOTIFICATION',1,'2026-10-07T00:00:11Z',null,'RUNNING',0,0,0,0,null,null),(588202,?,'2026-10-07','CLEAN_QUESTION',1,'2026-10-07T00:00:11Z','2026-10-07T00:00:12Z','FAILED',1,0,1,0,'COMMAND_FAILURE','batch"
                                      + " command failed')")) {
                        assertTrue(advisory(child));
                        statement.setObject(1, run.id());
                        statement.setObject(2, run.id());
                        assertEquals(2, statement.executeUpdate());
                        releaseAdvisory(child);
                      } catch (SQLException failure) {
                        throw new IOException("isolated partial fixture", failure);
                      }
                      return 30;
                    }));
            try {
              String before = mdb588Audit(observer, run);
              var actual = session.observeCleanupRejected(run, receipt, () -> 5_000_000_000L);
              var first =
                  new CleanupTerminalRepository.RejectedEntry(
                      new BatchStepAttempt(
                          588201,
                          run,
                          BatchStep.CLEAN_NOTIFICATION,
                          1,
                          began.plusSeconds(1),
                          false),
                      Optional.empty(),
                      Optional.empty());
              var second =
                  new CleanupTerminalRepository.RejectedEntry(
                      new BatchStepAttempt(
                          588202, run, BatchStep.CLEAN_QUESTION, 1, began.plusSeconds(1), false),
                      Optional.of(began.plusSeconds(2)),
                      Optional.of(
                          new BatchStepResult(
                              BatchStepResult.Status.FAILED,
                              1,
                              0,
                              1,
                              0,
                              BatchStepResult.Reason.COMMAND_FAILURE)));
              assertEquals(
                  List.of(
                      Optional.of(first),
                      Optional.of(second),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty()),
                  actual.entries());
              assertEquals(before, mdb588Audit(observer, run));
              assertFalse(advisory(observer));
            } catch (SQLException failure) {
              throw new IOException("isolated partial readback", failure);
            }
            return Boolean.TRUE;
          });
      awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
    }
  }

  @Test
  void mdb588003UnexpectedTransactionOrReadOnlyCannotEnterRejectedReadback() throws Exception {
    var receipt = dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture.cleanupReceipt(30);
    var run =
        new BatchRun(
            UUID.fromString("58800000-2222-4333-8444-555555555553"),
            Instant.parse("2026-10-05T15:00:00Z"));
    var retained = new AtomicReference<Connection>();
    var subject =
        new MorningDatabaseSession(
            actualUrl,
            () -> {},
            (url, properties) -> {
              var c = DriverManager.getConnection(url, properties);
              retained.set(c);
              return c;
            },
            c -> {});
    subject.execute(
        credential(),
        session -> {
          var pair = session.beginBackup(run, Instant.parse("2026-10-06T00:00:20Z"), false);
          confirmActualFailedPair(session, pair);
          assertEquals(30, session.handoffCleanup(() -> 30));
          dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner = () -> 5_000_000_000L;
          try {
            var c = retained.get();
            assertNotNull(c);
            c.setAutoCommit(false);
            assertThrows(
                IOException.class, () -> session.observeCleanupRejected(run, receipt, owner));
            assertFalse(c.getAutoCommit());
            c.rollback();
            c.setAutoCommit(true);
            c.setReadOnly(true);
            assertThrows(
                IOException.class, () -> session.observeCleanupRejected(run, receipt, owner));
            assertTrue(c.isReadOnly());
            c.setReadOnly(false);
            assertThrows(
                NullPointerException.class,
                () -> session.observeCleanupRejected(null, receipt, owner));
            assertThrows(
                NullPointerException.class, () -> session.observeCleanupRejected(run, null, owner));
            assertThrows(
                NullPointerException.class,
                () -> session.observeCleanupRejected(run, receipt, null));
          } catch (SQLException failure) {
            throw new IOException("isolated transaction fixture", failure);
          }
          return Boolean.TRUE;
        });
    assertTrue(retained.get().isClosed());
  }

  @Test
  void bresume001GenuinePriorPairAndCurrentSkipAreSeparateCommittedRows() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("38700000-2222-4333-8444-555555555555"),
            Instant.parse("2026-11-27T15:00:00Z"));
    var started = Instant.parse("2026-11-28T02:00:00Z");
    var observed = Instant.parse("2026-11-28T03:00:00Z");
    try (var admin = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var s = admin.createStatement()) {
      s.execute(
          "insert into"
              + " schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,byte_count)"
              + " values"
              + "(670001,'38700000-2222-4333-8444-555555555555','2026-11-28','BACKUP_DB',1,'2026-11-28T02:00:00Z','2026-11-28T02:00:03Z','SUCCESS',1,1,26),"
              + "(670002,'38700000-2222-4333-8444-555555555555','2026-11-28','BACKUP_CONFIG',1,'2026-11-28T02:00:00Z','2026-11-28T02:00:03Z','SUCCESS',2,2,67)");
    }
    var prior =
        new MorningDatabaseSession.BackupBegins(
            new BatchStepAttempt(670001, run, BatchStep.BACKUP_DB, 1, started, false),
            new BatchStepAttempt(670002, run, BatchStep.BACKUP_CONFIG, 1, started, false));
    var manifest =
        new BackupManifest(
            prior.database(),
            prior.configuration(),
            started,
            started.plusSeconds(2),
            new BackupVersions(
                "public-host", "1.0", "023", "ubuntu-26.04", "25.0.4", "18.6", "2.56.0", "1.2.1"),
            "0".repeat(64),
            new BackupFileDigest(26, "1".repeat(64)),
            new BackupFileDigest(35, "2".repeat(64)),
            new BackupFileDigest(32, "3".repeat(64)));
    var subject =
        new MorningDatabaseSession(
            actualUrl, () -> {}, DriverManager::getConnection, connection -> {});
    var current =
        subject.execute(
            credential(),
            session -> {
              assertEquals(Optional.of(prior), session.successfulBackup(run, observed));
              var skipped = session.beginResumeBackup(manifest, observed);
              assertTrue(skipped.database().skipped());
              assertTrue(skipped.configuration().skipped());
              assertNotEquals(prior.database().id(), skipped.database().id());
              assertEquals(2, skipped.database().attempt());
              assertEquals(2, skipped.configuration().attempt());
              assertThrows(
                  IOException.class, () -> session.completeReusedBackup(prior, manifest, observed));
              session.completeReusedBackup(skipped, manifest, observed.plusSeconds(1));
              var observedPair =
                  session.observeBackup(
                      skipped,
                      Optional.of(manifest),
                      observed.plusSeconds(1),
                      () -> 10_000_000_000L);
              assertEquals(
                  List.of(skipped.database(), skipped.configuration()),
                  observedPair.current().stream()
                      .map(BackupStepRepository.Terminal::attempt)
                      .toList());
              assertEquals(
                  List.of(prior.database(), prior.configuration()),
                  observedPair.prior().stream()
                      .map(BackupStepRepository.Terminal::attempt)
                      .toList());
              assertEquals(26, observedPair.prior().get(0).result().bytes());
              assertEquals(67, observedPair.prior().get(1).result().bytes());
              assertEquals(Optional.empty(), observedPair.prior().get(0).errorCode());
              assertThrows(
                  IOException.class,
                  () ->
                      session.observeBackup(
                          prior,
                          Optional.of(manifest),
                          observed.plusSeconds(1),
                          () -> 10_000_000_000L));
              assertTrue(session.retainedBackupSuccessful(manifest, observed.plusSeconds(1)));
              assertThrows(
                  NullPointerException.class,
                  () -> session.retainedBackupSuccessful(null, observed));
              assertThrows(
                  IOException.class, () -> session.retainedBackupSuccessful(manifest, started));
              session.recheckConsistent(run);
              assertThrows(
                  IOException.class,
                  () -> session.completeReusedBackup(skipped, manifest, observed.plusSeconds(1)));
              assertThrows(IOException.class, () -> session.successfulBackup(run, observed));
              return skipped;
            });
    try (var connection = DriverManager.getConnection(actualUrl, "schubert_batch", "")) {
      awaitAcquired(connection, TimeUnit.SECONDS.toNanos(5));
      connection.setAutoCommit(false);
      var repository = new BatchRunRepository(connection);
      repository.verifyAlreadySuccessful(current.database());
      repository.verifyAlreadySuccessful(current.configuration());
      assertEquals(
          Optional.of(started.plusSeconds(3)),
          new BackupStepRepository(connection).inspect(manifest, observed));
      try (var s = connection.createStatement();
          var rows =
              s.executeQuery(
                  FIXTURE_SELECT_8DAC6259
                      + " string_agg(step||':'||attempt||':'||status||':'||target_count||':'||success_count||':'||failure_count||':'||byte_count,','"
                      + " order by step,attempt) from schubert.batch_runs where"
                      + " run_id='38700000-2222-4333-8444-555555555555'")) {
        assertTrue(rows.next());
        assertEquals(
            "BACKUP_CONFIG:1:SUCCESS:2:2:0:67,BACKUP_CONFIG:2:SKIPPED:0:0:0:0,BACKUP_DB:1:SUCCESS:1:1:0:26,BACKUP_DB:2:SKIPPED:0:0:0:0",
            rows.getString(1));
        assertFalse(rows.next());
      }
      releaseAdvisory(connection);
    }
  }

  @Test
  void mdb015SameConnectionAtomicFailedPairAndReadbackWithoutMutation() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("37900000-2222-4333-8444-555555555555"),
            RUN.cutoff().plusSeconds(40L * 86400));
    Instant started = NOW.plusSeconds(40L * 86400);
    Instant ended = started.plusSeconds(2);
    var failed =
        new BatchStepResult(
            BatchStepResult.Status.FAILED, 1, 0, 1, 0, BatchStepResult.Reason.COMMAND_FAILURE);
    var success =
        new BatchStepResult(
            BatchStepResult.Status.SUCCESS, 1, 1, 0, 1, BatchStepResult.Reason.NONE);
    var subject =
        new MorningDatabaseSession(
            actualUrl, () -> {}, DriverManager::getConnection, connection -> {});
    var held = new AtomicReference<MorningDatabaseSession.Access>();
    var attempts = new AtomicReference<MorningDatabaseSession.BackupBegins>();
    subject.execute(
        credential(),
        session -> {
          held.set(session);
          var begins = session.beginBackup(run, started, false);
          attempts.set(begins);
          assertThrows(IOException.class, () -> session.failBackup(begins, ended, success, failed));
          assertThrows(IOException.class, () -> session.failBackup(begins, ended, failed, success));
          assertThrows(
              NullPointerException.class, () -> session.failBackup(null, ended, failed, failed));
          var wrong =
              new MorningDatabaseSession.BackupBegins(
                  new BatchStepAttempt(
                      begins.database().id() + 100, run, BatchStep.BACKUP_DB, 1, started, false),
                  begins.configuration());
          assertThrows(IOException.class, () -> session.failBackup(wrong, ended, failed, failed));
          session.failBackup(begins, ended, failed, failed);
          var pair = session.observeBackup(begins, Optional.empty(), ended, () -> 10_000_000_000L);
          assertTrue(pair.prior().isEmpty());
          assertEquals(2, pair.current().size());
          for (var row : pair.current()) {
            assertEquals(ended, row.ended());
            assertEquals(failed, row.result());
            assertEquals(Optional.of("COMMAND_FAILURE"), row.errorCode());
            assertEquals(Optional.of("batch command failed"), row.errorSummary());
          }
          assertThrows(
              IOException.class,
              () -> session.observeBackup(wrong, Optional.empty(), ended, () -> 10_000_000_000L));
          assertThrows(
              NullPointerException.class,
              () -> session.observeBackup(null, Optional.empty(), ended, () -> 10_000_000_000L));
          assertThrows(
              NullPointerException.class,
              () -> session.observeBackup(begins, null, ended, () -> 10_000_000_000L));
          assertThrows(
              NullPointerException.class,
              () -> session.observeBackup(begins, Optional.empty(), null, () -> 10_000_000_000L));
          assertThrows(
              NullPointerException.class,
              () -> session.observeBackup(begins, Optional.empty(), ended, null));
          assertThrows(IOException.class, () -> session.failBackup(begins, ended, failed, failed));
          var observed = session.failedBackupSnapshot(begins, () -> 10_000_000_000L);
          assertEquals(begins.database(), observed.database());
          assertEquals(begins.configuration(), observed.configuration());
          assertEquals(ended, observed.endedAt());
          assertThrows(
              IOException.class, () -> session.failedBackupSnapshot(wrong, () -> 10_000_000_000L));
          assertThrows(
              NullPointerException.class, () -> session.failedBackupSnapshot(null, () -> 1));
          assertThrows(
              NullPointerException.class, () -> session.failedBackupSnapshot(begins, null));
          return true;
        });
    assertThrows(
        IOException.class, () -> held.get().failBackup(attempts.get(), ended, failed, failed));
    assertThrows(
        IOException.class,
        () -> held.get().failedBackupSnapshot(attempts.get(), () -> 10_000_000_000L));
    try (var observer = DriverManager.getConnection(actualUrl, "schubert_batch", "")) {
      awaitAcquired(observer, TimeUnit.SECONDS.toNanos(5));
      observer.setAutoCommit(false);
      var repository = new BatchRunRepository(observer);
      repository.verifyFinished(attempts.get().database(), ended, failed);
      repository.verifyFinished(attempts.get().configuration(), ended, failed);
      assertThrows(
          BatchRepositoryException.class,
          () -> repository.verifyFinished(attempts.get().database(), ended.plusSeconds(1), failed));
      try (var statement =
          observer.prepareStatement(
              "select step,status,target_count,success_count,failure_count,byte_count,error_code"
                  + " from schubert.batch_runs where run_id=? order by step")) {
        statement.setObject(1, run.id());
        try (var rows = statement.executeQuery()) {
          for (String step : List.of(FIXTURE_BACKUP_CONFIG_8386D7E7, FIXTURE_BACKUP_DB_6C03A087)) {
            assertTrue(rows.next());
            assertEquals(step, rows.getString(1));
            assertEquals(FIXTURE_FAILED_7E8A57FE, rows.getString(2));
            assertEquals(1, rows.getLong(3));
            assertEquals(0, rows.getLong(4));
            assertEquals(1, rows.getLong(5));
            assertEquals(0, rows.getLong(6));
            assertEquals("COMMAND_FAILURE", rows.getString(7));
          }
          assertFalse(rows.next());
        }
      }
      releaseAdvisory(observer);
    }
  }

  @Test
  void bresume002PartialMismatchedAndMissingPriorPairsCannotPublishSkipProof() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("38710000-2222-4333-8444-555555555555"),
            Instant.parse("2026-11-29T15:00:00Z"));
    var observed = Instant.parse("2026-11-30T03:00:00Z");
    var subject =
        new MorningDatabaseSession(actualUrl, () -> {}, DriverManager::getConnection, c -> {});
    assertTrue(subject.execute(credential(), s -> s.successfulBackup(run, observed)).isEmpty());
    try (var admin = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var statement = admin.createStatement()) {
      String row =
          "insert into"
              + " schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,byte_count)"
              + " values";
      statement.execute(
          row
              + "(670101,'38710000-2222-4333-8444-555555555555','2026-11-30','BACKUP_DB',1,'2026-11-30T02:00:00Z','2026-11-30T02:00:03Z','SUCCESS',1,1,26)");
      assertThrows(
          IOException.class,
          () -> subject.execute(credential(), s -> s.successfulBackup(run, observed)));
      statement.execute(
          row
              + "(670102,'38710000-2222-4333-8444-555555555555','2026-11-30','BACKUP_CONFIG',1,'2026-11-30T02:00:00Z','2026-11-30T02:00:03Z','SUCCESS',2,2,67)");
      for (String change :
          List.of(
              "started_at='2026-11-30T02:00:01Z'",
              "ended_at='2026-11-30T02:00:04Z'",
              "attempt=2",
              "target_count=3",
              "success_count=1",
              "byte_count=0")) {
        statement.execute("update schubert.batch_runs set " + change + " where id=670102");
        assertThrows(
            IOException.class,
            () -> subject.execute(credential(), s -> s.successfulBackup(run, observed)));
        statement.execute(
            "update schubert.batch_runs set"
                + " started_at='2026-11-30T02:00:00Z',ended_at='2026-11-30T02:00:03Z',attempt=1,target_count=2,success_count=2,byte_count=67"
                + " where id=670102");
      }
      assertTrue(subject.execute(credential(), s -> s.successfulBackup(run, observed)).isPresent());
      assertThrows(
          IOException.class,
          () ->
              subject.execute(
                  credential(),
                  s -> s.successfulBackup(run, Instant.parse("2026-11-30T02:00:02Z"))));
      assertThrows(
          NullPointerException.class,
          () -> subject.execute(credential(), s -> s.successfulBackup(null, observed)));
      assertThrows(
          NullPointerException.class,
          () -> subject.execute(credential(), s -> s.successfulBackup(run, null)));
      assertThrows(
          NullPointerException.class,
          () -> subject.execute(credential(), s -> s.beginResumeBackup(null, observed)));
      try (var rows =
          statement.executeQuery(
              "select count(*) from schubert.batch_runs where"
                  + " run_id='38710000-2222-4333-8444-555555555555' and status='SKIPPED'")) {
        assertTrue(rows.next());
        assertEquals(0, rows.getInt(1));
        assertFalse(rows.next());
      }
    }
  }

  @Test
  void mdb016ActualAbandonedPairAndPostBeginOriginalProofAreDistinctFromAdmission()
      throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("38500000-2222-4333-8444-555555555555"),
            RUN.cutoff().plusSeconds(85L * 86400));
    Instant oldStart = NOW.plusSeconds(85L * 86400);
    Instant newStart = oldStart.plusSeconds(10);
    var previous = new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(run.id(), oldStart);
    var subject =
        new MorningDatabaseSession(actualUrl, () -> {}, DriverManager::getConnection, c -> {});
    subject.execute(
        credential(),
        s -> {
          assertThrows(IOException.class, () -> s.recheckConsistent(run));
          assertThrows(IOException.class, () -> s.requireAbandonedRequest(previous));
          s.beginBackup(run, oldStart, false);
          s.recheckConsistent(run);
          return true;
        });
    var held = new AtomicReference<MorningDatabaseSession.Access>();
    subject.execute(
        credential(),
        s -> {
          held.set(s);
          s.requireConsistent(run);
          var begins = s.beginBackup(run, newStart, true);
          assertEquals(2, begins.database().attempt());
          assertEquals(2, begins.configuration().attempt());
          assertThrows(IOException.class, () -> s.requireConsistent(run));
          assertThrows(NullPointerException.class, () -> s.recheckConsistent(null));
          assertThrows(NullPointerException.class, () -> s.requireAbandonedRequest(null));
          assertThrows(
              IOException.class,
              () ->
                  s.requireAbandonedRequest(
                      new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(
                          UUID.fromString("38500001-2222-4333-8444-555555555555"), oldStart)));
          assertThrows(
              IOException.class,
              () ->
                  s.requireAbandonedRequest(
                      new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(
                          run.id(), newStart)));
          s.requireAbandonedRequest(previous);
          s.recheckConsistent(run);
          var failed =
              new BatchStepResult(
                  BatchStepResult.Status.FAILED,
                  1,
                  0,
                  1,
                  0,
                  BatchStepResult.Reason.COMMAND_FAILURE);
          s.failBackup(begins, newStart.plusSeconds(2), failed, failed);
          s.recheckConsistent(run);
          assertThrows(IOException.class, () -> s.requireAbandonedRequest(previous));
          return true;
        });
    assertThrows(IOException.class, () -> held.get().recheckConsistent(run));
    assertThrows(IOException.class, () -> held.get().requireAbandonedRequest(previous));
    try (var c = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var s = c.createStatement();
        var rows =
            s.executeQuery(
                "select string_agg(step||':'||attempt||':'||status||':'||error_code,',' order by"
                    + " step,attempt) from schubert.batch_runs where"
                    + " run_id='38500000-2222-4333-8444-555555555555'")) {
      assertTrue(rows.next());
      assertEquals(
          "BACKUP_CONFIG:1:FAILED:ABANDONED,BACKUP_CONFIG:2:FAILED:COMMAND_FAILURE,BACKUP_DB:1:FAILED:ABANDONED,BACKUP_DB:2:FAILED:COMMAND_FAILURE",
          rows.getString(1));
      assertFalse(rows.next());
    }
  }

  /** PT-MDB-3920-001: cutoff-inclusive, current-start-exclusive retained request binding. */
  @Test
  void mdb3920001RetainedRequestTimeBoundariesPreserveActualRowsAndOwnedLock() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("39200001-2222-4333-8444-555555555555"),
            Instant.parse("2059-04-09T15:00:00Z"));
    Instant priorStart = run.cutoff();
    Instant currentStart = priorStart.plusNanos(1000);
    var previous =
        new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(run.id(), priorStart);
    var subject =
        new MorningDatabaseSession(actualUrl, () -> {}, DriverManager::getConnection, c -> {});
    subject.execute(
        credential(),
        session -> {
          session.beginBackup(run, priorStart, false);
          return true;
        });
    subject.execute(
        credential(),
        session -> {
          var begins = session.beginBackup(run, currentStart, true);
          assertEquals(2, begins.database().attempt());
          assertEquals(2, begins.configuration().attempt());
          try (var observer =
              DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "")) {
            String before = mdb588Audit(observer, run);
            for (var refused :
                List.of(
                    new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(
                        run.id(), priorStart.minusNanos(1000)),
                    new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(
                        run.id(), currentStart),
                    new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(
                        run.id(), currentStart.plusNanos(1000)),
                    new dev.codex.schubert.nk.batch.platform.BackupWorkerRequest(
                        UUID.fromString("39200002-2222-4333-8444-555555555555"), priorStart))) {
              IOException failure =
                  assertThrows(IOException.class, () -> session.requireAbandonedRequest(refused));
              assertEquals(FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, failure.getMessage());
              assertNull(failure.getCause());
              assertEquals(before, mdb588Audit(observer, run));
              assertFalse(advisory(observer));
              session.recheckConsistent(run);
            }
            // The actual original is exactly at cutoff, one database microsecond before current.
            session.requireAbandonedRequest(previous);
            assertEquals(before, mdb588Audit(observer, run));
            assertFalse(advisory(observer));
            session.recheckConsistent(run);
          } catch (SQLException failure) {
            throw new IOException("isolated retained-request row oracle unavailable", failure);
          }
          return true;
        });
    try (var observer = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var statement = observer.createStatement();
        var rows =
            statement.executeQuery(
                "select step,attempt,status,error_code,started_at,ended_at from schubert.batch_runs"
                    + " where run_id='39200001-2222-4333-8444-555555555555' order by step,attempt")) {
      for (String step : List.of(FIXTURE_BACKUP_CONFIG_8386D7E7, FIXTURE_BACKUP_DB_6C03A087)) {
        for (int attempt = 1; attempt <= 2; attempt++) {
          assertTrue(rows.next());
          assertEquals(step, rows.getString(1));
          assertEquals(attempt, rows.getInt(2));
          assertEquals(
              attempt == 1 ? FIXTURE_FAILED_7E8A57FE : FIXTURE_RUNNING_294BDBF9, rows.getString(3));
          assertEquals(attempt == 1 ? "ABANDONED" : null, rows.getString(4));
          assertEquals(attempt == 1 ? priorStart : currentStart, rows.getTimestamp(5).toInstant());
          assertEquals(
              attempt == 1 ? Optional.of(currentStart) : Optional.empty(),
              Optional.ofNullable(rows.getTimestamp(6)).map(Timestamp::toInstant));
        }
      }
      assertFalse(rows.next());
    }
    mdb2292NoOwnerResources();
  }

  /** PT-MDB-3924-001: different failure metrics are auditable but never a canonical pair proof. */
  @Test
  void mdb3924001DifferentFailureMetricsCannotMintCanonicalFailedPairSnapshot() throws Exception {
    for (int vector = 0; vector < 2; vector++) {
      var run =
          new BatchRun(
              UUID.fromString("3924000" + (vector + 1) + "-2222-4333-8444-555555555555"),
              Instant.parse("2059-05-09T15:00:00Z").plusSeconds(vector * 86400L));
      Instant started = run.cutoff().plusSeconds(60);
      Instant ended = started.plusSeconds(1);
      var canonical =
          new BatchStepResult(
              BatchStepResult.Status.FAILED, 1, 0, 1, 0, BatchStepResult.Reason.COMMAND_FAILURE);
      var different =
          new BatchStepResult(
              BatchStepResult.Status.FAILED, 2, 0, 2, 0, BatchStepResult.Reason.COMMAND_FAILURE);
      var database = vector == 0 ? canonical : different;
      var configuration = vector == 0 ? different : canonical;
      var subject =
          new MorningDatabaseSession(actualUrl, () -> {}, DriverManager::getConnection, c -> {});
      subject.execute(
          credential(),
          session -> {
            var begins = session.beginBackup(run, started, false);
            session.failBackup(begins, ended, database, configuration);
            try (var observer =
                DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "")) {
              String before = mdb588Audit(observer, run);
              IOException failure =
                  assertThrows(
                      IOException.class,
                      () -> session.failedBackupSnapshot(begins, () -> 10_000_000_000L));
              assertEquals(FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, failure.getMessage());
              assertNull(failure.getCause());
              assertEquals(before, mdb588Audit(observer, run));
              assertFalse(advisory(observer));
              session.recheckConsistent(run);
            } catch (SQLException failure) {
              throw new IOException("isolated failed-pair row oracle unavailable", failure);
            }
            // SS343/SSC124 admits only FAILED,1,0,1,0 for the public failed-pair projection.
            // Noncanonical committed metrics are audit data, not an observation capability.
            IOException observation =
                assertThrows(
                    IOException.class,
                    () ->
                        session.observeBackup(
                            begins, Optional.empty(), ended, () -> 10_000_000_000L));
            assertEquals(
                FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, observation.getMessage());
            assertNull(observation.getCause());
            return true;
          });
      try (var observer = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
          var query =
              observer.prepareStatement(
                  "select step,status,target_count,success_count,failure_count,byte_count,error_code"
                      + " from schubert.batch_runs where run_id=? order by step")) {
        query.setObject(1, run.id());
        try (var rows = query.executeQuery()) {
          for (String step : List.of(FIXTURE_BACKUP_CONFIG_8386D7E7, FIXTURE_BACKUP_DB_6C03A087)) {
            assertTrue(rows.next());
            long count =
                (step.equals(FIXTURE_BACKUP_DB_6C03A087) ? vector == 1 : vector == 0) ? 2 : 1;
            assertEquals(step, rows.getString(1));
            assertEquals(FIXTURE_FAILED_7E8A57FE, rows.getString(2));
            assertEquals(count, rows.getLong(3));
            assertEquals(0, rows.getLong(4));
            assertEquals(count, rows.getLong(5));
            assertEquals(0, rows.getLong(6));
            assertEquals("COMMAND_FAILURE", rows.getString(7));
          }
          assertFalse(rows.next());
        }
      }
      mdb2292NoOwnerResources();
    }
  }

  static final class Probe {
    final List<String> events = new ArrayList<>();
    final Map<String, Integer> counts = new HashMap<>();
    final Map<String, Throwable> faults = new HashMap<>();
    final Map<String, Integer> rowCounts = new HashMap<>();
    final Map<String, Object> role =
        new HashMap<>(
            Map.of(
                "effective_role",
                "schubert_batch",
                "login_role",
                "schubert_batch",
                "database_name",
                "schubert_nk",
                "recovery",
                false));
    boolean auto = true;
    boolean readonly;
    boolean lock = true;
    boolean nullLock;
    boolean held = true;
    boolean any;
    boolean identityConsistent = true;
    boolean nullConnection;
    boolean nullStatement;
    boolean nullRows;
    int isolation = Connection.TRANSACTION_READ_COMMITTED;
    int rowCount = 1;
    int connections;
    int statements;
    int rows;
    Properties retained;
    // MDB-PROJ-1737: optional literal provider rows, never schema/root authority.
    List<Map<String, Object>> successfulRows;
    String faultAt = "";
    Throwable failure = new SQLException("PRIVATE");

    void event(String name) throws Throwable {
      String point = name + "#" + counts.merge(name, 1, Integer::sum);
      events.add(point);
      if (faults.containsKey(name)) throw faults.get(name);
      if (point.equals(faultAt)) throw failure;
    }

    MorningDatabaseSession subject() {
      return new MorningDatabaseSession(
          URL,
          this::gate,
          (url, properties) -> open(url, properties, "schubert-nk-morning-controller"),
          this::schema);
    }

    CleanupDatabaseSession cleanupSubject() {
      return new CleanupDatabaseSession(
          URL,
          this::gate,
          (url, properties) -> open(url, properties, "schubert-nk-cleanup"),
          this::schema);
    }

    void gate() throws IOException {
      try {
        event("gate");
      } catch (IOException | RuntimeException | Error failure) {
        throw failure;
      } catch (Throwable failure) {
        throw new AssertionError(failure);
      }
    }

    void schema(Connection connection) throws SQLException, IOException {
      // Explicit synthetic schema port; this fixture does NOT mint root release authority.
      try {
        event("schema");
      } catch (SQLException | IOException | RuntimeException | Error failure) {
        throw failure;
      } catch (Throwable failure) {
        throw new AssertionError(failure);
      }
    }

    Connection open(String url, Properties properties, String application) throws SQLException {
      assertEquals(URL, url);
      assertEquals(
          Set.of("user", "password", "connectTimeout", "ApplicationName"),
          properties.stringPropertyNames());
      assertEquals("schubert_batch", properties.getProperty("user"));
      assertEquals("PUBLIC_PASSWORD", properties.getProperty("password"));
      assertEquals("3", properties.getProperty("connectTimeout"));
      assertEquals(application, properties.getProperty("ApplicationName"));
      retained = properties;
      try {
        event("connect");
      } catch (SQLException | RuntimeException | Error e) {
        throw e;
      } catch (Throwable e) {
        throw new AssertionError(e);
      }
      if (nullConnection) return null;
      connections++;
      return proxy(
          Connection.class,
          (m, a) -> {
            if (m.equals(FIXTURE_CLOSE_97959247)) {
              connections--;
              event("connection.close");
              return null;
            }
            event("connection." + m);
            return switch (m) {
              case FIXTURE_GETAUTOCOMMIT_C0200BDE -> auto;
              case "isReadOnly" -> readonly;
              case FIXTURE_GETTRANSACTIONISOLATION_6ED78CE6 -> isolation;
              case "setAutoCommit" -> {
                auto = (boolean) a[0];
                yield null;
              }
              case FIXTURE_PREPARESTATEMENT_CB987D1F -> statement((String) a[0]);
              case FIXTURE_COMMIT_5EA9C586, "rollback" -> null;
              default -> throw new AssertionError(m);
            };
          });
    }

    PreparedStatement statement(String sql) {
      if (nullStatement) return null;
      String kind =
          sql.contains("current_user")
              ? "ROLE"
              : sql.contains("pg_try_advisory")
                  ? "LOCK"
                  : sql.contains("pg_locks")
                      ? "HELD"
                      : sql.contains("maintenance_read_run_references") ? "REF" : "HISTORY";
      statements++;
      return proxy(
          PreparedStatement.class,
          (m, a) -> {
            if (m.equals(FIXTURE_CLOSE_97959247)) {
              statements--;
              event(kind + ".statement.close");
              return null;
            }
            event(kind + ".statement." + m);
            if (m.equals("setQueryTimeout")) {
              assertEquals(5, a[0]);
              return null;
            }
            if (m.equals("setObject") || m.equals("setString")) return null;
            if (!m.equals(FIXTURE_EXECUTEQUERY_85C8C423)) throw new AssertionError(m);
            if (kind.equals("HISTORY")) {
              if (successfulRows == null) throw new SQLException("PRIVATE");
              assertTrue(
                  sql.startsWith(
                      "select id,business_date,step,attempt,started_at,ended_at,target_count,"));
              assertTrue(sql.endsWith("order by started_at desc,id desc limit 2 for update"));
            }
            if (nullRows) return null;
            rows++;
            int[] index = {0};
            return proxy(
                ResultSet.class,
                (method, args) -> {
                  if (method.equals(FIXTURE_CLOSE_97959247)) {
                    rows--;
                    event(kind + ".row.close");
                    return null;
                  }
                  event(kind + ".row." + method);
                  return switch (method) {
                    case FIXTURE_NEXT_CA1733B5 ->
                        ++index[0]
                            <= (kind.equals("HISTORY")
                                ? successfulRows.size()
                                : rowCounts.getOrDefault(kind, rowCount));
                    case FIXTURE_GETSTRING_B3B802ED ->
                        kind.equals("HISTORY")
                            ? successfulRows.get(index[0] - 1).get((String) args[0])
                            : role.get((String) args[0]);
                    case FIXTURE_GETOBJECT_B6112877 -> {
                      String name = (String) args[0];
                      if (kind.equals("HISTORY")) yield successfulRows.get(index[0] - 1).get(name);
                      if (kind.equals("LOCK") && nullLock) yield null;
                      yield kind.equals("ROLE")
                          ? role.get(name)
                          : kind.equals("LOCK")
                              ? lock
                              : kind.equals("HELD")
                                  ? held
                                  : name.equals("identity_consistent")
                                      ? identityConsistent
                                      : name.equals("has_batch_history") ? any : false;
                    }
                    default -> throw new AssertionError(method);
                  };
                });
          });
    }

    void released() {
      assertEquals(0, connections);
      assertEquals(0, statements);
      assertEquals(0, rows);
      if (retained != null) assertTrue(retained.isEmpty());
    }
  }

  interface Invocation {
    Object call(String method, Object[] args) throws Throwable;
  }

  @SuppressWarnings("unchecked")
  static <T> T proxy(Class<T> type, Invocation invocation) {
    return (T)
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (p, m, a) -> invocation.call(m.getName(), a));
  }

  @Test
  void fixedUrlRootConstructorAndNullContracts() throws Exception {
    assertThrows(
        NullPointerException.class,
        () -> new MorningDatabaseSession(URL, () -> {}, (url, properties) -> null, null));
    for (String url :
        List.of(
            "",
            "jdbc:postgresql://localhost:5432/schubert_nk",
            URL + "?user=root",
            "jdbc:postgresql://127.0.0.1:0/schubert_nk",
            "jdbc:postgresql://127.0.0.1:65536/schubert_nk",
            URL.replace("schubert_nk", "postgres")))
      assertThrows(
          IllegalArgumentException.class,
          () -> new MorningDatabaseSession(url, () -> {}, (u, p) -> null));
    assertThrows(
        NullPointerException.class,
        () -> new MorningDatabaseSession(null, () -> {}, (u, p) -> null));
    assertThrows(
        NullPointerException.class, () -> new MorningDatabaseSession(URL, null, (u, p) -> null));
    assertThrows(NullPointerException.class, () -> new MorningDatabaseSession(URL, () -> {}, null));
    var context = RootStartupContext.create();
    var snapshot =
        new RootStartupContext.Snapshot(
            RootStartupContext.Service.MORNING, "PUBLIC", "PUBLIC", 2, 1, 1, "PUBLIC");
    assertThrows(NullPointerException.class, () -> new MorningDatabaseSession(URL, null, snapshot));
    assertThrows(NullPointerException.class, () -> new MorningDatabaseSession(URL, context, null));
    assertThrows(
        NullPointerException.class, () -> new MorningDatabaseSession(URL, context, snapshot, null));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningDatabaseSession(
                URL,
                context,
                new RootStartupContext.Snapshot(
                    RootStartupContext.Service.API, "P", "P", 2, 1, 1, "P")));
    assertThrows(
        IOException.class,
        () -> new MorningDatabaseSession(URL, context, snapshot).execute(credential(), s -> true));
    var p = new Probe();
    assertThrows(NullPointerException.class, () -> p.subject().execute(null, s -> true));
    var c = credential();
    assertThrows(NullPointerException.class, () -> p.subject().execute(c, null));
    assertThrows(IllegalStateException.class, c::copyPassword);
    p.released();
    assertThrows(
        NullPointerException.class, () -> new MorningDatabaseSession.BackupBegins(null, null));
    var a = new BatchStepAttempt(1, RUN, BatchStep.BACKUP_DB, 1, NOW, false);
    assertThrows(
        NullPointerException.class, () -> new MorningDatabaseSession.BackupBegins(a, null));
  }

  @Test
  void literalAdmissionAndSessionLifetime() throws Exception {
    var p = new Probe();
    var holder = new AtomicReference<MorningDatabaseSession.Session>();
    var c = credential();
    assertEquals(
        "PUBLIC",
        p.subject()
            .execute(
                c,
                s -> {
                  holder.set(s);
                  s.requireUnused(RUN);
                  return "PUBLIC";
                }));
    assertFalse(p.auto);
    assertThrows(IllegalStateException.class, c::copyPassword);
    p.released();
    int calls = p.events.size();
    assertThrows(IOException.class, () -> holder.get().requireUnused(RUN));
    assertEquals(calls, p.events.size());
    var current = new Probe();
    assertThrows(
        NullPointerException.class, () -> current.subject().execute(credential(), s -> null));
    current.released();
  }

  @Test
  void mdb013ResumeKeepsSameCutoffWithExistingReferences() throws Exception {
    var p = new Probe();
    p.any = true;
    var escaped = new AtomicReference<MorningDatabaseSession.Session>();
    assertEquals(
        "consistent",
        p.subject()
            .execute(
                credential(),
                session -> {
                  escaped.set(session);
                  session.requireConsistent(RUN);
                  assertThrows(IOException.class, () -> session.requireUnused(RUN));
                  return "consistent";
                }));
    assertTrue(p.events.stream().anyMatch(event -> event.startsWith("REF.statement.executeQuery")));
    p.released();
    assertThrows(IOException.class, () -> escaped.get().requireConsistent(RUN));

    var wrong = new Probe();
    wrong.any = true;
    wrong.identityConsistent = false;
    assertThrows(
        IOException.class,
        () ->
            wrong
                .subject()
                .execute(
                    credential(),
                    session -> {
                      session.requireConsistent(RUN);
                      return true;
                    }));
    wrong.released();

    var nullRun = new Probe();
    assertThrows(
        NullPointerException.class,
        () ->
            nullRun
                .subject()
                .execute(
                    credential(),
                    session -> {
                      session.requireConsistent(null);
                      return true;
                    }));
    nullRun.released();
  }

  @Test
  void mdb014RealResumeReferenceProjectionRejectsDifferentCutoff() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("34500000-2222-4333-8444-555555555555"),
            RUN.cutoff().plusSeconds(100L * 86400));
    var subject =
        new MorningDatabaseSession(
            actualUrl, () -> {}, DriverManager::getConnection, connection -> {});
    subject.execute(
        credential(),
        session -> {
          session.requireUnused(run);
          session.beginBackup(run, NOW.plusSeconds(100L * 86400), false);
          return true;
        });
    boolean consistent =
        subject.execute(
            credential(),
            session -> {
              session.requireConsistent(run);
              return true;
            });
    assertTrue(consistent);
    var sameBusinessDay = new BatchRun(run.id(), run.cutoff().plusSeconds(1));
    boolean sameDateAccepted =
        subject.execute(
            credential(),
            session -> {
              session.requireConsistent(sameBusinessDay);
              return true;
            });
    assertTrue(sameDateAccepted);
    // SS331 §3.12: batch history has only JST business_date, not the original instant.
    // Exact same-run cutoff is owned by the durable original; this SQL rejects a different day.
    var wrongCutoff = new BatchRun(run.id(), run.cutoff().plusSeconds(86400));
    assertThrows(
        IOException.class,
        () ->
            subject.execute(
                credential(),
                session -> {
                  session.requireConsistent(wrongCutoff);
                  return true;
                }));
  }

  @Test
  void roleRecoveryNullAndLockRejections() throws Exception {
    for (String kind : List.of("LOCK", "HELD"))
      for (int count : List.of(0, 2)) {
        var probe = new Probe();
        probe.rowCounts.put(kind, count);
        assertThrows(IOException.class, () -> probe.subject().execute(credential(), s -> true));
        probe.released();
      }
    for (String key : List.of("effective_role", "login_role", "database_name", "recovery"))
      for (boolean missing : List.of(false, true)) {
        var p = new Probe();
        if (missing) p.role.remove(key);
        else p.role.put(key, key.equals("recovery") ? true : "wrong");
        assertThrows(IOException.class, () -> p.subject().execute(credential(), s -> true), key);
        p.released();
      }
    for (String kind :
        List.of(
            "auto",
            "readonly",
            "isolation",
            "lock",
            "held",
            "connection",
            "statement",
            "rows",
            "none",
            "many")) {
      var p = new Probe();
      switch (kind) {
        case "auto" -> p.auto = false;
        case "readonly" -> p.readonly = true;
        case "isolation" -> p.isolation = 8;
        case "lock" -> p.lock = false;
        case "held" -> p.held = false;
        case "connection" -> p.nullConnection = true;
        case "statement" -> p.nullStatement = true;
        case "rows" -> p.nullRows = true;
        case "none" -> p.rowCount = 0;
        default -> p.rowCount = 2;
      }
      assertThrows(IOException.class, () -> p.subject().execute(credential(), s -> true), kind);
      p.released();
    }
  }

  @Test
  void allAdmissionResourceFailuresAndUnknownIdentity() throws Exception {
    var good = new Probe();
    good.subject()
        .execute(
            credential(),
            s -> {
              s.requireUnused(RUN);
              return true;
            });
    List<String> points = List.copyOf(good.events);
    for (String point : points)
      for (Throwable failure :
          List.of(
              point.startsWith("gate") ? new IOException("PRIVATE") : new SQLException("PRIVATE"),
              new IllegalStateException("PRIVATE"),
              new AssertionError("PRIVATE"))) {
        var p = new Probe();
        p.faultAt = point;
        p.failure = failure;
        Throwable actual =
            assertThrows(
                Throwable.class,
                () ->
                    p.subject()
                        .execute(
                            credential(),
                            s -> {
                              s.requireUnused(RUN);
                              return true;
                            }),
                point);
        if (failure instanceof RuntimeException || failure instanceof Error)
          assertSame(failure, actual, point);
        else assertEquals(FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, actual.getMessage());
        p.released();
      }
    var p = new Probe();
    p.any = true;
    assertThrows(
        IOException.class,
        () ->
            p.subject()
                .execute(
                    credential(),
                    s -> {
                      s.requireUnused(RUN);
                      return true;
                    }));
    p.released();
  }

  @Test
  void compoundUnknownAndNullMethodBoundaries() throws Exception {
    for (Throwable body :
        List.of(
            new SQLException("PRIVATE"),
            new IOException("PRIVATE"),
            new BatchRepositoryException()))
      for (Throwable close :
          List.of(
              new SQLException("PRIVATE"),
              new IllegalStateException("PRIVATE"),
              new AssertionError("PRIVATE"))) {
        var probe = new Probe();
        if (body instanceof SQLException) probe.faults.put("ROLE.row.next", body);
        probe.faults.put("connection.close", close);
        Throwable actual =
            assertThrows(
                Throwable.class,
                () ->
                    probe
                        .subject()
                        .execute(
                            credential(),
                            s -> {
                              if (body instanceof IOException io) throw io;
                              if (body instanceof BatchRepositoryException known) throw known;
                              return true;
                            }));
        if (close instanceof SQLException)
          assertEquals(FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891, actual.getMessage());
        else assertSame(close, actual);
        probe.released();
      }
    for (Throwable secondary :
        List.of(
            new SQLException("PRIVATE"),
            new IllegalStateException("PRIVATE"),
            new AssertionError("PRIVATE"))) {
      var p = new Probe();
      var primary = new IllegalStateException("PRIVATE");
      p.faults.put("ROLE.row.next", primary);
      p.faults.put("ROLE.row.close", secondary);
      p.faults.put("ROLE.statement.close", secondary);
      p.faults.put("connection.close", secondary);
      assertSame(
          primary,
          assertThrows(
              IllegalStateException.class, () -> p.subject().execute(credential(), s -> true)));
      assertEquals(3, primary.getSuppressed().length);
      for (var f : primary.getSuppressed())
        assertEquals("batch repository operation failed", f.getMessage());
      p.released();
    }
    var p = new Probe();
    assertEquals(
        Boolean.TRUE,
        p.subject()
            .execute(
                credential(),
                s -> {
                  assertThrows(NullPointerException.class, () -> s.requireUnused(null));
                  assertThrows(NullPointerException.class, () -> s.beginBackup(null, NOW, false));
                  assertThrows(NullPointerException.class, () -> s.beginBackup(RUN, null, false));
                  assertThrows(
                      BatchRepositoryException.class, () -> s.beginBackup(RUN, NOW, false));
                  return true;
                }));
    p.released();
    var other = new Probe();
    var primary = new SQLException("PRIVATE");
    var unknown = new AssertionError("PRIVATE");
    other.faults.put("ROLE.row.next", primary);
    other.faults.put("ROLE.row.close", unknown);
    var current = other;
    assertSame(
        unknown,
        assertThrows(
            AssertionError.class, () -> current.subject().execute(credential(), s -> true)));
    other.released();
  }

  @Test
  void interruptionAndForeignThreadCannotUseBorrowedSession() throws Exception {
    for (Throwable failure :
        List.of(
            new SQLException("PRIVATE"),
            new IOException("PRIVATE"),
            new IllegalStateException("PRIVATE"),
            new AssertionError("PRIVATE"))) {
      var blocked = new Probe();
      blocked.faults.put("schema", failure);
      Throwable actual =
          assertThrows(
              Throwable.class,
              () -> blocked.subject().execute(credential(), s -> s.beginBackup(RUN, NOW, false)));
      if (failure instanceof RuntimeException || failure instanceof Error)
        assertSame(failure, actual);
      else assertInstanceOf(IOException.class, actual);
      assertEquals(1, blocked.counts.get("schema"));
      assertTrue(blocked.events.stream().noneMatch(e -> e.startsWith("HISTORY.")));
      assertTrue(blocked.events.stream().noneMatch(e -> e.startsWith("connection.commit")));
      blocked.released();
    }
    var p = new Probe();
    Thread.currentThread().interrupt();
    try {
      assertThrows(IOException.class, () -> p.subject().execute(credential(), s -> true));
    } finally {
      Thread.interrupted();
    }
    assertTrue(p.events.isEmpty());
    p.released();
    var q = new Probe();
    assertThrows(
        IOException.class,
        () ->
            q.subject()
                .execute(
                    credential(),
                    s -> {
                      Thread.currentThread().interrupt();
                      return true;
                    }));
    Thread.interrupted();
    q.released();
    var r = new Probe();
    try (var executor = Executors.newSingleThreadExecutor()) {
      assertEquals(
          Boolean.TRUE,
          r.subject()
              .execute(
                  credential(),
                  s -> {
                    try {
                      assertEquals(
                          FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891,
                          executor
                              .submit(
                                  () ->
                                      assertThrows(IOException.class, () -> s.requireUnused(RUN))
                                          .getMessage())
                              .get(5, TimeUnit.SECONDS));
                    } catch (Exception e) {
                      throw new AssertionError(e);
                    }
                    return true;
                  }));
    }
    r.released();
  }

  @Test
  void actualBothBackupBeginsAreCommittedTogether() throws Exception {
    var unverified = new MorningDatabaseSession(actualUrl, () -> {}, DriverManager::getConnection);
    var absent =
        new BatchRun(
            UUID.fromString("31400000-2222-4333-8444-555555555555"),
            RUN.cutoff().plusSeconds(1728000));
    assertThrows(
        IOException.class,
        () ->
            unverified.execute(
                credential(),
                session -> session.beginBackup(absent, NOW.plusSeconds(1728000), false)));
    try (var connection = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var statement = connection.createStatement();
        var rows =
            statement.executeQuery(
                "select count(*) from schubert.batch_runs where"
                    + " run_id='31400000-2222-4333-8444-555555555555'")) {
      assertTrue(rows.next());
      assertEquals(0, rows.getInt(1));
      assertFalse(rows.next());
    }
    var schemaCalls = new AtomicInteger();
    var subject =
        new MorningDatabaseSession(
            actualUrl,
            () -> {},
            DriverManager::getConnection,
            connection -> {
              assertFalse(connection.isClosed());
              schemaCalls.incrementAndGet();
            });
    var begins =
        subject.execute(
            credential(),
            s -> {
              s.requireUnused(RUN);
              return s.beginBackup(RUN, NOW, false);
            });
    assertEquals(BatchStep.BACKUP_DB, begins.database().step());
    assertEquals(BatchStep.BACKUP_CONFIG, begins.configuration().step());
    assertEquals(RUN, begins.database().run());
    assertEquals(RUN, begins.configuration().run());
    assertNotEquals(begins.database().id(), begins.configuration().id());
    assertEquals(1, schemaCalls.get());
    try (var c = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var s = c.createStatement();
        var rows =
            s.executeQuery(
                "select string_agg(step||':'||status||':'||attempt,',' order by step) from"
                    + " schubert.batch_runs where run_id='31100000-2222-4333-8444-555555555555'")) {
      assertTrue(rows.next());
      assertEquals("BACKUP_CONFIG:RUNNING:1,BACKUP_DB:RUNNING:1", rows.getString(1));
      assertFalse(rows.next());
    }
  }

  @Test
  void actualCommitAmbiguityNeverReturnsHandles() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("31100001-2222-4333-8444-555555555555"),
            RUN.cutoff().plusSeconds(864000));
    for (boolean afterCommit : List.of(false, true)) {
      AtomicReference<Connection> owned = new AtomicReference<>();
      var subject =
          new MorningDatabaseSession(
              actualUrl,
              () -> {},
              (url, props) -> {
                var c = DriverManager.getConnection(url, props);
                owned.set(c);
                return proxy(
                    Connection.class,
                    (name, args) -> {
                      if (name.equals(FIXTURE_COMMIT_5EA9C586)) {
                        if (afterCommit) c.commit();
                        throw new SQLException("PRIVATE");
                      }
                      try {
                        return Connection.class
                            .getMethod(name, parameterTypes(name, args))
                            .invoke(c, args);
                      } catch (InvocationTargetException e) {
                        throw e.getCause();
                      }
                    });
              },
              connection -> assertFalse(connection.isClosed()));
      assertThrows(
          IOException.class,
          () ->
              subject.execute(
                  credential(),
                  s -> {
                    s.requireUnused(run);
                    return s.beginBackup(run, NOW.plusSeconds(864000), false);
                  }));
      assertTrue(owned.get().isClosed());
      try (var c = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "");
          var s = c.createStatement();
          var rows =
              s.executeQuery(
                  "select count(*) from schubert.batch_runs where"
                      + " run_id='31100001-2222-4333-8444-555555555555'")) {
        assertTrue(rows.next());
        assertEquals(afterCommit ? 2 : 0, rows.getInt(1));
      }
    }
  }

  @Test
  void mdb009NoHandoffBeforeConfirmedBackupCommit() throws Exception {
    var p = new Probe();
    var calls = new AtomicInteger();
    assertEquals(
        Boolean.TRUE,
        p.subject()
            .execute(
                credential(),
                session -> {
                  assertThrows(NullPointerException.class, () -> session.handoffCleanup(null));
                  assertEquals(
                      FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891,
                      assertThrows(
                              IOException.class,
                              () ->
                                  session.handoffCleanup(
                                      () -> {
                                        calls.incrementAndGet();
                                        return true;
                                      }))
                          .getMessage());
                  return true;
                }));
    assertEquals(0, calls.get());
    p.released();
  }

  @Test
  void mdb010RealSeparateChildAdvisoryHandoffAndParentReacquire() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("32600000-2222-4333-8444-555555555555"),
            RUN.cutoff().plusSeconds(2592000));
    var subject =
        new MorningDatabaseSession(
            actualUrl, () -> {}, DriverManager::getConnection, connection -> {});
    try (var observer = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "")) {
      assertEquals(
          "CHILD",
          subject.execute(
              credential(),
              session -> {
                session.requireUnused(run);
                var begins = session.beginBackup(run, NOW.plusSeconds(2592000), false);
                assertThrows(IOException.class, () -> session.handoffCleanup(() -> "PREMATURE"));
                confirmActualFailedPair(session, begins);
                assertThrows(
                    IOException.class,
                    () -> session.beginBackup(run, NOW.plusSeconds(2592000), false));
                try (var otherThread = Executors.newSingleThreadExecutor()) {
                  assertEquals(
                      FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891,
                      otherThread
                          .submit(
                              () ->
                                  assertThrows(
                                          IOException.class,
                                          () -> session.handoffCleanup(() -> "WRONG_THREAD"))
                                      .getMessage())
                          .get(5, TimeUnit.SECONDS));
                } catch (InterruptedException failure) {
                  Thread.currentThread().interrupt();
                  throw new IOException("thread check interrupted");
                } catch (ExecutionException | TimeoutException failure) {
                  throw new IOException("thread check failed");
                }
                String result =
                    session.handoffCleanup(
                        () -> {
                          assertThrows(IOException.class, () -> session.requireUnused(run));
                          assertThrows(
                              IOException.class, () -> session.handoffCleanup(() -> "REENTER"));
                          try (var child =
                              DriverManager.getConnection(actualUrl, "schubert_batch", "")) {
                            assertTrue(advisory(child));
                            assertFalse(advisory(observer));
                            releaseAdvisory(child);
                            return "CHILD";
                          } catch (SQLException failure) {
                            throw new IOException("child database unavailable");
                          }
                        });
                try {
                  assertFalse(advisory(observer));
                } catch (SQLException failure) {
                  throw new IOException("observer database unavailable");
                }
                assertThrows(IOException.class, () -> session.handoffCleanup(() -> "SECOND"));
                assertThrows(IOException.class, () -> session.requireUnused(run));
                return result;
              }));
      awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
    }
  }

  @Test
  void mdb011ChildFailureCannotBecomeSuccessOrRetainParentConnection() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("32600001-2222-4333-8444-555555555555"),
            RUN.cutoff().plusSeconds(2678400));
    var subject =
        new MorningDatabaseSession(
            actualUrl, () -> {}, DriverManager::getConnection, connection -> {});
    var callback = new AtomicInteger();
    assertEquals(
        FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891,
        assertThrows(
                IOException.class,
                () ->
                    subject.execute(
                        credential(),
                        session -> {
                          session.requireUnused(run);
                          var begins = session.beginBackup(run, NOW.plusSeconds(2678400), false);
                          confirmActualFailedPair(session, begins);
                          return session.handoffCleanup(
                              () -> {
                                callback.incrementAndGet();
                                throw new IOException("PRIVATE child failure");
                              });
                        }))
            .getMessage());
    assertEquals(1, callback.get());
    try (var observer = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "")) {
      awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
    }
  }

  @Test
  void mdb012AutocommitDriftAfterCommitRefusesChildWithoutCallback() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("32600002-2222-4333-8444-555555555555"),
            RUN.cutoff().plusSeconds(2764800));
    var restored = new AtomicBoolean();
    var borrowed = new AtomicReference<Connection>();
    var calls = new AtomicInteger();
    var subject =
        new MorningDatabaseSession(
            actualUrl,
            () -> {},
            (url, properties) -> {
              var real = DriverManager.getConnection(url, properties);
              borrowed.set(real);
              return proxy(
                  Connection.class,
                  (name, args) -> {
                    if (name.equals(FIXTURE_GETAUTOCOMMIT_C0200BDE) && restored.get()) return false;
                    try {
                      return Connection.class
                          .getMethod(name, parameterTypes(name, args))
                          .invoke(real, args);
                    } catch (InvocationTargetException e) {
                      throw e.getCause();
                    }
                  });
            },
            connection -> {});
    assertEquals(
        FIXTURE_ROOT_BATCH_DATABASE_UNAVAILABLE_1FB96891,
        assertThrows(
                IOException.class,
                () ->
                    subject.execute(
                        credential(),
                        session -> {
                          session.requireUnused(run);
                          var begins = session.beginBackup(run, NOW.plusSeconds(2764800), false);
                          confirmActualFailedPair(session, begins);
                          restored.set(
                              true); // Inject drift only after genuine terminal completion.
                          return session.handoffCleanup(
                              () -> {
                                calls.incrementAndGet();
                                return true;
                              });
                        }))
            .getMessage());
    assertEquals(0, calls.get());
    assertTrue(borrowed.get().isClosed());
  }

  @Test
  void mdb020ReleaseObservationHasFiniteDeadlineAndCannotUnlockAnotherOwner() throws Exception {
    try (var holder = DriverManager.getConnection(actualUrl, "schubert_batch", "");
        var observer = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "")) {
      assertTrue(advisory(holder));
      assertThrows(
          AssertionError.class, () -> awaitReleased(observer, TimeUnit.MILLISECONDS.toNanos(30)));
      assertFalse(advisory(observer));
      try (var unlock = holder.prepareStatement("select pg_advisory_unlock(71419602)")) {
        try (var result = unlock.executeQuery()) {
          assertTrue(result.next());
          assertTrue(result.getBoolean(1));
        }
      }
      awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
    }
  }

  private static void awaitReleased(Connection observer, long budgetNanos) throws Exception {
    awaitAcquired(observer, budgetNanos);
    // JDBC close sends Terminate without a server acknowledgement.
    releaseAdvisory(observer);
  }

  private static void awaitAcquired(Connection observer, long budgetNanos) throws Exception {
    long deadline = System.nanoTime() + budgetNanos;
    while (!advisory(observer)) {
      if (System.nanoTime() >= deadline) fail("server advisory release deadline exceeded");
      TimeUnit.MILLISECONDS.sleep(5);
    }
  }

  private static void releaseAdvisory(Connection connection) throws SQLException {
    try (var statement = connection.prepareStatement("select pg_advisory_unlock(71419602)");
        var rows = statement.executeQuery()) {
      assertTrue(rows.next());
      assertTrue(rows.getBoolean(1));
      assertFalse(rows.next());
    }
    assertFalse(ownsAdvisory(connection));
  }

  private static boolean ownsAdvisory(Connection connection) throws SQLException {
    try (var statement = connection.createStatement();
        var rows =
            statement.executeQuery(
                "select exists(select 1 from pg_locks where locktype='advisory' and"
                    + " pid=pg_backend_pid() and classid=0 and objid=71419602 and objsubid=1 and"
                    + " granted)")) {
      assertTrue(rows.next());
      boolean value = rows.getBoolean(1);
      assertFalse(rows.next());
      return value;
    }
  }

  @Test
  void mdb594002RetainedChildRefusesHandoffAndAcknowledgedUnlockAllowsParentReacquire()
      throws Exception {
    var reachedAfterHandoff = new AtomicInteger();
    try (var parent = DriverManager.getConnection(actualUrl, "schubert_batch", "");
        var child = DriverManager.getConnection(actualUrl, "schubert_batch", "");
        var observer = DriverManager.getConnection(actualUrl, FIXTURE_PGPT_ADMIN_F5D1227C, "")) {
      try {
        assertTrue(advisory(parent));
        assertThrows(
            dev.codex.schubert.nk.batch.cleanup.InspectorLockHandoff.Failure.class,
            () -> {
              dev.codex.schubert.nk.batch.cleanup.InspectorLockHandoff.execute(
                  parent,
                  () -> {
                    try {
                      assertTrue(advisory(child));
                      assertTrue(ownsAdvisory(child));
                    } catch (SQLException failure) {
                      throw new IOException("fixture retained child", failure);
                    }
                    return 0;
                  });
              reachedAfterHandoff.incrementAndGet();
            });
        assertEquals(0, reachedAfterHandoff.get());
        assertFalse(ownsAdvisory(parent));
        assertTrue(ownsAdvisory(child));
        assertFalse(advisory(observer));
        releaseAdvisory(child);
        assertTrue(advisory(parent));
        assertEquals(
            0,
            dev.codex.schubert.nk.batch.cleanup.InspectorLockHandoff.execute(
                parent,
                () -> {
                  try {
                    assertTrue(advisory(child));
                    assertFalse(advisory(observer));
                    releaseAdvisory(child);
                  } catch (SQLException failure) {
                    throw new IOException("fixture acknowledged child", failure);
                  }
                  return 0;
                }));
        reachedAfterHandoff.incrementAndGet();
        assertEquals(1, reachedAfterHandoff.get());
        assertTrue(ownsAdvisory(parent));
        assertFalse(ownsAdvisory(child));
        assertFalse(advisory(observer));
      } finally {
        if (ownsAdvisory(child)) releaseAdvisory(child);
        if (ownsAdvisory(parent)) releaseAdvisory(parent);
      }
      awaitReleased(observer, TimeUnit.SECONDS.toNanos(5));
      assertFalse(ownsAdvisory(observer));
    }
  }

  private static boolean advisory(Connection connection) throws SQLException {
    try (var statement = connection.prepareStatement("select pg_try_advisory_lock(71419602)")) {
      try (var rows = statement.executeQuery()) {
        assertTrue(rows.next());
        boolean result = rows.getBoolean(1);
        assertFalse(rows.next());
        return result;
      }
    }
  }

  private static void confirmActualFailedPair(
      MorningDatabaseSession.Access session, MorningDatabaseSession.BackupBegins begins)
      throws IOException {
    var failed =
        new BatchStepResult(
            BatchStepResult.Status.FAILED, 1, 0, 1, 0, BatchStepResult.Reason.COMMAND_FAILURE);
    session.failBackup(begins, begins.database().startedAt().plusSeconds(1), failed, failed);
  }

  private static Class<?>[] parameterTypes(String name, Object[] args) {
    if (args == null) return new Class<?>[0];
    if (name.equals(FIXTURE_PREPARESTATEMENT_CB987D1F)) return new Class<?>[] {String.class};
    if (name.equals("setAutoCommit")) return new Class<?>[] {boolean.class};
    throw new AssertionError(name);
  }
}
