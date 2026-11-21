package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Instant;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SS312, SS331 and SS351; PT-OUTBOX-VALUE-RAW, BUG-3218. */
final class OutboxRetainedValueContractTest {
  private static final String LAYOUT = "QWKREQ01";
  private static final String VERSION = "001";
  private static final byte[] EXPECTED_BODY = {9, 2, 3};

  @Test
  void destinationClosedCatalogUsesIndependentAddressesAndEnumNames() {
    var ordered = new OutboxDestination[] {OutboxDestination.ASYNC_WORK, OutboxDestination.DLQ};
    assertArrayEquals(ordered, OutboxDestination.values());
    OutboxDestination.values()[0] = OutboxDestination.DLQ;
    assertArrayEquals(ordered, OutboxDestination.values());
    assertEquals("nk.async.work", ordered[0].address());
    assertEquals("nk.dead.letter", ordered[1].address());
    assertSame(ordered[0], OutboxDestination.valueOf("ASYNC_WORK"));
    assertSame(ordered[1], OutboxDestination.valueOf("DLQ"));
    assertSame(ordered[0], OutboxDestination.fromAddress("nk.async.work"));
    assertSame(ordered[1], OutboxDestination.fromAddress("nk.dead.letter"));
    assertThrows(NullPointerException.class, () -> OutboxDestination.valueOf(null));
    assertThrows(NullPointerException.class, () -> OutboxDestination.fromAddress(null));
    assertThrows(IllegalArgumentException.class, () -> OutboxDestination.valueOf("UNLISTED"));
    var failure =
        assertThrows(
            IllegalArgumentException.class, () -> OutboxDestination.fromAddress("nk.unlisted"));
    assertEquals("outbox destination is not allowed", failure.getMessage());
  }

  @Test
  void borrowedBytesAndEmptyMetadataNeverAppearInRetainedDiagnostics() {
    UUID message = new UUID(0, 1);
    UUID correlation = new UUID(0, 2);
    Instant time = Instant.EPOCH;
    OutboxDestination destination = OutboxDestination.ASYNC_WORK;
    byte[] input = {9, 2, 3};
    var request =
        new OutboxRequest(message, correlation, destination, LAYOUT, VERSION, input, time, time);
    var entry =
        new OutboxEntry(
            1L,
            message,
            correlation,
            destination,
            LAYOUT,
            VERSION,
            input,
            0,
            time,
            time,
            "synthetic-owner",
            time.plusSeconds(1L));
    input[0] = 0;
    request.body()[0] = 0;
    entry.body()[0] = 0;

    assertArrayEquals(EXPECTED_BODY, request.body());
    assertArrayEquals(EXPECTED_BODY, entry.body());
    assertTrue(request.dlqMetadata().isEmpty());
    assertTrue(entry.dlqMetadata().isEmpty());
    assertEquals("OutboxRequest[<redacted>]", request.toString());
    assertEquals("OutboxEntry[<redacted>]", entry.toString());
  }

  @Test // PT-OUTBOX-COPY001; SS324/351
  void requestRejectsEmptyBodyBeforeProfileAndRetainsBorrowedBytesOnFailure() {
    UUID message = new UUID(0, 1);
    UUID correlation = new UUID(0, 2);
    Instant time = Instant.EPOCH;
    var destination = OutboxDestination.DLQ;
    assertEquals(
        "outbox body must not be empty",
        assertThrows(
                IllegalArgumentException.class,
                () ->
                    new OutboxRequest(
                        message,
                        correlation,
                        destination,
                        LAYOUT,
                        VERSION,
                        new byte[0],
                        time,
                        time))
            .getMessage());
    byte[] body = {9, 2, 3};
    assertEquals(
        "outbox destination and DLQ metadata disagree",
        assertThrows(
                IllegalArgumentException.class,
                () ->
                    new OutboxRequest(
                        message, correlation, destination, LAYOUT, VERSION, body, time, time))
            .getMessage());
    assertArrayEquals(new byte[] {9, 2, 3}, body);
  }

  @Test // PT-OUTBOX-COPY002; SS324/351
  void entryRejectsLeaseBeforeProfileAndRetainsBorrowedBytesOnFailure() {
    byte[] body = {9, 2, 3};
    assertEquals(
        "leaseOwner must contain 1 to 64 characters",
        assertThrows(IllegalArgumentException.class, () -> entryWithAbsentDlqMetadata(body, ""))
            .getMessage());
    assertEquals(
        "outbox destination and DLQ metadata disagree",
        assertThrows(
                IllegalArgumentException.class,
                () -> entryWithAbsentDlqMetadata(body, "synthetic-owner"))
            .getMessage());
    assertArrayEquals(new byte[] {9, 2, 3}, body);
  }

  private static OutboxEntry entryWithAbsentDlqMetadata(byte[] body, String lease) {
    return new OutboxEntry(
        1L,
        new UUID(0, 1),
        new UUID(0, 2),
        OutboxDestination.DLQ,
        LAYOUT,
        VERSION,
        body,
        0,
        Instant.EPOCH,
        Instant.EPOCH,
        lease,
        Instant.EPOCH.plusSeconds(1L));
  }
}
