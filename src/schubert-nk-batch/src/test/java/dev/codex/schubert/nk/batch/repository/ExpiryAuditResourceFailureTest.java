package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
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

  @Test
  void independent68CompoundFailuresPreserveTypedPriorityAndBorrowedConnection() {
    for (var sample : JdbcResourceCases.all()) {
      var probe = new Probe();
      sample.install(probe.faults);
      sample.verify(
          assertThrows(
              Throwable.class, () -> new ExpiryAuditRepository(probe.connection()).read(HANDLE)));
      probe.assertAuditClosed();
    }
  }

  @Test
  void normalEmptySnapshotMandatoryNullAndProviderUnknownRemainDistinct() {
    var empty = new Probe();
    assertTrue(new ExpiryAuditRepository(empty.connection()).read(HANDLE).isEmpty());
    empty.assertAuditClosed();
    assertEquals(2, empty.calls.get("reference.statement.executeQuery"));
    var present = new Probe();
    present.auditPresent = true;
    assertEquals(
        new ExpiryAuditRepository.Snapshot(
            "RUNNING", null, null, null, 0, 0, 0, 0, null, null, null),
        new ExpiryAuditRepository(present.connection()).read(HANDLE).orElseThrow());
    present.assertAuditClosed();
    for (String invalid :
        new String[] {
          "statement-null",
          "rows-null",
          "status",
          "target_count",
          "success_count",
          "failure_count",
          "byte_count",
          "invalid-status",
          "invalid-count"
        }) {
      var probe = new Probe();
      probe.auditPresent = true;
      if (invalid.equals("statement-null")) probe.nullStatement = true;
      else if (invalid.equals("rows-null")) probe.nullRows = true;
      else if (invalid.equals("invalid-status")) probe.values.put("status", "UNKNOWN");
      else if (invalid.equals("invalid-count")) probe.values.put("target_count", -1L);
      else probe.values.remove(invalid);
      Throwable fixed =
          assertThrows(
              BatchRepositoryException.class,
              () -> new ExpiryAuditRepository(probe.connection()).read(HANDLE));
      assertEquals("batch repository operation failed", fixed.getMessage());
      assertNull(fixed.getCause());
      assertEquals(0, fixed.getSuppressed().length);
      probe.assertAuditClosed();
    }
    for (String point :
        new String[] {
          "audit.prepare",
          "statement.setQueryTimeout",
          "statement.setLong",
          "statement.setObject",
          "statement.setInt",
          "statement.executeQuery",
          "row.next",
          "row.getString",
          "row.getObject",
          "row.close",
          "statement.close"
        }) {
      for (Throwable primary :
          new Throwable[] {
            new IllegalArgumentException("public argument"),
            new IllegalStateException("public state"),
            new NullPointerException("public null"),
            new AssertionError("public fatal")
          }) {
        var probe = new Probe();
        probe.auditPresent = true;
        probe.faults.put(point, primary);
        assertSame(
            primary,
            assertThrows(
                Throwable.class, () -> new ExpiryAuditRepository(probe.connection()).read(HANDLE)),
            point);
        assertEquals(0, primary.getSuppressed().length);
        probe.assertAuditClosed();
      }
    }
  }

  static final class Probe {
    final Map<String, Throwable> faults = new HashMap<>();
    final Map<String, Integer> calls = new HashMap<>();
    final Map<String, Object> values =
        new HashMap<>(
            Map.of(
                "status",
                "RUNNING",
                "target_count",
                0L,
                "success_count",
                0L,
                "failure_count",
                0L,
                "byte_count",
                0L));
    boolean auditPresent;
    boolean nullStatement;
    boolean nullRows;
    int statements;
    int rowsets;

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
                      if (!reference) {
                        assertTrue(sql.startsWith("select status,expiry_cutoff_at,"));
                        hit("audit.prepare");
                        if (nullStatement) yield null;
                      }
                      yield statement(reference);
                    }
                    default ->
                        throw new AssertionError(
                            "unexpected borrowed connection operation: " + method.getName());
                  });
    }

    PreparedStatement statement(boolean reference) {
      if (!reference) statements++;
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
                  case "executeQuery" -> !reference && nullRows ? null : rows(reference);
                  default ->
                      throw new AssertionError(
                          "unexpected statement operation: " + method.getName());
                };
              });
    }

    ResultSet rows(boolean reference) {
      if (!reference) rowsets++;
      int[] position = {0};
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                hit((reference ? "reference.row." : "row.") + method.getName());
                return switch (method.getName()) {
                  case "next" -> (reference || auditPresent) && position[0]++ == 0;
                  case "getObject" -> {
                    if (reference) {
                      assertEquals(Boolean.class, args[1]);
                      yield "identity_consistent".equals(args[0]);
                    }
                    Object value = values.get(args[0]);
                    if (value != null) assertTrue(((Class<?>) args[1]).isInstance(value));
                    yield value;
                  }
                  case "getString" -> values.get(args[0]);
                  case "close" -> null;
                  default ->
                      throw new AssertionError("unexpected result operation: " + method.getName());
                };
              });
    }

    void assertAuditClosed() {
      assertEquals(statements, calls.getOrDefault("statement.close", 0));
      assertEquals(rowsets, calls.getOrDefault("row.close", 0));
    }
  }
}
