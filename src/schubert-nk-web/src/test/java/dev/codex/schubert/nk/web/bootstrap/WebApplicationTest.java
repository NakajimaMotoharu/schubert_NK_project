package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.messaging.JmsContextFactory;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.security.MqAuthenticationProvider;
import dev.codex.schubert.nk.web.security.MqLoginClient;
import dev.codex.schubert.nk.web.security.MqLoginContextProbe;
import dev.codex.schubert.nk.web.session.SessionPayloadCodec;
import jakarta.jms.JMSContext;
import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.net.ServerSocket;
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
import java.util.Map;
import java.util.UUID;
import javax.sql.DataSource;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PG222/PT-SCR117..119: actual PG/Flyway, broker and secured HTTP, not deployed services. */
final class WebApplicationTest {
  @TempDir Path root;
  private final Clock clock = Clock.systemUTC();

  @Test
  void scr117ActualIntegratedLoginAndDirectDenial() throws Exception {
    var database = new WebLogDatabaseFixture(Files.createDirectory(root.resolve("pg")));
    var broker = startBroker(Files.createDirectory(root.resolve("broker")));
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var codec = codec();
        var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build()) {
      var app =
          application(
              source(database::web),
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              codec);
      try (var server = app.start(root, 0)) {
        var request =
            HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + server.port() + "/login"))
                .header("X-Forwarded-For", "203.0.113.1")
                .header("X-Forwarded-Proto", "https")
                .build();
        var page = client.send(request, HttpResponse.BodyHandlers.ofString());
        assertEquals(200, page.statusCode());
        var html = Jsoup.parse(page.body());
        assertEquals("schubert NK - ログイン", html.title());
        assertFalse(html.select("input[name=_csrf]").isEmpty());
        assertTrue(
            page.headers().firstValue("Set-Cookie").orElse("").startsWith("SCHUBERT_NK_SESSION="));
        try (var connection = database.web();
            var statement = connection.createStatement();
            var rows =
                statement.executeQuery(
                    "select count(*) from schubert_web_session.web_http_sessions")) {
          assertTrue(rows.next());
          assertEquals(1, rows.getLong(1));
        }
        var direct =
            client.send(
                HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + server.port() + "/login"))
                    .build(),
                HttpResponse.BodyHandlers.ofString());
        assertEquals(403, direct.statusCode());
      }
    } finally {
      broker.stop();
      database.stop();
    }
  }

  @Test
  void scr118DependencyFailurePreventsHttpBind() throws Exception {
    try (var codec = codec()) {
      try (var reserved = new ServerSocket(0)) {
        int port = reserved.getLocalPort();
        var databaseCalls = new java.util.concurrent.atomic.AtomicInteger();
        var brokerCalls = new java.util.concurrent.atomic.AtomicInteger();
        var failingDb =
            application(
                source(
                    () -> {
                      databaseCalls.incrementAndGet();
                      throw new SQLException("private-db-password");
                    }),
                () -> {
                  brokerCalls.incrementAndGet();
                  throw new AssertionError("broker must not be probed");
                },
                codec);
        var failure = assertThrows(WebStartupException.class, () -> failingDb.start(root, port));
        assertEquals("Web technical database is unavailable", failure.getMessage());
        assertEquals(1, databaseCalls.get());
        assertEquals(0, brokerCalls.get());
        var failingBroker =
            application(
                source(() -> connection(true)),
                () -> {
                  brokerCalls.incrementAndGet();
                  throw new IllegalStateException("private-mq-password");
                },
                codec);
        var mqFailure =
            assertThrows(WebStartupException.class, () -> failingBroker.start(root, port));
        assertEquals("Web Artemis reply Queue is unavailable", mqFailure.getMessage());
        assertEquals(1, brokerCalls.get());
        assertFalse(mqFailure.getMessage().contains("password"));
      }
    }
  }

  @Test
  void scr119NullAndInvalidInputStopsBeforeDependencyProbe() throws Exception {
    try (var codec = codec()) {
      DataSource db = source(() -> connection(true));
      JmsContextFactory broker = () -> null;
      var auth = authentication();
      var audit = audit();
      assertThrows(
          NullPointerException.class,
          () -> new WebApplication(null, broker, codec, clock, auth, audit, UUID::randomUUID));
      assertThrows(
          NullPointerException.class,
          () -> new WebApplication(db, null, codec, clock, auth, audit, UUID::randomUUID));
      assertThrows(
          NullPointerException.class,
          () -> new WebApplication(db, broker, null, clock, auth, audit, UUID::randomUUID));
      assertThrows(
          NullPointerException.class,
          () -> new WebApplication(db, broker, codec, null, auth, audit, UUID::randomUUID));
      assertThrows(
          NullPointerException.class,
          () -> new WebApplication(db, broker, codec, clock, null, audit, UUID::randomUUID));
      assertThrows(
          NullPointerException.class,
          () -> new WebApplication(db, broker, codec, clock, auth, null, UUID::randomUUID));
      assertThrows(
          NullPointerException.class,
          () -> new WebApplication(db, broker, codec, clock, auth, audit, null));
      var app = application(db, broker, codec);
      assertThrows(NullPointerException.class, () -> app.start(null, 0));
      assertThrows(NullPointerException.class, () -> app.start(root, 0, (Class<?>[]) null));
      assertThrows(IllegalArgumentException.class, () -> app.start(root.resolve("missing"), 0));
      assertThrows(IllegalArgumentException.class, () -> app.start(root, -1));
      assertThrows(IllegalArgumentException.class, () -> app.start(root, 65536));
      assertThrows(IllegalArgumentException.class, () -> app.start(root, 0, (Class<?>) null));
    }
  }

  @Test
  void scr122InvalidMvcDependencyStopsBeforeDatabaseBorrow() throws Exception {
    try (var codec = codec()) {
      var preProbe =
          application(
              source(
                  () -> {
                    throw new AssertionError("DB must not be probed");
                  }),
              () -> {
                throw new AssertionError("JMS must not be probed");
              },
              codec);
      assertThrows(
          IllegalArgumentException.class,
          () -> preProbe.start(root, 0, Map.of(String.class, new Object())));
    }
  }

  private WebApplication application(
      DataSource db, JmsContextFactory broker, SessionPayloadCodec codec) {
    return new WebApplication(
        db, broker, codec, clock, authentication(), audit(), UUID::randomUUID);
  }

  private MqAuthenticationProvider authentication() {
    var sender =
        (dev.codex.schubert.nk.web.messaging.JmsRequestSender)
            (id, bytes) -> fail("Login must not reach MQ in this GET fixture");
    return new MqAuthenticationProvider(
        new MqLoginClient(
            new JmsRequestReplyClient(), sender, clock, UUID::randomUUID, Duration.ofSeconds(2)),
        new MqLoginContextProbe(
            new JmsRequestReplyClient(), sender, clock, UUID::randomUUID, Duration.ofSeconds(2)));
  }

  private WebSecurityAudit audit() {
    return new WebSecurityAudit(System.getLogger("nk.pt.web.bootstrap"), clock, "1", "1");
  }

  private static SessionPayloadCodec codec() {
    return new SessionPayloadCodec("k1", new byte[32], null, null);
  }

  private static DataSource source(SqlOpen open) {
    return (DataSource)
        Proxy.newProxyInstance(
            DataSource.class.getClassLoader(),
            new Class<?>[] {DataSource.class},
            (instance, method, args) -> {
              if (method.getName().equals("getConnection")) return open.get();
              throw new AssertionError("unexpected DataSource call " + method.getName());
            });
  }

  private static Connection connection(boolean valid) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (instance, method, args) -> {
              if (method.getName().equals("isValid")) return valid;
              if (method.getName().equals("close")) return null;
              throw new AssertionError("unexpected connection call " + method.getName());
            });
  }

  private static EmbeddedActiveMQ startBroker(Path root) throws Exception {
    Configuration config;
    try (InputStream input = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      config = new FileConfigurationParser().parseMainConfig(input);
    }
    config
        .setPagingDirectory(root.resolve("paging").toString())
        .setBindingsDirectory(root.resolve("bindings").toString())
        .setJournalDirectory(root.resolve("journal").toString())
        .setLargeMessagesDirectory(root.resolve("large-messages").toString())
        .setSecurityEnabled(false)
        .clearAcceptorConfigurations()
        .addAcceptorConfiguration("component", "vm://0");
    return new EmbeddedActiveMQ().setConfiguration(config).start();
  }

  @FunctionalInterface
  private interface SqlOpen {
    Connection get() throws SQLException;
  }
}
