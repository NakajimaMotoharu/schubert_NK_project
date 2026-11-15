package dev.codex.schubert.nk.web.revocation;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * PT-REVOKE-VALUE001..004; QA050/SS331352: synthetic identity/bytes only, no retry/crypto/key/DB.
 */
final class RevocationValueContractTest {
  private static final String VERSION = "v1";
  private static final String STORED = "owned-value";
  private static final UUID ID = new UUID(0x0001020304050607L, 0x08090a0b0c0d0e0fL);
  private static final Instant REQUESTED = Instant.ofEpochSecond(-1, 123456000);
  private static final RevocationPayloadIdentity IDENTITY =
      new RevocationPayloadIdentity(ID, REQUESTED);
  private static final String AAD_HEX =
      "0000000a7765622d7265766f6b650000003073636875626572745f7765625f73657373696f6e2e70656e64696e675f636f6e746578745f7265766f636174696f6e7300000010000102030405060708090a0b0c0d0e0f0000000cffffffffffffffff075bca000000000101000000027631";

  @Test
  void revokevalue001IdentityUsesAllUuidAndTimeBitsAndIndependentSixFieldAad() {
    var equal = new RevocationPayloadIdentity(ID, REQUESTED);
    assertEquals(ID, IDENTITY.id());
    assertEquals(REQUESTED, IDENTITY.requestedAt());
    assertEquals(IDENTITY, equal);
    assertEquals(IDENTITY.hashCode(), equal.hashCode());
    assertEquals(STORED, Map.of(IDENTITY, STORED).get(equal));
    assertNotEquals(IDENTITY, new RevocationPayloadIdentity(new UUID(0, 1), REQUESTED));
    assertNotEquals(IDENTITY, new RevocationPayloadIdentity(ID, Instant.EPOCH));
    assertNotEquals(IDENTITY, null);
    assertNotEquals(IDENTITY, VERSION);
    assertEquals("RevocationPayloadIdentity[REDACTED]", IDENTITY.toString());
    byte[] expected = HexFormat.of().parseHex(AAD_HEX);
    assertArrayEquals(expected, IDENTITY.aad(VERSION));
    byte[] returned = IDENTITY.aad(VERSION);
    Arrays.fill(returned, (byte) 0);
    assertArrayEquals(expected, IDENTITY.aad(VERSION));
    for (Instant at : List.of(Instant.EPOCH, Instant.ofEpochSecond(1, 999999000)))
      assertEquals(at, new RevocationPayloadIdentity(ID, at).requestedAt());
    assertThrows(
        IllegalArgumentException.class,
        () -> new RevocationPayloadIdentity(ID, Instant.EPOCH.plusNanos(1)));
    assertThrows(NullPointerException.class, () -> new RevocationPayloadIdentity(null, REQUESTED));
    assertThrows(NullPointerException.class, () -> new RevocationPayloadIdentity(ID, null));
    assertThrows(NullPointerException.class, () -> IDENTITY.aad(null));
  }

  @Test
  void revokevalue002CiphertextOwnershipBoundsAndArrayReferenceEqualityRemainExplicit() {
    for (int length : List.of(29, 30, 115, 116)) {
      byte[] input = new byte[length];
      input[0] = 7;
      var value = new EncryptedRevocationPayload(VERSION, input);
      input[0] = 9;
      byte[] first = value.ciphertext();
      assertEquals(length, first.length);
      assertEquals(7, first[0]);
      first[0] = 11;
      assertEquals(7, value.ciphertext()[0]);
      assertNotSame(first, value.ciphertext());
      assertEquals(VERSION, value.keyVersion());
      assertEquals(value, value);
      assertEquals(STORED, Map.of(value, STORED).get(value));
      int originalHash = value.hashCode();
      value.ciphertext()[0] = 22;
      assertEquals(originalHash, value.hashCode());
      assertNotEquals(value, new EncryptedRevocationPayload(VERSION, value.ciphertext()));
      assertNotEquals(value, new EncryptedRevocationPayload("v2", value.ciphertext()));
      assertNotEquals(value, null);
      assertNotEquals(value, VERSION);
      assertEquals("EncryptedRevocationPayload[REDACTED]", value.toString());
    }
    for (String version : List.of("A", "A".repeat(16), "A._-09"))
      assertEquals(version, new EncryptedRevocationPayload(version, new byte[29]).keyVersion());
    for (String version : List.of("", "_bad", "A".repeat(17), "é", "v1 ", "v1/"))
      assertThrows(
          IllegalArgumentException.class,
          () -> new EncryptedRevocationPayload(version, new byte[29]));
    for (int length : List.of(0, 28, 117))
      assertThrows(
          IllegalArgumentException.class,
          () -> new EncryptedRevocationPayload(VERSION, new byte[length]));
    assertThrows(
        NullPointerException.class, () -> new EncryptedRevocationPayload(null, new byte[29]));
    assertThrows(NullPointerException.class, () -> new EncryptedRevocationPayload(VERSION, null));
  }

  @Test
  void revokevalue003FailureCodesHaveFixedLookupDefensiveValuesAndRetryDiagnostic() {
    var values =
        List.of(
            RevocationFailureCode.SESSION_INVALID,
            RevocationFailureCode.API_REJECTED,
            RevocationFailureCode.INVALID_RESPONSE,
            RevocationFailureCode.UNAVAILABLE,
            RevocationFailureCode.KEY_UNAVAILABLE,
            RevocationFailureCode.PAYLOAD_INVALID,
            RevocationFailureCode.CRYPTO_UNAVAILABLE);
    var names =
        List.of(
            "SESSION_INVALID",
            "API_REJECTED",
            "INVALID_RESPONSE",
            "UNAVAILABLE",
            "KEY_UNAVAILABLE",
            "PAYLOAD_INVALID",
            "CRYPTO_UNAVAILABLE");
    assertEquals(values, List.of(RevocationFailureCode.values()));
    for (int index = 0; index < names.size(); index++) {
      assertEquals(names.get(index), values.get(index).name());
      assertSame(values.get(index), RevocationFailureCode.valueOf(names.get(index)));
    }
    var copy = RevocationFailureCode.values();
    copy[0] = RevocationFailureCode.UNAVAILABLE;
    assertSame(RevocationFailureCode.SESSION_INVALID, RevocationFailureCode.values()[0]);
    for (String unknown : List.of("", "UNKNOWN", "session_invalid", "SESSION_INVALID "))
      assertThrows(IllegalArgumentException.class, () -> RevocationFailureCode.valueOf(unknown));
    assertThrows(NullPointerException.class, () -> RevocationFailureCode.valueOf(null));
    var retry = new RevocationRetryException();
    assertEquals("retained revocation retry infrastructure unavailable", retry.getMessage());
    assertNull(retry.getCause());
    assertEquals(0, retry.getSuppressed().length);
  }

  @Test
  void revokevalue004PayloadReasonsHaveExactDiagnosticNamesAndDefensiveValues() {
    var values =
        List.of(
            RevocationPayloadException.Reason.PAYLOAD_INVALID,
            RevocationPayloadException.Reason.KEY_UNAVAILABLE,
            RevocationPayloadException.Reason.CRYPTO_UNAVAILABLE);
    var names = List.of("PAYLOAD_INVALID", "KEY_UNAVAILABLE", "CRYPTO_UNAVAILABLE");
    assertEquals(values, List.of(RevocationPayloadException.Reason.values()));
    for (int index = 0; index < names.size(); index++) {
      assertEquals(names.get(index), values.get(index).name());
      assertSame(values.get(index), RevocationPayloadException.Reason.valueOf(names.get(index)));
      var failure = new RevocationPayloadException(values.get(index));
      assertEquals(
          "revocation encrypted payload rejected: " + names.get(index), failure.getMessage());
      assertSame(values.get(index), failure.reason());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
    var copy = RevocationPayloadException.Reason.values();
    copy[0] = RevocationPayloadException.Reason.KEY_UNAVAILABLE;
    assertSame(
        RevocationPayloadException.Reason.PAYLOAD_INVALID,
        RevocationPayloadException.Reason.values()[0]);
    for (String unknown : List.of("", "UNKNOWN", "payload_invalid", "PAYLOAD_INVALID "))
      assertThrows(
          IllegalArgumentException.class, () -> RevocationPayloadException.Reason.valueOf(unknown));
    assertThrows(NullPointerException.class, () -> RevocationPayloadException.Reason.valueOf(null));
  }
}
