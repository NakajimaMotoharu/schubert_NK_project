package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
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
import org.junit.jupiter.api.Test;

/** PT-BAT-SSC461-BF001–004: SSC-461 SQL graph and independent borrowed-resource expectations. */
final class BackupFailureSqlDiagnosticTest {
  private static final UUID RUN_ID = UUID.fromString("12345678-9abc-def0-8123-456789abcdef");
  private static final Instant CUTOFF = Instant.parse("2026-09-12T15:00:00Z");
  private static final Instant STARTED = Instant.parse("2026-09-13T02:00:00Z");
  private static final Instant ENDED = Instant.parse("2026-09-13T02:00:03Z");
  private static final String IDENTITY_SQL =
      "select has_batch_history,has_inbox_progress,has_log_progress,identity_consistent"
          + " from schubert.maintenance_read_run_references(?,?)";
  private static final String BACKUP_SQL =
      "select id,run_id,business_date,step,attempt,started_at,ended_at,status,"
          + "target_count,success_count,failure_count,byte_count,error_code,error_summary"
          + " from schubert.batch_runs where run_id=? and step=? order by attempt desc limit 1";

  @Test
  void bf001OrdinarySqlFailureKeepsOnlyFixedDiagnosticAndClosesOwnedResources() {
    assertFixedDiagnostic(new SQLException("fixture-only JDBC detail"));
  }

  @Test
  void bf002SqlNextEdgePreservesOriginalFatalObject() {
    var failure = new SQLException("fixture root");
    var fatal = new AssertionError("fixture fatal at SQL next");
    failure.setNextException(new SQLException("fixture edge", fatal));
    var fixture = new Fixture(failure);

    assertSame(fatal, assertThrows(AssertionError.class, fixture::verify));
    fixture.assertResourcesClosed();
  }

  @Test
  void bf003OrdinaryCauseHasPriorityOverSqlNext() {
    var cause = new AssertionError("fixture fatal at ordinary cause");
    var next = new AssertionError("fixture fatal at SQL next");
    var failure = new SQLException("fixture root", cause);
    failure.setNextException(new SQLException("fixture edge", next));
    var fixture = new Fixture(failure);

    assertSame(cause, assertThrows(AssertionError.class, fixture::verify));
    fixture.assertResourcesClosed();
  }

  @Test
  void bf004RepeatedNonfatalGraphStillReturnsFixedDiagnostic() {
    var failure = new SQLException("fixture root");
    var linked = new SQLException("fixture edge");
    failure.setNextException(linked);
    failure.addSuppressed(linked);
    linked.addSuppressed(failure);

    assertFixedDiagnostic(failure);
  }

  private static void assertFixedDiagnostic(SQLException sqlFailure) {
    var fixture = new Fixture(sqlFailure);
    var observed = assertThrows(IOException.class, fixture::verify);
    assertEquals("failed backup observation unavailable", observed.getMessage());
    assertNull(observed.getCause());
    assertEquals(0, observed.getSuppressed().length);
    fixture.assertResourcesClosed();
  }

  private static final class Fixture {
    private final SQLException failure;
    private final List<String> closed = new ArrayList<>();
    private int prepared;

    private Fixture(SQLException failure) {
      this.failure = failure;
    }

    void verify() throws IOException {
      var run = new BatchRun(RUN_ID, CUTOFF);
      var snapshot =
          new BackupFailureSnapshot(
              new BatchStepAttempt(7, run, BatchStep.BACKUP_DB, 4, STARTED, false),
              new BatchStepAttempt(8, run, BatchStep.BACKUP_CONFIG, 4, STARTED, false),
              ENDED);
      snapshot.verifyLatest(connection(), () -> 5_000_000_000L);
    }

    private Connection connection() {
      return proxy(
          Connection.class,
          (object, method, arguments) ->
              switch (method.getName()) {
                case "getAutoCommit", "isReadOnly" -> false;
                case "getTransactionIsolation" -> Connection.TRANSACTION_READ_COMMITTED;
                case "prepareStatement" -> statement((String) arguments[0]);
                default -> throw new AssertionError("unexpected loaned connection call");
              });
    }

    private PreparedStatement statement(String sql) {
      boolean identity = ++prepared == 1;
      assertEquals(identity ? IDENTITY_SQL : BACKUP_SQL, sql);
      return proxy(
          PreparedStatement.class,
          (object, method, arguments) -> {
            switch (method.getName()) {
              case "setQueryTimeout" -> assertEquals(5, arguments[0]);
              case "setObject" -> {
                int position = (int) arguments[0];
                assertEquals(
                    position == 1 ? RUN_ID : CUTOFF.atOffset(java.time.ZoneOffset.UTC),
                    arguments[1]);
              }
              case "setString" -> {
                assertEquals(2, arguments[0]);
                assertEquals("BACKUP_DB", arguments[1]);
              }
              case "executeQuery" -> {
                if (identity) return identityRows();
                throw failure;
              }
              case "close" -> closed.add(identity ? "identity statement" : "backup statement");
              default -> throw new AssertionError("unexpected statement call");
            }
            return null;
          });
    }

    private ResultSet identityRows() {
      return proxy(
          ResultSet.class,
          new InvocationHandler() {
            private boolean advanced;

            @Override
            public Object invoke(
                Object object, java.lang.reflect.Method method, Object[] arguments) {
              return switch (method.getName()) {
                case "next" -> {
                  boolean first = !advanced;
                  advanced = true;
                  yield first;
                }
                case "getObject" ->
                    switch ((String) arguments[0]) {
                      case "has_batch_history", "identity_consistent" -> true;
                      case "has_inbox_progress", "has_log_progress" -> false;
                      default -> throw new AssertionError("unexpected identity column");
                    };
                case "close" -> {
                  closed.add("identity row");
                  yield null;
                }
                default -> throw new AssertionError("unexpected result set call");
              };
            }
          });
    }

    void assertResourcesClosed() {
      assertEquals(2, prepared);
      assertEquals(List.of("identity row", "identity statement", "backup statement"), closed);
    }
  }

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }
}
