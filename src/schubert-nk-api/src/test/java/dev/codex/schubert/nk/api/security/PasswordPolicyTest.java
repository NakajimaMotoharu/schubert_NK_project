package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-AUT-001; literal Unicode/byte/length oracles from UI226 and SS314, no production expected. */
final class PasswordPolicyTest {
  private static final String SYNTHETIC_USERNAME = "user";
  private final PasswordPolicy policy = new PasswordPolicy();

  @Test
  void loginAndCreationBoundariesDifferAndInputsAreConsumed() {
    for (String value :
        List.of("a", "a".repeat(11), "a".repeat(12), "a".repeat(128), "a".repeat(256))) {
      char[] input = value.toCharArray();
      assertArrayEquals(value.toCharArray(), policy.normalizeForLogin(input));
      assertArrayEquals(new char[input.length], input);
    }
    for (String value :
        List.of("a".repeat(12), "a".repeat(128), "é".repeat(128), "😀".repeat(64))) {
      char[] input = value.toCharArray();
      assertArrayEquals(value.toCharArray(), policy.normalizeForCreation(input, "different-user"));
      assertArrayEquals(new char[input.length], input);
    }
    for (String value :
        List.of("a".repeat(11), "a".repeat(129), "é".repeat(128) + "a", "a".repeat(257))) {
      char[] input = value.toCharArray();
      assertThrows(
          IllegalArgumentException.class,
          () -> policy.normalizeForCreation(input, SYNTHETIC_USERNAME));
      assertArrayEquals(new char[input.length], input);
    }
  }

  @Test
  void nfcSupplementaryAndUsernameComparisonUseExplicitValues() {
    assertArrayEquals(
        "é".repeat(12).toCharArray(),
        policy.normalizeForCreation("e\u0301".repeat(12).toCharArray(), SYNTHETIC_USERNAME));
    assertArrayEquals(
        "😀".repeat(12).toCharArray(),
        policy.normalizeForCreation("😀".repeat(12).toCharArray(), SYNTHETIC_USERNAME));
    for (String username : List.of("abcdefghijkl", "ABCDEFGHIJKL", " ABCDEFGHIJKL ")) {
      assertThrows(
          IllegalArgumentException.class,
          () -> policy.normalizeForCreation("abcdefghijkl".toCharArray(), username));
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> policy.normalizeForCreation("é".repeat(12).toCharArray(), "E\u0301".repeat(12)));
    // SS314 does not require mixed character classes or a common-password list.
    assertArrayEquals(
        "1".repeat(12).toCharArray(),
        policy.normalizeForCreation("1".repeat(12).toCharArray(), SYNTHETIC_USERNAME));
  }

  @Test
  void malformedControlAndNullContractsRejectWithoutRetainingInput() {
    for (String value :
        List.of("", "a ", "a\n", "a\t", "a\u0000", "a\u007f", "a\u0085", "a\ud800", "a\udfff")) {
      char[] input = value.toCharArray();
      IllegalArgumentException failure =
          assertThrows(IllegalArgumentException.class, () -> policy.normalizeForLogin(input));
      assertArrayEquals(new char[input.length], input);
      assertNull(failure.getCause());
      assertFalse(failure.getMessage().contains("a\n"));
    }
    char[] input = "a".repeat(12).toCharArray();
    assertThrows(NullPointerException.class, () -> policy.normalizeForCreation(input, null));
    assertArrayEquals(new char[input.length], input);
    assertThrows(NullPointerException.class, () -> policy.normalizeForLogin(null));
    assertThrows(
        NullPointerException.class, () -> policy.normalizeForCreation(null, SYNTHETIC_USERNAME));
  }
}
