package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import jakarta.jms.JMSException;
import java.sql.SQLException;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-JMS-VALUE001/GRAPH002; SS312321: public synthetic exceptions, no provider/broker/DB. */
final class JmsExceptionGraphValueTest {
  private static final String TEXT = "public bounded failure";

  @Test
  void jmsvalue001ReasonsHaveExactNamesDefensiveArraysAndConstructorNullContracts() {
    var values =
        List.of(
            JmsRequestReplyException.Reason.CAPACITY,
            JmsRequestReplyException.Reason.TIMEOUT,
            JmsRequestReplyException.Reason.INTERRUPTED);
    var names = List.of("CAPACITY", "TIMEOUT", "INTERRUPTED");
    assertEquals(values, List.of(JmsRequestReplyException.Reason.values()));
    for (int index = 0; index < names.size(); index++) {
      assertEquals(names.get(index), values.get(index).name());
      assertSame(values.get(index), JmsRequestReplyException.Reason.valueOf(names.get(index)));
      var plain = new JmsRequestReplyException(values.get(index), TEXT);
      var cause = new IllegalStateException(TEXT);
      var caused = new JmsRequestReplyException(values.get(index), TEXT, cause);
      var explicitNull = new JmsRequestReplyException(values.get(index), TEXT, null);
      assertSame(values.get(index), plain.reason());
      assertSame(values.get(index), caused.reason());
      assertSame(values.get(index), explicitNull.reason());
      assertEquals(TEXT, plain.getMessage());
      assertEquals(TEXT, caused.getMessage());
      assertEquals(TEXT, explicitNull.getMessage());
      assertNull(plain.getCause());
      assertNull(explicitNull.getCause());
      assertSame(cause, caused.getCause());
      assertEquals(0, plain.getSuppressed().length);
      assertEquals(0, caused.getSuppressed().length);
    }
    var copy = JmsRequestReplyException.Reason.values();
    copy[0] = JmsRequestReplyException.Reason.TIMEOUT;
    assertSame(
        JmsRequestReplyException.Reason.CAPACITY, JmsRequestReplyException.Reason.values()[0]);
    for (String unknown : List.of("", "UNKNOWN", "capacity", "CAPACITY "))
      assertThrows(
          IllegalArgumentException.class, () -> JmsRequestReplyException.Reason.valueOf(unknown));
    assertThrows(NullPointerException.class, () -> JmsRequestReplyException.Reason.valueOf(null));
    assertThrows(NullPointerException.class, () -> new JmsRequestReplyException(null, TEXT));
    assertThrows(NullPointerException.class, () -> new JmsRequestReplyException(null, TEXT, null));
  }

  @Test
  void jmsgraph002FatalIdentityPrecedenceAndNonfatalCyclesAreFiniteAndUnmodified() {
    for (int kind = 0; kind < 7; kind++) {
      var fatal = new AssertionError(TEXT);
      Throwable root;
      switch (kind) {
        case 0 -> root = fatal;
        case 1 -> root = new IllegalStateException(TEXT, fatal);
        case 2 -> {
          root = new IllegalStateException(TEXT);
          root.addSuppressed(fatal);
        }
        case 3 -> {
          var sql = new SQLException(TEXT);
          sql.setNextException(new SQLException(TEXT, fatal));
          root = sql;
        }
        case 4 -> {
          var jms = new JMSException(TEXT);
          jms.setLinkedException(new IllegalStateException(TEXT, fatal));
          root = jms;
        }
        case 5 -> {
          var sql = new SQLException(TEXT);
          sql.setNextException(new SQLException(TEXT, fatal));
          var jms = new JMSException(TEXT);
          jms.setLinkedException(sql);
          root = jms;
        }
        case 6 -> {
          root = new IllegalStateException(TEXT, fatal);
          root.addSuppressed(new AssertionError("public second fatal"));
        }
        default -> throw new AssertionError(TEXT);
      }
      assertSame(
          fatal,
          assertThrows(AssertionError.class, () -> JmsRequestReplyException.preserveFatal(root)));
      assertEquals(0, fatal.getSuppressed().length);
    }
    var first = new IllegalStateException(TEXT);
    var second = new IllegalArgumentException(TEXT, first);
    first.initCause(second);
    var sqlFirst = new SQLException(TEXT);
    var sqlSecond = new SQLException(TEXT);
    sqlFirst.setNextException(sqlSecond);
    sqlSecond.setNextException(sqlFirst);
    var jmsFirst = new JMSException(TEXT);
    var jmsSecond = new JMSException(TEXT);
    jmsFirst.setLinkedException(jmsSecond);
    jmsSecond.setLinkedException(jmsFirst);
    first.addSuppressed(sqlFirst);
    first.addSuppressed(jmsFirst);
    second.addSuppressed(jmsSecond);
    assertDoesNotThrow(() -> JmsRequestReplyException.preserveFatal(first));
    assertSame(second, first.getCause());
    assertSame(first, second.getCause());
    assertSame(sqlSecond, sqlFirst.getNextException());
    assertSame(sqlFirst, sqlSecond.getNextException());
    assertSame(jmsSecond, jmsFirst.getLinkedException());
    assertSame(jmsFirst, jmsSecond.getLinkedException());
    assertDoesNotThrow(() -> JmsRequestReplyException.preserveFatal(new SQLException(TEXT)));
    assertDoesNotThrow(() -> JmsRequestReplyException.preserveFatal(new JMSException(TEXT)));
    assertThrows(NullPointerException.class, () -> JmsRequestReplyException.preserveFatal(null));
  }
}
