package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.web.config.LogMvcConfiguration;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.messaging.JmsContextFactory;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.LogSearchWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.security.MqAuthenticationProvider;
import dev.codex.schubert.nk.web.security.MqLoginClient;
import dev.codex.schubert.nk.web.security.MqLoginContextProbe;
import dev.codex.schubert.nk.web.session.SessionPayloadCodec;
import dev.codex.schubert.nk.web.session.SpringEncryptedSessionRepository;
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
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
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
      var captured = new AtomicReference<WebHttpServer>();
      try (var server =
          app.startOwnedWithCoreSessionDependencies(
              root, 0, (core, sessions) -> Map.of(), captured::set)) {
        assertSame(server, captured.get());
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
  void nativeCore003LegacyEntriesStillUseActualEncryptedSecurityChain() throws Exception {
    // BUG661: literal HTTP/SQL expectations cover the legacy delegates, not a coverage-only call.
    var database = new WebLogDatabaseFixture(Files.createDirectory(root.resolve("legacy-pg")));
    var broker = startBroker(Files.createDirectory(root.resolve("legacy-broker")));
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var codec = codec();
        var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build()) {
      var app =
          application(
              source(database::web),
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              codec);
      var supplied = new AtomicReference<SpringEncryptedSessionRepository>();
      for (int entry = 0; entry < 2; entry++) {
        try (var server =
            entry == 0
                ? app.start(root, 0)
                : app.startWithSessionDependencies(
                    root,
                    0,
                    sessions -> {
                      assertNull(supplied.get());
                      supplied.set(sessions);
                      return Map.of();
                    })) {
          var uri = URI.create("http://127.0.0.1:" + server.port() + "/login");
          var page =
              client.send(
                  HttpRequest.newBuilder(uri)
                      .header("X-Forwarded-For", "203.0.113.1")
                      .header("X-Forwarded-Proto", "https")
                      .build(),
                  HttpResponse.BodyHandlers.ofString());
          assertEquals(200, page.statusCode());
          var html = Jsoup.parse(page.body());
          assertEquals("schubert NK - ログイン", html.title());
          assertFalse(html.select("input[name=_csrf]").isEmpty());
          assertTrue(
              page.headers()
                  .firstValue("Set-Cookie")
                  .orElse("")
                  .startsWith("SCHUBERT_NK_SESSION="));
          try (var connection = database.web();
              var statement = connection.createStatement();
              var rows =
                  statement.executeQuery(
                      "select count(*) from schubert_web_session.web_http_sessions")) {
            assertTrue(rows.next());
            assertEquals(entry + 1L, rows.getLong(1));
            assertFalse(rows.next());
          }
          assertEquals(
              403,
              client
                  .send(HttpRequest.newBuilder(uri).build(), HttpResponse.BodyHandlers.ofString())
                  .statusCode());
        }
      }
      assertNotNull(supplied.get());
    } finally {
      broker.stop();
      database.stop();
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

  @Test
  void scr124SessionFactoryWiresLogMvcUsingSecurityRepository() throws Exception {
    var database = new WebLogDatabaseFixture(Files.createDirectory(root.resolve("pg")));
    var broker = startBroker(Files.createDirectory(root.resolve("broker")));
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var codec = codec();
        var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build()) {
      var audit = audit();
      var app =
          new WebApplication(
              source(database::web),
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              codec,
              clock,
              authentication(),
              audit,
              UUID::randomUUID);
      var supplied = new AtomicReference<SpringEncryptedSessionRepository>();
      var calls = new AtomicInteger();
      try (var server =
          app.startWithSessionDependencies(
              root,
              0,
              sessions -> {
                calls.incrementAndGet();
                supplied.set(sessions);
                var search =
                    new LogSearchWireClient(
                        new JmsRequestReplyClient(),
                        (id, bytes) -> fail("no search on GET /login"),
                        clock,
                        UUID::randomUUID,
                        Duration.ofSeconds(2));
                return Map.<Class<?>, Object>of(
                    LogSearchWireClient.class,
                    search,
                    ApiSessionInvalidHandler.class,
                    new ApiSessionInvalidHandler(sessions, audit));
              },
              LogMvcConfiguration.class)) {
        var page =
            client.send(
                HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + server.port() + "/login"))
                    .header("X-Forwarded-For", "203.0.113.1")
                    .header("X-Forwarded-Proto", "https")
                    .build(),
                HttpResponse.BodyHandlers.ofString());
        assertEquals(200, page.statusCode());
        assertEquals("schubert NK - ログイン", Jsoup.parse(page.body()).title());
        assertEquals(1, calls.get());
        assertNotNull(supplied.get());
        String cookie = page.headers().firstValue("Set-Cookie").orElseThrow();
        String sessionId = cookie.substring("SCHUBERT_NK_SESSION=".length(), cookie.indexOf(';'));
        assertNotNull(supplied.get().findById(sessionId));
      }
    } finally {
      broker.stop();
      database.stop();
    }
  }

  @Test
  void scr125NullSessionFactoryStopsBeforeBorrowingResources() throws Exception {
    try (var codec = codec()) {
      var app =
          application(
              source(
                  () -> {
                    throw new AssertionError("DB must not be borrowed");
                  }),
              () -> {
                throw new AssertionError("JMS must not be borrowed");
              },
              codec);
      assertThrows(
          NullPointerException.class, () -> app.startWithSessionDependencies(root, 0, null));
    }
  }

  @Test
  void scr126InvalidSessionDependenciesStopBeforeHttpBind() throws Exception {
    var broker = startBroker(Files.createDirectory(root.resolve("broker")));
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var codec = codec();
        var reserved = new ServerSocket(0)) {
      var app =
          application(
              source(() -> connection(true)),
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
              codec);
      var calls = new AtomicInteger();
      assertThrows(
          NullPointerException.class,
          () ->
              app.startWithSessionDependencies(
                  root,
                  reserved.getLocalPort(),
                  sessions -> {
                    calls.incrementAndGet();
                    return null;
                  }));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              app.startWithSessionDependencies(
                  root, reserved.getLocalPort(), sessions -> Map.of(String.class, new Object())));
      assertEquals(1, calls.get());
      assertFalse(reserved.isClosed());
    } finally {
      broker.stop();
    }
  }

  @Test
  void nativeCore001ExactFactoryPairReflectsHeldTokenIntoActualSecuritySession() throws Exception {
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
      var suppliedCore =
          new AtomicReference<dev.codex.schubert.nk.web.session.EncryptedWebSessionRepository>();
      var suppliedSpring = new AtomicReference<SpringEncryptedSessionRepository>();
      var calls = new AtomicInteger();
      try (var server =
          app.startWithCoreSessionDependencies(
              root,
              0,
              (core, sessions) -> {
                calls.incrementAndGet();
                suppliedCore.set(core);
                suppliedSpring.set(sessions);
                return Map.of();
              })) {
        var page =
            client.send(
                HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + server.port() + "/login"))
                    .header("X-Forwarded-For", "203.0.113.1")
                    .header("X-Forwarded-Proto", "https")
                    .build(),
                HttpResponse.BodyHandlers.ofString());
        assertEquals(200, page.statusCode());
        assertEquals("schubert NK - ログイン", Jsoup.parse(page.body()).title());
        assertEquals(1, calls.get());
        String cookie = page.headers().firstValue("Set-Cookie").orElseThrow();
        String sessionId = cookie.substring("SCHUBERT_NK_SESSION=".length(), cookie.indexOf(';'));
        var session = suppliedSpring.get().findById(sessionId);
        assertNotNull(session);
        var principal =
            new dev.codex.schubert.nk.web.session.SessionPrincipal(
                "reader",
                dev.codex.schubert.nk.protocol.layout.semantic.UserRole.USER,
                dev.codex.schubert.nk.protocol.header.AuthenticationContext.of("a".repeat(64)),
                clock.instant());
        session.setAttribute(
            dev.codex.schubert.nk.web.session.SpringWebSession.PRINCIPAL, principal);
        var current = dev.codex.schubert.nk.web.session.WebSessionId.parse(session.getId());
        UUID expected = new UUID(0, 123);
        assertTrue(
            suppliedCore
                .get()
                .mutate(
                    current,
                    attributes ->
                        new dev.codex.schubert.nk.web.session.SessionAttributes(
                            attributes.principal(),
                            attributes.csrfToken(),
                            attributes.savedRequest(),
                            java.util.List.of(
                                new dev.codex.schubert.nk.web.session.SessionOperationToken(
                                    "QDLREQ01", expected, clock.instant()))))
                .isPresent());
        var tokens =
            new dev.codex.schubert.nk.web.session.SessionOperationTokenLifecycle(
                suppliedCore.get(), clock);
        assertEquals(expected, tokens.require(current, "QDLREQ01", expected).token());
        var fresh = suppliedSpring.get().findById(current.cookieValue());
        assertNotNull(fresh);
        java.util.List<dev.codex.schubert.nk.web.session.SessionOperationToken> retained =
            fresh.getAttribute(dev.codex.schubert.nk.web.session.SpringWebSession.OPERATION_TOKENS);
        assertNotNull(retained);
        assertEquals(1, retained.size());
        assertEquals(expected, retained.getFirst().token());
        assertEquals("QDLREQ01", retained.getFirst().purpose());
        assertTrue(retained.getFirst().completedAt().isEmpty());
      }
    } finally {
      broker.stop();
      database.stop();
    }
  }

  @Test
  void nativeCore002NullFactoryAndLocalPathStopBeforeResources() throws Exception {
    try (var codec = codec()) {
      var app =
          application(
              source(
                  () -> {
                    throw new AssertionError("DB must not be borrowed");
                  }),
              () -> {
                throw new AssertionError("JMS must not be borrowed");
              },
              codec);
      assertThrows(
          NullPointerException.class, () -> app.startWithCoreSessionDependencies(root, 0, null));
      assertThrows(
          NullPointerException.class,
          () -> app.startOwnedWithCoreSessionDependencies(root, 0, null, ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () -> app.startOwnedWithCoreSessionDependencies(root, 0, (a, b) -> Map.of(), null));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              app.startOwnedWithCoreSessionDependencies(
                  root, -1, (a, b) -> Map.of(), ignored -> {}));
      assertThrows(
          NullPointerException.class,
          () -> app.startWithCoreSessionDependencies(null, 0, (a, b) -> Map.of()));
      assertThrows(
          IllegalArgumentException.class,
          () -> app.startWithCoreSessionDependencies(root, -1, (a, b) -> Map.of()));
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
