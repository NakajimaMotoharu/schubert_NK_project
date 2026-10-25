package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.UUID;
import org.apache.activemq.artemis.api.core.client.ActiveMQClient;
import org.apache.activemq.artemis.api.core.client.ClientRequestor;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.apache.activemq.artemis.api.core.management.ManagementHelper;
import org.apache.activemq.artemis.api.core.management.ResourceNames;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.spi.core.security.ActiveMQBasicSecurityManager;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SSC-076/BUG-236/PT-OPS-MQ-022: actual authenticated management-message RBAC. */
@SuppressWarnings("try") // EmbeddedActiveMQ and ClientRequestor declare broad close exceptions.
final class ArtemisExpiryManagementAuthorizationTest {
  @TempDir Path root;

  @Test
  void opsMq022MaintenanceCanOnlyInspectAndRemoveSelectedExpiryMessages() throws Exception {
    try (var fixture = securedBroker()) {
      try (var maintenance = fixture.session("nk_mq_maintenance")) {
        assertTrue(probe(maintenance, "nk.expiry.q", "countMessages", "_AMQ_ACTUAL_EXPIRY < 1"));
        assertTrue(probe(maintenance, "nk.expiry.q", "removeMessages", "_AMQ_ACTUAL_EXPIRY < 1"));
        assertFalse(
            probe(maintenance, "nk.dead.letter.q", "removeMessages", "_AMQ_ACTUAL_EXPIRY < 1"));
        assertFalse(
            probe(maintenance, "nk.sync.request.q", "removeMessages", "_AMQ_ACTUAL_EXPIRY < 1"));
        assertFalse(probe(maintenance, "nk.expiry.q", "removeAllMessages"));
        assertFalse(brokerProbe(maintenance, "getRolesAsJSON", "nk.expiry"));
      }
      try (var web = fixture.session("nk_web")) {
        assertFalse(probe(web, "nk.expiry.q", "countMessages", "_AMQ_ACTUAL_EXPIRY < 1"));
        assertFalse(probe(web, "nk.expiry.q", "removeMessages", "_AMQ_ACTUAL_EXPIRY < 1"));
      }
      try (var ops = fixture.session("nk_ops")) {
        assertTrue(brokerProbe(ops, "getRolesAsJSON", "nk.expiry"));
        assertTrue(probe(ops, "nk.dead.letter.q", "removeMessages", "_AMQ_ACTUAL_EXPIRY < 1"));
        assertTrue(probe(ops, "nk.expiry.q", "removeAllMessages"));
      }
      assertFalse(
          fixture.broker.getActiveMQServer().getPostOffice().getAddresses().stream()
              .anyMatch(address -> address.toString().startsWith("activemq.management.")));
    }
  }

  private static boolean probe(
      ClientSession session, String queue, String operation, String... args) {
    return query(session, ResourceNames.QUEUE + queue, operation, args);
  }

  private static boolean brokerProbe(ClientSession session, String operation, String... args) {
    return query(session, ResourceNames.BROKER, operation, args);
  }

  private static boolean query(
      ClientSession session, String resource, String operation, String... args) {
    try {
      session.start();
      try (var requestor = new ClientRequestor(session, "activemq.management")) {
        var request = session.createMessage(false);
        ManagementHelper.putOperationInvocation(request, resource, operation, (Object[]) args);
        var reply = requestor.request(request, 2_000L);
        return reply != null && ManagementHelper.hasOperationSucceeded(reply);
      }
    } catch (Exception denied) {
      return false;
    }
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
    String password = UUID.randomUUID().toString();
    var security =
        new ActiveMQBasicSecurityManager()
            .init(
                Map.of(
                    ActiveMQBasicSecurityManager.BOOTSTRAP_USER, "pt_ops",
                    ActiveMQBasicSecurityManager.BOOTSTRAP_PASSWORD, password,
                    ActiveMQBasicSecurityManager.BOOTSTRAP_ROLE, "nk_ops"));
    var broker =
        new EmbeddedActiveMQ().setConfiguration(config).setSecurityManager(security).start();
    try {
      var locator = ActiveMQClient.createServerLocator("vm://0");
      try {
        var factory = locator.createSessionFactory();
        return new Fixture(broker, security, locator, factory);
      } catch (Exception failure) {
        locator.close();
        throw failure;
      }
    } catch (Exception failure) {
      broker.stop();
      throw failure;
    }
  }

  private record Fixture(
      EmbeddedActiveMQ broker,
      ActiveMQBasicSecurityManager security,
      org.apache.activemq.artemis.api.core.client.ServerLocator locator,
      org.apache.activemq.artemis.api.core.client.ClientSessionFactory factory)
      implements AutoCloseable {
    ClientSession session(String role) throws Exception {
      String password = UUID.randomUUID().toString();
      String user = "pt_" + role;
      security.addNewUser(user, password, role);
      return factory.createSession(user, password, false, true, true, false, 0);
    }

    @Override
    public void close() throws Exception {
      factory.close();
      locator.close();
      broker.stop();
    }
  }
}
