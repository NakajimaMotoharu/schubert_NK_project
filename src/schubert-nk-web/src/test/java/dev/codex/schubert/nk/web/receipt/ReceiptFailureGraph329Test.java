package dev.codex.schubert.nk.web.receipt;

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
import java.time.ZoneOffset;
import javax.sql.DataSource;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** NK-WEB-002; SS312/331/332/354/SSC329; BUG1592/YKT1348; PT-WEB-RECEIPT-GRAPH329001..003. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class ReceiptFailureGraph329Test {
  private static final String ID = "00000000000000000000000001";
  private static final Instant TIME = Instant.parse("2026-10-04T00:00:00.123Z");

  @Test
  void receipt329001SelectedSqlGraphPreservesFatalAfterOwnedSetupClose() {
    for (String point : new String[] {"getConnection", "setAutoCommit"}) {
      for (int mode = 0; mode < 3; mode++) {
        var fatal = new AssertionError("PUBLIC fatal");
        var fixture = new Fixture(point, graph(fatal, mode), "", null);
        assertSame(fatal, assertThrows(AssertionError.class, () -> fixture.repository().find(ID)));
        assertEquals(point.equals("getConnection") ? 0 : 1, fixture.connectionCloses);
        assertEquals(0, fixture.rollbacks);
        assertEquals(0, fixture.commits);
      }
    }
  }

  @Test
  void receipt329002BothSqlCleanupGraphsCannotDisappearBeforeFixedCatalog() {
    for (String point :
        new String[] {
          "ResultSetClose", "PreparedStatementClose", "rollback", "ConnectionClose", "InsertClose"
        }) {
      var fatal = new AssertionError("PUBLIC fatal");
      boolean insert = point.equals("InsertClose");
      var fixture =
          new Fixture(
              insert
                  ? "executeUpdate"
                  : point.equals("ResultSetClose") ? "getString" : "executeQuery",
              new SQLException("PUBLIC primary"),
              insert ? "PreparedStatementClose" : point,
              graph(fatal, 2));
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () -> {
                if (insert) fixture.repository().register(new ReceiptReference(ID, 7, TIME));
                else fixture.repository().find(ID);
              }));
      assertEquals(1, fixture.connectionCloses, point);
      assertEquals(1, fixture.statementCloses, point);
      assertEquals(point.equals("ResultSetClose") ? 1 : 0, fixture.resultCloses, point);
      assertEquals(1, fixture.rollbacks, point);
      assertEquals(0, fixture.commits, point);
    }
  }

  @Test
  void receipt329003ExistingUnknownPriorityAndFixedNonFatalCyclesAreUnchanged() {
    var same = graph(null, 3);
    var sql = new Fixture("executeQuery", same, "PreparedStatementClose", same);
    var fixed = assertThrows(ReceiptReferenceException.class, () -> sql.repository().find(ID));
    assertEquals("receipt reference unavailable", fixed.getMessage());
    assertNull(fixed.getCause());
    assertEquals(0, fixed.getSuppressed().length);
    var unknown = new IllegalStateException("PUBLIC primary");
    var unknownFixture =
        new Fixture(
            "executeQuery",
            unknown,
            "PreparedStatementClose",
            new AssertionError("PUBLIC ignored secondary"));
    assertSame(
        unknown,
        assertThrows(IllegalStateException.class, () -> unknownFixture.repository().find(ID)));
    assertTrue(unknown.getSuppressed().length > 0);
    for (Throwable secondary : unknown.getSuppressed())
      assertInstanceOf(ReceiptReferenceException.class, secondary);
    var cleanup = new IllegalStateException("PUBLIC cleanup");
    var replaced =
        new Fixture(
            "executeQuery", new SQLException("PUBLIC primary"), "PreparedStatementClose", cleanup);
    assertSame(
        cleanup, assertThrows(IllegalStateException.class, () -> replaced.repository().find(ID)));
    var primaryError = new AssertionError("PUBLIC primary");
    var error =
        new Fixture(
            "executeQuery",
            primaryError,
            "PreparedStatementClose",
            new AssertionError("PUBLIC secondary"));
    assertSame(primaryError, assertThrows(AssertionError.class, () -> error.repository().find(ID)));
    for (Fixture fixture : new Fixture[] {sql, unknownFixture, replaced, error}) {
      assertEquals(1, fixture.connectionCloses);
      assertEquals(1, fixture.statementCloses);
      assertEquals(1, fixture.rollbacks);
      assertEquals(0, fixture.commits);
    }
  }

  private static SQLException graph(@Nullable AssertionError fatal, int mode) {
    var sql = new SQLException("PUBLIC SQL");
    var next = new SQLException("PUBLIC next");
    sql.setNextException(next);
    if (fatal == null) next.setNextException(sql);
    else if (mode == 0) sql.initCause(fatal);
    else if (mode == 1) sql.addSuppressed(fatal);
    else next.initCause(fatal);
    return sql;
  }

  private static final class Fixture {
    final String fault;
    final Throwable primary;
    final String closePoint;
    final @Nullable Throwable secondary;
    int connectionCloses;
    int statementCloses;
    int resultCloses;
    int rollbacks;
    int commits;

    Fixture(String fault, Throwable primary, String closePoint, @Nullable Throwable secondary) {
      this.fault = fault;
      this.primary = primary;
      this.closePoint = closePoint;
      this.secondary = secondary;
    }

    void fail(String point) throws Throwable {
      if (fault.equals(point)) throw primary;
      if (closePoint.equals(point) && secondary != null) throw secondary;
    }

    ReceiptReferenceRepository repository() {
      var source =
          (DataSource)
              Proxy.newProxyInstance(
                  DataSource.class.getClassLoader(),
                  new Class<?>[] {DataSource.class},
                  (object, method, args) -> {
                    assertEquals("getConnection", method.getName());
                    fail("getConnection");
                    return connection();
                  });
      return new ReceiptReferenceRepository(source);
    }

    Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (object, method, args) -> {
                String name = method.getName();
                if (name.equals("close")) {
                  connectionCloses++;
                  fail("ConnectionClose");
                  return null;
                }
                if (name.equals("rollback")) {
                  rollbacks++;
                  fail("rollback");
                  return null;
                }
                if (name.equals("commit")) {
                  commits++;
                  fail("commit");
                  return null;
                }
                fail(name);
                if (name.equals("prepareStatement")) return statement();
                if (java.util.Set.of("setAutoCommit", "setReadOnly", "setTransactionIsolation")
                    .contains(name)) return null;
                throw new AssertionError("Unexpected connection operation: " + name);
              });
    }

    PreparedStatement statement() {
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (object, method, args) -> {
                String name = method.getName();
                if (name.equals("close")) {
                  statementCloses++;
                  fail("PreparedStatementClose");
                  return null;
                }
                fail(name);
                if (name.equals("executeQuery")) return result();
                if (name.equals("executeUpdate")) return 1;
                if (java.util.Set.of("setString", "setLong", "setObject").contains(name))
                  return null;
                throw new AssertionError("Unexpected statement operation: " + name);
              });
    }

    ResultSet result() {
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (object, method, args) -> {
                String name = method.getName();
                if (name.equals("close")) {
                  resultCloses++;
                  fail("ResultSetClose");
                  return null;
                }
                fail(name);
                return switch (name) {
                  case "next" -> true;
                  case "getString" -> ID;
                  case "getObject" ->
                      args[0].equals("question_id") ? 7L : TIME.atOffset(ZoneOffset.UTC);
                  default -> throw new AssertionError("Unexpected result operation: " + name);
                };
              });
    }
  }
}
