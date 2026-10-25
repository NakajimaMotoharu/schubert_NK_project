package dev.codex.schubert.nk.web.receipt;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** RCPT005/BUG608/YKT428; actual JDBC with independent injected fault/close accounting. */
class ReceiptReferenceFaultTest {
  static final String ID = "00000000000000000000000001";
  static final Instant TIME = Instant.parse("2026-10-04T00:00:00.123Z");
  static WebLogDatabaseFixture db;

  @BeforeAll
  static void start(@TempDir Path root) throws Exception {
    db = new WebLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  static final class Probe {
    final String fault;
    final AtomicInteger live = new AtomicInteger();
    final AtomicInteger hits = new AtomicInteger();
    final AtomicInteger commits = new AtomicInteger();

    Probe(String fault) {
      this.fault = fault;
    }

    DataSource source() {
      return (DataSource)
          Proxy.newProxyInstance(
              DataSource.class.getClassLoader(),
              new Class<?>[] {DataSource.class},
              (proxy, method, args) -> {
                if (!method.getName().equals("getConnection"))
                  throw new UnsupportedOperationException("fixture method");
                if (fault.equals("connectionNull")) {
                  hits.incrementAndGet();
                  return null;
                }
                fail("getConnection");
                return wrap(Connection.class, db.web());
              });
    }

    void fail(String point) throws Throwable {
      if (Arrays.asList(fault.split("\\+", -1)).contains(point + "Sql")
          || (fault.equals("rollbackSql") && point.equals("executeQuery"))) {
        hits.incrementAndGet();
        throw new SQLException("fixture provider detail");
      }
      if (Arrays.asList(fault.split("\\+", -1)).contains(point + "Unknown")) {
        hits.incrementAndGet();
        throw new IllegalStateException("fixture unknown");
      }
      if (Arrays.asList(fault.split("\\+", -1)).contains(point + "Error")) {
        hits.incrementAndGet();
        throw new AssertionError("fixture error");
      }
    }

    <T> T wrap(Class<T> type, T target) {
      live.incrementAndGet();
      var nextCalls = new AtomicInteger();
      return type.cast(
          Proxy.newProxyInstance(
              type.getClassLoader(),
              new Class<?>[] {type},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals("close")) {
                  invoke(method, target, args);
                  live.decrementAndGet();
                  fail(type.getSimpleName() + "Close");
                  return null;
                }
                if (name.equals("prepareStatement") && fault.equals("statementNull")) {
                  hits.incrementAndGet();
                  return null;
                }
                if (name.equals("executeQuery") && fault.equals("rowNull")) {
                  hits.incrementAndGet();
                  return null;
                }
                fail(name);
                Object result = invoke(method, target, args);
                if (name.equals("commit")) commits.incrementAndGet();
                if (result instanceof PreparedStatement statement)
                  return wrap(PreparedStatement.class, statement);
                if (result instanceof ResultSet row) return wrap(ResultSet.class, row);
                if (name.equals("next")) {
                  int n = nextCalls.incrementAndGet();
                  if ((fault.equals("rowMissing") && n == 1)
                      || (fault.equals("rowDuplicate") && n == 2)) {
                    hits.incrementAndGet();
                    return fault.equals("rowDuplicate");
                  }
                }
                if (name.equals("executeUpdate") && fault.startsWith("count")) {
                  hits.incrementAndGet();
                  return fault.equals("countNegative") ? -1 : 2;
                }
                if (name.equals("getString") && fault.equals("idNull")) {
                  hits.incrementAndGet();
                  return null;
                }
                if (name.equals("getString") && fault.equals("idMismatch")) {
                  hits.incrementAndGet();
                  return "00000000000000000000000002";
                }
                if (name.equals("getString") && fault.equals("idInvalid")) {
                  hits.incrementAndGet();
                  return "invalid";
                }
                if (name.equals("getObject") && args[0].equals("question_id")) {
                  if (fault.equals("questionNull")) {
                    hits.incrementAndGet();
                    return null;
                  }
                  if (fault.equals("questionInvalid")) {
                    hits.incrementAndGet();
                    return 0L;
                  }
                }
                if (name.equals("getObject") && args[0].equals("submitted_at")) {
                  if (fault.equals("timeNull")) {
                    hits.incrementAndGet();
                    return null;
                  }
                  if (fault.equals("timeInvalid")) {
                    hits.incrementAndGet();
                    return TIME.plusNanos(1).atOffset(ZoneOffset.UTC);
                  }
                }
                return result;
              }));
    }

    static Object invoke(Method method, Object target, Object[] args) throws Throwable {
      try {
        return method.invoke(target, args);
      } catch (InvocationTargetException failure) {
        throw failure.getCause();
      }
    }
  }

  @BeforeEach
  void seed() throws Exception {
    try (var c = db.web();
        var s = c.createStatement()) {
      s.execute("delete from schubert_web_session.web_receipt_references");
      s.execute(
          "insert into schubert_web_session.web_receipt_references values ('00000000000000000000000001',7,'2026-10-04T00:00:00.123Z')");
    }
  }

  @Test
  void rcpt005ReadNullProjectionSqlAndOwnedCloseUncertainty() {
    for (String fault :
        List.of(
            "connectionNull",
            "getConnectionSql",
            "setAutoCommitSql",
            "setReadOnlySql",
            "setTransactionIsolationSql",
            "statementNull",
            "rowNull",
            "prepareStatementSql",
            "executeQuerySql",
            "idNull",
            "questionNull",
            "timeNull",
            "idInvalid",
            "questionInvalid",
            "timeInvalid",
            "idMismatch",
            "rowDuplicate",
            "commitSql",
            "ConnectionCloseSql",
            "PreparedStatementCloseSql",
            "ResultSetCloseSql",
            "rollbackSql")) {
      var p = new Probe(fault);
      var failure =
          assertThrows(
              ReceiptReferenceException.class,
              () -> new ReceiptReferenceRepository(p.source()).find(ID),
              fault);
      assertEquals("receipt reference unavailable", failure.getMessage());
      assertTrue(p.hits.get() > 0, fault);
      assertEquals(0, p.live.get(), fault);
    }
    var p = new Probe("ConnectionCloseSql");
    assertThrows(
        ReceiptReferenceException.class, () -> new ReceiptReferenceRepository(p.source()).find(ID));
    assertEquals(1, p.commits.get()); // commit alone did not return success.
  }

  @Test
  void rcpt005CompoundUnknownCloseMustDominatePrimarySql() {
    for (String fault :
        List.of(
            "executeQuerySql+PreparedStatementCloseUnknown",
            "getObjectSql+ResultSetCloseUnknown",
            "executeQuerySql+ConnectionCloseUnknown",
            "executeUpdateSql+PreparedStatementCloseUnknown",
            "executeQuerySql+rollbackUnknown")) {
      var p = new Probe(fault);
      assertThrows(
          IllegalStateException.class,
          () ->
              new ReceiptReferenceRepository(p.source())
                  .register(new ReceiptReference(ID, 7, TIME)),
          fault);
      assertEquals(0, p.live.get(), fault);
    }
  }

  @Test
  void rcpt005CompoundKnownAndPrimaryUnknownPrecedence() {
    for (String point :
        List.of("PreparedStatementClose", "ResultSetClose", "ConnectionClose", "rollback")) {
      String sqlPoint = point.equals("ResultSetClose") ? "getObject" : "executeQuery";
      for (String secondary : List.of("Sql", "Unknown", "Error")) {
        var p = new Probe(sqlPoint + "Unknown+" + point + secondary);
        var failure =
            assertThrows(
                IllegalStateException.class,
                () -> new ReceiptReferenceRepository(p.source()).find(ID));
        assertEquals("fixture unknown", failure.getMessage());
        assertEquals(0, p.live.get());
        assertTrue(failure.getSuppressed().length > 0);
        for (var suppressed : failure.getSuppressed())
          assertInstanceOf(ReceiptReferenceException.class, suppressed);
      }
      var p = new Probe(sqlPoint + "Sql+" + point + "Sql");
      assertThrows(
          ReceiptReferenceException.class,
          () -> new ReceiptReferenceRepository(p.source()).find(ID));
      assertEquals(0, p.live.get());
      var e = new Probe(sqlPoint + "Sql+" + point + "Error");
      assertThrows(AssertionError.class, () -> new ReceiptReferenceRepository(e.source()).find(ID));
      assertEquals(0, e.live.get());
    }
    var insert = new Probe("executeUpdateSql+PreparedStatementCloseSql");
    assertThrows(
        ReceiptReferenceException.class,
        () ->
            new ReceiptReferenceRepository(insert.source())
                .register(new ReceiptReference(ID, 7, TIME)));
    assertEquals(0, insert.live.get());
  }

  @Test
  void rcpt005RegisterCountsMissingUnknownAndErrorNeverSuccess() throws Exception {
    for (String fault : List.of("countNegative", "countExcess", "rowMissing", "executeUpdateSql")) {
      var p = new Probe(fault);
      assertThrows(
          ReceiptReferenceException.class,
          () ->
              new ReceiptReferenceRepository(p.source())
                  .register(new ReceiptReference(ID, 7, TIME)),
          fault);
      assertTrue(p.hits.get() > 0, fault);
      assertEquals(0, p.live.get(), fault);
      assertEquals(0, p.commits.get(), fault);
    }
    for (String fault :
        List.of(
            "getConnectionUnknown",
            "executeQueryUnknown",
            "ConnectionCloseUnknown",
            "getConnectionError",
            "executeQueryError",
            "ConnectionCloseError")) {
      var p = new Probe(fault);
      Class<? extends Throwable> expected =
          fault.endsWith("Error") ? AssertionError.class : IllegalStateException.class;
      assertThrows(expected, () -> new ReceiptReferenceRepository(p.source()).find(ID), fault);
      assertEquals(0, p.live.get(), fault);
    }
    var p = new Probe("");
    new ReceiptReferenceRepository(p.source()).register(new ReceiptReference(ID, 7, TIME));
    assertEquals(0, p.live.get());
    assertEquals(1, p.commits.get());
    try (var c = db.web();
        var s = c.createStatement();
        var row =
            s.executeQuery(
                "select question_id,submitted_at from schubert_web_session.web_receipt_references")) {
      assertTrue(row.next());
      assertEquals(7, row.getLong(1));
      assertEquals(TIME, row.getObject(2, OffsetDateTime.class).toInstant());
      assertFalse(row.next());
    }
  }
}
