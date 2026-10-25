package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
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
      var requestQueue =
          broker.getActiveMQServer().locateQueue(SimpleString.of("nk.sync.request.q"));
      // BUG1245/YKT1011: durable send confirmation is not iterator-visible delivery.
      // Hold this real queue's executor to make the original race deterministic.
      var entered = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      var completed = new CompletableFuture<Void>();
      requestQueue
          .getExecutor()
          .execute(
              () -> {
                entered.countDown();
                try {
                  if (release.await(10, TimeUnit.SECONDS)) completed.complete(null);
                  else completed.completeExceptionally(new AssertionError("fixture gate deadline"));
                } catch (InterruptedException interrupted) {
                  Thread.currentThread().interrupt();
                  completed.completeExceptionally(interrupted);
                }
              });
      try {
        assertTrue(entered.await(5, TimeUnit.SECONDS));
        var message = web.createMessage(true);
        // Explicit force-expiry below creates the broker's actual timestamp.
        // No automatic short TTL may race that fixture-only transition.
        message.setExpiration(Long.MAX_VALUE);
        message.getBodyBuffer().writeString("sanitized PT payload");
        web.createProducer("nk.sync.request").send(message);
        assertEquals(
            0,
            requestQueue.expireReferences((org.apache.activemq.artemis.core.filter.Filter) null));
      } finally {
        release.countDown();
      }
      completed.get(5, TimeUnit.SECONDS);
      long deliveryStart = System.nanoTime();
      while (requestQueue.getMessageCount() != 1
          && System.nanoTime() - deliveryStart < TimeUnit.SECONDS.toNanos(5)) {
        Thread.sleep(1);
      }
      assertEquals(1, requestQueue.getMessageCount());
      var delivered = new CountDownLatch(1);
      requestQueue.flushOnIntermediate(delivered::countDown);
      assertTrue(delivered.await(5, TimeUnit.SECONDS));
      assertTrue(requestQueue.flushExecutor());
      assertEquals(1, requestQueue.getMessageCount());
      assertEquals(
          1, requestQueue.expireReferences((org.apache.activemq.artemis.core.filter.Filter) null));
      var expiryQueue = broker.getActiveMQServer().locateQueue(SimpleString.of("nk.expiry.q"));
      assertTrue(expiryQueue.flushExecutor());
      long expiryCount =
          ArtemisExpiryPurgeClient.integer(
              ArtemisManagementReadinessClient.queueMetric(
                  maintenance, "nk.expiry.q", "messageCount"));
      assertEquals(1, expiryCount);
      long actualExpiry;
      try (var messages = expiryQueue.iterator()) {
        assertTrue(messages.hasNext());
        actualExpiry = messages.next().getMessage().getLongProperty("_AMQ_ACTUAL_EXPIRY");
        assertFalse(messages.hasNext());
      }
      var equalBoundaryRun =
          new BatchRun(
              UUID.randomUUID(), Instant.ofEpochMilli(actualExpiry).plus(7, ChronoUnit.DAYS));
      var client = new ArtemisExpiryPurgeClient();
      var retainedObservation = client.observe(maintenance, equalBoundaryRun);
      assertEquals(0, retainedObservation.selectedCount());
      var retained = client.purgeObserved(maintenance, equalBoundaryRun, retainedObservation);
      assertEquals(0, retained.selectedCount());
      assertEquals(0, retained.removedCount());
      assertEquals(1, retained.afterCount());
      var fractionalRun =
          new BatchRun(
              UUID.randomUUID(),
              Instant.ofEpochMilli(actualExpiry).plus(7, ChronoUnit.DAYS).plusNanos(500_000));
      var fractionalObservation = client.observe(maintenance, fractionalRun);
      assertEquals(1, fractionalObservation.selectedCount()); // timestamp t < t+500µs.
      assertEquals(1, expiryCount); // Observation does not remove the broker message.
      var plusOneMillisecondRun =
          new BatchRun(
              UUID.randomUUID(),
              Instant.ofEpochMilli(actualExpiry).plus(7, ChronoUnit.DAYS).plusMillis(1));
      var purgeObservation = client.observe(maintenance, plusOneMillisecondRun);
      assertEquals(1, purgeObservation.selectedCount());
      assertEquals(1, expiryCount);
      var purged = client.purgeObserved(maintenance, plusOneMillisecondRun, purgeObservation);
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
    var client = new ArtemisExpiryPurgeClient(operations);
    var observation = client.observe(unusedSession(), run());
    assertEquals(new ArtemisExpiryPurgeClient.Observation(CUTOFF, 3, 2, 300, 200), observation);
    assertEquals(0, operations.removeCalls); // The parent can durably commit here.
    var result = client.purgeObserved(unusedSession(), run(), observation);
    assertEquals(
        new ArtemisExpiryPurgeClient.Result(CUTOFF, 3, 2, 2, 1, 300, 200, 200, 100), result);
    assertEquals("_AMQ_ACTUAL_EXPIRY < 1789603200000", operations.selector);
    assertEquals(1, operations.removeCalls);
    assertEquals(3, operations.countCalls);
    assertEquals(3, operations.byteCalls);

    var empty = new Fake(0, 0, 0, 0, 0, 0);
    var emptyClient = new ArtemisExpiryPurgeClient(empty);
    assertEquals(
        0,
        emptyClient
            .purgeObserved(unusedSession(), run(), emptyClient.observe(unusedSession(), run()))
            .removedCount());
    assertEquals(0, empty.removeCalls);
    var retained = new Fake(2, 80, 0, 0, 2, 80);
    var retainedClient = new ArtemisExpiryPurgeClient(retained);
    assertEquals(
        0,
        retainedClient
            .purgeObserved(unusedSession(), run(), retainedClient.observe(unusedSession(), run()))
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
    assertThrows(
        IllegalStateException.class,
        () -> new ArtemisExpiryPurgeClient(fault).observe(unusedSession(), run()));
    assertThrows(NullPointerException.class, () -> new ArtemisExpiryPurgeClient(null));
    assertThrows(
        NullPointerException.class, () -> new ArtemisExpiryPurgeClient().observe(null, run()));
    assertThrows(
        NullPointerException.class,
        () -> new ArtemisExpiryPurgeClient().observe(unusedSession(), null));
    assertThrows(
        NullPointerException.class,
        () -> new ArtemisExpiryPurgeClient().purgeObserved(null, run(), validObservation()));
    assertThrows(
        NullPointerException.class,
        () ->
            new ArtemisExpiryPurgeClient()
                .purgeObserved(unusedSession(), null, validObservation()));
    assertThrows(
        NullPointerException.class,
        () -> new ArtemisExpiryPurgeClient().purgeObserved(unusedSession(), run(), null));
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
            IllegalStateException.class,
            () ->
                ArtemisManagementReadinessClient.putExpiryOperation(
                    failingMessage, "countMessages", "_AMQ_ACTUAL_EXPIRY < 1"));
    assertNull(failure.getCause());
  }

  @Test
  void opsMq027RejectsUnstagedOrDriftedObservationBeforeRemove() {
    var invalid =
        new ArtemisExpiryPurgeClient.Observation[] {
          new ArtemisExpiryPurgeClient.Observation(CUTOFF + 1, 1, 1, 10, 10),
          new ArtemisExpiryPurgeClient.Observation(CUTOFF, -1, 0, 10, 0),
          new ArtemisExpiryPurgeClient.Observation(CUTOFF, 1, 1, -1, 0),
          new ArtemisExpiryPurgeClient.Observation(CUTOFF, 1, -1, 10, 0),
          new ArtemisExpiryPurgeClient.Observation(CUTOFF, 1, 2, 10, 0),
          new ArtemisExpiryPurgeClient.Observation(CUTOFF, 1, 1, 10, -1),
          new ArtemisExpiryPurgeClient.Observation(CUTOFF, 1, 1, 10, 11),
          new ArtemisExpiryPurgeClient.Observation(CUTOFF, 2, 1, 10, 4),
          new ArtemisExpiryPurgeClient.Observation(CUTOFF, 2, 2, Long.MAX_VALUE, Long.MAX_VALUE)
        };
    for (var value : invalid) {
      var operations = new Fake(1, 10, 1, 1, 0, 0);
      assertPurgeRejectedBeforeRemove(operations, value);
    }
    var countDrift = new Fake(1, 10, 1, 1, 0, 0);
    countDrift.prePurgeCount = 0;
    countDrift.countCalls = 1;
    assertPurgeRejectedBeforeRemove(countDrift, validObservation());
    var byteDrift = new Fake(1, 10, 1, 1, 0, 0);
    byteDrift.prePurgeBytes = 9;
    byteDrift.byteCalls = 1;
    assertPurgeRejectedBeforeRemove(byteDrift, validObservation());
    var selectedDrift = new Fake(1, 10, 1, 1, 0, 0);
    selectedDrift.selectedAfterStage = 0;
    selectedDrift.selectedCalls = 1;
    assertPurgeRejectedBeforeRemove(selectedDrift, validObservation());
    var providerFailure = new Fake(1, 10, 1, 1, 0, 0);
    providerFailure.failSelected = true;
    assertThrows(
        IllegalStateException.class,
        () ->
            new ArtemisExpiryPurgeClient(providerFailure)
                .purgeObserved(unusedSession(), run(), validObservation()));
    assertEquals(0, providerFailure.removeCalls);
  }

  @Test
  void opsMq028StrictSevenDayCutoffRetainsSubmillisecondPrecision() {
    var operations = new Fake(1, 10, 1, 1, 0, 0);
    var client = new ArtemisExpiryPurgeClient(operations);
    var microRun = new BatchRun(UUID.randomUUID(), Instant.parse("2026-09-24T00:00:00.000500Z"));
    var observation = client.observe(unusedSession(), microRun);
    assertEquals(CUTOFF + 1, observation.cutoffEpochMillis());
    assertEquals("_AMQ_ACTUAL_EXPIRY < 1789603200001", operations.selector);
    assertEquals(1, client.purgeObserved(unusedSession(), microRun, observation).removedCount());
    assertEquals("_AMQ_ACTUAL_EXPIRY < 1789603200001", operations.selector);

    var beforeEpoch = new Fake(1, 10, 1, 1, 0, 0);
    var beforeEpochRun =
        new BatchRun(UUID.randomUUID(), Instant.parse("1970-01-07T23:59:59.999500Z"));
    var negativeObservation =
        new ArtemisExpiryPurgeClient(beforeEpoch).observe(unusedSession(), beforeEpochRun);
    assertEquals(0, negativeObservation.cutoffEpochMillis());
    assertEquals("_AMQ_ACTUAL_EXPIRY < 0", beforeEpoch.selector);
  }

  private static void assertPurgeRejectedBeforeRemove(
      Fake operations, ArtemisExpiryPurgeClient.Observation observation) {
    var failure =
        assertThrows(
            ArtemisExpiryPurgeException.class,
            () ->
                new ArtemisExpiryPurgeClient(operations)
                    .purgeObserved(unusedSession(), run(), observation));
    assertNull(failure.getCause());
    assertEquals(0, operations.removeCalls);
  }

  private static void assertRedacted(Fake operations) {
    var failure =
        assertThrows(
            ArtemisExpiryPurgeException.class,
            () -> {
              var client = new ArtemisExpiryPurgeClient(operations);
              client.purgeObserved(unusedSession(), run(), client.observe(unusedSession(), run()));
            });
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertFalse(failure.getMessage().contains("private"));
  }

  private static BatchRun run() {
    return new BatchRun(
        UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
        Instant.parse("2026-09-24T00:00:00Z"));
  }

  private static ArtemisExpiryPurgeClient.Observation validObservation() {
    return new ArtemisExpiryPurgeClient.Observation(CUTOFF, 1, 1, 10, 10);
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
    int selectedCalls;
    String selector = "";
    boolean failSelected;
    long prePurgeCount;
    long prePurgeBytes;
    long selectedAfterStage;

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
      prePurgeCount = beforeCount;
      prePurgeBytes = beforeBytes;
      selectedAfterStage = selected;
    }

    @Override
    public long count(ClientSession ignored) {
      return switch (countCalls++) {
        case 0 -> beforeCount;
        case 1 -> prePurgeCount;
        default -> afterCount;
      };
    }

    @Override
    public long bytes(ClientSession ignored) {
      return switch (byteCalls++) {
        case 0 -> beforeBytes;
        case 1 -> prePurgeBytes;
        default -> afterBytes;
      };
    }

    @Override
    public long selected(ClientSession ignored, String value) {
      if (failSelected) throw new IllegalStateException("private-management-value");
      selector = value;
      return selectedCalls++ == 0 ? selected : selectedAfterStage;
    }

    @Override
    public long remove(ClientSession ignored, String value) {
      removeCalls++;
      assertEquals(selector, value);
      return removed;
    }
  }
}
