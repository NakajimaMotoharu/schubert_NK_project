package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-F02-CTERM-REF-001/002, SS332 and SSC-461. */
@Timeout(5)
final class CleanupTerminalReferencesJdbcGraphTest {
  private static final Instant CUTOFF = Instant.parse("2026-10-01T21:00:00Z");
  private static final Instant STARTED = Instant.parse("2026-10-01T21:00:01Z");
  private static final BatchRun RUN = new BatchRun(new UUID(0, 7), CUTOFF);
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
  private static final List<String> EXPECTED_CALLS =
      List.of("identity", "result close", "statement close", "prior success");
  private static final List<String> EXPECTED_READ_CALLS =
      List.of(
          "identity",
          "result close",
          "statement close",
          "terminal query",
          "terminal timeout",
          "terminal run",
          "terminal date",
          "terminal close");

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
    return connection(
        TERMINAL_READ_SQL,
        () -> {
          calls.add("terminal query");
          return proxy(
              PreparedStatement.class,
              (unused, method, args) ->
                  switch (method.getName()) {
                    case "setQueryTimeout" -> {
                      assertEquals(5, args[0]);
                      calls.add("terminal timeout");
                      yield null;
                    }
                    case "setObject" -> {
                      switch ((int) args[0]) {
                        case 1 -> {
                          calls.add("terminal run");
                          assertEquals(new UUID(0, 7), args[1]);
                        }
                        case 2 -> {
                          calls.add("terminal date");
                          assertEquals(LocalDate.of(2026, 10, 2), args[1]);
                        }
                        default -> throw new AssertionError("unexpected terminal parameter");
                      }
                      yield null;
                    }
                    case "executeQuery" -> throw provider;
                    case "close" -> {
                      calls.add("terminal close");
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
    PreparedStatement prepare() throws SQLException;
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
                calls.add("identity");
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
              case "close" -> {
                calls.add("statement close");
                yield null;
              }
              default -> throw new AssertionError("unexpected statement call: " + method.getName());
            });
  }

  private static ResultSet referenceRows(List<String> calls) {
    var position = new java.util.concurrent.atomic.AtomicInteger();
    return proxy(
        ResultSet.class,
        (unused, method, args) ->
            switch (method.getName()) {
              case "next" -> position.incrementAndGet() == 1;
              case "getObject" -> "identity_consistent".equals(args[0]);
              case "close" -> {
                calls.add("result close");
                yield null;
              }
              default -> throw new AssertionError("unexpected row call: " + method.getName());
            });
  }

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }
}
