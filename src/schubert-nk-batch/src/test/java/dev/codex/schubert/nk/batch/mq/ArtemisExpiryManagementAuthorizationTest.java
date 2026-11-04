package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import org.apache.activemq.artemis.api.core.ActiveMQSecurityException;
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
      AuthenticatedSession session, String queue, String operation, String... args)
      throws Exception {
    return query(session, ResourceNames.QUEUE + queue, operation, args);
  }

  private static boolean brokerProbe(AuthenticatedSession session, String operation, String... args)
      throws Exception {
    return query(session, ResourceNames.BROKER, operation, args);
  }

  private static boolean query(
      AuthenticatedSession authenticated, String resource, String operation, String... args)
      throws Exception {
    // SS321/SSC076; BUG2242/YKT1988; PT-OPS-MQ-022: unknown failure is not a denial.
    ClientSession session = authenticated.client();
    String user = authenticated.username();
    session.start();
    ClientRequestor requestor;
    try {
      requestor = new ClientRequestor(session, "activemq.management");
    } catch (ActiveMQSecurityException denied) {
      if (isReplySetupDenied(denied.getMessage(), user)) return false;
      throw denied;
    }
    // A cleanup failure must escape even when the request itself was genuinely denied.
    try (requestor) {
      var request = session.createMessage(false);
      ManagementHelper.putOperationInvocation(request, resource, operation, (Object[]) args);
      org.apache.activemq.artemis.api.core.client.ClientMessage reply;
      try {
        reply = requestor.request(request, 2_000L);
      } catch (ActiveMQSecurityException denied) {
        if (isPermissionDenied(denied.getMessage(), user, "SEND", "activemq.management"))
          return false;
        throw denied;
      }
      if (reply == null || !ManagementHelper.isOperationResult(reply))
        throw new AssertionError("Missing management operation result");
      Boolean succeeded = reply.getBooleanProperty(ManagementHelper.HDR_OPERATION_SUCCEEDED);
      if (succeeded == null) throw new AssertionError("Missing management result status");
      if (succeeded) return true;
      String permission =
          switch (operation) {
            case "countMessages", "getRolesAsJSON" -> "VIEW";
            case "removeMessages", "removeAllMessages" -> "EDIT";
            default -> throw new AssertionError("Unregistered management operation");
          };
      Object result = ManagementHelper.getResult(reply);
      if (result instanceof String message
          && isPermissionDenied(message, user, permission, "mops." + resource + "." + operation))
        return false;
      throw new AssertionError("Management failure was not the expected authorization denial");
    }
  }

  /** Exact fixed SDK permission error, not an authentication or transport error. */
  private static boolean isPermissionDenied(
      String message, String user, String permission, String address) {
    return ("AMQ229032: User: "
            + user
            + " does not have permission='"
            + permission
            + "' on address "
            + address)
        .equals(message);
  }

  /** Web may be denied before sending because its temporary management reply queue is forbidden. */
  private static boolean isReplySetupDenied(String message, String user) {
    if (message == null) return false;
    for (String permission : List.of("CREATE_NON_DURABLE_QUEUE", "CREATE_ADDRESS")) {
      String addressPrefix =
          "AMQ229032: User: " + user + " does not have permission='" + permission + "' on address ";
      if (message.startsWith(addressPrefix))
        return isManagementReplyName(message.substring(addressPrefix.length()));
      String queuePrefix =
          "AMQ229213: User: " + user + " does not have permission='" + permission + "' for queue ";
      if (message.startsWith(queuePrefix)) {
        String targets = message.substring(queuePrefix.length());
        int delimiter = targets.indexOf(" on address ");
        if (delimiter < 0) return false;
        String queue = targets.substring(0, delimiter);
        String address = targets.substring(delimiter + " on address ".length());
        return queue.equals(address) && isManagementReplyName(queue);
      }
    }
    return false;
  }

  private static boolean isManagementReplyName(String address) {
    String prefix = "activemq.management.";
    if (!address.startsWith(prefix)) return false;
    String suffix = address.substring(prefix.length());
    try {
      return UUID.fromString(suffix).toString().equals(suffix);
    } catch (IllegalArgumentException malformed) {
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
    AuthenticatedSession session(String role) throws Exception {
      String password = UUID.randomUUID().toString();
      String user = "pt_" + role;
      security.addNewUser(user, password, role);
      return new AuthenticatedSession(
          user, factory.createSession(user, password, false, true, true, false, 0));
    }

    @Override
    public void close() throws Exception {
      factory.close();
      locator.close();
      broker.stop();
    }
  }

  private record AuthenticatedSession(String username, ClientSession client)
      implements AutoCloseable {
    private AuthenticatedSession {
      Objects.requireNonNull(username, "username");
      Objects.requireNonNull(client, "client");
    }

    @Override
    public void close() throws Exception {
      client.close();
    }

    @Override
    public String toString() {
      return "AuthenticatedSession[redacted]";
    }
  }
}
