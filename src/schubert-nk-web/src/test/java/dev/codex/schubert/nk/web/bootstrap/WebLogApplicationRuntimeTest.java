package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.logging.WebLogDispatcher;
import dev.codex.schubert.nk.web.logging.WebLogMessageSender;
import dev.codex.schubert.nk.web.logging.WebLogOutboxRepository;
import dev.codex.schubert.nk.web.logging.WebLogPayloadCodec;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.session.SessionPayloadCodec;
import jakarta.jms.JMSContext;
import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Duration;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import javax.sql.DataSource;
import org.apache.activemq.artemis.api.core.SimpleString;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PG231: real Log-path Web boot plus deterministic resource-failure boundaries. */
final class WebLogApplicationRuntimeTest {
  @TempDir Path root;
  private final Clock clock = Clock.systemUTC();

  @Test
  void scr127RealReplyWorkerAndSecuredLogMvcStartAndClose() throws Exception {
    var db = new WebLogDatabaseFixture(Files.createDirectory(root.resolve("pg")));
    var broker = startBroker(Files.createDirectory(root.resolve("broker")));
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var sessionCodec = new SessionPayloadCodec("test", new byte[32], null, null);
        var logCodec = new WebLogPayloadCodec("test", new byte[32], null, null);
        var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build()) {
      var contexts =
          (dev.codex.schubert.nk.web.messaging.JmsContextFactory)
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED);
      var dispatcher = dispatcher(source(db::web), logCodec, contexts);
      var runtime =
          WebLogApplicationRuntime.start(
              root,
              0,
              source(db::web),
              contexts,
              sessionCodec,
              clock,
              audit(),
              java.util.UUID::randomUUID,
              dispatcher,
              "web-log-worker",
              10,
              Duration.ofMillis(10),
              ignored -> {
                throw new AssertionError("unexpected fatal reply");
              });
      int port = runtime.port();
      assertTrue(runtime.ready());
      assertFalse(runtime.terminalFailureObserved());
      assertEquals(1, consumerCount(broker));
      var page =
          client.send(
              HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + port + "/login"))
                  .header("X-Forwarded-For", "203.0.113.1")
                  .header("X-Forwarded-Proto", "https")
                  .build(),
              HttpResponse.BodyHandlers.ofString());
      assertEquals(200, page.statusCode());
      assertEquals("schubert NK - ログイン", Jsoup.parse(page.body()).title());
      runtime.close();
      runtime.close();
      assertFalse(runtime.ready());
      assertThrows(IllegalStateException.class, runtime::port);
      assertEquals(0, consumerCount(broker));
    } finally {
      broker.stop();
      db.stop();
    }
  }

  @Test
  void scr128InvalidReplyDlqMakesWholeRuntimeNotReady() throws Exception {
    var db = new WebLogDatabaseFixture(Files.createDirectory(root.resolve("pg")));
    var broker = startBroker(Files.createDirectory(root.resolve("broker")));
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var dlq = observer.createConsumer(new ActiveMQQueue("nk.dead.letter::nk.dead.letter.q"));
        var sessionCodec = new SessionPayloadCodec("test", new byte[32], null, null);
        var logCodec = new WebLogPayloadCodec("test", new byte[32], null, null)) {
      var contexts =
          (dev.codex.schubert.nk.web.messaging.JmsContextFactory)
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED);
      var signals = new AtomicInteger();
      var signalled = new CountDownLatch(1);
      try (var runtime =
          WebLogApplicationRuntime.start(
              root,
              0,
              source(db::web),
              contexts,
              sessionCodec,
              clock,
              audit(),
              java.util.UUID::randomUUID,
              dispatcher(source(db::web), logCodec, contexts),
              "web-log-worker",
              10,
              Duration.ofMillis(10),
              ignored -> {
                signals.incrementAndGet();
                signalled.countDown();
              })) {
        producer
            .createProducer()
            .send(
                new ActiveMQQueue("nk.sync.reply.web::nk.sync.reply.web.q"),
                producer.createTextMessage("invalid"));
        assertNotNull(dlq.receive(5_000));
        assertTrue(signalled.await(5, TimeUnit.SECONDS));
        assertEquals(1, signals.get());
        assertTrue(runtime.terminalFailureObserved());
        assertFalse(runtime.ready());
      }
    } finally {
      broker.stop();
      db.stop();
    }
  }

  @Test
  void scr129PartialStartupClosesReplyConsumer() throws Exception {
    var broker = startBroker(Files.createDirectory(root.resolve("broker")));
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var sessionCodec = new SessionPayloadCodec("test", new byte[32], null, null);
        var logCodec = new WebLogPayloadCodec("test", new byte[32], null, null)) {
      var contexts =
          (dev.codex.schubert.nk.web.messaging.JmsContextFactory)
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED);
      DataSource unavailable =
          source(
              () -> {
                throw new SQLException("synthetic private DB failure");
              });
      var dispatcher = dispatcher(unavailable, logCodec, contexts);
      assertThrows(
          IllegalArgumentException.class,
          () ->
              WebLogApplicationRuntime.start(
                  root,
                  0,
                  unavailable,
                  contexts,
                  sessionCodec,
                  clock,
                  audit(),
                  java.util.UUID::randomUUID,
                  dispatcher,
                  "",
                  10,
                  Duration.ofMillis(10),
                  ignored -> {}));
      assertEquals(0, consumerCount(broker));
      assertThrows(
          WebStartupException.class,
          () ->
              WebLogApplicationRuntime.start(
                  root,
                  0,
                  unavailable,
                  contexts,
                  sessionCodec,
                  clock,
                  audit(),
                  java.util.UUID::randomUUID,
                  dispatcher,
                  "web-log-worker",
                  10,
                  Duration.ofMillis(10),
                  ignored -> {}));
      assertEquals(0, consumerCount(broker));
    } finally {
      broker.stop();
    }
  }

  @Test
  void scr130LifecycleAggregatesCloseFailuresAndReadinessBoundaries() throws Exception {
    var order = new java.util.ArrayList<String>();
    var terminal = new AtomicBoolean();
    var runtime =
        new WebLogApplicationRuntime(
            () -> {
              order.add("http");
              throw new SQLException("http close");
            },
            () -> {
              order.add("worker");
              throw new IllegalStateException("worker close");
            },
            () -> {
              order.add("reply");
              throw new IllegalStateException("reply close");
            },
            () -> 1234,
            () -> true,
            () -> true,
            terminal);
    assertEquals(1234, runtime.port());
    assertTrue(runtime.ready());
    IllegalStateException failure = assertThrows(IllegalStateException.class, runtime::close);
    assertEquals("Web Log runtime stop failed", failure.getMessage());
    assertEquals("http close", failure.getCause().getMessage());
    assertEquals(2, failure.getCause().getSuppressed().length);
    assertEquals(java.util.List.of("http", "worker", "reply"), order);
    runtime.close();
    assertEquals(3, order.size());
    assertFalse(runtime.ready());
    assertThrows(IllegalStateException.class, runtime::port);
    var notReady =
        new WebLogApplicationRuntime(
            () -> {}, () -> {}, () -> {}, () -> 1, () -> false, () -> true, terminal);
    assertFalse(notReady.ready());
    var workerStopped =
        new WebLogApplicationRuntime(
            () -> {}, () -> {}, () -> {}, () -> 1, () -> true, () -> false, terminal);
    assertFalse(workerStopped.ready());
    terminal.set(true);
    assertTrue(notReady.terminalFailureObserved());
    assertFalse(workerStopped.ready());
    notReady.close();
    workerStopped.close();
  }

  @Test
  void scr131StartupNullContractsAndSuppressedCleanup() throws Exception {
    var calls = new AtomicInteger();
    DataSource database =
        source(
            () -> {
              calls.incrementAndGet();
              return null;
            });
    var contexts =
        (dev.codex.schubert.nk.web.messaging.JmsContextFactory)
            () -> {
              throw new AssertionError("broker must not be borrowed");
            };
    try (var sessionCodec = new SessionPayloadCodec("test", new byte[32], null, null);
        var logCodec = new WebLogPayloadCodec("test", new byte[32], null, null)) {
      var dispatcher = dispatcher(database, logCodec, contexts);
      assertThrows(
          NullPointerException.class,
          () ->
              WebLogApplicationRuntime.start(
                  root,
                  0,
                  null,
                  contexts,
                  sessionCodec,
                  clock,
                  audit(),
                  java.util.UUID::randomUUID,
                  dispatcher,
                  "worker",
                  1,
                  Duration.ofSeconds(1),
                  ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              WebLogApplicationRuntime.start(
                  root,
                  0,
                  database,
                  null,
                  sessionCodec,
                  clock,
                  audit(),
                  java.util.UUID::randomUUID,
                  dispatcher,
                  "worker",
                  1,
                  Duration.ofSeconds(1),
                  ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              WebLogApplicationRuntime.start(
                  root,
                  0,
                  database,
                  contexts,
                  null,
                  clock,
                  audit(),
                  java.util.UUID::randomUUID,
                  dispatcher,
                  "worker",
                  1,
                  Duration.ofSeconds(1),
                  ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              WebLogApplicationRuntime.start(
                  root,
                  0,
                  database,
                  contexts,
                  sessionCodec,
                  null,
                  audit(),
                  java.util.UUID::randomUUID,
                  dispatcher,
                  "worker",
                  1,
                  Duration.ofSeconds(1),
                  ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              WebLogApplicationRuntime.start(
                  root,
                  0,
                  database,
                  contexts,
                  sessionCodec,
                  clock,
                  null,
                  java.util.UUID::randomUUID,
                  dispatcher,
                  "worker",
                  1,
                  Duration.ofSeconds(1),
                  ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              WebLogApplicationRuntime.start(
                  root,
                  0,
                  database,
                  contexts,
                  sessionCodec,
                  clock,
                  audit(),
                  null,
                  dispatcher,
                  "worker",
                  1,
                  Duration.ofSeconds(1),
                  ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              WebLogApplicationRuntime.start(
                  root,
                  0,
                  database,
                  contexts,
                  sessionCodec,
                  clock,
                  audit(),
                  java.util.UUID::randomUUID,
                  null,
                  "worker",
                  1,
                  Duration.ofSeconds(1),
                  ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              WebLogApplicationRuntime.start(
                  root,
                  0,
                  database,
                  contexts,
                  sessionCodec,
                  clock,
                  audit(),
                  java.util.UUID::randomUUID,
                  dispatcher,
                  null,
                  1,
                  Duration.ofSeconds(1),
                  ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              WebLogApplicationRuntime.start(
                  root,
                  0,
                  database,
                  contexts,
                  sessionCodec,
                  clock,
                  audit(),
                  java.util.UUID::randomUUID,
                  dispatcher,
                  "worker",
                  1,
                  null,
                  ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              WebLogApplicationRuntime.start(
                  root,
                  0,
                  database,
                  contexts,
                  sessionCodec,
                  clock,
                  audit(),
                  java.util.UUID::randomUUID,
                  dispatcher,
                  "worker",
                  1,
                  Duration.ofSeconds(1),
                  null));
      assertEquals(0, calls.get());
      var primary = new IllegalStateException("startup");
      WebLogApplicationRuntime.closeAfterFailure(
          primary,
          () -> {
            throw new IllegalStateException("worker close");
          },
          () -> {
            throw new IllegalStateException("reply close");
          });
      assertEquals(2, primary.getSuppressed().length);
      WebLogApplicationRuntime.closeAfterFailure(primary, null, () -> {});
      assertEquals(2, primary.getSuppressed().length);
    }
  }

  private WebSecurityAudit audit() {
    return new WebSecurityAudit(System.getLogger("nk.pt.web.runtime"), clock, "1", "1");
  }

  private WebLogDispatcher dispatcher(
      DataSource database,
      WebLogPayloadCodec codec,
      dev.codex.schubert.nk.web.messaging.JmsContextFactory contexts) {
    return new WebLogDispatcher(
        database,
        new WebLogOutboxRepository(() -> 0),
        new WebLogMessageSender(codec, contexts),
        clock);
  }

  private static DataSource source(SqlOpen open) {
    return (DataSource)
        Proxy.newProxyInstance(
            DataSource.class.getClassLoader(),
            new Class<?>[] {DataSource.class},
            (ignored, method, arguments) -> {
              if (method.getName().equals("getConnection")) return open.get();
              throw new AssertionError(method.getName());
            });
  }

  private static int consumerCount(EmbeddedActiveMQ broker) {
    return broker
        .getActiveMQServer()
        .locateQueue(SimpleString.of("nk.sync.reply.web.q"))
        .getConsumerCount();
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

  @FunctionalInterface
  private interface SqlOpen {
    Connection get() throws SQLException;
  }
}
