package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.application.scenario.ScenarioApplicationAssembly;
import dev.codex.schubert.nk.api.dispatch.ApiLogPathApplicationRuntime;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.security.AuthContextCodec;
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
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.GeneralSecurityException;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Duration;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.Locale;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
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

/** PG231/SSC324 START003: Log-path boot, ownership and distinct fatal infrastructure health. */
final class WebLogApplicationRuntimeTest {
  private static final String FIXTURE_TEST_4D967A30 = "test";
  private static final String FIXTURE_WEB_LOG_WORKER_34947EFB = "web-log-worker";
  private static final String FIXTURE_BROKER_4F6E4F9C = "broker";
  private static final String FIXTURE_VM_0_0C76084A = "vm://0";
  private static final String FIXTURE_HTTP_127_0_0_1_B897D8EE = "http://127.0.0.1:";
  private static final String FIXTURE_X_FORWARDED_FOR_BECAABD0 = "X-Forwarded-For";
  private static final String FIXTURE_203_0_113_1_9BB16FDC = "203.0.113.1";
  private static final String FIXTURE_X_FORWARDED_PROTO_6D975CE8 = "X-Forwarded-Proto";
  private static final String FIXTURE_HTTPS_F7FB094B = "https";
  private static final String FIXTURE_SET_COOKIE_10F4EA2C = "Set-Cookie";
  private static final String FIXTURE_HTTPONLY_03BEA470 = "httponly";
  private static final String FIXTURE_SECURE_ABE38CF1 = "secure";
  private static final String FIXTURE_COOKIE_1E78060F = "Cookie";
  private static final String FIXTURE_HTTP_A321F717 = "http";
  private static final String FIXTURE_WORKER_1636F9EC = "worker";

  @Test
  void start324003FatalReplyInfrastructureSignalsRuntimeWithoutBusinessAck() throws Exception {
    var db = new WebLogDatabaseFixture(Files.createDirectory(root.resolve("pg")));
    var listener = new java.util.concurrent.atomic.AtomicReference<jakarta.jms.MessageListener>();
    var opened = new AtomicInteger();
    var closed = new AtomicInteger();
    var rollbacks = new AtomicInteger();
    var commits = new AtomicInteger();
    var committedSignals = new AtomicInteger();
    var reads = new AtomicInteger();
    var fatal = new AssertionError("synthetic provider fatal");
    dev.codex.schubert.nk.web.messaging.JmsContextFactory contexts =
        () -> {
          opened.incrementAndGet();
          return (JMSContext)
              Proxy.newProxyInstance(
                  JMSContext.class.getClassLoader(),
                  new Class<?>[] {JMSContext.class},
                  (proxy, method, arguments) ->
                      switch (method.getName()) {
                        case "getSessionMode" -> JMSContext.SESSION_TRANSACTED;
                        case "setAutoStart", "start" -> null;
                        case "createQueue" -> new ActiveMQQueue((String) arguments[0]);
                        case "createConsumer" ->
                            Proxy.newProxyInstance(
                                jakarta.jms.JMSConsumer.class.getClassLoader(),
                                new Class<?>[] {jakarta.jms.JMSConsumer.class},
                                (consumer, action, values) ->
                                    switch (action.getName()) {
                                      case "setMessageListener" -> {
                                        assertTrue(
                                            listener.compareAndSet(
                                                null, (jakarta.jms.MessageListener) values[0]));
                                        yield null;
                                      }
                                      case "close" -> null;
                                      default ->
                                          throw new AssertionError(
                                              "unexpected consumer fixture operation");
                                    });
                        case "rollback" -> {
                          rollbacks.incrementAndGet();
                          yield null;
                        }
                        case "commit" -> {
                          commits.incrementAndGet();
                          yield null;
                        }
                        case "close" -> {
                          closed.incrementAndGet();
                          yield null;
                        }
                        default -> throw new AssertionError("unexpected context fixture operation");
                      });
        };
    try (var sessionCodec =
            new SessionPayloadCodec(FIXTURE_TEST_4D967A30, new byte[32], null, null);
        var logCodec = new WebLogPayloadCodec(FIXTURE_TEST_4D967A30, new byte[32], null, null)) {
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
              FIXTURE_WEB_LOG_WORKER_34947EFB,
              10,
              Duration.ofMillis(10),
              ignored -> committedSignals.incrementAndGet())) {
        assertTrue(runtime.ready());
        assertFalse(runtime.terminalFailureObserved());
        assertEquals(2, opened.get(), "reply owner and one readiness probe, no business send");
        assertEquals(1, closed.get(), "only readiness probe has returned before fault");
        var message =
            (jakarta.jms.BytesMessage)
                Proxy.newProxyInstance(
                    jakarta.jms.BytesMessage.class.getClassLoader(),
                    new Class<?>[] {jakarta.jms.BytesMessage.class},
                    (proxy, method, arguments) -> {
                      if (!method.getName().equals("getBodyLength"))
                        throw new AssertionError("unexpected body fixture accessor");
                      reads.incrementAndGet();
                      throw fatal;
                    });
        var callback = listener.get();
        assertNotNull(callback);
        assertSame(fatal, assertThrows(AssertionError.class, () -> callback.onMessage(message)));
        assertEquals(1, reads.get());
        assertEquals(1, rollbacks.get());
        assertEquals(0, commits.get());
        assertEquals(0, committedSignals.get());
        assertTrue(runtime.terminalFailureObserved());
        assertFalse(runtime.ready());
      }
      assertEquals(2, closed.get(), "both synthetic contexts closed by their actual owner scopes");
    } finally {
      db.stop();
    }
  }

  @Test
  void rerun008UnknownWorkerJoinMustRetainReplyOwnerAndAllowRetry() {
    var workerKnownStopped = new AtomicBoolean();
    var repliesClosed = new AtomicInteger();
    var httpClosed = new AtomicInteger();
    var runtime =
        new WebLogApplicationRuntime(
            httpClosed::incrementAndGet,
            () -> {
              if (!workerKnownStopped.get())
                throw new IllegalStateException("synthetic join UNKNOWN");
            },
            repliesClosed::incrementAndGet,
            () -> 1234,
            () -> true,
            () -> true,
            new AtomicBoolean());
    assertTrue(runtime.ready());
    assertThrows(IllegalStateException.class, runtime::close);
    assertFalse(runtime.ready());
    assertEquals(0, repliesClosed.get());
    assertThrows(IllegalStateException.class, runtime::close);
    assertEquals(0, repliesClosed.get());
    workerKnownStopped.set(true);
    runtime.close();
    assertEquals(1, repliesClosed.get());
    runtime.close();
    assertEquals(1, repliesClosed.get());
    assertEquals(1, httpClosed.get());
  }

  @TempDir Path root;
  private final Clock clock = Clock.systemUTC();

  @Test
  void scr134RealHttpLoginUsesProductionApiBrokerAndSession() throws Exception {
    var db = new WebLogDatabaseFixture(Files.createDirectory(root.resolve("pg")));
    var broker = startBroker(Files.createDirectory(root.resolve(FIXTURE_BROKER_4F6E4F9C)));
    try (var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        var fingerprints = new FingerprintKeyRing("f1", syntheticKey(7), null, null);
        var contexts = new AuthContextCodec("a1", syntheticKey(1), null, null);
        var snapshots = new ResponseSnapshotCodec("s1", syntheticKey(3), null, null);
        var sessionCodec =
            new SessionPayloadCodec(FIXTURE_TEST_4D967A30, syntheticKey(4), null, null);
        var logCodec = new WebLogPayloadCodec(FIXTURE_TEST_4D967A30, syntheticKey(5), null, null);
        var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build()) {
      try (var connection = db.api();
          var statement =
              connection.prepareStatement(
                  "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at)"
                      + " values(7,'reader','reader',?,'USER','ACTIVE','2026-09-24','2026-09-24','2026-09-24')")) {
        statement.setString(1, independentLoginHash());
        assertEquals(1, statement.executeUpdate());
      }
      var transport =
          (dev.codex.schubert.nk.web.messaging.JmsContextFactory)
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED);
      try (var api =
              ApiLogPathApplicationRuntime.startWithLogin(
                  () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
                  () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
                  source(db::api),
                  fingerprints,
                  contexts,
                  snapshots,
                  ignored -> {
                    throw new AssertionError("game is outside Login PT");
                  },
                  ignored -> {
                    throw new AssertionError("Log search is outside Login PT");
                  },
                  clock,
                  ignored -> {
                    throw new AssertionError("unexpected terminal API delivery");
                  });
          var web =
              WebLogApplicationRuntime.start(
                  root,
                  0,
                  source(db::web),
                  transport,
                  sessionCodec,
                  clock,
                  audit(),
                  java.util.UUID::randomUUID,
                  dispatcher(source(db::web), logCodec, transport),
                  FIXTURE_WEB_LOG_WORKER_34947EFB,
                  10,
                  Duration.ofMillis(10),
                  ignored -> {
                    throw new AssertionError("unexpected terminal Web reply");
                  })) {
        assertTrue(api.ready());
        assertTrue(web.ready());
        URI login = URI.create(FIXTURE_HTTP_127_0_0_1_B897D8EE + web.port() + "/login");
        var get =
            client.send(
                HttpRequest.newBuilder(login)
                    .header(FIXTURE_X_FORWARDED_FOR_BECAABD0, FIXTURE_203_0_113_1_9BB16FDC)
                    .header(FIXTURE_X_FORWARDED_PROTO_6D975CE8, FIXTURE_HTTPS_F7FB094B)
                    .build(),
                HttpResponse.BodyHandlers.ofString());
        assertEquals(200, get.statusCode());
        var page = Jsoup.parse(get.body());
        assertEquals("schubert NK - ログイン", page.title());
        var hidden = page.selectFirst("input[name=_csrf]");
        assertNotNull(hidden);
        String csrf = hidden.attr("value");
        assertFalse(csrf.isEmpty());
        String anonymousSetCookie =
            get.headers().firstValue(FIXTURE_SET_COOKIE_10F4EA2C).orElseThrow();
        assertTrue(anonymousSetCookie.toLowerCase(Locale.ROOT).contains(FIXTURE_HTTPONLY_03BEA470));
        assertTrue(anonymousSetCookie.toLowerCase(Locale.ROOT).contains(FIXTURE_SECURE_ABE38CF1));
        String anonymousCookie = anonymousSetCookie.split(";", 2)[0];
        assertTrue(anonymousCookie.startsWith("SCHUBERT_NK_SESSION="));
        String form =
            "username=reader&password=synthetic-password&_csrf="
                + URLEncoder.encode(csrf, StandardCharsets.UTF_8);
        var post =
            client.send(
                HttpRequest.newBuilder(login)
                    .header(FIXTURE_X_FORWARDED_FOR_BECAABD0, FIXTURE_203_0_113_1_9BB16FDC)
                    .header(FIXTURE_X_FORWARDED_PROTO_6D975CE8, FIXTURE_HTTPS_F7FB094B)
                    .header(FIXTURE_COOKIE_1E78060F, anonymousCookie)
                    .header("Content-Type", "application/x-www-form-urlencoded;charset=UTF-8")
                    .POST(HttpRequest.BodyPublishers.ofString(form, StandardCharsets.UTF_8))
                    .build(),
                HttpResponse.BodyHandlers.ofString());
        assertEquals(302, post.statusCode());
        assertEquals("/", post.headers().firstValue("Location").orElseThrow());
        String authenticatedSetCookie =
            post.headers().firstValue(FIXTURE_SET_COOKIE_10F4EA2C).orElseThrow();
        assertTrue(
            authenticatedSetCookie.toLowerCase(Locale.ROOT).contains(FIXTURE_HTTPONLY_03BEA470));
        assertTrue(
            authenticatedSetCookie.toLowerCase(Locale.ROOT).contains(FIXTURE_SECURE_ABE38CF1));
        String authenticatedCookie = authenticatedSetCookie.split(";", 2)[0];
        assertTrue(authenticatedCookie.startsWith("SCHUBERT_NK_SESSION="));
        assertNotEquals(anonymousCookie, authenticatedCookie);
        var menu =
            client.send(
                HttpRequest.newBuilder(
                        URI.create(FIXTURE_HTTP_127_0_0_1_B897D8EE + web.port() + "/"))
                    .header(FIXTURE_X_FORWARDED_FOR_BECAABD0, FIXTURE_203_0_113_1_9BB16FDC)
                    .header(FIXTURE_X_FORWARDED_PROTO_6D975CE8, FIXTURE_HTTPS_F7FB094B)
                    .header(FIXTURE_COOKIE_1E78060F, authenticatedCookie)
                    .build(),
                HttpResponse.BodyHandlers.ofString());
        assertEquals(200, menu.statusCode());
        assertEquals(
            1,
            count(
                db.api(),
                "select count(*) from schubert.request_inbox where request_layout_id='LGNREQ01' and processing_state='COMPLETED' and result_ref_type='AUTH_SESSION'"));
        assertEquals(
            1,
            count(
                db.api(),
                "select count(*) from schubert.auth_sessions where user_id=7 and not revoked"));
        assertEquals(
            1,
            count(
                db.api(), "select count(*) from schubert.app_logs where action='LOGIN_SUCCEEDED'"));
        assertEquals(0, count(db.api(), "select failed_count from schubert.app_users where id=7"));
        assertEquals(
            1, count(db.web(), "select count(*) from schubert_web_session.web_http_sessions"));
        assertTrue(api.ready());
        assertTrue(web.ready());
      }
    } finally {
      broker.stop();
      db.stop();
    }
  }

  @Test
  void scr135RealHttpAdminLogSearchUsesProductionApiBroker() throws Exception {
    var db = new WebLogDatabaseFixture(Files.createDirectory(root.resolve("pg")));
    var broker = startBroker(Files.createDirectory(root.resolve(FIXTURE_BROKER_4F6E4F9C)));
    try (var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        var fingerprints = new FingerprintKeyRing("f1", syntheticKey(7), null, null);
        var contexts = new AuthContextCodec("a1", syntheticKey(1), null, null);
        var snapshots = new ResponseSnapshotCodec("s1", syntheticKey(3), null, null);
        var sessionCodec =
            new SessionPayloadCodec(FIXTURE_TEST_4D967A30, syntheticKey(4), null, null);
        var logCodec = new WebLogPayloadCodec(FIXTURE_TEST_4D967A30, syntheticKey(5), null, null);
        var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build()) {
      try (var connection = db.api();
          var statement =
              connection.prepareStatement(
                  "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at)"
                      + " values(8,'adminpt','adminpt',?,'ADMIN','ACTIVE','2026-09-24','2026-09-24','2026-09-24')")) {
        statement.setString(1, independentLoginHash());
        assertEquals(1, statement.executeUpdate());
      }
      var gameService =
          ScenarioApplicationAssembly.create(
              source(db::api),
              fingerprints,
              snapshots,
              (records, generatedAt) -> {
                throw new AssertionError("file publication is outside SCR135");
              },
              descriptor -> {
                throw new AssertionError("file inspection is outside SCR135");
              },
              clock);
      var transport =
          (dev.codex.schubert.nk.web.messaging.JmsContextFactory)
              () -> factory.createContext(JMSContext.SESSION_TRANSACTED);
      try (var api =
              ApiLogPathApplicationRuntime.startWithLoginAndLog(
                  () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
                  () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
                  source(db::api),
                  fingerprints,
                  contexts,
                  snapshots,
                  gameService,
                  clock,
                  ignored -> {
                    throw new AssertionError("unexpected terminal API delivery");
                  });
          var web =
              WebLogApplicationRuntime.startWithScenario(
                  root,
                  0,
                  source(db::web),
                  transport,
                  sessionCodec,
                  clock,
                  audit(),
                  java.util.UUID::randomUUID,
                  dispatcher(source(db::web), logCodec, transport),
                  FIXTURE_WEB_LOG_WORKER_34947EFB,
                  10,
                  Duration.ofMillis(10),
                  ignored -> {
                    throw new AssertionError("unexpected terminal Web reply");
                  })) {
        URI login = URI.create(FIXTURE_HTTP_127_0_0_1_B897D8EE + web.port() + "/login");
        var get =
            client.send(
                HttpRequest.newBuilder(login)
                    .header(FIXTURE_X_FORWARDED_FOR_BECAABD0, FIXTURE_203_0_113_1_9BB16FDC)
                    .header(FIXTURE_X_FORWARDED_PROTO_6D975CE8, FIXTURE_HTTPS_F7FB094B)
                    .build(),
                HttpResponse.BodyHandlers.ofString());
        assertEquals(200, get.statusCode());
        assertEquals("schubert NK - ログイン", Jsoup.parse(get.body()).title());
        var csrf = Jsoup.parse(get.body()).selectFirst("input[name=_csrf]");
        assertNotNull(csrf);
        assertFalse(csrf.attr("value").isEmpty());
        String anonymous = get.headers().firstValue(FIXTURE_SET_COOKIE_10F4EA2C).orElseThrow();
        assertTrue(anonymous.toLowerCase(Locale.ROOT).contains(FIXTURE_SECURE_ABE38CF1));
        assertTrue(anonymous.toLowerCase(Locale.ROOT).contains(FIXTURE_HTTPONLY_03BEA470));
        String form =
            "username=adminpt&password=synthetic-password&_csrf="
                + URLEncoder.encode(csrf.attr("value"), StandardCharsets.UTF_8);
        var post =
            client.send(
                HttpRequest.newBuilder(login)
                    .header(FIXTURE_X_FORWARDED_FOR_BECAABD0, FIXTURE_203_0_113_1_9BB16FDC)
                    .header(FIXTURE_X_FORWARDED_PROTO_6D975CE8, FIXTURE_HTTPS_F7FB094B)
                    .header(FIXTURE_COOKIE_1E78060F, anonymous.split(";", 2)[0])
                    .header("Content-Type", "application/x-www-form-urlencoded;charset=UTF-8")
                    .POST(HttpRequest.BodyPublishers.ofString(form, StandardCharsets.UTF_8))
                    .build(),
                HttpResponse.BodyHandlers.ofString());
        assertEquals(302, post.statusCode());
        assertEquals("/", post.headers().firstValue("Location").orElseThrow());
        String authenticated = post.headers().firstValue(FIXTURE_SET_COOKIE_10F4EA2C).orElseThrow();
        assertTrue(authenticated.toLowerCase(Locale.ROOT).contains(FIXTURE_SECURE_ABE38CF1));
        assertTrue(authenticated.toLowerCase(Locale.ROOT).contains(FIXTURE_HTTPONLY_03BEA470));
        String cookie = authenticated.split(";", 2)[0];
        assertNotEquals(anonymous.split(";", 2)[0], cookie);
        try (var connection = db.api();
            var statement = connection.createStatement()) {
          assertEquals(
              1,
              statement.executeUpdate(
                  "insert into schubert.app_logs(logged_at,service,category,level,action,message)"
                      + " values(current_timestamp,'API','ACTION','INFO','PTSCR135','synthetic log result')"));
        }
        var result =
            client.send(
                HttpRequest.newBuilder(
                        URI.create(
                            FIXTURE_HTTP_127_0_0_1_B897D8EE + web.port() + "/logs?action=PTSCR135"))
                    .header(FIXTURE_X_FORWARDED_FOR_BECAABD0, FIXTURE_203_0_113_1_9BB16FDC)
                    .header(FIXTURE_X_FORWARDED_PROTO_6D975CE8, FIXTURE_HTTPS_F7FB094B)
                    .header(FIXTURE_COOKIE_1E78060F, cookie)
                    .build(),
                HttpResponse.BodyHandlers.ofString());
        assertEquals(200, result.statusCode());
        var rows = Jsoup.parse(result.body()).select(".log-row");
        assertEquals(1, rows.size());
        assertTrue(rows.first().text().contains("PTSCR135"));
        assertTrue(rows.first().text().contains("synthetic log result"));
        var games =
            client.send(
                HttpRequest.newBuilder(
                        URI.create(FIXTURE_HTTP_127_0_0_1_B897D8EE + web.port() + "/scenarios"))
                    .header(FIXTURE_X_FORWARDED_FOR_BECAABD0, FIXTURE_203_0_113_1_9BB16FDC)
                    .header(FIXTURE_X_FORWARDED_PROTO_6D975CE8, FIXTURE_HTTPS_F7FB094B)
                    .header(FIXTURE_COOKIE_1E78060F, cookie)
                    .build(),
                HttpResponse.BodyHandlers.ofString());
        assertEquals(200, games.statusCode());
        assertEquals("Scenario Games", Jsoup.parse(games.body()).selectFirst("h1").text());
        assertEquals(
            1,
            count(
                db.api(),
                "select count(*) from schubert.request_inbox where request_layout_id='GAMREQ01' and processing_state='COMPLETED'"));
        assertEquals(
            1,
            count(
                db.api(),
                "select count(*) from schubert.request_inbox where request_layout_id='LGSREQ01' and processing_state='COMPLETED'"));
        assertEquals(
            1, count(db.api(), "select count(*) from schubert.app_logs where action='PTSCR135'"));
        assertTrue(api.ready());
        assertTrue(web.ready());
      }
    } finally {
      broker.stop();
      db.stop();
    }
  }

  private static int count(Connection connection, String query) throws SQLException {
    try (connection;
        var statement = connection.createStatement();
        var rows = statement.executeQuery(query)) {
      assertTrue(rows.next());
      int value = rows.getInt(1);
      assertFalse(rows.next());
      return value;
    }
  }

  private static byte[] syntheticKey(int value) {
    byte[] bytes = new byte[32];
    Arrays.fill(bytes, (byte) value);
    return bytes;
  }

  private static String independentLoginHash() throws GeneralSecurityException {
    byte[] salt = new byte[16];
    Arrays.fill(salt, (byte) 17);
    var specification = new PBEKeySpec("synthetic-password".toCharArray(), salt, 310000, 256);
    try {
      return "{pbkdf2-v1}"
          + HexFormat.of().formatHex(salt)
          + HexFormat.of()
              .formatHex(
                  SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
                      .generateSecret(specification)
                      .getEncoded());
    } finally {
      specification.clearPassword();
      Arrays.fill(salt, (byte) 0);
    }
  }

  @Test
  void scr127RealReplyWorkerAndSecuredLogMvcStartAndClose() throws Exception {
    var db = new WebLogDatabaseFixture(Files.createDirectory(root.resolve("pg")));
    var broker = startBroker(Files.createDirectory(root.resolve(FIXTURE_BROKER_4F6E4F9C)));
    try (var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        var sessionCodec =
            new SessionPayloadCodec(FIXTURE_TEST_4D967A30, new byte[32], null, null);
        var logCodec = new WebLogPayloadCodec(FIXTURE_TEST_4D967A30, new byte[32], null, null);
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
              FIXTURE_WEB_LOG_WORKER_34947EFB,
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
              HttpRequest.newBuilder(URI.create(FIXTURE_HTTP_127_0_0_1_B897D8EE + port + "/login"))
                  .header(FIXTURE_X_FORWARDED_FOR_BECAABD0, FIXTURE_203_0_113_1_9BB16FDC)
                  .header(FIXTURE_X_FORWARDED_PROTO_6D975CE8, FIXTURE_HTTPS_F7FB094B)
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
    var broker = startBroker(Files.createDirectory(root.resolve(FIXTURE_BROKER_4F6E4F9C)));
    try (var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        var producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var dlq = observer.createConsumer(new ActiveMQQueue("nk.dead.letter::nk.dead.letter.q"));
        var sessionCodec =
            new SessionPayloadCodec(FIXTURE_TEST_4D967A30, new byte[32], null, null);
        var logCodec = new WebLogPayloadCodec(FIXTURE_TEST_4D967A30, new byte[32], null, null)) {
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
              FIXTURE_WEB_LOG_WORKER_34947EFB,
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
    var broker = startBroker(Files.createDirectory(root.resolve(FIXTURE_BROKER_4F6E4F9C)));
    try (var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A);
        var sessionCodec =
            new SessionPayloadCodec(FIXTURE_TEST_4D967A30, new byte[32], null, null);
        var logCodec = new WebLogPayloadCodec(FIXTURE_TEST_4D967A30, new byte[32], null, null)) {
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
                  FIXTURE_WEB_LOG_WORKER_34947EFB,
                  10,
                  Duration.ofMillis(10),
                  ignored -> {}));
      assertEquals(0, consumerCount(broker));
    } finally {
      broker.stop();
    }
  }

  @Test
  void scr130LifecycleRetainsUnknownResourceAndReadinessBoundaries() throws Exception {
    var order = new java.util.ArrayList<String>();
    var terminal = new AtomicBoolean();
    var runtime =
        new WebLogApplicationRuntime(
            () -> {
              order.add(FIXTURE_HTTP_A321F717);
              throw new SQLException("http close");
            },
            () -> {
              order.add(FIXTURE_WORKER_1636F9EC);
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
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertEquals(java.util.List.of(FIXTURE_HTTP_A321F717), order);
    assertThrows(IllegalStateException.class, runtime::close);
    assertEquals(java.util.List.of(FIXTURE_HTTP_A321F717, FIXTURE_HTTP_A321F717), order);
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
  void scr133SameThrowableAcrossOwnedClosuresKeepsPrimary() throws Exception {
    SQLException shared = new SQLException("synthetic shared close failure");
    AtomicInteger closes = new AtomicInteger();
    AutoCloseable owner =
        () -> {
          closes.incrementAndGet();
          throw shared;
        };
    var runtime =
        new WebLogApplicationRuntime(
            owner, owner, owner, () -> 1, () -> true, () -> true, new AtomicBoolean());
    IllegalStateException stopped = assertThrows(IllegalStateException.class, runtime::close);
    assertEquals("Web Log runtime stop failed", stopped.getMessage());
    assertNull(stopped.getCause());
    assertEquals(0, shared.getSuppressed().length);
    assertEquals(1, closes.get());

    // SSC324/BUG1575: same-object startup UNKNOWN must retain, not return after two closes.
    WebStartupRetentionTest.assertOwnedRetention(root, java.util.List.of("3"));
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
    try (var sessionCodec =
            new SessionPayloadCodec(FIXTURE_TEST_4D967A30, new byte[32], null, null);
        var logCodec = new WebLogPayloadCodec(FIXTURE_TEST_4D967A30, new byte[32], null, null)) {
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
                  FIXTURE_WORKER_1636F9EC,
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
                  FIXTURE_WORKER_1636F9EC,
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
                  FIXTURE_WORKER_1636F9EC,
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
                  FIXTURE_WORKER_1636F9EC,
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
                  FIXTURE_WORKER_1636F9EC,
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
                  FIXTURE_WORKER_1636F9EC,
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
                  FIXTURE_WORKER_1636F9EC,
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
                  FIXTURE_WORKER_1636F9EC,
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
                  FIXTURE_WORKER_1636F9EC,
                  1,
                  Duration.ofSeconds(1),
                  null));
      assertEquals(0, calls.get());
      var primary = new IllegalStateException("startup");
      // SSC324/BUG1575: keep worker and reply UNKNOWN branches in finite, inert owned JVMs.
      WebStartupRetentionTest.assertOwnedRetention(root, java.util.List.of("1", "4"));
      var normalReplyClosed = new AtomicInteger();
      WebLogApplicationRuntime.closeAfterFailure(primary, null, normalReplyClosed::incrementAndGet);
      assertEquals(1, normalReplyClosed.get());
      assertEquals(0, primary.getSuppressed().length);
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
        .addAcceptorConfiguration("component", FIXTURE_VM_0_0C76084A);
    return new EmbeddedActiveMQ().setConfiguration(configuration).start();
  }

  @FunctionalInterface
  private interface SqlOpen {
    Connection get() throws SQLException;
  }
}
