package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import org.apache.activemq.artemis.api.core.client.ActiveMQClient;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.spi.core.security.ActiveMQBasicSecurityManager;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PG242/PT-OPS-MQ-019..021; real Ops metrics and independent SS321 capacity literals. */
@SuppressWarnings("try") // EmbeddedActiveMQ.stop declares Exception; fixture owns it.
final class ArtemisQueuePressureClientTest {
  private static final String FIXTURE_NK_SYNC_REQUEST_422EE207 = "nk.sync.request";
  private static final String FIXTURE_NK_DEAD_LETTER_6588D12C = "nk.dead.letter";
  private static final Set<String> ADDRESSES =
      Set.of(
          FIXTURE_NK_SYNC_REQUEST_422EE207,
          "nk.sync.reply.web",
          "nk.async.work",
          "nk.web.log",
          FIXTURE_NK_DEAD_LETTER_6588D12C,
          "nk.expiry");
  // Exact integer threshold literals from SS321 §5.2; none is obtained from production.
  private static final Map<String, long[]> BOUNDARIES =
      Map.of(
          FIXTURE_NK_SYNC_REQUEST_422EE207,
          new long[] {250, 450, 187_904_820, 241_591_911},
          "nk.sync.reply.web",
          new long[] {250, 450, 187_904_820, 241_591_911},
          "nk.async.work",
          new long[] {5_000, 9_000, 751_619_277, 966_367_642},
          "nk.web.log",
          new long[] {5_000, 9_000, 187_904_820, 241_591_911},
          "nk.expiry",
          new long[] {1_000, 5_000, 751_619_277, 966_367_642});

  @TempDir Path root;

  @Test
  void opsMq019LiveSixEmptyQueueMetricsAndApplicationDenial() throws Exception {
    try (var fixture = securedBroker()) {
      var result = new ArtemisQueuePressureClient().inspect(fixture.session);
      assertEquals(ADDRESSES, result.keySet());
      for (var state : result.values())
        assertEquals(ArtemisQueuePressureClient.Pressure.NORMAL, state);
      assertFalse(fixture.session.isClosed());
      assertFalse(
          fixture.broker.getActiveMQServer().getPostOffice().getAddresses().stream()
              .anyMatch(address -> address.toString().startsWith("activemq.management.")));
      String appCredential = UUID.randomUUID().toString();
      fixture.security.addNewUser("pt_api", appCredential, "nk_api");
      try (var app =
          fixture.factory.createSession("pt_api", appCredential, false, true, true, false, 0)) {
        assertRedacted(() -> new ArtemisQueuePressureClient().inspect(app));
        assertFalse(app.isClosed());
      }
    }
  }

  @Test
  void opsMq020EveryCountAndByteBoundaryIncludingDlqAlert() {
    var session = unusedSession();
    var baseline = zeroes();
    assertEquals(
        Set.of(ArtemisQueuePressureClient.Pressure.NORMAL),
        Set.copyOf(candidate(baseline).inspect(session).values()));
    for (var entry : BOUNDARIES.entrySet()) {
      String address = entry.getKey();
      long[] b = entry.getValue();
      assertState(address, b[0] - 1, 0, ArtemisQueuePressureClient.Pressure.NORMAL);
      assertState(address, b[0], 0, ArtemisQueuePressureClient.Pressure.WARNING);
      assertState(address, b[0] + 1, 0, ArtemisQueuePressureClient.Pressure.WARNING);
      assertState(address, b[1] - 1, 0, ArtemisQueuePressureClient.Pressure.WARNING);
      assertState(address, b[1], 0, ArtemisQueuePressureClient.Pressure.CRITICAL);
      assertState(address, b[1] + 1, 0, ArtemisQueuePressureClient.Pressure.CRITICAL);
      assertState(address, 0, b[2] - 1, ArtemisQueuePressureClient.Pressure.NORMAL);
      assertState(address, 0, b[2], ArtemisQueuePressureClient.Pressure.WARNING);
      assertState(address, 0, b[2] + 1, ArtemisQueuePressureClient.Pressure.WARNING);
      assertState(address, 0, b[3] - 1, ArtemisQueuePressureClient.Pressure.WARNING);
      assertState(address, 0, b[3], ArtemisQueuePressureClient.Pressure.CRITICAL);
      assertState(address, 0, b[3] + 1, ArtemisQueuePressureClient.Pressure.CRITICAL);
    }
    assertState(FIXTURE_NK_DEAD_LETTER_6588D12C, 0, 0, ArtemisQueuePressureClient.Pressure.NORMAL);
    assertState(FIXTURE_NK_DEAD_LETTER_6588D12C, 1, 0, ArtemisQueuePressureClient.Pressure.ALERT);
    assertState(
        FIXTURE_NK_DEAD_LETTER_6588D12C,
        10_000,
        1_503_238_553,
        ArtemisQueuePressureClient.Pressure.ALERT);
    assertState(
        FIXTURE_NK_DEAD_LETTER_6588D12C,
        0,
        1_503_238_554,
        ArtemisQueuePressureClient.Pressure.WARNING);
    assertState(
        FIXTURE_NK_DEAD_LETTER_6588D12C,
        1,
        1_503_238_554,
        ArtemisQueuePressureClient.Pressure.ALERT);
    assertState(
        FIXTURE_NK_DEAD_LETTER_6588D12C,
        0,
        1_932_735_283,
        ArtemisQueuePressureClient.Pressure.WARNING);
    assertState(
        FIXTURE_NK_DEAD_LETTER_6588D12C,
        1,
        1_932_735_284,
        ArtemisQueuePressureClient.Pressure.CRITICAL);
    assertState(
        FIXTURE_NK_SYNC_REQUEST_422EE207,
        250,
        241_591_911,
        ArtemisQueuePressureClient.Pressure.CRITICAL);
  }

  @Test
  void opsMq021NullInvalidMetricsAndProviderFaultAreRedacted() {
    assertThrows(NullPointerException.class, () -> new ArtemisQueuePressureClient(null));
    assertThrows(NullPointerException.class, () -> new ArtemisQueuePressureClient().inspect(null));
    var session = unusedSession();
    for (Object invalid : new Object[] {-1L, -1, 1.0, "1", true}) {
      assertRedacted(() -> new ArtemisQueuePressureClient((s, q, a) -> invalid).inspect(session));
    }
    assertRedacted(() -> new ArtemisQueuePressureClient((s, q, a) -> null).inspect(session));
    assertThrows(
        IllegalStateException.class,
        () ->
            new ArtemisQueuePressureClient(
                    (s, q, a) -> {
                      throw new IllegalStateException("private-management-value");
                    })
                .inspect(session));
    // Integer and Long are the two legal Core management integer projections.
    assertEquals(
        ArtemisQueuePressureClient.Pressure.NORMAL,
        new ArtemisQueuePressureClient((s, q, a) -> 0)
            .inspect(session)
            .get(FIXTURE_NK_SYNC_REQUEST_422EE207));
    var oneMissingByte =
        new ArtemisQueuePressureClient(
            (s, q, a) -> q.equals("nk.sync.request.q") && a.equals("persistentSize") ? null : 0L);
    assertRedacted(() -> oneMissingByte.inspect(session));
    var providerSession =
        (ClientSession)
            Proxy.newProxyInstance(
                ClientSession.class.getClassLoader(),
                new Class<?>[] {ClientSession.class},
                (proxy, method, arguments) -> {
                  throw new IllegalStateException("private-management-value");
                });
    assertThrows(
        IllegalStateException.class,
        () -> new ArtemisQueuePressureClient().inspect(providerSession));
  }

  private static void assertState(
      String address, long count, long bytes, ArtemisQueuePressureClient.Pressure expected) {
    var values = zeroes();
    values.put(address + ".q", new long[] {count, bytes});
    assertEquals(expected, candidate(values).inspect(unusedSession()).get(address), address);
  }

  private static ArtemisQueuePressureClient candidate(Map<String, long[]> values) {
    return new ArtemisQueuePressureClient(
        (session, queue, attribute) -> {
          long[] pair = values.get(queue);
          return attribute.equals("messageCount") ? pair[0] : pair[1];
        });
  }

  private static Map<String, long[]> zeroes() {
    var values = new HashMap<String, long[]>();
    for (String address : ADDRESSES) values.put(address + ".q", new long[] {0, 0});
    return values;
  }

  private static ClientSession unusedSession() {
    return (ClientSession)
        Proxy.newProxyInstance(
            ClientSession.class.getClassLoader(),
            new Class<?>[] {ClientSession.class},
            (proxy, method, arguments) -> {
              throw new AssertionError("fixture must not use borrowed session");
            });
  }

  private Fixture securedBroker() throws Exception {
    Configuration config;
    try (InputStream input = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      config = new FileConfigurationParser().parseMainConfig(input);
    }
    config
        .setPagingDirectory(root.resolve("paging").toString())
        .setBindingsDirectory(root.resolve("bindings").toString())
        .setJournalDirectory(root.resolve("journal").toString())
        .setLargeMessagesDirectory(root.resolve("large-messages").toString())
        .setSecurityEnabled(true)
        .clearAcceptorConfigurations()
        .addAcceptorConfiguration("component", "vm://0");
    String credential = UUID.randomUUID().toString();
    var security =
        new ActiveMQBasicSecurityManager()
            .init(
                Map.of(
                    ActiveMQBasicSecurityManager.BOOTSTRAP_USER, "pt_ops",
                    ActiveMQBasicSecurityManager.BOOTSTRAP_PASSWORD, credential,
                    ActiveMQBasicSecurityManager.BOOTSTRAP_ROLE, "nk_ops"));
    var broker =
        new EmbeddedActiveMQ().setConfiguration(config).setSecurityManager(security).start();
    try {
      var locator = ActiveMQClient.createServerLocator("vm://0");
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
