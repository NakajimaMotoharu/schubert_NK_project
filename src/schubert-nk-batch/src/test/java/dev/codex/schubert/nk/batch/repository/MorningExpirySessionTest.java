package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * EXPARENT001/003/004/005: real isolated PG advisory handoffs, independent SQL/audit oracle.
 * Provider counters are fixed input here; genuine native MQ/Unit evidence is separate in 294.
 */
final class MorningExpirySessionTest {
  private static final String FIXTURE_AUTOCOMMIT_36FCE733 = "AUTOCOMMIT";
  private static final String FIXTURE_READONLY_72E7E87D = "READONLY";
  private static final String FIXTURE_GETAUTOCOMMIT_C0200BDE = "getAutoCommit";
  private static final String FIXTURE_ISREADONLY_B1148EC6 = "isReadOnly";
  private static final String FIXTURE_PGPT_ADMIN_F5D1227C = "pgpt_admin";
  private static final String FIXTURE_VALID_53E4338E = "VALID";
  private static final String FIXTURE_SCHUBERT_BATCH_F9C88479 = "schubert_batch";
  private static final String FIXTURE_SUCCESS_10855C7F = "SUCCESS";
  @TempDir static Path root;
  static BatchDatabaseFixture db;
  static String url;
  static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("39100000-2222-4333-8444-555555555555"),
          Instant.parse("2026-09-12T15:00:00Z"));
  static final Instant NOW = Instant.parse("2026-09-13T02:00:00Z");
  static final MaintenanceOwnerFrame.Guard OWNER = () -> 30_000_000_000L;

  /** PT-MDB2614-001: expiry readback never promotes RUNNING or unrelated data to completion. */
  @Test
  void mdb2614001ExpiryReadbackRejectsRunningWrongTargetAndDbDriftWithoutMutation()
      throws Exception {
    for (String fault :
        List.of(
            "RUNNING",
            "WRONG_TARGET",
            "WRONG_BEGIN",
            FIXTURE_AUTOCOMMIT_36FCE733,
            FIXTURE_READONLY_72E7E87D)) {
      reset();
      var armed = new java.util.concurrent.atomic.AtomicBoolean();
      var retained = new java.util.concurrent.atomic.AtomicReference<Connection>();
      var receipt =
          fault.equals("WRONG_TARGET")
              ? ExpiryReceiptFixture.backupReceipt(0)
              : ExpiryReceiptFixture.receipt(0);
      var subject =
          new MorningDatabaseSession(
              url,
              () -> {},
              (address, properties) -> {
                var connection = DriverManager.getConnection(address, properties);
                retained.set(connection);
                return (Connection)
                    java.lang.reflect.Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          if (armed.get()) {
                            if (fault.equals(FIXTURE_AUTOCOMMIT_36FCE733)
                                && method.getName().equals(FIXTURE_GETAUTOCOMMIT_C0200BDE))
                              return false;
                            if (fault.equals(FIXTURE_READONLY_72E7E87D)
                                && method.getName().equals(FIXTURE_ISREADONLY_B1148EC6))
                              return true;
                          }
                          return mdb2604Invoke(method, connection, args);
                        });
              },
              c -> {});
      subject.execute(
          credential(),
          session -> {
            ready(session, 1);
            var begins = session.beginExpiry(RUN, NOW.plusSeconds(14), OWNER);
            session.handoffExpiry(() -> Boolean.TRUE);
            var handle = begins.current();
            var input =
                fault.equals("WRONG_BEGIN")
                    ? new MorningDatabaseSession.ExpiryBegins(
                        new BatchStepAttempt(
                            handle.id() + 1_000_000,
                            handle.run(),
                            handle.step(),
                            handle.attempt(),
                            handle.startedAt(),
                            false),
                        Optional.empty())
                    : begins;
            String before;
            try {
              before = mdb2604Rows();
            } catch (SQLException failure) {
              throw new IOException("isolated SQL precondition unavailable", failure);
            }
            armed.set(true);
            assertThrows(
                IOException.class, () -> session.observeExpiry(input, receipt, OWNER), fault);
            try {
              assertEquals(before, mdb2604Rows());
            } catch (SQLException failure) {
              throw new IOException("isolated SQL postcondition unavailable", failure);
            }
            return Boolean.TRUE;
          });
      assertTrue(retained.get().isClosed());
      try (var observer = DriverManager.getConnection(url, FIXTURE_PGPT_ADMIN_F5D1227C, "");
          var statement = observer.createStatement();
          var rows =
              statement.executeQuery(
                  "select (select count(*) from pg_stat_activity where application_name='schubert-nk-morning-controller' and datname=current_database()),(select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted)")) {
        assertTrue(rows.next());
        assertEquals(0, rows.getLong(1));
        assertEquals(0, rows.getLong(2));
        assertFalse(rows.next());
      }
    }
  }

  /** PT-MDB2612-001: retained cleanup references must match the current complete SQL readback. */
  @Test
  void mdb2612001CleanupReferencesRejectDriftAndForgedSnapshotWithoutChangingRows()
      throws Exception {
    for (String fault :
        List.of(
            FIXTURE_VALID_53E4338E,
            FIXTURE_AUTOCOMMIT_36FCE733,
            FIXTURE_READONLY_72E7E87D,
            "MISMATCH",
            "SQL")) {
      reset();
      var armed = new java.util.concurrent.atomic.AtomicBoolean();
      var retained = new java.util.concurrent.atomic.AtomicReference<Connection>();
      var subject =
          new MorningDatabaseSession(
              url,
              () -> {},
              (address, properties) -> {
                var connection = DriverManager.getConnection(address, properties);
                retained.set(connection);
                return (Connection)
                    java.lang.reflect.Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          if (armed.get()) {
                            if (fault.equals(FIXTURE_AUTOCOMMIT_36FCE733)
                                && method.getName().equals(FIXTURE_GETAUTOCOMMIT_C0200BDE))
                              return false;
                            if (fault.equals(FIXTURE_READONLY_72E7E87D)
                                && method.getName().equals(FIXTURE_ISREADONLY_B1148EC6))
                              return true;
                            if (fault.equals("SQL")
                                && method.getName().equals("prepareStatement")
                                && ((String) args[0]).startsWith("select distinct on(step)"))
                              throw new SQLException("isolated reference read refusal", "08006");
                          }
                          return mdb2604Invoke(method, connection, args);
                        });
              },
              c -> {});
      subject.execute(
          credential(),
          session -> {
            ready(session, 1);
            var actualInput = session.observeCleanupBackupUnavailable(RUN, 0, OWNER);
            var entries = new ArrayList<>(actualInput.entries());
            if (fault.equals("MISMATCH")) {
              var first = entries.getFirst();
              var handle = first.attempt();
              entries.set(
                  0,
                  new CleanupTerminalRepository.Entry(
                      new BatchStepAttempt(
                          handle.id() + 1_000_000,
                          handle.run(),
                          handle.step(),
                          handle.attempt(),
                          handle.startedAt(),
                          handle.skipped()),
                      first.endedAt(),
                      first.result(),
                      first.progressSeal()));
            }
            var expectedInput = new CleanupTerminalRepository.Snapshot(entries);
            armed.set(true);
            if (fault.equals(FIXTURE_VALID_53E4338E))
              assertEquals(
                  List.of(
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty()),
                  session.cleanupReferences(expectedInput, OWNER));
            else
              assertThrows(
                  IOException.class, () -> session.cleanupReferences(expectedInput, OWNER), fault);
            return Boolean.TRUE;
          });
      assertTrue(retained.get().isClosed());
      try (var observer = DriverManager.getConnection(url, FIXTURE_PGPT_ADMIN_F5D1227C, "");
          var statement = observer.createStatement();
          var rows =
              statement.executeQuery(
                  "select count(*),count(*) filter(where step='CLEAN_EXPIRY'),count(*) filter(where step like 'BACKUP_%' and status='FAILED'),count(*) filter(where step not like 'BACKUP_%' and step<>'CLEAN_TRANSFER' and status='SKIPPED'),count(*) filter(where step='CLEAN_TRANSFER' and status='SUCCESS'),sum(byte_count),(select count(*) from pg_stat_activity where application_name='schubert-nk-morning-controller' and datname=current_database()),(select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted) from schubert.batch_runs")) {
        assertTrue(rows.next());
        assertEquals(9, rows.getLong(1));
        assertEquals(0, rows.getLong(2));
        assertEquals(2, rows.getLong(3));
        assertEquals(6, rows.getLong(4));
        assertEquals(1, rows.getLong(5));
        assertEquals(0, rows.getLong(6));
        assertEquals(0, rows.getLong(7));
        assertEquals(0, rows.getLong(8));
        assertFalse(rows.next());
      }
    }
  }

  /** PT-MDB2610-001: cleanup receipt and failed-backup mode cannot bypass DB readback guards. */
  @Test
  void mdb2610001CleanupReadbackRejectsDbDriftReceiptAndBackupModeWithoutMutation()
      throws Exception {
    for (String fault :
        List.of(
            FIXTURE_AUTOCOMMIT_36FCE733,
            FIXTURE_READONLY_72E7E87D,
            "CODE10",
            "FAILED_MODE",
            "REJECTED_READONLY")) {
      reset();
      var rejected = ExpiryReceiptFixture.cleanupReceipt(30);
      var armed = new java.util.concurrent.atomic.AtomicBoolean();
      var retained = new java.util.concurrent.atomic.AtomicReference<Connection>();
      var subject =
          new MorningDatabaseSession(
              url,
              () -> {},
              (address, properties) -> {
                var connection = DriverManager.getConnection(address, properties);
                retained.set(connection);
                return (Connection)
                    java.lang.reflect.Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          if (armed.get()) {
                            if (fault.equals(FIXTURE_AUTOCOMMIT_36FCE733)
                                && method.getName().equals(FIXTURE_GETAUTOCOMMIT_C0200BDE))
                              return false;
                            if ((fault.equals(FIXTURE_READONLY_72E7E87D)
                                    || fault.equals("REJECTED_READONLY"))
                                && method.getName().equals(FIXTURE_ISREADONLY_B1148EC6))
                              return true;
                          }
                          return mdb2604Invoke(method, connection, args);
                        });
              },
              c -> {});
      subject.execute(
          credential(),
          session -> {
            ready(session, 1);
            armed.set(true);
            if (fault.equals("FAILED_MODE"))
              assertThrows(IOException.class, () -> session.observeCleanup(RUN, 0, OWNER));
            else if (fault.equals("REJECTED_READONLY"))
              assertThrows(
                  IOException.class, () -> session.observeCleanupRejected(RUN, rejected, OWNER));
            else
              assertThrows(
                  IOException.class,
                  () ->
                      session.observeCleanupBackupUnavailable(
                          RUN, fault.equals("CODE10") ? 10 : 0, OWNER),
                  fault);
            return Boolean.TRUE;
          });
      assertTrue(retained.get().isClosed());
      try (var observer = DriverManager.getConnection(url, FIXTURE_PGPT_ADMIN_F5D1227C, "");
          var statement = observer.createStatement();
          var rows =
              statement.executeQuery(
                  "select count(*),count(*) filter(where step='CLEAN_EXPIRY'),count(*) filter(where step like 'BACKUP_%' and status='FAILED'),count(*) filter(where step not like 'BACKUP_%' and step<>'CLEAN_TRANSFER' and status='SKIPPED'),count(*) filter(where step='CLEAN_TRANSFER' and status='SUCCESS'),sum(byte_count),(select count(*) from pg_stat_activity where application_name='schubert-nk-morning-controller' and datname=current_database()),(select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted) from schubert.batch_runs")) {
        assertTrue(rows.next());
        assertEquals(9, rows.getLong(1));
        assertEquals(0, rows.getLong(2));
        assertEquals(2, rows.getLong(3));
        assertEquals(6, rows.getLong(4));
        assertEquals(1, rows.getLong(5));
        assertEquals(0, rows.getLong(6));
        assertEquals(0, rows.getLong(7));
        assertEquals(0, rows.getLong(8));
        assertFalse(rows.next());
      }
    }
  }

  /** PT-MDB2608-001: failed expiry handoff is not a worker success or renewed authority. */
  @Test
  void mdb2608001ExpiryHandoffRejectsTransactionUnlockAndReacquireFailure() throws Exception {
    for (String fault : List.of(FIXTURE_AUTOCOMMIT_36FCE733, "UNLOCK", "RELOCK")) {
      reset();
      var armed = new java.util.concurrent.atomic.AtomicBoolean();
      var callbacks = new java.util.concurrent.atomic.AtomicInteger();
      var retained = new java.util.concurrent.atomic.AtomicReference<Connection>();
      var subject =
          new MorningDatabaseSession(
              url,
              () -> {},
              (address, properties) -> {
                var connection = DriverManager.getConnection(address, properties);
                retained.set(connection);
                return (Connection)
                    java.lang.reflect.Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          if (armed.get()) {
                            if (fault.equals(FIXTURE_AUTOCOMMIT_36FCE733)
                                && method.getName().equals(FIXTURE_GETAUTOCOMMIT_C0200BDE))
                              return false;
                            if (method.getName().equals("prepareStatement")
                                && ((fault.equals("UNLOCK")
                                        && ((String) args[0]).contains("pg_advisory_unlock"))
                                    || (fault.equals("RELOCK")
                                        && ((String) args[0]).contains("pg_try_advisory_lock"))))
                              throw new SQLException("isolated handoff SQL refusal", "08006");
                          }
                          return mdb2604Invoke(method, connection, args);
                        });
              },
              c -> {});
      subject.execute(
          credential(),
          session -> {
            ready(session, 1);
            session.beginExpiry(RUN, NOW.plusSeconds(14), OWNER);
            String before;
            try {
              before = mdb2604Rows();
            } catch (SQLException failure) {
              throw new IOException("isolated SQL precondition unavailable", failure);
            }
            armed.set(true);
            assertThrows(
                IOException.class,
                () ->
                    session.handoffExpiry(
                        () -> {
                          callbacks.incrementAndGet();
                          return Boolean.TRUE;
                        }),
                fault);
            assertEquals(fault.equals("RELOCK") ? 1 : 0, callbacks.get());
            try {
              assertEquals(before, mdb2604Rows());
            } catch (SQLException failure) {
              throw new IOException("isolated SQL postcondition unavailable", failure);
            }
            return Boolean.TRUE;
          });
      assertTrue(retained.get().isClosed());
      try (var observer = DriverManager.getConnection(url, FIXTURE_PGPT_ADMIN_F5D1227C, "");
          var statement = observer.createStatement();
          var rows =
              statement.executeQuery(
                  "select (select count(*) from pg_stat_activity where application_name='schubert-nk-morning-controller' and datname=current_database()),(select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted)")) {
        assertTrue(rows.next());
        assertEquals(0, rows.getLong(1));
        assertEquals(0, rows.getLong(2));
        assertFalse(rows.next());
      }
    }
  }

  /** PT-MDB2606-001: no expiry row may be published from an incompatible parent DB state. */
  @Test
  void mdb2606001ExpiryAdmissionRejectsForeignRunAndTransactionDriftBeforePublishing()
      throws Exception {
    for (String fault :
        List.of("FOREIGN_RUN", FIXTURE_AUTOCOMMIT_36FCE733, FIXTURE_READONLY_72E7E87D)) {
      reset();
      var armed = new java.util.concurrent.atomic.AtomicBoolean();
      var retained = new java.util.concurrent.atomic.AtomicReference<Connection>();
      var subject =
          new MorningDatabaseSession(
              url,
              () -> {},
              (address, properties) -> {
                var connection = DriverManager.getConnection(address, properties);
                retained.set(connection);
                return (Connection)
                    java.lang.reflect.Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          if (armed.get()
                              && fault.equals(FIXTURE_AUTOCOMMIT_36FCE733)
                              && method.getName().equals(FIXTURE_GETAUTOCOMMIT_C0200BDE))
                            return false;
                          if (armed.get()
                              && fault.equals(FIXTURE_READONLY_72E7E87D)
                              && method.getName().equals(FIXTURE_ISREADONLY_B1148EC6)) return true;
                          return mdb2604Invoke(method, connection, args);
                        });
              },
              c -> {});
      subject.execute(
          credential(),
          session -> {
            ready(session, 1);
            var candidate =
                fault.equals("FOREIGN_RUN")
                    ? new BatchRun(
                        UUID.fromString("26060000-2222-4333-8444-555555555555"), RUN.cutoff())
                    : RUN;
            armed.set(true);
            assertThrows(
                IOException.class,
                () -> session.beginExpiry(candidate, NOW.plusSeconds(14), OWNER),
                fault);
            return Boolean.TRUE;
          });
      assertTrue(retained.get().isClosed());
      try (var observer = DriverManager.getConnection(url, FIXTURE_PGPT_ADMIN_F5D1227C, "");
          var statement = observer.createStatement();
          var rows =
              statement.executeQuery(
                  "select count(*),count(*) filter(where step='CLEAN_EXPIRY'),count(*) filter(where step like 'BACKUP_%' and status='FAILED'),count(*) filter(where step not like 'BACKUP_%' and step<>'CLEAN_TRANSFER' and status='SKIPPED'),count(*) filter(where step='CLEAN_TRANSFER' and status='SUCCESS'),sum(byte_count),(select count(*) from pg_stat_activity where application_name='schubert-nk-morning-controller' and datname=current_database()),(select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted) from schubert.batch_runs")) {
        assertTrue(rows.next());
        assertEquals(9, rows.getLong(1));
        assertEquals(0, rows.getLong(2));
        assertEquals(2, rows.getLong(3));
        assertEquals(6, rows.getLong(4));
        assertEquals(1, rows.getLong(5));
        assertEquals(0, rows.getLong(6));
        assertEquals(0, rows.getLong(7));
        assertEquals(0, rows.getLong(8));
        assertFalse(rows.next());
      }
    }
  }

  /** PT-MDB2604-001: actual DB handoff guards; literal release facts grant no OS authority. */
  @Test
  void mdb2604001PermitReadbackRequiresBothLocksAndFreshSchemaWithoutChangingRows()
      throws Exception {
    for (String fault :
        List.of(FIXTURE_VALID_53E4338E, "INITIAL_HELD", "FINAL_HELD", "SCHEMA_SQL")) {
      reset();
      var armed = new java.util.concurrent.atomic.AtomicBoolean();
      var heldReads = new java.util.concurrent.atomic.AtomicInteger();
      var retained = new java.util.concurrent.atomic.AtomicReference<Connection>();
      var facts =
          new dev.codex.schubert.nk.batch.platform.RootReleaseAdmission.DatabaseInspection(
              new dev.codex.schubert.nk.bootstrap.StartupReleaseManifest.Contents(
                  "PUBLIC", "a".repeat(64), List.of(), Map.of(), Map.of()),
              List.of(),
              Map.of());
      MorningDatabaseSession.Schema schema =
          new MorningDatabaseSession.Schema() {
            public void verify(Connection connection) {}

            public dev.codex.schubert.nk.batch.platform.RootReleaseAdmission.DatabaseInspection
                inspect(Connection connection) throws SQLException {
              if (fault.equals("SCHEMA_SQL"))
                throw new SQLException("isolated schema refusal", "08006");
              return facts;
            }
          };
      var subject =
          new MorningDatabaseSession(
              url,
              () -> {},
              (address, properties) -> {
                var connection = DriverManager.getConnection(address, properties);
                retained.set(connection);
                return (Connection)
                    java.lang.reflect.Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (unused, method, args) -> {
                          Object result = mdb2604Invoke(method, connection, args);
                          if (!armed.get()
                              || !method.getName().equals("prepareStatement")
                              || !((String) args[0]).contains("pg_locks")) return result;
                          var statement = (PreparedStatement) result;
                          return java.lang.reflect.Proxy.newProxyInstance(
                              PreparedStatement.class.getClassLoader(),
                              new Class<?>[] {PreparedStatement.class},
                              (unusedStatement, called, inputs) -> {
                                Object value = mdb2604Invoke(called, statement, inputs);
                                if (!called.getName().equals("executeQuery")) return value;
                                var rows = (ResultSet) value;
                                return java.lang.reflect.Proxy.newProxyInstance(
                                    ResultSet.class.getClassLoader(),
                                    new Class<?>[] {ResultSet.class},
                                    (unusedRows, read, columns) -> {
                                      if (read.getName().equals("getObject")
                                          && columns[0].equals("value")) {
                                        int n = heldReads.incrementAndGet();
                                        if ((fault.equals("INITIAL_HELD") && n == 1)
                                            || (fault.equals("FINAL_HELD") && n == 2)) return false;
                                      }
                                      return mdb2604Invoke(read, rows, columns);
                                    });
                              });
                        });
              },
              schema);
      subject.execute(
          credential(),
          session -> {
            ready(session, 1);
            session.beginExpiry(RUN, NOW.plusSeconds(14), OWNER);
            session.handoffExpiry(() -> Boolean.TRUE);
            String before;
            try {
              before = mdb2604Rows();
            } catch (SQLException failure) {
              throw new IOException("isolated SQL precondition unavailable", failure);
            }
            armed.set(true);
            if (fault.equals(FIXTURE_VALID_53E4338E)) {
              var value = session.inspectPermitDatabase(OWNER);
              assertEquals(FIXTURE_SCHUBERT_BATCH_F9C88479, value.loginRole());
              assertEquals(FIXTURE_SCHUBERT_BATCH_F9C88479, value.effectiveRole());
              assertEquals("schubert_nk", value.database());
              assertTrue(value.autoCommit());
              assertFalse(value.jdbcReadOnly());
              assertEquals(Connection.TRANSACTION_READ_COMMITTED, value.isolation());
              assertFalse(value.recovery());
              assertTrue(value.advisoryHeld());
              assertSame(facts, value.release());
              assertEquals(2, heldReads.get());
            } else
              assertThrows(IOException.class, () -> session.inspectPermitDatabase(OWNER), fault);
            try {
              assertEquals(before, mdb2604Rows());
            } catch (SQLException failure) {
              throw new IOException("isolated SQL postcondition unavailable", failure);
            }
            return Boolean.TRUE;
          });
      assertTrue(retained.get().isClosed());
      try (var observer = DriverManager.getConnection(url, FIXTURE_PGPT_ADMIN_F5D1227C, "");
          var statement = observer.createStatement();
          var rows =
              statement.executeQuery(
                  "select (select count(*) from pg_stat_activity where application_name='schubert-nk-morning-controller' and datname=current_database()),(select count(*) from pg_locks where locktype='advisory' and classid=0 and objid=71419602 and granted)")) {
        assertTrue(rows.next());
        assertEquals(0, rows.getLong(1));
        assertEquals(0, rows.getLong(2));
        assertFalse(rows.next());
      }
    }
  }

  private static Object mdb2604Invoke(java.lang.reflect.Method method, Object target, Object[] args)
      throws Throwable {
    try {
      return method.invoke(target, args);
    } catch (java.lang.reflect.InvocationTargetException failure) {
      throw failure.getCause();
    }
  }

  private static String mdb2604Rows() throws SQLException {
    try (var observer = DriverManager.getConnection(url, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var statement =
            observer.prepareStatement(
                "select step,attempt,status,started_at,ended_at,target_count,success_count,failure_count,byte_count,error_code,error_summary from schubert.batch_runs where run_id=? order by step")) {
      statement.setObject(1, RUN.id());
      try (var rows = statement.executeQuery()) {
        var actual = new ArrayList<String>();
        for (String step :
            List.of(
                "BACKUP_CONFIG",
                "BACKUP_DB",
                "CLEAN_BATCH_RUN",
                "CLEAN_EXPIRY",
                "CLEAN_INBOX_OUTBOX",
                "CLEAN_LOG",
                "CLEAN_NOTIFICATION",
                "CLEAN_QUESTION",
                "CLEAN_SESSION",
                "CLEAN_TRANSFER")) {
          assertTrue(rows.next());
          assertEquals(step, rows.getString("step"));
          assertEquals(1, rows.getInt("attempt"));
          assertEquals(
              step.startsWith("BACKUP_")
                  ? "FAILED"
                  : step.equals("CLEAN_EXPIRY")
                      ? "RUNNING"
                      : step.equals("CLEAN_TRANSFER") ? FIXTURE_SUCCESS_10855C7F : "SKIPPED",
              rows.getString("status"));
          assertEquals(0, rows.getLong("byte_count"));
          var fields = new ArrayList<String>();
          for (int i = 1; i <= 11; i++) fields.add(rows.getString(i));
          actual.add(fields.toString());
        }
        assertFalse(rows.next());
        return actual.toString();
      }
    }
  }

  @BeforeAll
  static void start() throws Exception {
    db = new BatchDatabaseFixture(root);
    try (var c = db.admin();
        var s = c.createStatement()) {
      url = c.getMetaData().getURL().replace("/postgres", "/schubert_nk");
      s.execute("create database schubert_nk");
    }
    Path resources =
        Path.of(
            System.getProperty("nk.pt.repository"), "src/schubert-nk-api/src/main/resources/db");
    try (var c = DriverManager.getConnection(url, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var s = c.createStatement()) {
      s.execute(Files.readString(resources.resolve("provisioning/001_roles.sql")));
    }
    Flyway.configure()
        .dataSource(url, "schubert_migration", "")
        .defaultSchema("schubert_meta")
        .schemas("schubert_meta")
        .createSchemas(true)
        .initSql("SET ROLE nk_owner")
        .locations("filesystem:" + resources.resolve("migration"))
        .validateOnMigrate(true)
        .cleanDisabled(true)
        .load()
        .migrate();
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = DriverManager.getConnection(url, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var s = c.createStatement()) {
      s.execute("delete from schubert.batch_runs");
    }
  }

  static InspectorDbCredential credential() {
    return InspectorDbCredential.consume("PUBLIC_PASSWORD".getBytes(StandardCharsets.US_ASCII));
  }

  static MorningDatabaseSession subject() {
    return new MorningDatabaseSession(url, () -> {}, DriverManager::getConnection, c -> {});
  }

  static void sql(Connection c, String text) throws SQLException {
    try (var s = c.createStatement()) {
      s.execute(text);
    }
  }

  static boolean held(Connection c) throws SQLException {
    try (var s = c.createStatement();
        var r =
            s.executeQuery(
                "select exists(select 1 from pg_locks where locktype='advisory' and pid=pg_backend_pid() and classid=0 and objid=71419602 and granted)")) {
      assertTrue(r.next());
      return r.getBoolean(1);
    }
  }

  static void ready(MorningDatabaseSession.Session session, int attempt) throws IOException {
    var start = NOW.plusSeconds(attempt * 10L);
    var backup = session.beginBackup(RUN, start, true);
    var failed =
        new BatchStepResult(
            BatchStepResult.Status.FAILED, 1, 0, 1, 0, BatchStepResult.Reason.COMMAND_FAILURE);
    session.failBackup(backup, start.plusSeconds(1), failed, failed);
    session.handoffCleanup(
        () -> {
          try (var c = DriverManager.getConnection(url, FIXTURE_SCHUBERT_BATCH_F9C88479, "")) {
            sql(c, "select pg_advisory_lock(71419602)");
            assertTrue(held(c));
            for (String step :
                List.of(
                    "CLEAN_NOTIFICATION",
                    "CLEAN_QUESTION",
                    "CLEAN_SESSION",
                    "CLEAN_INBOX_OUTBOX",
                    "CLEAN_LOG",
                    "CLEAN_BATCH_RUN"))
              sql(
                  c,
                  "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary) values('"
                      + RUN.id()
                      + "','2026-09-13','"
                      + step
                      + "',"
                      + attempt
                      + ",'"
                      + start.plusSeconds(2)
                      + "','"
                      + start.plusSeconds(2)
                      + "','SKIPPED',0,0,0,0,'BACKUP_UNAVAILABLE','verified backup unavailable')");
            sql(
                c,
                "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count"
                    + (attempt == 1 ? "" : ",error_code,error_summary")
                    + ") values('"
                    + RUN.id()
                    + "','2026-09-13','CLEAN_TRANSFER',"
                    + attempt
                    + ",'"
                    + start.plusSeconds(2)
                    + "','"
                    + start.plusSeconds(attempt == 1 ? 3 : 2)
                    + "','"
                    + (attempt == 1 ? FIXTURE_SUCCESS_10855C7F : "SKIPPED")
                    + "',0,0,0,0"
                    + (attempt == 1
                        ? ""
                        : ",'ALREADY_SUCCESSFUL','step already successful for business date'")
                    + ")");
          } catch (SQLException known) {
            throw new IOException(known);
          }
          return true;
        });
    assertEquals(0, session.observeCleanupBackupUnavailable(RUN, 0, OWNER).exitCode());
  }

  @Test
  void actualFreshThenNormalSkipKeepOriginalAuditAndEachHandoffIsOneShot() throws Exception {
    for (int attempt = 1; attempt <= 2; attempt++) {
      final int current = attempt;
      var receipt = ExpiryReceiptFixture.receipt(0);
      subject()
          .execute(
              credential(),
              s -> {
                assertThrows(IOException.class, () -> s.beginExpiry(RUN, NOW, OWNER));
                assertThrows(
                    IOException.class,
                    () -> s.handoffExpiry(() -> fail("no child before Cleanup")));
                ready(s, current);
                var begins = s.beginExpiry(RUN, NOW.plusSeconds(current * 10L + 4), OWNER);
                assertEquals(current == 2, begins.current().skipped());
                assertEquals(current, begins.current().attempt());
                assertEquals(current == 2, begins.prior().isPresent());
                assertThrows(
                    IOException.class, () -> s.beginExpiry(RUN, NOW.plusSeconds(60), OWNER));
                s.handoffExpiry(
                    () -> {
                      try (var c =
                          DriverManager.getConnection(url, FIXTURE_SCHUBERT_BATCH_F9C88479, "")) {
                        sql(c, "select pg_advisory_lock(71419602)");
                        assertTrue(held(c));
                        c.setAutoCommit(false);
                        if (current == 1) {
                          var audit = new ExpiryAuditRepository(c);
                          var stage = audit.stage(begins.current(), 3, 2, 200);
                          c.commit();
                          audit.finish(
                              begins.current(),
                              stage,
                              NOW.plusSeconds(15),
                              1L,
                              new BatchStepResult(
                                  BatchStepResult.Status.SUCCESS,
                                  2,
                                  2,
                                  0,
                                  200,
                                  BatchStepResult.Reason.NONE));
                          c.commit();
                        } else new BatchRunRepository(c).verifyAlreadySuccessful(begins.current());
                      } catch (SQLException known) {
                        throw new IOException(known);
                      }
                      return true;
                    });
                var observed = s.observeExpiry(begins, receipt, OWNER);
                assertEquals(
                    new ExpiryAuditRepository.Snapshot(
                        FIXTURE_SUCCESS_10855C7F,
                        Instant.parse("2026-09-05T15:00:00Z"),
                        3L,
                        1L,
                        2,
                        2,
                        0,
                        200,
                        NOW.plusSeconds(15),
                        null,
                        null),
                    observed.audit());
                assertEquals(begins, observed.begins());
                assertSame(receipt, observed.receipt());
                assertEquals(
                    current == 1 ? NOW.plusSeconds(15) : NOW.plusSeconds(24), observed.ended());
                assertEquals(
                    current == 1
                        ? new BatchStepResult(
                            BatchStepResult.Status.SUCCESS,
                            2,
                            2,
                            0,
                            200,
                            BatchStepResult.Reason.NONE)
                        : new BatchStepResult(
                            BatchStepResult.Status.SKIPPED,
                            0,
                            0,
                            0,
                            0,
                            BatchStepResult.Reason.ALREADY_SUCCESSFUL),
                    observed.result());
                if (current == 2) {
                  var prior = observed.begins().prior().orElseThrow();
                  assertNotEquals(begins.current().id(), prior.handle().id());
                  assertEquals(1, prior.handle().attempt());
                  assertEquals(NOW.plusSeconds(14), prior.handle().startedAt());
                  assertEquals(prior.audit(), observed.audit());
                }
                s.recheckExpiry(observed, OWNER);
                assertThrows(IOException.class, () -> s.recheckExpiry(observed, () -> 0));
                assertThrows(
                    IOException.class,
                    () -> s.handoffExpiry(() -> fail("cannot reacquire a second handoff")));
                return true;
              });
    }
    try (var c = DriverManager.getConnection(url, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select attempt,status,target_count,success_count,failure_count,byte_count,error_code,started_at=ended_at as same_time,expiry_before_count,expiry_after_count from schubert.batch_runs where step='CLEAN_EXPIRY' order by attempt")) {
      assertTrue(r.next());
      assertEquals(1, r.getInt("attempt"));
      assertEquals(FIXTURE_SUCCESS_10855C7F, r.getString("status"));
      assertEquals(2, r.getLong("target_count"));
      assertEquals(2, r.getLong("success_count"));
      assertEquals(0, r.getLong("failure_count"));
      assertEquals(200, r.getLong("byte_count"));
      assertEquals(3, r.getLong("expiry_before_count"));
      assertEquals(1, r.getLong("expiry_after_count"));
      assertNull(r.getString("error_code"));
      assertFalse(r.getBoolean("same_time"));
      assertTrue(r.next());
      assertEquals(2, r.getInt("attempt"));
      assertEquals("SKIPPED", r.getString("status"));
      for (String field : List.of("target_count", "success_count", "failure_count", "byte_count"))
        assertEquals(0, r.getLong(field));
      assertEquals("ALREADY_SUCCESSFUL", r.getString("error_code"));
      assertTrue(r.getBoolean("same_time"));
      assertNull(r.getObject("expiry_before_count"));
      assertNull(r.getObject("expiry_after_count"));
      assertFalse(r.next());
    }
  }

  @Test
  void expiredOwnerNeverCommitsExpiryBeginAndDefaultCapabilityDoesNotGrantOperation()
      throws Exception {
    subject()
        .execute(
            credential(),
            s -> {
              ready(s, 1);
              assertThrows(
                  IOException.class, () -> s.beginExpiry(RUN, NOW.plusSeconds(14), () -> 0));
              assertThrows(NullPointerException.class, () -> s.beginExpiry(null, NOW, OWNER));
              assertThrows(NullPointerException.class, () -> s.beginExpiry(RUN, null, OWNER));
              assertThrows(NullPointerException.class, () -> s.beginExpiry(RUN, NOW, null));
              return true;
            });
    try (var c = DriverManager.getConnection(url, FIXTURE_PGPT_ADMIN_F5D1227C, "");
        var s = c.createStatement();
        var r =
            s.executeQuery("select count(*) from schubert.batch_runs where step='CLEAN_EXPIRY'")) {
      assertTrue(r.next());
      assertEquals(0, r.getLong(1));
    }
  }
}
