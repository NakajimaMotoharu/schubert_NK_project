package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;
import org.apache.activemq.artemis.api.core.JsonUtil;
import org.apache.activemq.artemis.api.core.client.ActiveMQClient;
import org.apache.activemq.artemis.api.core.client.ClientMessage;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.json.JsonObject;
import org.apache.activemq.artemis.json.JsonValue;
import org.apache.activemq.artemis.spi.core.security.ActiveMQBasicSecurityManager;
import org.apache.activemq.artemis.utils.JsonLoader;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PG237/PT-OPS-MQ-010..012; live broker and independent SS321 literal mutation oracle. */
@SuppressWarnings("try") // EmbeddedActiveMQ.stop declares Exception; the fixture is caller-owned.
final class ArtemisAddressSettingsReadinessClientTest {
  @TempDir Path root;

  @Test
  void opsMq010ReadsSixEffectiveSettingsWithOpsRole() throws Exception {
    try (var fixture = securedBroker()) {
      assertDoesNotThrow(() -> new ArtemisAddressSettingsReadinessClient().verify(fixture.session));
      assertFalse(fixture.session.isClosed());
      assertFalse(
          fixture.broker.getActiveMQServer().getPostOffice().getAddresses().stream()
              .anyMatch(address -> address.toString().startsWith("activemq.management.")));
      Map<String, long[]> expected = new LinkedHashMap<>();
      expected.put("nk.sync.request", new long[] {32, 50, 224, 450});
      expected.put("nk.sync.reply.web", new long[] {32, 50, 224, 450});
      expected.put("nk.async.work", new long[] {128, 1_000, 896, 9_000});
      expected.put("nk.web.log", new long[] {64, 1_000, 192, 9_000});
      expected.put("nk.dead.letter", new long[] {128, 1_000, 1_920, 9_000});
      expected.put("nk.expiry", new long[] {64, 1_000, 960, 9_000});
      Map<String, String> common =
          Map.ofEntries(
              Map.entry("deadLetterAddress", "\"nk.dead.letter\""),
              Map.entry("expiryAddress", "\"nk.expiry\""),
              Map.entry("autoCreateDeadLetterResources", "false"),
              Map.entry("autoCreateExpiryResources", "false"),
              Map.entry("autoCreateAddresses", "false"),
              Map.entry("autoCreateQueues", "false"),
              Map.entry("autoDeleteAddresses", "false"),
              Map.entry("autoDeleteQueues", "false"),
              Map.entry("autoDeleteCreatedQueues", "false"),
              Map.entry("addressFullMessagePolicy", "\"PAGE\""),
              Map.entry("pageFullMessagePolicy", "\"FAIL\""),
              Map.entry("diskFullMessagePolicy", "\"BLOCK\""),
              Map.entry("pageSizeBytes", "8388608"),
              Map.entry("maxReadPageBytes", "16777216"),
              Map.entry("maxReadPageMessages", "100"),
              Map.entry("redeliveryCollisionAvoidanceFactor", "0.0"),
              Map.entry("redeliveryDelay", "1000"),
              Map.entry("redeliveryMultiplier", "5.0"),
              Map.entry("maxRedeliveryDelay", "30000"),
              Map.entry("maxDeliveryAttempts", "4"),
              Map.entry("enableMetrics", "true"),
              Map.entry("enableIngressTimestamp", "true"));
      assertEquals(6, expected.size());
      for (var entry : expected.entrySet()) {
        var actual =
            JsonUtil.readJsonObject(
                (String)
                    ArtemisManagementReadinessClient.addressSettings(
                        fixture.session, entry.getKey()));
        long[] capacity = entry.getValue();
        assertEquals(
            capacity[0] * 1024 * 1024, actual.getJsonNumber("maxSizeBytes").longValueExact());
        assertEquals(capacity[1], actual.getJsonNumber("maxSizeMessages").longValueExact());
        assertEquals(
            capacity[2] * 1024 * 1024, actual.getJsonNumber("pageLimitBytes").longValueExact());
        assertEquals(capacity[3], actual.getJsonNumber("pageLimitMessages").longValueExact());
        assertEquals("PAGE", actual.getString("addressFullMessagePolicy"));
        assertEquals("FAIL", actual.getString("pageFullMessagePolicy"));
        assertEquals("BLOCK", actual.getString("diskFullMessagePolicy"));
        assertEquals("nk.dead.letter", actual.getString("deadLetterAddress"));
        assertEquals("nk.expiry", actual.getString("expiryAddress"));
        common.forEach((key, literal) -> assertEquals(literal, actual.get(key).toString(), key));
      }
    }
  }

  @Test
  void opsMq011RejectsEveryCommonAndCapacityDriftAndMissingValues() throws Exception {
    try (var fixture = securedBroker()) {
      String source = source(fixture, "nk.sync.request");
      var parsed = JsonUtil.readJsonObject(source);
      var fields =
          new String[] {
            "deadLetterAddress",
            "expiryAddress",
            "autoCreateDeadLetterResources",
            "autoCreateExpiryResources",
            "autoCreateAddresses",
            "autoCreateQueues",
            "autoDeleteAddresses",
            "autoDeleteQueues",
            "autoDeleteCreatedQueues",
            "addressFullMessagePolicy",
            "pageFullMessagePolicy",
            "diskFullMessagePolicy",
            "pageSizeBytes",
            "maxReadPageBytes",
            "maxReadPageMessages",
            "redeliveryCollisionAvoidanceFactor",
            "redeliveryDelay",
            "redeliveryMultiplier",
            "maxRedeliveryDelay",
            "maxDeliveryAttempts",
            "enableMetrics",
            "enableIngressTimestamp",
            "maxSizeBytes",
            "maxSizeMessages",
            "pageLimitBytes",
            "pageLimitMessages"
          };
      for (String field : fields) {
        assertNotNull(parsed.get(field), field);
        String changed = changed(parsed, field, JsonValue.NULL, false);
        assertRedacted(
            () ->
                new ArtemisAddressSettingsReadinessClient(
                        (session, address) ->
                            address.equals("nk.sync.request") ? changed : source(fixture, address))
                    .verify(fixture.session));
      }
      var wrongNumber = JsonUtil.readJsonObject("{\"value\":1}").get("value");
      for (String address :
          new String[] {
            "nk.sync.reply.web", "nk.async.work", "nk.web.log", "nk.dead.letter", "nk.expiry"
          }) {
        var current = JsonUtil.readJsonObject(source(fixture, address));
        for (String field :
            new String[] {
              "maxSizeBytes", "maxSizeMessages", "pageLimitBytes", "pageLimitMessages"
            }) {
          String changed = changed(current, field, wrongNumber, false);
          assertRedacted(
              () ->
                  new ArtemisAddressSettingsReadinessClient(
                          (session, candidate) ->
                              candidate.equals(address) ? changed : source(fixture, candidate))
                      .verify(fixture.session));
        }
      }
      String missing = changed(parsed, "maxSizeBytes", JsonValue.NULL, true);
      assertRedacted(
          () ->
              new ArtemisAddressSettingsReadinessClient(
                      (session, address) ->
                          address.equals("nk.sync.request") ? missing : source(fixture, address))
                  .verify(fixture.session));
      assertFalse(fixture.session.isClosed());
    }
  }

  @Test
  void opsMq012RejectsNullMalformedUnknownAndProviderFailures() throws Exception {
    assertThrows(NullPointerException.class, () -> new ArtemisAddressSettingsReadinessClient(null));
    assertThrows(
        NullPointerException.class, () -> new ArtemisAddressSettingsReadinessClient().verify(null));
    try (var fixture = securedBroker()) {
      for (Object invalid : new Object[] {"", "not-json", 7}) {
        assertRedacted(
            () ->
                new ArtemisAddressSettingsReadinessClient((session, address) -> invalid)
                    .verify(fixture.session));
      }
      assertRedacted(
          () ->
              new ArtemisAddressSettingsReadinessClient((session, address) -> null)
                  .verify(fixture.session));
      assertThrows(
          IllegalStateException.class,
          () ->
              new ArtemisAddressSettingsReadinessClient(
                      (session, address) -> {
                        throw new IllegalStateException("private-management-value");
                      })
                  .verify(fixture.session));
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
          () ->
              ArtemisManagementReadinessClient.putAddressSettingsOperation(
                  failingMessage, "nk.sync.request"));
      // Artemis repository resolves unknown names through a default match. The full six-value
      // verifier must reject that fallback; the raw management operation is not an existence test.
      Object fallback =
          ArtemisManagementReadinessClient.addressSettings(fixture.session, "unknown");
      assertInstanceOf(String.class, fallback);
      assertRedacted(
          () ->
              new ArtemisAddressSettingsReadinessClient((session, address) -> fallback)
                  .verify(fixture.session));
      assertFalse(fixture.session.isClosed());
    }
  }

  private static String changed(
      JsonObject source, String field, JsonValue replacement, boolean omit) {
    var builder = JsonLoader.createObjectBuilder();
    source.forEach(
        (key, value) -> {
          if (!key.equals(field)) builder.add(key, value);
        });
    if (!omit) builder.add(field, replacement);
    return builder.build().toString();
  }

  private static String source(Fixture fixture, String address) {
    return fixture
        .broker
        .getActiveMQServer()
        .getAddressSettingsRepository()
        .getMatch(address)
        .toJSON();
  }

  private Fixture securedBroker() throws Exception {
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
        .addAcceptorConfiguration("component", "vm://0");
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
      var locator = ActiveMQClient.createServerLocator("vm://0");
      try {
        var factory = locator.createSessionFactory();
        try {
          var session = factory.createSession("pt_ops", credential, false, true, true, false, 0);
          return new Fixture(broker, locator, factory, session);
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
