package dev.codex.schubert.nk.web.revocation;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.file.InspectorCredentialException;
import dev.codex.schubert.nk.api.file.ServiceCredentialException;
import dev.codex.schubert.nk.web.logging.WebLogSendException;
import dev.codex.schubert.nk.web.messaging.CommittedFatalReplyException;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SS314/331/321/343; REVOKE-VALUE001..010. Public metadata, not actual claims or operations. */
final class RevokeProjectionValueContractTest {
  private static final Instant REQUESTED = Instant.parse("2026-11-01T00:00:00.123456Z");
  private static final UUID OWNER = new UUID(0, 95);
  private static RevocationPayloadIdentity identity() {
    return new RevocationPayloadIdentity(new UUID(0, 94), REQUESTED);
  }
  private static EncryptedRevocationPayload payload() {
    return new EncryptedRevocationPayload("PUBLIC", new byte[29]);
  }
  private static ClaimedRevocation claim(int attempt, Instant expiry, Instant lease) {
    return new ClaimedRevocation(identity(), null, attempt, expiry, OWNER, lease, "PUBLIC");
  }
  @Test
  void revokeValue001UnknownPayloadAndExpiryRemainUnknownAtMinimumAttempt() {
    var identity = identity();
    var lease = REQUESTED.plusSeconds(1);
    var value = new ClaimedRevocation(identity, null, 0, null, OWNER, lease, "PUBLIC");
    assertSame(identity, value.identity());
    assertNull(value.payload());
    assertEquals(0, value.attemptCount());
    assertNull(value.expiresAt());
    assertSame(OWNER, value.leaseOwner());
    assertEquals(lease, value.leaseUntil());
    assertEquals("PUBLIC", value.keyVersion());
    assertEquals("ClaimedRevocation[REDACTED]", value.toString());
  }
  @Test
  void revokeValue002MaximumAttemptAndKnownExpiryPreserveIndependentLease() {
    var payload = payload();
    var expiry = REQUESTED.plusNanos(1000);
    var lease = REQUESTED.plusSeconds(1);
    var value = new ClaimedRevocation(identity(), payload, 100, expiry, OWNER, lease, "PUBLIC");
    assertSame(payload, value.payload());
    assertEquals(100, value.attemptCount());
    assertEquals(Instant.parse("2026-11-01T00:00:00.123457Z"), value.expiresAt());
    assertEquals(Instant.parse("2026-11-01T00:00:01.123456Z"), value.leaseUntil());
    assertEquals("ClaimedRevocation[REDACTED]", value.toString());
  }
  @Test
  void revokeValue003VersionBindingAndSyntaxRejectWithoutDecryptingPayload() {
    assertEquals("claimed revocation key binding is invalid", assertThrows(IllegalArgumentException.class,
        () -> new ClaimedRevocation(identity(), payload(), 0, null, OWNER,
            REQUESTED.plusSeconds(1), "OTHER")).getMessage());
    for (String version : List.of("", "bad value", "a".repeat(17))) {
      assertThrows(IllegalArgumentException.class, () -> new ClaimedRevocation(identity(), null,
          0, null, OWNER, REQUESTED.plusSeconds(1), version));
    }
    assertThrows(NullPointerException.class, () -> new ClaimedRevocation(identity(), null,
        0, null, OWNER, REQUESTED.plusSeconds(1), null));
  }
  @Test
  void revokeValue004AttemptCountRejectsOutsideZeroThroughOneHundred() {
    for (int attempt : List.of(-1, 101, Integer.MIN_VALUE, Integer.MAX_VALUE)) {
      assertEquals("claimed revocation metadata is invalid", assertThrows(IllegalArgumentException.class,
          () -> claim(attempt, null, REQUESTED.plusSeconds(1))).getMessage());
    }
  }
  @Test
  void revokeValue005LeaseOwnerTimeAndIdentityBoundariesReject() {
    for (Instant lease : List.of(REQUESTED, REQUESTED.minusNanos(1000))) {
      assertThrows(IllegalArgumentException.class, () -> claim(0, null, lease));
    }
    assertEquals("revocation time must fit database microseconds", assertThrows(IllegalArgumentException.class,
        () -> claim(0, null, REQUESTED.plusNanos(1))).getMessage());
    assertThrows(NullPointerException.class, () -> claim(0, null, null));
    assertThrows(NullPointerException.class, () -> new ClaimedRevocation(identity(), null,
        0, null, null, REQUESTED.plusSeconds(1), "PUBLIC"));
    assertThrows(NullPointerException.class, () -> new ClaimedRevocation(null, null,
        0, null, OWNER, REQUESTED.plusSeconds(1), "PUBLIC"));
  }
  @Test
  void revokeValue006KnownExpiryIsStrictlyAfterRequestAndAlreadyMicrosecondPrecise() {
    for (Instant expiry : List.of(REQUESTED, REQUESTED.minusNanos(1000))) {
      assertEquals("known revocation expiry is invalid", assertThrows(IllegalArgumentException.class,
          () -> claim(0, expiry, REQUESTED.plusSeconds(1))).getMessage());
    }
    assertEquals("revocation time must fit database microseconds", assertThrows(IllegalArgumentException.class,
        () -> claim(0, REQUESTED.plusNanos(1), REQUESTED.plusSeconds(1))).getMessage());
  }
  @Test
  void revokeValue007FailureCatalogIsClosedOrderedAndArraySnapshotsAreIndependent() {
    String[] expected = {"SESSION_INVALID", "API_REJECTED", "INVALID_RESPONSE", "UNAVAILABLE",
        "KEY_UNAVAILABLE", "PAYLOAD_INVALID", "CRYPTO_UNAVAILABLE"};
    assertArrayEquals(expected, java.util.Arrays.stream(RevocationFailureCode.values())
        .map(Enum::name).toArray(String[]::new));
    var caller = RevocationFailureCode.values();
    caller[0] = RevocationFailureCode.CRYPTO_UNAVAILABLE;
    assertEquals(RevocationFailureCode.SESSION_INVALID, RevocationFailureCode.values()[0]);
    assertThrows(IllegalArgumentException.class, () -> RevocationFailureCode.valueOf("UNKNOWN"));
    assertThrows(NullPointerException.class, () -> RevocationFailureCode.valueOf(null));
  }
  @Test
  void revokeValue008LogSendExceptionsOnlyRetainExplicitCallerMessageAndCause() {
    var plain = new WebLogSendException("PUBLIC_SEND_MARKER");
    assertEquals("PUBLIC_SEND_MARKER", plain.getMessage());
    assertNull(plain.getCause());
    var publicCause = new IllegalArgumentException("PUBLIC_CAUSE");
    var caused = new WebLogSendException("PUBLIC_SEND_MARKER", publicCause);
    assertEquals("PUBLIC_SEND_MARKER", caused.getMessage());
    assertSame(publicCause, caused.getCause());
    assertNull(new WebLogSendException(null).getMessage());
    assertNull(new WebLogSendException(null, null).getCause());
  }
  @Test
  void revokeValue009CommittedReplyMarkerRetainsCauseButPerformsNoCommit() {
    var empty = new CommittedFatalReplyException(null);
    assertEquals("invalid JMS reply was committed to the fatal DLQ", empty.getMessage());
    assertNull(empty.getCause());
    var publicCause = new AssertionError("PUBLIC_REPLY_MARKER");
    var value = new CommittedFatalReplyException(publicCause);
    assertSame(publicCause, value.getCause());
    assertEquals("invalid JMS reply was committed to the fatal DLQ", value.getMessage());
    assertEquals(0, value.getSuppressed().length);
  }
  @Test
  void revokeValue010CredentialErrorsAreFixedValuesNotFileReaders() {
    var service = new ServiceCredentialException();
    assertEquals("service credential cannot be loaded", service.getMessage());
    assertNull(service.getCause());
    assertEquals(0, service.getSuppressed().length);
    var inspector = new InspectorCredentialException();
    assertEquals("inspector credential cannot be loaded", inspector.getMessage());
    assertNull(inspector.getCause());
    assertEquals(0, inspector.getSuppressed().length);
  }
}
