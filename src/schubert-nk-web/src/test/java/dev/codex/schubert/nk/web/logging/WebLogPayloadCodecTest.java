package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

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
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.Test;

/**
 * PT-IDEM-012/015 codec portion. UI 232/235 offsets build the plaintext independently;
 * DataOutputStream and JCE compute the AAD/envelope oracle without any production codec call.
 * Keys/nonces are public synthetic sequences and never represent deployed credentials.
 */
final class WebLogPayloadCodecTest {
  private static final UUID MESSAGE = UUID.fromString("00000000-0000-0000-0000-000000000012");
  private static final UUID CORRELATION = UUID.fromString("00000000-0000-0000-0000-000000000015");
  private static final WebLogPayloadIdentity IDENTITY =
      new WebLogPayloadIdentity(MESSAGE, CORRELATION);
  private static final byte[] CURRENT = sequence(32, 0);
  private static final byte[] PREVIOUS = sequence(32, 32);
  private static final byte[] NONCE = sequence(12, 64);

  @Test
  void bug036CallerMonitorCannotBlockEncryptionDecryptionOrClose() throws Exception {
    byte[] plaintext = goldenWire();
    byte[] expected = independentEnvelope("v2", CURRENT, independentAad(IDENTITY, "v2"), plaintext);
    WebLogPayloadCodec codec = fixedCodec("v2", CURRENT, null, null);
    var executor = Executors.newVirtualThreadPerTaskExecutor();
    try {
      synchronized (codec) {
        executor
            .submit(
                () -> {
                  assertArrayEquals(expected, codec.encrypt(IDENTITY, plaintext).ciphertext());
                  assertArrayEquals(
                      plaintext,
                      codec.decrypt(IDENTITY, new EncryptedWebLogPayload("v2", expected)));
                  codec.close();
                  assertThrows(
                      IllegalStateException.class, () -> codec.encrypt(IDENTITY, plaintext));
                  return 0;
                })
            .get(5, java.util.concurrent.TimeUnit.SECONDS);
      }
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
      codec.close();
    }
  }

  @Test
  void canonicalAadAndFullEnvelopeMatchIndependentVectorAndCopiesAreDefensive() throws Exception {
    byte[] plaintext = goldenWire();
    byte[] sourceKey = CURRENT.clone();
    try (WebLogPayloadCodec codec = fixedCodec("v2", sourceKey, null, null)) {
      Arrays.fill(sourceKey, (byte) 0);
      byte[] input = plaintext.clone();
      EncryptedWebLogPayload encrypted = codec.encrypt(IDENTITY, input);
      byte[] expected =
          independentEnvelope("v2", CURRENT, independentAad(IDENTITY, "v2"), plaintext);
      assertArrayEquals(independentAad(IDENTITY, "v2"), IDENTITY.aad("v2"));
      assertArrayEquals(expected, encrypted.ciphertext());
      assertArrayEquals(plaintext, input);
      assertEquals("v2", encrypted.keyVersion());
      assertEquals(2_374, encrypted.ciphertext().length);
      assertArrayEquals(NONCE, Arrays.copyOfRange(encrypted.ciphertext(), 10, 22));
      assertArrayEquals(plaintext, codec.decrypt(IDENTITY, encrypted));
      byte[] exposed = encrypted.ciphertext();
      exposed[0] ^= 1;
      assertArrayEquals(expected, encrypted.ciphertext());
      EncryptedWebLogPayload copy = new EncryptedWebLogPayload("v2", expected);
      expected[0] ^= 1;
      assertArrayEquals(plaintext, codec.decrypt(IDENTITY, copy));
      assertEquals("EncryptedWebLogPayload[keyVersion/ciphertext=<redacted>]", copy.toString());
      assertEquals("WebLogPayloadIdentity[message/correlation=<redacted>]", IDENTITY.toString());
      assertEquals(MESSAGE, IDENTITY.messageId());
      assertEquals(CORRELATION, IDENTITY.correlationId());
    }
    assertArrayEquals(sequence(32, 0), CURRENT);
  }

  @Test
  void currentWritesPreviousReadsAndUnknownKeyDenyClosed() throws Exception {
    byte[] plaintext = goldenWire();
    try (WebLogPayloadCodec codec = fixedCodec("v2", CURRENT, "v1", PREVIOUS)) {
      EncryptedWebLogPayload previous = independentPayload("v1", PREVIOUS, plaintext);
      assertArrayEquals(plaintext, codec.decrypt(IDENTITY, previous));
      assertEquals("v2", codec.encrypt(IDENTITY, plaintext).keyVersion());
      assertReason(
          WebLogPayloadException.Reason.KEY_UNAVAILABLE,
          () -> codec.decrypt(IDENTITY, independentPayload("v0", PREVIOUS, plaintext)));
      assertReason(
          WebLogPayloadException.Reason.PAYLOAD_INVALID,
          () -> codec.decrypt(IDENTITY, new EncryptedWebLogPayload("v2", previous.ciphertext())));
    }
    try (WebLogPayloadCodec codec = fixedCodec("v2", CURRENT, null, null)) {
      assertReason(
          WebLogPayloadException.Reason.KEY_UNAVAILABLE,
          () -> codec.decrypt(IDENTITY, independentPayload("v1", PREVIOUS, plaintext)));
    }
    for (String version : List.of("a", "a1234567890._-AB")) {
      try (WebLogPayloadCodec codec = fixedCodec(version, CURRENT, null, null)) {
        assertArrayEquals(plaintext, codec.decrypt(IDENTITY, codec.encrypt(IDENTITY, plaintext)));
      }
    }
  }

  @Test
  void malformedEnvelopeMagicVersionKeyIdLengthNonceCiphertextAndTagAreRejected() {
    try (WebLogPayloadCodec codec = fixedCodec("v2", CURRENT, null, null)) {
      byte[] valid = codec.encrypt(IDENTITY, goldenWire()).ciphertext();
      assertInvalid(codec, new byte[29]);
      for (int index : new int[] {0, 6, 10, 22, valid.length - 1}) {
        byte[] changed = valid.clone();
        changed[index] ^= 1;
        assertInvalid(codec, changed);
      }
      for (int keyLength : new int[] {0, 17, 255}) {
        byte[] changed = valid.clone();
        changed[7] = (byte) keyLength;
        assertInvalid(codec, changed);
      }
      byte[] missingTag = Arrays.copyOf(valid, 37);
      missingTag[7] = 16;
      assertInvalid(codec, missingTag);
      for (byte keyCharacter : new byte[] {' ', (byte) 0xff}) {
        byte[] changed = valid.clone();
        changed[8] = keyCharacter;
        assertInvalid(codec, changed);
      }
      byte[] databaseVersionMismatch = valid.clone();
      databaseVersionMismatch[9] = '1';
      assertInvalid(codec, databaseVersionMismatch);
      assertInvalid(codec, Arrays.copyOf(valid, valid.length - 1));
      assertInvalid(codec, Arrays.copyOf(valid, valid.length + 1));
    }
  }

  @Test
  void everyAadFieldMutationAndCrossRowMoveFailAuthenticationBeforeAnyPlaintext() throws Exception {
    try (WebLogPayloadCodec codec = fixedCodec("v2", CURRENT, "v1", PREVIOUS)) {
      EncryptedWebLogPayload valid = codec.encrypt(IDENTITY, goldenWire());
      for (WebLogPayloadIdentity other :
          List.of(
              new WebLogPayloadIdentity(CORRELATION, CORRELATION),
              new WebLogPayloadIdentity(MESSAGE, MESSAGE))) {
        assertReason(
            WebLogPayloadException.Reason.PAYLOAD_INVALID, () -> codec.decrypt(other, valid));
      }
      // Separate mutations cover purpose, table, message ID, correlation ID, format, key ID,
      // layout, layout version and each corresponding length prefix.
      byte[] originalAad = independentAad(IDENTITY, "v2");
      int offset = 0;
      // schubert_web_session (20 ASCII) + '.' (1) + web_log_outbox (14) = 35.
      int[] lengths = {14, 35, 16, 16, 1, 2, 8, 3};
      for (int length : lengths) {
        for (int index : new int[] {offset + 3, offset + 4}) {
          byte[] altered = originalAad.clone();
          altered[index] ^= 1;
          EncryptedWebLogPayload forged =
              new EncryptedWebLogPayload(
                  "v2", independentEnvelope("v2", CURRENT, altered, goldenWire()));
          assertReason(
              WebLogPayloadException.Reason.PAYLOAD_INVALID, () -> codec.decrypt(IDENTITY, forged));
        }
        offset += Integer.BYTES + length;
      }
      assertEquals(originalAad.length, offset);
    }
  }

  @Test
  void exact2336ByteWireHeaderIdentityAndPayloadSemanticsAreCheckedBeforeStorageAndAfterAuth()
      throws Exception {
    try (WebLogPayloadCodec codec = fixedCodec("v2", CURRENT, null, null)) {
      for (int length : new int[] {0, 2_080, 2_335, 2_337}) {
        byte[] candidate = Arrays.copyOf(goldenWire(), length);
        assertReason(
            WebLogPayloadException.Reason.PAYLOAD_INVALID,
            () -> codec.encrypt(IDENTITY, candidate));
        assertReason(
            WebLogPayloadException.Reason.PAYLOAD_INVALID,
            () -> codec.decrypt(IDENTITY, independentPayload("v2", CURRENT, candidate)));
      }
      List<byte[]> invalidWires = new ArrayList<>();
      byte[] otherLayout = goldenWire();
      ascii(otherLayout, 11, "QWKREQ01");
      ascii(otherLayout, 181, "000064");
      ascii(otherLayout, 199, "000000320");
      invalidWires.add(otherLayout);
      byte[] messageMismatch = goldenWire();
      ascii(messageMismatch, 24, CORRELATION.toString());
      invalidWires.add(messageMismatch);
      byte[] correlationMismatch = goldenWire();
      ascii(correlationMismatch, 60, MESSAGE.toString());
      invalidWires.add(correlationMismatch);
      byte[] invalidHeader = goldenWire();
      invalidHeader[0] = 'X';
      invalidWires.add(invalidHeader);
      byte[] badVersion = goldenWire();
      ascii(badVersion, 19, "002");
      invalidWires.add(badVersion);
      byte[] secretContext = goldenWire();
      Arrays.fill(secretContext, 113, 177, (byte) 'a');
      invalidWires.add(secretContext);
      byte[] missingRequired = goldenWire();
      Arrays.fill(missingRequired, 256 + 105, 256 + 617, (byte) ' ');
      invalidWires.add(missingRequired);
      byte[] unknownLevel = goldenWire();
      ascii(unknownLevel, 256 + 33, "FATAL");
      invalidWires.add(unknownLevel);
      byte[] invalidMethod = goldenWire();
      ascii(invalidMethod, 256 + 653, "get");
      invalidWires.add(invalidMethod);
      byte[] queryLeak = goldenWire();
      ascii(queryLeak, 256 + 661, "/login?test=synthetic");
      invalidWires.add(queryLeak);
      byte[] crlf = goldenWire();
      crlf[256 + 106] = '\r';
      invalidWires.add(crlf);
      byte[] reserved = goldenWire();
      reserved[2_335] = 'X';
      invalidWires.add(reserved);
      for (byte[] invalid : invalidWires) {
        assertReason(
            WebLogPayloadException.Reason.PAYLOAD_INVALID, () -> codec.encrypt(IDENTITY, invalid));
        assertReason(
            WebLogPayloadException.Reason.PAYLOAD_INVALID,
            () -> codec.decrypt(IDENTITY, independentPayload("v2", CURRENT, invalid)));
      }
    }
  }

  @Test
  void modelBoundsConfigurationNullAndClosedLifecycleFailExplicitly() {
    assertThrows(NullPointerException.class, () -> new WebLogPayloadIdentity(null, CORRELATION));
    assertThrows(NullPointerException.class, () -> new WebLogPayloadIdentity(MESSAGE, null));
    assertThrows(NullPointerException.class, () -> IDENTITY.aad(null));
    assertThrows(NullPointerException.class, () -> new WebLogPayloadException(null));
    assertThrows(NullPointerException.class, () -> new EncryptedWebLogPayload(null, new byte[29]));
    assertThrows(NullPointerException.class, () -> new EncryptedWebLogPayload("v2", null));
    for (String version : List.of("", " ", "bad id", "日本語", "v12345678901234567")) {
      assertThrows(
          IllegalArgumentException.class, () -> new EncryptedWebLogPayload(version, new byte[29]));
      assertThrows(
          IllegalArgumentException.class,
          () -> new WebLogPayloadCodec(version, CURRENT, null, null));
      assertThrows(
          IllegalArgumentException.class,
          () -> new WebLogPayloadCodec("v2", CURRENT, version, PREVIOUS));
    }
    for (int length : new int[] {0, 28, 2_389}) {
      assertThrows(
          IllegalArgumentException.class, () -> new EncryptedWebLogPayload("v2", new byte[length]));
    }
    assertEquals(29, new EncryptedWebLogPayload("v2", new byte[29]).ciphertext().length);
    assertEquals(2_388, new EncryptedWebLogPayload("v2", new byte[2_388]).ciphertext().length);
    assertThrows(
        NullPointerException.class, () -> new WebLogPayloadCodec(null, CURRENT, null, null));
    assertThrows(NullPointerException.class, () -> new WebLogPayloadCodec("v2", null, null, null));
    for (int length : new int[] {0, 31, 33}) {
      assertThrows(
          IllegalArgumentException.class,
          () -> new WebLogPayloadCodec("v2", new byte[length], null, null));
      assertThrows(
          IllegalArgumentException.class,
          () -> new WebLogPayloadCodec("v2", CURRENT, "v1", new byte[length]));
    }
    assertThrows(
        IllegalArgumentException.class, () -> new WebLogPayloadCodec("v2", CURRENT, "v1", null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new WebLogPayloadCodec("v2", CURRENT, null, PREVIOUS));
    assertThrows(
        IllegalArgumentException.class,
        () -> new WebLogPayloadCodec("v2", CURRENT, "v2", PREVIOUS));
    assertThrows(
        NullPointerException.class, () -> new WebLogPayloadCodec("v2", CURRENT, null, null, null));
    WebLogPayloadCodec codec = fixedCodec("v2", CURRENT, null, null);
    try {
      EncryptedWebLogPayload encrypted = codec.encrypt(IDENTITY, goldenWire());
      assertThrows(NullPointerException.class, () -> codec.encrypt(null, goldenWire()));
      assertThrows(NullPointerException.class, () -> codec.encrypt(IDENTITY, null));
      assertThrows(NullPointerException.class, () -> codec.decrypt(null, encrypted));
      assertThrows(NullPointerException.class, () -> codec.decrypt(IDENTITY, null));
      codec.close();
      codec.close();
      assertThrows(IllegalStateException.class, () -> codec.encrypt(IDENTITY, goldenWire()));
      assertThrows(IllegalStateException.class, () -> codec.decrypt(IDENTITY, encrypted));
    } finally {
      codec.close();
    }
  }

  @Test
  void concurrentProductionNonceGenerationKeepsEveryMessageAuthenticAndDistinct() throws Exception {
    WebLogPayloadCodec codec = new WebLogPayloadCodec("v2", CURRENT, "v1", PREVIOUS);
    var executor = Executors.newFixedThreadPool(4);
    try {
      List<Callable<EncryptedWebLogPayload>> jobs = new ArrayList<>();
      for (int index = 0; index < 100; index++) {
        jobs.add(() -> codec.encrypt(IDENTITY, goldenWire()));
      }
      HashSet<String> nonces = new HashSet<>();
      for (var future : executor.invokeAll(jobs, 10, TimeUnit.SECONDS)) {
        EncryptedWebLogPayload encrypted = future.get(10, TimeUnit.SECONDS);
        assertTrue(
            nonces.add(
                HexFormat.of().formatHex(Arrays.copyOfRange(encrypted.ciphertext(), 10, 22))));
        assertArrayEquals(goldenWire(), codec.decrypt(IDENTITY, encrypted));
      }
      assertEquals(100, nonces.size());
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
      codec.close();
    }
  }

  /** PT-WEB-WEBLOG-OWN002: admission failure order and borrowed key ownership. */
  @Test
  void invalidConfigurationPreservesFailureOrderAndBorrowedKeys() {
    byte[] current = sequence(32, 0);
    byte[] previous = sequence(32, 32);
    assertEquals(
        "web log key must contain exactly 256 bits",
        assertThrows(
                IllegalArgumentException.class,
                () -> new WebLogPayloadCodec("v2", new byte[31], "v1", null, null))
            .getMessage());
    assertEquals(
        "previous web log key and version must be paired",
        assertThrows(
                IllegalArgumentException.class,
                () -> new WebLogPayloadCodec("v2", current, null, previous, null))
            .getMessage());
    assertEquals(
        "web log key versions must be distinct",
        assertThrows(
                IllegalArgumentException.class,
                () -> new WebLogPayloadCodec("v2", current, "v2", previous, null))
            .getMessage());
    assertEquals(
        "random",
        assertThrows(
                NullPointerException.class,
                () -> new WebLogPayloadCodec("v2", current, "v1", previous, null))
            .getMessage());
    assertArrayEquals(sequence(32, 0), current);
    assertArrayEquals(sequence(32, 32), previous);
  }

  @Test
  void unavailableCipherProviderHasBoundedFailureAndNoRawProviderCause() throws Exception {
    EncryptedWebLogPayload payload = independentPayload("v2", CURRENT, goldenWire());
    Provider provider = Security.getProvider("SunJCE");
    int position = Arrays.asList(Security.getProviders()).indexOf(provider) + 1;
    assertTrue(position > 0);
    Security.removeProvider("SunJCE");
    try (WebLogPayloadCodec codec = fixedCodec("v2", CURRENT, null, null)) {
      assertReason(
          WebLogPayloadException.Reason.CRYPTO_UNAVAILABLE,
          () -> codec.encrypt(IDENTITY, goldenWire()));
      assertReason(
          WebLogPayloadException.Reason.PAYLOAD_INVALID, () -> codec.decrypt(IDENTITY, payload));
    } finally {
      assertNotEquals(-1, Security.insertProviderAt(provider, position));
    }
  }

  private static void assertInvalid(WebLogPayloadCodec codec, byte[] bytes) {
    assertReason(
        WebLogPayloadException.Reason.PAYLOAD_INVALID,
        () -> codec.decrypt(IDENTITY, new EncryptedWebLogPayload("v2", bytes)));
  }

  private static void assertReason(WebLogPayloadException.Reason reason, ThrowingCheck check) {
    WebLogPayloadException exception = assertThrows(WebLogPayloadException.class, check::run);
    assertEquals(reason, exception.reason());
    assertEquals("web log encrypted payload rejected: " + reason, exception.getMessage());
    assertNull(exception.getCause());
    assertFalse(exception.toString().contains(MESSAGE.toString()));
    assertFalse(exception.toString().contains("00010203"));
  }

  private static WebLogPayloadCodec fixedCodec(
      String currentVersion, byte[] currentKey, String previousVersion, byte[] previousKey) {
    return new WebLogPayloadCodec(
        currentVersion, currentKey, previousVersion, previousKey, new FixedNonceRandom());
  }

  private static EncryptedWebLogPayload independentPayload(String version, byte[] key, byte[] plain)
      throws Exception {
    return new EncryptedWebLogPayload(
        version, independentEnvelope(version, key, independentAad(IDENTITY, version), plain));
  }

  private static byte[] independentEnvelope(
      String version, byte[] key, byte[] aad, byte[] plaintext) throws Exception {
    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "AES"), new GCMParameterSpec(128, NONCE));
    cipher.updateAAD(aad);
    ByteArrayOutputStream output = new ByteArrayOutputStream();
    output.write("NKENC1".getBytes(StandardCharsets.US_ASCII));
    output.write(1);
    output.write(version.length());
    output.write(version.getBytes(StandardCharsets.US_ASCII));
    output.write(NONCE);
    output.write(cipher.doFinal(plaintext));
    return output.toByteArray();
  }

  private static byte[] independentAad(WebLogPayloadIdentity identity, String version)
      throws Exception {
    ByteArrayOutputStream output = new ByteArrayOutputStream();
    try (DataOutputStream data = new DataOutputStream(output)) {
      for (byte[] field :
          List.of(
              "web-log-outbox".getBytes(StandardCharsets.US_ASCII),
              "schubert_web_session.web_log_outbox".getBytes(StandardCharsets.US_ASCII),
              HexFormat.of().parseHex(identity.messageId().toString().replace("-", "")),
              HexFormat.of().parseHex(identity.correlationId().toString().replace("-", "")),
              new byte[] {1},
              version.getBytes(StandardCharsets.US_ASCII),
              "WLGEVT01".getBytes(StandardCharsets.US_ASCII),
              "001".getBytes(StandardCharsets.US_ASCII))) {
        data.writeInt(field.length);
        data.write(field);
      }
    }
    return output.toByteArray();
  }

  /** Golden UI 232 header and UI 235 data offsets; no production encoder builds the oracle. */
  static byte[] goldenWire() {
    byte[] wire = new byte[2_336];
    Arrays.fill(wire, (byte) ' ');
    ascii(wire, 0, "SCHBNK01001WLGEVT01001EI");
    ascii(wire, 24, MESSAGE.toString());
    ascii(wire, 60, CORRELATION.toString());
    ascii(wire, 96, "20260905060000000");
    ascii(wire, 177, "0256002080000000000000000002336");
    ascii(wire, 256, "20260905060000000");
    ascii(wire, 256 + 17, "REQUEST");
    ascii(wire, 256 + 33, "INFO");
    ascii(wire, 256 + 41, "HTTP_REQUEST_COMPLETED");
    ascii(wire, 256 + 105, "Synthetic HTTP request completed");
    ascii(wire, 256 + 617, "00000000-0000-0000-0000-000000000099");
    ascii(wire, 256 + 653, "GET");
    ascii(wire, 256 + 661, "/login");
    ascii(wire, 256 + 917, "200");
    ascii(wire, 256 + 920, "12");
    ascii(wire, 256 + 929, "127.0.0.1");
    ascii(wire, 256 + 1043, "{\"projection\":\"PENDING\"}");
    return wire;
  }

  private static void ascii(byte[] destination, int offset, String value) {
    byte[] ascii = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(ascii, 0, destination, offset, ascii.length);
  }

  private static byte[] sequence(int size, int start) {
    byte[] bytes = new byte[size];
    for (int index = 0; index < size; index++) {
      bytes[index] = (byte) (start + index);
    }
    return bytes;
  }

  @FunctionalInterface
  private interface ThrowingCheck {
    void run() throws Exception;
  }

  private static final class FixedNonceRandom extends SecureRandom {
    private static final long serialVersionUID = 1L;

    @Override
    public void nextBytes(byte[] bytes) {
      assertEquals(12, bytes.length);
      System.arraycopy(NONCE, 0, bytes, 0, NONCE.length);
    }
  }

  /** WEBLOG-OWN001/SSC420: direct Error is retained, then another worker uses the same codec. */
  @Test
  void weblogOwn001NonceErrorThenOtherWorkerMatchesIndependentGolden() throws Exception {
    var calls = new java.util.concurrent.atomic.AtomicInteger();
    var buffers = new ArrayList<byte[]>();
    var fatal = new AssertionError("PUBLIC nonce fault");
    var random =
        new SecureRandom() {
          private static final long serialVersionUID = 1L;

          @Override
          public void nextBytes(byte[] output) {
            buffers.add(output);
            System.arraycopy(NONCE, 0, output, 0, NONCE.length);
            if (calls.incrementAndGet() == 1) throw fatal;
          }
        };
    byte[] plaintext = goldenWire();
    byte[] before = plaintext.clone();
    byte[] expected = independentEnvelope("v2", CURRENT, independentAad(IDENTITY, "v2"), plaintext);
    var codec = new WebLogPayloadCodec("v2", CURRENT, null, null, random);
    var executor = Executors.newSingleThreadExecutor();
    try {
      org.junit.jupiter.api.Assertions.assertSame(
          fatal, assertThrows(AssertionError.class, () -> codec.encrypt(IDENTITY, plaintext)));
      assertEquals(1, calls.get());
      assertArrayEquals(new byte[12], buffers.getFirst());
      assertArrayEquals(before, plaintext);
      var actual =
          executor.submit(() -> codec.encrypt(IDENTITY, plaintext)).get(5, TimeUnit.SECONDS);
      assertArrayEquals(expected, actual.ciphertext());
      assertEquals(2, calls.get());
      assertEquals(2, buffers.size());
      org.junit.jupiter.api.Assertions.assertNotSame(buffers.getFirst(), buffers.getLast());
      for (byte[] bytes : buffers) assertArrayEquals(new byte[12], bytes);
      assertArrayEquals(before, plaintext);
    } finally {
      executor.shutdownNow();
      if (executor.awaitTermination(10, TimeUnit.SECONDS)) codec.close();
      else throw new AssertionError("PUBLIC encryption worker termination unconfirmed");
    }
  }
}
