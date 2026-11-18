package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayOutputStream;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.Provider;
import java.security.SecureRandom;
import java.security.Security;
import java.util.Arrays;
import java.util.OptionalLong;
import java.util.Random;
import java.util.UUID;
import java.util.zip.Deflater;
import java.util.zip.DeflaterOutputStream;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.Test;

/** PT-IDEM-007/008 independent AES-GCM, bound, tamper and compression-bomb vectors. */
final class ResponseSnapshotCodecTest {
  private static final String FIXTURE_LOGRSP01_BEEB0A2B = "LOGRSP01";
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final byte[] NKENC1 = "NKENC1".getBytes(StandardCharsets.US_ASCII);
  private static final byte FORMAT_VERSION = 1;
  private static final UUID MESSAGE_ID = UUID.fromString("00000000-0000-0000-0000-000000000007");
  private static final ResponseSnapshotIdentity IDENTITY =
      ResponseSnapshotIdentity.authenticated(
          MESSAGE_ID, FIXTURE_LOGRSP01_BEEB0A2B, FIXTURE_001_A3FEAA64, 7);
  private static final byte[] CURRENT_KEY = sequence(0);
  private static final byte[] PREVIOUS_KEY = sequence(32);
  private static final byte[] NONCE = new byte[] {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11};

  @Test
  void scope002QuestionScopeFrameMatchesIndependentCompressionAadAndJceCiphertext()
      throws Exception {
    byte[] wire = new byte[304];
    Arrays.fill(wire, (byte) ' ');
    byte[] literal = new byte[312];
    System.arraycopy(java.util.HexFormat.of().parseHex("4e4b515259310041"), 0, literal, 0, 8);
    Arrays.fill(literal, 8, literal.length, (byte) ' ');
    var identity =
        ResponseSnapshotIdentity.authenticated(MESSAGE_ID, "QSSRSP01", FIXTURE_001_A3FEAA64, 7);
    byte[] frame = QuestionQueryScopeFrame.wrap(dev.codex.schubert.nk.api.domain.Role.ADMIN, wire);
    try (var codec = fixedCodec("k2", CURRENT_KEY, null, null)) {
      var actual = codec.encrypt(identity, frame);
      assertArrayEquals(literal, frame);
      assertArrayEquals(
          storedCiphertext(
              "k2",
              CURRENT_KEY,
              NONCE,
              independentAad(identity, "k2"),
              independentCompress(literal)),
          actual.ciphertext());
      assertArrayEquals(literal, codec.decrypt(identity, actual));
      assertEquals("k2", actual.keyVersion());
      assertArrayEquals(
          "NKENC1".getBytes(StandardCharsets.US_ASCII), Arrays.copyOf(actual.ciphertext(), 6));
    } finally {
      Arrays.fill(frame, (byte) 0);
      Arrays.fill(literal, (byte) 0);
    }
  }

  @Test
  void fixedNonceCiphertextMatchesIndependentCompressionAndAadVector() throws Exception {
    byte[] plaintext = "public synthetic snapshot".getBytes(StandardCharsets.UTF_8);
    byte[] callerKey = CURRENT_KEY.clone();
    byte[] callerPlaintext = plaintext.clone();
    try (ResponseSnapshotCodec codec = fixedCodec("k2", callerKey, null, null)) {
      EncryptedResponseSnapshot actual = codec.encrypt(IDENTITY, callerPlaintext);
      byte[] independent =
          storedCiphertext(
              "k2",
              CURRENT_KEY,
              NONCE,
              independentAad(IDENTITY, "k2"),
              independentCompress(plaintext));

      assertEquals("k2", actual.keyVersion());
      assertArrayEquals(independent, actual.ciphertext());
      assertArrayEquals(NKENC1, Arrays.copyOfRange(actual.ciphertext(), 0, NKENC1.length));
      assertEquals(FORMAT_VERSION, actual.ciphertext()[6]);
      assertEquals(2, actual.ciphertext()[7]);
      assertArrayEquals(
          "k2".getBytes(StandardCharsets.US_ASCII), Arrays.copyOfRange(actual.ciphertext(), 8, 10));
      assertArrayEquals(NONCE, Arrays.copyOfRange(actual.ciphertext(), 10, 22));
      assertArrayEquals(plaintext, codec.decrypt(IDENTITY, actual));
      assertArrayEquals(plaintext, callerPlaintext);
      assertArrayEquals(CURRENT_KEY, callerKey);
      assertEquals(
          "EncryptedResponseSnapshot[keyVersion/ciphertext=<redacted>]", actual.toString());
      assertEquals(
          "ResponseSnapshotIdentity[request/layout/version/owner=<redacted>]", IDENTITY.toString());

      byte[] returned = actual.ciphertext();
      returned[0] ^= 1;
      assertNotEquals(returned[0], actual.ciphertext()[0]);
    }

    try (ResponseSnapshotCodec productionConstructor =
        new ResponseSnapshotCodec("k2", CURRENT_KEY, null, null)) {
      EncryptedResponseSnapshot snapshot =
          productionConstructor.encrypt(
              ResponseSnapshotIdentity.anonymous(MESSAGE_ID, "LGNRSP01", FIXTURE_001_A3FEAA64),
              new byte[0]);
      assertArrayEquals(
          new byte[0],
          productionConstructor.decrypt(
              ResponseSnapshotIdentity.anonymous(MESSAGE_ID, "LGNRSP01", FIXTURE_001_A3FEAA64),
              snapshot));
    }
  }

  @Test
  void zeroAndMaximumPlaintextRoundTripAndEveryLengthBoundaryIsGuarded() {
    byte[] maximum = new byte[ResponseSnapshotCodec.MAXIMUM_PLAINTEXT_BYTES];
    new Random(7).nextBytes(maximum);
    try (ResponseSnapshotCodec codec = fixedCodec("k2", CURRENT_KEY, null, null)) {
      EncryptedResponseSnapshot encryptedMaximum = codec.encrypt(IDENTITY, maximum);
      assertTrue(
          encryptedMaximum.ciphertext().length
              <= EncryptedResponseSnapshot.MAXIMUM_CIPHERTEXT_BYTES);
      assertArrayEquals(maximum, codec.decrypt(IDENTITY, encryptedMaximum));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              codec.encrypt(IDENTITY, new byte[ResponseSnapshotCodec.MAXIMUM_PLAINTEXT_BYTES + 1]));
    }

    new EncryptedResponseSnapshot(
        "v1", new byte[EncryptedResponseSnapshot.MINIMUM_CIPHERTEXT_BYTES]);
    new EncryptedResponseSnapshot(
        "v1", new byte[EncryptedResponseSnapshot.MAXIMUM_CIPHERTEXT_BYTES]);
    assertThrows(
        IllegalArgumentException.class, () -> new EncryptedResponseSnapshot("v1", new byte[28]));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new EncryptedResponseSnapshot(
                "v1", new byte[EncryptedResponseSnapshot.MAXIMUM_CIPHERTEXT_BYTES + 1]));
  }

  @Test
  void currentPreviousUnknownTamperAndEveryAadMutationDenyClosed() throws Exception {
    byte[] plaintext = "replay".getBytes(StandardCharsets.UTF_8);
    try (ResponseSnapshotCodec codec = fixedCodec("k2", CURRENT_KEY, "k1", PREVIOUS_KEY)) {
      EncryptedResponseSnapshot current = codec.encrypt(IDENTITY, plaintext);
      EncryptedResponseSnapshot previous =
          independentSnapshot("k1", PREVIOUS_KEY, IDENTITY, independentCompress(plaintext));
      assertArrayEquals(plaintext, codec.decrypt(IDENTITY, current));
      assertArrayEquals(plaintext, codec.decrypt(IDENTITY, previous));

      EncryptedResponseSnapshot unknown = new EncryptedResponseSnapshot("k0", current.ciphertext());
      assertReason(
          ResponseSnapshotException.Reason.SNAPSHOT_INVALID,
          () -> codec.decrypt(IDENTITY, unknown));

      byte[] unknownKeyEnvelope = current.ciphertext();
      unknownKeyEnvelope[9] = '0';
      assertReason(
          ResponseSnapshotException.Reason.KEY_UNAVAILABLE,
          () -> codec.decrypt(IDENTITY, new EncryptedResponseSnapshot("k0", unknownKeyEnvelope)));

      byte[] wrongMagic = current.ciphertext();
      wrongMagic[0] ^= 1;
      assertInvalidEnvelope(codec, wrongMagic);
      byte[] wrongFormat = current.ciphertext();
      wrongFormat[6] = 2;
      assertInvalidEnvelope(codec, wrongFormat);
      byte[] zeroKeyLength = current.ciphertext();
      zeroKeyLength[7] = 0;
      assertInvalidEnvelope(codec, zeroKeyLength);
      byte[] oversizedKeyLength = current.ciphertext();
      oversizedKeyLength[7] = 17;
      assertInvalidEnvelope(codec, oversizedKeyLength);
      byte[] invalidKeyId = current.ciphertext();
      invalidKeyId[8] = ' ';
      assertInvalidEnvelope(codec, invalidKeyId);
      assertInvalidEnvelope(codec, Arrays.copyOf(current.ciphertext(), 36));
      assertInvalidEnvelope(codec, Arrays.copyOf(current.ciphertext(), 37));

      byte[] tampered = current.ciphertext();
      tampered[tampered.length - 1] ^= 1;
      assertReason(
          ResponseSnapshotException.Reason.SNAPSHOT_INVALID,
          () -> codec.decrypt(IDENTITY, new EncryptedResponseSnapshot("k2", tampered)));

      assertInvalidAad(
          codec,
          current,
          ResponseSnapshotIdentity.authenticated(
              UUID.fromString("00000000-0000-0000-0000-000000000008"),
              FIXTURE_LOGRSP01_BEEB0A2B,
              FIXTURE_001_A3FEAA64,
              7));
      assertInvalidAad(
          codec,
          current,
          ResponseSnapshotIdentity.authenticated(MESSAGE_ID, "QSTRSP01", FIXTURE_001_A3FEAA64, 7));
      assertInvalidAad(
          codec,
          current,
          ResponseSnapshotIdentity.authenticated(MESSAGE_ID, FIXTURE_LOGRSP01_BEEB0A2B, "002", 7));
      assertInvalidAad(
          codec,
          current,
          ResponseSnapshotIdentity.authenticated(
              MESSAGE_ID, FIXTURE_LOGRSP01_BEEB0A2B, FIXTURE_001_A3FEAA64, 8));
      assertInvalidAad(
          codec,
          current,
          ResponseSnapshotIdentity.anonymous(
              MESSAGE_ID, FIXTURE_LOGRSP01_BEEB0A2B, FIXTURE_001_A3FEAA64));
    }

    try (ResponseSnapshotCodec codecWithoutRotation = fixedCodec("k2", CURRENT_KEY, null, null)) {
      EncryptedResponseSnapshot unavailablePrevious =
          independentSnapshot("k1", PREVIOUS_KEY, IDENTITY, independentCompress(plaintext));
      assertReason(
          ResponseSnapshotException.Reason.KEY_UNAVAILABLE,
          () -> codecWithoutRotation.decrypt(IDENTITY, unavailablePrevious));
    }
  }

  @Test
  void malformedTruncatedTrailingDictionaryAndCompressionBombStreamsAreRejected() throws Exception {
    try (ResponseSnapshotCodec codec = fixedCodec("k2", CURRENT_KEY, null, null)) {
      assertInvalidCompressed(codec, new byte[] {1, 2, 3, 4});

      byte[] valid = independentCompress("value".getBytes(StandardCharsets.UTF_8));
      assertInvalidCompressed(codec, Arrays.copyOf(valid, valid.length - 1));
      byte[] trailing = Arrays.copyOf(valid, valid.length + 1);
      trailing[trailing.length - 1] = 1;
      assertInvalidCompressed(codec, trailing);

      assertInvalidCompressed(codec, independentCompressWithDictionary(new byte[] {1, 2, 3}));
      assertInvalidCompressed(
          codec, independentCompress(new byte[ResponseSnapshotCodec.MAXIMUM_PLAINTEXT_BYTES + 1]));
    }
  }

  @Test
  void identitySnapshotKeyAndLifecycleContractsRejectNullAndInvalidValues() {
    assertThrows(
        NullPointerException.class,
        () ->
            new ResponseSnapshotIdentity(
                null, FIXTURE_LOGRSP01_BEEB0A2B, FIXTURE_001_A3FEAA64, OptionalLong.empty()));
    assertThrows(
        NullPointerException.class,
        () ->
            new ResponseSnapshotIdentity(
                MESSAGE_ID, null, FIXTURE_001_A3FEAA64, OptionalLong.empty()));
    assertThrows(
        NullPointerException.class,
        () ->
            new ResponseSnapshotIdentity(
                MESSAGE_ID, FIXTURE_LOGRSP01_BEEB0A2B, null, OptionalLong.empty()));
    assertThrows(
        NullPointerException.class,
        () ->
            new ResponseSnapshotIdentity(
                MESSAGE_ID, FIXTURE_LOGRSP01_BEEB0A2B, FIXTURE_001_A3FEAA64, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> ResponseSnapshotIdentity.anonymous(MESSAGE_ID, "short", FIXTURE_001_A3FEAA64));
    assertThrows(
        IllegalArgumentException.class,
        () -> ResponseSnapshotIdentity.anonymous(MESSAGE_ID, FIXTURE_LOGRSP01_BEEB0A2B, "v1"));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            ResponseSnapshotIdentity.authenticated(
                MESSAGE_ID, FIXTURE_LOGRSP01_BEEB0A2B, FIXTURE_001_A3FEAA64, 0));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            ResponseSnapshotIdentity.authenticated(
                MESSAGE_ID, FIXTURE_LOGRSP01_BEEB0A2B, FIXTURE_001_A3FEAA64, 1_000_000_000_000L));

    assertThrows(
        NullPointerException.class, () -> new EncryptedResponseSnapshot(null, new byte[29]));
    assertThrows(NullPointerException.class, () -> new EncryptedResponseSnapshot("v1", null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new EncryptedResponseSnapshot("bad version", new byte[29]));

    assertThrows(
        NullPointerException.class, () -> new ResponseSnapshotCodec(null, CURRENT_KEY, null, null));
    assertThrows(
        NullPointerException.class, () -> new ResponseSnapshotCodec("k2", null, null, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new ResponseSnapshotCodec("bad version", CURRENT_KEY, null, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new ResponseSnapshotCodec("k2", new byte[31], null, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new ResponseSnapshotCodec("k2", CURRENT_KEY, "k1", null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new ResponseSnapshotCodec("k2", CURRENT_KEY, null, PREVIOUS_KEY));
    assertThrows(
        IllegalArgumentException.class,
        () -> new ResponseSnapshotCodec("k2", CURRENT_KEY, "bad version", PREVIOUS_KEY));
    assertThrows(
        IllegalArgumentException.class,
        () -> new ResponseSnapshotCodec("k2", CURRENT_KEY, "k1", new byte[31]));
    assertThrows(
        IllegalArgumentException.class,
        () -> new ResponseSnapshotCodec("k2", CURRENT_KEY, "k2", PREVIOUS_KEY));
    assertThrows(
        NullPointerException.class,
        () -> new ResponseSnapshotCodec("k2", CURRENT_KEY, null, null, null));

    ResponseSnapshotCodec codec = fixedCodec("k2", CURRENT_KEY, null, null);
    assertThrows(NullPointerException.class, () -> codec.encrypt(null, new byte[0]));
    assertThrows(NullPointerException.class, () -> codec.encrypt(IDENTITY, null));
    EncryptedResponseSnapshot snapshot = codec.encrypt(IDENTITY, new byte[0]);
    assertThrows(NullPointerException.class, () -> codec.decrypt(null, snapshot));
    assertThrows(NullPointerException.class, () -> codec.decrypt(IDENTITY, null));
    codec.close();
    codec.close();
    assertThrows(IllegalStateException.class, () -> codec.encrypt(IDENTITY, new byte[0]));
    assertThrows(IllegalStateException.class, () -> codec.decrypt(IDENTITY, snapshot));
  }

  @Test
  void unavailableAesProviderProducesTypedBoundedFailure() {
    Provider provider = Security.getProvider("SunJCE");
    int position = providerPosition("SunJCE");
    Security.removeProvider("SunJCE");
    try (ResponseSnapshotCodec codec = fixedCodec("k2", CURRENT_KEY, null, null)) {
      ResponseSnapshotException failure =
          assertThrows(ResponseSnapshotException.class, () -> codec.encrypt(IDENTITY, new byte[0]));
      assertEquals(ResponseSnapshotException.Reason.CRYPTO_UNAVAILABLE, failure.reason());
      assertEquals("response snapshot encryption is unavailable", failure.getMessage());
      assertFalse(failure.getMessage().contains("000102"));
    } finally {
      assertNotEquals(-1, position);
      Security.insertProviderAt(provider, position);
    }
  }

  private static ResponseSnapshotCodec fixedCodec(
      String currentVersion, byte[] currentKey, String previousVersion, byte[] previousKey) {
    return new ResponseSnapshotCodec(
        currentVersion, currentKey, previousVersion, previousKey, new FixedSecureRandom(NONCE));
  }

  private static void assertInvalidAad(
      ResponseSnapshotCodec codec,
      EncryptedResponseSnapshot snapshot,
      ResponseSnapshotIdentity changed) {
    assertReason(
        ResponseSnapshotException.Reason.SNAPSHOT_INVALID, () -> codec.decrypt(changed, snapshot));
  }

  private static void assertInvalidCompressed(ResponseSnapshotCodec codec, byte[] compressed)
      throws Exception {
    EncryptedResponseSnapshot snapshot =
        independentSnapshot("k2", CURRENT_KEY, IDENTITY, compressed);
    assertReason(
        ResponseSnapshotException.Reason.SNAPSHOT_INVALID, () -> codec.decrypt(IDENTITY, snapshot));
  }

  private static void assertInvalidEnvelope(ResponseSnapshotCodec codec, byte[] envelope) {
    assertReason(
        ResponseSnapshotException.Reason.SNAPSHOT_INVALID,
        () -> codec.decrypt(IDENTITY, new EncryptedResponseSnapshot("k2", envelope)));
  }

  private static void assertReason(
      ResponseSnapshotException.Reason expected, ThrowingOperation operation) {
    ResponseSnapshotException failure =
        assertThrows(ResponseSnapshotException.class, operation::run);
    assertEquals(expected, failure.reason());
    assertFalse(failure.getMessage().contains("public synthetic snapshot"));
  }

  private static EncryptedResponseSnapshot independentSnapshot(
      String version, byte[] key, ResponseSnapshotIdentity identity, byte[] compressed)
      throws Exception {
    return new EncryptedResponseSnapshot(
        version,
        storedCiphertext(version, key, NONCE, independentAad(identity, version), compressed));
  }

  private static byte[] storedCiphertext(
      String keyVersion, byte[] key, byte[] nonce, byte[] aad, byte[] compressed) throws Exception {
    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "AES"), new GCMParameterSpec(128, nonce));
    cipher.updateAAD(aad);
    byte[] encrypted = cipher.doFinal(compressed);
    byte[] keyId = keyVersion.getBytes(StandardCharsets.US_ASCII);
    return ByteBuffer.allocate(NKENC1.length + 2 + keyId.length + nonce.length + encrypted.length)
        .put(NKENC1)
        .put(FORMAT_VERSION)
        .put((byte) keyId.length)
        .put(keyId)
        .put(nonce)
        .put(encrypted)
        .array();
  }

  private static byte[] independentAad(ResponseSnapshotIdentity identity, String keyVersion) {
    byte[] purpose = "api-inbox-response".getBytes(StandardCharsets.US_ASCII);
    byte[] table = "schubert.request_inbox".getBytes(StandardCharsets.US_ASCII);
    byte[] messageId =
        ByteBuffer.allocate(16)
            .putLong(identity.requestMessageId().getMostSignificantBits())
            .putLong(identity.requestMessageId().getLeastSignificantBits())
            .array();
    byte[] format = new byte[] {FORMAT_VERSION};
    byte[] keyId = keyVersion.getBytes(StandardCharsets.US_ASCII);
    byte[] layout = identity.responseLayoutId().getBytes(StandardCharsets.US_ASCII);
    byte[] version = identity.responseVersion().getBytes(StandardCharsets.US_ASCII);
    byte[] owner =
        identity.ownerUserId().isPresent()
            ? ByteBuffer.allocate(Long.BYTES).putLong(identity.ownerUserId().getAsLong()).array()
            : new byte[0];
    ByteBuffer buffer =
        ByteBuffer.allocate(
            8 * Integer.BYTES
                + purpose.length
                + table.length
                + messageId.length
                + format.length
                + keyId.length
                + layout.length
                + version.length
                + owner.length);
    putLengthPrefixed(buffer, purpose);
    putLengthPrefixed(buffer, table);
    putLengthPrefixed(buffer, messageId);
    putLengthPrefixed(buffer, format);
    putLengthPrefixed(buffer, keyId);
    putLengthPrefixed(buffer, layout);
    putLengthPrefixed(buffer, version);
    putLengthPrefixed(buffer, owner);
    return buffer.array();
  }

  private static void putLengthPrefixed(ByteBuffer buffer, byte[] value) {
    buffer.putInt(value.length);
    buffer.put(value);
  }

  private static byte[] independentCompress(byte[] plaintext) throws Exception {
    return independentCompress(plaintext, null);
  }

  private static byte[] independentCompressWithDictionary(byte[] plaintext) throws Exception {
    return independentCompress(plaintext, new byte[] {9, 8, 7, 6});
  }

  private static byte[] independentCompress(byte[] plaintext, byte[] dictionary) throws Exception {
    ByteArrayOutputStream output = new ByteArrayOutputStream();
    Deflater deflater = new Deflater(3);
    try {
      if (dictionary != null) {
        deflater.setDictionary(dictionary);
      }
      try (DeflaterOutputStream stream = new DeflaterOutputStream(output, deflater)) {
        stream.write(plaintext);
      }
    } finally {
      deflater.end();
    }
    return output.toByteArray();
  }

  private static byte[] sequence(int start) {
    byte[] value = new byte[32];
    for (int index = 0; index < value.length; index++) {
      value[index] = (byte) (start + index);
    }
    return value;
  }

  private static int providerPosition(String name) {
    Provider[] providers = Security.getProviders();
    for (int index = 0; index < providers.length; index++) {
      if (providers[index].getName().equals(name)) {
        return index + 1;
      }
    }
    return -1;
  }

  @FunctionalInterface
  private interface ThrowingOperation {
    void run();
  }

  private static final class FixedSecureRandom extends SecureRandom {
    private static final long serialVersionUID = 1L;
    private final byte[] value;

    private FixedSecureRandom(byte[] value) {
      this.value = value.clone();
    }

    @Override
    public void nextBytes(byte[] bytes) {
      System.arraycopy(value, 0, bytes, 0, bytes.length);
    }
  }
}
