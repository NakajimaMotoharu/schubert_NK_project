package dev.codex.schubert.nk.web.revocation;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** QA-050 and SS314 §10. Synthetic metadata only, with no database or crypto operation. */
final class ClaimedRevocationValueTest {
  private static final Instant REQUESTED = Instant.parse("2026-01-01T00:00:00Z");
  private static final Instant LEASE_END = Instant.parse("2026-01-01T00:00:00.000001Z");
  private static final Instant KNOWN_EXPIRY = Instant.parse("2026-01-01T00:00:00.000010Z");
  private static final UUID OWNER = new UUID(0, 2);
  private static final String VERSION = "v1";
  private static final RevocationPayloadIdentity IDENTITY =
      new RevocationPayloadIdentity(new UUID(0, 1), REQUESTED);

  @Test // PT-OPS-RVR-CLAIM001
  void boundedAttemptsAndOptionalFieldsKeepTheClaimedRowValue() {
    var unknown = claimed(0, null, LEASE_END);
    assertEquals(0, unknown.attemptCount());
    assertNull(unknown.payload());
    assertNull(unknown.expiresAt());

    var payload = new EncryptedRevocationPayload(VERSION, new byte[29]);
    var known =
        new ClaimedRevocation(IDENTITY, payload, 100, KNOWN_EXPIRY, OWNER, LEASE_END, VERSION);
    assertEquals(IDENTITY, known.identity());
    assertSame(payload, known.payload());
    assertEquals(100, known.attemptCount());
    assertEquals(KNOWN_EXPIRY, known.expiresAt());
    assertEquals(OWNER, known.leaseOwner());
    assertEquals(LEASE_END, known.leaseUntil());
    assertEquals(VERSION, known.keyVersion());
    assertEquals("ClaimedRevocation[REDACTED]", known.toString());

    var equal =
        new ClaimedRevocation(IDENTITY, payload, 100, KNOWN_EXPIRY, OWNER, LEASE_END, VERSION);
    assertEquals(known, equal);
    assertNotEquals(known, claimed(100, KNOWN_EXPIRY, LEASE_END));
    var records = new HashMap<ClaimedRevocation, String>();
    records.put(known, "known");
    assertEquals("known", records.get(equal));
  }

  @Test // PT-OPS-RVR-CLAIM002
  void rejectsAttemptsOutsideTheRangeAndInvalidLeaseOrExpiryTimes() {
    for (int count : new int[] {-1, 101}) {
      assertThrows(IllegalArgumentException.class, () -> claimed(count, null, LEASE_END));
    }
    for (var at : List.of(REQUESTED.minusNanos(1_000), REQUESTED, REQUESTED.plusNanos(1))) {
      assertThrows(IllegalArgumentException.class, () -> claimed(0, null, at));
      assertThrows(IllegalArgumentException.class, () -> claimed(0, at, LEASE_END));
    }
  }

  @Test // PT-OPS-RVR-CLAIM003
  void rejectsMissingIdentityOwnerTimesOrInvalidKeyBinding() {
    assertThrows(
        NullPointerException.class,
        () -> new ClaimedRevocation(null, null, 0, null, OWNER, LEASE_END, VERSION));
    assertThrows(
        NullPointerException.class,
        () -> new ClaimedRevocation(IDENTITY, null, 0, null, null, LEASE_END, VERSION));
    assertThrows(NullPointerException.class, () -> claimed(0, null, null));
    assertThrows(
        NullPointerException.class,
        () -> new ClaimedRevocation(IDENTITY, null, 0, null, OWNER, LEASE_END, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new ClaimedRevocation(IDENTITY, null, 0, null, OWNER, LEASE_END, "_unknown"));

    var payload = new EncryptedRevocationPayload("v2", new byte[29]);
    assertThrows(
        IllegalArgumentException.class,
        () -> new ClaimedRevocation(IDENTITY, payload, 0, null, OWNER, LEASE_END, VERSION));
  }

  private static ClaimedRevocation claimed(int count, Instant expiry, Instant leaseEnd) {
    return new ClaimedRevocation(IDENTITY, null, count, expiry, OWNER, leaseEnd, VERSION);
  }
}
