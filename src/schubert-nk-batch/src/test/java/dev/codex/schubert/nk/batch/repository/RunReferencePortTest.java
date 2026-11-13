package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** PT-BAT-RUNPORT001..008: borrowed JDBC ports; no real DB, lock, file, Root or backend. */
final class RunReferencePortTest {
  private static final String SQL =
      "select has_batch_history,has_inbox_progress,has_log_progress,identity_consistent"
          + " from schubert.maintenance_read_run_references(?,?)";
  private static final List<String> COLUMNS =
      List.of("has_batch_history", "has_inbox_progress", "has_log_progress", "identity_consistent");
  private static final String ENTRY_POINT = "entry";
  private static final String AUTO = "auto";
  private static final String READONLY = "readonly";
  private static final String ISOLATION = "isolation";
  private static final String PREPARE = "prepare";
  private static final String TIMEOUT = "timeout";
  private static final String BIND_ONE = "bind1";
  private static final String BIND_TWO = "bind2";
  private static final String QUERY = "query";
  private static final String FIRST_NEXT = "next1";
  private static final String SECOND_NEXT = "next2";
  private static final String ROW_CLOSE = "rowClose";
  private static final String STATEMENT_CLOSE = "statementClose";
  private static final String FIXED_DIAGNOSTIC = "batch repository operation failed";
  private static final BatchRun RUN =
      new BatchRun(new UUID(0, 1), Instant.parse("2026-11-05T00:00:00.123456Z"));

  @Test
  void literalSqlTimeoutBindingsAndOwnershipOrderMatchBorrowedParentContract() {
    Fixture fixture = new Fixture();
    var actual = new RunReferenceRepository(fixture.connection()).read(RUN);
    assertEquals(SQL, fixture.sql);
    assertEquals(5, fixture.timeout);
    assertEquals(
        Map.of(1, new UUID(0, 1), 2, OffsetDateTime.parse("2026-11-05T00:00:00.123456Z")),
        fixture.bindings);
    assertEquals(
        List.of(
            AUTO,
            READONLY,
            ISOLATION,
            PREPARE,
            TIMEOUT,
            BIND_ONE,
            BIND_TWO,
            QUERY,
            FIRST_NEXT,
            COLUMNS.get(0),
            COLUMNS.get(1),
            COLUMNS.get(2),
            COLUMNS.get(3),
            SECOND_NEXT,
            ROW_CLOSE,
            STATEMENT_CLOSE),
        fixture.events);
    assertEquals(false, actual.hasBatchHistory());
    assertEquals(false, actual.hasInboxProgress());
    assertEquals(false, actual.hasLogProgress());
    assertEquals(true, actual.identityConsistent());
    fixture.assertClosed(1, 1);
  }

  @Test
  void allSixteenProjectionTuplesKeepFourIndependentBooleansOrRejectOnlyInconsistentEmpty() {
    for (int bits = 0; bits < 16; bits++) {
      Fixture fixture = new Fixture();
      for (int column = 0; column < 4; column++)
        fixture.values[column] = (bits & (1 << column)) != 0;
      var repository = new RunReferenceRepository(fixture.connection());
      if (bits == 0) catalog(() -> repository.read(RUN));
      else {
        var actual = repository.read(RUN);
        assertEquals((bits & 1) != 0, actual.hasBatchHistory());
        assertEquals((bits & 2) != 0, actual.hasInboxProgress());
        assertEquals((bits & 4) != 0, actual.hasLogProgress());
        assertEquals((bits & 8) != 0, actual.identityConsistent());
      }
      fixture.assertClosed(1, 1);
    }
  }

  @Test
  void nullAndTransactionPreconditionsRejectBeforeAcquiringAnyOwnedResource() {
    assertThrows(NullPointerException.class, () -> new RunReferenceRepository(null));
    Fixture empty = new Fixture();
    assertThrows(
        NullPointerException.class,
        () -> new RunReferenceRepository(empty.connection()).read(null));
    assertTrue(empty.events.isEmpty());
    for (String invalid : List.of(AUTO, READONLY, ISOLATION)) {
      Fixture fixture = new Fixture();
      fixture.autoCommit = invalid.equals(AUTO);
      fixture.readOnly = invalid.equals(READONLY);
      fixture.isolation =
          invalid.equals(ISOLATION)
              ? Connection.TRANSACTION_SERIALIZABLE
              : Connection.TRANSACTION_READ_COMMITTED;
      catalog(() -> new RunReferenceRepository(fixture.connection()).read(RUN));
      assertNull(fixture.sql);
      fixture.assertClosed(0, 0);
    }
  }

  @Test
  void nullAcquisitionsMissingDuplicateRowsAndRequiredColumnsNeverBecomeDefaults() {
    for (String missing : List.of("statement", "row")) {
      Fixture fixture = new Fixture();
      fixture.missing = missing;
      catalog(() -> new RunReferenceRepository(fixture.connection()).read(RUN));
      fixture.assertClosed(missing.equals("statement") ? 0 : 1, 0);
    }
    for (int rows : new int[] {0, 2}) {
      Fixture fixture = new Fixture();
      fixture.rows = rows;
      catalog(() -> new RunReferenceRepository(fixture.connection()).read(RUN));
      fixture.assertClosed(1, 1);
    }
    for (int column = 0; column < 4; column++) {
      Fixture fixture = new Fixture();
      fixture.values[column] = null;
      catalog(() -> new RunReferenceRepository(fixture.connection()).read(RUN));
      fixture.assertClosed(1, 1);
    }
  }

  @Test
  void eachProviderFailureHasFixedSqlOrOriginalUnknownIdentityAndAttemptsOwnedClose() {
    var points =
        new ArrayList<>(
            List.of(
                AUTO,
                READONLY,
                ISOLATION,
                PREPARE,
                TIMEOUT,
                BIND_ONE,
                BIND_TWO,
                QUERY,
                FIRST_NEXT,
                SECOND_NEXT,
                ROW_CLOSE,
                STATEMENT_CLOSE));
    points.addAll(COLUMNS);
    for (String point : points) {
      for (Throwable original : providerFailures()) {
        Fixture fixture = new Fixture();
        fixture.faults = Map.of(point, original);
        expected(original, () -> new RunReferenceRepository(fixture.connection()).read(RUN));
        boolean acquiredStatement = !List.of(AUTO, READONLY, ISOLATION, PREPARE).contains(point);
        boolean acquiredRow =
            acquiredStatement && !List.of(TIMEOUT, BIND_ONE, BIND_TWO, QUERY).contains(point);
        fixture.assertClosed(acquiredStatement ? 1 : 0, acquiredRow ? 1 : 0);
      }
    }
  }

  @Test
  void declaredSqlUnknownCleanupSelectionUsesPrimaryIdentityAndFixedSecondaryOnly() {
    for (String closing : List.of(ROW_CLOSE, STATEMENT_CLOSE)) {
      for (int kind = 0; kind < 3; kind++) {
        for (Throwable secondary : failures()) {
          Throwable primary = failures().get(kind);
          Fixture fixture = new Fixture();
          fixture.faults = Map.of(FIRST_NEXT, primary, closing, secondary);
          Throwable selected =
              primary instanceof SQLException && !(secondary instanceof SQLException)
                  ? secondary
                  : primary;
          expected(selected, () -> new RunReferenceRepository(fixture.connection()).read(RUN));
          fixture.assertClosed(1, 1);
          if (!(primary instanceof SQLException)) {
            assertEquals(1, primary.getSuppressed().length);
            assertEquals(BatchRepositoryException.class, primary.getSuppressed()[0].getClass());
            assertEquals(FIXED_DIAGNOSTIC, primary.getSuppressed()[0].getMessage());
          }
        }
      }
    }
    SQLException same = new SQLException("own same SQL");
    Fixture identical = new Fixture();
    identical.faults = Map.of(FIRST_NEXT, same, ROW_CLOSE, same);
    catalog(() -> new RunReferenceRepository(identical.connection()).read(RUN));
    assertEquals(0, same.getSuppressed().length);
    var disabled = new NoSuppression();
    Fixture suppressed = new Fixture();
    suppressed.faults =
        Map.of(FIRST_NEXT, disabled, ROW_CLOSE, new SQLException("own closing SQL"));
    assertSame(
        disabled,
        assertThrows(
            NoSuppression.class,
            () -> new RunReferenceRepository(suppressed.connection()).read(RUN)));
    assertEquals(0, disabled.getSuppressed().length);
  }

  @Test
  void ownWorkerInterruptionAtEntryOrAfterCleanupNeverLeaksResultOrInterruptsCaller()
      throws Exception {
    assertEquals(false, Thread.currentThread().isInterrupted());
    for (String phase : List.of(ENTRY_POINT, ROW_CLOSE, STATEMENT_CLOSE)) {
      Fixture fixture = new Fixture();
      if (!phase.equals(ENTRY_POINT)) fixture.interruptAt = phase;
      var worker = Executors.newSingleThreadExecutor();
      try {
        var task =
            worker.submit(
                () -> {
                  if (phase.equals(ENTRY_POINT)) Thread.currentThread().interrupt();
                  try {
                    catalog(() -> new RunReferenceRepository(fixture.connection()).read(RUN));
                    return Thread.currentThread().isInterrupted();
                  } finally {
                    Thread.interrupted();
                  }
                });
        assertEquals(true, task.get(5, TimeUnit.SECONDS));
      } finally {
        worker.shutdownNow();
        assertTrue(worker.awaitTermination(5, TimeUnit.SECONDS));
      }
      fixture.assertClosed(phase.equals(ENTRY_POINT) ? 0 : 1, phase.equals(ENTRY_POINT) ? 0 : 1);
    }
    assertEquals(false, Thread.currentThread().isInterrupted());
  }

  @Test
  void independentBorrowedParentsNeverShareBindingsOrReturnedProjection() throws Exception {
    Fixture one = new Fixture();
    Fixture two = new Fixture();
    two.values[0] = true;
    BatchRun other = new BatchRun(new UUID(0, 2), RUN.cutoff());
    var workers = Executors.newFixedThreadPool(2);
    try {
      var first = workers.submit(() -> new RunReferenceRepository(one.connection()).read(RUN));
      var second = workers.submit(() -> new RunReferenceRepository(two.connection()).read(other));
      assertEquals(false, first.get(5, TimeUnit.SECONDS).hasBatchHistory());
      assertEquals(true, second.get(5, TimeUnit.SECONDS).hasBatchHistory());
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(5, TimeUnit.SECONDS));
    }
    assertEquals(new UUID(0, 1), one.bindings.get(1));
    assertEquals(new UUID(0, 2), two.bindings.get(1));
    one.assertClosed(1, 1);
    two.assertClosed(1, 1);
  }

  // RUNPORT009-BEGIN: pure primitive projection, no database/FS fixture.
  @Test
  void literalProjectionOrAndRedactedDisplayAreIndependentOfDatabaseSetup() {
    for (int bits = 0; bits < 16; bits++) {
      boolean history = (bits & 1) != 0;
      boolean inbox = (bits & 2) != 0;
      boolean log = (bits & 4) != 0;
      boolean consistent = (bits & 8) != 0;
      if (bits == 0) {
        assertThrows(
            IllegalArgumentException.class,
            () -> new RunReferences(history, inbox, log, consistent));
      } else {
        var value = new RunReferences(history, inbox, log, consistent);
        assertEquals(history, value.hasBatchHistory());
        assertEquals(inbox, value.hasInboxProgress());
        assertEquals(log, value.hasLogProgress());
        assertEquals(consistent, value.identityConsistent());
        assertEquals((bits & 7) != 0, value.anyReference());
        assertEquals("RunReferences[observation=<redacted>]", value.toString());
      }
    }
  }

  // RUNPORT009-END

  /** RUNPORT010/BUG2775: fixed provider-point table and independent fatal graph identities. */
  @Test
  void knownSqlFatalGraphsNeverBecomeFixedRepositoryFailures() {
    var points =
        new ArrayList<>(
            List.of(
                AUTO,
                READONLY,
                ISOLATION,
                PREPARE,
                TIMEOUT,
                BIND_ONE,
                BIND_TWO,
                QUERY,
                FIRST_NEXT,
                SECOND_NEXT,
                ROW_CLOSE,
                STATEMENT_CLOSE));
    points.addAll(COLUMNS);
    assertEquals(16, points.size());
    for (String point : points) {
      for (int graph = 0; graph < 3; graph++) {
        Fixture fixture = new Fixture();
        var marker = new AssertionError("own fatal provider marker");
        var provider = new SQLException("own declared provider fault");
        switch (graph) {
          case 0 -> provider.initCause(marker);
          case 1 -> provider.addSuppressed(marker);
          default -> {
            var cycle = new IllegalStateException("own cyclic provider graph");
            provider.initCause(cycle);
            cycle.initCause(provider);
            cycle.addSuppressed(marker);
          }
        }
        fixture.faults = Map.of(point, provider);
        assertSame(
            marker,
            assertThrows(
                AssertionError.class,
                () -> new RunReferenceRepository(fixture.connection()).read(RUN)),
            point);
        assertEquals(0, marker.getSuppressed().length);
        boolean statement = !List.of(AUTO, READONLY, ISOLATION, PREPARE).contains(point);
        boolean row = statement && !List.of(TIMEOUT, BIND_ONE, BIND_TWO, QUERY).contains(point);
        fixture.assertClosed(statement ? 1 : 0, row ? 1 : 0);
      }
    }
  }

  private static List<Throwable> providerFailures() {
    var values = new ArrayList<>(failures());
    values.add(new IllegalArgumentException("own provider argument"));
    values.add(new NullPointerException("own provider null"));
    return values;
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("own SQL"),
        new IllegalStateException("own unknown"),
        new AssertionError("own Error"));
  }

  private static void expected(Throwable failure, Executable action) {
    if (failure instanceof SQLException) catalog(action);
    else assertSame(failure, assertThrows(failure.getClass(), action));
  }

  private static void catalog(Executable action) {
    var actual = assertThrows(BatchRepositoryException.class, action);
    assertEquals(FIXED_DIAGNOSTIC, actual.getMessage());
    assertNull(actual.getCause());
    assertEquals(0, actual.getSuppressed().length);
  }

  private static final class NoSuppression extends RuntimeException {
    private static final long serialVersionUID = 1L;

    NoSuppression() {
      super("own suppression-disabled", null, false, false);
    }
  }

  private static final class Fixture {
    final Boolean[] values = {false, false, false, true};
    final List<String> events = new ArrayList<>();
    final Map<Integer, Object> bindings = new HashMap<>();
    Map<String, Throwable> faults = Map.of();
    boolean autoCommit;
    boolean readOnly;
    int isolation = Connection.TRANSACTION_READ_COMMITTED;
    String missing = "none";
    String interruptAt = "none";
    String sql;
    int timeout;
    int rows = 1;
    int nextCalls;
    int statementCloses;
    int rowCloses;

    void event(String point) throws Throwable {
      events.add(point);
      if (point.equals(interruptAt)) Thread.currentThread().interrupt();
      Throwable failure = faults.get(point);
      if (failure != null) throw failure;
    }

    void assertClosed(int statements, int rowCount) {
      assertEquals(statements, statementCloses);
      assertEquals(rowCount, rowCloses);
    }

    Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                return switch (method.getName()) {
                  case "getAutoCommit" -> {
                    event(AUTO);
                    yield autoCommit;
                  }
                  case "isReadOnly" -> {
                    event(READONLY);
                    yield readOnly;
                  }
                  case "getTransactionIsolation" -> {
                    event(ISOLATION);
                    yield isolation;
                  }
                  case "prepareStatement" -> {
                    sql = (String) args[0];
                    event(PREPARE);
                    yield missing.equals("statement") ? null : statement();
                  }
                  default -> throw new AssertionError("borrowed connection ownership violated");
                };
              });
    }

    PreparedStatement statement() {
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) -> {
                return switch (method.getName()) {
                  case "setQueryTimeout" -> {
                    timeout = (Integer) args[0];
                    event(TIMEOUT);
                    yield null;
                  }
                  case "setObject" -> {
                    int index = (Integer) args[0];
                    bindings.put(index, args[1]);
                    event(index == 1 ? BIND_ONE : BIND_TWO);
                    yield null;
                  }
                  case "executeQuery" -> {
                    event(QUERY);
                    yield missing.equals("row") ? null : row();
                  }
                  case "close" -> {
                    statementCloses++;
                    event(STATEMENT_CLOSE);
                    yield null;
                  }
                  default -> throw new AssertionError("unexpected owned statement operation");
                };
              });
    }

    ResultSet row() {
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                return switch (method.getName()) {
                  case "next" -> {
                    nextCalls++;
                    event(nextCalls == 1 ? FIRST_NEXT : SECOND_NEXT);
                    yield nextCalls <= rows;
                  }
                  case "getObject" -> {
                    String column = (String) args[0];
                    assertEquals(Boolean.class, args[1]);
                    event(column);
                    yield values[COLUMNS.indexOf(column)];
                  }
                  case "close" -> {
                    rowCloses++;
                    event(ROW_CLOSE);
                    yield null;
                  }
                  default -> throw new AssertionError("unexpected owned row operation");
                };
              });
    }
  }
}
