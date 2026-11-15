package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-AUT-VALUE001/002; SS314/352/451; public row IDs and opaque synthetic ciphertext only. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class AuthContextValueContractTest {
  @Test
  void value001RowBindingsAndDefensiveCiphertextRemainReliableMapKeys() {
    var first = new AuthContextIdentity(UUID.fromString("c1000000-0000-0000-0000-000000000001"), 7);
    var equal = new AuthContextIdentity(UUID.fromString("c1000000-0000-0000-0000-000000000001"), 7);
    var otherUser =
        new AuthContextIdentity(UUID.fromString("c1000000-0000-0000-0000-000000000001"), 8);
    var otherRow =
        new AuthContextIdentity(UUID.fromString("c1000000-0000-0000-0000-000000000002"), 7);
    assertNotSame(first, equal);
    assertTrue(first.equals(first));
    assertTrue(first.equals(equal));
    assertTrue(equal.equals(first));
    assertFalse(first.equals(otherUser));
    assertFalse(first.equals(otherRow));
    assertFalse(first.equals(null));
    assertFalse(first.equals("row"));
    assertEquals(
        "AuthContextIdentity[sessionId=c1000000-0000-0000-0000-000000000001, userId=7]",
        first.toString());
    var owners = new HashMap<AuthContextIdentity, String>();
    owners.put(first, "owner");
    assertEquals("owner", owners.get(equal));
    assertNull(owners.get(otherUser));
    assertNull(owners.get(otherRow));
    owners.put(otherUser, "other");
    assertEquals(2, owners.size());
    assertEquals("other", owners.get(otherUser));

    byte[] caller = new byte[102];
    Arrays.fill(caller, (byte) 7);
    byte[] expected = new byte[102];
    Arrays.fill(expected, (byte) 7);
    var cipherA = new EncryptedAuthContext("v1", caller);
    var cipherB = new EncryptedAuthContext("v1", caller);
    var otherVersion = new EncryptedAuthContext("v2", caller);
    // Java record array components retain array identity; each constructor defensively clones.
    assertTrue(cipherA.equals(cipherA));
    assertFalse(cipherA.equals(cipherB));
    assertFalse(cipherA.equals(otherVersion));
    assertFalse(cipherA.equals(null));
    assertFalse(cipherA.equals(first));
    var ciphertexts = new HashMap<EncryptedAuthContext, String>();
    ciphertexts.put(cipherA, "cipher-a");
    ciphertexts.put(cipherB, "cipher-b");
    Arrays.fill(caller, (byte) 0);
    byte[] exposed = cipherA.ciphertext();
    Arrays.fill(exposed, (byte) 9);
    assertArrayEquals(expected, cipherA.ciphertext());
    assertArrayEquals(expected, cipherB.ciphertext());
    assertEquals(2, ciphertexts.size());
    assertEquals("cipher-a", ciphertexts.get(cipherA));
    assertEquals("cipher-b", ciphertexts.get(cipherB));
    assertEquals("EncryptedAuthContext[keyVersion=v1, ciphertext=<redacted>]", cipherA.toString());
  }

  @Test
  void value002CryptoReasonVocabularyLookupAndValuesCopyRemainClosed() {
    assertEquals(
        List.of("INVALID", "KEY_UNAVAILABLE", "CRYPTO_UNAVAILABLE"),
        Arrays.stream(AuthContextCryptoException.Reason.values()).map(Enum::name).toList());
    assertSame(
        AuthContextCryptoException.Reason.INVALID,
        AuthContextCryptoException.Reason.valueOf("INVALID"));
    assertSame(
        AuthContextCryptoException.Reason.KEY_UNAVAILABLE,
        AuthContextCryptoException.Reason.valueOf("KEY_UNAVAILABLE"));
    assertSame(
        AuthContextCryptoException.Reason.CRYPTO_UNAVAILABLE,
        AuthContextCryptoException.Reason.valueOf("CRYPTO_UNAVAILABLE"));
    var exposed = AuthContextCryptoException.Reason.values();
    exposed[0] = AuthContextCryptoException.Reason.CRYPTO_UNAVAILABLE;
    assertEquals(
        List.of("INVALID", "KEY_UNAVAILABLE", "CRYPTO_UNAVAILABLE"),
        Arrays.stream(AuthContextCryptoException.Reason.values()).map(Enum::name).toList());
    for (String unknown : List.of("UNKNOWN", "", "invalid", " INVALID ")) {
      assertThrows(
          IllegalArgumentException.class, () -> AuthContextCryptoException.Reason.valueOf(unknown));
    }
    assertThrows(NullPointerException.class, () -> AuthContextCryptoException.Reason.valueOf(null));
  }
}
