package dev.codex.schubert.nk.web.session;

import static dev.codex.schubert.nk.web.session.SessionAttributeCodecTest.CSRF;
import static dev.codex.schubert.nk.web.session.SessionAttributeCodecTest.TIME;
import static dev.codex.schubert.nk.web.session.SessionAttributeCodecTest.attributes;
import static dev.codex.schubert.nk.web.session.SessionAttributeCodecTest.bytes;
import static dev.codex.schubert.nk.web.session.SessionAttributeCodecTest.check;
import static dev.codex.schubert.nk.web.session.SessionAttributeCodecTest.json;
import static dev.codex.schubert.nk.web.session.SessionPayloadException.Reason.CRYPTO_UNAVAILABLE;
import static dev.codex.schubert.nk.web.session.SessionPayloadException.Reason.KEY_UNAVAILABLE;
import static dev.codex.schubert.nk.web.session.SessionPayloadException.Reason.PAYLOAD_INVALID;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
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

/**
 * NK-WEB-001; FUN-001/AUT-001..004; UI226/242; SS314/331/352; SSC-039/PG-D-095/PT-WEB-016..023.
 * Independent DataOutputStream AAD and JCE golden envelopes; all values synthetic, not credentials.
 */
class SessionPayloadCodecTest {
  private static final String FIXTURE_READER_F734AAEA = "reader";
  private static final UUID ID = UUID.fromString("00112233-4455-6677-8899-aabbccddeeff");
  private static final Instant CREATED = Instant.parse("2026-09-08T00:00:00.123456Z");
  private static final SessionPayloadIdentity IDENTITY =
      new SessionPayloadIdentity(ID, "a".repeat(64), CREATED);
  private static final byte[] KEY =
      HexFormat.of().parseHex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f");
  private static final byte[] OLD =
      HexFormat.of().parseHex("202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f");
  private static final byte[] NONCE = HexFormat.of().parseHex("a0a1a2a3a4a5a6a7a8a9aaab");

  @Test
  void web016IndependentEnvelopeAndDefensiveOwnership() throws Exception {
    byte[] caller = KEY.clone();
    byte[] previous = OLD.clone();
    var random = new FixedRandom();
    try (var codec = new SessionPayloadCodec("v2", caller, "v1", previous, random)) {
      Arrays.fill(caller, (byte) 99);
      Arrays.fill(previous, (byte) 99);
      for (boolean authenticated : List.of(false, true)) {
        byte[] expected = envelope("v2", KEY, aad("v2"), plain(authenticated));
        var encrypted = codec.encrypt(IDENTITY, sample(authenticated));
        assertEquals("v2", encrypted.keyVersion());
        assertArrayEquals(expected, encrypted.ciphertext());
        assertArrayEquals(new byte[12], random.last);
        byte[] exposed = encrypted.ciphertext();
        Arrays.fill(exposed, (byte) 0);
        assertArrayEquals(expected, encrypted.ciphertext());
        var copy = new EncryptedSessionPayload("v2", expected);
        Arrays.fill(expected, (byte) 0);
        assertArrayEquals(encrypted.ciphertext(), copy.ciphertext());
        checkSample(codec.decrypt(IDENTITY, copy), authenticated);
        checkSample(
            codec.decrypt(IDENTITY, independent("v2", KEY, plain(authenticated))), authenticated);
        assertEquals("EncryptedSessionPayload[REDACTED]", copy.toString());
      }
      checkSample(codec.decrypt(IDENTITY, independent("v1", OLD, plain(true))), true);
    }
    assertEquals(ID, IDENTITY.id());
    assertEquals("a".repeat(64), IDENTITY.sessionIdHash());
    assertEquals(CREATED, IDENTITY.createdAt());
    assertEquals("SessionPayloadIdentity[REDACTED]", IDENTITY.toString());
  }

  @Test
  void web017CurrentPreviousAndUnknownKeyFailClosed() throws Exception {
    try (var codec = fixed("v2", KEY, "v1", OLD)) {
      assertEquals("v2", codec.encrypt(IDENTITY, sample(false)).keyVersion());
      checkSample(codec.decrypt(IDENTITY, independent("v1", OLD, plain(true))), true);
      reason(KEY_UNAVAILABLE, () -> codec.decrypt(IDENTITY, independent("v0", OLD, plain(false))));
      reason(PAYLOAD_INVALID, () -> codec.decrypt(IDENTITY, independent("v2", OLD, plain(false))));
      var old = independent("v1", OLD, plain(false));
      reason(
          PAYLOAD_INVALID,
          () -> codec.decrypt(IDENTITY, new EncryptedSessionPayload("v2", old.ciphertext())));
    }
    try (var currentOnly = fixed("v2", KEY, null, null)) {
      reason(
          KEY_UNAVAILABLE,
          () -> currentOnly.decrypt(IDENTITY, independent("v1", OLD, plain(false))));
    }
    for (String version : List.of("a", "abcdefghijklmnop")) {
      try (var codec = fixed(version, KEY, null, null)) {
        assertArrayEquals(
            envelope(version, KEY, aad(version), plain(false)),
            codec.encrypt(IDENTITY, sample(false)).ciphertext());
        checkSample(codec.decrypt(IDENTITY, independent(version, KEY, plain(false))), false);
      }
    }
  }

  @Test
  void tokv206IndependentLegacyPlaintextStillDecryptsUnderEitherKey() throws Exception {
    // JSON oracle is the independent literal builder, never production encode().
    byte[] legacy =
        bytes(
            new String(plain(true), StandardCharsets.UTF_8)
                .replace("\"formatVersion\":2", "\"formatVersion\":1"));
    try (var codec = fixed("v2", KEY, "v1", OLD)) {
      for (String version : List.of("v1", "v2")) {
        var value =
            codec.decrypt(IDENTITY, independent(version, version.equals("v1") ? OLD : KEY, legacy));
        checkSample(value, true);
        assertTrue(value.operationTokens().getFirst().completedAt().isEmpty());
        assertEquals("v2", codec.encrypt(IDENTITY, value).keyVersion());
      }
    }
  }

  @Test
  void web018EnvelopeAndEveryAadFieldMutationReject() throws Exception {
    byte[] valid = envelope("v2", KEY, aad("v2"), plain(true));
    try (var codec = fixed("v2", KEY, null, null)) {
      for (int length : new int[] {29, 36, 37, valid.length - 1})
        invalid(codec, Arrays.copyOf(valid, length));
      for (int offset : new int[] {0, 1, 2, 3, 4, 5, 6, 8, 9}) {
        byte[] bad = valid.clone();
        bad[offset] = 0;
        invalid(codec, bad);
      }
      for (int length : new int[] {0, 16, 17, 255}) {
        byte[] bad = valid.clone();
        bad[7] = (byte) length;
        if (length == 16) bad = Arrays.copyOf(bad, 37);
        invalid(codec, bad);
      }
      byte[] nonAscii = valid.clone();
      nonAscii[8] = (byte) 0xff;
      invalid(codec, nonAscii);
      for (int offset = 10; offset < valid.length; offset++) {
        byte[] bad = valid.clone();
        bad[offset] ^= 1;
        invalid(codec, bad);
      }
      invalid(codec, Arrays.copyOf(valid, valid.length + 1));
      for (int field = 0; field < 7; field++) {
        var fields = fields("v2");
        fields.get(field)[0] ^= 1;
        invalid(codec, envelope("v2", KEY, lp(fields), plain(false)));
      }
      var encrypted = new EncryptedSessionPayload("v2", valid);
      for (var other :
          List.of(
              new SessionPayloadIdentity(new UUID(0, 9), "a".repeat(64), CREATED),
              new SessionPayloadIdentity(ID, "b".repeat(64), CREATED),
              new SessionPayloadIdentity(ID, "a".repeat(64), CREATED.plusNanos(1000))))
        reason(PAYLOAD_INVALID, () -> codec.decrypt(other, encrypted));
    }
  }

  @Test
  void web019AuthenticatedInvalidJsonAndSizeBoundariesReject() throws Exception {
    try (var codec = fixed("v2", KEY, null, null)) {
      for (byte[] bad :
          List.of(
              new byte[0],
              new byte[] {(byte) 0xff},
              bytes("{}"),
              bytes("{\"formatVersion\":1,\"operationTokens\":[],\"password\":\"private-marker\"}"),
              bytes("null"),
              bytes(
                  json(true, FIXTURE_READER_F734AAEA, "USER", null, null, 1)
                      .replace(TIME, "private-marker")),
              new byte[16385]))
        reason(PAYLOAD_INVALID, () -> codec.decrypt(IDENTITY, independent("v2", KEY, bad)));
      byte[] max = Arrays.copyOf(plain(false), 16384);
      Arrays.fill(max, plain(false).length, max.length, (byte) ' ');
      checkSample(codec.decrypt(IDENTITY, independent("v2", KEY, max)), false);
      try (var longVersion = fixed("abcdefghijklmnop", KEY, null, null)) {
        var maxEnvelope = independent("abcdefghijklmnop", KEY, max);
        assertEquals(16436, maxEnvelope.ciphertext().length);
        checkSample(longVersion.decrypt(IDENTITY, maxEnvelope), false);
      }
    }
    for (int length : new int[] {0, 28, 16437})
      assertThrows(
          IllegalArgumentException.class,
          () -> new EncryptedSessionPayload("v2", new byte[length]));
    assertEquals(29, new EncryptedSessionPayload("v2", new byte[29]).ciphertext().length);
    assertEquals(16436, new EncryptedSessionPayload("v2", new byte[16436]).ciphertext().length);
  }

  @Test
  void web020NullConfigurationIdentityAndClosedLifetime() {
    assertThrows(
        NullPointerException.class,
        () -> new SessionPayloadIdentity(null, "a".repeat(64), CREATED));
    assertThrows(NullPointerException.class, () -> new SessionPayloadIdentity(ID, null, CREATED));
    assertThrows(
        NullPointerException.class, () -> new SessionPayloadIdentity(ID, "a".repeat(64), null));
    assertThrows(NullPointerException.class, () -> IDENTITY.aad(null));
    for (String hash : List.of("", "a".repeat(63), "a".repeat(65), "A".repeat(64), "g".repeat(64)))
      assertThrows(
          IllegalArgumentException.class, () -> new SessionPayloadIdentity(ID, hash, CREATED));
    assertThrows(
        IllegalArgumentException.class,
        () -> new SessionPayloadIdentity(ID, "a".repeat(64), CREATED.plusNanos(1)));
    assertThrows(NullPointerException.class, () -> new EncryptedSessionPayload(null, new byte[29]));
    assertThrows(NullPointerException.class, () -> new EncryptedSessionPayload("v2", null));
    assertThrows(NullPointerException.class, () -> new SessionPayloadException(null));
    assertThrows(NullPointerException.class, () -> fixed(null, KEY, null, null));
    assertThrows(NullPointerException.class, () -> fixed("v2", null, null, null));
    assertThrows(
        NullPointerException.class, () -> new SessionPayloadCodec("v2", KEY, null, null, null));
    for (String version : List.of("", " ", "bad id", "日本語", "abcdefghijklmnopq")) {
      assertThrows(
          IllegalArgumentException.class, () -> new EncryptedSessionPayload(version, new byte[29]));
      assertThrows(IllegalArgumentException.class, () -> fixed(version, KEY, null, null));
      assertThrows(IllegalArgumentException.class, () -> fixed("v2", KEY, version, OLD));
    }
    for (int length : new int[] {0, 31, 33}) {
      assertThrows(IllegalArgumentException.class, () -> fixed("v2", new byte[length], null, null));
      assertThrows(IllegalArgumentException.class, () -> fixed("v2", KEY, "v1", new byte[length]));
    }
    assertThrows(IllegalArgumentException.class, () -> fixed("v2", KEY, "v1", null));
    assertThrows(IllegalArgumentException.class, () -> fixed("v2", KEY, null, OLD));
    assertThrows(IllegalArgumentException.class, () -> fixed("v2", KEY, "v2", OLD));
    var codec = fixed("v2", KEY, null, null);
    var payload = codec.encrypt(IDENTITY, sample(false));
    assertThrows(NullPointerException.class, () -> codec.encrypt(null, sample(false)));
    assertThrows(NullPointerException.class, () -> codec.encrypt(IDENTITY, null));
    assertThrows(NullPointerException.class, () -> codec.decrypt(null, payload));
    assertThrows(NullPointerException.class, () -> codec.decrypt(IDENTITY, null));
    codec.close();
    codec.close();
    assertThrows(IllegalStateException.class, () -> codec.encrypt(IDENTITY, sample(false)));
    assertThrows(IllegalStateException.class, () -> codec.decrypt(IDENTITY, payload));
  }

  @Test
  void web021ConcurrentNonceAndCallerMonitorIsolation() throws Exception {
    var codec = new SessionPayloadCodec("v2", KEY, "v1", OLD);
    var pool = Executors.newFixedThreadPool(10);
    try {
      var futures = new ArrayList<Future<EncryptedSessionPayload>>();
      for (int i = 0; i < 100; i++) {
        final int n = i;
        futures.add(
            pool.submit(
                () ->
                    codec.encrypt(
                        IDENTITY,
                        attributes(
                            true,
                            FIXTURE_READER_F734AAEA + n,
                            UserRole.ADMIN,
                            CSRF,
                            "/logs?q=" + n,
                            n % 11))));
      }
      var nonces = new HashSet<String>();
      for (int i = 0; i < 100; i++) {
        var encrypted = futures.get(i).get(20, TimeUnit.SECONDS);
        assertTrue(
            nonces.add(
                HexFormat.of().formatHex(Arrays.copyOfRange(encrypted.ciphertext(), 10, 22))));
        check(
            codec.decrypt(IDENTITY, encrypted),
            true,
            FIXTURE_READER_F734AAEA + i,
            UserRole.ADMIN,
            CSRF,
            "/logs?q=" + i,
            i % 11);
      }
      assertEquals(100, nonces.size());
      synchronized (codec) {
        pool.submit(
                () -> {
                  checkSample(
                      codec.decrypt(IDENTITY, codec.encrypt(IDENTITY, sample(false))), false);
                  codec.close();
                })
            .get(20, TimeUnit.SECONDS);
      }
      assertThrows(IllegalStateException.class, () -> codec.encrypt(IDENTITY, sample(false)));
    } finally {
      pool.shutdownNow();
      if (!pool.awaitTermination(10, TimeUnit.SECONDS)) {
        throw new AssertionError("session payload nonce workers did not terminate");
      }
      codec.close();
    }
  }

  @Test
  void web022ProviderAndRandomFailuresAreRedacted() throws Exception {
    var encrypted = independent("v2", KEY, plain(false));
    var provider = Security.getProvider("SunJCE");
    int position = Arrays.asList(Security.getProviders()).indexOf(provider) + 1;
    assertTrue(position > 0);
    Security.removeProvider("SunJCE");
    try (var codec = fixed("v2", KEY, null, null)) {
      reason(CRYPTO_UNAVAILABLE, () -> codec.encrypt(IDENTITY, sample(false)));
      reason(PAYLOAD_INVALID, () -> codec.decrypt(IDENTITY, encrypted));
    } finally {
      assertNotEquals(-1, Security.insertProviderAt(provider, position));
    }
    var random = new FixedRandom();
    random.fail = true;
    try (var codec = new SessionPayloadCodec("v2", KEY, null, null, random)) {
      reason(CRYPTO_UNAVAILABLE, () -> codec.encrypt(IDENTITY, sample(false)));
      assertArrayEquals(new byte[12], random.last);
    }
  }

  @Test
  void web023RotationKeysAndCloseAreSerialized() throws Exception {
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
    var codec = new SessionPayloadCodec("v2", KEY, "v1", OLD, random);
    var pool = Executors.newFixedThreadPool(2);
    try {
      var encrypted = pool.submit(() -> codec.encrypt(IDENTITY, sample(true)));
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
      var payload = encrypted.get(20, TimeUnit.SECONDS);
      close.get(20, TimeUnit.SECONDS);
      assertArrayEquals(new byte[12], random.last);
      assertArrayEquals(envelope("v2", KEY, aad("v2"), plain(true)), payload.ciphertext());
      assertThrows(IllegalStateException.class, () -> codec.decrypt(IDENTITY, payload));
      try (var restarted = new SessionPayloadCodec("v3", OLD, "v2", KEY)) {
        checkSample(restarted.decrypt(IDENTITY, payload), true);
        assertEquals("v3", restarted.encrypt(IDENTITY, sample(false)).keyVersion());
      }
    } finally {
      release.countDown();
      pool.shutdownNow();
      if (!pool.awaitTermination(10, TimeUnit.SECONDS)) {
        throw new AssertionError("session payload close workers did not terminate");
      }
      codec.close();
    }
  }

  private static SessionPayloadCodec fixed(
      String version, byte[] key, String previous, byte[] old) {
    return new SessionPayloadCodec(version, key, previous, old, new FixedRandom());
  }

  private static SessionAttributes sample(boolean authenticated) {
    return attributes(
        authenticated, FIXTURE_READER_F734AAEA, UserRole.ADMIN, CSRF, "/logs?q=日本語", 1);
  }

  private static byte[] plain(boolean authenticated) {
    return bytes(json(authenticated, FIXTURE_READER_F734AAEA, "ADMIN", CSRF, "/logs?q=日本語", 1));
  }

  private static void checkSample(SessionAttributes actual, boolean authenticated) {
    check(actual, authenticated, FIXTURE_READER_F734AAEA, UserRole.ADMIN, CSRF, "/logs?q=日本語", 1);
  }

  private static List<byte[]> fields(String version) throws Exception {
    var time = new ByteArrayOutputStream();
    try (var data = new DataOutputStream(time)) {
      data.writeLong(1788825600L);
      data.writeInt(123456000);
    }
    return new ArrayList<>(
        List.of(
            bytes("web-session"),
            bytes("schubert_web_session.web_http_sessions"),
            HexFormat.of().parseHex("00112233445566778899aabbccddeeff"),
            bytes("a".repeat(64)),
            time.toByteArray(),
            new byte[] {1},
            bytes(version)));
  }

  private static byte[] lp(List<byte[]> fields) throws Exception {
    var output = new ByteArrayOutputStream();
    try (var data = new DataOutputStream(output)) {
      for (byte[] field : fields) {
        data.writeInt(field.length);
        data.write(field);
      }
    }
    return output.toByteArray();
  }

  private static byte[] aad(String version) throws Exception {
    return lp(fields(version));
  }

  private static byte[] envelope(String version, byte[] key, byte[] aad, byte[] plaintext)
      throws Exception {
    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "AES"), new GCMParameterSpec(128, NONCE));
    cipher.updateAAD(aad);
    var output = new ByteArrayOutputStream();
    output.write(bytes("NKENC1"));
    output.write(1);
    output.write(version.length());
    output.write(version.getBytes(StandardCharsets.US_ASCII));
    output.write(NONCE);
    output.write(cipher.doFinal(plaintext));
    return output.toByteArray();
  }

  private static EncryptedSessionPayload independent(String version, byte[] key, byte[] plaintext)
      throws Exception {
    return new EncryptedSessionPayload(version, envelope(version, key, aad(version), plaintext));
  }

  private static void invalid(SessionPayloadCodec codec, byte[] envelope) {
    reason(
        PAYLOAD_INVALID,
        () -> codec.decrypt(IDENTITY, new EncryptedSessionPayload("v2", envelope)));
  }

  private static void reason(
      SessionPayloadException.Reason expected, org.junit.jupiter.api.function.Executable action) {
    var error = assertThrows(SessionPayloadException.class, action);
    assertEquals(expected, error.reason());
    assertEquals("session encrypted payload rejected: " + expected, error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  private static class FixedRandom extends SecureRandom {
    private static final long serialVersionUID = 1L;
    byte[] last = new byte[0];
    boolean fail;

    @Override
    public void nextBytes(byte[] output) {
      assertEquals(12, output.length);
      last = output;
      System.arraycopy(NONCE, 0, output, 0, 12);
      if (fail) throw new ProviderException("private-provider-marker");
    }
  }
}
