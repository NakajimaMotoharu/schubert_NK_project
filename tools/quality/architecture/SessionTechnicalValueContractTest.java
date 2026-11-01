package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.messaging.inbound.CommittedFatalInboundException;
import dev.codex.schubert.nk.web.security.LoginFormRejectedException;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SS314 7.2.3/331/321; TECH-VALUE001..008. Synthetic metadata, not authentication or commit. */
final class SessionTechnicalValueContractTest {
  private static final Instant CREATED = Instant.parse("2026-11-01T00:00:00.123456Z");
  private static SessionPayloadIdentity identity() {
    return new SessionPayloadIdentity(new UUID(0, 91), "0".repeat(64), CREATED);
  }
  private static EncryptedSessionPayload payload() {
    return new EncryptedSessionPayload("PUBLIC", new byte[29]);
  }
  private static WebSessionRow row(Instant last, Instant expiry, int ttl, long version) {
    return new WebSessionRow(identity(), payload(), last, expiry, ttl, version);
  }
  @Test
  void technicalValue001InclusiveTtlVersionAndEqualTimesRetainOnlyMetadata() {
    var identity = identity();
    var payload = payload();
    var minimum = new WebSessionRow(identity, payload, CREATED, CREATED, 1, 0);
    assertSame(identity, minimum.identity());
    assertSame(payload, minimum.payload());
    assertEquals(CREATED, minimum.lastAccessedAt());
    assertEquals(CREATED, minimum.expiresAt());
    assertEquals(1, minimum.maxInactiveSeconds());
    assertEquals(0L, minimum.version());
    var maximum = row(CREATED, CREATED.plusSeconds(28800), 28800, 999999999);
    assertEquals(28800, maximum.maxInactiveSeconds());
    assertEquals(999999999L, maximum.version());
    assertEquals(CREATED.plusSeconds(28800), maximum.expiresAt());
    assertEquals("WebSessionRow[REDACTED]", minimum.toString());
    assertEquals("WebSessionRow[REDACTED]", maximum.toString());
  }
  @Test
  void technicalValue002EachSubMicrosecondTimeRejectsWithoutRounding() {
    assertEquals("session row metadata is invalid", assertThrows(IllegalArgumentException.class,
        () -> row(CREATED.plusNanos(1), CREATED.plusSeconds(1), 1, 0)).getMessage());
    assertEquals("session row metadata is invalid", assertThrows(IllegalArgumentException.class,
        () -> row(CREATED, CREATED.plusNanos(1), 1, 0)).getMessage());
  }
  @Test
  void technicalValue003EachReversedTimeRejectsButEqualAndOrderedTimesRemainExact() {
    assertThrows(IllegalArgumentException.class,
        () -> row(CREATED.minusNanos(1000), CREATED, 1, 0));
    assertThrows(IllegalArgumentException.class,
        () -> row(CREATED.plusNanos(1000), CREATED, 1, 0));
    var ordered = row(CREATED.plusNanos(1000), CREATED.plusNanos(2000), 1, 0);
    assertEquals(Instant.parse("2026-11-01T00:00:00.123457Z"), ordered.lastAccessedAt());
    assertEquals(Instant.parse("2026-11-01T00:00:00.123458Z"), ordered.expiresAt());
  }
  @Test
  void technicalValue004TtlOutsideSecondsOneThrough28800Rejects() {
    for (int ttl : List.of(0, 28801, Integer.MIN_VALUE, Integer.MAX_VALUE)) {
      assertEquals("session row metadata is invalid", assertThrows(IllegalArgumentException.class,
          () -> row(CREATED, CREATED, ttl, 0)).getMessage());
    }
  }
  @Test
  void technicalValue005VersionOutsideNineDigitsRejects() {
    for (long version : List.of(-1L, 1000000000L, Long.MIN_VALUE, Long.MAX_VALUE)) {
      assertEquals("session row version is invalid", assertThrows(IllegalArgumentException.class,
          () -> row(CREATED, CREATED, 1, version)).getMessage());
    }
  }
  @Test
  void technicalValue006EachRequiredRowFieldRejectsNull() {
    assertThrows(NullPointerException.class,
        () -> new WebSessionRow(null, payload(), CREATED, CREATED, 1, 0));
    assertThrows(NullPointerException.class,
        () -> new WebSessionRow(identity(), null, CREATED, CREATED, 1, 0));
    assertThrows(NullPointerException.class,
        () -> row(null, CREATED, 1, 0));
    assertThrows(NullPointerException.class,
        () -> row(CREATED, null, 1, 0));
  }
  @Test
  void technicalValue007FormAndOperationRejectionHaveFixedMessagesAndNoCause() {
    var form = new LoginFormRejectedException();
    assertEquals("login form is invalid", form.getMessage());
    assertNull(form.getCause());
    assertEquals(0, form.getSuppressed().length);
    var conflict = new OperationTokenConflictException();
    assertEquals("operation form is unavailable; get a new form explicitly", conflict.getMessage());
    assertEquals(409, conflict.httpStatus());
    assertNull(conflict.getCause());
    assertEquals(0, conflict.getSuppressed().length);
  }
  @Test
  void technicalValue008CommittedFatalMarkerPreservesCauseWithoutDoingIsolation() {
    var empty = new CommittedFatalInboundException(null);
    assertEquals("invalid inbound JMS message was committed to the fatal DLQ", empty.getMessage());
    assertNull(empty.getCause());
    assertEquals(0, empty.getSuppressed().length);
    var publicCause = new AssertionError("PUBLIC_SYNTHETIC_MARKER");
    var retained = new CommittedFatalInboundException(publicCause);
    assertSame(publicCause, retained.getCause());
    assertEquals("invalid inbound JMS message was committed to the fatal DLQ", retained.getMessage());
    assertEquals(0, retained.getSuppressed().length);
  }
}
