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
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;

/** SSC-461 and PT-F02-EXPIRY-GRAPH-001/002: in-memory borrowed JDBC ownership. */
@Timeout(5)
final class ExpiryAuditJdbcFailureGraphTest {
  private static final Instant CUTOFF = Instant.parse("2026-10-01T21:00:00Z");
  private static final Instant STARTED = Instant.parse("2026-10-01T21:00:01Z");
  private static final Instant ENDED = Instant.parse("2026-10-01T21:00:02Z");
  private static final BatchRun RUN =
      new BatchRun(UUID.fromString("11111111-1111-4111-8111-111111111111"), CUTOFF);
  private static final BatchStepAttempt ATTEMPT =
      new BatchStepAttempt(17, RUN, BatchStep.CLEAN_EXPIRY, 1, STARTED, false);

  private enum Entry {
    SUCCESSFUL("select id,run_id,attempt,started_at"),
    STAGE("update schubert.batch_runs set expiry_cutoff_at"),
    FINISH("update schubert.batch_runs set ended_at"),
    READ("select status,expiry_cutoff_at");

    private final String sqlPrefix;

    Entry(String sqlPrefix) {
      this.sqlPrefix = sqlPrefix;
    }

    void invoke(ExpiryAuditRepository repository) throws Exception {
      switch (this) {
        case SUCCESSFUL -> repository.successful(RUN, STARTED, () -> 5_000_000_000L);
        case STAGE -> repository.stage(ATTEMPT, 3, 2, 200);
        case FINISH ->
            repository.finish(
                ATTEMPT,
                new ExpiryAuditRepository.Stage(Instant.parse("2026-09-24T21:00:00Z"), 3, 2, 200),
                ENDED,
                1L,
                new BatchStepResult(
                    BatchStepResult.Status.SUCCESS, 2, 2, 0, 200, BatchStepResult.Reason.NONE));
        case READ -> repository.read(ATTEMPT);
      }
    }
  }

  @ParameterizedTest
  @EnumSource(Entry.class)
  void preservesTheFirstFatalFromTheSqlNextChain(Entry entry) {
    var fatal = new LinkageError("public test error");
    var provider = new SQLException("public test diagnostic");
    provider.setNextException(new SQLException("public test next", fatal));
    var calls = new ArrayList<String>();
    var repository = new ExpiryAuditRepository(connection(entry, provider, calls));
    assertSame(fatal, assertThrows(LinkageError.class, () -> entry.invoke(repository)));
    assertEquals(List.of("identity", "rows.close", "statement.close", "target"), calls);
  }

  @ParameterizedTest
  @EnumSource(Entry.class)
  void emitsOnlyTheFixedNonfatalDiagnostic(Entry entry) {
    var calls = new ArrayList<String>();
    var repository =
        new ExpiryAuditRepository(
            connection(entry, new SQLException("public test diagnostic"), calls));
    var failure = assertThrows(BatchRepositoryException.class, () -> entry.invoke(repository));
    assertEquals("batch repository operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertEquals(List.of("identity", "rows.close", "statement.close", "target"), calls);
  }

  private static Connection connection(Entry expected, SQLException provider, List<String> calls) {
    return proxy(
        Connection.class,
        (unused, method, args) ->
            switch (method.getName()) {
              case "getAutoCommit", "isReadOnly" -> false;
              case "getTransactionIsolation" -> Connection.TRANSACTION_READ_COMMITTED;
              case "prepareStatement" -> {
                String sql = (String) args[0];
                if (sql.startsWith(expected.sqlPrefix)) {
                  calls.add("target");
                  throw provider;
                }
                if (!sql.contains("schubert.maintenance_read_run_references(?,?)"))
                  throw new AssertionError("unexpected statement");
                calls.add("identity");
                yield identityStatement(calls);
              }
              default ->
                  throw new AssertionError("unexpected connection call: " + method.getName());
            });
  }

  private static PreparedStatement identityStatement(List<String> calls) {
    return proxy(
        PreparedStatement.class,
        (unused, method, args) ->
            switch (method.getName()) {
              case "setQueryTimeout", "setObject" -> null;
              case "executeQuery" -> identityRows(calls);
              case "close" -> {
                calls.add("statement.close");
                yield null;
              }
              default -> throw new AssertionError("unexpected statement call: " + method.getName());
            });
  }

  private static ResultSet identityRows(List<String> calls) {
    var position = new java.util.concurrent.atomic.AtomicInteger();
    return proxy(
        ResultSet.class,
        (unused, method, args) ->
            switch (method.getName()) {
              case "next" -> position.incrementAndGet() == 1;
              case "getObject" -> "identity_consistent".equals(args[0]);
              case "close" -> {
                calls.add("rows.close");
                yield null;
              }
              default -> throw new AssertionError("unexpected row call: " + method.getName());
            });
  }

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }
}
