package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SS332/SSC320; BUG2245/YKT1991; NK-OPS-001/3505. JDK proxies only, no fixture instance. */
final class WebLogDatabaseFixtureTransactionTest {
  private static final String SETUP_EVENT = "setup:false";
  private static final String CLOSE_EVENT = "close";

  /** PT-FIX-SETUP001: ownership transfers only after successful setup. */
  @Test
  void normalTransfersOwnership() throws SQLException {
    List<String> events = new ArrayList<>();
    Connection connection = connection(null, null, events);
    assertSame(connection, WebLogDatabaseFixture.beginTransaction(connection));
    assertEquals(List.of(SETUP_EVENT), events);
  }

  /** PT-FIX-SETUP002: literal SS320 truth table, independent of the implementation. */
  @Test
  void exactFailureMatrix() {
    List<String> rows =
        List.of(
            "S-_-P", "S-S-P", "S-R-P", "S-N-P", "S-E-C", "R-_-P", "R-S-P", "R-R-P", "R-N-P",
            "R-E-C", "N-_-P", "N-S-P", "N-R-P", "N-N-P", "N-E-C", "E-_-P", "E-S-P", "E-R-P",
            "E-N-P", "E-E-P");
    assertEquals(20, rows.size());
    for (String row : rows) {
      Throwable primary = failure(row.charAt(0));
      Throwable secondary = failure(row.charAt(2));
      Throwable expected = row.charAt(4) == 'P' ? primary : secondary;
      Throwable other = row.charAt(4) == 'P' ? secondary : primary;
      List<String> events = new ArrayList<>();
      Connection connection = connection(primary, secondary, events);
      Throwable actual =
          assertThrows(Throwable.class, () -> WebLogDatabaseFixture.beginTransaction(connection));
      assertSame(expected, actual, row);
      assertArrayEquals(
          other == null ? new Throwable[0] : new Throwable[] {other}, actual.getSuppressed(), row);
      assertEquals(List.of(SETUP_EVENT, CLOSE_EVENT), events, row);
    }
  }

  /** PT-FIX-SETUP003: repeated provider identity is never suppressed onto itself. */
  @Test
  void identicalThrowableIsNeverSelfSuppressed() {
    for (char kind : new char[] {'S', 'R', 'N', 'E'}) {
      Throwable original = failure(kind);
      List<String> events = new ArrayList<>();
      Connection connection = connection(original, original, events);
      assertSame(
          original,
          assertThrows(Throwable.class, () -> WebLogDatabaseFixture.beginTransaction(connection)));
      assertArrayEquals(new Throwable[0], original.getSuppressed());
      assertEquals(List.of(SETUP_EVENT, CLOSE_EVENT), events);
    }
  }

  /** PT-FIX-SETUP004: null violates the helper's input invariant before JDBC. */
  @Test
  void nullFailsBeforeAnyJdbcAccess() {
    NullPointerException failure =
        assertThrows(
            NullPointerException.class, () -> WebLogDatabaseFixture.beginTransaction(null));
    assertEquals("connection", failure.getMessage());
    assertArrayEquals(new Throwable[0], failure.getSuppressed());
  }

  private static Throwable failure(char kind) {
    return switch (kind) {
      case '_' -> null;
      case 'S' -> new SQLException("synthetic setup SQL");
      case 'R' -> new IllegalStateException("synthetic unknown runtime");
      case 'N' -> new NullPointerException("synthetic provider null failure");
      case 'E' -> new LinkageError("synthetic fatal identity");
      default -> throw new AssertionError("unknown literal vector");
    };
  }

  private static Connection connection(Throwable setup, Throwable close, List<String> events) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, arguments) -> {
              switch (method.getName()) {
                case "setAutoCommit":
                  assertEquals(1, arguments.length);
                  assertFalse((boolean) arguments[0]);
                  events.add(SETUP_EVENT);
                  if (setup != null) throw setup;
                  return null;
                case CLOSE_EVENT:
                  events.add(CLOSE_EVENT);
                  if (close != null) throw close;
                  return null;
                default:
                  throw new AssertionError("Unexpected JDBC call: " + method.getName());
              }
            });
  }
}
