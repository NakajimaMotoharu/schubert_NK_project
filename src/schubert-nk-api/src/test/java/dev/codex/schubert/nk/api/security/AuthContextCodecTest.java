package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.nio.charset.StandardCharsets;
import java.security.Provider;
import java.security.SecureRandom;
import java.security.Security;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.parallel.Isolated;

/** PT-AUT-005-C01..04; independent JCE/DataOutputStream oracle; all material is synthetic. */
@Isolated("JCA failure fixture temporarily removes providers and restores their exact order")
final class AuthContextCodecTest {
  private static final AuthContextIdentity IDENTITY =
      new AuthContextIdentity(UUID.fromString("c1000000-0000-0000-0000-000000000001"), 7);
  private static final AuthenticationContext RAW = AuthenticationContext.of("a".repeat(64));

  @Test
  void bug036CallerMonitorCannotBlockEncryptionDecryptionOrClose() throws Exception {
    byte[] expected =
        independentEnvelope(
            "v1", key(0), IDENTITY, RAW.wireValue().getBytes(StandardCharsets.US_ASCII));
    var codec = new AuthContextCodec("v1", key(0), null, null, new FixedNonce());
    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      synchronized (codec) {
        executor
            .submit(
                () -> {
                  assertArrayEquals(expected, codec.encrypt(IDENTITY, RAW).ciphertext());
                  assertEquals(
                      RAW, codec.decrypt(IDENTITY, new EncryptedAuthContext("v1", expected)));
                  codec.close();
                  assertThrows(IllegalStateException.class, () -> codec.encrypt(IDENTITY, RAW));
                  return 0;
                })
            .get(5, java.util.concurrent.TimeUnit.SECONDS);
      }
    } finally {
      codec.close();
    }
  }

  @Test
  void independentEnvelopeAadAndDefensiveCopiesMatchExactly() throws Exception {
    byte[] key = key(0);
    byte[] expected =
        independentEnvelope(
            "v1", key, IDENTITY, RAW.wireValue().getBytes(StandardCharsets.US_ASCII));
    assertArrayEquals(independentAad(IDENTITY, "v1"), IDENTITY.aad("v1"));
    try (var codec = new AuthContextCodec("v1", key, null, null, new FixedNonce())) {
      Arrays.fill(key, (byte) 0);
      EncryptedAuthContext actual = codec.encrypt(IDENTITY, RAW);
      assertEquals("v1", actual.keyVersion());
      assertArrayEquals(expected, actual.ciphertext());
      assertEquals(RAW, codec.decrypt(IDENTITY, actual));
      byte[] returned = actual.ciphertext();
      returned[0] = 0;
      assertArrayEquals(expected, actual.ciphertext());
      byte[] supplied = expected.clone();
      EncryptedAuthContext copied = new EncryptedAuthContext("v1", supplied);
      supplied[0] = 0;
      assertArrayEquals(expected, copied.ciphertext());
      assertEquals("EncryptedAuthContext[keyVersion=v1, ciphertext=<redacted>]", copied.toString());
      assertEquals(
          IDENTITY.sessionId(), new AuthContextIdentity(IDENTITY.sessionId(), 7).sessionId());
      assertEquals(7, IDENTITY.userId());
    }
  }

  @Test
  void currentPreviousAndEveryIdentityBindingFailClosedOnMismatch() throws Exception {
    EncryptedAuthContext old =
        new EncryptedAuthContext(
            "v1",
            independentEnvelope(
                "v1", key(0), IDENTITY, RAW.wireValue().getBytes(StandardCharsets.US_ASCII)));
    byte[] previous = key(0);
    try (var codec = new AuthContextCodec("v2", key(1), "v1", previous)) {
      Arrays.fill(previous, (byte) 0);
      assertEquals(RAW, codec.decrypt(IDENTITY, old));
      var current = codec.encrypt(IDENTITY, RAW);
      assertEquals("v2", current.keyVersion());
      assertEquals(RAW, codec.decrypt(IDENTITY, current));
      assertReason(
          AuthContextCryptoException.Reason.INVALID,
          () -> codec.decrypt(new AuthContextIdentity(IDENTITY.sessionId(), 8), old));
      assertReason(
          AuthContextCryptoException.Reason.INVALID,
          () ->
              codec.decrypt(
                  new AuthContextIdentity(
                      UUID.fromString("c1000000-0000-0000-0000-000000000002"), 7),
                  old));
    }
    try (var codec = new AuthContextCodec("v2", key(1), null, null)) {
      assertReason(
          AuthContextCryptoException.Reason.KEY_UNAVAILABLE, () -> codec.decrypt(IDENTITY, old));
    }
    try (var codec = new AuthContextCodec("v1", key(1), null, null)) {
      assertReason(AuthContextCryptoException.Reason.INVALID, () -> codec.decrypt(IDENTITY, old));
    }
  }

  @Test
  void envelopeMutationsAndAuthenticatedNonContextPlaintextAreRejected() throws Exception {
    byte[] golden =
        independentEnvelope(
            "v1", key(0), IDENTITY, RAW.wireValue().getBytes(StandardCharsets.US_ASCII));
    try (var codec = new AuthContextCodec("v1", key(0), null, null)) {
      for (int offset : new int[] {0, 1, 2, 3, 4, 5, 6, 8, 10, golden.length - 1}) {
        byte[] changed = golden.clone();
        changed[offset] ^= 1;
        assertReason(
            AuthContextCryptoException.Reason.INVALID,
            () -> codec.decrypt(IDENTITY, new EncryptedAuthContext("v1", changed)));
      }
      for (int length : new int[] {0, 17}) {
        byte[] changed = golden.clone();
        changed[7] = (byte) length;
        assertReason(
            AuthContextCryptoException.Reason.INVALID,
            () -> codec.decrypt(IDENTITY, new EncryptedAuthContext("v1", changed)));
      }
      assertReason(
          AuthContextCryptoException.Reason.INVALID,
          () -> codec.decrypt(IDENTITY, new EncryptedAuthContext("v2", golden)));
      assertReason(
          AuthContextCryptoException.Reason.INVALID,
          () ->
              codec.decrypt(IDENTITY, new EncryptedAuthContext("v1", Arrays.copyOf(golden, 101))));
      for (byte fill : new byte[] {'A', 'g', (byte) 0xff}) {
        byte[] plaintext = new byte[64];
        Arrays.fill(plaintext, fill);
        var value =
            new EncryptedAuthContext("v1", independentEnvelope("v1", key(0), IDENTITY, plaintext));
        assertReason(
            AuthContextCryptoException.Reason.INVALID, () -> codec.decrypt(IDENTITY, value));
      }
    }
  }

  @Test
  void lengthVersionKeyAndNullInvariantsIncludeBothEndpointsAndClose() throws Exception {
    assertThrows(NullPointerException.class, () -> new AuthContextIdentity(null, 1));
    assertThrows(
        IllegalArgumentException.class, () -> new AuthContextIdentity(IDENTITY.sessionId(), 0));
    assertThrows(
        IllegalArgumentException.class,
        () -> new AuthContextIdentity(IDENTITY.sessionId(), 1_000_000_000_000L));
    assertEquals(
        999_999_999_999L, new AuthContextIdentity(IDENTITY.sessionId(), 999_999_999_999L).userId());
    assertThrows(NullPointerException.class, () -> IDENTITY.aad(null));
    assertThrows(IllegalArgumentException.class, () -> IDENTITY.aad("?"));
    assertThrows(NullPointerException.class, () -> new EncryptedAuthContext(null, new byte[101]));
    assertThrows(NullPointerException.class, () -> new EncryptedAuthContext("v1", null));
    assertThrows(
        IllegalArgumentException.class, () -> new EncryptedAuthContext("?", new byte[101]));
    assertThrows(
        IllegalArgumentException.class, () -> new EncryptedAuthContext("v1", new byte[100]));
    assertThrows(
        IllegalArgumentException.class, () -> new EncryptedAuthContext("v1", new byte[117]));
    assertEquals(101, new EncryptedAuthContext("v1", new byte[101]).ciphertext().length);
    assertEquals(116, new EncryptedAuthContext("v1", new byte[116]).ciphertext().length);
    assertThrows(NullPointerException.class, () -> new AuthContextCodec(null, key(0), null, null));
    assertThrows(NullPointerException.class, () -> new AuthContextCodec("v1", null, null, null));
    assertThrows(
        NullPointerException.class, () -> new AuthContextCodec("v1", key(0), null, null, null));
    assertThrows(
        IllegalArgumentException.class, () -> new AuthContextCodec("v1", new byte[31], null, null));
    assertThrows(
        IllegalArgumentException.class, () -> new AuthContextCodec("v1", key(0), "v0", null));
    assertThrows(
        IllegalArgumentException.class, () -> new AuthContextCodec("v1", key(0), null, key(0)));
    assertThrows(
        IllegalArgumentException.class, () -> new AuthContextCodec("v1", key(0), "v1", key(0)));
    assertThrows(
        IllegalArgumentException.class,
        () -> new AuthContextCodec("v1", key(0), "v0", new byte[33]));
    for (String version : List.of("", "?", "v".repeat(17))) {
      assertThrows(
          IllegalArgumentException.class, () -> new AuthContextCodec(version, key(0), null, null));
      assertThrows(
          IllegalArgumentException.class,
          () -> new AuthContextCodec("v1", key(0), version, key(0)));
    }
    assertThrows(NullPointerException.class, () -> new AuthContextCryptoException(null));
    for (String version : List.of("v", "v".repeat(16))) {
      var codec = new AuthContextCodec(version, key(0), null, null);
      try {
        var value = codec.encrypt(IDENTITY, RAW);
        assertEquals(100 + version.length(), value.ciphertext().length);
        assertEquals(RAW, codec.decrypt(IDENTITY, value));
        assertThrows(NullPointerException.class, () -> codec.encrypt(null, RAW));
        assertThrows(NullPointerException.class, () -> codec.encrypt(IDENTITY, null));
        assertThrows(NullPointerException.class, () -> codec.decrypt(null, value));
        assertThrows(NullPointerException.class, () -> codec.decrypt(IDENTITY, null));
      } finally {
        codec.close();
      }
      codec.close();
      assertThrows(IllegalStateException.class, () -> codec.encrypt(IDENTITY, RAW));
      assertThrows(
          IllegalStateException.class,
          () -> codec.decrypt(IDENTITY, new EncryptedAuthContext(version, new byte[101])));
    }
  }

  @Test
  void jcaUnavailabilityIsTypedAndProvidersAreRestored() throws Exception {
    var value =
        new EncryptedAuthContext(
            "v1",
            independentEnvelope(
                "v1", key(0), IDENTITY, RAW.wireValue().getBytes(StandardCharsets.US_ASCII)));
    try (var codec = new AuthContextCodec("v1", key(0), null, null, new FixedNonce())) {
      Provider[] original = Security.getProviders();
      try {
        for (Provider provider : original) Security.removeProvider(provider.getName());
        assertReason(
            AuthContextCryptoException.Reason.CRYPTO_UNAVAILABLE,
            () -> codec.encrypt(IDENTITY, RAW));
        assertReason(
            AuthContextCryptoException.Reason.CRYPTO_UNAVAILABLE,
            () -> codec.decrypt(IDENTITY, value));
      } finally {
        for (int i = 0; i < original.length; i++) Security.insertProviderAt(original[i], i + 1);
      }
      assertArrayEquals(original, Security.getProviders());
    }
  }

  @Test
  void concurrentEncryptionHasDistinctNoncesAndCorrectRowBinding() throws Exception {
    try (var codec = new AuthContextCodec("v1", key(0), null, null);
        var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      var results = new ArrayList<Future<EncryptedAuthContext>>();
      for (int i = 0; i < 100; i++)
        results.add(executor.submit(() -> codec.encrypt(IDENTITY, RAW)));
      var nonces = new HashSet<String>();
      for (var result : results) {
        EncryptedAuthContext value = result.get();
        assertEquals(RAW, codec.decrypt(IDENTITY, value));
        byte[] bytes = value.ciphertext();
        nonces.add(HexFormat.of().formatHex(Arrays.copyOfRange(bytes, 10, 22)));
      }
      assertEquals(100, nonces.size());
    }
  }

  private static void assertReason(
      AuthContextCryptoException.Reason reason, org.junit.jupiter.api.function.Executable action) {
    AuthContextCryptoException failure = assertThrows(AuthContextCryptoException.class, action);
    assertEquals(reason, failure.reason());
    assertEquals("authentication context cryptography failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static byte[] independentAad(AuthContextIdentity identity, String version)
      throws Exception {
    ByteArrayOutputStream bytes = new ByteArrayOutputStream();
    try (DataOutputStream output = new DataOutputStream(bytes)) {
      for (String part :
          new String[] {
            "SCHUBERT-NK-AUTHCTX-v1",
            "schubert.auth_sessions",
            identity.sessionId().toString(),
            Long.toString(identity.userId()),
            "1",
            version
          }) {
        byte[] value = part.getBytes(StandardCharsets.US_ASCII);
        output.writeInt(value.length);
        output.write(value);
      }
    }
    return bytes.toByteArray();
  }

  private static byte[] independentEnvelope(
      String version, byte[] key, AuthContextIdentity identity, byte[] plaintext) throws Exception {
    byte[] nonce = new byte[12];
    Arrays.fill(nonce, (byte) 42);
    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "AES"), new GCMParameterSpec(128, nonce));
    cipher.updateAAD(independentAad(identity, version));
    byte[] encrypted = cipher.doFinal(plaintext);
    ByteArrayOutputStream bytes = new ByteArrayOutputStream();
    try (DataOutputStream output = new DataOutputStream(bytes)) {
      output.write("NKENC1".getBytes(StandardCharsets.US_ASCII));
      output.writeByte(1);
      output.writeByte(version.length());
      output.write(version.getBytes(StandardCharsets.US_ASCII));
      output.write(nonce);
      output.write(encrypted);
    }
    return bytes.toByteArray();
  }

  private static byte[] key(int offset) {
    byte[] value = new byte[32];
    for (int i = 0; i < value.length; i++) value[i] = (byte) (i + offset);
    return value;
  }

  private static final class FixedNonce extends SecureRandom {
    private static final long serialVersionUID = 1L;

    @Override
    public void nextBytes(byte[] bytes) {
      Arrays.fill(bytes, (byte) 42);
    }
  }
}
