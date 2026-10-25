package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.InputStream;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import org.apache.activemq.artemis.api.core.ActiveMQSecurityException;
import org.apache.activemq.artemis.api.core.QueueConfiguration;
import org.apache.activemq.artemis.api.core.SimpleString;
import org.apache.activemq.artemis.api.core.client.ActiveMQClient;
import org.apache.activemq.artemis.api.core.client.ClientConsumer;
import org.apache.activemq.artemis.api.core.client.ClientMessage;
import org.apache.activemq.artemis.api.core.client.ClientProducer;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.spi.core.security.ActiveMQBasicSecurityManager;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PG235/PT-OPS-MQ-005..007; independent SS321 literals and real read-only Core management. */
final class ArtemisManagementReadinessClientTest {
  @TempDir Path root;

  @Test
  void opsMq005ReadsActualBrokerWithoutChangingOrClosingBorrowedSession() throws Exception {
    var broker = start(root);
    try (var locator = ActiveMQClient.createServerLocator("vm://0");
        var factory = locator.createSessionFactory();
        var session = factory.createSession()) {
      assertDoesNotThrow(() -> new ArtemisManagementReadinessClient().verifyBroker(session));
      assertFalse(session.isClosed());
      assertThrows(
          ArtemisManagementReadinessException.class,
          () -> ArtemisManagementReadinessClient.read(session, "noSuchAttribute"));
      assertFalse(session.isClosed());
    } finally {
      broker.stop();
    }
  }

  @Test
  void opsMq008ProductionOpsRoleCanReadEffectiveManagementValues() throws Exception {
    var location = Files.createDirectory(root.resolve("secured"));
    Configuration config;
    try (InputStream input = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      config = new FileConfigurationParser().parseMainConfig(input);
    }
    config
        .setPagingDirectory(location.resolve("paging").toString())
        .setBindingsDirectory(location.resolve("bindings").toString())
        .setJournalDirectory(location.resolve("journal").toString())
        .setLargeMessagesDirectory(location.resolve("large-messages").toString())
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
        new EmbeddedActiveMQ().setConfiguration(config).setSecurityManager(security).start();
    String applicationCredential = UUID.randomUUID().toString();
    security.addNewUser("pt_api", applicationCredential, "nk_api");
    try (var locator = ActiveMQClient.createServerLocator("vm://0");
        var factory = locator.createSessionFactory();
        var session = factory.createSession("pt_ops", credential, false, true, true, false, 0)) {
      var reply = SimpleString.of("activemq.management.ptprobe");
      assertDoesNotThrow(
          () ->
              session.createQueue(
                  QueueConfiguration.of(reply).setDurable(false).setTemporary(true)));
      session.deleteQueue(reply);
      assertFalse(
          broker.getActiveMQServer().getPostOffice().getAddresses().stream()
              .anyMatch(address -> address.toString().startsWith("activemq.management.")));
      assertDoesNotThrow(() -> new ArtemisManagementReadinessClient().verifyBroker(session));
      assertFalse(session.isClosed());
      assertFalse(
          broker.getActiveMQServer().getPostOffice().getAddresses().stream()
              .anyMatch(address -> address.toString().startsWith("activemq.management.")));
      try (var application =
          factory.createSession("pt_api", applicationCredential, false, true, true, false, 0)) {
        assertThrows(
            ActiveMQSecurityException.class,
            () ->
                application.createQueue(
                    QueueConfiguration.of(reply).setDurable(false).setTemporary(true)));
        assertRedacted(() -> new ArtemisManagementReadinessClient().verifyBroker(application));
      }
    } finally {
      broker.stop();
    }
  }

  @Test
  void opsMq006EveryApprovedValueIsCheckedAndDiskBoundaryIsStrict() {
    var expected = expected();
    var session = unusedSession();
    var client = new ArtemisManagementReadinessClient((ignored, name) -> expected.get(name));
    assertDoesNotThrow(() -> client.verifyBroker(session));
    Map<String, Object> wrong =
        Map.ofEntries(
            Map.entry("name", "other"),
            Map.entry("persistenceEnabled", false),
            Map.entry("journalType", "ASYNCIO"),
            Map.entry("journalFileSize", 1L),
            Map.entry("journalMinFiles", 3),
            Map.entry("journalPoolFiles", 19),
            Map.entry("globalMaxSize", 0L),
            Map.entry("IDCacheSize", 1),
            Map.entry("persistIDCache", false),
            Map.entry("maxDiskUsage", 91),
            Map.entry("diskStoreUsage", 0.9));
    for (var entry : wrong.entrySet()) {
      var observed = new LinkedHashMap<>(expected);
      observed.put(entry.getKey(), entry.getValue());
      assertRedacted(
          () ->
              new ArtemisManagementReadinessClient((ignored, key) -> observed.get(key))
                  .verifyBroker(session));
    }
    for (Object invalid : new Object[] {-0.01, 0.9, Double.NaN, Double.POSITIVE_INFINITY, "0.5"}) {
      var observed = new LinkedHashMap<>(expected);
      observed.put("diskStoreUsage", invalid);
      assertRedacted(
          () ->
              new ArtemisManagementReadinessClient((ignored, key) -> observed.get(key))
                  .verifyBroker(session));
    }
    expected.put("diskStoreUsage", 0.899999);
    assertDoesNotThrow(() -> client.verifyBroker(session));
  }

  @Test
  void opsMq007NullMalformedAndProviderFailureAreRedactedWithoutSessionOwnership() {
    assertThrows(NullPointerException.class, () -> new ArtemisManagementReadinessClient(null));
    assertThrows(
        NullPointerException.class,
        () -> new ArtemisManagementReadinessClient().verifyBroker(null));
    var session = unusedSession();
    var observed = expected();
    observed.put("journalMinFiles", null);
    assertRedacted(
        () ->
            new ArtemisManagementReadinessClient((ignored, key) -> observed.get(key))
                .verifyBroker(session));
    observed.put("journalMinFiles", 4.5);
    assertRedacted(
        () ->
            new ArtemisManagementReadinessClient((ignored, key) -> observed.get(key))
                .verifyBroker(session));
    observed.put("journalMinFiles", 4);
    observed.put("diskStoreUsage", null);
    assertRedacted(
        () ->
            new ArtemisManagementReadinessClient((ignored, key) -> observed.get(key))
                .verifyBroker(session));
    var calls = new AtomicInteger();
    assertThrows(
        IllegalStateException.class,
        () ->
            new ArtemisManagementReadinessClient(
                    (ignored, key) -> {
                      calls.incrementAndGet();
                      throw new IllegalStateException("private-broker-password");
                    })
                .verifyBroker(session));
    assertEquals(1, calls.get());
  }

  @Test
  void opsMq009MissingManagementReplyIsBoundedAndInterruptIsRestored() {
    var timeout = new AtomicLong(-1);
    var closes = new AtomicInteger();
    var deletes = new AtomicInteger();
    var session = noReplySession(timeout, closes, deletes, false);
    assertRedacted(() -> ArtemisManagementReadinessClient.read(session, "name"));
    assertEquals(2_000L, timeout.get());
    assertEquals(2, closes.get());
    assertEquals(1, deletes.get());
    assertFalse(Thread.currentThread().isInterrupted());

    var closeFault =
        noReplySession(new AtomicLong(), new AtomicInteger(), new AtomicInteger(), true);
    assertRedacted(() -> ArtemisManagementReadinessClient.read(closeFault, "name"));

    assertRedacted(
        () ->
            ArtemisManagementReadinessClient.read(
                session,
                "name",
                (ignored, attribute) -> {
                  throw new InterruptedException();
                }));
    assertTrue(Thread.interrupted());
  }

  private static ClientSession noReplySession(
      AtomicLong timeout, AtomicInteger closes, AtomicInteger deletes, boolean failDelete) {
    return proxy(
        ClientSession.class,
        (instance, method, args) ->
            switch (method.getName()) {
              case "start" -> instance;
              case "createProducer" ->
                  proxy(
                      ClientProducer.class,
                      (producer, operation, ignored) -> {
                        if (operation.getName().equals("send")) return null;
                        if (operation.getName().equals("close")) {
                          closes.incrementAndGet();
                          return null;
                        }
                        throw new AssertionError(operation.getName());
                      });
              case "createConsumer" ->
                  proxy(
                      ClientConsumer.class,
                      (consumer, operation, input) -> {
                        if (operation.getName().equals("receive")) {
                          timeout.set((Long) input[0]);
                          return null;
                        }
                        if (operation.getName().equals("close")) {
                          closes.incrementAndGet();
                          return null;
                        }
                        throw new AssertionError(operation.getName());
                      });
              case "createMessage" ->
                  proxy(
                      ClientMessage.class,
                      (message, operation, ignored) -> {
                        if (operation.getName().equals("putStringProperty")) return message;
                        throw new AssertionError(operation.getName());
                      });
              case "createQueue" -> null;
              case "deleteQueue" -> {
                deletes.incrementAndGet();
                if (failDelete) throw new IllegalStateException("private-close-failure");
                yield null;
              }
              default -> throw new AssertionError(method.getName());
            });
  }

  @SuppressWarnings("unchecked")
  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return (T) Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler);
  }

  private static void assertRedacted(org.junit.jupiter.api.function.Executable action) {
    var failure = assertThrows(ArtemisManagementReadinessException.class, action);
    assertEquals("Artemis effective broker configuration is unavailable", failure.getMessage());
    assertNull(failure.getCause());
  }

  private static Map<String, Object> expected() {
    var values = new LinkedHashMap<String, Object>();
    values.put("name", "schubert-nk-broker");
    values.put("persistenceEnabled", true);
    values.put("journalType", "NIO");
    values.put("journalFileSize", 10 * 1024 * 1024);
    values.put("journalMinFiles", 4);
    values.put("journalPoolFiles", 20);
    values.put("globalMaxSize", 512L * 1024 * 1024);
    values.put("IDCacheSize", 20_000);
    values.put("persistIDCache", true);
    values.put("maxDiskUsage", 90);
    values.put("diskStoreUsage", 0.2);
    return values;
  }

  private static ClientSession unusedSession() {
    return (ClientSession)
        Proxy.newProxyInstance(
            ClientSession.class.getClassLoader(),
            new Class<?>[] {ClientSession.class},
            (proxy, method, args) -> {
              throw new AssertionError("borrowed session operation: " + method.getName());
            });
  }

  private static EmbeddedActiveMQ start(Path root) throws Exception {
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
}
