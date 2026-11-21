package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-IDEM-009/011 null, bounds, defensive-copy, and redaction contract. */
final class OutboxModelTest {
  private static final String FIXTURE_QWKREQ01_19741256 = "QWKREQ01";
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final UUID MESSAGE = UUID.fromString("71000000-0000-0000-0000-000000000001");
  private static final UUID CORRELATION = UUID.fromString("72000000-0000-0000-0000-000000000001");
  private static final Instant NOW = Instant.parse("2026-09-05T00:00:00Z");

  @Test
  void entryOwnsBodyExposesEveryFieldAndRedactsText() {
    byte[] source = {1, 2, 3};
    OutboxEntry entry = entry(source);
    source[0] = 9;
    byte[] first = entry.body();
    first[1] = 9;

    assertEquals(1, entry.id());
    assertEquals(MESSAGE, entry.messageId());
    assertEquals(CORRELATION, entry.correlationId());
    assertEquals(OutboxDestination.ASYNC_WORK, entry.destination());
    assertEquals(FIXTURE_QWKREQ01_19741256, entry.layoutId());
    assertEquals(FIXTURE_001_A3FEAA64, entry.layoutVersion());
    assertArrayEquals(new byte[] {1, 2, 3}, entry.body());
    assertEquals(0, entry.attemptCount());
    assertEquals(NOW, entry.nextAttemptAt());
    assertEquals(NOW.minusSeconds(1), entry.createdAt());
    assertEquals("worker-a", entry.leaseOwner());
    assertEquals(NOW.plusSeconds(10), entry.leaseUntil());
    assertEquals("OutboxEntry[<redacted>]", entry.toString());
    assertFalse(entry.toString().contains("[1, 2, 3]"));
  }

  @Test
  void entryRejectsEveryInvalidBoundaryAndNull() {
    assertThrows(
        IllegalArgumentException.class,
        () -> entry(0, 0, FIXTURE_QWKREQ01_19741256, FIXTURE_001_A3FEAA64, bytes(), "w"));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            entry(
                1_000_000_000_000L,
                0,
                FIXTURE_QWKREQ01_19741256,
                FIXTURE_001_A3FEAA64,
                bytes(),
                "w"));
    assertThrows(
        IllegalArgumentException.class,
        () -> entry(1, -1, FIXTURE_QWKREQ01_19741256, FIXTURE_001_A3FEAA64, bytes(), "w"));
    assertThrows(
        IllegalArgumentException.class,
        () -> entry(1, 101, FIXTURE_QWKREQ01_19741256, FIXTURE_001_A3FEAA64, bytes(), "w"));
    assertThrows(
        NullPointerException.class, () -> entry(null, CORRELATION, OutboxDestination.ASYNC_WORK));
    assertThrows(
        NullPointerException.class, () -> entry(MESSAGE, null, OutboxDestination.ASYNC_WORK));
    assertThrows(NullPointerException.class, () -> entry(MESSAGE, CORRELATION, null));
    assertThrows(
        NullPointerException.class, () -> entry(1, 0, null, FIXTURE_001_A3FEAA64, bytes(), "w"));
    assertThrows(
        IllegalArgumentException.class,
        () -> entry(1, 0, "lower001", FIXTURE_001_A3FEAA64, bytes(), "w"));
    assertThrows(
        NullPointerException.class,
        () -> entry(1, 0, FIXTURE_QWKREQ01_19741256, null, bytes(), "w"));
    assertThrows(
        IllegalArgumentException.class,
        () -> entry(1, 0, FIXTURE_QWKREQ01_19741256, "01A", bytes(), "w"));
    assertThrows(
        NullPointerException.class,
        () -> entry(1, 0, FIXTURE_QWKREQ01_19741256, FIXTURE_001_A3FEAA64, null, "w"));
    assertThrows(
        IllegalArgumentException.class,
        () -> entry(1, 0, FIXTURE_QWKREQ01_19741256, FIXTURE_001_A3FEAA64, new byte[0], "w"));
    assertThrows(
        NullPointerException.class, () -> entryWithTimes(null, NOW.minusSeconds(1), "w", NOW));
    assertThrows(NullPointerException.class, () -> entryWithTimes(NOW, null, "w", NOW));
    assertThrows(NullPointerException.class, () -> entryWithTimes(NOW, NOW, null, NOW));
    assertThrows(IllegalArgumentException.class, () -> entryWithTimes(NOW, NOW, " ", NOW));
    assertThrows(
        IllegalArgumentException.class, () -> entryWithTimes(NOW, NOW, "x".repeat(65), NOW));
    assertThrows(NullPointerException.class, () -> entryWithTimes(NOW, NOW, "w", null));
  }

  @Test
  void requestOwnsBodyExposesEveryFieldAndRejectsEveryInvalidValue() {
    byte[] source = bytes();
    OutboxRequest request = request(source);
    source[0] = 9;
    byte[] returned = request.body();
    returned[0] = 8;
    assertEquals(MESSAGE, request.messageId());
    assertEquals(CORRELATION, request.correlationId());
    assertEquals(OutboxDestination.ASYNC_WORK, request.destination());
    assertEquals(FIXTURE_QWKREQ01_19741256, request.layoutId());
    assertEquals(FIXTURE_001_A3FEAA64, request.layoutVersion());
    assertArrayEquals(bytes(), request.body());
    assertEquals(NOW, request.nextAttemptAt());
    assertEquals(NOW.minusSeconds(1), request.createdAt());
    assertEquals("OutboxRequest[<redacted>]", request.toString());

    assertThrows(
        NullPointerException.class,
        () ->
            request(
                null,
                CORRELATION,
                OutboxDestination.ASYNC_WORK,
                FIXTURE_QWKREQ01_19741256,
                FIXTURE_001_A3FEAA64,
                bytes(),
                NOW,
                NOW));
    assertThrows(
        NullPointerException.class,
        () ->
            request(
                MESSAGE,
                null,
                OutboxDestination.ASYNC_WORK,
                FIXTURE_QWKREQ01_19741256,
                FIXTURE_001_A3FEAA64,
                bytes(),
                NOW,
                NOW));
    assertThrows(
        NullPointerException.class,
        () ->
            request(
                MESSAGE,
                CORRELATION,
                null,
                FIXTURE_QWKREQ01_19741256,
                FIXTURE_001_A3FEAA64,
                bytes(),
                NOW,
                NOW));
    assertThrows(
        NullPointerException.class,
        () ->
            request(
                MESSAGE,
                CORRELATION,
                OutboxDestination.ASYNC_WORK,
                null,
                FIXTURE_001_A3FEAA64,
                bytes(),
                NOW,
                NOW));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            request(
                MESSAGE,
                CORRELATION,
                OutboxDestination.ASYNC_WORK,
                "BAD",
                FIXTURE_001_A3FEAA64,
                bytes(),
                NOW,
                NOW));
    assertThrows(
        NullPointerException.class,
        () ->
            request(
                MESSAGE,
                CORRELATION,
                OutboxDestination.ASYNC_WORK,
                FIXTURE_QWKREQ01_19741256,
                null,
                bytes(),
                NOW,
                NOW));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            request(
                MESSAGE,
                CORRELATION,
                OutboxDestination.ASYNC_WORK,
                FIXTURE_QWKREQ01_19741256,
                "1",
                bytes(),
                NOW,
                NOW));
    assertThrows(
        NullPointerException.class,
        () ->
            request(
                MESSAGE,
                CORRELATION,
                OutboxDestination.ASYNC_WORK,
                FIXTURE_QWKREQ01_19741256,
                FIXTURE_001_A3FEAA64,
                null,
                NOW,
                NOW));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            request(
                MESSAGE,
                CORRELATION,
                OutboxDestination.ASYNC_WORK,
                FIXTURE_QWKREQ01_19741256,
                FIXTURE_001_A3FEAA64,
                new byte[0],
                NOW,
                NOW));
    assertThrows(
        NullPointerException.class,
        () ->
            request(
                MESSAGE,
                CORRELATION,
                OutboxDestination.ASYNC_WORK,
                FIXTURE_QWKREQ01_19741256,
                FIXTURE_001_A3FEAA64,
                bytes(),
                null,
                NOW));
    assertThrows(
        NullPointerException.class,
        () ->
            request(
                MESSAGE,
                CORRELATION,
                OutboxDestination.ASYNC_WORK,
                FIXTURE_QWKREQ01_19741256,
                FIXTURE_001_A3FEAA64,
                bytes(),
                NOW,
                null));
  }

  @Test
  void reportAndIntegrityExceptionsCoverEveryInvariant() {
    assertEquals(2, new OutboxDispatchReport(2, 1, 1, 0).claimed());
    assertEquals(1, new OutboxDispatchReport(2, 1, 1, 0).sent());
    assertEquals(1, new OutboxDispatchReport(2, 1, 1, 0).failed());
    assertEquals(0, new OutboxDispatchReport(2, 1, 1, 0).leaseLost());
    assertThrows(IllegalArgumentException.class, () -> new OutboxDispatchReport(-1, 0, 0, 0));
    assertThrows(IllegalArgumentException.class, () -> new OutboxDispatchReport(0, -1, 0, 0));
    assertThrows(IllegalArgumentException.class, () -> new OutboxDispatchReport(0, 0, -1, 0));
    assertThrows(IllegalArgumentException.class, () -> new OutboxDispatchReport(0, 0, 0, -1));
    assertThrows(IllegalArgumentException.class, () -> new OutboxDispatchReport(1, 0, 0, 0));

    OutboxIntegrityException direct = new OutboxIntegrityException("bounded");
    IllegalStateException cause = new IllegalStateException("synthetic");
    OutboxIntegrityException wrapped = new OutboxIntegrityException("bounded", cause);
    assertEquals("bounded", direct.getMessage());
    assertEquals(cause, wrapped.getCause());
    OutboxSendException sendDirect = new OutboxSendException("bounded send");
    OutboxSendException sendWrapped = new OutboxSendException("bounded send", cause);
    assertEquals("bounded send", sendDirect.getMessage());
    assertEquals(cause, sendWrapped.getCause());
  }

  private static byte[] bytes() {
    return new byte[] {1, 2, 3};
  }

  private static OutboxEntry entry(byte[] body) {
    return entry(1, 0, FIXTURE_QWKREQ01_19741256, FIXTURE_001_A3FEAA64, body, "worker-a");
  }

  private static OutboxEntry entry(
      long id, int attempts, String layout, String version, byte[] body, String worker) {
    return new OutboxEntry(
        id,
        MESSAGE,
        CORRELATION,
        OutboxDestination.ASYNC_WORK,
        layout,
        version,
        body,
        attempts,
        NOW,
        NOW.minusSeconds(1),
        worker,
        NOW.plusSeconds(10));
  }

  private static OutboxEntry entry(UUID message, UUID correlation, OutboxDestination destination) {
    return new OutboxEntry(
        1,
        message,
        correlation,
        destination,
        FIXTURE_QWKREQ01_19741256,
        FIXTURE_001_A3FEAA64,
        bytes(),
        0,
        NOW,
        NOW,
        "w",
        NOW);
  }

  private static OutboxEntry entryWithTimes(
      Instant next, Instant created, String worker, Instant leaseUntil) {
    return new OutboxEntry(
        1,
        MESSAGE,
        CORRELATION,
        OutboxDestination.ASYNC_WORK,
        FIXTURE_QWKREQ01_19741256,
        FIXTURE_001_A3FEAA64,
        bytes(),
        0,
        next,
        created,
        worker,
        leaseUntil);
  }

  private static OutboxRequest request(byte[] body) {
    return request(
        MESSAGE,
        CORRELATION,
        OutboxDestination.ASYNC_WORK,
        FIXTURE_QWKREQ01_19741256,
        FIXTURE_001_A3FEAA64,
        body,
        NOW,
        NOW.minusSeconds(1));
  }

  private static OutboxRequest request(
      UUID message,
      UUID correlation,
      OutboxDestination destination,
      String layout,
      String version,
      byte[] body,
      Instant next,
      Instant created) {
    return new OutboxRequest(
        message, correlation, destination, layout, version, body, next, created);
  }
}
