package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-IDEM-WIPE-001..004; synthetic buffers only, no reflection or actual heap/credential dump. */
final class SecretBufferTest {
  private static final int MAXIMUM_FIXTURE_CAPACITY = 1_050_000;
  private static final String REDACTED = "WipingByteArrayOutputStream[<redacted>]";
  private static final String ANONYMOUS_OWNER = "ANONYMOUS";
  private static final String LOGIN_REQUEST_LAYOUT = "LGNREQ01";
  private static final String LAYOUT_VERSION = "001";

  @Test
  void supersededAndCurrentStreamStorageAreWipedAtGrowthResetAndClose() {
    try (var stream = new Inspectable()) {

      byte[] original = stream.storage();
      byte[] fixture = new byte[8192];
      Arrays.fill(fixture, (byte) 17);
      stream.writeBytes(fixture);
      assertArrayEquals(fixture, stream.toByteArray());
      stream.write(18);
      assertArrayEquals(new byte[original.length], original);
      byte[] expanded = stream.storage();
      byte[] expected = Arrays.copyOf(fixture, 8193);
      expected[8192] = 18;
      assertArrayEquals(expected, stream.toByteArray());
      stream.reset();
      assertArrayEquals(new byte[expanded.length], expanded);
      assertEquals(0, stream.size());
      stream.write(new byte[] {8, 9, 10, 11}, 1, 2);
      assertArrayEquals(new byte[] {9, 10}, stream.toByteArray());
      assertEquals(REDACTED, stream.toString());
      byte[] returnedCopy = stream.toByteArray();
      assertDoesNotThrow(stream::close);
      assertDoesNotThrow(stream::close);
      assertArrayEquals(new byte[expanded.length], expanded);
      assertArrayEquals(
          new byte[] {9, 10}, returnedCopy); // Explicit caller ownership, not an alias.
      assertEquals(0, stream.size());
      Arrays.fill(returnedCopy, (byte) 0);
    }
  }

  @Test
  void diagnosticIsIdenticalAcrossDifferentSizesAndAfterWiping() {
    try (var stream = new Inspectable()) {
      assertEquals(REDACTED, String.valueOf(stream));
      stream.writeBytes(new byte[] {71, 82, 93});
      assertEquals(3, stream.size());
      assertEquals(REDACTED, String.valueOf(stream));
      stream.write(104);
      assertEquals(4, stream.size());
      assertEquals(REDACTED, String.valueOf(stream));
      stream.reset();
      assertEquals(0, stream.size());
      assertEquals(REDACTED, String.valueOf(stream));
    }
  }

  @Test
  void streamBoundsAndExceptionalExitWipeAllOwnedCapacity() {
    for (int length : new int[] {0, 8191, 8192, 8193, 1_050_000}) {
      byte[] fixture = new byte[length];
      Arrays.fill(fixture, (byte) 22);
      var stream = new Inspectable();
      try (stream) {
        stream.writeBytes(fixture);
        assertArrayEquals(fixture, stream.toByteArray());
        assertThrows(NullPointerException.class, () -> stream.write(null, 0, 0));
        assertThrows(IndexOutOfBoundsException.class, () -> stream.write(new byte[1], -1, 1));
        assertThrows(IndexOutOfBoundsException.class, () -> stream.write(new byte[1], 0, 2));
        assertThrows(IllegalArgumentException.class, () -> stream.writeBytes(new byte[1_050_001]));
        if (length == MAXIMUM_FIXTURE_CAPACITY)
          assertThrows(IllegalArgumentException.class, () -> stream.write(1));
        assertArrayEquals(fixture, stream.toByteArray());
      }
      assertArrayEquals(new byte[stream.storage().length], stream.storage());
    }
    var failing = new Inspectable();
    assertThrows(
        IllegalArgumentException.class,
        () -> {
          try (failing) {
            failing.write(17);
            failing.writeBytes(new byte[1_050_000]);
          }
        });
    assertArrayEquals(new byte[failing.storage().length], failing.storage());
  }

  @Test
  void requestOwnerClosesEveryFieldWithoutModifyingCallerCopiesOrFingerprint() throws Exception {
    byte[] input = {1, 2, 3};
    try (var value = new CanonicalField("password", "X1", input);
        var absent = new CanonicalField("absent", "X1", null);
        var empty = new CanonicalField("empty", "X1", new byte[0]);
        var request =
            new CanonicalRequest(
                ANONYMOUS_OWNER,
                LOGIN_REQUEST_LAYOUT,
                LAYOUT_VERSION,
                "LOGIN:synthetic",
                List.of(value, absent, empty))) {

      byte[] copy = value.value();
      byte[] expected = independentHmac();
      assertArrayEquals(expected, OperationFingerprint.INSTANCE.calculate(request, new byte[32]));
      try (request) {
        assertArrayEquals(new byte[] {1, 2, 3}, value.value());
      }
      assertDoesNotThrow(request::close);
      assertArrayEquals(new byte[3], value.value());
      assertArrayEquals(new byte[] {1, 2, 3}, input);
      assertArrayEquals(new byte[] {1, 2, 3}, copy);
      assertNull(absent.value());
      assertArrayEquals(new byte[0], empty.value());
      // This test's JCA/DataOutputStream oracle and the existing OpenSSL vector are independent.
      Arrays.fill(copy, (byte) 0);
      Arrays.fill(input, (byte) 0);
      Arrays.fill(expected, (byte) 0);
      var exceptionallyClosed = new CanonicalField("value", "X1", new byte[] {17});
      assertThrows(
          IllegalArgumentException.class,
          () -> {
            try (var invalid =
                new CanonicalRequest(
                    ANONYMOUS_OWNER,
                    LOGIN_REQUEST_LAYOUT,
                    LAYOUT_VERSION,
                    "LOGIN:synthetic",
                    List.of(exceptionallyClosed))) {
              OperationFingerprint.INSTANCE.calculate(invalid, new byte[0]);
            }
          });
      assertArrayEquals(new byte[1], exceptionallyClosed.value());
      for (var large :
          List.of(
              new CanonicalRequest(
                  ANONYMOUS_OWNER,
                  LOGIN_REQUEST_LAYOUT,
                  LAYOUT_VERSION,
                  "t".repeat(1_050_000),
                  List.of()),
              new CanonicalRequest(
                  ANONYMOUS_OWNER,
                  LOGIN_REQUEST_LAYOUT,
                  LAYOUT_VERSION,
                  "t",
                  List.of(new CanonicalField("value", "X1", new byte[1_050_000]))))) {
        try (large) {
          assertThrows(
              IllegalArgumentException.class,
              () -> OperationFingerprint.INSTANCE.calculate(large, new byte[32]));
        }
      }
    }
  }

  private static byte[] independentHmac() throws Exception {
    var buffer = new java.io.ByteArrayOutputStream();
    var out = new java.io.DataOutputStream(buffer);
    out.write("SCHUBERT-NK-OP1".getBytes(java.nio.charset.StandardCharsets.US_ASCII));
    for (String text :
        new String[] {ANONYMOUS_OWNER, LOGIN_REQUEST_LAYOUT, LAYOUT_VERSION, "LOGIN:synthetic"})
      lp(out, text);
    out.writeInt(3);
    lp(out, "password");
    lp(out, "X1");
    out.writeInt(3);
    out.write(new byte[] {1, 2, 3});
    lp(out, "absent");
    lp(out, "X1");
    out.writeInt(-1);
    lp(out, "empty");
    lp(out, "X1");
    out.writeInt(0);
    var mac = javax.crypto.Mac.getInstance("HmacSHA256");
    mac.init(new javax.crypto.spec.SecretKeySpec(new byte[32], "HmacSHA256"));
    return mac.doFinal(buffer.toByteArray());
  }

  private static void lp(java.io.DataOutputStream out, String text) throws java.io.IOException {
    byte[] bytes = text.getBytes(java.nio.charset.StandardCharsets.UTF_8);
    out.writeInt(bytes.length);
    out.write(bytes);
  }

  // ByteArrayOutputStream explicitly provides protected storage for subclasses. This seam verifies
  // secret erasure as a security contract, not a reflective reach into private coverage-only state.
  private static final class Inspectable extends WipingByteArrayOutputStream {
    byte[] storage() {
      return buf;
    }
  }
}
