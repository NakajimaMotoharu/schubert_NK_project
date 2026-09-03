package dev.codex.schubert.nk.api.messaging.config;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSRuntimeException;
import jakarta.jms.JMSSecurityException;
import jakarta.jms.JMSSecurityRuntimeException;
import jakarta.jms.Queue;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.apache.activemq.artemis.spi.core.security.ActiveMQBasicSecurityManager;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-JMS-002 actual credential/role ACL enforcement against the production topology. */
final class ArtemisSecurityTest {
  private static final Set<String> ADDRESSES =
      Set.of(
          "nk.sync.request",
          "nk.sync.reply.web",
          "nk.async.work",
          "nk.web.log",
          "nk.dead.letter",
          "nk.expiry");

  @Test
  @DisplayName("PT-JMS-002 actual broker permits only each role's send/consume/browse matrix")
  void actualBrokerEnforcesEveryRoleAddressAndOperationCombination(@TempDir Path root)
      throws Exception {
    Map<String, Set<String>> oracle = new LinkedHashMap<>();
    oracle.put(
        "nk_web",
        Set.of(
            permission(Operation.SEND, "nk.sync.request"),
            permission(Operation.CONSUME, "nk.sync.reply.web"),
            permission(Operation.SEND, "nk.web.log"),
            permission(Operation.SEND, "nk.dead.letter")));
    oracle.put(
        "nk_api",
        Set.of(
            permission(Operation.CONSUME, "nk.sync.request"),
            permission(Operation.SEND, "nk.sync.reply.web"),
            permission(Operation.SEND, "nk.async.work"),
            permission(Operation.CONSUME, "nk.async.work"),
            permission(Operation.CONSUME, "nk.web.log"),
            permission(Operation.SEND, "nk.dead.letter")));
    oracle.put(
        "nk_ops",
        Set.of(
            permission(Operation.BROWSE, "nk.sync.request"),
            permission(Operation.BROWSE, "nk.sync.reply.web"),
            permission(Operation.SEND, "nk.async.work"),
            permission(Operation.BROWSE, "nk.async.work"),
            permission(Operation.BROWSE, "nk.web.log"),
            permission(Operation.CONSUME, "nk.dead.letter"),
            permission(Operation.BROWSE, "nk.dead.letter"),
            permission(Operation.CONSUME, "nk.expiry"),
            permission(Operation.BROWSE, "nk.expiry")));
    oracle.put(
        "nk_mq_maintenance",
        Set.of(
            permission(Operation.CONSUME, "nk.expiry"),
            permission(Operation.BROWSE, "nk.expiry")));
    oracle.put("nk_unprivileged", Set.of());

    Map<String, String> ephemeralCredentials = new LinkedHashMap<>();
    oracle.keySet().forEach(
        role -> {
          String user = "pt_" + role;
          String credential = UUID.randomUUID().toString();
          ephemeralCredentials.put(user, credential);
        });

    Configuration configuration = isolatedProductionConfiguration(root);
    String bootstrapUser = "pt_nk_web";
    ActiveMQBasicSecurityManager securityManager =
        new ActiveMQBasicSecurityManager()
            .init(
                Map.of(
                    ActiveMQBasicSecurityManager.BOOTSTRAP_USER,
                    bootstrapUser,
                    ActiveMQBasicSecurityManager.BOOTSTRAP_PASSWORD,
                    ephemeralCredentials.get(bootstrapUser),
                    ActiveMQBasicSecurityManager.BOOTSTRAP_ROLE,
                    "nk_web"));
    EmbeddedActiveMQ broker =
        new EmbeddedActiveMQ()
            .setConfiguration(configuration)
            .setSecurityManager(securityManager)
            .start();
    for (String role : oracle.keySet()) {
      String user = "pt_" + role;
      if (!user.equals(bootstrapUser)) {
        securityManager.addNewUser(user, ephemeralCredentials.get(user), role);
      }
    }
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory("vm://0")) {
      oracle.forEach(
          (role, allowed) -> {
            String user = "pt_" + role;
            ADDRESSES.forEach(
                address -> {
                  for (Operation operation : Operation.values()) {
                    String permission = permission(operation, address);
                    ThrowingOperation actual =
                        () -> {
                          try (JMSContext context =
                              factory.createContext(
                                  user,
                                  ephemeralCredentials.get(user),
                                  JMSContext.SESSION_TRANSACTED)) {
                            exercise(context, address, operation);
                          }
                        };
                    if (allowed.contains(permission)) {
                      assertDoesNotThrow(actual::run);
                    } else {
                      assertSecurityDenied(actual, user + " must not have " + permission);
                    }
                  }
                });
          });

      String validUser = "pt_nk_web";
      assertThrows(
          JMSRuntimeException.class,
          () ->
              factory.createContext(
                  validUser, UUID.randomUUID().toString(), JMSContext.AUTO_ACKNOWLEDGE));
      assertThrows(
          JMSRuntimeException.class,
          () ->
              factory.createContext(
                  "pt_unknown", UUID.randomUUID().toString(), JMSContext.AUTO_ACKNOWLEDGE));
      assertThrows(
          JMSRuntimeException.class,
          () -> factory.createContext(JMSContext.AUTO_ACKNOWLEDGE));
    } finally {
      broker.stop();
      ephemeralCredentials.clear();
    }
  }

  private static void exercise(JMSContext context, String address, Operation operation)
      throws JMSException {
    Queue destination = new ActiveMQQueue(address + "::" + address + ".q");
    switch (operation) {
      case SEND -> {
        BytesMessage message = context.createBytesMessage();
        message.writeBytes(new byte[] {0x01});
        context
            .createProducer()
            .setDeliveryMode(DeliveryMode.PERSISTENT)
            .send(destination, message);
        context.commit();
      }
      case CONSUME -> context.createConsumer(destination).close();
      case BROWSE -> {
        try (var browser = context.createBrowser(destination)) {
          browser.getEnumeration().hasMoreElements();
        }
      }
    }
  }

  private static String permission(Operation operation, String address) {
    return operation + ":" + address;
  }

  private static void assertSecurityDenied(ThrowingOperation actual, String message) {
    Throwable denial = assertThrows(Throwable.class, actual::run, message);
    assertTrue(
        denial instanceof JMSSecurityException || denial instanceof JMSSecurityRuntimeException,
        () -> message + "; actual exception was " + denial.getClass().getName());
  }

  private static Configuration isolatedProductionConfiguration(Path root) throws Exception {
    Path template = Path.of(System.getProperty("broker.template"));
    Configuration configuration;
    try (InputStream input = Files.newInputStream(template)) {
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
    return configuration;
  }

  private enum Operation {
    SEND,
    CONSUME,
    BROWSE
  }

  @FunctionalInterface
  private interface ThrowingOperation {
    void run() throws Exception;
  }
}
