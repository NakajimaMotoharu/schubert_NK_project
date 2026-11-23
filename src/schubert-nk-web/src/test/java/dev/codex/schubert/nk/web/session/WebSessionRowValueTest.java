package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** SS314 §7.2.3 and SS331 §9.1. Standalone row values only. */
final class WebSessionRowValueTest {
  private static final Instant CREATED = Instant.parse("2026-02-03T04:05:06.123456Z");
  private static final Instant ACCESSED = CREATED.plusNanos(1000);
  private static final Instant EXPIRY = ACCESSED.plusNanos(1000);
  private static final SessionPayloadIdentity IDENTITY =
      new SessionPayloadIdentity(new UUID(4, 2), "a".repeat(64), CREATED);
  private static final EncryptedSessionPayload PAYLOAD =
      new EncryptedSessionPayload("fixture-v1", new byte[29]);
  private static final String METADATA_INVALID = "session row metadata is invalid";
  private static final String VERSION_INVALID = "session row version is invalid";
  private static final long MAX_VERSION = 999_999_999L;

  /** PT-WEB-ROW001. */
  @Test
  void row001InclusiveBoundsAndEqualTimestampsAreAccepted() {
    var minimum = new WebSessionRow(IDENTITY, PAYLOAD, CREATED, CREATED, 1, 0);
    assertSame(IDENTITY, minimum.identity());
    assertSame(PAYLOAD, minimum.payload());
    assertEquals(CREATED, minimum.lastAccessedAt());
    assertEquals(CREATED, minimum.expiresAt());
    assertEquals(1, minimum.maxInactiveSeconds());
    assertEquals(0, minimum.version());
    var maximum = new WebSessionRow(IDENTITY, PAYLOAD, ACCESSED, EXPIRY, 28800, MAX_VERSION);
    assertEquals(28800, maximum.maxInactiveSeconds());
    assertEquals(MAX_VERSION, maximum.version());
    assertEquals(ACCESSED, maximum.lastAccessedAt());
    assertEquals(EXPIRY, maximum.expiresAt());
  }

  /** PT-WEB-ROW002. */
  @Test
  void row002RejectsSubMicrosecondAndOutOfOrderMetadataSeparately() {
    List<Executable> invalid =
        List.of(
            () -> new WebSessionRow(IDENTITY, PAYLOAD, ACCESSED.plusNanos(1), EXPIRY, 1, 0),
            () -> new WebSessionRow(IDENTITY, PAYLOAD, ACCESSED, EXPIRY.plusNanos(1), 1, 0),
            () -> new WebSessionRow(IDENTITY, PAYLOAD, CREATED.minusNanos(1000), EXPIRY, 1, 0),
            () -> new WebSessionRow(IDENTITY, PAYLOAD, ACCESSED, CREATED, 1, 0));
    for (Executable input : invalid) {
      assertEquals(
          METADATA_INVALID, assertThrows(IllegalArgumentException.class, input).getMessage());
    }
  }

  /** PT-WEB-ROW003. */
  @Test
  void row003RejectsIdleAndVersionOutsideTheirOwnInclusiveBounds() {
    for (int idle : new int[] {0, 28801}) {
      assertEquals(
          METADATA_INVALID,
          assertThrows(
                  IllegalArgumentException.class,
                  () -> new WebSessionRow(IDENTITY, PAYLOAD, ACCESSED, EXPIRY, idle, 0))
              .getMessage());
    }
    for (long version : new long[] {-1, 1_000_000_000L}) {
      assertEquals(
          VERSION_INVALID,
          assertThrows(
                  IllegalArgumentException.class,
                  () -> new WebSessionRow(IDENTITY, PAYLOAD, ACCESSED, EXPIRY, 1, version))
              .getMessage());
    }
  }

  /** PT-WEB-ROW004. */
  @Test
  void row004EveryRequiredReferenceRejectsNullAtItsOwnBoundary() {
    assertEquals(
        "identity",
        assertThrows(
                NullPointerException.class,
                () -> new WebSessionRow(null, PAYLOAD, ACCESSED, EXPIRY, 1, 0))
            .getMessage());
    assertEquals(
        "payload",
        assertThrows(
                NullPointerException.class,
                () -> new WebSessionRow(IDENTITY, null, ACCESSED, EXPIRY, 1, 0))
            .getMessage());
    assertEquals(
        "lastAccessedAt",
        assertThrows(
                NullPointerException.class,
                () -> new WebSessionRow(IDENTITY, PAYLOAD, null, EXPIRY, 1, 0))
            .getMessage());
    assertEquals(
        "expiresAt",
        assertThrows(
                NullPointerException.class,
                () -> new WebSessionRow(IDENTITY, PAYLOAD, ACCESSED, null, 1, 0))
            .getMessage());
  }

  /** PT-WEB-ROW005. */
  @Test
  void row005ValueEqualityAndGeneralDiagnosticHaveIndependentExpectations() {
    var first = new WebSessionRow(IDENTITY, PAYLOAD, ACCESSED, EXPIRY, 1, 0);
    var duplicate = new WebSessionRow(IDENTITY, PAYLOAD, ACCESSED, EXPIRY, 1, 0);
    var updated = new WebSessionRow(IDENTITY, PAYLOAD, ACCESSED, EXPIRY, 1, 1);
    assertEquals(first, duplicate);
    assertEquals(first.hashCode(), duplicate.hashCode());
    assertNotEquals(first, updated);
    assertEquals("WebSessionRow[REDACTED]", first.toString());
  }
}
