package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SS312/SSC153/BUG423/YKT334; PT-JMS-EVENT-DELIVERY independent bounds. */
final class DeliveryMetadataTest {
  private static final Instant NOW = Instant.parse("2026-10-01T00:00:00Z");

  @Test
  void countsAndPrintable128ByteBoundaryAreNotCapped() {
    for (int count : List.of(1, 3, 4, 5, Integer.MAX_VALUE)) {
      for (String id : List.of("!", "ID:actual-delivery", "~".repeat(128))) {
        var delivery = new DeliveryMetadata(count, id, NOW);
        assertEquals(count, delivery.deliveryCount());
        assertEquals(id, delivery.transportMessageId());
        assertEquals(NOW, delivery.receivedAt());
        assertEquals("DeliveryMetadata[metadata=<redacted>]", delivery.toString());
      }
    }
  }

  @Test
  void nullMissingInvalidAndControlMetadataReject() {
    assertThrows(NullPointerException.class, () -> new DeliveryMetadata(1, null, NOW));
    assertThrows(NullPointerException.class, () -> new DeliveryMetadata(1, "ID:test", null));
    for (int count : List.of(0, -1, Integer.MIN_VALUE))
      assertThrows(
          IllegalArgumentException.class, () -> new DeliveryMetadata(count, "ID:test", NOW));
    for (String id : List.of("", " ", "!".repeat(129), "ID:\u001f", "ID:\u007f", "ID:日本"))
      assertThrows(IllegalArgumentException.class, () -> new DeliveryMetadata(1, id, NOW));
  }
}
