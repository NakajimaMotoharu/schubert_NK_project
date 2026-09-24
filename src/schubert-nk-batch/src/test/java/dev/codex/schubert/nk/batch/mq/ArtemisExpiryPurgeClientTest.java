package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Map;
import java.util.UUID;
import org.apache.activemq.artemis.api.core.SimpleString;
import org.apache.activemq.artemis.api.core.client.ActiveMQClient;
import org.apache.activemq.artemis.api.core.client.ClientMessage;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.spi.core.security.ActiveMQBasicSecurityManager;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PG244/PT-OPS-MQ-023..026; SS321/341 fixed cutoff and destructive-operation safety. */
final class ArtemisExpiryPurgeClientTest {
  private static final long CUTOFF = 1_789_603_200_000L; // 2026-09-17T00:00:00Z, SS seven days.
  @TempDir Path root;

  @Test
  void opsMq026RealBrokerRemovesOnlyActualExpiredMessage() throws Exception {
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
    String opsPassword = UUID.randomUUID().toString();
    var security =
        new ActiveMQBasicSecurityManager()
            .init(
                Map.of(
                    ActiveMQBasicSecurityManager.BOOTSTRAP_USER, "pt_ops",
                    ActiveMQBasicSecurityManager.BOOTSTRAP_PASSWORD, opsPassword,
                    ActiveMQBasicSecurityManager.BOOTSTRAP_ROLE, "nk_ops"));
    String webPassword = UUID.randomUUID().toString();
    String maintenancePassword = UUID.randomUUID().toString();
    var broker =
        new EmbeddedActiveMQ().setConfiguration(config).setSecurityManager(security).start();
    security.addNewUser("pt_web", webPassword, "nk_web");
    security.addNewUser("pt_maintenance", maintenancePassword, "nk_mq_maintenance");
    try (var locator = ActiveMQClient.createServerLocator("vm://0");
        var factory = locator.createSessionFactory();
        var web = factory.createSession("pt_web", webPassword, false, true, true, false, 0);
        var maintenance =
            factory.createSession(
                "pt_maintenance", maintenancePassword, false, true, true, false, 0)) {
      var message = web.createMessage(true);
      message.setExpiration(System.currentTimeMillis() + 10_000);
      message.getBodyBuffer().writeString("sanitized PT payload");
      web.createProducer("nk.sync.request").send(message);
      var requestQueue =
          broker.getActiveMQServer().locateQueue(SimpleString.of("nk.sync.request.q"));
      assertEquals(
          1, requestQueue.expireReferences((org.apache.activemq.artemis.core.filter.Filter) null));
      long expiryCount =
          ArtemisExpiryPurgeClient.integer(
              ArtemisManagementReadinessClient.queueMetric(
                  maintenance, "nk.expiry.q", "messageCount"));
      assertEquals(1, expiryCount);
      long actualExpiry;
      try (var messages =
          broker.getActiveMQServer().locateQueue(SimpleString.of("nk.expiry.q")).iterator()) {
        assertTrue(messages.hasNext());
        actualExpiry = messages.next().getMessage().getLongProperty("_AMQ_ACTUAL_EXPIRY");
        assertFalse(messages.hasNext());
      }
      var equalBoundaryRun =
          new BatchRun(
              UUID.randomUUID(), Instant.ofEpochMilli(actualExpiry).plus(7, ChronoUnit.DAYS));
      var retained = new ArtemisExpiryPurgeClient().purge(maintenance, equalBoundaryRun);
      assertEquals(0, retained.selectedCount());
      assertEquals(0, retained.removedCount());
      assertEquals(1, retained.afterCount());
      var plusOneMillisecondRun =
          new BatchRun(
              UUID.randomUUID(),
              Instant.ofEpochMilli(actualExpiry).plus(7, ChronoUnit.DAYS).plusMillis(1));
      var purged = new ArtemisExpiryPurgeClient().purge(maintenance, plusOneMillisecondRun);
      assertEquals(1, purged.beforeCount());
      assertEquals(1, purged.selectedCount());
      assertEquals(1, purged.removedCount());
      assertEquals(0, purged.afterCount());
      assertTrue(purged.beforeBytes() > 0);
      assertEquals(0, purged.afterBytes());
      assertFalse(maintenance.isClosed());
      assertFalse(
          broker.getActiveMQServer().getPostOffice().getAddresses().stream()
              .anyMatch(address -> address.toString().startsWith("activemq.management.")));
    } finally {
      broker.stop();
    }
  }

  @Test
  void opsMq023FixedCutoffCountAndByteReconciliationWithoutCallerSelector() {
    var operations = new Fake(3, 300, 2, 2, 1, 100);
    var result = new ArtemisExpiryPurgeClient(operations).purge(unusedSession(), run());
    assertEquals(
        new ArtemisExpiryPurgeClient.Result(CUTOFF, 3, 2, 2, 1, 300, 200, 200, 100), result);
    assertEquals("_AMQ_ACTUAL_EXPIRY < 1789603200000", operations.selector);
    assertEquals(1, operations.removeCalls);
    assertEquals(2, operations.countCalls);
    assertEquals(2, operations.byteCalls);

    var empty = new Fake(0, 0, 0, 0, 0, 0);
    assertEquals(
        0, new ArtemisExpiryPurgeClient(empty).purge(unusedSession(), run()).removedCount());
    assertEquals(0, empty.removeCalls);
    var retained = new Fake(2, 80, 0, 0, 2, 80);
    assertEquals(
        0,
        new ArtemisExpiryPurgeClient(retained)
            .purge(unusedSession(), run())
            .estimatedSelectedBytes());
    assertEquals(0, retained.removeCalls);
  }

  @Test
  void opsMq024RejectsEveryCounterDriftOverflowAndProviderFailure() {
    assertRedacted(new Fake(1, 10, 2, 0, 1, 10)); // selected > before
    assertRedacted(new Fake(1, 10, 1, 0, 1, 10)); // remove mismatch
    assertRedacted(new Fake(2, 10, 1, 1, 2, 5)); // count mismatch
    assertRedacted(new Fake(2, 10, 1, 1, 1, 11)); // byte growth
    assertRedacted(new Fake(-1, 10, 0, 0, 0, 0));
    assertRedacted(new Fake(1, -1, 0, 0, 1, 0));
    assertRedacted(new Fake(1, 10, -1, 0, 1, 10));
    assertRedacted(new Fake(1, 10, 1, -1, 0, 0));
    assertRedacted(new Fake(1, 10, 1, 1, -1, 0));
    assertRedacted(new Fake(1, 10, 1, 1, 0, -1));
    assertRedacted(new Fake(2, Long.MAX_VALUE, 2, 2, 0, 0)); // estimated byte overflow
    var fault = new Fake(1, 10, 1, 1, 0, 0);
    fault.failSelected = true;
    assertRedacted(fault);
    assertThrows(NullPointerException.class, () -> new ArtemisExpiryPurgeClient(null));
    assertThrows(
        NullPointerException.class, () -> new ArtemisExpiryPurgeClient().purge(null, run()));
    assertThrows(
        NullPointerException.class,
        () -> new ArtemisExpiryPurgeClient().purge(unusedSession(), null));
  }

  @Test
  void opsMq025RejectsMissingMalformedOrUnboundedManagementSelector() {
    assertEquals(4L, ArtemisExpiryPurgeClient.integer(4));
    assertEquals(4L, ArtemisExpiryPurgeClient.integer(4L));
    for (Object bad : new Object[] {"4", 4.0, true}) {
      assertThrows(ArtemisExpiryPurgeException.class, () -> ArtemisExpiryPurgeClient.integer(bad));
    }
    assertThrows(ArtemisExpiryPurgeException.class, () -> ArtemisExpiryPurgeClient.integer(null));
    for (String invalid : new String[] {"", "_AMQ_ACTUAL_EXPIRY < ", "_AMQ_ACTUAL_EXPIRY > 1"}) {
      assertThrows(
          ArtemisManagementReadinessException.class,
          () ->
              ArtemisManagementReadinessClient.expiryOperation(
                  unusedSession(), "removeMessages", invalid));
    }
    assertThrows(
        ArtemisManagementReadinessException.class,
        () ->
            ArtemisManagementReadinessClient.expiryOperation(
                unusedSession(), "removeMessages", null));
    assertThrows(
        ArtemisManagementReadinessException.class,
        () ->
            ArtemisManagementReadinessClient.expiryOperation(
                unusedSession(), "removeAllMessages", "_AMQ_ACTUAL_EXPIRY < 1"));
    assertThrows(
        ArtemisManagementReadinessException.class,
        () ->
            ArtemisManagementReadinessClient.expiryOperation(
                unusedSession(), null, "_AMQ_ACTUAL_EXPIRY < 1"));
    var failingMessage =
        (ClientMessage)
            Proxy.newProxyInstance(
                ClientMessage.class.getClassLoader(),
                new Class<?>[] {ClientMessage.class},
                (proxy, method, arguments) -> {
                  throw new IllegalStateException("private-management-value");
                });
    var failure =
        assertThrows(
            ArtemisManagementReadinessException.class,
            () ->
                ArtemisManagementReadinessClient.putExpiryOperation(
                    failingMessage, "countMessages", "_AMQ_ACTUAL_EXPIRY < 1"));
    assertNull(failure.getCause());
  }

  private static void assertRedacted(Fake operations) {
    var failure =
        assertThrows(
            ArtemisExpiryPurgeException.class,
            () -> new ArtemisExpiryPurgeClient(operations).purge(unusedSession(), run()));
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertFalse(failure.getMessage().contains("private"));
  }

  private static BatchRun run() {
    return new BatchRun(
        UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
        Instant.parse("2026-09-24T00:00:00Z"));
  }

  private static ClientSession unusedSession() {
    return (ClientSession)
        Proxy.newProxyInstance(
            ClientSession.class.getClassLoader(),
            new Class<?>[] {ClientSession.class},
            (proxy, method, arguments) -> {
              throw new AssertionError("fake must not call broker");
            });
  }

  private static final class Fake implements ArtemisExpiryPurgeClient.Operations {
    final long beforeCount;
    final long beforeBytes;
    final long selected;
    final long removed;
    final long afterCount;
    final long afterBytes;
    int countCalls;
    int byteCalls;
    int removeCalls;
    String selector = "";
    boolean failSelected;

    Fake(
        long beforeCount,
        long beforeBytes,
        long selected,
        long removed,
        long afterCount,
        long afterBytes) {
      this.beforeCount = beforeCount;
      this.beforeBytes = beforeBytes;
      this.selected = selected;
      this.removed = removed;
      this.afterCount = afterCount;
      this.afterBytes = afterBytes;
    }

    @Override
    public long count(ClientSession ignored) {
      return countCalls++ == 0 ? beforeCount : afterCount;
    }

    @Override
    public long bytes(ClientSession ignored) {
      return byteCalls++ == 0 ? beforeBytes : afterBytes;
    }

    @Override
    public long selected(ClientSession ignored, String value) {
      if (failSelected) throw new IllegalStateException("private-management-value");
      selector = value;
      return selected;
    }

    @Override
    public long remove(ClientSession ignored, String value) {
      removeCalls++;
      assertEquals(selector, value);
      return removed;
    }
  }
}
