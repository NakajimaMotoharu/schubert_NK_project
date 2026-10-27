package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-QST-DLQ-MODEL; SS331/SSC155; literals independent of production calculations. */
final class OutboxDlqMetadataTest {
  private static final String EXPECTED_RETRY_EXHAUSTED = "QUESTION_RETRY_EXHAUSTED";
  private static final String ORIGINAL_TRANSPORT_ID = "ID:original";
  private static final String QUESTION_WORK_LAYOUT = "QWKREQ01";
  private static final String LAYOUT_VERSION = "001";
  private static final UUID W = UUID.fromString("83000000-0000-4000-8000-000000000001");
  private static final UUID D = UUID.fromString("83000000-0000-4000-8000-000000000002");
  private static final Instant TIME = Instant.parse("2026-10-01T00:00:00Z");

  @Test
  void boundsActualCountAndUtcMicrosecondsAreImmutableAndRedacted() {
    for (int count : List.of(1, 4, Integer.MAX_VALUE)) {
      for (String id : List.of("!", "x".repeat(128))) {
        for (String time :
            List.of(
                "0001-01-01T00:00:00Z", "1582-10-10T00:00:00Z", "9999-12-31T23:59:59.999999Z")) {
          var metadata =
              new OutboxDlqMetadata(W, id, count, EXPECTED_RETRY_EXHAUSTED, Instant.parse(time));
          assertEquals(W, metadata.originalMessageId());
          assertEquals(id, metadata.originalTransportId());
          assertEquals(count, metadata.deliveryCount());
          assertEquals(EXPECTED_RETRY_EXHAUSTED, metadata.errorCode());
          assertEquals(Instant.parse(time), metadata.detectedAt());
          assertEquals("OutboxDlqMetadata[<redacted>]", metadata.toString());
        }
      }
    }
    for (String id : List.of("", " ", "x".repeat(129), "\n", "ID:\n", "\u007f", "日"))
      assertThrows(IllegalArgumentException.class, () -> metadata(id, 4, TIME));
    for (int count : List.of(0, -1, Integer.MIN_VALUE))
      assertThrows(
          IllegalArgumentException.class, () -> metadata(ORIGINAL_TRANSPORT_ID, count, TIME));
    for (Instant time : List.of(Instant.MIN, Instant.MAX, TIME.plusNanos(1)))
      assertThrows(IllegalArgumentException.class, () -> metadata(ORIGINAL_TRANSPORT_ID, 4, time));
    assertThrows(
        IllegalArgumentException.class,
        () -> new OutboxDlqMetadata(W, ORIGINAL_TRANSPORT_ID, 4, "UNKNOWN", TIME));
    assertThrows(
        NullPointerException.class,
        () ->
            new OutboxDlqMetadata(null, ORIGINAL_TRANSPORT_ID, 4, EXPECTED_RETRY_EXHAUSTED, TIME));
    assertThrows(NullPointerException.class, () -> metadata(null, 4, TIME));
    assertThrows(
        NullPointerException.class,
        () -> new OutboxDlqMetadata(W, ORIGINAL_TRANSPORT_ID, 4, null, TIME));
    assertThrows(NullPointerException.class, () -> metadata(ORIGINAL_TRANSPORT_ID, 4, null));
  }

  @Test
  void exactDestinationSpecificProfileOwnsBodyAndRequiresOriginalDifferentFromDispatch() {
    var m = Optional.of(metadata(ORIGINAL_TRANSPORT_ID, 4, TIME));
    byte[] body = new byte[320];
    var request = request(D, OutboxDestination.DLQ, QUESTION_WORK_LAYOUT, LAYOUT_VERSION, body, m);
    var entry =
        new OutboxEntry(
            1,
            D,
            W,
            OutboxDestination.DLQ,
            QUESTION_WORK_LAYOUT,
            LAYOUT_VERSION,
            body,
            0,
            TIME,
            TIME,
            "worker",
            TIME.plusSeconds(10),
            m);
    body[0] = 99;
    assertEquals(0, request.body()[0]);
    assertEquals(0, entry.body()[0]);
    assertEquals(m, request.dlqMetadata());
    assertEquals(m, entry.dlqMetadata());
    assertThrows(
        IllegalArgumentException.class,
        () ->
            request(
                W, OutboxDestination.DLQ, QUESTION_WORK_LAYOUT, LAYOUT_VERSION, new byte[320], m));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            request(
                D,
                OutboxDestination.ASYNC_WORK,
                QUESTION_WORK_LAYOUT,
                LAYOUT_VERSION,
                new byte[320],
                m));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            request(
                D,
                OutboxDestination.DLQ,
                QUESTION_WORK_LAYOUT,
                LAYOUT_VERSION,
                new byte[320],
                Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () -> request(D, OutboxDestination.DLQ, "LOGREQ01", LAYOUT_VERSION, new byte[320], m));
    assertThrows(
        IllegalArgumentException.class,
        () -> request(D, OutboxDestination.DLQ, QUESTION_WORK_LAYOUT, "002", new byte[320], m));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            request(
                D, OutboxDestination.DLQ, QUESTION_WORK_LAYOUT, LAYOUT_VERSION, new byte[319], m));
    assertThrows(
        NullPointerException.class,
        () ->
            request(
                D,
                OutboxDestination.DLQ,
                QUESTION_WORK_LAYOUT,
                LAYOUT_VERSION,
                new byte[320],
                null));
    assertTrue(
        request(
                D,
                OutboxDestination.ASYNC_WORK,
                QUESTION_WORK_LAYOUT,
                LAYOUT_VERSION,
                new byte[320],
                Optional.empty())
            .dlqMetadata()
            .isEmpty());
  }

  private static OutboxDlqMetadata metadata(String transport, int count, Instant time) {
    return new OutboxDlqMetadata(W, transport, count, EXPECTED_RETRY_EXHAUSTED, time);
  }

  private static OutboxRequest request(
      UUID id,
      OutboxDestination destination,
      String layout,
      String version,
      byte[] body,
      Optional<OutboxDlqMetadata> metadata) {
    return new OutboxRequest(id, W, destination, layout, version, body, TIME, TIME, metadata);
  }
}
