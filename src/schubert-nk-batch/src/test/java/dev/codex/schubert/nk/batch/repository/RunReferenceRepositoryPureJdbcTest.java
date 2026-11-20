package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
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
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** NK-DAT-001; DAT009/OPS009/UI251/SS332; RRF-PURE-001..009; no database or native calls. */
final class RunReferenceRepositoryPureJdbcTest {
  private static final String STATEMENT_CLOSE = "statement.close";
  private static final String ROW_GET_OBJECT = "row.getObject";
  private static final String ROW_NEXT = "row.next";
  private static final String STATEMENT_BIND = "statement.setObject";
  private static final String ROW_CLOSE = "row.close";
  private static final String CLOSE = "close";
  private static final UUID ID = UUID.fromString("12345678-9abc-def0-8123-456789abcdef");
  private static final BatchRun RUN =
      new BatchRun(ID, Instant.parse("2026-09-12T15:00:00.123456Z"));
  private static final String SQL =
      "select has_batch_history,has_inbox_progress,has_log_progress,identity_consistent"
          + " from schubert.maintenance_read_run_references(?,?)";
  private static final List<String> COLUMNS =
      List.of("has_batch_history", "has_inbox_progress", "has_log_progress", "identity_consistent");

  @Test
  void literalSqlAndUtcBindings() {
    for (String literal :
        List.of(
            "0001-01-01T00:00:00Z",
            "1582-10-05T00:00:00Z",
            "2026-09-12T15:00:00.123456Z",
            "9999-12-31T23:59:59.999999Z")) {
      var fixture = new Fixture();
      var result = fixture.read(new BatchRun(ID, Instant.parse(literal)));
      assertFalse(result.hasBatchHistory());
      assertFalse(result.hasInboxProgress());
      assertFalse(result.hasLogProgress());
      assertTrue(result.identityConsistent());
      assertEquals(SQL, fixture.sql);
      assertEquals(5, fixture.timeout);
      assertSame(ID, fixture.parameters.get(1));
      assertEquals(OffsetDateTime.parse(literal), fixture.parameters.get(2));
      assertEquals(
          List.of(
              "connection.getAutoCommit",
              "connection.isReadOnly",
              "connection.getTransactionIsolation",
              "connection.prepareStatement",
              "statement.setQueryTimeout",
              STATEMENT_BIND,
              STATEMENT_BIND,
              "statement.executeQuery",
              ROW_NEXT,
              ROW_GET_OBJECT,
              ROW_GET_OBJECT,
              ROW_GET_OBJECT,
              ROW_GET_OBJECT,
              ROW_NEXT,
              ROW_CLOSE,
              STATEMENT_CLOSE),
          fixture.events);
      fixture.closed();
    }
  }

  @Test
  void independentBooleanProjections() {
    for (int mask = 1; mask < 16; mask++) {
      var fixture = new Fixture();
      for (int bit = 0; bit < 4; bit++) fixture.values[bit] = (mask & (1 << bit)) != 0;
      var actual = fixture.read(RUN);
      assertEquals((mask & 1) != 0, actual.hasBatchHistory());
      assertEquals((mask & 2) != 0, actual.hasInboxProgress());
      assertEquals((mask & 4) != 0, actual.hasLogProgress());
      assertEquals((mask & 8) != 0, actual.identityConsistent());
      assertEquals((mask & 7) != 0, actual.anyReference());
      assertEquals("RunReferences[observation=<redacted>]", actual.toString());
      fixture.closed();
    }
  }

  @Test
  void nullTransactionAndInterruptContracts() {
    assertThrows(NullPointerException.class, () -> new RunReferenceRepository(null));
    var fixture = new Fixture();
    assertThrows(NullPointerException.class, () -> fixture.read(null));
    assertTrue(fixture.events.isEmpty());
    for (int mode = 0; mode < 3; mode++) {
      var invalid = new Fixture();
      if (mode == 0) invalid.autoCommit = true;
      if (mode == 1) invalid.readOnly = true;
      if (mode == 2) invalid.isolation = Connection.TRANSACTION_SERIALIZABLE;
      redacted(() -> invalid.read(RUN));
      assertFalse(invalid.statementAcquired);
      invalid.closed();
    }
    try {
      Thread.currentThread().interrupt();
      redacted(() -> fixture.read(RUN));
      assertTrue(Thread.currentThread().isInterrupted());
      assertTrue(fixture.events.isEmpty());
    } finally {
      Thread.interrupted();
    }
    var late = new Fixture();
    late.interruptOnRowClose = true;
    try {
      redacted(() -> late.read(RUN));
      assertTrue(Thread.currentThread().isInterrupted());
      late.closed();
    } finally {
      Thread.interrupted();
    }
  }

  @Test
  void missingProjectionAndCardinality() {
    for (int mode = 0; mode < 9; mode++) {
      var fixture = new Fixture();
      if (mode == 0) fixture.nullStatement = true;
      if (mode == 1) fixture.nullRow = true;
      if (mode == 2) fixture.rowCount = 0;
      if (mode == 3) fixture.rowCount = 2;
      if (mode == 4) fixture.values = new Boolean[] {false, false, false, false};
      if (mode >= 5) fixture.values[mode - 5] = null;
      redacted(() -> fixture.read(RUN));
      fixture.closed();
    }
  }

  @Test
  void everySqlFailurePositionClosesOwnedResources() {
    for (Position position : positions()) {
      var fixture = new Fixture();
      fixture.fail(position.name(), position.occurrence(), new SQLException("provider detail"));
      redacted(() -> fixture.read(RUN));
      assertEquals(position.occurrence(), fixture.counts.get(position.name()));
      fixture.closed();
    }
  }

  @Test
  void uncheckedAndCloseFailurePrecedence() {
    for (Position position : positions()) {
      for (Throwable primary :
          List.of(new IllegalStateException("unchecked"), new AssertionError("fatal"))) {
        var fixture = new Fixture();
        fixture.fail(position.name(), position.occurrence(), primary);
        assertSame(primary, assertThrows(Throwable.class, () -> fixture.read(RUN)));
        fixture.closed();
      }
    }
    for (String closeScope : List.of(ROW_CLOSE, STATEMENT_CLOSE)) {
      for (int primaryKind = 0; primaryKind < 3; primaryKind++) {
        for (int secondaryKind = 0; secondaryKind < 3; secondaryKind++) {
          var fixture = new Fixture();
          Throwable primary = failure(primaryKind);
          Throwable secondary = failure(secondaryKind);
          fixture.fail(ROW_GET_OBJECT, 2, primary);
          fixture.fail(closeScope, 1, secondary);
          Throwable result = assertThrows(Throwable.class, () -> fixture.read(RUN));
          if (primaryKind == 0 && secondaryKind == 0) {
            assertRedacted(result);
          } else if (primaryKind == 0) {
            assertSame(secondary, result);
          } else {
            assertSame(primary, result);
            assertEquals(1, result.getSuppressed().length);
            assertRedacted(result.getSuppressed()[0]);
          }
          fixture.closed();
        }
      }
    }
    var both = new Fixture();
    var rowFatal = new AssertionError("first fatal");
    both.fail(ROW_CLOSE, 1, rowFatal);
    both.fail(STATEMENT_CLOSE, 1, new SQLException("secondary provider"));
    assertSame(rowFatal, assertThrows(AssertionError.class, () -> both.read(RUN)));
    assertEquals(1, rowFatal.getSuppressed().length);
    assertRedacted(rowFatal.getSuppressed()[0]);
    both.closed();
  }

  @Test
  void fatalProviderGraphIsNotDiscarded() {
    for (int edge = 0; edge < 3; edge++) {
      var fixture = new Fixture();
      var fatal = new AssertionError("fatal graph");
      var sql = new SQLException("provider detail");
      if (edge == 0) sql.initCause(fatal);
      if (edge == 1) sql.addSuppressed(fatal);
      if (edge == 2) sql.setNextException(new SQLException("next", fatal));
      fixture.fail(ROW_NEXT, 1, sql);
      assertSame(fatal, assertThrows(AssertionError.class, () -> fixture.read(RUN)));
      fixture.closed();
    }
  }

  @Test
  void combinedReadAndCloseSqlFailuresKeepFirstFatalAndReleaseBothResources() {
    var bodyFatal = new AssertionError("read");
    var rowFatal = new LinkageError("row close");
    var statementFatal = new AssertionError("statement close");
    record Expected(boolean fatalInRead, boolean fatalInRow, Error first, int redactedSuppressed) {}
    var scenarios =
        List.of(
            new Expected(true, true, bodyFatal, 1),
            new Expected(false, true, rowFatal, 1),
            new Expected(false, false, statementFatal, 0));
    for (Expected scenario : scenarios) {
      var fixture = new Fixture();
      var read = new SQLException("read provider");
      if (scenario.fatalInRead()) read.initCause(bodyFatal);
      var rowClose = new SQLException("row provider");
      if (scenario.fatalInRow()) rowClose.addSuppressed(rowFatal);
      var statementClose = new SQLException("statement provider");
      statementClose.setNextException(new SQLException("statement next", statementFatal));
      fixture.fail(ROW_GET_OBJECT, 2, read);
      fixture.fail(ROW_CLOSE, 1, rowClose);
      fixture.fail(STATEMENT_CLOSE, 1, statementClose);

      Error actual = assertThrows(Error.class, () -> fixture.read(RUN));
      assertSame(scenario.first(), actual);
      assertNull(actual.getCause());
      assertEquals(scenario.redactedSuppressed(), actual.getSuppressed().length);
      for (Throwable suppressed : actual.getSuppressed()) assertRedacted(suppressed);
      assertEquals(
          List.of(ROW_GET_OBJECT, ROW_CLOSE, STATEMENT_CLOSE),
          fixture.events.subList(fixture.events.size() - 3, fixture.events.size()));
      fixture.closed();
    }
  }

  @Test
  void independentConnectionsCanRunConcurrently() throws Exception {
    var executor = Executors.newVirtualThreadPerTaskExecutor();
    try {
      List<Future<Boolean>> results = new ArrayList<>();
      for (int index = 0; index < 32; index++) {
        results.add(
            executor.submit(
                () -> {
                  var fixture = new Fixture();
                  var result = fixture.read(RUN);
                  fixture.closed();
                  return result.identityConsistent() && !result.anyReference();
                }));
      }
      for (var result : results) assertTrue(result.get(10, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  private static List<Position> positions() {
    return List.of(
        new Position("connection.getAutoCommit", 1),
        new Position("connection.isReadOnly", 1),
        new Position("connection.getTransactionIsolation", 1),
        new Position("connection.prepareStatement", 1),
        new Position("statement.setQueryTimeout", 1),
        new Position(STATEMENT_BIND, 1),
        new Position(STATEMENT_BIND, 2),
        new Position("statement.executeQuery", 1),
        new Position(ROW_NEXT, 1),
        new Position(ROW_GET_OBJECT, 1),
        new Position(ROW_GET_OBJECT, 2),
        new Position(ROW_GET_OBJECT, 3),
        new Position(ROW_GET_OBJECT, 4),
        new Position(ROW_NEXT, 2),
        new Position(ROW_CLOSE, 1),
        new Position(STATEMENT_CLOSE, 1));
  }

  private static Throwable failure(int kind) {
    return switch (kind) {
      case 0 -> new SQLException("provider detail");
      case 1 -> new IllegalStateException("unchecked");
      default -> new AssertionError("fatal");
    };
  }

  private static void redacted(Runnable operation) {
    assertRedacted(assertThrows(BatchRepositoryException.class, operation::run));
  }

  private static void assertRedacted(Throwable failure) {
    assertEquals(BatchRepositoryException.class, failure.getClass());
    assertEquals("batch repository operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private record Position(String name, int occurrence) {}

  private static final class Fixture {
    final List<String> events = new ArrayList<>();
    final Map<String, Integer> counts = new HashMap<>();
    final Map<Position, Throwable> failures = new HashMap<>();
    final Map<Integer, Object> parameters = new HashMap<>();
    Boolean[] values = {false, false, false, true};
    boolean autoCommit;
    boolean readOnly;
    int isolation = Connection.TRANSACTION_READ_COMMITTED;
    int rowCount = 1;
    int rowIndex;
    boolean nullStatement;
    boolean nullRow;
    boolean statementAcquired;
    boolean rowAcquired;
    boolean interruptOnRowClose;
    int statementCloses;
    int rowCloses;
    String sql;
    int timeout;

    void fail(String name, int occurrence, Throwable failure) {
      failures.put(new Position(name, occurrence), failure);
    }

    void hit(String name) throws Throwable {
      events.add(name);
      int occurrence = counts.merge(name, 1, Integer::sum);
      Throwable failure = failures.get(new Position(name, occurrence));
      if (failure != null) throw failure;
    }

    RunReferences read(BatchRun run) {
      var connection =
          proxy(
              Connection.class,
              (name, args) -> {
                hit("connection." + name);
                return switch (name) {
                  case "getAutoCommit" -> autoCommit;
                  case "isReadOnly" -> readOnly;
                  case "getTransactionIsolation" -> isolation;
                  case "prepareStatement" -> {
                    sql = (String) args[0];
                    statementAcquired = !nullStatement;
                    yield nullStatement ? null : statement();
                  }
                  default -> throw new AssertionError("borrowed connection changed: " + name);
                };
              });
      return new RunReferenceRepository(connection).read(run);
    }

    PreparedStatement statement() {
      return proxy(
          PreparedStatement.class,
          (name, args) -> {
            if (name.equals(CLOSE)) statementCloses++;
            hit("statement." + name);
            return switch (name) {
              case "setQueryTimeout" -> {
                timeout = (Integer) args[0];
                yield null;
              }
              case "setObject" -> {
                parameters.put((Integer) args[0], args[1]);
                yield null;
              }
              case "executeQuery" -> {
                rowAcquired = !nullRow;
                yield nullRow ? null : row();
              }
              case CLOSE -> null;
              default -> throw new AssertionError("unexpected statement call: " + name);
            };
          });
    }

    ResultSet row() {
      return proxy(
          ResultSet.class,
          (name, args) -> {
            if (name.equals(CLOSE)) rowCloses++;
            hit("row." + name);
            return switch (name) {
              case "next" -> {
                rowIndex++;
                yield rowIndex <= rowCount;
              }
              case "getObject" -> {
                assertSame(Boolean.class, args[1]);
                int index = COLUMNS.indexOf((String) args[0]);
                assertTrue(index >= 0);
                yield values[index];
              }
              case CLOSE -> {
                if (interruptOnRowClose) Thread.currentThread().interrupt();
                yield null;
              }
              default -> throw new AssertionError("unexpected row call: " + name);
            };
          });
    }

    void closed() {
      assertEquals(statementAcquired ? 1 : 0, statementCloses);
      assertEquals(rowAcquired ? 1 : 0, rowCloses);
      assertFalse(events.contains("connection.close"));
      assertFalse(events.contains("connection.commit"));
      assertFalse(events.contains("connection.rollback"));
    }
  }

  @FunctionalInterface
  private interface Calls {
    Object invoke(String name, Object[] args) throws Throwable;
  }

  private static <T> T proxy(Class<T> type, Calls calls) {
    return type.cast(
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (ignored, method, args) ->
                calls.invoke(method.getName(), args == null ? new Object[0] : args)));
  }
}
