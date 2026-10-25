package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
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

/** PG241/PT-OPS-MQ-016..018; independent SS321 role table and live authenticated broker. */
@SuppressWarnings("try") // EmbeddedActiveMQ.stop declares Exception; fixture owns it.
final class ArtemisRoleReadinessClientTest {
  // Independent PT oracle copied from SS321 §10 and the approved management-namespace delta.
  private static final String[] PERMISSIONS = {
    "send",
    "consume",
    "createDurableQueue",
    "deleteDurableQueue",
    "createNonDurableQueue",
    "deleteNonDurableQueue",
    "manage",
    "browse",
    "createAddress",
    "deleteAddress",
    "view",
    "edit"
  };
  private static final Map<String, Map<String, Set<String>>> TABLE = table();

  @TempDir Path root;

  @Test
  void opsMq1413002CorrectRoleCountWithNonObjectMembersIsRejected() {
    // SS321 independent role table: correct cardinality must not mask an invalid projection.
    String match = "nk.sync.request";
    int required = TABLE.get(match).size();
    assertEquals(3, required);
    for (String member : new String[] {"null", "7", "true", "\"role\"", "[]"}) {
      var changed = copy(golden());
      changed.put(
          match, "[" + String.join(",", java.util.Collections.nCopies(required, member)) + "]");
      assertRedacted(() -> candidate(changed).verify(unusedSession()));
    }
  }

  @Test
  void opsMq016LiveEffectiveSevenRoleMatchesAndApplicationDenial() throws Exception {
    try (var fixture = securedBroker()) {
      var reader = new ArtemisRoleReadinessClient();
      assertDoesNotThrow(() -> reader.verify(fixture.session));
      assertFalse(fixture.session.isClosed());
      for (String match : TABLE.keySet()) {
        assertInstanceOf(
            String.class, ArtemisManagementReadinessClient.roles(fixture.session, match));
      }
      assertFalse(
          fixture.broker.getActiveMQServer().getPostOffice().getAddresses().stream()
              .anyMatch(address -> address.toString().startsWith("activemq.management.")));
      String appCredential = UUID.randomUUID().toString();
      fixture.security.addNewUser("pt_web", appCredential, "nk_web");
      try (var app =
          fixture.factory.createSession("pt_web", appCredential, false, true, true, false, 0)) {
        assertRedacted(() -> reader.verify(app));
        assertFalse(app.isClosed());
      }
    }
  }

  @Test
  void opsMq017RejectsEachPermissionDriftMissingExcessRoleAndMalformedProjection() {
    var canonical = golden();
    assertDoesNotThrow(() -> candidate(canonical).verify(unusedSession()));
    for (var entry : TABLE.entrySet()) {
      String match = entry.getKey();
      for (var role : entry.getValue().entrySet()) {
        for (String permission : PERMISSIONS) {
          var changed = copy(canonical);
          var modified = new LinkedHashMap<>(entry.getValue());
          var grants = new java.util.HashSet<>(role.getValue());
          if (!grants.add(permission)) grants.remove(permission);
          modified.put(role.getKey(), Set.copyOf(grants));
          changed.put(match, json(modified));
          assertRedacted(() -> candidate(changed).verify(unusedSession()));
        }
      }
      var missing = copy(canonical);
      missing.put(match, "[]");
      assertRedacted(() -> candidate(missing).verify(unusedSession()));
      var duplicate = copy(canonical);
      String first =
          json(
              Map.of(
                  entry.getValue().keySet().iterator().next(),
                  entry.getValue().values().iterator().next()));
      duplicate.put(match, first.substring(0, first.length() - 1) + "," + first.substring(1));
      assertRedacted(() -> candidate(duplicate).verify(unusedSession()));
    }
    String match = "nk.sync.request";
    for (String invalid :
        new String[] {
          "{}",
          "[null]",
          "[{\"name\":\"unknown\"}]",
          canonical.get(match).replace("\"name\":\"nk_web\"", "\"name\":\"unknown\""),
          canonical.get(match).replace("\"name\":\"nk_web\",", ""),
          canonical
              .get(match)
              .replace("\"name\":\"nk_web\",", "\"name\":\"nk_web\",\"unexpected\":true,"),
          canonical.get(match).replace("\"send\":true", "\"send\":1"),
          canonical.get(match).replace("\"send\":true", "\"send\":null")
        }) {
      var changed = copy(canonical);
      changed.put(match, invalid);
      assertRedacted(() -> candidate(changed).verify(unusedSession()));
    }
  }

  @Test
  void opsMq018NullMalformedProviderAndEncoderFailuresAreRedacted() {
    assertThrows(NullPointerException.class, () -> new ArtemisRoleReadinessClient(null));
    assertThrows(NullPointerException.class, () -> new ArtemisRoleReadinessClient().verify(null));
    for (Object invalid : new Object[] {"", "not-json", 7}) {
      assertRedacted(
          () ->
              new ArtemisRoleReadinessClient((session, match) -> invalid).verify(unusedSession()));
    }
    assertRedacted(
        () -> new ArtemisRoleReadinessClient((session, match) -> null).verify(unusedSession()));
    assertThrows(
        IllegalStateException.class,
        () ->
            new ArtemisRoleReadinessClient(
                    (session, match) -> {
                      throw new IllegalStateException("private-management-value");
                    })
                .verify(unusedSession()));
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
            ArtemisManagementReadinessClient.putRolesOperation(failingMessage, "nk.sync.request"));
  }

  private static Map<String, Map<String, Set<String>>> table() {
    var values = new LinkedHashMap<String, Map<String, Set<String>>>();
    values.put(
        "nk.sync.request",
        Map.of("nk_web", Set.of("send"), "nk_api", Set.of("consume"), "nk_ops", Set.of("browse")));
    values.put(
        "nk.sync.reply.web",
        Map.of("nk_web", Set.of("consume"), "nk_api", Set.of("send"), "nk_ops", Set.of("browse")));
    values.put(
        "nk.async.work",
        Map.of("nk_api", Set.of("send", "consume"), "nk_ops", Set.of("send", "browse")));
    values.put(
        "nk.web.log",
        Map.of("nk_web", Set.of("send"), "nk_api", Set.of("consume"), "nk_ops", Set.of("browse")));
    values.put(
        "nk.dead.letter",
        Map.of(
            "nk_web",
            Set.of("send"),
            "nk_api",
            Set.of("send"),
            "nk_ops",
            Set.of("consume", "browse", "manage")));
    values.put(
        "nk.expiry",
        Map.of(
            "nk_mq_maintenance",
            Set.of("consume", "browse"),
            "nk_ops",
            Set.of("consume", "browse", "manage")));
    values.put(
        "activemq.management.#",
        Map.of(
            "nk_ops",
            Set.of(
                "send",
                "consume",
                "manage",
                "createAddress",
                "deleteAddress",
                "createNonDurableQueue",
                "deleteNonDurableQueue"),
            "nk_mq_maintenance",
            Set.of(
                "send",
                "consume",
                "manage",
                "createAddress",
                "deleteAddress",
                "createNonDurableQueue",
                "deleteNonDurableQueue")));
    values.put("mops.#", Map.of("nk_ops", Set.of("manage", "view", "edit")));
    var view =
        Map.of("nk_ops", Set.of("manage", "view"), "nk_mq_maintenance", Set.of("manage", "view"));
    values.put("mops.queue.nk.expiry.q.countMessages", view);
    values.put("mops.queue.nk.expiry.q.getMessageCount", view);
    values.put("mops.queue.nk.expiry.q.getPersistentSize", view);
    values.put(
        "mops.queue.nk.expiry.q.removeMessages",
        Map.of("nk_ops", Set.of("manage", "edit"), "nk_mq_maintenance", Set.of("manage", "edit")));
    return Map.copyOf(values);
  }

  private static Map<String, String> golden() {
    var values = new HashMap<String, String>();
    TABLE.forEach((match, roles) -> values.put(match, json(roles)));
    return values;
  }

  private static String json(Map<String, Set<String>> roles) {
    var text = new StringBuilder("[");
    for (var entry : roles.entrySet()) {
      if (text.length() > 1) text.append(',');
      text.append("{\"name\":\"").append(entry.getKey()).append('"');
      for (String permission : PERMISSIONS) {
        text.append(",\"")
            .append(permission)
            .append("\":")
            .append(entry.getValue().contains(permission));
      }
      text.append('}');
    }
    return text.append(']').toString();
  }

  private static Map<String, String> copy(Map<String, String> source) {
    return new HashMap<>(source);
  }

  private static ArtemisRoleReadinessClient candidate(Map<String, String> responses) {
    return new ArtemisRoleReadinessClient((session, match) -> responses.get(match));
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
