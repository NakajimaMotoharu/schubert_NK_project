package dev.codex.schubert.nk.api.messaging.config;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.Map;
import org.apache.activemq.artemis.api.core.TransportConfiguration;
import org.apache.activemq.artemis.core.remoting.impl.netty.NettyConnectorFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.junit.jupiter.api.Test;

/** PT-JMS-011 independent effective-value checks for all three client profiles. */
final class ArtemisConnectionFactoryProviderTest {
  @Test
  void commonConnectionAndReconnectPolicyIsExactAndCredentialFree() {
    try (ActiveMQConnectionFactory factory = create(ArtemisConnectionFactoryProvider.ConsumerProfile.SYNC)) {
      assertFalse(factory.isHA());
      assertEquals(2_000L, factory.getCallTimeout());
      assertEquals(10_000L, factory.getClientFailureCheckPeriod());
      assertEquals(30_000L, factory.getConnectionTTL());
      assertEquals(3, factory.getInitialConnectAttempts());
      assertEquals(-1, factory.getReconnectAttempts());
      assertEquals(1_000L, factory.getRetryInterval());
      assertEquals(2.0, factory.getRetryIntervalMultiplier());
      assertEquals(30_000L, factory.getMaxRetryInterval());
      assertTrue(factory.isBlockOnDurableSend());
      assertFalse(factory.isPreAcknowledge());
      assertFalse(factory.isUseTopologyForLoadBalancing());
      assertNull(factory.getUser());
      assertNull(factory.getPassword());

      TransportConfiguration[] connectors = factory.getStaticConnectors();
      assertEquals(1, connectors.length);
      assertEquals(NettyConnectorFactory.class.getName(), connectors[0].getFactoryClassName());
      assertEquals("schubert-nk-core", connectors[0].getName());
      assertEquals(
          Map.of(
              "host", "127.0.0.1",
              "port", 61_616,
              "connect-timeout-millis", 3_000),
          connectors[0].getParams());
    }
  }

  @Test
  void consumerWindowProfilesAreOneMibZeroAndSixtyFourKib() {
    assertEquals(3, ArtemisConnectionFactoryProvider.ConsumerProfile.values().length);
    assertEquals(
        ArtemisConnectionFactoryProvider.ConsumerProfile.SYNC,
        ArtemisConnectionFactoryProvider.ConsumerProfile.valueOf("SYNC"));
    assertWindow(ArtemisConnectionFactoryProvider.ConsumerProfile.SYNC, 1_048_576);
    assertWindow(ArtemisConnectionFactoryProvider.ConsumerProfile.ASYNC, 0);
    assertWindow(ArtemisConnectionFactoryProvider.ConsumerProfile.WEB_LOG, 65_536);
    assertThrows(
        NullPointerException.class,
        () -> ArtemisConnectionFactoryProvider.INSTANCE.create(null));
  }

  private static ActiveMQConnectionFactory create(
      ArtemisConnectionFactoryProvider.ConsumerProfile profile) {
    return ArtemisConnectionFactoryProvider.INSTANCE.create(profile);
  }

  private static void assertWindow(
      ArtemisConnectionFactoryProvider.ConsumerProfile profile, int expected) {
    try (ActiveMQConnectionFactory factory = create(profile)) {
      assertEquals(expected, factory.getConsumerWindowSize());
      assertEquals(expected, profile.windowBytes());
    }
  }
}
