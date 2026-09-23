package dev.codex.schubert.nk.api.dispatch;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.messaging.inbound.CommittedFatalInboundException;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import jakarta.jms.JMSContext;
import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import javax.sql.DataSource;
import org.apache.activemq.artemis.api.core.SimpleString;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.postgresql.ds.PGSimpleDataSource;

/** PG233/PT-JMS-018: actual PostgreSQL/JMS parent and independent three-route markers. */
final class ApiLogPathApplicationRuntimeTest {
  private static final byte[] LOGIN = "login".getBytes(StandardCharsets.US_ASCII);
  private static final byte[] GAME = "game".getBytes(StandardCharsets.US_ASCII);
  private static final byte[] LOG = "log".getBytes(StandardCharsets.US_ASCII);

  @Test
  void realDatabaseAndBrokerBindThreeRoutesAndTerminal(@TempDir Path root) throws Exception {
    Files.createDirectory(root.resolve("postgres"));
    var database = new ApiLogDatabaseFixture(root.resolve("postgres"));
    DataSource source =
        (DataSource)
            Proxy.newProxyInstance(
                DataSource.class.getClassLoader(),
                new Class<?>[] {DataSource.class},
                (ignored, method, arguments) -> {
                  if (method.getName().equals("getConnection")
                      && (arguments == null || arguments.length == 0)) return database.api();
                  throw new AssertionError(method.getName());
                });
    EmbeddedActiveMQ broker = startBroker(root.resolve("broker"));
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        JMSContext producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var dlq = observer.createConsumer(new ActiveMQQueue("nk.dead.letter::nk.dead.letter.q"))) {
      var login = new AtomicInteger();
      var game = new AtomicInteger();
      var logs = new AtomicInteger();
      var terminal = new AtomicInteger();
      var signal = new CountDownLatch(1);
      var runtime =
          ApiLogPathApplicationRuntime.start(
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              source,
              (connection, request, receivedAt) -> {
                assertFalse(connection.getAutoCommit());
                assertEquals("LGNREQ01", request.header().layoutId().value());
                assertNotNull(receivedAt);
                login.incrementAndGet();
                return LOGIN;
              },
              ignored -> {
                game.incrementAndGet();
                return GAME;
              },
              ignored -> {
                logs.incrementAndGet();
                return LOG;
              },
              Clock.systemUTC(),
              ignored -> {
                terminal.incrementAndGet();
                signal.countDown();
              });
      assertTrue(runtime.ready());
      assertFalse(runtime.terminalFailureObserved());
      assertEquals(4, consumerCount(broker, "nk.sync.request.q"));
      assertEquals(1, consumerCount(broker, "nk.web.log.q"));
      assertArrayEquals(LOGIN, runtime.processor().process(request("LGNREQ01", 384)));
      assertArrayEquals(GAME, runtime.processor().process(request("GAMREQ01", 0)));
      assertArrayEquals(LOG, runtime.processor().process(request("LGSREQ01", 656)));
      assertEquals(1, login.get());
      assertEquals(1, game.get());
      assertEquals(1, logs.get());
      producer
          .createProducer()
          .send(
              new ActiveMQQueue("nk.sync.request::nk.sync.request.q"),
              producer.createTextMessage("invalid"));
      assertNotNull(dlq.receive(5_000));
      assertTrue(signal.await(5, TimeUnit.SECONDS));
      assertEquals(1, terminal.get());
      assertTrue(runtime.terminalFailureObserved());
      assertFalse(runtime.ready());
      runtime.close();
      runtime.close();
      assertFalse(runtime.ready());
      assertEquals(0, consumerCount(broker, "nk.sync.request.q"));
      assertEquals(0, consumerCount(broker, "nk.web.log.q"));
    } finally {
      broker.stop();
      database.stop();
    }
  }

  @Test
  void allDependenciesFailBeforeOpeningConsumer() {
    var opened = new AtomicInteger();
    java.util.function.Supplier<JMSContext> factory =
        () -> {
          opened.incrementAndGet();
          return null;
        };
    DataSource database = new PGSimpleDataSource();
    TransactionalRequestHandler login = (connection, request, receivedAt) -> LOGIN;
    SyncRequestProcessor game = ignored -> GAME;
    SyncRequestProcessor log = ignored -> LOG;
    java.util.function.Consumer<CommittedFatalInboundException> terminal = ignored -> {};
    assertThrows(
        NullPointerException.class,
        () ->
            ApiLogPathApplicationRuntime.start(
                null, database, login, game, log, Clock.systemUTC(), terminal));
    assertThrows(
        NullPointerException.class,
        () ->
            ApiLogPathApplicationRuntime.start(
                factory, null, login, game, log, Clock.systemUTC(), terminal));
    assertThrows(
        NullPointerException.class,
        () ->
            ApiLogPathApplicationRuntime.start(
                factory, database, null, game, log, Clock.systemUTC(), terminal));
    assertThrows(
        NullPointerException.class,
        () ->
            ApiLogPathApplicationRuntime.start(
                factory, database, login, null, log, Clock.systemUTC(), terminal));
    assertThrows(
        NullPointerException.class,
        () ->
            ApiLogPathApplicationRuntime.start(
                factory, database, login, game, null, Clock.systemUTC(), terminal));
    assertThrows(
        NullPointerException.class,
        () ->
            ApiLogPathApplicationRuntime.start(
                factory, database, login, game, log, null, terminal));
    assertThrows(
        NullPointerException.class,
        () ->
            ApiLogPathApplicationRuntime.start(
                factory, database, login, game, log, Clock.systemUTC(), null));
    assertEquals(0, opened.get());
  }

  @Test
  void failedConsumerStartupDoesNotReturnPartialRuntime() {
    var opened = new AtomicInteger();
    DataSource database = new PGSimpleDataSource();
    assertThrows(
        IllegalStateException.class,
        () ->
            ApiLogPathApplicationRuntime.start(
                () -> {
                  opened.incrementAndGet();
                  return null;
                },
                database,
                (connection, request, receivedAt) -> LOGIN,
                ignored -> GAME,
                ignored -> LOG,
                Clock.systemUTC(),
                ignored -> {}));
    assertEquals(1, opened.get());
  }

  private static WireMessage<FixedPayload> request(String layout, int dataLength) {
    UUID id = UUID.fromString("00000000-0000-0000-0000-000000000001");
    var context =
        layout.equals("LGNREQ01")
            ? Optional.<AuthenticationContext>empty()
            : Optional.of(AuthenticationContext.of("a".repeat(64)));
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(layout),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            id,
            id,
            Instant.parse("2026-09-24T00:00:00Z"),
            context,
            256,
            dataLength,
            0,
            0,
            256 + dataLength,
            Optional.empty());
    return new WireMessage<>(header, new FixedPayload(new byte[dataLength], 0, List.of()));
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
        .addAcceptorConfiguration("component", "vm://0");
    return new EmbeddedActiveMQ().setConfiguration(configuration).start();
  }
}
