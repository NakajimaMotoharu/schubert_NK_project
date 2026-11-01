package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** NK-MSG-002/DAT009; SS324/352; STORED-METADATA001..006. No key or cipher operations. */
final class StoredMetadataContractTest {
  @Test
  void storedMetadata001FingerprintRetainsVersionAndCopiesInputAndEveryReturnedDigest() {
    for (String version : List.of("A", "0", "v1", "A._-0123456789ab")) {
      byte[] input = new byte[32];
      Arrays.fill(input, (byte) 0x33);
      var value = new Fingerprint(version, input);
      input[0] = 0x44;
      byte[] expected = new byte[32];
      Arrays.fill(expected, (byte) 0x33);
      assertArrayEquals(expected, value.digest());
      byte[] first = value.digest();
      first[31] = 0x55;
      assertArrayEquals(expected, value.digest());
      assertNotSame(first, value.digest());
      assertEquals(version, value.keyVersion());
      assertEquals("Fingerprint[keyVersion=" + version + ", digest=<redacted>]", value.toString());
    }
  }

  @Test
  void storedMetadata002FingerprintRejectsNullBadVersionAndEveryDigestLengthBoundary() {
    assertThrows(NullPointerException.class, () -> new Fingerprint(null, new byte[32]));
    assertThrows(NullPointerException.class, () -> new Fingerprint("v1", null));
    for (String version : List.of("", "_v1", "-v1", ".v1", "v 1", "v/1", "v\n", "あ",
        "a".repeat(17))) {
      assertEquals("fingerprint metadata is invalid", assertThrows(IllegalArgumentException.class,
          () -> new Fingerprint(version, new byte[32])).getMessage());
    }
    for (int length : new int[] {0, 31, 33}) {
      assertEquals("fingerprint metadata is invalid", assertThrows(IllegalArgumentException.class,
          () -> new Fingerprint("v1", new byte[length])).getMessage());
    }
  }

  @Test
  void storedMetadata003CiphertextMetadataCopiesBothLengthLimitsAndRetainsPublicVersion() {
    assertEquals(29, EncryptedResponseSnapshot.MINIMUM_CIPHERTEXT_BYTES);
    assertEquals(1_050_000, EncryptedResponseSnapshot.MAXIMUM_CIPHERTEXT_BYTES);
    for (int size : new int[] {29, 30, 1_049_999, 1_050_000}) {
      byte[] input = new byte[size];
      input[0] = 0x33;
      input[size - 1] = 0x55;
      var value = new EncryptedResponseSnapshot("A._-0123456789ab", input);
      input[0] = 0x44;
      byte[] first = value.ciphertext();
      assertEquals(size, first.length);
      assertEquals(0x33, first[0]);
      assertEquals(0x55, first[size - 1]);
      first[size - 1] = 0;
      assertEquals(0x55, value.ciphertext()[size - 1]);
      assertNotSame(first, value.ciphertext());
      assertEquals("A._-0123456789ab", value.keyVersion());
      assertEquals("EncryptedResponseSnapshot[keyVersion=A._-0123456789ab, ciphertext=<redacted>]",
          value.toString());
    }
    assertEquals("v1", new EncryptedResponseSnapshot("v1", new byte[29]).keyVersion());
  }

  @Test
  void storedMetadata004CiphertextMetadataRejectsNullVersionSyntaxAndOutsideLimits() {
    assertThrows(NullPointerException.class, () -> new EncryptedResponseSnapshot(null, new byte[29]));
    assertThrows(NullPointerException.class, () -> new EncryptedResponseSnapshot("v1", null));
    for (String version : List.of("", "_v1", "-v1", ".v1", "v 1", "v/1", "v\n", "あ",
        "a".repeat(17))) {
      assertEquals("response snapshot key version is invalid",
          assertThrows(IllegalArgumentException.class,
              () -> new EncryptedResponseSnapshot(version, new byte[29])).getMessage());
    }
    for (int size : new int[] {0, 28, 1_050_001}) {
      assertEquals("response snapshot ciphertext length is invalid",
          assertThrows(IllegalArgumentException.class,
              () -> new EncryptedResponseSnapshot("v1", new byte[size])).getMessage());
    }
  }

  @Test
  void storedMetadata005SavedMessageAndOutcomeAreRetainedWithoutGrantingExecution() {
    var message = new UUID(0, 77);
    var inProgress = InboxExecution.inProgress();
    var value = new BoundInboxExecution(message, inProgress);
    assertSame(message, value.sourceMessageId());
    assertSame(inProgress, value.execution());
    assertEquals(InboxExecutionStatus.IN_PROGRESS, value.execution().status());
    assertEquals("BoundInboxExecution[REDACTED]", value.toString());
    assertThrows(NullPointerException.class, () -> new BoundInboxExecution(null, inProgress));
    assertThrows(NullPointerException.class, () -> new BoundInboxExecution(message, null));
  }

  @Test
  void storedMetadata006FingerprintVerificationIsOnlyAClosedThreeValueCatalog() {
    assertArrayEquals(new String[] {"MATCH", "MISMATCH", "KEY_UNAVAILABLE"},
        Arrays.stream(FingerprintVerification.values()).map(Enum::name).toArray(String[]::new));
    assertSame(FingerprintVerification.MATCH, FingerprintVerification.valueOf("MATCH"));
    assertSame(FingerprintVerification.MISMATCH, FingerprintVerification.valueOf("MISMATCH"));
    assertSame(FingerprintVerification.KEY_UNAVAILABLE, FingerprintVerification.valueOf("KEY_UNAVAILABLE"));
    assertThrows(IllegalArgumentException.class, () -> FingerprintVerification.valueOf("UNKNOWN"));
    assertThrows(NullPointerException.class, () -> FingerprintVerification.valueOf(null));
  }
}
