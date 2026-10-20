package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.*;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** NK-BAT-001/DAT009/OPS009/UI251/SS331200/332063199; EXP310001; BUG1530/YKT1290. */
final class ExpiryAuditResourceFailureTest {
  static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
          Instant.parse("2026-09-12T15:00:00.123456Z"));
  static final BatchStepAttempt HANDLE =
      new BatchStepAttempt(42, RUN, BatchStep.CLEAN_EXPIRY, 1, RUN.cutoff().plusSeconds(1), false);

  @Test
  void primaryErrorSurvivesSqlCloseExactlyOnce() {
    var probe = new Probe();
    var primary = new AssertionError("public primary fixture");
    probe.faults.put("row.next", primary);
    probe.faults.put("row.close", new SQLException("public secondary fixture"));
    Throwable actual =
        assertThrows(
            Throwable.class, () -> new ExpiryAuditRepository(probe.connection()).read(HANDLE));
    assertSame(primary, actual);
    assertEquals(1, actual.getSuppressed().length);
    Throwable fixed = actual.getSuppressed()[0];
    assertInstanceOf(BatchRepositoryException.class, fixed);
    assertEquals("batch repository operation failed", fixed.getMessage());
    assertNull(fixed.getCause());
    assertEquals(0, fixed.getSuppressed().length);
    probe.assertAuditClosed();
  }

  static final class Probe {
    final Map<String, Throwable> faults = new HashMap<>();
    final Map<String, Integer> calls = new HashMap<>();

    void hit(String key) throws Throwable {
      calls.merge(key, 1, Integer::sum);
      Throwable failure = faults.get(key);
      if (failure != null) throw failure;
    }

    Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) ->
                  switch (method.getName()) {
                    case "getAutoCommit", "isReadOnly" -> false;
                    case "getTransactionIsolation" -> Connection.TRANSACTION_READ_COMMITTED;
                    case "prepareStatement" -> {
                      String sql = (String) args[0];
                      boolean reference = sql.contains("maintenance_read_run_references");
                      if (!reference) assertTrue(sql.startsWith("select status,expiry_cutoff_at,"));
                      yield statement(reference);
                    }
                    default ->
                        throw new AssertionError(
                            "unexpected borrowed connection operation: " + method.getName());
                  });
    }

    PreparedStatement statement(boolean reference) {
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) -> {
                String key = (reference ? "reference.statement." : "statement.") + method.getName();
                hit(key);
                return switch (method.getName()) {
                  case "setQueryTimeout" -> {
                    assertEquals(5, args[0]);
                    yield null;
                  }
                  case "setObject", "setLong", "setInt", "close" -> null;
                  case "executeQuery" -> rows(reference);
                  default ->
                      throw new AssertionError(
                          "unexpected statement operation: " + method.getName());
                };
              });
    }

    ResultSet rows(boolean reference) {
      int[] position = {0};
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                hit((reference ? "reference.row." : "row.") + method.getName());
                return switch (method.getName()) {
                  case "next" -> reference && position[0]++ == 0;
                  case "getObject" -> {
                    assertTrue(reference);
                    assertEquals(Boolean.class, args[1]);
                    yield "identity_consistent".equals(args[0]);
                  }
                  case "close" -> null;
                  default ->
                      throw new AssertionError("unexpected result operation: " + method.getName());
                };
              });
    }

    void assertAuditClosed() {
      assertEquals(1, calls.get("statement.close"));
      assertEquals(calls.containsKey("statement.executeQuery") ? 1 : null, calls.get("row.close"));
    }
  }
}
