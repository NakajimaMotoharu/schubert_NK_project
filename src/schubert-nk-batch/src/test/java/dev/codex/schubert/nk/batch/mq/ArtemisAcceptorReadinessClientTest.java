package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.UUID;
import org.apache.activemq.artemis.api.core.client.ActiveMQClient;
import org.apache.activemq.artemis.api.core.client.ClientMessage;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.spi.core.security.ActiveMQBasicSecurityManager;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PG240/PT-OPS-MQ-013..015; independent SS321 loopback/CORE literals and real Ops broker. */
@SuppressWarnings("try") // EmbeddedActiveMQ.stop declares Exception; fixture owns it.
final class ArtemisAcceptorReadinessClientTest {
  private static final String GOOD_JSON =
      "[{\"name\":\"core\",\"factoryClassName\":\"org.apache.activemq.artemis.core.remoting.impl.netty.NettyAcceptorFactory\",\"params\":{\"scheme\":\"tcp\",\"port\":\"61616\",\"host\":\"127.0.0.1\",\"protocols\":\"CORE\"},\"extraProps\":{}}]";
  @TempDir Path root;

  @Test
  void opsMq013RealLoopbackCoreAcceptorAndOpsOnlyManagement() throws Exception {
    try (var fixture = securedTcpBroker()) {
      assertDoesNotThrow(() -> new ArtemisAcceptorReadinessClient().verify(fixture.session));
      var detailed = new ArtemisStartupObservation().inspectEvidence(fixture.session);
      assertEquals(
          Map.of(
              "name",
              "core",
              "factoryClassName",
              "org.apache.activemq.artemis.core.remoting.impl.netty.NettyAcceptorFactory",
              "scheme",
              "tcp",
              "host",
              "127.0.0.1",
              "port",
              "61616",
              "protocols",
              "CORE",
              "started",
              "1"),
          detailed.acceptor());
      assertEquals("schubert-nk-broker", detailed.broker().get("name"));
      assertEquals("NIO", detailed.broker().get("journalType"));
      assertEquals("10485760", detailed.broker().get("journalFileSize"));
      assertEquals("536870912", detailed.broker().get("globalMaxSize"));
      assertEquals(11, detailed.broker().size());
      var addresses =
          java.util.Set.of(
              "nk.sync.request",
              "nk.sync.reply.web",
              "nk.async.work",
              "nk.web.log",
              "nk.dead.letter",
              "nk.expiry");
      assertEquals(addresses, detailed.topology().keySet());
      assertEquals(addresses, detailed.settings().keySet());
      assertEquals(addresses, detailed.pressure().keySet());
      for (String address : addresses) {
        assertEquals(address + ".q", detailed.topology().get(address).get("queue_names"));
        assertEquals("ANYCAST", detailed.topology().get(address).get("routing_type"));
        assertEquals("1", detailed.topology().get(address).get("durable"));
        assertEquals(26, detailed.settings().get(address).size());
        assertEquals(
            "\"nk.dead.letter\"", detailed.settings().get(address).get("deadLetterAddress"));
        assertEquals(
            new ArtemisQueuePressureClient.Value(0, 0, ArtemisQueuePressureClient.Pressure.NORMAL),
            detailed.pressure().get(address));
      }
      assertEquals(12, detailed.roles().size());
      assertEquals(Boolean.TRUE, detailed.roles().get("nk.sync.request").get("nk_web").get("send"));
      assertEquals(
          Boolean.FALSE, detailed.roles().get("nk.sync.request").get("nk_web").get("consume"));
      assertEquals(12, detailed.roles().get("nk.sync.request").get("nk_web").size());
      assertThrows(UnsupportedOperationException.class, () -> detailed.broker().clear());
      assertThrows(
          UnsupportedOperationException.class, () -> detailed.settings().get("nk.expiry").clear());
      assertThrows(
          UnsupportedOperationException.class,
          () -> detailed.roles().get("nk.expiry").get("nk_ops").clear());
      assertEquals("ArtemisEvidence[observations=<redacted>]", detailed.toString());
      assertFalse(fixture.session.isClosed());
      assertEquals(GOOD_JSON, ArtemisManagementReadinessClient.acceptors(fixture.session));
      assertEquals(Boolean.TRUE, ArtemisManagementReadinessClient.acceptorStarted(fixture.session));
      assertFalse(
          fixture.broker.getActiveMQServer().getPostOffice().getAddresses().stream()
              .anyMatch(address -> address.toString().startsWith("activemq.management.")));
      String appCredential = UUID.randomUUID().toString();
      fixture.security.addNewUser("pt_api", appCredential, "nk_api");
      try (var application =
          fixture.factory.createSession("pt_api", appCredential, false, true, true, false, 0)) {
        assertRedacted(() -> new ArtemisAcceptorReadinessClient().verify(application));
        assertFalse(application.isClosed());
      }
    }
  }

  @Test
  void opsMq014RejectsEveryAcceptorFieldDriftAndExtraListener() {
    var session = unusedSession();
    assertDoesNotThrow(() -> candidate(GOOD_JSON, Boolean.TRUE).verify(session));
    for (String wrong :
        new String[] {
          GOOD_JSON.replace("\"name\":\"core\",", "\"name\":\"other\","),
          GOOD_JSON.replace("NettyAcceptorFactory", "InVMAcceptorFactory"),
          GOOD_JSON.replace("\"scheme\":\"tcp\"", "\"scheme\":\"udp\""),
          GOOD_JSON.replace("\"host\":\"127.0.0.1\"", "\"host\":\"0.0.0.0\""),
          GOOD_JSON.replace("\"host\":\"127.0.0.1\"", "\"host\":\"::\""),
          GOOD_JSON.replace("\"port\":\"61616\"", "\"port\":\"61617\""),
          GOOD_JSON.replace("\"protocols\":\"CORE\"", "\"protocols\":\"CORE,AMQP\""),
          GOOD_JSON.replace("\"extraProps\":{}", "\"extraProps\":{\"unknown\":\"x\"}"),
          GOOD_JSON.replace("\"name\":\"core\",", ""),
          GOOD_JSON.replace("\"name\":\"core\",", "\"name\":\"core\",\"unknown\":true,"),
          GOOD_JSON.replace("\"host\":\"127.0.0.1\",", ""),
          GOOD_JSON.replace("\"port\":\"61616\"", "\"port\":61616"),
          GOOD_JSON.substring(0, GOOD_JSON.length() - 1) + "," + GOOD_JSON.substring(1),
          "[]",
          "{}",
          "[null]"
        }) {
      assertRedacted(() -> candidate(wrong, Boolean.TRUE).verify(session));
    }
  }

  @Test
  void opsMq015NullMalformedStartedAndProviderFailuresAreRedacted() {
    var session = unusedSession();
    assertThrows(
        NullPointerException.class,
        () -> new ArtemisAcceptorReadinessClient(null, ignored -> true));
    assertThrows(
        NullPointerException.class,
        () -> new ArtemisAcceptorReadinessClient(ignored -> GOOD_JSON, null));
    assertThrows(
        NullPointerException.class, () -> new ArtemisAcceptorReadinessClient().verify(null));
    for (Object invalid : new Object[] {"", "not-json", 7}) {
      assertRedacted(() -> candidate(invalid, true).verify(session));
    }
    assertRedacted(() -> candidate(null, true).verify(session));
    assertRedacted(() -> candidate(GOOD_JSON, false).verify(session));
    assertRedacted(() -> candidate(GOOD_JSON, null).verify(session));
    assertThrows(
        IllegalStateException.class,
        () ->
            new ArtemisAcceptorReadinessClient(
                    ignored -> {
                      throw new IllegalStateException("private-management-value");
                    },
                    ignored -> true)
                .verify(session));
    assertThrows(
        IllegalStateException.class,
        () ->
            new ArtemisAcceptorReadinessClient(
                    ignored -> GOOD_JSON,
                    ignored -> {
                      throw new IllegalStateException("private-management-value");
                    })
                .verify(session));
    var failingMessage =
        (ClientMessage)
            Proxy.newProxyInstance(
                ClientMessage.class.getClassLoader(),
                new Class<?>[] {ClientMessage.class},
                (proxy, method, arguments) -> {
                  throw new IllegalStateException("private-management-value");
                });
    assertThrows(
        IllegalStateException.class,
        () -> ArtemisManagementReadinessClient.putAcceptorsOperation(failingMessage));
  }

  private static ArtemisAcceptorReadinessClient candidate(Object json, Object started) {
    return new ArtemisAcceptorReadinessClient(ignored -> json, ignored -> started);
  }

  private static ClientSession unusedSession() {
    return (ClientSession)
        Proxy.newProxyInstance(
            ClientSession.class.getClassLoader(),
            new Class<?>[] {ClientSession.class},
            (proxy, method, arguments) -> {
              throw new AssertionError("borrowed session must not be used by fixture reader");
            });
  }

  private Fixture securedTcpBroker() throws Exception {
    Configuration configuration;
    try (InputStream input = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      configuration = new FileConfigurationParser().parseMainConfig(input);
    }
    configuration
        .setPagingDirectory(root.resolve("paging").toString())
        .setBindingsDirectory(root.resolve("bindings").toString())
        .setJournalDirectory(root.resolve("journal").toString())
        .setLargeMessagesDirectory(root.resolve("large-messages").toString())
        .setSecurityEnabled(true)
        .clearAcceptorConfigurations()
        .addAcceptorConfiguration("core", "tcp://127.0.0.1:61616?protocols=CORE");
    String credential = UUID.randomUUID().toString();
    var security =
        new ActiveMQBasicSecurityManager()
            .init(
                Map.of(
                    ActiveMQBasicSecurityManager.BOOTSTRAP_USER,
                    "pt_ops",
                    ActiveMQBasicSecurityManager.BOOTSTRAP_PASSWORD,
                    credential,
                    ActiveMQBasicSecurityManager.BOOTSTRAP_ROLE,
                    "nk_ops"));
    var broker =
        new EmbeddedActiveMQ().setConfiguration(configuration).setSecurityManager(security).start();
    try {
      var locator = ActiveMQClient.createServerLocator("tcp://127.0.0.1:61616");
      try {
        var factory = locator.createSessionFactory();
        try {
          var session = factory.createSession("pt_ops", credential, false, true, true, false, 0);
          return new Fixture(broker, security, locator, factory, session);
        } catch (Exception failure) {
          factory.close();
          throw failure;
        }
      } catch (Exception failure) {
        locator.close();
        throw failure;
      }
    } catch (Exception failure) {
      broker.stop();
      throw failure;
    }
  }

  private static void assertRedacted(org.junit.jupiter.api.function.Executable operation) {
    var failure = assertThrows(ArtemisManagementReadinessException.class, operation);
    assertNull(failure.getCause());
    assertFalse(failure.getMessage().contains("private"));
    assertEquals(0, failure.getSuppressed().length);
  }

  private record Fixture(
      EmbeddedActiveMQ broker,
      ActiveMQBasicSecurityManager security,
      org.apache.activemq.artemis.api.core.client.ServerLocator locator,
      org.apache.activemq.artemis.api.core.client.ClientSessionFactory factory,
      ClientSession session)
      implements AutoCloseable {
    @Override
    public void close() throws Exception {
      session.close();
      factory.close();
      locator.close();
      broker.stop();
    }
  }
}
