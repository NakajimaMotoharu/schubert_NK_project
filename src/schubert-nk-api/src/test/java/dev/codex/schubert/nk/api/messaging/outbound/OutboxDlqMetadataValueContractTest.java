package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Instant;
import java.util.HashSet;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SS312 and SS351; PT-QST-DLQ-VALUES, BUG-3217. */
final class OutboxDlqMetadataValueContractTest {
  private static final UUID ORIGINAL = new UUID(0, 1);
  private static final String TRANSPORT = "ID:synthetic-original";
  private static final String ERROR_CODE = "QUESTION_RETRY_EXHAUSTED";
  private static final String REDACTED = "OutboxDlqMetadata[<redacted>]";
  private static final Instant DETECTED = Instant.parse("2026-10-01T00:00:00.000031Z");

  @Test
  void originalDeliveryFieldsDetermineValueAndStayOutOfDiagnostics() {
    var value = new OutboxDlqMetadata(ORIGINAL, TRANSPORT, 4, ERROR_CODE, DETECTED);
    var equal =
        new OutboxDlqMetadata(
            new UUID(0, 1), TRANSPORT, 4, ERROR_CODE, Instant.ofEpochSecond(1790812800L, 31000));
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertFalse(value.equals(null));
    assertFalse(value.equals(TRANSPORT));
    assertEquals(ORIGINAL, value.originalMessageId());
    assertEquals(TRANSPORT, value.originalTransportId());
    assertEquals(4, value.deliveryCount());
    assertEquals(ERROR_CODE, value.errorCode());
    assertEquals(DETECTED, value.detectedAt());
    assertEquals(REDACTED, value.toString());

    var values = new HashSet<OutboxDlqMetadata>();
    assertTrue(values.add(value));
    assertFalse(values.add(equal));
    for (var other :
        List.of(
            new OutboxDlqMetadata(new UUID(0, 2), TRANSPORT, 4, ERROR_CODE, DETECTED),
            new OutboxDlqMetadata(ORIGINAL, "ID:synthetic-alternate", 4, ERROR_CODE, DETECTED),
            new OutboxDlqMetadata(ORIGINAL, TRANSPORT, 5, ERROR_CODE, DETECTED),
            new OutboxDlqMetadata(ORIGINAL, TRANSPORT, 4, ERROR_CODE, DETECTED.plusNanos(1000)))) {
      assertNotEquals(value, other);
      assertTrue(values.add(other));
      assertEquals(REDACTED, other.toString());
    }
    assertEquals(5, values.size());
  }
}
