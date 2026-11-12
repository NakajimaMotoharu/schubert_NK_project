package dev.codex.schubert.nk.web.revocation;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.nio.charset.StandardCharsets;
import java.security.ProviderException;
import java.security.SecureRandom;
import java.security.Security;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.Test;

/** Independent JCA/length-prefix oracle; only public synthetic vectors. 016077/RERUN003/PG-D359. */
final class RevocationPayloadCodecTest {
  private static final UUID ID = UUID.fromString("00112233-4455-6677-8899-aabbccddeeff");
  private static final Instant REQUESTED = Instant.parse("2026-09-08T00:00:00.123456Z");
  private static final RevocationPayloadIdentity IDENTITY =
      new RevocationPayloadIdentity(ID, REQUESTED);
  private static final String CONTEXT = "0123456789abcdef".repeat(4);
  private static final AuthenticationContext AUTH = AuthenticationContext.of(CONTEXT);
  private static final byte[] KEY =
      HexFormat.of().parseHex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f");
  private static final byte[] OLD =
      HexFormat.of().parseHex("202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f");
  private static final byte[] NONCE = HexFormat.of().parseHex("a0a1a2a3a4a5a6a7a8a9aaab");

  @Test
  void rerun003aIndependentGoldenAndDefensiveCopies() throws Exception {
    byte[] caller = KEY.clone();
    byte[] previous = OLD.clone();
    var random = new FixedRandom();
    try (var codec = new RevocationPayloadCodec("v2", caller, "v1", previous, random)) {
      Arrays.fill(caller, (byte) 0);
      Arrays.fill(previous, (byte) 0);
      var value = codec.encrypt(IDENTITY, AUTH);
      byte[] golden = envelope("v2", KEY, fields("v2"), ascii(CONTEXT));
      assertEquals("v2", value.keyVersion());
      assertArrayEquals(golden, value.ciphertext());
      assertArrayEquals(new byte[12], random.last);
      byte[] exposed = value.ciphertext();
      Arrays.fill(exposed, (byte) 0);
      assertArrayEquals(golden, value.ciphertext());
      var copied = new EncryptedRevocationPayload("v2", golden);
      Arrays.fill(golden, (byte) 0);
      assertArrayEquals(value.ciphertext(), copied.ciphertext());
      assertEquals(AUTH, codec.decrypt(IDENTITY, copied));
      assertEquals(AUTH, codec.decrypt(IDENTITY, independent("v1", OLD, CONTEXT)));
      assertEquals("EncryptedRevocationPayload[REDACTED]", value.toString());
    }
    assertEquals(ID, IDENTITY.id());
    assertEquals(REQUESTED, IDENTITY.requestedAt());
    assertEquals("RevocationPayloadIdentity[REDACTED]", IDENTITY.toString());
    for (String version : List.of("a", "abcdefghijklmnop")) {
      try (var codec = fixed(version, KEY, null, null)) {
        var value = codec.encrypt(IDENTITY, AUTH);
        assertEquals(100 + version.length(), value.ciphertext().length);
        assertArrayEquals(
            envelope(version, KEY, fields(version), ascii(CONTEXT)), value.ciphertext());
        assertEquals(AUTH, codec.decrypt(IDENTITY, independent(version, KEY, CONTEXT)));
      }
    }
  }

  @Test
  void rerun003bUnknownKeyAndEveryAadFieldRejectWithoutReplacement() throws Exception {
    try (var codec = fixed("v2", KEY, "v1", OLD)) {
      reason(
          RevocationPayloadException.Reason.KEY_UNAVAILABLE,
          () -> codec.decrypt(IDENTITY, independent("v0", OLD, CONTEXT)));
      reason(
          RevocationPayloadException.Reason.PAYLOAD_INVALID,
          () -> codec.decrypt(IDENTITY, independent("v2", OLD, CONTEXT)));
      var old = independent("v1", OLD, CONTEXT);
      reason(
          RevocationPayloadException.Reason.PAYLOAD_INVALID,
          () -> codec.decrypt(IDENTITY, new EncryptedRevocationPayload("v2", old.ciphertext())));
      for (int index = 0; index < 6; index++) {
        var aadFields = fields("v2");
        aadFields.get(index)[0] ^= 1;
        invalid(codec, envelope("v2", KEY, aadFields, ascii(CONTEXT)));
      }
      // A fully valid session-purpose cryptogram must not become a revoke context.
      var sessionPurpose = fields("v2");
      sessionPurpose.set(0, ascii("web-session"));
      sessionPurpose.set(1, ascii("schubert_web_session.web_http_sessions"));
      invalid(codec, envelope("v2", KEY, sessionPurpose, ascii(CONTEXT)));
      var good = independent("v2", KEY, CONTEXT);
      for (var other :
          List.of(
              new RevocationPayloadIdentity(new UUID(0, 9), REQUESTED),
              new RevocationPayloadIdentity(ID, REQUESTED.plusNanos(1000)))) {
        reason(RevocationPayloadException.Reason.PAYLOAD_INVALID, () -> codec.decrypt(other, good));
      }
    }
    try (var codec = fixed("v2", KEY, null, null)) {
      reason(
          RevocationPayloadException.Reason.KEY_UNAVAILABLE,
          () -> codec.decrypt(IDENTITY, independent("v1", OLD, CONTEXT)));
    }
  }

  @Test
  void rerun003cEnvelopeLengthHeaderNonceTagAndPlaintextReject() throws Exception {
    byte[] good = envelope("v2", KEY, fields("v2"), ascii(CONTEXT));
    try (var codec = fixed("v2", KEY, null, null)) {
      for (int size : new int[] {29, 100, 101, 103, 116}) invalid(codec, Arrays.copyOf(good, size));
      for (int offset = 0; offset < 7; offset++) {
        byte[] bad = good.clone();
        bad[offset] = 0;
        invalid(codec, bad);
      }
      for (int length : new int[] {0, 17, 255}) {
        byte[] bad = good.clone();
        bad[7] = (byte) length;
        invalid(codec, bad);
      }
      for (byte value : new byte[] {'!', (byte) 0xff}) {
        byte[] bad = good.clone();
        bad[8] = value;
        invalid(codec, bad);
      }
      for (int offset = 10; offset < good.length; offset++) {
        byte[] bad = good.clone();
        bad[offset] ^= 1;
        invalid(codec, bad);
      }
      for (String plain :
          List.of("", "a".repeat(63), "a".repeat(65), "A".repeat(64), "/".repeat(64)))
        invalid(codec, envelope("v2", KEY, fields("v2"), ascii(plain)));
      byte[] nonAscii = ascii(CONTEXT);
      nonAscii[1] = (byte) 0xff;
      invalid(codec, envelope("v2", KEY, fields("v2"), nonAscii));
    }
  }

  @Test
  void rerun003dNullContractsAndConstructorBoundaries() {
    assertThrows(NullPointerException.class, () -> new RevocationPayloadIdentity(null, REQUESTED));
    assertThrows(NullPointerException.class, () -> new RevocationPayloadIdentity(ID, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new RevocationPayloadIdentity(ID, REQUESTED.plusNanos(1)));
    assertThrows(
        NullPointerException.class, () -> new EncryptedRevocationPayload(null, new byte[29]));
    assertThrows(NullPointerException.class, () -> new EncryptedRevocationPayload("v2", null));
    for (int size : new int[] {0, 28, 117})
      assertThrows(
          IllegalArgumentException.class,
          () -> new EncryptedRevocationPayload("v2", new byte[size]));
    for (String version : List.of("", "!", "abcdefghijklmnopq", "é", "v2 ")) {
      assertThrows(IllegalArgumentException.class, () -> fixed(version, KEY, null, null));
      assertThrows(IllegalArgumentException.class, () -> fixed("v2", KEY, version, OLD));
    }
    assertThrows(NullPointerException.class, () -> fixed(null, KEY, null, null));
    assertThrows(NullPointerException.class, () -> fixed("v2", null, null, null));
    for (int length : new int[] {0, 31, 33}) {
      assertThrows(IllegalArgumentException.class, () -> fixed("v2", new byte[length], null, null));
      assertThrows(IllegalArgumentException.class, () -> fixed("v2", KEY, "v1", new byte[length]));
    }
    assertThrows(IllegalArgumentException.class, () -> fixed("v2", KEY, null, OLD));
    assertThrows(IllegalArgumentException.class, () -> fixed("v2", KEY, "v1", null));
    assertThrows(IllegalArgumentException.class, () -> fixed("v2", KEY, "v2", OLD));
    assertThrows(
        NullPointerException.class, () -> new RevocationPayloadCodec("v2", KEY, null, null, null));
    assertThrows(NullPointerException.class, () -> new RevocationPayloadException(null));
    try (var codec = fixed("v2", KEY, null, null)) {
      assertThrows(NullPointerException.class, () -> codec.encrypt(null, AUTH));
      assertThrows(NullPointerException.class, () -> codec.encrypt(IDENTITY, null));
      assertThrows(
          NullPointerException.class,
          () -> codec.decrypt(null, new EncryptedRevocationPayload("v2", new byte[29])));
      assertThrows(NullPointerException.class, () -> codec.decrypt(IDENTITY, null));
    }
  }

  @Test
  void rerun003eProviderRandomFailuresRedactAndErase() throws Exception {
    var cryptogram = independent("v2", KEY, CONTEXT);
    var provider = Security.getProvider("SunJCE");
    int position = Arrays.asList(Security.getProviders()).indexOf(provider) + 1;
    assertTrue(position > 0);
    Security.removeProvider("SunJCE");
    try (var codec = fixed("v2", KEY, null, null)) {
      reason(
          RevocationPayloadException.Reason.CRYPTO_UNAVAILABLE,
          () -> codec.encrypt(IDENTITY, AUTH));
      reason(
          RevocationPayloadException.Reason.PAYLOAD_INVALID,
          () -> codec.decrypt(IDENTITY, cryptogram));
    } finally {
      assertNotEquals(-1, Security.insertProviderAt(provider, position));
    }
    var random = new FixedRandom();
    random.fail = true;
    try (var codec = new RevocationPayloadCodec("v2", KEY, null, null, random)) {
      reason(
          RevocationPayloadException.Reason.CRYPTO_UNAVAILABLE,
          () -> codec.encrypt(IDENTITY, AUTH));
      assertArrayEquals(new byte[12], random.last);
    }
  }

  @Test
  void rerun003fHundredConcurrentFreshNoncesAndOwnedClose() throws Exception {
    var codec = new RevocationPayloadCodec("v2", KEY, null, null);
    var pool = Executors.newVirtualThreadPerTaskExecutor();
    try {
      var futures = new ArrayList<Future<EncryptedRevocationPayload>>();
      for (int i = 0; i < 100; i++) futures.add(pool.submit(() -> codec.encrypt(IDENTITY, AUTH)));
      var nonces = new HashSet<String>();
      for (var future : futures) {
        var value = future.get(20, TimeUnit.SECONDS);
        assertEquals(AUTH, codec.decrypt(IDENTITY, value));
        assertTrue(
            nonces.add(HexFormat.of().formatHex(Arrays.copyOfRange(value.ciphertext(), 10, 22))));
      }
      assertEquals(100, nonces.size());
    } finally {
      pool.shutdownNow();
      if (!pool.awaitTermination(10, TimeUnit.SECONDS)) {
        throw new AssertionError("PUBLIC crypto worker termination unconfirmed");
      }
      codec.close();
      codec.close();
    }
    assertThrows(IllegalStateException.class, () -> codec.encrypt(IDENTITY, AUTH));
    assertThrows(
        IllegalStateException.class,
        () -> codec.decrypt(IDENTITY, new EncryptedRevocationPayload("v2", new byte[29])));
  }

  @Test
  void rerun003gCloseWaitsForBorrowerAndRestartReadsPrevious() throws Exception {
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    var closing = new CountDownLatch(1);
    var random =
        new FixedRandom() {
          private static final long serialVersionUID = 1L;

          @Override
          public void nextBytes(byte[] output) {
            super.nextBytes(output);
            entered.countDown();
            try {
              assertTrue(release.await(20, TimeUnit.SECONDS));
            } catch (InterruptedException failure) {
              Thread.currentThread().interrupt();
              throw new AssertionError(failure);
            }
          }
        };
    var codec = new RevocationPayloadCodec("v2", KEY, "v1", OLD, random);
    var pool = Executors.newFixedThreadPool(2);
    try {
      var encrypt = pool.submit(() -> codec.encrypt(IDENTITY, AUTH));
      assertTrue(entered.await(20, TimeUnit.SECONDS));
      var close =
          pool.submit(
              () -> {
                closing.countDown();
                codec.close();
              });
      try {
        assertTrue(closing.await(20, TimeUnit.SECONDS));
        assertFalse(close.isDone());
      } finally {
        release.countDown();
      }
      var value = encrypt.get(20, TimeUnit.SECONDS);
      close.get(20, TimeUnit.SECONDS);
      assertArrayEquals(new byte[12], random.last);
      assertArrayEquals(envelope("v2", KEY, fields("v2"), ascii(CONTEXT)), value.ciphertext());
      assertThrows(IllegalStateException.class, () -> codec.decrypt(IDENTITY, value));
      try (var restarted = new RevocationPayloadCodec("v3", OLD, "v2", KEY)) {
        assertEquals(AUTH, restarted.decrypt(IDENTITY, value));
        assertEquals("v3", restarted.encrypt(IDENTITY, AUTH).keyVersion());
      }
    } finally {
      release.countDown();
      pool.shutdownNow();
      if (!pool.awaitTermination(10, TimeUnit.SECONDS)) {
        throw new AssertionError("PUBLIC crypto worker termination unconfirmed");
      }
      codec.close();
    }
  }

  private static RevocationPayloadCodec fixed(
      String version, byte[] key, String previous, byte[] old) {
    return new RevocationPayloadCodec(version, key, previous, old, new FixedRandom());
  }

  private static EncryptedRevocationPayload independent(
      String version, byte[] key, String plaintext) throws Exception {
    return new EncryptedRevocationPayload(
        version, envelope(version, key, fields(version), ascii(plaintext)));
  }

  private static List<byte[]> fields(String version) throws Exception {
    var time = new ByteArrayOutputStream();
    try (var data = new DataOutputStream(time)) {
      data.writeLong(1788825600L);
      data.writeInt(123456000);
    }
    return new ArrayList<>(
        List.of(
            ascii("web-revoke"),
            ascii("schubert_web_session.pending_context_revocations"),
            HexFormat.of().parseHex("00112233445566778899aabbccddeeff"),
            time.toByteArray(),
            new byte[] {1},
            ascii(version)));
  }

  private static byte[] envelope(String version, byte[] key, List<byte[]> aad, byte[] plaintext)
      throws Exception {
    var bound = new ByteArrayOutputStream();
    try (var data = new DataOutputStream(bound)) {
      for (byte[] field : aad) {
        data.writeInt(field.length);
        data.write(field);
      }
    }
    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "AES"), new GCMParameterSpec(128, NONCE));
    cipher.updateAAD(bound.toByteArray());
    var result = new ByteArrayOutputStream();
    try (var data = new DataOutputStream(result)) {
      data.write(ascii("NKENC1"));
      data.writeByte(1);
      data.writeByte(version.length());
      data.write(ascii(version));
      data.write(NONCE);
      data.write(cipher.doFinal(plaintext));
    }
    return result.toByteArray();
  }

  private static byte[] ascii(String value) {
    return value.getBytes(StandardCharsets.US_ASCII);
  }

  private static void invalid(RevocationPayloadCodec codec, byte[] bytes) {
    reason(
        RevocationPayloadException.Reason.PAYLOAD_INVALID,
        () -> codec.decrypt(IDENTITY, new EncryptedRevocationPayload("v2", bytes)));
  }

  private static void reason(
      RevocationPayloadException.Reason expected,
      org.junit.jupiter.api.function.Executable action) {
    var failure = assertThrows(RevocationPayloadException.class, action);
    assertEquals(expected, failure.reason());
    assertEquals("revocation encrypted payload rejected: " + expected, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static class FixedRandom extends SecureRandom {
    private static final long serialVersionUID = 1L;
    byte[] last;
    boolean fail;

    @Override
    public void nextBytes(byte[] output) {
      last = output;
      System.arraycopy(NONCE, 0, output, 0, NONCE.length);
      if (fail) throw new ProviderException("private-test-only-marker");
    }
  }
}
