package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSProducer;
import jakarta.jms.JMSRuntimeException;
import jakarta.jms.Queue;
import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQDestination;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-JMS-005/006 production request sender transaction and transport tests. */
final class ArtemisRequestSenderTest {
  private static final UUID MESSAGE_ID = UUID.fromString("00000000-0000-0000-0000-000000000001");

  @Test
  @DisplayName("PT-JMS-005 production sender commits exact persistent request properties")
  void sendsOneValidatedPersistentRequestAndCommits(@TempDir Path root) throws Exception {
    byte[] expectedBody = independentRequestWire();
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory("vm://0")) {
      ArtemisRequestSender sender =
          new ArtemisRequestSender(() -> factory.createContext(JMSContext.SESSION_TRANSACTED));
      long beforeSend = System.currentTimeMillis();
      sender.send(MESSAGE_ID, expectedBody);

      Queue requestQueue =
          new org.apache.activemq.artemis.jms.client.ActiveMQQueue(
              "nk.sync.request::nk.sync.request.q");
      try (JMSContext receive = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
          var consumer = receive.createConsumer(requestQueue)) {
        BytesMessage actual = (BytesMessage) consumer.receive(5_000);
        assertNotNull(actual);
        byte[] actualBody = new byte[Math.toIntExact(actual.getBodyLength())];
        actual.readBytes(actualBody);
        assertArrayEquals(expectedBody, actualBody);
        assertEquals(MESSAGE_ID.toString(), actual.getJMSCorrelationID());
        assertEquals(
            "nk.sync.reply.web", ((ActiveMQDestination) actual.getJMSReplyTo()).getAddress());
        assertEquals(MESSAGE_ID.toString(), actual.getStringProperty("NKMessageID"));
        assertEquals("LOGREQ01", actual.getStringProperty("NKLayoutID"));
        assertEquals("001", actual.getStringProperty("NKProtocolVersion"));
        assertEquals(DeliveryMode.PERSISTENT, actual.getJMSDeliveryMode());
        assertTrue(
            actual.getJMSExpiration()
                >= beforeSend + ArtemisRequestSender.REQUEST_TIME_TO_LIVE_MILLIS - 500);
        assertTrue(
            actual.getJMSExpiration()
                <= beforeSend + ArtemisRequestSender.REQUEST_TIME_TO_LIVE_MILLIS + 2_000);
      }
    } finally {
      broker.stop();
    }
  }

  @Test
  void nullWireIdentityLengthKindAndSessionModeFailBeforeCommit() throws Exception {
    byte[] request = independentRequestWire();
    AtomicBoolean opened = new AtomicBoolean();
    ArtemisRequestSender unopened =
        new ArtemisRequestSender(
            () -> {
              opened.set(true);
              return context(Map.of("getSessionMode", JMSContext.SESSION_TRANSACTED));
            });
    assertThrows(NullPointerException.class, () -> new ArtemisRequestSender(null));
    assertThrows(NullPointerException.class, () -> unopened.send(null, request));
    assertThrows(NullPointerException.class, () -> unopened.send(MESSAGE_ID, null));
    assertFalse(opened.get());

    assertThrows(IllegalArgumentException.class, () -> unopened.send(new UUID(0, 2), request));
    assertThrows(
        IllegalArgumentException.class,
        () -> unopened.send(MESSAGE_ID, Arrays.copyOf(request, request.length + 1)));
    assertThrows(
        IllegalArgumentException.class, () -> unopened.send(MESSAGE_ID, independentResponseWire()));
    assertThrows(
        IllegalArgumentException.class,
        () -> unopened.send(MESSAGE_ID, independentAsyncRequestWire()));
    assertFalse(opened.get());

    ArtemisRequestSender nullContext = new ArtemisRequestSender(() -> null);
    assertThrows(NullPointerException.class, () -> nullContext.send(MESSAGE_ID, request));
    ArtemisRequestSender autoAck =
        new ArtemisRequestSender(
            () -> context(Map.of("getSessionMode", JMSContext.AUTO_ACKNOWLEDGE)));
    assertThrows(IllegalStateException.class, () -> autoAck.send(MESSAGE_ID, request));
  }

  @Test
  void checkedAndRuntimeProviderFailuresRollbackAndPreserveThePrimaryFailure() throws Exception {
    byte[] request = independentRequestWire();
    AtomicBoolean checkedRollback = new AtomicBoolean();
    JMSException checked = new JMSException("synthetic-write-failure");
    BytesMessage failingMessage =
        proxy(
            BytesMessage.class,
            (method, arguments) -> {
              if (method.getName().equals("writeBytes")) {
                throw checked;
              }
              return defaultValue(method.getReturnType());
            });
    ArtemisRequestSender checkedSender =
        new ArtemisRequestSender(
            () ->
                context(
                    Map.of(
                        "getSessionMode",
                        JMSContext.SESSION_TRANSACTED,
                        "createBytesMessage",
                        failingMessage,
                        "rollback",
                        checkedRollback)));
    assertEquals(
        checked, assertThrows(JMSException.class, () -> checkedSender.send(MESSAGE_ID, request)));
    assertTrue(checkedRollback.get());

    JMSRuntimeException runtime = new JMSRuntimeException("synthetic-provider-failure");
    JMSRuntimeException rollback = new JMSRuntimeException("synthetic-rollback-failure");
    ArtemisRequestSender runtimeSender =
        new ArtemisRequestSender(
            () ->
                context(
                    Map.of(
                        "getSessionMode",
                        JMSContext.SESSION_TRANSACTED,
                        "createBytesMessage",
                        runtime,
                        "rollback",
                        rollback)));
    JMSRuntimeException actual =
        assertThrows(JMSRuntimeException.class, () -> runtimeSender.send(MESSAGE_ID, request));
    assertEquals(runtime, actual);
    assertArrayEquals(new Throwable[] {rollback}, actual.getSuppressed());
  }

  @Test
  void jms020aSameFailureReplayedByRollbackCannotMaskPrimary() throws Exception {
    byte[] request = independentRequestWire();
    JMSRuntimeException primary = new JMSRuntimeException("synthetic-primary");
    AtomicInteger rollbackCalls = new AtomicInteger();
    AtomicInteger closeCalls = new AtomicInteger();
    ArtemisRequestSender sameRollback =
        new ArtemisRequestSender(
            () -> failingContext(primary, primary, null, rollbackCalls, closeCalls));
    assertSame(
        primary,
        assertThrows(JMSRuntimeException.class, () -> sameRollback.send(MESSAGE_ID, request)));
    assertEquals(0, primary.getSuppressed().length);
    assertEquals(1, rollbackCalls.get());
    assertEquals(1, closeCalls.get());
  }

  @Test
  void jms020bSameFailureReplayedByCloseCannotMaskPrimary() throws Exception {
    byte[] request = independentRequestWire();
    AtomicInteger rollbackCalls = new AtomicInteger();
    AtomicInteger closeCalls = new AtomicInteger();
    JMSRuntimeException sameClose = new JMSRuntimeException("synthetic-same-close");
    ArtemisRequestSender closeReplaysPrimary =
        new ArtemisRequestSender(
            () -> failingContext(sameClose, null, sameClose, rollbackCalls, closeCalls));
    assertSame(
        sameClose,
        assertThrows(
            JMSRuntimeException.class, () -> closeReplaysPrimary.send(MESSAGE_ID, request)));
    assertEquals(0, sameClose.getSuppressed().length);
    assertEquals(1, rollbackCalls.get());
    assertEquals(1, closeCalls.get());
  }

  @Test
  void jms020dDistinctSecondaryFailuresRemainVisible() throws Exception {
    byte[] request = independentRequestWire();
    JMSRuntimeException primary = new JMSRuntimeException("synthetic-primary");
    JMSRuntimeException rollback = new JMSRuntimeException("synthetic-rollback");
    JMSRuntimeException close = new JMSRuntimeException("synthetic-close");
    AtomicInteger rollbackCalls = new AtomicInteger();
    AtomicInteger closeCalls = new AtomicInteger();
    ArtemisRequestSender compound =
        new ArtemisRequestSender(
            () -> failingContext(primary, rollback, close, rollbackCalls, closeCalls));
    assertSame(
        primary, assertThrows(JMSRuntimeException.class, () -> compound.send(MESSAGE_ID, request)));
    assertArrayEquals(new Throwable[] {rollback, close}, primary.getSuppressed());
    assertEquals(1, rollbackCalls.get());
    assertEquals(1, closeCalls.get());
  }

  @Test
  void jms020cCloseOnlyFailureRemainsVisible() throws Exception {
    byte[] request = independentRequestWire();
    AtomicInteger successfulCloseCalls = new AtomicInteger();
    JMSRuntimeException closeOnly = new JMSRuntimeException("synthetic-close-only");
    ArtemisRequestSender closeOnlySender =
        new ArtemisRequestSender(() -> successfulContext(closeOnly, successfulCloseCalls));
    assertSame(
        closeOnly,
        assertThrows(JMSRuntimeException.class, () -> closeOnlySender.send(MESSAGE_ID, request)));
    assertEquals(1, successfulCloseCalls.get());
  }

  private static JMSContext failingContext(
      JMSRuntimeException primary,
      JMSRuntimeException rollback,
      JMSRuntimeException close,
      AtomicInteger rollbackCalls,
      AtomicInteger closeCalls) {
    return proxy(
        JMSContext.class,
        (method, ignored) ->
            switch (method.getName()) {
              case "getSessionMode" -> JMSContext.SESSION_TRANSACTED;
              case "createBytesMessage" -> throw primary;
              case "rollback" -> {
                rollbackCalls.incrementAndGet();
                if (rollback != null) throw rollback;
                yield null;
              }
              case "close" -> {
                closeCalls.incrementAndGet();
                if (close != null) throw close;
                yield null;
              }
              default -> throw new AssertionError(method.getName());
            });
  }

  private static JMSContext successfulContext(JMSRuntimeException close, AtomicInteger closeCalls) {
    JMSProducer[] producer = new JMSProducer[1];
    producer[0] =
        proxy(
            JMSProducer.class,
            (method, ignored) ->
                switch (method.getName()) {
                  case "setDeliveryMode", "setTimeToLive" -> producer[0];
                  case "send" -> null;
                  default -> throw new AssertionError(method.getName());
                });
    BytesMessage message =
        proxy(BytesMessage.class, (method, ignored) -> defaultValue(method.getReturnType()));
    return proxy(
        JMSContext.class,
        (method, ignored) ->
            switch (method.getName()) {
              case "getSessionMode" -> JMSContext.SESSION_TRANSACTED;
              case "createBytesMessage" -> message;
              case "createProducer" -> producer[0];
              case "commit" -> null;
              case "close" -> {
                closeCalls.incrementAndGet();
                throw close;
              }
              default -> throw new AssertionError(method.getName());
            });
  }

  private static JMSContext context(Map<String, Object> actions) {
    return proxy(
        JMSContext.class,
        (method, arguments) -> {
          Object action = actions.get(method.getName());
          if (action instanceof RuntimeException failure) {
            throw failure;
          }
          if (action instanceof AtomicBoolean called) {
            called.set(true);
            return defaultValue(method.getReturnType());
          }
          if (action != null) {
            return action;
          }
          if (method.getName().equals("close")) {
            return null;
          }
          if (method.getName().equals("toString")) {
            return "SyntheticJmsContext";
          }
          if (method.getName().equals("hashCode")) {
            return System.identityHashCode(actions);
          }
          if (method.getName().equals("equals")) {
            return actions == arguments[0];
          }
          throw new UnsupportedOperationException(method.getName());
        });
  }

  private static Object defaultValue(Class<?> type) {
    if (type == void.class) {
      return null;
    }
    if (!type.isPrimitive()) {
      return null;
    }
    if (type == boolean.class) {
      return false;
    }
    if (type == byte.class) {
      return (byte) 0;
    }
    if (type == short.class) {
      return (short) 0;
    }
    if (type == int.class) {
      return 0;
    }
    if (type == long.class) {
      return 0L;
    }
    if (type == float.class) {
      return 0.0F;
    }
    if (type == double.class) {
      return 0.0D;
    }
    if (type == char.class) {
      return '\0';
    }
    throw new AssertionError(type);
  }

  @SuppressWarnings("unchecked")
  private static <T> T proxy(Class<T> type, Invocation invocation) {
    return (T)
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (ignored, method, arguments) -> invocation.invoke(method, arguments));
  }

  private static byte[] independentRequestWire() {
    return independentWire('Q', 'S', "LOGREQ01", MESSAGE_ID, 0, false);
  }

  private static byte[] independentResponseWire() {
    return independentWire(
        'S', 'S', "LOGRSP01", UUID.fromString("00000000-0000-0000-0000-000000000002"), 24, true);
  }

  private static byte[] independentAsyncRequestWire() {
    return independentWire('Q', 'A', "QSBREQ01", MESSAGE_ID, 4_144, false);
  }

  private static byte[] independentWire(
      char kind,
      char interaction,
      String layout,
      UUID correlationId,
      int dataLength,
      boolean response) {
    int total = 256 + dataLength;
    byte[] body = new byte[total];
    Arrays.fill(body, (byte) ' ');
    ascii(body, 0, "SCHBNK01");
    ascii(body, 8, "001");
    ascii(body, 11, layout);
    ascii(body, 19, "001");
    body[22] = (byte) kind;
    body[23] = (byte) interaction;
    ascii(body, 24, MESSAGE_ID.toString());
    ascii(body, 60, correlationId.toString());
    ascii(body, 96, "20260903120000000");
    ascii(body, 113, "a".repeat(64));
    ascii(body, 177, "0256");
    ascii(body, 181, "%06d".formatted(dataLength));
    ascii(body, 187, "000000");
    ascii(body, 193, "000000");
    ascii(body, 199, "%09d".formatted(total));
    if (response) {
      ascii(body, 208, "0000");
    }
    return body;
  }

  private static void ascii(byte[] target, int offset, String value) {
    byte[] source = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(source, 0, target, offset, source.length);
  }

  private static EmbeddedActiveMQ start(Path root) throws Exception {
    Configuration configuration;
    try (InputStream input = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      configuration = new FileConfigurationParser().parseMainConfig(input);
    }
    configuration
        .setPagingDirectory(root.resolve("paging").toString())
        .setBindingsDirectory(root.resolve("bindings").toString())
        .setJournalDirectory(root.resolve("journal").toString())
        .setLargeMessagesDirectory(root.resolve("large-messages").toString())
        .setSecurityEnabled(false)
        .clearAcceptorConfigurations()
        .addAcceptorConfiguration("component", "vm://0");
    return new EmbeddedActiveMQ().setConfiguration(configuration).start();
  }

  @FunctionalInterface
  private interface Invocation {
    Object invoke(java.lang.reflect.Method method, Object[] arguments) throws Throwable;
  }
}
