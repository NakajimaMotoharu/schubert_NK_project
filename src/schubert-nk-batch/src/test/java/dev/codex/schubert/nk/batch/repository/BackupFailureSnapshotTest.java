package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** CFDB001..002: isolated real PostgreSQL with independent SQL/full 14-column postconditions. */
final class BackupFailureSnapshotTest {
  @TempDir static Path root;
  static BatchDatabaseFixture db;
  private static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
          Instant.parse("2026-09-12T15:00:00Z"));
  private static final Instant START = Instant.parse("2026-09-13T02:00:00Z");
  private static final Instant END = Instant.parse("2026-09-13T02:00:03Z");

  @BeforeAll
  static void start() throws Exception {
    db = new BatchDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void seed() throws Exception {
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute("delete from schubert.batch_runs");
      for (String row : List.of("7,'BACKUP_DB'", "8,'BACKUP_CONFIG'"))
        s.execute(
            "insert into"
                + " schubert.batch_runs(id,step,run_id,business_date,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary)"
                + " values("
                + row
                + ",'12345678-9abc-def0-8123-456789abcdef','2026-09-13',4,'2026-09-13T02:00:00Z','2026-09-13T02:00:03Z','FAILED',1,0,1,0,'COMMAND_FAILURE','batch"
                + " command failed')");
    }
  }

  private static BackupFailureSnapshot snapshot() {
    return new BackupFailureSnapshot(
        new BatchStepAttempt(7, RUN, BatchStep.BACKUP_DB, 4, START, false),
        new BatchStepAttempt(8, RUN, BatchStep.BACKUP_CONFIG, 4, START, false),
        END);
  }

  private void verify() throws Exception {
    try (var c = CleanupStepFixture.locked(db, false)) {
      snapshot().verifyLatest(c, () -> 10_000_000_000L);
      assertFalse(c.isClosed());
      assertFalse(c.getAutoCommit());
      c.rollback();
    }
  }

  /** PT-CFDB-2916-001: first and final independent identity observations are mandatory. */
  @Test
  void cfdb2916001FirstAndFinalIdentityDriftRejectWithoutMutation() throws Exception {
    for (int driftAt : List.of(1, 2)) {
      var reads = new AtomicInteger();
      try (var actual = CleanupStepFixture.locked(db, false)) {
        var connection =
            cfdb2916Proxy(
                actual,
                (sql, column, observed) -> {
                  if (sql.contains("maintenance_read_run_references")
                      && column.equals("identity_consistent")) {
                    return reads.incrementAndGet() == driftAt ? Boolean.FALSE : observed;
                  }
                  return observed;
                },
                "");
        var failure =
            assertThrows(
                IOException.class,
                () -> snapshot().verifyLatest(connection, () -> 10_000_000_000L));
        assertEquals("failed backup run identity unavailable", failure.getMessage());
        assertNull(failure.getCause());
        assertEquals(driftAt, reads.get());
        assertFalse(actual.isClosed());
        actual.rollback();
      }
      cfdb2916CommittedRows();
    }
  }

  /** PT-CFDB-2916-002: every nullable typed projection and both JDBC resource boundaries. */
  @Test
  void cfdb2916002EveryNullColumnAndMissingResourceIsBounded() throws Exception {
    for (String fault :
        List.of(
            "id",
            "run_id",
            "business_date",
            "step",
            "attempt",
            "started_at",
            "ended_at",
            "status",
            "target_count",
            "success_count",
            "failure_count",
            "byte_count",
            "error_code",
            "error_summary",
            "STATEMENT",
            "ROWS")) {
      var injected = new AtomicInteger();
      try (var actual = CleanupStepFixture.locked(db, false)) {
        var connection =
            cfdb2916Proxy(
                actual,
                (sql, column, observed) -> {
                  if (sql.startsWith("select id,run_id,") && column.equals(fault)) {
                    injected.incrementAndGet();
                    return null;
                  }
                  return observed;
                },
                fault);
        var failure =
            assertThrows(
                IOException.class,
                () -> snapshot().verifyLatest(connection, () -> 10_000_000_000L));
        assertEquals("failed backup observation unavailable", failure.getMessage());
        assertNull(failure.getCause());
        assertEquals(0, failure.getSuppressed().length);
        assertEquals(fault.equals("STATEMENT") || fault.equals("ROWS") ? 0 : 1, injected.get());
        assertFalse(actual.isClosed());
        actual.rollback();
      }
      cfdb2916CommittedRows();
    }
  }

  /** PT-CFDB-2916-003: same id and a different run cannot form a failed pair. */
  @Test
  void cfdb2916003PairRejectsEqualIdAndForeignRunAtConstructor() {
    var database = snapshot().database();
    var foreign =
        new BatchRun(UUID.fromString("12345678-9abc-def0-8123-456789abcdee"), RUN.cutoff());
    for (var configuration :
        List.of(
            new BatchStepAttempt(7, RUN, BatchStep.BACKUP_CONFIG, 4, START, false),
            new BatchStepAttempt(8, foreign, BatchStep.BACKUP_CONFIG, 4, START, false))) {
      var failure =
          assertThrows(
              IllegalArgumentException.class,
              () -> new BackupFailureSnapshot(database, configuration, END));
      assertEquals("failed backup pair invalid", failure.getMessage());
    }
  }

  @FunctionalInterface
  private interface CfdbProjection {
    Object read(String sql, String column, Object observed);
  }

  /** PT-CFDB-2936-001: an invalid provider's extra row cannot certify a failed pair. */
  @Test
  void cfdb2936001ProviderExtraRowRejectsWithoutCertifyingOrMutatingPair() throws Exception {
    var next = new AtomicInteger();
    try (var actual = CleanupStepFixture.locked(db, false)) {
      var connection =
          cfdb2916Proxy(
              actual,
              (sql, column, observed) -> {
                assertEquals("__next__", column);
                int call = next.incrementAndGet();
                assertEquals(call == 1, observed);
                // Literal malformed provider response: one real row then a phantom second row.
                return Boolean.TRUE;
              },
              "EXTRA_ROW");
      var failure =
          assertThrows(
              IOException.class, () -> snapshot().verifyLatest(connection, () -> 10_000_000_000L));
      assertEquals("failed backup observation unavailable", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
      assertEquals(2, next.get());
      assertFalse(actual.isClosed());
      actual.rollback();
    }
    cfdb2916CommittedRows();
  }

  private static Object cfdb2916Invoke(Method method, Object target, Object[] args)
      throws Throwable {
    try {
      return method.invoke(target, args);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }

  private static Connection cfdb2916Proxy(
      Connection actual, CfdbProjection projection, String fault) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (unused, method, args) -> {
              var observed = cfdb2916Invoke(method, actual, args);
              if (!method.getName().equals("prepareStatement")) return observed;
              var sql = (String) args[0];
              var statement = (PreparedStatement) observed;
              if (sql.startsWith("select id,run_id,") && fault.equals("STATEMENT")) {
                statement.close();
                return null;
              }
              return Proxy.newProxyInstance(
                  PreparedStatement.class.getClassLoader(),
                  new Class<?>[] {PreparedStatement.class},
                  (unusedStatement, called, input) -> {
                    var value = cfdb2916Invoke(called, statement, input);
                    if (!called.getName().equals("executeQuery")) return value;
                    var rows = (ResultSet) value;
                    if (sql.startsWith("select id,run_id,") && fault.equals("ROWS")) {
                      rows.close();
                      return null;
                    }
                    return Proxy.newProxyInstance(
                        ResultSet.class.getClassLoader(),
                        new Class<?>[] {ResultSet.class},
                        (unusedRows, read, values) -> {
                          var cell = cfdb2916Invoke(read, rows, values);
                          if (fault.equals("EXTRA_ROW")) {
                            if (sql.startsWith("select id,run_id,")
                                && read.getName().equals("next"))
                              return projection.read(sql, "__next__", cell);
                            return cell;
                          }
                          return read.getName().equals("getObject") && values.length == 2
                              ? projection.read(sql, (String) values[0], cell)
                              : cell;
                        });
                  });
            });
  }

  private static void cfdb2916CommittedRows() throws Exception {
    try (var c = db.admin();
        var s = c.createStatement();
        var rows =
            s.executeQuery(
                "select"
                    + " id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary"
                    + " from schubert.batch_runs order by id")) {
      for (var expected : List.of(List.of(7L, "BACKUP_DB"), List.of(8L, "BACKUP_CONFIG"))) {
        assertTrue(rows.next());
        assertEquals(expected.get(0), rows.getObject("id", Long.class));
        assertEquals(expected.get(1), rows.getString("step"));
        assertEquals(
            UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
            rows.getObject("run_id", UUID.class));
        assertEquals(
            java.time.LocalDate.of(2026, 9, 13),
            rows.getObject("business_date", java.time.LocalDate.class));
        assertEquals(
            Instant.parse("2026-09-13T02:00:00Z"),
            rows.getObject("started_at", java.time.OffsetDateTime.class).toInstant());
        assertEquals(
            Instant.parse("2026-09-13T02:00:03Z"),
            rows.getObject("ended_at", java.time.OffsetDateTime.class).toInstant());
        assertEquals(4, rows.getInt("attempt"));
        assertEquals("FAILED", rows.getString("status"));
        assertEquals(1, rows.getLong("target_count"));
        assertEquals(0, rows.getLong("success_count"));
        assertEquals(1, rows.getLong("failure_count"));
        assertEquals(0, rows.getLong("byte_count"));
        assertEquals("COMMAND_FAILURE", rows.getString("error_code"));
        assertEquals("batch command failed", rows.getString("error_summary"));
      }
      assertFalse(rows.next());
    }
  }

  @Test
  void cfdb001ActualBothLatestFullRowsAreReadWithoutMutationAndLockIsMandatory() throws Exception {
    verify();
    try (var c = db.admin();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select"
                    + " count(*),sum(target_count),sum(success_count),sum(failure_count),sum(byte_count)"
                    + " from schubert.batch_runs where status='FAILED' and"
                    + " error_code='COMMAND_FAILURE' and error_summary='batch command failed'")) {
      assertTrue(r.next());
      assertEquals(2, r.getLong(1));
      assertEquals(2, r.getLong(2));
      assertEquals(0, r.getLong(3));
      assertEquals(2, r.getLong(4));
      assertEquals(0, r.getLong(5));
      assertFalse(r.next());
    }
    try (var c = db.open("schubert_batch")) {
      assertThrows(
          BatchRepositoryException.class, () -> snapshot().verifyLatest(c, () -> 10_000_000_000L));
    }
    assertThrows(NullPointerException.class, () -> snapshot().verifyLatest(null, () -> 1));
    try (var c = CleanupStepFixture.locked(db, false)) {
      assertThrows(NullPointerException.class, () -> snapshot().verifyLatest(c, null));
      var failure = new IOException("independent owner fault");
      assertSame(
          failure,
          assertThrows(
              IOException.class,
              () ->
                  snapshot()
                      .verifyLatest(
                          c,
                          () -> {
                            throw failure;
                          })));
      c.rollback();
    }
  }

  @Test
  void cfdb002LatestIdentityAndEveryTerminalColumnRejectMismatch() throws Exception {
    for (String assignment :
        List.of(
            "id=70",
            "attempt=5",
            "started_at='2026-09-13T02:00:01Z'",
            "ended_at='2026-09-13T02:00:04Z'",
            "status='SUCCESS',success_count=1,failure_count=0,error_code=null,error_summary=null",
            "target_count=2",
            "success_count=1,target_count=2",
            "failure_count=0",
            "byte_count=1",
            "error_code='ABANDONED',error_summary='previous same-run attempt abandoned'")) {
      seed();
      try (var c = db.admin();
          var s = c.createStatement()) {
        s.execute("update schubert.batch_runs set " + assignment + " where id=7");
      }
      assertThrows(IOException.class, this::verify);
    }
    seed();
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute(
          "insert into schubert.batch_runs(id,step,run_id,business_date,attempt,started_at,status)"
              + " values(9,'BACKUP_DB','12345678-9abc-def0-8123-456789abcdef','2026-09-13',5,'2026-09-13T02:00:04Z','RUNNING')");
    }
    assertThrows(IOException.class, this::verify);
    seed();
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute("delete from schubert.batch_runs where id=8");
    }
    assertThrows(IOException.class, this::verify);
  }

  @Test
  void cfdb003SnapshotInvariantUsesActualPairNotAFrameCertificate() {
    var value = snapshot();
    assertThrows(
        NullPointerException.class,
        () -> new BackupFailureSnapshot(null, value.configuration(), END));
    assertThrows(
        NullPointerException.class, () -> new BackupFailureSnapshot(value.database(), null, END));
    assertThrows(
        NullPointerException.class,
        () -> new BackupFailureSnapshot(value.database(), value.configuration(), null));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new BackupFailureSnapshot(
                value.database(), value.configuration(), START.minusSeconds(1)));
    for (var handle :
        List.of(
            new BatchStepAttempt(7, RUN, BatchStep.BACKUP_CONFIG, 4, START, false),
            new BatchStepAttempt(8, RUN, BatchStep.CLEAN_LOG, 4, START, false),
            new BatchStepAttempt(8, RUN, BatchStep.BACKUP_CONFIG, 4, START, true),
            new BatchStepAttempt(8, RUN, BatchStep.BACKUP_CONFIG, 4, START.plusSeconds(1), false)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new BackupFailureSnapshot(value.database(), handle, END));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new BackupFailureSnapshot(
                new BatchStepAttempt(7, RUN, BatchStep.BACKUP_CONFIG, 4, START, false),
                value.configuration(),
                END));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new BackupFailureSnapshot(
                new BatchStepAttempt(7, RUN, BatchStep.BACKUP_DB, 4, START, true),
                value.configuration(),
                END));
  }
}
