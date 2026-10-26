package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.security.Provider;
import java.security.Security;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-IDEM-001/002 independent NKOP1 golden vectors and boundary cases. */
class OperationFingerprintTest {
  private static final String QUESTION_REQUEST_LAYOUT = "QSTREQ01";
  private static final String LAYOUT_VERSION = "001";
  private static final String QUESTION_SEVEN_TARGET = "QUESTION:7";
  private static final HexFormat HEX = HexFormat.of();
  private static final String GOLDEN_CANONICAL =
      "53434855424552542d4e4b2d4f5031"
          + "0000000137"
          + "000000085153545245513031"
          + "00000003303031"
          + "0000000a5155455354494f4e3a37"
          + "00000002"
          + "000000057469746c65"
          + "000000025831"
          + "ffffffff"
          + "00000004626f6479"
          + "000000025831"
          + "00000000";
  private static final String GOLDEN_HMAC =
      "605896204af0c777ef2911589343b4e4a50cd7aa87560662a5f634249240be81";

  @Test
  void goldenCanonicalAndHmacMatchIndependentOpenSslVector() {
    CanonicalRequest request = goldenRequest();
    byte[] key = HEX.parseHex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f");

    assertEquals(
        GOLDEN_CANONICAL, HEX.formatHex(OperationFingerprint.INSTANCE.canonicalBytes(request)));
    assertEquals(GOLDEN_HMAC, HEX.formatHex(OperationFingerprint.INSTANCE.calculate(request, key)));
    assertEquals(
        "CanonicalRequest[layoutId=QSTREQ01, layoutVersion=001, owner/target/fields=<redacted>]",
        request.toString());
  }

  @Test
  void nfcNormalizationAndNullEmptyDistinctionAreStable() {
    CanonicalRequest nfd =
        new CanonicalRequest(
            "u\u0308ser",
            QUESTION_REQUEST_LAYOUT,
            LAYOUT_VERSION,
            "cafe\u0301",
            List.of(new CanonicalField("value", "X1", "e\u0301".getBytes(StandardCharsets.UTF_8))));
    CanonicalRequest nfc =
        new CanonicalRequest(
            "\u00fcser",
            QUESTION_REQUEST_LAYOUT,
            LAYOUT_VERSION,
            "caf\u00e9",
            List.of(new CanonicalField("value", "X1", "e\u0301".getBytes(StandardCharsets.UTF_8))));
    CanonicalRequest nullValue =
        new CanonicalRequest(
            "7",
            QUESTION_REQUEST_LAYOUT,
            LAYOUT_VERSION,
            QUESTION_SEVEN_TARGET,
            List.of(new CanonicalField("v", "X1", null)));
    CanonicalRequest emptyValue =
        new CanonicalRequest(
            "7",
            QUESTION_REQUEST_LAYOUT,
            LAYOUT_VERSION,
            QUESTION_SEVEN_TARGET,
            List.of(new CanonicalField("v", "X1", new byte[0])));

    assertArrayEquals(
        OperationFingerprint.INSTANCE.canonicalBytes(nfd),
        OperationFingerprint.INSTANCE.canonicalBytes(nfc));
    assertFalse(
        java.util.Arrays.equals(
            OperationFingerprint.INSTANCE.canonicalBytes(nullValue),
            OperationFingerprint.INSTANCE.canonicalBytes(emptyValue)));
  }

  @Test
  void canonicalModelsDefensivelyCopyAndRedact() {
    byte[] secret = {1, 2, 3};
    CanonicalField field = new CanonicalField("body", "X1", secret);
    secret[0] = 9;
    byte[] first = field.value();
    first[1] = 9;
    ArrayList<CanonicalField> mutable = new ArrayList<>();
    mutable.add(field);
    CanonicalRequest request =
        new CanonicalRequest(
            "7", QUESTION_REQUEST_LAYOUT, LAYOUT_VERSION, QUESTION_SEVEN_TARGET, mutable);
    mutable.clear();

    assertArrayEquals(new byte[] {1, 2, 3}, field.value());
    assertEquals(1, request.fields().size());
    assertEquals("CanonicalField[name=body, typeVersion=X1, value=<redacted>]", field.toString());
    assertTrue(new CanonicalField("body", "X1", null).value() == null);
  }

  @Test
  void invalidModelsAndFingerprintArgumentsAreRejected() {
    assertThrows(NullPointerException.class, () -> new CanonicalField(null, "X1", null));
    assertThrows(NullPointerException.class, () -> new CanonicalField("v", null, null));
    assertThrows(IllegalArgumentException.class, () -> new CanonicalField("", "X1", null));
    assertThrows(IllegalArgumentException.class, () -> new CanonicalField("v", "?", null));
    assertThrows(
        NullPointerException.class,
        () -> new CanonicalRequest(null, QUESTION_REQUEST_LAYOUT, LAYOUT_VERSION, "t", List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () -> new CanonicalRequest("", QUESTION_REQUEST_LAYOUT, LAYOUT_VERSION, "t", List.of()));
    assertThrows(
        NullPointerException.class,
        () -> new CanonicalRequest("7", QUESTION_REQUEST_LAYOUT, LAYOUT_VERSION, null, List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () -> new CanonicalRequest("7", QUESTION_REQUEST_LAYOUT, LAYOUT_VERSION, "", List.of()));
    assertThrows(
        NullPointerException.class,
        () -> new CanonicalRequest("7", null, LAYOUT_VERSION, "t", List.of()));
    assertThrows(
        NullPointerException.class,
        () -> new CanonicalRequest("7", QUESTION_REQUEST_LAYOUT, null, "t", List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () -> new CanonicalRequest("7", "short", LAYOUT_VERSION, "t", List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () -> new CanonicalRequest("7", QUESTION_REQUEST_LAYOUT, "v1", "t", List.of()));
    assertThrows(
        NullPointerException.class,
        () -> new CanonicalRequest("7", QUESTION_REQUEST_LAYOUT, LAYOUT_VERSION, "t", null));
    assertThrows(
        NullPointerException.class,
        () ->
            new CanonicalRequest(
                "7",
                QUESTION_REQUEST_LAYOUT,
                LAYOUT_VERSION,
                "t",
                java.util.Arrays.asList((CanonicalField) null)));

    CanonicalRequest request = goldenRequest();
    assertThrows(
        NullPointerException.class,
        () -> OperationFingerprint.INSTANCE.calculate(null, new byte[32]));
    assertThrows(
        NullPointerException.class, () -> OperationFingerprint.INSTANCE.calculate(request, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> OperationFingerprint.INSTANCE.calculate(request, new byte[31]));
    assertThrows(
        NullPointerException.class, () -> OperationFingerprint.INSTANCE.canonicalBytes(null));
  }

  @Test
  void unavailableHmacProviderProducesTypedStartupFailure() {
    Provider provider = Security.getProvider("SunJCE");
    int position = providerPosition("SunJCE");
    Security.removeProvider("SunJCE");
    try {
      IllegalStateException failure =
          assertThrows(
              IllegalStateException.class,
              () -> OperationFingerprint.INSTANCE.calculate(goldenRequest(), new byte[32]));
      assertEquals("HMAC-SHA-256 is unavailable", failure.getMessage());
    } finally {
      assertNotEquals(-1, position);
      Security.insertProviderAt(provider, position);
    }
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

  private static CanonicalRequest goldenRequest() {
    return new CanonicalRequest(
        "7",
        QUESTION_REQUEST_LAYOUT,
        LAYOUT_VERSION,
        QUESTION_SEVEN_TARGET,
        List.of(
            new CanonicalField("title", "X1", null),
            new CanonicalField("body", "X1", new byte[0])));
  }
}
