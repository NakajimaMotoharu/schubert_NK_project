package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.BytesMessage;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSProducer;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Arrays;
import java.util.UUID;
import org.apache.activemq.artemis.api.core.ActiveMQDuplicateIdException;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** MQ006008/UI242/SS312324354/SSC320322330; PT-JMS330001..003; BUG1598/YKT1351. */
final class OutboxSecondary330Test {
  @Test
  void jms330001DisabledPrimaryRetainsRollbackFatalThroughFinalDisposition() {
    for (int kind = 0; kind < 3; kind++) {
      for (boolean directClose : new boolean[] {false, true}) {
        var fatal = new AssertionError("PUBLIC rollback fatal");
        var closing = new AssertionError("PUBLIC direct close fatal");
        var state = new Fixture();
        state.stage = new NoSuppression(null);
        state.rollback = graph(fatal, kind);
        if (directClose) state.closing = closing;
        Throwable actual = state.send();
        state.assertCounts(0, 1);
        assertTrue(disposition(actual) == (directClose ? closing : fatal));
      }
    }
  }

  @Test
  void jms330002DuplicateCannotConfirmSuccessBeforeRollbackFatalClassification() {
    for (boolean disabled : new boolean[] {false, true}) {
      for (boolean directClose : new boolean[] {false, true}) {
        var duplicate = new ActiveMQDuplicateIdException("PUBLIC duplicate");
        var fatal = new AssertionError("PUBLIC rollback fatal");
        var closing = new AssertionError("PUBLIC direct close fatal");
        var state = new Fixture();
        state.commit = disabled ? new NoSuppression(duplicate) : new RuntimeException(duplicate);
        state.rollback = graph(fatal, 1);
        if (directClose) state.closing = closing;
        Throwable actual = state.send();
        state.assertCounts(1, 1);
        assertTrue(disposition(actual) == (directClose ? closing : fatal));
      }
    }
  }

  @Test
  void jms330003NonfatalCyclesDuplicateEvidenceAndDirectCleanupPriorityStayUnchanged() {
    var success = new Fixture();
    assertNull(success.send());
    success.assertCounts(1, 0);
    var duplicate = new Fixture();
    duplicate.commit = new RuntimeException(new ActiveMQDuplicateIdException("PUBLIC duplicate"));
    assertNull(duplicate.send());
    duplicate.assertCounts(1, 1);
    var notConfirmed = new Fixture();
    var primary = new RuntimeException("PUBLIC ordinary commit");
    primary.addSuppressed(new ActiveMQDuplicateIdException("PUBLIC suppressed only"));
    notConfirmed.commit = primary;
    assertSame(
        primary, assertInstanceOf(OutboxSendException.class, notConfirmed.send()).getCause());
    notConfirmed.assertCounts(1, 1);
    var cycle = new Fixture();
    var first = new JMSException("PUBLIC linked cycle");
    var second = new JMSException("PUBLIC linked cycle");
    first.setLinkedException(second);
    second.setLinkedException(first);
    var ordinary = new NoSuppression(first);
    cycle.stage = ordinary;
    cycle.rollback = ordinary;
    Throwable actual = cycle.send();
    cycle.assertCounts(0, 1);
    assertSame(ordinary, assertInstanceOf(OutboxSendException.class, actual).getCause());
    assertSame(actual, disposition(actual));
    for (int closeKind = 0; closeKind < 3; closeKind++) {
      var direct = new AssertionError("PUBLIC primary");
      var state = new Fixture();
      state.stage = direct;
      state.closing =
          closeKind == 0
              ? direct
              : closeKind == 1
                  ? graph(new AssertionError("PUBLIC nested"), 2)
                  : new AssertionError("PUBLIC closing");
      actual = state.send();
      state.assertCounts(0, 0);
      assertSame(direct, actual);
    }
  }

  private static @Nullable Throwable disposition(@Nullable Throwable failure) {
    if (failure == null) return null;
    try {
      OutboxDispatcher.preserveFatal(failure);
      return failure;
    } catch (Error fatal) {
      return fatal;
    }
  }

  private static RuntimeException graph(Error fatal, int kind) {
    if (kind == 0) return new RuntimeException(fatal);
    if (kind == 1) {
      var jms = new JMSException("PUBLIC linked");
      jms.setLinkedException(new Exception(fatal));
      return new RuntimeException(jms);
    }
    var sql = new SQLException("PUBLIC SQL next");
    sql.setNextException(new SQLException("PUBLIC next", fatal));
    return new RuntimeException(sql);
  }

  private static final class NoSuppression extends RuntimeException {
    private static final long serialVersionUID = 1L;

    NoSuppression(@Nullable Throwable cause) {
      super("PUBLIC primary", cause, false, false);
    }
  }

  private static final class Fixture {
    @Nullable Throwable stage;
    @Nullable Throwable commit;
    @Nullable Throwable rollback;
    @Nullable Throwable closing;
    int opens;
    int writes;
    int sends;
    int commits;
    int rollbacks;
    int closes;
    int unexpected;

    @Nullable Throwable send() {
      try {
        new OutboxJmsSender().send(this::open, entry());
        return null;
      } catch (Throwable failure) {
        return failure;
      }
    }

    JMSContext open() {
      opens++;
      BytesMessage message =
          proxy(
              BytesMessage.class,
              (self, method, args) -> {
                if (method.equals("writeBytes")) {
                  writes++;
                  return null;
                }
                if (method.equals("setJMSCorrelationID") || method.equals("setStringProperty"))
                  return null;
                unexpected++;
                throw new AssertionError("unexpected BytesMessage method");
              });
      JMSProducer producer =
          proxy(
              JMSProducer.class,
              (self, method, args) -> {
                if (method.equals("setDeliveryMode") || method.equals("setTimeToLive")) return self;
                if (method.equals("send")) {
                  sends++;
                  raise(stage);
                  return self;
                }
                unexpected++;
                throw new AssertionError("unexpected JMSProducer method");
              });
      return proxy(
          JMSContext.class,
          (self, method, args) -> {
            return switch (method) {
              case "getSessionMode" -> JMSContext.SESSION_TRANSACTED;
              case "createBytesMessage" -> message;
              case "createProducer" -> producer;
              case "commit" -> {
                commits++;
                raise(commit);
                yield null;
              }
              case "rollback" -> {
                rollbacks++;
                raise(rollback);
                yield null;
              }
              case "close" -> {
                closes++;
                raise(closing);
                yield null;
              }
              default -> {
                unexpected++;
                throw new AssertionError("unexpected JMSContext method");
              }
            };
          });
    }

    void assertCounts(int expectedCommits, int expectedRollbacks) {
      assertEquals(0, unexpected);
      assertEquals(1, opens);
      assertEquals(1, writes);
      assertEquals(1, sends);
      assertEquals(expectedCommits, commits);
      assertEquals(expectedRollbacks, rollbacks);
      assertEquals(1, closes);
    }
  }

  private interface Call {
    @Nullable Object invoke(Object self, String method, Object[] args) throws Throwable;
  }

  private static <T> T proxy(Class<T> type, Call call) {
    return type.cast(
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (self, method, args) ->
                call.invoke(self, method.getName(), args == null ? new Object[0] : args)));
  }

  private static void raise(@Nullable Throwable failure) throws Throwable {
    if (failure != null) throw failure;
  }

  private static OutboxEntry entry() {
    var now = Instant.parse("2026-09-05T12:00:00Z");
    var message = UUID.fromString("00000000-0000-4000-8000-000000000001");
    var correlation = UUID.fromString("00000000-0000-4000-8000-000000000002");
    byte[] bytes = new byte[320];
    Arrays.fill(bytes, (byte) ' ');
    put(bytes, 0, "SCHBNK01");
    put(bytes, 8, "001");
    put(bytes, 11, "QWKREQ01");
    put(bytes, 19, "001");
    put(bytes, 22, "EI");
    put(bytes, 24, message.toString());
    put(bytes, 60, correlation.toString());
    put(bytes, 96, "20260905120000000");
    put(bytes, 177, "0256");
    put(bytes, 181, "000064");
    put(bytes, 187, "000000");
    put(bytes, 193, "000000");
    put(bytes, 199, "000000320");
    put(bytes, 256, "01ARZ3NDEKTSV4RRFFQ69G5FAV");
    put(bytes, 282, "000000000001");
    put(bytes, 294, "000000000002");
    return new OutboxEntry(
        1,
        message,
        correlation,
        OutboxDestination.ASYNC_WORK,
        "QWKREQ01",
        "001",
        bytes,
        0,
        now,
        now.minusSeconds(30),
        "worker",
        now.plusSeconds(10));
  }

  private static void put(byte[] bytes, int offset, String value) {
    byte[] text = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(text, 0, bytes, offset, text.length);
  }
}
