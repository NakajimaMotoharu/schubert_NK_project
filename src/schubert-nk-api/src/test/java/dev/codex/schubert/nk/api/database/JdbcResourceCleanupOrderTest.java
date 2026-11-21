package dev.codex.schubert.nk.api.database;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.Proxy;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-JDBC-CLEANUP008; SSC425 and SS332, using JDK resource proxies only. */
final class JdbcResourceCleanupOrderTest {
  @Test
  void preservesExistingSuppressionAndAppendsBothFailuresInCallOrder() {
    var primary = new SQLException("body failure");
    var existing = new IllegalStateException("earlier cleanup failure");
    var rowFailure = new SQLException("row close failure");
    var statementFailure = new AssertionError("statement close failure");
    primary.addSuppressed(existing);
    var closeOrder = new ArrayList<String>();

    var observed =
        assertThrows(
            SQLException.class,
            () -> {
              try {
                throw primary;
              } finally {
                JdbcResourceCleanup.closeRows(
                    primary, failingClose(ResultSet.class, closeOrder, "rows", rowFailure));
                JdbcResourceCleanup.closeStatement(
                    primary,
                    failingClose(Statement.class, closeOrder, "statement", statementFailure));
              }
            });

    assertSame(primary, observed);
    assertEquals(List.of("rows", "statement"), closeOrder);
    var suppressed = observed.getSuppressed();
    assertEquals(3, suppressed.length);
    assertSame(existing, suppressed[0]);
    assertSame(rowFailure, suppressed[1]);
    assertSame(statementFailure, suppressed[2]);
  }

  private static <T> T failingClose(
      Class<T> type, List<String> closeOrder, String name, Throwable failure) {
    return type.cast(
        Proxy.newProxyInstance(
            Thread.currentThread().getContextClassLoader(),
            new Class<?>[] {type},
            (proxy, method, args) -> {
              assertEquals("close", method.getName());
              closeOrder.add(name);
              throw failure;
            }));
  }
}
