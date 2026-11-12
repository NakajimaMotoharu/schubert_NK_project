package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.OptionalLong;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-IDEM-PUBLIC-001..008; SS324/352; independent public byte values, no crypto or authority. */
public final class PublicCanonicalAadValueTest {
  private static final String FIELD_LABEL = "label";
  private static final String RESPONSE_LAYOUT = "QSSRSP01";
  private static final String RESPONSE_VERSION = "001";
  private static final String INVALID_METADATA = "canonical field metadata is invalid";
  private static final UUID ID = UUID.fromString("00112233-4455-6677-8899-aabbccddeeff");
  private static final String AAD_PREFIX =
      "000000126170692d696e626f782d726573706f6e7365"
          + "0000001673636875626572742e726571756573745f696e626f78"
          + "0000001000112233445566778899aabbccddeeff"
          + "0000000101"
          + "000000027631"
          + "000000085153535253503031"
          + "00000003303031";
  private static final byte[] ANONYMOUS = HexFormat.of().parseHex(AAD_PREFIX + "00000000");
  private static final byte[] MINIMUM =
      HexFormat.of().parseHex(AAD_PREFIX + "000000080000000000000001");
  private static final byte[] MAXIMUM =
      HexFormat.of().parseHex(AAD_PREFIX + "00000008000000e8d4a50fff");

  @Test
  void public001MetadataNullLexicalAndLengthBoundaries() {
    for (String[] pair :
        new String[][] {{"a", "1"}, {"a".repeat(64), "V".repeat(32)}, {"a._-09", "V._-09"}}) {
      try (var field = new CanonicalField(pair[0], pair[1], null)) {
        assertEquals(pair[0], field.name());
        assertEquals(pair[1], field.typeVersion());
      }
    }
    assertThrows(NullPointerException.class, () -> new CanonicalField(null, "X1", null));
    assertThrows(NullPointerException.class, () -> new CanonicalField("a", null, null));
    for (String bad : List.of("", "a".repeat(65), "/", "é", "a\n", "a b")) {
      var error =
          assertThrows(IllegalArgumentException.class, () -> new CanonicalField(bad, "X1", null));
      assertEquals(INVALID_METADATA, error.getMessage());
    }
    for (String bad : List.of("", "V".repeat(33), "/", "é", "X1\n", "X 1")) {
      var error =
          assertThrows(IllegalArgumentException.class, () -> new CanonicalField("a", bad, null));
      assertEquals(INVALID_METADATA, error.getMessage());
    }
  }

  @Test
  void public002CopiesNullEmptyAndTerminalWiping() {
    var absent = new CanonicalField("a", "X1", null);
    try (var empty = new CanonicalField("a", "X1", new byte[0])) {
      assertNull(absent.value());
      assertArrayEquals(new byte[0], empty.value());
      absent.close();
      assertNull(absent.value());
    }
    byte[] input = {1, 2, 3};
    var field = new CanonicalField("a", "X1", input);
    try {
      input[0] = 99;
      assertArrayEquals(new byte[] {1, 2, 3}, field.value());
      byte[] copied = field.value();
      assertNotNull(copied);
      copied[1] = 99;
      assertArrayEquals(new byte[] {1, 2, 3}, field.value());
      field.close();
      assertArrayEquals(new byte[] {0, 0, 0}, field.value());
      field.close();
      assertArrayEquals(new byte[] {0, 0, 0}, field.value());
      assertArrayEquals(new byte[] {99, 2, 3}, input);
    } finally {
      field.close();
    }
  }

  @Test
  void public003NfcUtf8AndIndependentSignedDecimalLiterals() {
    try (var field = CanonicalField.text(FIELD_LABEL, "e\u0301日本")) {
      assertEquals(FIELD_LABEL, field.name());
      assertEquals("X1", field.typeVersion());
      assertArrayEquals(HexFormat.of().parseHex("c3a9e697a5e69cac"), field.value());
    }
    assertThrows(NullPointerException.class, () -> CanonicalField.text(FIELD_LABEL, null));
    long[] numbers = {Long.MIN_VALUE, -1, 0, Long.MAX_VALUE};
    String[] expected = {"-9223372036854775808", "-1", "0", "9223372036854775807"};
    for (int i = 0; i < numbers.length; i++) {
      try (var field = CanonicalField.number("count", numbers[i])) {
        assertEquals("N1", field.typeVersion());
        assertArrayEquals(expected[i].getBytes(StandardCharsets.US_ASCII), field.value());
      }
    }
  }

  @Test
  void public004DiagnosticNeverContainsSyntheticValue() {
    for (byte[] value :
        new byte[][] {null, new byte[0], "PUBLIC_ONLY".getBytes(StandardCharsets.US_ASCII)}) {
      try (var field = new CanonicalField(FIELD_LABEL, "X1", value)) {
        assertEquals(
            "CanonicalField[name=label, typeVersion=X1, value=<redacted>]", field.toString());
        assertFalse(field.toString().contains("PUBLIC_ONLY"));
      }
    }
  }

  @Test
  void public005IdentityRejectsMissingMalformedAndOutOfRangeValues() {
    assertThrows(
        NullPointerException.class,
        () ->
            new ResponseSnapshotIdentity(
                null, RESPONSE_LAYOUT, RESPONSE_VERSION, OptionalLong.empty()));
    assertThrows(
        NullPointerException.class,
        () -> new ResponseSnapshotIdentity(ID, null, RESPONSE_VERSION, OptionalLong.empty()));
    assertThrows(
        NullPointerException.class,
        () -> new ResponseSnapshotIdentity(ID, RESPONSE_LAYOUT, null, OptionalLong.empty()));
    assertThrows(
        NullPointerException.class,
        () -> new ResponseSnapshotIdentity(ID, RESPONSE_LAYOUT, RESPONSE_VERSION, null));
    for (String layout : List.of("", "QSSRSP0", "QSSRSP001", "qssrsp01", "QSSRSP0_")) {
      var error =
          assertThrows(
              IllegalArgumentException.class,
              () -> ResponseSnapshotIdentity.anonymous(ID, layout, RESPONSE_VERSION));
      assertEquals("responseLayoutId is invalid", error.getMessage());
    }
    for (String version : List.of("", "00", "0000", "x01", "０01")) {
      var error =
          assertThrows(
              IllegalArgumentException.class,
              () -> ResponseSnapshotIdentity.anonymous(ID, RESPONSE_LAYOUT, version));
      assertEquals("responseVersion is invalid", error.getMessage());
    }
    for (long owner : new long[] {-1, 0, 1_000_000_000_000L}) {
      var error =
          assertThrows(
              IllegalArgumentException.class,
              () ->
                  ResponseSnapshotIdentity.authenticated(
                      ID, RESPONSE_LAYOUT, RESPONSE_VERSION, owner));
      assertEquals("ownerUserId is outside N12", error.getMessage());
    }
  }

  @Test
  void public006FactoriesRetainOnlyDataAndRedactDiagnostic() {
    var anonymous = ResponseSnapshotIdentity.anonymous(ID, RESPONSE_LAYOUT, RESPONSE_VERSION);
    assertSame(ID, anonymous.requestMessageId());
    assertEquals(RESPONSE_LAYOUT, anonymous.responseLayoutId());
    assertEquals(RESPONSE_VERSION, anonymous.responseVersion());
    assertEquals(OptionalLong.empty(), anonymous.ownerUserId());
    for (long owner : new long[] {1, 999_999_999_999L}) {
      var authenticated =
          ResponseSnapshotIdentity.authenticated(ID, RESPONSE_LAYOUT, RESPONSE_VERSION, owner);
      assertEquals(OptionalLong.of(owner), authenticated.ownerUserId());
      assertEquals(
          "ResponseSnapshotIdentity[request/layout/version/owner=<redacted>]",
          authenticated.toString());
    }
    assertEquals(
        "ResponseSnapshotIdentity[request/layout/version/owner=<redacted>]", anonymous.toString());
  }

  @Test
  void public007AadMatchesIndependentWholeByteVectorsAndNewBuffers() {
    var anonymous = ResponseSnapshotIdentity.anonymous(ID, RESPONSE_LAYOUT, RESPONSE_VERSION);
    assertEquals(102, ANONYMOUS.length);
    assertArrayEquals(ANONYMOUS, anonymous.aad((byte) 1, "v1"));
    assertEquals(110, MINIMUM.length);
    assertEquals(110, MAXIMUM.length);
    assertArrayEquals(
        MINIMUM,
        ResponseSnapshotIdentity.authenticated(ID, RESPONSE_LAYOUT, RESPONSE_VERSION, 1)
            .aad((byte) 1, "v1"));
    assertArrayEquals(
        MAXIMUM,
        ResponseSnapshotIdentity.authenticated(
                ID, RESPONSE_LAYOUT, RESPONSE_VERSION, 999_999_999_999L)
            .aad((byte) 1, "v1"));
    byte[] changed = anonymous.aad((byte) 1, "v1");
    changed[0] = 99;
    assertArrayEquals(ANONYMOUS, anonymous.aad((byte) 1, "v1"));
    assertThrows(NullPointerException.class, () -> anonymous.aad((byte) 1, null));
  }

  @Test
  void public008ConcurrentValueCallsUseIndependentOwnedBuffers() throws Exception {
    var identity = ResponseSnapshotIdentity.authenticated(ID, RESPONSE_LAYOUT, RESPONSE_VERSION, 1);
    var pool = Executors.newFixedThreadPool(4);
    try {
      var tasks = new ArrayList<Callable<byte[]>>();
      for (int i = 0; i < 32; i++) tasks.add(() -> identity.aad((byte) 1, "v1"));
      byte[] previous = null;
      for (var result : pool.invokeAll(tasks, 10, TimeUnit.SECONDS)) {
        byte[] actual = result.get(5, TimeUnit.SECONDS);
        assertArrayEquals(MINIMUM, actual);
        if (previous != null) assertNotSame(previous, actual);
        previous = actual;
      }
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void public009MalformedUtf16AndFactoryMetadataFailuresKeepIndependentContracts() {
    for (String raw : List.of("\uD800", "\uDC00", "a\uDBFF", "\uDFFFz")) {
      var failure =
          assertThrows(IllegalArgumentException.class, () -> CanonicalField.text(FIELD_LABEL, raw));
      assertEquals("canonical text contains malformed UTF-16", failure.getMessage());
    }
    var textMetadata =
        assertThrows(IllegalArgumentException.class, () -> CanonicalField.text("/", "PUBLIC"));
    assertEquals(INVALID_METADATA, textMetadata.getMessage());
    var numberMetadata =
        assertThrows(IllegalArgumentException.class, () -> CanonicalField.number("/", -1));
    assertEquals(INVALID_METADATA, numberMetadata.getMessage());
    try (var field = CanonicalField.text(FIELD_LABEL, "😀")) {
      assertArrayEquals(HexFormat.of().parseHex("f09f9880"), field.value());
    }
  }
}
