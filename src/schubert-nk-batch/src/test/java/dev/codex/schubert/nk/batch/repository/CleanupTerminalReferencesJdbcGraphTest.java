package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.IntUnaryOperator;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-F02-CTERM-REF-001/002, SS332 and SSC-461. */
@Timeout(5)
final class CleanupTerminalReferencesJdbcGraphTest {
  private static final Instant CUTOFF = Instant.parse("2026-10-01T21:00:00Z");
  private static final Instant STARTED = Instant.parse("2026-10-01T21:00:01Z");
  private static final Instant ENDED = Instant.parse("2026-10-01T21:00:02Z");
  private static final BatchRun RUN = new BatchRun(new UUID(0, 7), CUTOFF);
  private static final UUID PRIOR_RUN_ID = new UUID(0, 4);
  private static final List<BatchStep> EXPECTED_STEPS =
      List.of(
          BatchStep.CLEAN_NOTIFICATION,
          BatchStep.CLEAN_QUESTION,
          BatchStep.CLEAN_SESSION,
          BatchStep.CLEAN_INBOX_OUTBOX,
          BatchStep.CLEAN_LOG,
          BatchStep.CLEAN_BATCH_RUN,
          BatchStep.CLEAN_TRANSFER);
  private static final String SUCCESS_REFERENCE_SQL =
      "select id,run_id,business_date,step,attempt,started_at,ended_at,status,"
          + "target_count,success_count,failure_count,byte_count,error_code,error_summary"
          + " from schubert.batch_runs where business_date=? and step=?"
          + " and status='SUCCESS' and attempt<? order by attempt desc limit 2";
  private static final String TERMINAL_READ_SQL =
      "select distinct on(step) id,run_id,business_date,step,attempt,started_at,ended_at,status,"
          + "target_count,success_count,failure_count,byte_count,error_code,error_summary"
          + " from schubert.batch_runs where run_id=? and business_date=? and step in"
          + " ('CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX',"
          + "'CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER') order by step,attempt desc";
  private static final String IDENTITY_CHECK = "identity";
  private static final String IDENTITY_ROWS_CLOSE = "result close";
  private static final String IDENTITY_STATEMENT_CLOSE = "statement close";
  private static final String CLOSE_METHOD = "close";
  private static final String NEXT_METHOD = "next";
  private static final String TERMINAL_QUERY = "terminal query";
  private static final String TERMINAL_TIMEOUT = "terminal timeout";
  private static final String TERMINAL_RUN = "terminal run";
  private static final String TERMINAL_DATE = "terminal date";
  private static final String TERMINAL_ROWS_CLOSE = "terminal rows close";
  private static final String TERMINAL_CLOSE = "terminal close";
  private static final List<String> EXPECTED_CALLS =
      List.of(IDENTITY_CHECK, IDENTITY_ROWS_CLOSE, IDENTITY_STATEMENT_CLOSE, "prior success");
  private static final String PRIOR_RESOLVE = "resolve independent prior owner";
  private static final String PRIOR_ROW_CLOSE = "prior row close";
  private static final String PRIOR_STATEMENT_CLOSE = "prior statement close";
  private static final List<String> EXPECTED_READ_CALLS =
      List.of(
          IDENTITY_CHECK,
          IDENTITY_ROWS_CLOSE,
          IDENTITY_STATEMENT_CLOSE,
          TERMINAL_QUERY,
          TERMINAL_TIMEOUT,
          TERMINAL_RUN,
          TERMINAL_DATE,
          TERMINAL_CLOSE);
  private static final List<String> EXPECTED_ACQUIRED_CLOSE_CALLS =
      List.of(
          IDENTITY_CHECK,
          IDENTITY_ROWS_CLOSE,
          IDENTITY_STATEMENT_CLOSE,
          TERMINAL_QUERY,
          TERMINAL_TIMEOUT,
          TERMINAL_RUN,
          TERMINAL_DATE,
          TERMINAL_ROWS_CLOSE,
          TERMINAL_CLOSE);
  private static final List<String> EXPECTED_SUCCESS_READ_CALLS =
      List.of(
          IDENTITY_CHECK,
          IDENTITY_ROWS_CLOSE,
          IDENTITY_STATEMENT_CLOSE,
          TERMINAL_QUERY,
          TERMINAL_TIMEOUT,
          TERMINAL_RUN,
          TERMINAL_DATE,
          TERMINAL_ROWS_CLOSE,
          TERMINAL_CLOSE,
          IDENTITY_CHECK,
          IDENTITY_ROWS_CLOSE,
          IDENTITY_STATEMENT_CLOSE);

  @Test
  void successfulReferenceQueryPreservesTheOriginalFatalCause() {
    var fatal = new LinkageError("public reference fixture");
    var provider = new SQLException("public primary fixture");
    provider.setNextException(new SQLException("public next fixture", fatal));
    var calls = new ArrayList<String>();
    var repository =
        new CleanupTerminalRepository(connection(provider, calls), () -> 5_000_000_000L);
    assertSame(fatal, assertThrows(LinkageError.class, () -> repository.references(snapshot())));
    assertEquals(EXPECTED_CALLS, calls);
  }

  @Test
  void ordinaryProviderErrorIsCataloguedAndTheBorrowedConnectionStaysOpen() {
    var calls = new ArrayList<String>();
    var connection = connection(new SQLException("public provider diagnostic"), calls);
    var repository = new CleanupTerminalRepository(connection, () -> 5_000_000_000L);
    var failure =
        assertThrows(BatchRepositoryException.class, () -> repository.references(snapshot()));
    assertFixedDiagnostic(failure);
    assertEquals(EXPECTED_CALLS, calls);
  }

  /** PT-F02-CTERM-REF-003. */
  @Test
  void checkedPriorLookupFailureRemainsPrimaryWhenResultCloseThrowsSql() {
    assertCheckedLookupFailure(
        () -> {
          throw new SQLException("independent prior row close failure");
        },
        () -> {});
  }

  /** PT-F02-CTERM-REF-004. */
  @Test
  void checkedPriorLookupFailureRemainsPrimaryWhenStatementCloseThrowsError() {
    assertCheckedLookupFailure(
        () -> {},
        () -> {
          throw new LinkageError("independent prior statement close error");
        });
  }

  private static void assertCheckedLookupFailure(CloseAction rowClose, CloseAction statementClose) {
    var calls = new ArrayList<String>();
    var primary = new IOException("independent prior lookup failure");
    var connection =
        connection(
            SUCCESS_REFERENCE_SQL,
            () -> priorLookupStatement(calls, rowClose, statementClose),
            calls);
    var repository = new CleanupTerminalRepository(connection, () -> 5_000_000_000L);

    var observed =
        assertThrows(
            IOException.class,
            () ->
                repository.references(
                    snapshot(),
                    (id, instant) -> {
                      assertEquals(PRIOR_RUN_ID, id);
                      assertEquals(STARTED, instant);
                      calls.add(PRIOR_RESOLVE);
                      throw primary;
                    }));

    assertSame(primary, observed);
    assertNull(observed.getCause());
    var suppressed = observed.getSuppressed();
    assertEquals(1, suppressed.length);
    assertFixedDiagnostic(assertInstanceOf(BatchRepositoryException.class, suppressed[0]));
    assertEquals(
        List.of(
            IDENTITY_CHECK,
            IDENTITY_ROWS_CLOSE,
            IDENTITY_STATEMENT_CLOSE,
            PRIOR_RESOLVE,
            PRIOR_ROW_CLOSE,
            PRIOR_STATEMENT_CLOSE),
        calls);
  }

  /** PT-F02-CTERM-READ001. */
  @Test
  void ordinaryTerminalReadPreservesTheOriginalFatalErrorAfterClosingItsStatement() {
    var fatal = new LinkageError("public terminal read fixture");
    var provider = new SQLException("public terminal diagnostic");
    provider.setNextException(new SQLException("public terminal next fixture", fatal));
    var calls = new ArrayList<String>();
    var repository =
        new CleanupTerminalRepository(terminalConnection(provider, calls), () -> 5_000_000_000L);

    assertSame(fatal, assertThrows(LinkageError.class, () -> repository.read(RUN, STARTED)));
    assertEquals(EXPECTED_READ_CALLS, calls);
  }

  /** PT-F02-CTERM-READ002. */
  @Test
  void ordinaryTerminalReadReturnsTheFixedDiagnosticWithoutClosingTheBorrowedConnection() {
    var calls = new ArrayList<String>();
    var provider = new SQLException("public ordinary read fixture");
    var repository =
        new CleanupTerminalRepository(terminalConnection(provider, calls), () -> 5_000_000_000L);

    assertFixedDiagnostic(
        assertThrows(BatchRepositoryException.class, () -> repository.read(RUN, STARTED)));
    assertEquals(EXPECTED_READ_CALLS, calls);
  }

  /** PT-F02-CTERM-READ003. */
  @Test
  void ordinaryTerminalReadProjectsTheSevenSuccessfulRowsInFixedOrder() {
    var calls = new ArrayList<String>();
    var repository =
        new CleanupTerminalRepository(
            terminalConnection(() -> successfulTerminalRows(calls), calls), () -> 5_000_000_000L);

    var snapshot = repository.read(RUN, ENDED);

    assertEquals(
        EXPECTED_STEPS, snapshot.entries().stream().map(entry -> entry.attempt().step()).toList());
    assertEquals(
        List.of(90L, 91L, 92L, 93L, 94L, 95L, 96L),
        snapshot.entries().stream().map(entry -> entry.attempt().id()).toList());
    assertEquals(0, snapshot.exitCode());
    for (var entry : snapshot.entries()) {
      assertEquals(STARTED, entry.attempt().startedAt());
      assertEquals(ENDED, entry.endedAt());
      assertEquals(BatchStepResult.Status.SUCCESS, entry.result().status());
      assertEquals(2L, entry.result().success());
      assertEquals(0L, entry.result().failure());
      assertTrue(entry.progressSeal().isEmpty());
    }
    assertEquals(EXPECTED_SUCCESS_READ_CALLS, calls);
  }

  /** PT-F02-CTERM-READ004. */
  @Test
  void ordinaryTerminalReadKeepsRuntimePrimaryAndRecordsTwoSanitizedCloseFailures() {
    var calls = new ArrayList<String>();
    var primary = new IllegalStateException("independent row failure");
    var repository =
        new CleanupTerminalRepository(
            terminalConnection(
                () ->
                    terminalRows(
                        calls,
                        () -> {
                          throw primary;
                        },
                        () -> {
                          throw new SQLException("independent result close detail");
                        }),
                calls,
                () -> {
                  throw new SQLException("independent statement close detail");
                }),
            () -> 5_000_000_000L);

    assertSame(
        primary, assertThrows(IllegalStateException.class, () -> repository.read(RUN, ENDED)));
    var suppressed = primary.getSuppressed();
    assertEquals(2, suppressed.length);
    assertFixedDiagnostic(assertInstanceOf(BatchRepositoryException.class, suppressed[0]));
    assertFixedDiagnostic(assertInstanceOf(BatchRepositoryException.class, suppressed[1]));
    assertNotSame(suppressed[0], suppressed[1]);
    assertEquals(EXPECTED_ACQUIRED_CLOSE_CALLS, calls);
  }

  /** PT-F02-CTERM-READ005. */
  @Test
  void ordinaryTerminalReadRejectsAnOtherwiseCompleteReadWhenResultCloseFails() {
    var calls = new ArrayList<String>();
    var repository =
        new CleanupTerminalRepository(
            terminalConnection(
                () ->
                    successfulTerminalRows(
                        calls,
                        () -> {
                          throw new SQLException("independent result close failure");
                        }),
                calls),
            () -> 5_000_000_000L);

    assertFixedDiagnostic(
        assertThrows(BatchRepositoryException.class, () -> repository.read(RUN, ENDED)));
    assertEquals(EXPECTED_ACQUIRED_CLOSE_CALLS, calls);
  }

  /** PT-F02-CTERM-READ006. */
  @Test
  void ordinaryTerminalReadKeepsAnOriginalCloseErrorOverTheKnownSqlFailure() {
    var calls = new ArrayList<String>();
    var closeError = new LinkageError("independent close error");
    var repository =
        new CleanupTerminalRepository(
            terminalConnection(
                () ->
                    terminalRows(
                        calls,
                        () -> {
                          throw new SQLException("independent row failure");
                        },
                        () -> {
                          throw closeError;
                        }),
                calls),
            () -> 5_000_000_000L);

    assertSame(closeError, assertThrows(LinkageError.class, () -> repository.read(RUN, ENDED)));
    assertEquals(EXPECTED_ACQUIRED_CLOSE_CALLS, calls);
  }

  /** PT-F02-CTERM-READ007. */
  @Test
  void ordinaryTerminalReadRejectsAnAbsentStatementWithoutClosingUnownedHandles() {
    var calls = new ArrayList<String>();
    var repository =
        new CleanupTerminalRepository(
            connection(
                TERMINAL_READ_SQL,
                () -> {
                  calls.add(TERMINAL_QUERY);
                  return null;
                },
                calls),
            () -> 5_000_000_000L);

    assertFixedDiagnostic(
        assertThrows(BatchRepositoryException.class, () -> repository.read(RUN, ENDED)));
    assertEquals(
        List.of(IDENTITY_CHECK, IDENTITY_ROWS_CLOSE, IDENTITY_STATEMENT_CLOSE, TERMINAL_QUERY),
        calls);
  }

  /** PT-F02-CTERM-READ008. */
  @Test
  void ordinaryTerminalReadRejectsAbsentRowsAndClosesOnlyItsStatement() {
    var calls = new ArrayList<String>();
    var repository =
        new CleanupTerminalRepository(terminalConnection(() -> null, calls), () -> 5_000_000_000L);

    assertFixedDiagnostic(
        assertThrows(BatchRepositoryException.class, () -> repository.read(RUN, ENDED)));
    assertEquals(EXPECTED_READ_CALLS, calls);
  }

  /** PT-F02-CTERM-READ009. */
  @Test
  void ordinaryTerminalReadRejectsARepeatedStepAndClosesBothOwnedHandles() {
    var calls = new ArrayList<String>();
    var highestProjectedRow = new AtomicInteger(-1);
    var repository =
        new CleanupTerminalRepository(
            terminalConnection(
                () ->
                    projectedTerminalRows(
                        calls,
                        () -> {},
                        index -> {
                          highestProjectedRow.accumulateAndGet(index, Math::max);
                          return index == 1 ? 0 : index;
                        }),
                calls),
            () -> 5_000_000_000L);

    assertFixedDiagnostic(
        assertThrows(BatchRepositoryException.class, () -> repository.read(RUN, ENDED)));
    assertEquals(1, highestProjectedRow.get());
    assertEquals(EXPECTED_ACQUIRED_CLOSE_CALLS, calls);
  }

  private static void assertFixedDiagnostic(BatchRepositoryException failure) {
    assertEquals("batch repository operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static CleanupTerminalRepository.Snapshot snapshot() {
    var entries = new ArrayList<CleanupTerminalRepository.Entry>();
    for (int index = 0; index < EXPECTED_STEPS.size(); index++) {
      boolean skipped = index == 0;
      var attempt =
          new BatchStepAttempt(index + 1, RUN, EXPECTED_STEPS.get(index), 2, STARTED, skipped);
      var status = skipped ? BatchStepResult.Status.SKIPPED : BatchStepResult.Status.SUCCESS;
      var reason =
          skipped ? BatchStepResult.Reason.ALREADY_SUCCESSFUL : BatchStepResult.Reason.NONE;
      var result = new BatchStepResult(status, 0, 0, 0, 0, reason);
      entries.add(new CleanupTerminalRepository.Entry(attempt, STARTED, result));
    }
    return new CleanupTerminalRepository.Snapshot(entries);
  }

  private static Connection connection(SQLException provider, List<String> calls) {
    return connection(
        SUCCESS_REFERENCE_SQL,
        () -> {
          calls.add("prior success");
          throw provider;
        },
        calls);
  }

  private static Connection terminalConnection(SQLException provider, List<String> calls) {
    return terminalConnection(
        () -> {
          throw provider;
        },
        calls);
  }

  private static Connection terminalConnection(RowsSupplier rows, List<String> calls) {
    return terminalConnection(rows, calls, () -> {});
  }

  private static Connection terminalConnection(
      RowsSupplier rows, List<String> calls, CloseAction closeAction) {
    return connection(
        TERMINAL_READ_SQL,
        () -> {
          calls.add(TERMINAL_QUERY);
          return proxy(
              PreparedStatement.class,
              (unused, method, args) ->
                  switch (method.getName()) {
                    case "setQueryTimeout" -> {
                      assertEquals(5, args[0]);
                      calls.add(TERMINAL_TIMEOUT);
                      yield null;
                    }
                    case "setObject" -> {
                      switch ((int) args[0]) {
                        case 1 -> {
                          calls.add(TERMINAL_RUN);
                          assertEquals(new UUID(0, 7), args[1]);
                        }
                        case 2 -> {
                          calls.add(TERMINAL_DATE);
                          assertEquals(LocalDate.of(2026, 10, 2), args[1]);
                        }
                        default -> throw new AssertionError("unexpected terminal parameter");
                      }
                      yield null;
                    }
                    case "executeQuery" -> rows.read();
                    case CLOSE_METHOD -> {
                      calls.add(TERMINAL_CLOSE);
                      closeAction.close();
                      yield null;
                    }
                    default ->
                        throw new AssertionError("unexpected terminal call: " + method.getName());
                  });
        },
        calls);
  }

  @FunctionalInterface
  private interface StatementSupplier {
    @Nullable PreparedStatement prepare() throws SQLException;
  }

  @FunctionalInterface
  private interface RowsSupplier {
    @Nullable ResultSet read() throws SQLException;
  }

  @FunctionalInterface
  private interface CloseAction {
    void close() throws SQLException;
  }

  @FunctionalInterface
  private interface NextRow {
    boolean next() throws SQLException;
  }

  private static ResultSet terminalRows(List<String> calls, NextRow next, CloseAction closeAction) {
    return proxy(
        ResultSet.class,
        (unused, method, args) ->
            switch (method.getName()) {
              case NEXT_METHOD -> next.next();
              case CLOSE_METHOD -> {
                calls.add(TERMINAL_ROWS_CLOSE);
                closeAction.close();
                yield null;
              }
              default ->
                  throw new AssertionError("unexpected terminal row call: " + method.getName());
            });
  }

  private static ResultSet successfulTerminalRows(List<String> calls) {
    return successfulTerminalRows(calls, () -> {});
  }

  private static ResultSet successfulTerminalRows(List<String> calls, CloseAction closeAction) {
    return projectedTerminalRows(calls, closeAction, index -> index);
  }

  private static ResultSet projectedTerminalRows(
      List<String> calls, CloseAction closeAction, IntUnaryOperator rowOrder) {
    var cursor = new AtomicInteger(-1);
    return proxy(
        ResultSet.class,
        (unused, method, args) ->
            switch (method.getName()) {
              case NEXT_METHOD -> cursor.incrementAndGet() < EXPECTED_STEPS.size();
              case "getString" ->
                  terminalColumn(rowOrder.applyAsInt(cursor.get()), (String) args[0]);
              case "getObject" ->
                  ((Class<?>) args[1])
                      .cast(terminalColumn(rowOrder.applyAsInt(cursor.get()), (String) args[0]));
              case CLOSE_METHOD -> {
                calls.add(TERMINAL_ROWS_CLOSE);
                closeAction.close();
                yield null;
              }
              default ->
                  throw new AssertionError("unexpected terminal row call: " + method.getName());
            });
  }

  private static PreparedStatement priorLookupStatement(
      List<String> calls, CloseAction rowClose, CloseAction statementClose) {
    return proxy(
        PreparedStatement.class,
        (unused, method, args) -> {
          switch (method.getName()) {
            case "setQueryTimeout" -> assertEquals(5, args[0]);
            case "setObject" -> {
              assertEquals(1, args[0]);
              assertEquals(LocalDate.of(2026, 10, 2), args[1]);
            }
            case "setString" -> {
              assertEquals(2, args[0]);
              assertEquals("CLEAN_NOTIFICATION", args[1]);
            }
            case "setInt" -> {
              assertEquals(3, args[0]);
              assertEquals(2, args[1]);
            }
            case "executeQuery" -> {
              return priorLookupRow(calls, rowClose);
            }
            case CLOSE_METHOD -> {
              calls.add(PRIOR_STATEMENT_CLOSE);
              statementClose.close();
            }
            default -> throw new AssertionError("unexpected prior lookup statement call");
          }
          return null;
        });
  }

  private static ResultSet priorLookupRow(List<String> calls, CloseAction rowClose) {
    var cursor = new AtomicInteger();
    return proxy(
        ResultSet.class,
        (unused, method, args) ->
            switch (method.getName()) {
              case NEXT_METHOD -> cursor.incrementAndGet() == 1;
              case "getString" -> priorLookupColumn((String) args[0]);
              case "getObject" -> ((Class<?>) args[1]).cast(priorLookupColumn((String) args[0]));
              case CLOSE_METHOD -> {
                calls.add(PRIOR_ROW_CLOSE);
                rowClose.close();
                yield null;
              }
              default -> throw new AssertionError("unexpected prior lookup row call");
            });
  }

  private static Object priorLookupColumn(String column) {
    return switch (column) {
      case "id" -> 80L;
      case "run_id" -> PRIOR_RUN_ID;
      case "started_at" -> CUTOFF.atOffset(ZoneOffset.UTC);
      case "ended_at" -> STARTED.atOffset(ZoneOffset.UTC);
      default -> terminalColumn(EXPECTED_STEPS.size() - 1, column);
    };
  }

  private static Object terminalColumn(int offset, String column) {
    int row = EXPECTED_STEPS.size() - offset - 1;
    return switch (column) {
      case "id" -> 90L + row;
      case "run_id" -> new UUID(0, 7);
      case "business_date" -> LocalDate.of(2026, 10, 2);
      case "step" -> EXPECTED_STEPS.get(row).name();
      case "attempt" -> 1;
      case "started_at" -> STARTED.atOffset(ZoneOffset.UTC);
      case "ended_at" -> ENDED.atOffset(ZoneOffset.UTC);
      case "status" -> "SUCCESS";
      case "target_count", "success_count" -> 2L;
      case "failure_count", "byte_count" -> 0L;
      case "error_code", "error_summary" -> null;
      default -> throw new AssertionError("unexpected terminal column: " + column);
    };
  }

  private static Connection connection(
      String targetSql, StatementSupplier target, List<String> calls) {
    return proxy(
        Connection.class,
        (unused, method, args) ->
            switch (method.getName()) {
              case "getAutoCommit", "isReadOnly" -> false;
              case "getTransactionIsolation" -> Connection.TRANSACTION_READ_COMMITTED;
              case "prepareStatement" -> {
                var sql = (String) args[0];
                if (targetSql.equals(sql)) yield target.prepare();
                assertEquals(
                    "select"
                        + " has_batch_history,has_inbox_progress,has_log_progress,identity_consistent"
                        + " from schubert.maintenance_read_run_references(?,?)",
                    sql);
                calls.add(IDENTITY_CHECK);
                yield referenceStatement(calls);
              }
              default -> throw new AssertionError("unexpected borrowed call: " + method.getName());
            });
  }

  private static PreparedStatement referenceStatement(List<String> calls) {
    return proxy(
        PreparedStatement.class,
        (unused, method, args) ->
            switch (method.getName()) {
              case "setObject", "setQueryTimeout" -> null;
              case "executeQuery" -> referenceRows(calls);
              case CLOSE_METHOD -> {
                calls.add(IDENTITY_STATEMENT_CLOSE);
                yield null;
              }
              default -> throw new AssertionError("unexpected statement call: " + method.getName());
            });
  }

  private static ResultSet referenceRows(List<String> calls) {
    var position = new AtomicInteger();
    return proxy(
        ResultSet.class,
        (unused, method, args) ->
            switch (method.getName()) {
              case NEXT_METHOD -> position.incrementAndGet() == 1;
              case "getObject" -> "identity_consistent".equals(args[0]);
              case CLOSE_METHOD -> {
                calls.add(IDENTITY_ROWS_CLOSE);
                yield null;
              }
              default -> throw new AssertionError("unexpected row call: " + method.getName());
            });
  }

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }
}
