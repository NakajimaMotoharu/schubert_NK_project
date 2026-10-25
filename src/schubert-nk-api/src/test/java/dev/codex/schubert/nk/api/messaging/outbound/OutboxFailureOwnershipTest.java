package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSProducer;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** NK-MSG-002/MQ006008/ASY001/UI213241242/SS324332354/SSC320; PT-IDEM-FAIL320001..006. */
final class OutboxFailureOwnershipTest {
  private static final Instant NOW = Instant.parse("2026-09-05T12:00:00Z");
  private static final Clock CLOCK = Clock.fixed(NOW, ZoneOffset.UTC);
  private static final UUID MESSAGE = UUID.fromString("00000000-0000-4000-8000-000000000001");
  private static final UUID CORRELATION = UUID.fromString("00000000-0000-4000-8000-000000000002");

  @Test
  void fail320001NonfatalJmsPrimaryCannotHideCleanupError() {
    for (int kind = 0; kind < 2; kind++) {
      RuntimeException primary =
          kind == 0
              ? new IllegalStateException("fixture mode")
              : new jakarta.jms.JMSRuntimeException("fixture mode");
      var secondary = new AssertionError("fixture close");
      var state = new JmsState(primary, secondary);
      assertSame(
          secondary,
          assertThrows(Error.class, () -> new OutboxJmsSender().send(state::open, entry())));
      assertEquals(1, secondary.getSuppressed().length);
      var retained = assertInstanceOf(OutboxSendException.class, secondary.getSuppressed()[0]);
      assertSame(primary, retained.getCause());
      state.assertBeforeStage();
    }
  }

  @Test
  void fail320002UnreturnedJdbcSetupErrorClosesExactlyOnce() {
    for (int kind = 0; kind < 3; kind++) {
      var primary = fault(kind);
      var state = new SqlState(primary, null, null, null);
      assertSame(primary, assertThrows(Throwable.class, () -> state.dispatch()));
      state.assertSetupFailure();
      assertEquals(0, primary.getSuppressed().length);
    }
  }

  @Test
  void fail320003JdbcSetupCompoundFailuresPreserveIdentity() {
    for (int primaryKind = 0; primaryKind < 3; primaryKind++) {
      for (int closingKind = 0; closingKind < 4; closingKind++) {
        var primary = fault(primaryKind);
        var closing = closingKind == 3 ? primary : fault(closingKind);
        var state = new SqlState(primary, null, null, closing);
        var actual = assertThrows(Throwable.class, () -> state.dispatch());
        assertCombined(primary, closing, actual);
        state.assertSetupFailure();
      }
    }
  }

  @Test
  void fail320004RollbackCompoundFailuresNeverSelfSuppress() {
    for (int primaryKind = 0; primaryKind < 2; primaryKind++) {
      for (int rollbackKind = 0; rollbackKind < 4; rollbackKind++) {
        var primary = fault(primaryKind);
        var secondary = rollbackKind == 3 ? primary : fault(rollbackKind);
        var state = new SqlState(null, primary, secondary, null);
        var actual = assertThrows(Throwable.class, () -> state.dispatch());
        assertCombined(primary, secondary, actual);
        assertEquals(1, state.opens.get());
        assertEquals(1, state.setup.get());
        assertEquals(1, state.prepare.get());
        assertEquals(1, state.rollbacks.get());
        assertEquals(1, state.closes.get());
        assertEquals(0, state.commits.get());
        assertEquals(0, state.jms.get());
      }
    }
  }

  @Test
  void fail320005JmsFatalPrimarySurvivesEveryClose() {
    for (int closingKind = 0; closingKind < 4; closingKind++) {
      var primary = new AssertionError("fixture original fatal");
      @Nullable Throwable closing =
          switch (closingKind) {
            case 1 -> new IllegalStateException("fixture close");
            case 2 -> new AssertionError("fixture secondary fatal");
            case 3 -> primary;
            default -> null;
          };
      var state = new JmsState(primary, closing);
      assertSame(
          primary,
          assertThrows(Error.class, () -> new OutboxJmsSender().send(state::open, entry())));
      assertEquals(closing == null || closing == primary ? 0 : 1, primary.getSuppressed().length);
      if (closing != null && closing != primary) assertSame(closing, primary.getSuppressed()[0]);
      state.assertBeforeStage();
    }
  }

  @Test
  void fail320006NormalSendCommitsAndClosesWithoutRetry() throws Exception {
    var state = new JmsState(null, null);
    new OutboxJmsSender().send(state::open, entry());
    assertEquals(1, state.opens.get());
    assertEquals(1, state.sends.get());
    assertEquals(1, state.commits.get());
    assertEquals(0, state.rollbacks.get());
    assertEquals(1, state.closes.get());
    assertArrayEquals(golden(), state.wire);
    assertEquals(CORRELATION.toString(), state.properties.get("correlation"));
    assertEquals(MESSAGE.toString(), state.properties.get("NKMessageID"));
    assertEquals(MESSAGE.toString(), state.properties.get("_AMQ_DUPL_ID"));
    assertEquals("QWKREQ01", state.properties.get("NKLayoutID"));
    assertEquals("001", state.properties.get("NKProtocolVersion"));
  }

  private static Throwable fault(int kind) {
    return switch (kind) {
      case 0 -> new SQLException("fixture SQL");
      case 1 -> new IllegalStateException("fixture runtime");
      default -> new AssertionError("fixture fatal");
    };
  }

  private static void assertCombined(Throwable primary, Throwable secondary, Throwable actual) {
    var expected = secondary instanceof Error && !(primary instanceof Error) ? secondary : primary;
    assertSame(expected, actual, "fatal class/primary identity is not retryable wrapper identity");
    assertEquals(primary == secondary ? 0 : 1, actual.getSuppressed().length);
    if (primary != secondary)
      assertSame(actual == primary ? secondary : primary, actual.getSuppressed()[0]);
  }

  private static OutboxEntry entry() {
    return new OutboxEntry(
        1,
        MESSAGE,
        CORRELATION,
        OutboxDestination.ASYNC_WORK,
        "QWKREQ01",
        "001",
        golden(),
        0,
        NOW,
        NOW.minusSeconds(30),
        "worker",
        NOW.plusSeconds(10));
  }

  private static byte[] golden() {
    // SS323 literal offsets/lengths, never an encoder-derived expected value.
    byte[] body = new byte[320];
    Arrays.fill(body, (byte) ' ');
    ascii(body, 0, "SCHBNK01");
    ascii(body, 8, "001");
    ascii(body, 11, "QWKREQ01");
    ascii(body, 19, "001");
    ascii(body, 22, "EI");
    ascii(body, 24, MESSAGE.toString());
    ascii(body, 60, CORRELATION.toString());
    ascii(body, 96, "20260905120000000");
    ascii(body, 177, "0256");
    ascii(body, 181, "000064");
    ascii(body, 187, "000000");
    ascii(body, 193, "000000");
    ascii(body, 199, "000000320");
    ascii(body, 256, "01ARZ3NDEKTSV4RRFFQ69G5FAV");
    ascii(body, 282, "000000000001");
    ascii(body, 294, "000000000002");
    return body;
  }

  private static void ascii(byte[] body, int offset, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(bytes, 0, body, offset, bytes.length);
  }

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }

  private static final class SqlState {
    private final AtomicInteger opens = new AtomicInteger();
    private final AtomicInteger setup = new AtomicInteger();
    private final AtomicInteger prepare = new AtomicInteger();
    private final AtomicInteger rollbacks = new AtomicInteger();
    private final AtomicInteger closes = new AtomicInteger();
    private final AtomicInteger commits = new AtomicInteger();
    private final AtomicInteger jms = new AtomicInteger();
    private final Connection connection;

    private SqlState(
        @Nullable Throwable setupFailure,
        @Nullable Throwable claimFailure,
        @Nullable Throwable rollbackFailure,
        @Nullable Throwable closeFailure) {
      connection =
          proxy(
              Connection.class,
              (object, method, args) -> {
                switch (method.getName()) {
                  case "setAutoCommit" -> {
                    assertFalse((Boolean) args[0]);
                    setup.incrementAndGet();
                    if (setupFailure != null) throw setupFailure;
                  }
                  case "getAutoCommit", "isReadOnly" -> {
                    return false;
                  }
                  case "prepareStatement" -> {
                    prepare.incrementAndGet();
                    if (claimFailure != null) throw claimFailure;
                    throw new AssertionError("unexpected SQL stage");
                  }
                  case "rollback" -> {
                    rollbacks.incrementAndGet();
                    if (rollbackFailure != null) throw rollbackFailure;
                  }
                  case "close" -> {
                    closes.incrementAndGet();
                    if (closeFailure != null) throw closeFailure;
                  }
                  case "commit" -> commits.incrementAndGet();
                  case "toString" -> {
                    return "owned-jdbc-fixture";
                  }
                  default -> throw new AssertionError("unexpected JDBC method " + method.getName());
                }
                return null;
              });
    }

    private void dispatch() throws SQLException {
      new OutboxDispatcher(
              () -> {
                opens.incrementAndGet();
                return connection;
              },
              () -> {
                jms.incrementAndGet();
                throw new AssertionError("unexpected JMS stage");
              },
              new JdbcOutboxRepository(
                  () -> {
                    throw new AssertionError("unexpected jitter");
                  }),
              new OutboxJmsSender(),
              CLOCK)
          .dispatch("worker", 1);
    }

    private void assertSetupFailure() {
      assertEquals(1, opens.get());
      assertEquals(1, setup.get());
      assertEquals(1, closes.get());
      assertEquals(0, prepare.get());
      assertEquals(0, commits.get());
      assertEquals(0, rollbacks.get());
      assertEquals(0, jms.get());
    }
  }

  private static final class JmsState {
    private final AtomicInteger opens = new AtomicInteger();
    private final AtomicInteger closes = new AtomicInteger();
    private final AtomicInteger commits = new AtomicInteger();
    private final AtomicInteger rollbacks = new AtomicInteger();
    private final AtomicInteger sends = new AtomicInteger();
    private final Map<String, String> properties = new HashMap<>();
    private byte[] wire = new byte[0];
    private final JMSContext context;

    private JmsState(@Nullable Throwable modeFailure, @Nullable Throwable closeFailure) {
      BytesMessage message =
          proxy(
              BytesMessage.class,
              (object, method, args) -> {
                switch (method.getName()) {
                  case "writeBytes" -> wire = ((byte[]) args[0]).clone();
                  case "setJMSCorrelationID" -> properties.put("correlation", (String) args[0]);
                  case "setStringProperty" -> properties.put((String) args[0], (String) args[1]);
                  default ->
                      throw new AssertionError("unexpected message method " + method.getName());
                }
                return null;
              });
      JMSProducer producer =
          proxy(
              JMSProducer.class,
              (object, method, args) -> {
                switch (method.getName()) {
                  case "setDeliveryMode" -> assertEquals(DeliveryMode.PERSISTENT, args[0]);
                  case "setTimeToLive" -> assertEquals(0L, args[0]);
                  case "send" -> {
                    assertEquals(
                        "nk.async.work::nk.async.work.q",
                        ((org.apache.activemq.artemis.jms.client.ActiveMQQueue) args[0]).getName());
                    assertSame(message, args[1]);
                    sends.incrementAndGet();
                  }
                  default ->
                      throw new AssertionError("unexpected producer method " + method.getName());
                }
                return object;
              });
      context =
          proxy(
              JMSContext.class,
              (object, method, args) -> {
                switch (method.getName()) {
                  case "getSessionMode" -> {
                    if (modeFailure != null) throw modeFailure;
                    return JMSContext.SESSION_TRANSACTED;
                  }
                  case "createBytesMessage" -> {
                    return message;
                  }
                  case "createProducer" -> {
                    return producer;
                  }
                  case "close" -> {
                    closes.incrementAndGet();
                    if (closeFailure != null) throw closeFailure;
                  }
                  case "commit" -> commits.incrementAndGet();
                  case "rollback" -> rollbacks.incrementAndGet();
                  default -> throw new AssertionError("unexpected JMS method " + method.getName());
                }
                return null;
              });
    }

    private JMSContext open() {
      opens.incrementAndGet();
      return context;
    }

    private void assertBeforeStage() {
      assertEquals(1, opens.get());
      assertEquals(1, closes.get());
      assertEquals(0, sends.get());
      assertEquals(0, commits.get());
      assertEquals(0, rollbacks.get());
    }
  }
}
