package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Clock;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.activemq.artemis.api.core.SimpleString;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PG229/PT-JMS-016: API receive-group ownership, distinct from full process boot. */
final class ApiMessagingRuntimeTest {
  private static final String FIXTURE_VM_0_0C76084A = "vm://0";
  private static final String FIXTURE_NK_SYNC_REQUEST_Q_583BA80B = "nk.sync.request.q";
  private static final String FIXTURE_NK_WEB_LOG_Q_88E21E63 = "nk.web.log.q";

  @Test
  void core001ActualSixContextsThirdFifoProfileAndOneFatalAcrossThreeQueues(@TempDir Path root)
      throws Exception {
    var broker = startBroker(root);
    try (var sync = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        var log = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        var async = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        var sending = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        var producer = sending.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var observation = sending.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var dlq =
            observation.createConsumer(new ActiveMQQueue("nk.dead.letter::nk.dead.letter.q"))) {
      sync.setConsumerWindowSize(1_048_576);
      log.setConsumerWindowSize(65_536);
      async.setConsumerWindowSize(0);
      var terminal = new AtomicInteger();
      var fatal = new AtomicInteger();
      try (var runtime =
          ApiMessagingRuntime.start(
              () -> sync.createContext(JMSContext.SESSION_TRANSACTED),
              () -> log.createContext(JMSContext.SESSION_TRANSACTED),
              () -> async.createContext(JMSContext.SESSION_TRANSACTED),
              ignored -> new byte[0],
              ignored -> {},
              ignored -> {},
              Clock.systemUTC(),
              ignored -> terminal.incrementAndGet(),
              fatal::incrementAndGet)) {
        assertEquals(4, consumerCount(broker, FIXTURE_NK_SYNC_REQUEST_Q_583BA80B));
        assertEquals(1, consumerCount(broker, FIXTURE_NK_WEB_LOG_Q_88E21E63));
        assertEquals(1, consumerCount(broker, "nk.async.work.q"));
        assertEquals(0, async.getConsumerWindowSize());
        assertTrue(runtime.ready());
        for (String queue :
            java.util.List.of(
                "nk.async.work::nk.async.work.q",
                "nk.web.log::nk.web.log.q",
                "nk.sync.request::nk.sync.request.q")) {
          producer
              .createProducer()
              .send(new ActiveMQQueue(queue), producer.createTextMessage("invalid"));
          assertNotNull(dlq.receive(5_000));
        }
        assertEquals(1, terminal.get());
        assertEquals(0, fatal.get());
        assertTrue(runtime.terminalFailureObserved());
        assertFalse(runtime.ready());
      }
      assertEquals(0, consumerCount(broker, FIXTURE_NK_SYNC_REQUEST_Q_583BA80B));
      assertEquals(0, consumerCount(broker, FIXTURE_NK_WEB_LOG_Q_88E21E63));
      assertEquals(0, consumerCount(broker, "nk.async.work.q"));
    } finally {
      broker.stop();
    }
  }

  @Test
  void core002EveryPartialFactoryRuntimeOrFatalReleasesAllEarlierContexts() {
    for (int failAt = 1; failAt <= 6; failAt++) {
      for (boolean fatal : new boolean[] {false, true}) {
        var opened = new AtomicInteger();
        var closed = new AtomicInteger();
        int point = failAt;
        Error error = new AssertionError("synthetic-private");
        java.util.function.Supplier<JMSContext> supplier =
            () -> {
              if (opened.incrementAndGet() == point) {
                if (fatal) throw error;
                throw new IllegalStateException("synthetic-private");
              }
              return syntheticContext(closed, false);
            };
        Class<? extends Throwable> expectedType =
            fatal ? AssertionError.class : IllegalStateException.class;
        var failure =
            assertThrows(
                expectedType,
                () ->
                    ApiMessagingRuntime.start(
                        supplier,
                        supplier,
                        supplier,
                        ignored -> new byte[0],
                        ignored -> {},
                        ignored -> {},
                        Clock.systemUTC(),
                        ignored -> {},
                        () -> {}));
        if (fatal) org.junit.jupiter.api.Assertions.assertSame(error, failure);
        assertEquals(point, opened.get());
        assertEquals(point - 1, closed.get());
      }
    }
  }

  @Test
  void core003CompleteNullPortsFailBeforeOpeningAnyContext() {
    var count = new AtomicInteger();
    java.util.function.Supplier<JMSContext> factory =
        () -> {
          count.incrementAndGet();
          return null;
        };
    assertThrows(
        NullPointerException.class,
        () ->
            ApiMessagingRuntime.start(
                factory,
                factory,
                null,
                ignored -> new byte[0],
                ignored -> {},
                ignored -> {},
                Clock.systemUTC(),
                ignored -> {},
                () -> {}));
    assertThrows(
        NullPointerException.class,
        () ->
            ApiMessagingRuntime.start(
                factory,
                factory,
                factory,
                ignored -> new byte[0],
                ignored -> {},
                null,
                Clock.systemUTC(),
                ignored -> {},
                () -> {}));
    assertThrows(
        NullPointerException.class,
        () ->
            ApiMessagingRuntime.start(
                factory,
                factory,
                factory,
                ignored -> new byte[0],
                ignored -> {},
                ignored -> {},
                Clock.systemUTC(),
                ignored -> {},
                null));
    assertEquals(0, count.get());
  }

  @Test
  void approvedSyncAndWebLogProfilesHaveSeparateRuntimeSuppliers(@TempDir Path root)
      throws Exception {
    var syncOpens = new AtomicInteger();
    var logOpens = new AtomicInteger();
    EmbeddedActiveMQ broker = startBroker(root);
    try (var sync = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        var log = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A)) {
      sync.setConsumerWindowSize(1_048_576);
      log.setConsumerWindowSize(65_536);
      try (var runtime =
          ApiMessagingRuntime.start(
              () -> {
                syncOpens.incrementAndGet();
                return sync.createContext(JMSContext.SESSION_TRANSACTED);
              },
              () -> {
                logOpens.incrementAndGet();
                return log.createContext(JMSContext.SESSION_TRANSACTED);
              },
              ignored -> new byte[0],
              ignored -> {},
              Clock.systemUTC(),
              ignored -> {})) {
        assertEquals(1_048_576, sync.getConsumerWindowSize());
        assertEquals(65_536, log.getConsumerWindowSize());
        assertEquals(4, syncOpens.get());
        assertEquals(1, logOpens.get());
        assertEquals(4, consumerCount(broker, FIXTURE_NK_SYNC_REQUEST_Q_583BA80B));
        assertEquals(1, consumerCount(broker, FIXTURE_NK_WEB_LOG_Q_88E21E63));
        assertTrue(runtime.ready());
      }
      assertEquals(0, consumerCount(broker, FIXTURE_NK_SYNC_REQUEST_Q_583BA80B));
      assertEquals(0, consumerCount(broker, FIXTURE_NK_WEB_LOG_Q_88E21E63));
    } finally {
      broker.stop();
    }
  }

  @Test
  void opensFiveConsumersAndSignalsOneTerminalAcrossGroups(@TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = startBroker(root);
    try (var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var dlq = observer.createConsumer(new ActiveMQQueue("nk.dead.letter::nk.dead.letter.q"))) {
      AtomicInteger terminals = new AtomicInteger();
      var runtime =
          ApiMessagingRuntime.start(
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              ignored -> new byte[0],
              ignored -> {},
              Clock.systemUTC(),
              ignored -> terminals.incrementAndGet());
      assertTrue(runtime.ready());
      assertFalse(runtime.terminalFailureObserved());
      assertEquals(4, consumerCount(broker, FIXTURE_NK_SYNC_REQUEST_Q_583BA80B));
      assertEquals(1, consumerCount(broker, FIXTURE_NK_WEB_LOG_Q_88E21E63));
      producer
          .createProducer()
          .send(
              new ActiveMQQueue("nk.sync.request::nk.sync.request.q"),
              producer.createTextMessage("invalid"));
      assertNotNull(dlq.receive(5_000));
      producer
          .createProducer()
          .send(
              new ActiveMQQueue("nk.web.log::nk.web.log.q"), producer.createTextMessage("invalid"));
      assertNotNull(dlq.receive(5_000));
      assertTrue(runtime.terminalFailureObserved());
      assertFalse(runtime.ready());
      assertEquals(1, terminals.get());
      runtime.close();
      runtime.close();
      assertFalse(runtime.ready());
      assertEquals(0, consumerCount(broker, FIXTURE_NK_SYNC_REQUEST_Q_583BA80B));
      assertEquals(0, consumerCount(broker, FIXTURE_NK_WEB_LOG_Q_88E21E63));
    } finally {
      broker.stop();
    }
  }

  @Test
  void validatesAllPortsBeforeOpeningAnyContext() {
    AtomicInteger opened = new AtomicInteger();
    java.util.function.Supplier<JMSContext> factory =
        () -> {
          opened.incrementAndGet();
          return null;
        };
    SyncRequestProcessor sync = ignored -> new byte[0];
    InternalEventProcessor log = ignored -> {};
    java.util.function.Consumer<CommittedFatalInboundException> terminal = ignored -> {};
    assertThrows(
        NullPointerException.class,
        () -> ApiMessagingRuntime.start(null, factory, sync, log, Clock.systemUTC(), terminal));
    assertThrows(
        NullPointerException.class,
        () -> ApiMessagingRuntime.start(factory, null, sync, log, Clock.systemUTC(), terminal));
    assertThrows(
        NullPointerException.class,
        () -> ApiMessagingRuntime.start(factory, factory, null, log, Clock.systemUTC(), terminal));
    assertThrows(
        NullPointerException.class,
        () -> ApiMessagingRuntime.start(factory, factory, sync, null, Clock.systemUTC(), terminal));
    assertThrows(
        NullPointerException.class,
        () -> ApiMessagingRuntime.start(factory, factory, sync, log, null, terminal));
    assertThrows(
        NullPointerException.class,
        () -> ApiMessagingRuntime.start(factory, factory, sync, log, Clock.systemUTC(), null));
    assertEquals(0, opened.get());
  }

  @Test
  void fifthContextFailureClosesFourEarlierContexts() {
    AtomicInteger opened = new AtomicInteger();
    AtomicInteger closed = new AtomicInteger();
    IllegalStateException failure =
        assertThrows(
            IllegalStateException.class,
            () ->
                ApiMessagingRuntime.start(
                    () -> opened.incrementAndGet() == 5 ? null : syntheticContext(closed, false),
                    () -> opened.incrementAndGet() == 5 ? null : syntheticContext(closed, false),
                    ignored -> new byte[0],
                    ignored -> {},
                    Clock.systemUTC(),
                    ignored -> {}));
    assertEquals("API messaging startup failed", failure.getMessage());
    assertEquals(5, opened.get());
    assertEquals(4, closed.get());
  }

  @Test
  void failedSecondStartupPreservesFirstCloseFailure() {
    AtomicInteger opened = new AtomicInteger();
    AtomicInteger closed = new AtomicInteger();
    IllegalStateException failure =
        assertThrows(
            IllegalStateException.class,
            () ->
                ApiMessagingRuntime.start(
                    () -> opened.incrementAndGet() == 5 ? null : syntheticContext(closed, true),
                    () -> opened.incrementAndGet() == 5 ? null : syntheticContext(closed, true),
                    ignored -> new byte[0],
                    ignored -> {},
                    Clock.systemUTC(),
                    ignored -> {}));
    assertEquals(4, closed.get());
    assertEquals(1, failure.getCause().getSuppressed().length);
    assertEquals(
        "API sync consumer close failed", failure.getCause().getSuppressed()[0].getMessage());
  }

  @Test
  void closeAttemptsBothGroupsAndPreservesBothFailures() {
    AtomicInteger closed = new AtomicInteger();
    ApiMessagingRuntime runtime =
        ApiMessagingRuntime.start(
            () -> syntheticContext(closed, true),
            () -> syntheticContext(closed, true),
            ignored -> new byte[0],
            ignored -> {},
            Clock.systemUTC(),
            ignored -> {});
    assertTrue(runtime.ready());
    IllegalStateException failure = assertThrows(IllegalStateException.class, runtime::close);
    assertEquals("API messaging close failed", failure.getMessage());
    assertEquals("API Web log consumer close failed", failure.getCause().getMessage());
    assertEquals(
        "API sync consumer close failed", failure.getCause().getSuppressed()[0].getMessage());
    assertEquals(5, closed.get());
    // SSC314/BUG1548: every child is still unconfirmed; a second call must fail again.
    assertThrows(IllegalStateException.class, runtime::close);
    assertEquals(10, closed.get());
    assertFalse(runtime.ready());
  }

  @Test
  void closeHandlesOnlySyncFailure() {
    AtomicInteger opened = new AtomicInteger();
    ApiMessagingRuntime runtime =
        ApiMessagingRuntime.start(
            () -> syntheticContext(new AtomicInteger(), opened.incrementAndGet() < 5),
            () -> syntheticContext(new AtomicInteger(), false),
            ignored -> new byte[0],
            ignored -> {},
            Clock.systemUTC(),
            ignored -> {});
    IllegalStateException failure = assertThrows(IllegalStateException.class, runtime::close);
    assertEquals("API sync consumer close failed", failure.getCause().getMessage());
  }

  private static JMSContext syntheticContext(AtomicInteger closes, boolean failClose) {
    JMSConsumer consumer =
        (JMSConsumer)
            Proxy.newProxyInstance(
                JMSConsumer.class.getClassLoader(),
                new Class<?>[] {JMSConsumer.class},
                (ignored, method, arguments) -> {
                  if (method.getName().equals("setMessageListener")) return null;
                  throw new AssertionError(method.getName());
                });
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (ignored, method, arguments) ->
                switch (method.getName()) {
                  case "setAutoStart", "start" -> null;
                  case "getSessionMode" -> JMSContext.SESSION_TRANSACTED;
                  case "createConsumer" -> consumer;
                  case "close" -> {
                    closes.incrementAndGet();
                    if (failClose) throw new IllegalStateException("synthetic close failure");
                    yield null;
                  }
                  default -> throw new AssertionError(method.getName());
                });
  }

  private static int consumerCount(EmbeddedActiveMQ broker, String queue) {
    return broker.getActiveMQServer().locateQueue(SimpleString.of(queue)).getConsumerCount();
  }

  private static EmbeddedActiveMQ startBroker(Path root) throws Exception {
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
