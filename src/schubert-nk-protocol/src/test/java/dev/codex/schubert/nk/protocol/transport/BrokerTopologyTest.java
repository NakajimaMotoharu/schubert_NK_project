package dev.codex.schubert.nk.protocol.transport;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-JMS-002/005 independent SS 321 topology and transport-limit matrix. */
final class BrokerTopologyTest {
  @Test
  void sixDestinationsMatchTheIndependentPhysicalAndLimitOracle() {
    List<Vector> expected =
        List.of(
            new Vector("SYNC_REQUEST", "nk.sync.request", 1_000_000, 5_000),
            new Vector("SYNC_REPLY_WEB", "nk.sync.reply.web", 1_000_000, 10_000),
            new Vector("ASYNC_WORK", "nk.async.work", 1_000, 0),
            new Vector("WEB_LOG", "nk.web.log", 10_000, 0),
            new Vector("DEAD_LETTER", "nk.dead.letter", 1_000_000, 0),
            new Vector("EXPIRY", "nk.expiry", 1_000_000, 0));

    assertEquals(6, BrokerTopology.values().length);
    for (int index = 0; index < expected.size(); index++) {
      Vector vector = expected.get(index);
      BrokerTopology actual = BrokerTopology.values()[index];
      assertEquals(vector.constant(), actual.name());
      assertEquals(vector.address(), actual.address());
      assertEquals(vector.address() + ".q", actual.queue());
      assertEquals(vector.address() + "::" + vector.address() + ".q", actual.fullyQualifiedQueue());
      assertEquals(vector.maximumBodyLength(), actual.maximumBodyLength());
      assertEquals(vector.timeToLiveMillis(), actual.timeToLiveMillis());
      assertEquals(vector.timeToLiveMillis() > 0, actual.expirationRequired());
      assertEquals(actual, BrokerTopology.requireAddress(vector.address()));
    }
    assertTrue(BrokerTopology.SYNC_REQUEST.expirationRequired());
    assertFalse(BrokerTopology.ASYNC_WORK.expirationRequired());
  }

  @Test
  void nullUnknownAndNearMatchAddressesAreDenied() {
    assertThrows(NullPointerException.class, () -> BrokerTopology.requireAddress(null));
    assertThrows(
        IllegalArgumentException.class, () -> BrokerTopology.requireAddress("nk.sync.request.q"));
    assertThrows(
        IllegalArgumentException.class, () -> BrokerTopology.requireAddress("nk.sync.request "));
  }

  private record Vector(
      String constant, String address, int maximumBodyLength, long timeToLiveMillis) {}
}
