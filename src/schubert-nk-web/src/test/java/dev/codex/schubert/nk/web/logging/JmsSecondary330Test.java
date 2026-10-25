package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.messaging.ArtemisRequestSender;
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

/** MQ003008/MON003/UI231242/SS312321324354/SSC321323330; PT-JMS330004..009; BUG1598/YKT1351. */
final class JmsSecondary330Test {
  @Test
  void jms330004LogDisabledPrimaryCannotLoseRollbackOrCloseFatal() {
    for (int kind = 0; kind < 3; kind++) {
      for (boolean duringClose : new boolean[] {false, true}) {
        var fatal = new AssertionError("PUBLIC secondary fatal");
        var state = new Fixture();
        if (duringClose) {
          state.mode = new NoSuppression(null);
          state.closing = graph(fatal, kind);
        } else {
          state.stage = new NoSuppression(null);
          state.rollback = graph(fatal, kind);
        }
        Throwable actual = state.log();
        state.assertCounts(duringClose ? 0 : 1, 0, duringClose ? 0 : 1);
        assertTrue(disposition(actual) == fatal);
        state.assertWiped();
      }
    }
  }

  @Test
  void jms330005LogDuplicateCannotHideRollbackFatalAndDirectCloseStillWins() {
    for (boolean disabled : new boolean[] {false, true}) {
      for (boolean directClose : new boolean[] {false, true}) {
        var fatal = new AssertionError("PUBLIC rollback fatal");
        var closing = new AssertionError("PUBLIC direct close fatal");
        var duplicate = new ActiveMQDuplicateIdException("PUBLIC duplicate");
        var state = new Fixture();
        state.commit = disabled ? new NoSuppression(duplicate) : new RuntimeException(duplicate);
        state.rollback = graph(fatal, 1);
        if (directClose) state.closing = closing;
        Throwable actual = state.log();
        state.assertCounts(1, 1, 1);
        state.assertWiped();
        assertTrue(disposition(actual) == (directClose ? closing : fatal));
      }
    }
  }

  @Test
  void jms330006LogNonfatalDuplicateAndDirectPrimaryPriorityRetainWipe() {
    var success = new Fixture();
    assertNull(success.log());
    success.assertCounts(1, 1, 0);
    success.assertWiped();
    var duplicate = new Fixture();
    duplicate.commit = new RuntimeException(new ActiveMQDuplicateIdException("PUBLIC duplicate"));
    assertNull(duplicate.log());
    duplicate.assertCounts(1, 1, 1);
    duplicate.assertWiped();
    var notConfirmed = new Fixture();
    var primary = new RuntimeException("PUBLIC ordinary commit");
    primary.addSuppressed(new ActiveMQDuplicateIdException("PUBLIC suppressed only"));
    notConfirmed.commit = primary;
    assertSame(primary, assertInstanceOf(WebLogSendException.class, notConfirmed.log()).getCause());
    notConfirmed.assertCounts(1, 1, 1);
    notConfirmed.assertWiped();
    var same = new Fixture();
    same.stage = new NoSuppression(null);
    same.rollback = same.stage;
    assertSame(same.stage, assertInstanceOf(WebLogSendException.class, same.log()).getCause());
    same.assertCounts(1, 0, 1);
    same.assertWiped();
    var fatal = new AssertionError("PUBLIC primary");
    var direct = new Fixture();
    direct.stage = fatal;
    direct.closing = new AssertionError("PUBLIC closing");
    assertSame(fatal, direct.log());
    direct.assertCounts(1, 0, 0);
    direct.assertWiped();
  }

  @Test
  void jms330007RequestRetainsDisabledPrimaryRollbackFatalAfterOwnedClose() {
    for (int kind = 0; kind < 3; kind++) {
      for (boolean directClose : new boolean[] {false, true}) {
        var fatal = new AssertionError("PUBLIC rollback fatal");
        var closing = new AssertionError("PUBLIC direct close fatal");
        var state = new Fixture();
        state.stage = new NoSuppression(null);
        state.rollback = graph(fatal, kind);
        if (directClose) state.closing = closing;
        byte[] input = request();
        byte[] before = input.clone();
        Throwable actual = state.request(input);
        state.assertCounts(1, 0, 1);
        assertArrayEquals(before, input);
        assertTrue(actual == (directClose ? closing : fatal));
      }
    }
  }

  @Test
  void jms330008RequestClassifiesCloseGraphAfterModeFailureOrSuccessfulCommit() {
    for (int kind = 0; kind < 3; kind++) {
      for (boolean modeFailure : new boolean[] {false, true}) {
        var fatal = new AssertionError("PUBLIC close fatal");
        var state = new Fixture();
        state.closing = graph(fatal, kind);
        if (modeFailure) state.mode = new NoSuppression(null);
        byte[] input = request();
        byte[] before = input.clone();
        Throwable actual = state.request(input);
        state.assertCounts(modeFailure ? 0 : 1, modeFailure ? 0 : 1, 0);
        assertArrayEquals(before, input);
        assertTrue(actual == fatal);
      }
    }
  }

  @Test
  void jms330009RequestNonfatalCyclesDirectPrioritiesAndCallerWireStayUnchanged() {
    var success = new Fixture();
    byte[] input = request();
    byte[] before = input.clone();
    assertNull(success.request(input));
    success.assertCounts(1, 1, 0);
    assertArrayEquals(before, input);
    assertEquals(5_000L, success.ttl);
    assertEquals(2, success.delivery);
    assertEquals("LOGREQ01", success.layout);
    assertEquals("001", success.version);
    assertEquals(ID.toString(), success.correlation);
    assertEquals(ID.toString(), success.message);
    var first = new JMSException("PUBLIC linked cycle");
    var second = new JMSException("PUBLIC linked cycle");
    first.setLinkedException(second);
    second.setLinkedException(first);
    var ordinary = new NoSuppression(first);
    var cycle = new Fixture();
    cycle.stage = ordinary;
    cycle.rollback = ordinary;
    assertSame(ordinary, cycle.request(request()));
    cycle.assertCounts(1, 0, 1);
    var direct = new Fixture();
    var fatal = new AssertionError("PUBLIC primary");
    direct.stage = fatal;
    direct.closing = new AssertionError("PUBLIC close");
    assertSame(fatal, direct.request(request()));
    direct.assertCounts(1, 0, 0);
    var close = new Fixture();
    close.stage = new NoSuppression(null);
    var closing = new AssertionError("PUBLIC close");
    close.closing = closing;
    assertSame(closing, close.request(request()));
    close.assertCounts(1, 0, 1);
  }

  private static @Nullable Throwable disposition(@Nullable Throwable failure) {
    if (failure == null) return null;
    try {
      WebLogDispatcher.preserveFatal(failure);
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

  private static final UUID ID = UUID.fromString("00000000-0000-0000-0000-000000000001");

  private static final class Fixture {
    @Nullable Throwable mode;
    @Nullable Throwable stage;
    @Nullable Throwable commit;
    @Nullable Throwable rollback;
    @Nullable Throwable closing;
    @Nullable byte[] written;
    @Nullable String correlation;
    @Nullable String message;
    @Nullable String layout;
    @Nullable String version;
    long ttl;
    int delivery;
    int opens;
    int writes;
    int sends;
    int commits;
    int rollbacks;
    int closes;
    int unexpected;

    @Nullable Throwable log() {
      var codec = new WebLogPayloadCodec("public-fixture", new byte[32], null, null);
      var identity =
          new WebLogPayloadIdentity(
              UUID.fromString("00000000-0000-0000-0000-000000000012"),
              UUID.fromString("00000000-0000-0000-0000-000000000015"));
      var now = Instant.parse("2026-09-05T12:00:00Z");
      var row =
          new ClaimedWebLog(
              1,
              identity,
              codec.encrypt(identity, WebLogPayloadCodecTest.goldenWire()),
              0,
              now,
              now,
              "worker",
              now.plusSeconds(10));
      try {
        new WebLogMessageSender(codec, this::open).send(row);
        return null;
      } catch (Throwable failure) {
        return failure;
      }
    }

    @Nullable Throwable request(byte[] wire) {
      try {
        new ArtemisRequestSender(this::open).send(ID, wire);
        return null;
      } catch (Throwable failure) {
        return failure;
      }
    }

    JMSContext open() {
      opens++;
      BytesMessage bytes =
          proxy(
              BytesMessage.class,
              (self, method, args) -> {
                switch (method) {
                  case "writeBytes" -> {
                    writes++;
                    written = (byte[]) args[0];
                  }
                  case "setJMSCorrelationID" -> correlation = (String) args[0];
                  case "setJMSReplyTo" -> {}
                  case "setStringProperty" -> {
                    switch ((String) args[0]) {
                      case "NKMessageID" -> message = (String) args[1];
                      case "NKLayoutID" -> layout = (String) args[1];
                      case "NKProtocolVersion" -> version = (String) args[1];
                      case "_AMQ_DUPL_ID" -> {}
                      default -> {
                        unexpected++;
                        throw new AssertionError("unexpected property");
                      }
                    }
                  }
                  default -> {
                    unexpected++;
                    throw new AssertionError("unexpected BytesMessage method");
                  }
                }
                return null;
              });
      JMSProducer producer =
          proxy(
              JMSProducer.class,
              (self, method, args) -> {
                switch (method) {
                  case "setDeliveryMode" -> delivery = (Integer) args[0];
                  case "setTimeToLive" -> ttl = (Long) args[0];
                  case "send" -> {
                    sends++;
                    raise(stage);
                  }
                  default -> {
                    unexpected++;
                    throw new AssertionError("unexpected JMSProducer method");
                  }
                }
                return self;
              });
      return proxy(
          JMSContext.class,
          (self, method, args) -> {
            return switch (method) {
              case "getSessionMode" -> {
                raise(mode);
                yield JMSContext.SESSION_TRANSACTED;
              }
              case "createBytesMessage" -> bytes;
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

    void assertCounts(int staged, int expectedCommits, int expectedRollbacks) {
      assertEquals(0, unexpected);
      assertEquals(1, opens);
      assertEquals(staged, writes);
      assertEquals(staged, sends);
      assertEquals(expectedCommits, commits);
      assertEquals(expectedRollbacks, rollbacks);
      assertEquals(1, closes);
    }

    void assertWiped() {
      if (written != null) assertArrayEquals(new byte[written.length], written);
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

  private static byte[] request() {
    byte[] bytes = new byte[256];
    Arrays.fill(bytes, (byte) ' ');
    put(bytes, 0, "SCHBNK01");
    put(bytes, 8, "001");
    put(bytes, 11, "LOGREQ01");
    put(bytes, 19, "001");
    put(bytes, 22, "QS");
    put(bytes, 24, ID.toString());
    put(bytes, 60, ID.toString());
    put(bytes, 96, "20260903120000000");
    put(bytes, 113, "a".repeat(64));
    put(bytes, 177, "0256");
    put(bytes, 181, "000000");
    put(bytes, 187, "000000");
    put(bytes, 193, "000000");
    put(bytes, 199, "000000256");
    return bytes;
  }

  private static void put(byte[] bytes, int offset, String value) {
    byte[] text = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(text, 0, bytes, offset, text.length);
  }
}
