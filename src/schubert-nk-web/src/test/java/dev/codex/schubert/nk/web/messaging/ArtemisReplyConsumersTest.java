package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.MessageListener;
import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.apache.activemq.artemis.api.core.SimpleString;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-JMS-014 A-D: the dedicated Web reply consumer lifecycle on real Artemis and failure paths. */
final class ArtemisReplyConsumersTest {
  private static final String FIXTURE_GETSESSIONMODE_BF25AD1A = "getSessionMode";
  private static final String FIXTURE_CREATECONSUMER_BEB7888D = "createConsumer";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  private static final String FIXTURE_VM_0_0C76084A = "vm://0";

  @Test
  void jmsown003BindAcquisitionFailureAndNullKeepIdentityBeforeOwnership() {
    for (Throwable failure :
        new Throwable[] {
          new IllegalArgumentException("public factory argument"),
          new IllegalStateException("public factory state"),
          new NullPointerException("public factory null"),
          new AssertionError("public factory fatal")
        }) {
      var calls = new AtomicInteger();
      assertSame(
          failure,
          assertThrows(
              Throwable.class,
              () ->
                  ArtemisReplyConsumers.bind(
                      () -> {
                        calls.incrementAndGet();
                        if (failure instanceof RuntimeException runtime) throw runtime;
                        throw (Error) failure;
                      })));
      assertEquals(1, calls.get());
    }
    var calls = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            ArtemisReplyConsumers.bind(
                () -> {
                  calls.incrementAndGet();
                  return null;
                }));
    assertEquals(1, calls.get());
  }

  @Test
  void nativeSameFatalStartupAndCloseMustNotSelfSuppress() {
    var fatal = new LinkageError("same synthetic fatal");
    var closes = new AtomicInteger();
    var context =
        (JMSContext)
            Proxy.newProxyInstance(
                JMSContext.class.getClassLoader(),
                new Class<?>[] {JMSContext.class},
                (proxy, method, args) ->
                    switch (method.getName()) {
                      case FIXTURE_GETSESSIONMODE_BF25AD1A -> JMSContext.SESSION_TRANSACTED;
                      case FIXTURE_CREATECONSUMER_BEB7888D ->
                          Proxy.newProxyInstance(
                              JMSConsumer.class.getClassLoader(),
                              new Class<?>[] {JMSConsumer.class},
                              (p, m, a) -> null);
                      case "start" -> throw fatal;
                      case FIXTURE_CLOSE_97959247 -> {
                        closes.incrementAndGet();
                        throw fatal;
                      }
                      default -> null;
                    });
    assertSame(
        fatal,
        assertThrows(
            LinkageError.class,
            () ->
                ArtemisReplyConsumers.start(
                    () -> context, reply(new ReplyCorrelationRegistry()), ignored -> {})));
    assertEquals(1, closes.get());
    assertEquals(0, fatal.getSuppressed().length);
  }

  @Test
  void nativeOwnedBindStartOnceAndConfirmedCloseAfterUnknown() {
    var calls = new AtomicInteger();
    var closeFailure =
        new java.util.concurrent.atomic.AtomicReference<Throwable>(
            new IllegalStateException("synthetic unknown"));
    var context =
        (JMSContext)
            Proxy.newProxyInstance(
                JMSContext.class.getClassLoader(),
                new Class<?>[] {JMSContext.class},
                (proxy, method, args) ->
                    switch (method.getName()) {
                      case FIXTURE_GETSESSIONMODE_BF25AD1A -> JMSContext.SESSION_TRANSACTED;
                      case FIXTURE_CREATECONSUMER_BEB7888D ->
                          Proxy.newProxyInstance(
                              JMSConsumer.class.getClassLoader(),
                              new Class<?>[] {JMSConsumer.class},
                              (p, m, a) -> null);
                      case FIXTURE_CLOSE_97959247 -> {
                        calls.incrementAndGet();
                        var failure = closeFailure.get();
                        if (failure != null) throw failure;
                        yield null;
                      }
                      default -> null;
                    });
    var owner = ArtemisReplyConsumers.bind(() -> context);
    assertFalse(owner.ready());
    assertThrows(NullPointerException.class, () -> owner.start(null, ignored -> {}));
    assertThrows(
        NullPointerException.class, () -> owner.start(reply(new ReplyCorrelationRegistry()), null));
    owner.start(reply(new ReplyCorrelationRegistry()), ignored -> {});
    assertTrue(owner.ready());
    assertThrows(
        IllegalStateException.class,
        () -> owner.start(reply(new ReplyCorrelationRegistry()), ignored -> {}));
    assertThrows(IllegalStateException.class, owner::close);
    assertFalse(owner.ready());
    assertThrows(IllegalStateException.class, owner::close);
    assertEquals(2, calls.get());
    var fatal = new LinkageError("synthetic close fatal");
    closeFailure.set(fatal);
    assertSame(fatal, assertThrows(LinkageError.class, owner::close));
    assertFalse(owner.ready());
    assertThrows(
        IllegalStateException.class,
        () -> owner.start(reply(new ReplyCorrelationRegistry()), ignored -> {}));
    closeFailure.set(null);
    owner.close();
    owner.close();
    assertEquals(4, calls.get());
    assertThrows(NullPointerException.class, () -> ArtemisReplyConsumers.bind(null));
    assertThrows(NullPointerException.class, () -> ArtemisReplyConsumers.bind(() -> null));
  }

  private static final UUID REQUEST_ID = UUID.fromString("00000000-0000-0000-0000-000000000001");
  private static final UUID RESPONSE_ID = UUID.fromString("00000000-0000-0000-0000-000000000002");
  private static final Instant NOW = Instant.parse("2026-09-03T00:00:00Z");
  private static final String REPLY_QUEUE = "nk.sync.reply.web::nk.sync.reply.web.q";

  @Test
  void oneConsumerDeliversActiveAndLateReplies(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE)) {
      ReplyCorrelationRegistry registry = new ReplyCorrelationRegistry();
      byte[] expected = responseWire();
      PendingReply pending = registry.register(REQUEST_ID, NOW.plusSeconds(2), NOW).orElseThrow();
      try (ArtemisReplyConsumers consumers =
          ArtemisReplyConsumers.start(
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              reply(registry),
              ignored -> {
                throw new AssertionError("valid reply cannot be fatal");
              })) {
        assertTrue(consumers.ready());
        assertEquals(
            1,
            broker
                .getActiveMQServer()
                .locateQueue(SimpleString.of("nk.sync.reply.web.q"))
                .getConsumerCount());
        sendReply(producer, expected);
        assertArrayEquals(expected, pending.completion().toCompletableFuture().get());
        sendReply(producer, expected);
        awaitCount(registry);
        assertEquals(0, registry.pendingCount());
        assertFalse(consumers.terminalFailureObserved());
      }
      assertEquals(
          0,
          broker
              .getActiveMQServer()
              .locateQueue(SimpleString.of("nk.sync.reply.web.q"))
              .getConsumerCount());
    } finally {
      broker.stop();
    }
  }

  @Test
  void invalidRepliesAreCommittedToDlqAndTerminalIsSignalledOnce(@TempDir Path root)
      throws Exception {
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSConsumer dlq =
            observer.createConsumer(new ActiveMQQueue("nk.dead.letter::nk.dead.letter.q"))) {
      AtomicReference<CommittedFatalReplyException> terminal = new AtomicReference<>();
      AtomicInteger signals = new AtomicInteger();
      var notified = new CountDownLatch(1);
      try (ArtemisReplyConsumers consumers =
          ArtemisReplyConsumers.start(
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              reply(new ReplyCorrelationRegistry()),
              failure -> {
                terminal.set(failure);
                signals.incrementAndGet();
                notified.countDown();
              })) {
        producer
            .createProducer()
            .setDeliveryMode(DeliveryMode.PERSISTENT)
            .send(new ActiveMQQueue(REPLY_QUEUE), producer.createTextMessage("first-invalid"));
        assertNotNull(dlq.receive(5_000));
        assertTrue(notified.await(5, TimeUnit.SECONDS));
        producer
            .createProducer()
            .setDeliveryMode(DeliveryMode.PERSISTENT)
            .send(
                new ActiveMQQueue(REPLY_QUEUE),
                producer.createTextMessage("second-unacknowledged"));
        assertNull(dlq.receive(200));
        assertNotNull(terminal.get());
        assertEquals(1, signals.get());
        assertFalse(consumers.ready());
        assertTrue(consumers.terminalFailureObserved());
      }
      try (var pending = observer.createConsumer(new ActiveMQQueue(REPLY_QUEUE))) {
        var returned = pending.receive(10_000);
        assertNotNull(returned);
        assertEquals("second-unacknowledged", returned.getBody(String.class));
        assertNull(pending.receiveNoWait());
      }
    } finally {
      broker.stop();
    }
  }

  @Test
  void startupRejectsNullAndWrongModeAndClosesPartialSession(@TempDir Path root) throws Exception {
    assertThrows(
        NullPointerException.class,
        () ->
            ArtemisReplyConsumers.start(
                null, reply(new ReplyCorrelationRegistry()), ignored -> {}));
    assertThrows(
        NullPointerException.class,
        () ->
            ArtemisReplyConsumers.start(
                () -> null, reply(new ReplyCorrelationRegistry()), ignored -> {}));
    assertThrows(
        NullPointerException.class,
        () -> ArtemisReplyConsumers.start(() -> null, null, ignored -> {}));
    assertThrows(
        NullPointerException.class,
        () -> ArtemisReplyConsumers.start(() -> null, reply(new ReplyCorrelationRegistry()), null));
    EmbeddedActiveMQ broker = start(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A)) {
      IllegalStateException failure =
          assertThrows(
              IllegalStateException.class,
              () ->
                  ArtemisReplyConsumers.start(
                      () -> factory.createContext(JMSContext.AUTO_ACKNOWLEDGE),
                      reply(new ReplyCorrelationRegistry()),
                      ignored -> {}));
      assertEquals("Web reply consumer startup failed", failure.getMessage());
      assertEquals("Web reply consumer must be transacted", failure.getCause().getMessage());
      assertEquals(
          0,
          broker
              .getActiveMQServer()
              .locateQueue(SimpleString.of("nk.sync.reply.web.q"))
              .getConsumerCount());
    } finally {
      broker.stop();
    }
  }

  @Test
  void closeIsIdempotentAndPreservesStartupAndCloseFailures() {
    AtomicInteger closes = new AtomicInteger();
    ArtemisReplyConsumers runtime =
        ArtemisReplyConsumers.start(
            () -> syntheticContext(closes, false),
            reply(new ReplyCorrelationRegistry()),
            ignored -> {});
    assertTrue(runtime.ready());
    IllegalStateException close = assertThrows(IllegalStateException.class, runtime::close);
    assertEquals("Web reply consumer close failed", close.getMessage());
    assertEquals("synthetic-close", close.getCause().getMessage());
    assertFalse(runtime.ready());
    assertThrows(IllegalStateException.class, runtime::close);
    assertEquals(2, closes.get());

    AtomicInteger startupCloses = new AtomicInteger();
    IllegalStateException startup =
        assertThrows(
            IllegalStateException.class,
            () ->
                ArtemisReplyConsumers.start(
                    () -> syntheticContext(startupCloses, true),
                    reply(new ReplyCorrelationRegistry()),
                    ignored -> {}));
    assertEquals("synthetic-create", startup.getCause().getMessage());
    assertEquals(1, startupCloses.get());
    assertEquals(1, startup.getCause().getSuppressed().length);
    assertEquals(
        "Web reply consumer close failed", startup.getCause().getSuppressed()[0].getMessage());
  }

  @Test
  void temporaryReadFailureRollsBackAndLeavesRuntimeReady() throws Exception {
    AtomicReference<MessageListener> installed = new AtomicReference<>();
    AtomicInteger rollbacks = new AtomicInteger();
    AtomicInteger closes = new AtomicInteger();
    JMSContext context =
        (JMSContext)
            Proxy.newProxyInstance(
                JMSContext.class.getClassLoader(),
                new Class<?>[] {JMSContext.class},
                (proxy, method, arguments) ->
                    switch (method.getName()) {
                      case FIXTURE_GETSESSIONMODE_BF25AD1A -> JMSContext.SESSION_TRANSACTED;
                      case FIXTURE_CREATECONSUMER_BEB7888D ->
                          Proxy.newProxyInstance(
                              JMSConsumer.class.getClassLoader(),
                              new Class<?>[] {JMSConsumer.class},
                              (consumer, consumerMethod, consumerArgs) -> {
                                if (consumerMethod.getName().equals("setMessageListener")) {
                                  installed.set((MessageListener) consumerArgs[0]);
                                }
                                return null;
                              });
                      case "rollback" -> {
                        rollbacks.incrementAndGet();
                        yield null;
                      }
                      case FIXTURE_CLOSE_97959247 -> {
                        closes.incrementAndGet();
                        yield null;
                      }
                      default -> null;
                    });
    try (ArtemisReplyConsumers runtime =
        ArtemisReplyConsumers.start(
            () -> context,
            reply(new ReplyCorrelationRegistry()),
            ignored -> {
              throw new AssertionError("temporary failure cannot be fatal");
            })) {
      JMSException readFailure = new JMSException("synthetic-read");
      BytesMessage broken =
          (BytesMessage)
              Proxy.newProxyInstance(
                  BytesMessage.class.getClassLoader(),
                  new Class<?>[] {BytesMessage.class},
                  (proxy, method, arguments) -> {
                    if (method.getName().equals("getBodyLength")) {
                      throw readFailure;
                    }
                    return null;
                  });
      installed.get().onMessage(broken);
      assertEquals(1, rollbacks.get());
      assertTrue(runtime.ready());
      assertFalse(runtime.terminalFailureObserved());
    }
    assertEquals(1, closes.get());
  }

  private static ArtemisReplyConsumer reply(ReplyCorrelationRegistry registry) {
    Clock clock = Clock.fixed(NOW, ZoneOffset.UTC);
    return new ArtemisReplyConsumer(
        new JmsRequestReplyClient(registry, clock, 1),
        new JmsReplyDecoder(),
        new ArtemisReplyDlqSender(clock));
  }

  private static JMSContext syntheticContext(AtomicInteger closes, boolean failCreate) {
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (proxy, method, args) ->
                switch (method.getName()) {
                  case FIXTURE_GETSESSIONMODE_BF25AD1A -> JMSContext.SESSION_TRANSACTED;
                  case FIXTURE_CREATECONSUMER_BEB7888D -> {
                    if (failCreate) {
                      throw new IllegalStateException("synthetic-create");
                    }
                    yield Proxy.newProxyInstance(
                        JMSConsumer.class.getClassLoader(),
                        new Class<?>[] {JMSConsumer.class},
                        (p, m, a) -> null);
                  }
                  case FIXTURE_CLOSE_97959247 -> {
                    closes.incrementAndGet();
                    throw new IllegalStateException("synthetic-close");
                  }
                  default -> null;
                });
  }

  private static void awaitCount(ReplyCorrelationRegistry registry) throws InterruptedException {
    for (int attempt = 0; attempt < 100 && registry.lateResponseCount() == 0; attempt++) {
      Thread.sleep(10);
    }
    assertEquals(1, registry.lateResponseCount());
  }

  private static void sendReply(JMSContext context, byte[] body) throws Exception {
    BytesMessage reply = context.createBytesMessage();
    reply.writeBytes(body);
    reply.setJMSCorrelationID(REQUEST_ID.toString());
    reply.setStringProperty("NKMessageID", RESPONSE_ID.toString());
    reply.setStringProperty("NKLayoutID", "LOGRSP01");
    reply.setStringProperty("NKProtocolVersion", "001");
    context
        .createProducer()
        .setDeliveryMode(DeliveryMode.PERSISTENT)
        .setTimeToLive(10_000)
        .send(new ActiveMQQueue(REPLY_QUEUE), reply);
  }

  private static byte[] responseWire() {
    byte[] body = new byte[280];
    Arrays.fill(body, (byte) ' ');
    ascii(body, 0, "SCHBNK01");
    ascii(body, 8, "001");
    ascii(body, 11, "LOGRSP01");
    ascii(body, 19, "001");
    body[22] = 'S';
    body[23] = 'S';
    ascii(body, 24, RESPONSE_ID.toString());
    ascii(body, 60, REQUEST_ID.toString());
    ascii(body, 96, "20260903120000000");
    ascii(body, 113, "a".repeat(64));
    ascii(body, 177, "0256");
    ascii(body, 181, "000024");
    ascii(body, 187, "000000");
    ascii(body, 193, "000000");
    ascii(body, 199, "000000280");
    ascii(body, 208, "0000");
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
        .addAcceptorConfiguration("component", FIXTURE_VM_0_0C76084A);
    return new EmbeddedActiveMQ().setConfiguration(configuration).start();
  }
}
