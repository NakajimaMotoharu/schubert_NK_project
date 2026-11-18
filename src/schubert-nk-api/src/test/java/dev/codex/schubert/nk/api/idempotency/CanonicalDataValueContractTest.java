package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-IDEM-CANONVALUE001..006; SS324/352/354: synthetic data only, never HMAC/keyring/DB. */
final class CanonicalDataValueContractTest {
  private static final String FIELD = "field";
  private static final String RAW_TYPE = "B1";
  private static final String OWNER = "1";
  private static final String LAYOUT = "QRYREQ01";
  private static final String VERSION = "001";
  private static final String TARGET = "REQUEST:QRYREQ01";
  private static final String FP_VERSION = "v1";
  private static final String MARKER = "retained";
  private static final String MALFORMED = "canonical text contains malformed UTF-16";

  @Test
  void canonicalValue001RawNullableFieldMetadataCopyingAndTerminalWipeRemainDistinct() {
    byte[] input = {65, 0, -1};
    CanonicalField owned = new CanonicalField(FIELD, RAW_TYPE, input);
    try (owned) {
      byte[] output = owned.value();
      assertNotSame(input, output);
      assertArrayEquals(new byte[] {65, 0, -1}, output);
      input[0] = 99;
      output[2] = 33;
      assertArrayEquals(new byte[] {65, 0, -1}, owned.value());
      assertEquals(FIELD, owned.name());
      assertEquals(RAW_TYPE, owned.typeVersion());
      assertEquals("CanonicalField[<redacted>]", owned.toString());
    }
    assertArrayEquals(new byte[] {0, 0, 0}, owned.value());
    assertArrayEquals(new byte[] {99, 0, -1}, input);
    try (CanonicalField nil = new CanonicalField(FIELD, RAW_TYPE, null);
        CanonicalField equal = new CanonicalField(FIELD, RAW_TYPE, null);
        CanonicalField empty = new CanonicalField(FIELD, RAW_TYPE, new byte[0]);
        CanonicalField otherName = new CanonicalField("other", RAW_TYPE, null);
        CanonicalField otherType = new CanonicalField(FIELD, "OTHER", null)) {
      assertNull(nil.value());
      assertArrayEquals(new byte[0], empty.value());
      sameValue(nil, equal, List.of(empty, otherName, otherType));
    }
    for (String name : List.of("f", "_", "A0._-", "a".repeat(64))) {
      try (CanonicalField field = new CanonicalField(name, "t".repeat(32), null)) {
        assertEquals(name, field.name());
        assertEquals("t".repeat(32), field.typeVersion());
      }
    }
    for (String bad : List.of("", "a".repeat(65), "bad/name", "あ", "a\n")) {
      assertThrows(IllegalArgumentException.class, () -> new CanonicalField(bad, RAW_TYPE, null));
    }
    for (String bad : List.of("", "t".repeat(33), "bad:type", "あ", "t\n")) {
      assertThrows(IllegalArgumentException.class, () -> new CanonicalField(FIELD, bad, null));
    }
    assertThrows(NullPointerException.class, () -> new CanonicalField(null, RAW_TYPE, null));
    assertThrows(NullPointerException.class, () -> new CanonicalField(FIELD, null, null));
  }

  @Test
  void canonicalValue002TextAndSignedNumberFactoriesMatchIndependentFixedHexAndErrorPaths() {
    String[][] textVectors = {{"e\u0301", "c3a9"}, {"é", "c3a9"}, {"😀", "f09f9880"}, {"", ""}};
    for (String[] vector : textVectors) {
      try (CanonicalField field = CanonicalField.text(FIELD, vector[0])) {
        assertEquals(FIELD, field.name());
        assertEquals("X1", field.typeVersion());
        assertArrayEquals(HexFormat.of().parseHex(vector[1]), field.value());
      }
    }
    long[] numbers = {0, -1, Long.MAX_VALUE, Long.MIN_VALUE};
    String[] hex = {
      "30",
      "2d31",
      "39323233333732303336383534373735383037",
      "2d39323233333732303336383534373735383038"
    };
    for (int index = 0; index < numbers.length; index++) {
      try (CanonicalField field = CanonicalField.number(FIELD, numbers[index])) {
        assertEquals("N1", field.typeVersion());
        assertArrayEquals(HexFormat.of().parseHex(hex[index]), field.value());
      }
    }
    for (String malformed : List.of(String.valueOf((char) 0xd800), String.valueOf((char) 0xdc00))) {
      assertEquals(
          MALFORMED,
          assertThrows(IllegalArgumentException.class, () -> CanonicalField.text(FIELD, malformed))
              .getMessage());
    }
    assertThrows(NullPointerException.class, () -> CanonicalField.text(FIELD, null));
    assertThrows(NullPointerException.class, () -> CanonicalField.text(null, "PUBLIC"));
    assertThrows(IllegalArgumentException.class, () -> CanonicalField.text("bad/name", "PUBLIC"));
    assertThrows(NullPointerException.class, () -> CanonicalField.number(null, 0));
    assertThrows(IllegalArgumentException.class, () -> CanonicalField.number("bad/name", 0));
  }

  @Test
  void canonicalValue003RequiredTextAndLayoutMetadataApplyNfcBeforeAdmittingCanonicalData() {
    try (CanonicalRequest value =
            new CanonicalRequest(OWNER, LAYOUT, VERSION, "e\u0301😀", List.of());
        CanonicalRequest anonymous =
            new CanonicalRequest("ANONYMOUS", LAYOUT, VERSION, TARGET, List.of())) {
      assertEquals(OWNER, value.ownerScope());
      assertEquals("é😀", value.target());
      assertEquals("ANONYMOUS", anonymous.ownerScope());
      assertEquals(LAYOUT, value.layoutId());
      assertEquals(VERSION, value.layoutVersion());
    }
    assertEquals(
        "ownerScope must not be empty",
        assertThrows(
                IllegalArgumentException.class,
                () -> new CanonicalRequest("", LAYOUT, VERSION, TARGET, List.of()))
            .getMessage());
    assertEquals(
        "target must not be empty",
        assertThrows(
                IllegalArgumentException.class,
                () -> new CanonicalRequest(OWNER, LAYOUT, VERSION, "", List.of()))
            .getMessage());
    for (String malformed : List.of(String.valueOf((char) 0xd800), String.valueOf((char) 0xdc00))) {
      assertEquals(
          MALFORMED,
          assertThrows(
                  IllegalArgumentException.class,
                  () -> new CanonicalRequest(malformed, LAYOUT, VERSION, TARGET, List.of()))
              .getMessage());
      assertEquals(
          MALFORMED,
          assertThrows(
                  IllegalArgumentException.class,
                  () -> new CanonicalRequest(OWNER, LAYOUT, VERSION, malformed, List.of()))
              .getMessage());
    }
    for (String bad : List.of("", "QRYREQ0", "QRYREQ011", "qryreq01", "QRYREQ0_", "QRYREQ0\n")) {
      assertEquals(
          "layout identity is invalid",
          assertThrows(
                  IllegalArgumentException.class,
                  () -> new CanonicalRequest(OWNER, bad, VERSION, TARGET, List.of()))
              .getMessage());
    }
    for (String bad : List.of("", "01", "0000", "a01", "0 1", "00\n")) {
      assertThrows(
          IllegalArgumentException.class,
          () -> new CanonicalRequest(OWNER, LAYOUT, bad, TARGET, List.of()));
    }
    assertThrows(
        NullPointerException.class,
        () -> new CanonicalRequest(null, LAYOUT, VERSION, TARGET, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> new CanonicalRequest(OWNER, null, VERSION, TARGET, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> new CanonicalRequest(OWNER, LAYOUT, null, TARGET, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> new CanonicalRequest(OWNER, LAYOUT, VERSION, null, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> new CanonicalRequest(OWNER, LAYOUT, VERSION, TARGET, null));
    assertThrows(
        NullPointerException.class,
        () ->
            new CanonicalRequest(OWNER, LAYOUT, VERSION, TARGET, Collections.singletonList(null)));
  }

  @Test
  void canonicalValue004OrderedImmutableSnapshotAndAllRecordComponentsKeepOwnerCleanupObservable() {
    byte[] firstInput = {1, 2};
    byte[] secondInput = {3};
    try (CanonicalField first = new CanonicalField("first", RAW_TYPE, firstInput);
        CanonicalField second = new CanonicalField("second", RAW_TYPE, secondInput)) {
      ArrayList<CanonicalField> caller = new ArrayList<>(List.of(first, second));
      try (CanonicalRequest request =
          new CanonicalRequest(OWNER, LAYOUT, VERSION, TARGET, caller)) {
        caller.clear();
        assertEquals(2, request.fields().size());
        assertSame(first, request.fields().get(0));
        assertSame(second, request.fields().get(1));
        assertThrows(UnsupportedOperationException.class, () -> request.fields().add(first));
        assertEquals("CanonicalRequest[<redacted>]", request.toString());
      }
      assertArrayEquals(new byte[] {0, 0}, first.value());
      assertArrayEquals(new byte[] {0}, second.value());
    }
    assertArrayEquals(new byte[] {1, 2}, firstInput);
    assertArrayEquals(new byte[] {3}, secondInput);
    try (CanonicalRequest value = request(OWNER, LAYOUT, VERSION, TARGET, FIELD);
        CanonicalRequest equal = request(OWNER, LAYOUT, VERSION, TARGET, FIELD);
        CanonicalRequest owner = request("2", LAYOUT, VERSION, TARGET, FIELD);
        CanonicalRequest layout = request(OWNER, "NTFREQ01", VERSION, TARGET, FIELD);
        CanonicalRequest version = request(OWNER, LAYOUT, "002", TARGET, FIELD);
        CanonicalRequest target = request(OWNER, LAYOUT, VERSION, "REQUEST:NTFREQ01", FIELD);
        CanonicalRequest fields = request(OWNER, LAYOUT, VERSION, TARGET, "other")) {
      sameValue(value, equal, List.of(owner, layout, version, target, fields));
    }
  }

  @Test
  void canonicalValue005SyntheticDigestMetadataIsClonedRedactedAndNeverCalculatesAFingerprint() {
    byte[] expected = new byte[32];
    Arrays.fill(expected, (byte) 7);
    byte[] input = expected.clone();
    Fingerprint value = new Fingerprint(FP_VERSION, input);
    byte[] output = value.digest();
    assertNotSame(input, output);
    assertArrayEquals(expected, output);
    Map<Fingerprint, String> retained = Map.of(value, MARKER);
    int hashBefore = value.hashCode();
    input[0] = 99;
    output[1] = 88;
    assertArrayEquals(expected, value.digest());
    assertEquals(MARKER, retained.get(value));
    assertEquals(hashBefore, value.hashCode());
    assertEquals(FP_VERSION, value.keyVersion());
    assertEquals("Fingerprint[<redacted>]", value.toString());
    assertEquals("Fingerprint[<redacted>]", new Fingerprint("v2", expected).toString());
    assertEquals(value, value);
    assertNotEquals(value, null);
    assertNotEquals(value, VERSION);
    assertNotEquals(value, new Fingerprint("v2", expected));
    assertNotEquals(value, new Fingerprint(FP_VERSION, new byte[32]));
    for (String version : List.of("a", "A1", "1", "a".repeat(16))) {
      assertEquals(version, new Fingerprint(version, expected).keyVersion());
    }
    for (String invalid : List.of("", "_v", ".v", "-v", "a".repeat(17), "v\n", "あ")) {
      assertEquals(
          "fingerprint metadata is invalid",
          assertThrows(IllegalArgumentException.class, () -> new Fingerprint(invalid, expected))
              .getMessage());
    }
    for (int size : new int[] {0, 31, 33}) {
      byte[] invalid = new byte[size];
      assertThrows(IllegalArgumentException.class, () -> new Fingerprint(FP_VERSION, invalid));
    }
    assertThrows(NullPointerException.class, () -> new Fingerprint(null, expected));
    assertThrows(NullPointerException.class, () -> new Fingerprint(FP_VERSION, null));
  }

  @Test
  void canonicalValue006VerificationCatalogIsClosedAndItsFactoriesKeepIndependentArrays() {
    String[] names = {"MATCH", "MISMATCH", "KEY_UNAVAILABLE"};
    FingerprintVerification[] values = FingerprintVerification.values();
    assertArrayEquals(names, Arrays.stream(values).map(Enum::name).toArray(String[]::new));
    for (int i = 0; i < names.length; i++) {
      assertEquals(i, values[i].ordinal());
      assertSame(values[i], FingerprintVerification.valueOf(names[i]));
    }
    FingerprintVerification[] copy = FingerprintVerification.values();
    assertNotSame(values, copy);
    copy[0] = null;
    assertSame(FingerprintVerification.MATCH, FingerprintVerification.values()[0]);
    for (String unknown : List.of("", "match", "MATCH ", "unknown")) {
      assertThrows(IllegalArgumentException.class, () -> FingerprintVerification.valueOf(unknown));
    }
    assertThrows(NullPointerException.class, () -> FingerprintVerification.valueOf(null));
  }

  private static CanonicalRequest request(
      String owner, String layout, String version, String target, String field) {
    return new CanonicalRequest(
        owner, layout, version, target, List.of(new CanonicalField(field, RAW_TYPE, null)));
  }

  private static <T> void sameValue(T value, T equal, List<T> different) {
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertEquals(value.hashCode(), equal.hashCode());
    assertEquals(MARKER, Map.of(value, MARKER).get(equal));
    assertNotEquals(value, null);
    assertNotEquals(value, VERSION);
    for (T other : different) {
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
  }
}
