package dev.codex.schubert.nk.api.messaging.guard;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.codec.TransportBodyType;
import dev.codex.schubert.nk.protocol.codec.TransportMetadata;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import java.util.HashSet;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-JMS-DIAG-001..002, SSC-467; transport value fixtures without a message or broker. */
final class GuardedJmsDiagnosticTest {
  private static final String DIAGNOSTIC = "GuardedJmsMessage[<redacted>]";

  @Test
  void differentBodiesAndMetadataProduceOneFixedDiagnosticWithoutChangingReadback() {
    byte[] input = {3, 7};
    var firstMetadata = metadata("public-a", 1);
    var first = new GuardedJmsMessage(input, firstMetadata);
    var second = new GuardedJmsMessage(new byte[0], metadata("public-b", 7));
    var values = new HashSet<GuardedJmsMessage>();
    values.add(first);
    input[0] = 41;
    byte[] copy = first.body();
    copy[1] = 19;

    assertArrayEquals(new byte[] {3, 7}, first.body());
    assertArrayEquals(new byte[0], second.body());
    assertSame(firstMetadata, first.metadata());
    assertEquals("public-a", first.metadata().transportMessageId());
    assertEquals(7, second.metadata().deliveryCount());
    assertEquals(DIAGNOSTIC, String.valueOf(first));
    assertEquals(DIAGNOSTIC, String.valueOf(second));
    assertTrue(values.contains(first));
    assertFalse(values.contains(second));
    assertFalse(first.equals(second));
  }

  @Test
  void nullBodyOrMetadataCannotCreateAnEnvelope() {
    var metadata = metadata("public-c", 2);
    assertThrows(NullPointerException.class, () -> new GuardedJmsMessage(null, metadata));
    assertThrows(NullPointerException.class, () -> new GuardedJmsMessage(new byte[0], null));
  }

  private static TransportMetadata metadata(String transportId, int deliveryCount) {
    return new TransportMetadata(
        TransportBodyType.BYTES,
        transportId,
        new UUID(0, 11),
        Optional.of("public.reply"),
        1_234L,
        2,
        deliveryCount,
        new UUID(0, 12),
        new LayoutId("LOGREQ01"),
        "001",
        "public.request");
  }
}
