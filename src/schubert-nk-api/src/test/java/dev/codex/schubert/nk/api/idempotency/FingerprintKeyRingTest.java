package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-IDEM-003 current/previous/unknown key and tamper cases. */
class FingerprintKeyRingTest {
  @Test
  void currentAndPreviousKeysVerifyWhileUnknownAndTamperedDenyClosed() {
    CanonicalRequest request = request("target");
    byte[] current = key((byte) 1);
    byte[] previous = key((byte) 2);
    try (FingerprintKeyRing ring = new FingerprintKeyRing("k2", current, "k1", previous)) {
      Fingerprint currentFingerprint = ring.calculate(request);
      Fingerprint previousFingerprint =
          new Fingerprint("k1", OperationFingerprint.INSTANCE.calculate(request, previous));
      Fingerprint unknown = new Fingerprint("k0", currentFingerprint.digest());
      byte[] changed = currentFingerprint.digest();
      changed[0] ^= 1;

      assertEquals("k2", currentFingerprint.keyVersion());
      assertEquals(FingerprintVerification.MATCH, ring.verify(currentFingerprint, request));
      assertEquals(FingerprintVerification.MATCH, ring.verify(previousFingerprint, request));
      assertEquals(FingerprintVerification.KEY_UNAVAILABLE, ring.verify(unknown, request));
      assertEquals(
          FingerprintVerification.MISMATCH, ring.verify(new Fingerprint("k2", changed), request));
      assertTrue(ring.matches(currentFingerprint, request));
      assertTrue(ring.matches(previousFingerprint, request));
      assertFalse(ring.matches(unknown, request));
      assertFalse(ring.matches(new Fingerprint("k2", changed), request));
      assertFalse(ring.matches(currentFingerprint, request("different")));
      assertEquals("Fingerprint[<redacted>]", currentFingerprint.toString());
    }
    assertNotEquals(0, current[0]);
    assertNotEquals(0, previous[0]);
  }

  @Test
  void fingerprintDefensivelyCopiesAndValidates() {
    byte[] digest = new byte[32];
    digest[0] = 7;
    Fingerprint fingerprint = new Fingerprint("v1", digest);
    digest[0] = 9;
    byte[] returned = fingerprint.digest();
    returned[0] = 8;

    assertArrayEquals(arrayWithFirst((byte) 7), fingerprint.digest());
    assertThrows(NullPointerException.class, () -> new Fingerprint(null, new byte[32]));
    assertThrows(NullPointerException.class, () -> new Fingerprint("v1", null));
    assertThrows(
        IllegalArgumentException.class, () -> new Fingerprint("bad version", new byte[32]));
    assertThrows(IllegalArgumentException.class, () -> new Fingerprint("v1", new byte[31]));
  }

  @Test
  void keyRingInvariantsNullContractsAndCloseAreEnforced() {
    byte[] key = key((byte) 3);
    assertThrows(NullPointerException.class, () -> new FingerprintKeyRing(null, key, null, null));
    assertThrows(NullPointerException.class, () -> new FingerprintKeyRing("v1", null, null, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new FingerprintKeyRing("bad version", key, null, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new FingerprintKeyRing("v1", new byte[31], null, null));
    assertThrows(
        IllegalArgumentException.class, () -> new FingerprintKeyRing("v1", key, "v0", null));
    assertThrows(
        IllegalArgumentException.class, () -> new FingerprintKeyRing("v1", key, null, key));
    assertThrows(
        IllegalArgumentException.class,
        () -> new FingerprintKeyRing("v1", key, "bad version", key));
    assertThrows(
        IllegalArgumentException.class,
        () -> new FingerprintKeyRing("v1", key, "v0", new byte[31]));
    assertThrows(
        IllegalArgumentException.class, () -> new FingerprintKeyRing("v1", key, "v1", key));

    FingerprintKeyRing noPrevious = new FingerprintKeyRing("v1", key, null, null);
    assertThrows(NullPointerException.class, () -> noPrevious.matches(null, request("t")));
    assertThrows(NullPointerException.class, () -> noPrevious.verify(null, request("t")));
    Fingerprint valid = noPrevious.calculate(request("t"));
    assertThrows(NullPointerException.class, () -> noPrevious.matches(valid, null));
    assertThrows(NullPointerException.class, () -> noPrevious.verify(valid, null));
    assertFalse(noPrevious.matches(new Fingerprint("v0", valid.digest()), request("t")));
    noPrevious.close();
    noPrevious.close();
    assertThrows(IllegalStateException.class, () -> noPrevious.calculate(request("t")));
    assertThrows(IllegalStateException.class, () -> noPrevious.matches(valid, request("t")));
    assertThrows(IllegalStateException.class, () -> noPrevious.verify(valid, request("t")));
  }

  private static CanonicalRequest request(String target) {
    return new CanonicalRequest("7", "QSTREQ01", "001", target, List.of());
  }

  private static byte[] key(byte value) {
    byte[] key = new byte[32];
    java.util.Arrays.fill(key, value);
    return key;
  }

  private static byte[] arrayWithFirst(byte value) {
    byte[] array = new byte[32];
    array[0] = value;
    return array;
  }
}
