package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/**
 * PT-DELIVERY-VALUE001; SS312/321/354: value semantics alone certify no actual guarded delivery.
 */
final class DeliveryValueContractTest {
  private static final String TRANSPORT = "ID:synthetic";

  @Test
  void deliveryValue001AllThreeComponentsAndRedactedRenderingDefineTheValue() {
    DeliveryMetadata value = new DeliveryMetadata(1, TRANSPORT, Instant.EPOCH);
    DeliveryMetadata equal = new DeliveryMetadata(1, TRANSPORT, Instant.EPOCH);
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertEquals(value.hashCode(), equal.hashCode());
    assertEquals("found", Map.of(value, "found").get(equal));
    assertNotEquals(value, null);
    assertNotEquals(value, "different type");
    for (DeliveryMetadata other :
        List.of(
            new DeliveryMetadata(2, TRANSPORT, Instant.EPOCH),
            new DeliveryMetadata(1, "ID:other", Instant.EPOCH),
            new DeliveryMetadata(1, TRANSPORT, Instant.parse("1970-01-01T00:00:01Z")))) {
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
    assertEquals("DeliveryMetadata[metadata=<redacted>]", value.toString());
  }
}
