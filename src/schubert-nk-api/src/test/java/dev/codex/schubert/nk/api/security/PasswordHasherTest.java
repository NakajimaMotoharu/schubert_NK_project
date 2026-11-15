package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicReference;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import org.junit.jupiter.api.Test;
import org.springframework.security.crypto.password.PasswordEncoder;

/** PT-AUT-002; independent JCA oracle, fixed 0..15 salt, no production method creates expected. */
final class PasswordHasherTest {
  private static final String SYNTHETIC_HASH =
      "{pbkdf2-v1}000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000";
  private final PasswordHasher hasher = new PasswordHasher();

  @Test
  void fixedSaltIndependentPbkdf2VectorAndNfcMatch() throws Exception {
    byte[] salt = new byte[16];
    for (int i = 0; i < salt.length; i++) salt[i] = (byte) i;
    String expected = independentHash("é".repeat(12), salt);
    char[] input = "e\u0301".repeat(12).toCharArray();
    assertTrue(hasher.matches(input, expected));
    assertArrayEquals(new char[input.length], input);
    assertFalse(hasher.matches("other".repeat(3).toCharArray(), expected));
    assertFalse(hasher.needsUpgrade(expected));
  }

  @Test
  void encodeUsesFreshSaltAndFull256BytePassword() throws Exception {
    String value = "é".repeat(128);
    char[] firstInput = value.toCharArray();
    String first = hasher.encode(firstInput);
    String second = hasher.encode(value.toCharArray());
    assertArrayEquals(new char[firstInput.length], firstInput);
    assertTrue(first.matches("\\{pbkdf2-v1}[0-9a-f]{96}"));
    byte[] firstBytes = HexFormat.of().parseHex(first.substring(11));
    assertEquals(independentHash(value, Arrays.copyOf(firstBytes, 16)), first);
    byte[] secondBytes = HexFormat.of().parseHex(second.substring(11));
    assertEquals(independentHash(value, Arrays.copyOf(secondBytes, 16)), second);
    assertFalse(Arrays.equals(Arrays.copyOf(firstBytes, 16), Arrays.copyOf(secondBytes, 16)));
    assertTrue(hasher.matches(value.toCharArray(), first));
    assertFalse(hasher.matches(("é".repeat(127) + "ê").toCharArray(), first));
  }

  @Test
  void invalidStoredGenerationAndInputsAreBoundedAndConsumed() {
    for (String stored :
        List.of(
            "",
            "{pbkdf2-v2}" + "0".repeat(96),
            "0".repeat(96),
            "{pbkdf2-v1}" + "0".repeat(95),
            "{pbkdf2-v1}" + "g".repeat(96))) {
      char[] input = "a".repeat(12).toCharArray();
      IllegalArgumentException failure =
          assertThrows(IllegalArgumentException.class, () -> hasher.matches(input, stored));
      assertArrayEquals(new char[input.length], input);
      assertEquals("stored password encoding is invalid or unsupported", failure.getMessage());
      assertNull(failure.getCause());
      assertThrows(IllegalArgumentException.class, () -> hasher.needsUpgrade(stored));
    }
    char[] input = "a".repeat(12).toCharArray();
    assertThrows(NullPointerException.class, () -> hasher.matches(input, null));
    assertArrayEquals(new char[input.length], input);
    assertThrows(NullPointerException.class, () -> hasher.encode(null));
    assertThrows(NullPointerException.class, () -> hasher.matches(null, ""));
    assertThrows(NullPointerException.class, () -> hasher.needsUpgrade(null));
    assertThrows(IllegalArgumentException.class, () -> hasher.encode(new char[0]));
  }

  @Test
  void hashfault001EncoderFailureConsumesCallerAndObservedNormalizedBuffer() {
    for (Throwable failure :
        List.of(
            new IllegalStateException("synthetic encoder fault"),
            new AssertionError("synthetic encoder fault"))) {
      var observed = new AtomicReference<CharSequence>();
      var encoder =
          new PasswordEncoder() {
            @Override
            public String encode(CharSequence raw) {
              observed.set(raw);
              throw encoderFailure(failure);
            }

            @Override
            public boolean matches(CharSequence raw, String stored) {
              observed.set(raw);
              throw encoderFailure(failure);
            }
          };
      var subject = new PasswordHasher(encoder);
      for (boolean matching : List.of(false, true)) {
        char[] input = "e\u0301".repeat(12).toCharArray();
        assertSame(
            failure,
            assertThrows(
                Throwable.class,
                () -> {
                  if (matching) subject.matches(input, SYNTHETIC_HASH);
                  else subject.encode(input);
                }));
        assertArrayEquals(new char[input.length], input);
        assertEquals("\0".repeat(12), Objects.requireNonNull(observed.get()).toString());
      }
    }
    assertThrows(NullPointerException.class, () -> new PasswordHasher(null));
  }

  private static RuntimeException encoderFailure(Throwable failure) {
    if (failure instanceof Error error) throw error;
    return (RuntimeException) failure;
  }

  private static String independentHash(String value, byte[] salt) throws Exception {
    PBEKeySpec spec = new PBEKeySpec(value.toCharArray(), salt, 310_000, 256);
    try {
      byte[] derived =
          SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).getEncoded();
      return "{pbkdf2-v1}" + HexFormat.of().formatHex(salt) + HexFormat.of().formatHex(derived);
    } finally {
      spec.clearPassword();
    }
  }
}
