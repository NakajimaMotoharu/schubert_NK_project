package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Instant;
import java.util.HashSet;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SS312 and SS351; PT-JMS-EVENT-DELIVERY-VALUE, BUG-3215. */
final class DeliveryMetadataValueContractTest {
  private static final String SYNTHETIC_ID = "ID:synthetic-reference";

  @Test
  void allThreeFieldsDefineValueIdentityWithoutChangingDiagnostic() {
    var time = Instant.parse("2026-10-01T00:00:00Z");
    var value = new DeliveryMetadata(2, SYNTHETIC_ID, time);
    var equal = new DeliveryMetadata(2, SYNTHETIC_ID, Instant.ofEpochSecond(1790812800L));

    assertEquals(value, equal);
    assertEquals(equal, value);
    assertFalse(value.equals(null));
    assertFalse(value.equals(SYNTHETIC_ID));

    var distinct = new HashSet<DeliveryMetadata>();
    assertTrue(distinct.add(value));
    assertFalse(distinct.add(equal));
    for (var other :
        List.of(
            new DeliveryMetadata(3, SYNTHETIC_ID, time),
            new DeliveryMetadata(2, "ID:other-reference", time),
            new DeliveryMetadata(2, SYNTHETIC_ID, time.plusSeconds(1)))) {
      assertNotEquals(value, other);
      assertTrue(distinct.add(other));
      assertEquals("DeliveryMetadata[metadata=<redacted>]", other.toString());
    }
    assertEquals(4, distinct.size());
    assertEquals("DeliveryMetadata[metadata=<redacted>]", value.toString());
  }
}
