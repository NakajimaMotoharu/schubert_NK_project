package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.logging.WebLogOutboxRepository;
import dev.codex.schubert.nk.web.logging.WebLogPayloadCodec;
import dev.codex.schubert.nk.web.logging.WebMediaAudit;
import dev.codex.schubert.nk.web.logging.WebRequestLogProducer;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.media.DescriptorFileResolver;
import dev.codex.schubert.nk.web.media.MediaRangeService;
import dev.codex.schubert.nk.web.messaging.AnimationWireClient;
import dev.codex.schubert.nk.web.messaging.ArtemisRequestSender;
import dev.codex.schubert.nk.web.messaging.JmsContextFactory;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.LogSearchWireClient;
import dev.codex.schubert.nk.web.messaging.MediaDescriptorWireClient;
import dev.codex.schubert.nk.web.messaging.MusicWireClient;
import dev.codex.schubert.nk.web.messaging.NotificationWireClient;
import dev.codex.schubert.nk.web.messaging.QuestionWireClient;
import dev.codex.schubert.nk.web.messaging.ScenarioWireClient;
import dev.codex.schubert.nk.web.messaging.UserAdministrationWireClient;
import dev.codex.schubert.nk.web.revocation.RevocationPayloadCodec;
import dev.codex.schubert.nk.web.security.MqAuthenticationProvider;
import dev.codex.schubert.nk.web.security.MqLoginClient;
import dev.codex.schubert.nk.web.security.MqLoginContextProbe;
import dev.codex.schubert.nk.web.session.SessionPayloadCodec;
import dev.codex.schubert.nk.web.storage.LargeResultReader;
import java.io.InputStream;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermissions;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Duration;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import javax.sql.DataSource;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Actual full MVC registration, fixed independent UI/SS routes; NATIVE-GRAPH001002. */
final class WebBusinessAssemblyTest {
  @TempDir Path root;
  private static final Set<String> ROUTES =
      Set.of(
          "/",
          "/login",
          "/logout",
          "/error",
          "/search",
          "/logs",
          "/scenarios",
          "/scenarios/{id:[0-9]{1,12}}",
          "/scenarios/{game:NUKITASHI[12]}",
          "/scenarios/{game:NUKITASHI[12]}/{prefix:[0-9]{2}}",
          "/animation",
          "/animation/main",
          "/animation/ova",
          "/animation/opening",
          "/animation/videos/{id}",
          "/animation/media/{id}",
          "/music",
          "/music/{category}",
          "/music/{category}/{section}",
          "/music/media/{id}",
          "/music/download/{id}",
          "/audio/{id}",
          "/audio/{id}/download",
          "/admin/users",
          "/admin/users/new",
          "/admin/users/{id:[0-9]{1,12}}",
          "/questions",
          "/questions/new",
          "/questions/accepted/{receiptId}",
          "/questions/{id:[0-9]{1,12}}",
          "/notifications",
          "/notifications/{id:[0-9]{1,12}}");

  @Test
  void graph001ActualWholeMvcAndSamePairBeforeAdmission() throws Exception {
    var db = new WebLogDatabaseFixture(Files.createDirectory(root.resolve("pg")));
    var broker = broker(Files.createDirectory(root.resolve("broker")));
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var session = new SessionPayloadCodec("s1", new byte[32], null, null);
        var log = new WebLogPayloadCodec("l1", new byte[32], null, null);
        var revoke = new RevocationPayloadCodec("r1", new byte[32], null, null);
        var transfer = directory("transfer");
        var assets = directory("assets");
        var http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).build()) {
      var database = source(db);
      var clock = Clock.systemUTC();
      var client = new JmsRequestReplyClient();
      JmsContextFactory contexts =
          () -> factory.createContext(jakarta.jms.JMSContext.SESSION_TRANSACTED);
      var sender = new ArtemisRequestSender(contexts);
      var audit = new WebSecurityAudit(System.getLogger("pgpt.graph"), clock, "1", "1");
      var logger =
          new WebRequestLogProducer(
              database,
              log,
              new WebLogOutboxRepository(),
              System.getLogger("pgpt.graph.request"),
              clock,
              UUID::randomUUID,
              "1",
              "1",
              () -> fail("no terminal"));
      var gate = new WebHttpAdmission();
      var identity = identity(root.resolve("assets"));
      var assembly =
          new WebBusinessAssembly(
              client,
              sender,
              clock,
              UUID::randomUUID,
              audit,
              database,
              new LargeResultReader(transfer, identity(root.resolve("transfer"))),
              new MediaRangeService(new DescriptorFileResolver(assets, identity)),
              new WebMediaAudit(System.getLogger("pgpt.graph.media"), clock, "1", "1"),
              logger,
              revoke,
              gate,
              Duration.ofMillis(100));
      Object[] required = {
        client,
        sender,
        clock,
        (java.util.function.Supplier<UUID>) UUID::randomUUID,
        audit,
        database,
        new LargeResultReader(transfer, identity(root.resolve("transfer"))),
        new MediaRangeService(new DescriptorFileResolver(assets, identity)),
        new WebMediaAudit(System.getLogger("pgpt.graph.media"), clock, "1", "1"),
        logger,
        revoke,
        gate
      };
      for (int index = 0; index < required.length; index++) {
        Object original = required[index];
        required[index] = null;
        assertThrows(NullPointerException.class, () -> construct(required));
        required[index] = original;
      }
      assertThrows(NullPointerException.class, () -> construct(required, null));
      var defaults = construct(required);
      for (Duration bad :
          new Duration[] {Duration.ofMillis(100).minusNanos(1), Duration.ofSeconds(2).plusNanos(1)})
        assertThrows(IllegalArgumentException.class, () -> construct(required, bad));
      assertEquals(
          Duration.ofMillis(100),
          WebNativeRuntime.replyTimeout(
              WebNonSecretConfig.parse("", "nk.web.mq.reply-timeout: 100ms")));
      assertEquals(
          Duration.ofSeconds(2), WebNativeRuntime.replyTimeout(WebNonSecretConfig.parse("", "")));
      assertThrows(NullPointerException.class, () -> WebNativeRuntime.replyTimeout(null));
      var application =
          new WebApplication(
              database,
              contexts,
              session,
              clock,
              new MqAuthenticationProvider(
                  new MqLoginClient(client, sender, clock, UUID::randomUUID, Duration.ofSeconds(2)),
                  new MqLoginContextProbe(
                      client, sender, clock, UUID::randomUUID, Duration.ofSeconds(2))),
              audit,
              UUID::randomUUID);
      try (var server =
          application.startWithCoreSessionDependencies(
              root,
              0,
              (core, spring) -> {
                var ports = assembly.dependencies(core, spring);
                var defaultPorts = defaults.dependencies(core, spring);
                assertEquals(17, defaultPorts.size());
                assertEquals(17, ports.size());
                assertSame(gate, ports.get(WebHttpAdmission.class));
                assertSame(logger, ports.get(WebRequestLogProducer.class));
                // Read actual configured client state; expected duration is a handwritten constant.
                for (Class<?> type :
                    List.of(
                        LogSearchWireClient.class,
                        ScenarioWireClient.class,
                        AnimationWireClient.class,
                        MusicWireClient.class,
                        UserAdministrationWireClient.class,
                        NotificationWireClient.class,
                        QuestionWireClient.class,
                        MediaDescriptorWireClient.class)) {
                  try {
                    var wrapped = type.getDeclaredField("client");
                    wrapped.setAccessible(true);
                    Object actual = wrapped.get(ports.get(type));
                    var field = actual.getClass().getDeclaredField("timeout");
                    field.setAccessible(true);
                    assertEquals(Duration.ofMillis(100), field.get(actual));
                    Object defaultActual = wrapped.get(defaultPorts.get(type));
                    assertEquals(Duration.ofSeconds(2), field.get(defaultActual));
                  } catch (ReflectiveOperationException brokenFixture) {
                    throw new AssertionError(brokenFixture);
                  }
                }
                assertThrows(NullPointerException.class, () -> assembly.dependencies(null, spring));
                assertThrows(NullPointerException.class, () -> assembly.dependencies(core, null));
                return ports;
              },
              WebBusinessAssembly.configurations())) {
        assertEquals(ROUTES, server.mappedPaths());
        String base = "http://127.0.0.1:" + server.port();
        assertEquals(503, get(http, base + "/login").statusCode());
        gate.admit();
        var login = get(http, base + "/login");
        assertEquals(200, login.statusCode());
        assertEquals("schubert NK - ログイン", org.jsoup.Jsoup.parse(login.body()).title());
        assertFalse(org.jsoup.Jsoup.parse(login.body()).select("input[name=_csrf]").isEmpty());
        for (String path :
            List.of(
                "/questions",
                "/notifications",
                "/admin/users",
                "/scenarios",
                "/music",
                "/animation")) {
          var protectedPage = get(http, base + path);
          assertEquals(302, protectedPage.statusCode());
          assertTrue(
              protectedPage.headers().firstValue("Location").orElseThrow().endsWith("/login"));
        }
        gate.drain(Duration.ofSeconds(3));
      }
    } finally {
      broker.stop();
      db.stop();
    }
  }

  @SuppressWarnings("unchecked") // Fixture slots have fixed independently declared types above.
  private static WebBusinessAssembly construct(Object[] slots) {
    return new WebBusinessAssembly(
        (JmsRequestReplyClient) slots[0],
        (ArtemisRequestSender) slots[1],
        (Clock) slots[2],
        (java.util.function.Supplier<UUID>) slots[3],
        (WebSecurityAudit) slots[4],
        (DataSource) slots[5],
        (LargeResultReader) slots[6],
        (MediaRangeService) slots[7],
        (WebMediaAudit) slots[8],
        (WebRequestLogProducer) slots[9],
        (RevocationPayloadCodec) slots[10],
        (WebHttpAdmission) slots[11]);
  }

  @SuppressWarnings("unchecked") // Same fixed fixture slots; only timeout varies independently.
  private static WebBusinessAssembly construct(Object[] s, Duration timeout) {
    return new WebBusinessAssembly(
        (JmsRequestReplyClient) s[0],
        (ArtemisRequestSender) s[1],
        (Clock) s[2],
        (java.util.function.Supplier<UUID>) s[3],
        (WebSecurityAudit) s[4],
        (DataSource) s[5],
        (LargeResultReader) s[6],
        (MediaRangeService) s[7],
        (WebMediaAudit) s[8],
        (WebRequestLogProducer) s[9],
        (RevocationPayloadCodec) s[10],
        (WebHttpAdmission) s[11],
        timeout);
  }

  private static HttpResponse<String> get(HttpClient http, String uri) throws Exception {
    return http.send(
        HttpRequest.newBuilder(URI.create(uri))
            .header("X-Forwarded-For", "203.0.113.1")
            .header("X-Forwarded-Proto", "https")
            .timeout(Duration.ofSeconds(3))
            .build(),
        HttpResponse.BodyHandlers.ofString());
  }

  private OwnedTransferDirectory directory(String name) throws Exception {
    var path = Files.createDirectory(root.resolve(name));
    Files.setPosixFilePermissions(path, PosixFilePermissions.fromString("rwxr-x---"));
    return OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), path);
  }

  private static StorageIdentity identity(Path path) throws Exception {
    var attributes = Files.readAttributes(path, java.nio.file.attribute.PosixFileAttributes.class);
    return new StorageIdentity(attributes.owner().getName(), attributes.group().getName());
  }

  private static DataSource source(WebLogDatabaseFixture db) {
    return new DataSource() {
      @Override
      public Connection getConnection() throws SQLException {
        return db.web();
      }

      @Override
      public Connection getConnection(String user, String password) throws SQLException {
        throw new SQLException("not supported");
      }

      @Override
      public java.io.PrintWriter getLogWriter() {
        return null;
      }

      @Override
      public void setLogWriter(java.io.PrintWriter writer) {}

      @Override
      public void setLoginTimeout(int seconds) {}

      @Override
      public int getLoginTimeout() {
        return 0;
      }

      @Override
      public java.util.logging.Logger getParentLogger() {
        return java.util.logging.Logger.getGlobal();
      }

      @Override
      public <T> T unwrap(Class<T> type) throws SQLException {
        throw new SQLException("not supported");
      }

      @Override
      public boolean isWrapperFor(Class<?> type) {
        return false;
      }
    };
  }

  private static EmbeddedActiveMQ broker(Path path) throws Exception {
    Configuration config;
    try (InputStream input = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      config = new FileConfigurationParser().parseMainConfig(input);
    }
    config
        .setPagingDirectory(path.resolve("paging").toString())
        .setBindingsDirectory(path.resolve("bindings").toString())
        .setJournalDirectory(path.resolve("journal").toString())
        .setLargeMessagesDirectory(path.resolve("large").toString())
        .setSecurityEnabled(false)
        .clearAcceptorConfigurations()
        .addAcceptorConfiguration("component", "vm://0");
    return new EmbeddedActiveMQ().setConfiguration(config).start();
  }
}
