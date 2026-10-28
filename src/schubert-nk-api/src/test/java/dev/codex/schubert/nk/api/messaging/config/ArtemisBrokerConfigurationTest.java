package dev.codex.schubert.nk.api.messaging.config;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;
import java.util.stream.Collectors;
import org.apache.activemq.artemis.api.core.QueueConfiguration;
import org.apache.activemq.artemis.api.core.RoutingType;
import org.apache.activemq.artemis.api.core.TransportConfiguration;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.security.Role;
import org.apache.activemq.artemis.core.server.JournalType;
import org.apache.activemq.artemis.core.settings.impl.AddressFullMessagePolicy;
import org.apache.activemq.artemis.core.settings.impl.AddressSettings;
import org.apache.activemq.artemis.core.settings.impl.DiskFullMessagePolicy;
import org.apache.activemq.artemis.core.settings.impl.PageFullMessagePolicy;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * Artemis 2.56 production-template component PT.
 *
 * <p>Trace: RD MQ-001..013/MQ-040..045; UI 231; SS 321; PT-JMS-001..004/010. Every expected
 * topology, limit and ACL in this test is a literal oracle independent from the XML.
 */
final class ArtemisBrokerConfigurationTest {
  private static final String FIXTURE_NK_DEAD_LETTER_6588D12C = "nk.dead.letter";
  private static final String FIXTURE_NK_EXPIRY_41CB6B4A = "nk.expiry";
  private static final long MIB = 1024L * 1024L;
  private static final Set<String> ADDRESSES =
      Set.of(
          "nk.sync.request",
          "nk.sync.reply.web",
          "nk.async.work",
          "nk.web.log",
          FIXTURE_NK_DEAD_LETTER_6588D12C,
          FIXTURE_NK_EXPIRY_41CB6B4A);

  private static Configuration configuration;

  @BeforeAll
  static void parseProductionTemplate() throws Exception {
    Path template = Path.of(System.getProperty("broker.template"));
    try (InputStream input = Files.newInputStream(template)) {
      configuration = new FileConfigurationParser().parseMainConfig(input);
    }
  }

  @Test
  @DisplayName("PT-JMS-001 schema parse, persistence, File Journal and global limits")
  void globalBrokerAndJournalSettingsMatchTheIndependentOracle() {
    assertEquals("schubert-nk-broker", configuration.getName());
    assertTrue(configuration.isPersistenceEnabled());
    assertTrue(configuration.isGracefulShutdownEnabled());
    assertEquals(60_000L, configuration.getGracefulShutdownTimeout());
    assertFalse(configuration.isResolveProtocols());
    assertEquals(JournalType.NIO, configuration.getJournalType());
    assertTrue(configuration.isJournalDatasync());
    assertEquals("data/paging", configuration.getPagingDirectory());
    assertEquals("data/bindings", configuration.getBindingsDirectory());
    assertEquals("data/journal", configuration.getJournalDirectory());
    assertEquals("data/large-messages", configuration.getLargeMessagesDirectory());
    assertEquals(10 * MIB, configuration.getJournalFileSize());
    assertEquals(4, configuration.getJournalMinFiles());
    assertEquals(20, configuration.getJournalPoolFiles());
    assertEquals(30, configuration.getJournalCompactPercentage());
    assertEquals(10, configuration.getJournalCompactMinFiles());
    assertEquals(512 * MIB, configuration.getGlobalMaxSize());
    assertEquals(50_000L, configuration.getGlobalMaxMessages());
    assertEquals(90, configuration.getMaxDiskUsage());
    assertEquals(5_000, configuration.getDiskScanPeriod());
    assertEquals(20_000, configuration.getIDCacheSize());
    assertTrue(configuration.isPersistIDCache());
  }

  @Test
  @DisplayName("PT-JMS-002 six durable ANYCAST address/queue pairs and loopback CORE acceptor")
  void topologyAndTransportAreClosedToTheApprovedSet() {
    Map<String, QueueConfiguration> queues = new HashMap<>();
    Map<String, Set<RoutingType>> routing = new HashMap<>();
    configuration
        .getAddressConfigurations()
        .forEach(
            address -> {
              routing.put(address.getName(), address.getRoutingTypes());
              address.getQueueConfigs().forEach(queue -> queues.put(address.getName(), queue));
            });

    assertEquals(ADDRESSES, routing.keySet());
    routing.values().forEach(types -> assertEquals(Set.of(RoutingType.ANYCAST), types));
    assertEquals(ADDRESSES, queues.keySet());
    ADDRESSES.forEach(
        address -> {
          QueueConfiguration queue = queues.get(address);
          assertEquals(address, queue.getAddress().toString());
          assertEquals(address + ".q", queue.getName().toString());
          assertEquals(RoutingType.ANYCAST, queue.getRoutingType());
          assertTrue(queue.isDurable());
        });

    assertEquals(1, configuration.getAcceptorConfigurations().size());
    TransportConfiguration acceptor = configuration.getAcceptorConfigurations().iterator().next();
    assertEquals("core", acceptor.getName());
    assertEquals("127.0.0.1", acceptor.getParams().get("host"));
    assertEquals("61616", acceptor.getParams().get("port"));
    assertEquals("CORE", acceptor.getParams().get("protocols"));
  }

  @Test
  @DisplayName("PT-JMS-003 per-address capacity, paging and redelivery are exact")
  void addressPoliciesMatchTheIndependentCapacityMatrix() {
    Map<String, Capacity> expected = new LinkedHashMap<>();
    expected.put("nk.sync.request", new Capacity(32, 50, 224, 450));
    expected.put("nk.sync.reply.web", new Capacity(32, 50, 224, 450));
    expected.put("nk.async.work", new Capacity(128, 1_000, 896, 9_000));
    expected.put("nk.web.log", new Capacity(64, 1_000, 192, 9_000));
    expected.put(FIXTURE_NK_DEAD_LETTER_6588D12C, new Capacity(128, 1_000, 1_920, 9_000));
    expected.put(FIXTURE_NK_EXPIRY_41CB6B4A, new Capacity(64, 1_000, 960, 9_000));

    assertEquals(ADDRESSES, configuration.getAddressSettings().keySet());
    expected.forEach(
        (address, capacity) ->
            assertAddressPolicy(configuration.getAddressSettings().get(address), capacity));
  }

  @Test
  @DisplayName("PT-JMS-002 ACL matrix denies every unlisted operation and role")
  void securityRolesMatchTheIndependentAclMatrix() {
    Map<String, Set<String>> expected = new LinkedHashMap<>();
    expected.put("nk.sync.request", Set.of("nk_web:S", "nk_api:C", "nk_ops:B"));
    expected.put("nk.sync.reply.web", Set.of("nk_web:C", "nk_api:S", "nk_ops:B"));
    expected.put("nk.async.work", Set.of("nk_api:CS", "nk_ops:BS"));
    expected.put("nk.web.log", Set.of("nk_web:S", "nk_api:C", "nk_ops:B"));
    expected.put(FIXTURE_NK_DEAD_LETTER_6588D12C, Set.of("nk_web:S", "nk_api:S", "nk_ops:BCM"));
    expected.put(FIXTURE_NK_EXPIRY_41CB6B4A, Set.of("nk_mq_maintenance:BC", "nk_ops:BCM"));
    expected.put("activemq.management.#", Set.of("nk_ops:CMSadnx", "nk_mq_maintenance:CMSadnx"));
    expected.put("mops.#", Set.of("nk_ops:Mve"));
    expected.put(
        "mops.queue.nk.expiry.q.countMessages", Set.of("nk_ops:Mv", "nk_mq_maintenance:Mv"));
    expected.put(
        "mops.queue.nk.expiry.q.removeMessages", Set.of("nk_ops:Me", "nk_mq_maintenance:Me"));
    expected.put(
        "mops.queue.nk.expiry.q.getMessageCount", Set.of("nk_ops:Mv", "nk_mq_maintenance:Mv"));
    expected.put(
        "mops.queue.nk.expiry.q.getPersistentSize", Set.of("nk_ops:Mv", "nk_mq_maintenance:Mv"));
    expected.put("#", Set.of());

    assertTrue(configuration.isManagementMessageRbac());
    assertEquals("mops", configuration.getManagementRbacPrefix());

    Map<String, Set<String>> actual =
        configuration.getSecurityRoles().entrySet().stream()
            .collect(
                Collectors.toMap(
                    Map.Entry::getKey,
                    entry ->
                        entry.getValue().stream()
                            .map(ArtemisBrokerConfigurationTest::permissionSignature)
                            .collect(Collectors.toCollection(TreeSet::new))));
    assertEquals(expected, actual);
  }

  private static void assertAddressPolicy(AddressSettings settings, Capacity capacity) {
    assertEquals(FIXTURE_NK_DEAD_LETTER_6588D12C, settings.getDeadLetterAddress().toString());
    assertEquals(FIXTURE_NK_EXPIRY_41CB6B4A, settings.getExpiryAddress().toString());
    assertEquals(1_000L, settings.getRedeliveryDelay());
    assertEquals(5.0, settings.getRedeliveryMultiplier());
    assertEquals(0.0, settings.getRedeliveryCollisionAvoidanceFactor());
    assertEquals(30_000L, settings.getMaxRedeliveryDelay());
    assertEquals(4, settings.getMaxDeliveryAttempts());
    assertEquals(capacity.maxSizeMib() * MIB, settings.getMaxSizeBytes());
    assertEquals(capacity.maxMessages(), settings.getMaxSizeMessages());
    assertEquals(capacity.pageLimitMib() * MIB, settings.getPageLimitBytes());
    assertEquals(capacity.pageLimitMessages(), settings.getPageLimitMessages());
    assertEquals(8 * MIB, settings.getPageSizeBytes());
    assertEquals(100, settings.getMaxReadPageMessages());
    assertEquals(16 * MIB, settings.getMaxReadPageBytes());
    assertEquals(AddressFullMessagePolicy.PAGE, settings.getAddressFullMessagePolicy());
    assertEquals(DiskFullMessagePolicy.BLOCK, settings.getDiskFullMessagePolicy());
    assertEquals(PageFullMessagePolicy.FAIL, settings.getPageFullMessagePolicy());
    assertEquals(Boolean.FALSE, settings.isAutoCreateQueues());
    assertEquals(Boolean.FALSE, settings.isAutoDeleteQueues());
    assertEquals(Boolean.FALSE, settings.isAutoDeleteCreatedQueues());
    assertEquals(Boolean.FALSE, settings.isAutoCreateAddresses());
    assertEquals(Boolean.FALSE, settings.isAutoDeleteAddresses());
    assertFalse(settings.isAutoCreateDeadLetterResources());
    assertFalse(settings.isAutoCreateExpiryResources());
    assertTrue(settings.isEnableMetrics());
    assertTrue(settings.isEnableIngressTimestamp());
  }

  private static String permissionSignature(Role role) {
    StringBuilder permissions = new StringBuilder();
    if (role.isBrowse()) {
      permissions.append('B');
    }
    if (role.isConsume()) {
      permissions.append('C');
    }
    if (role.isManage()) {
      permissions.append('M');
    }
    if (role.isSend()) {
      permissions.append('S');
    }
    if (role.isCreateAddress()) {
      permissions.append('a');
    }
    if (role.isDeleteAddress()) {
      permissions.append('d');
    }
    if (role.isCreateNonDurableQueue()) {
      permissions.append('n');
    }
    if (role.isDeleteNonDurableQueue()) {
      permissions.append('x');
    }
    assertFalse(role.isCreateDurableQueue());
    assertFalse(role.isDeleteDurableQueue());
    if (role.isView()) {
      permissions.append('v');
    }
    if (role.isEdit()) {
      permissions.append('e');
    }
    return role.getName() + ":" + permissions;
  }

  private record Capacity(
      long maxSizeMib, long maxMessages, long pageLimitMib, long pageLimitMessages) {}
}
