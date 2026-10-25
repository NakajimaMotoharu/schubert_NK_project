package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Locale;
import org.junit.jupiter.api.Test;

/** PT-AUT-NAME-001..003, UI226/242 literal oracle, SSC-014/BUG-028/YKT-025. */
final class LoginUsernameTest {
  @Test
  void normalizesNfcTrimAndLocaleIndependentKeyWithoutChangingDisplay() {
    assertEquals("ÉCOLE", new LoginUsername("  E\u0301COLE  ").value());
    assertEquals("école", new LoginUsername("  E\u0301COLE  ").key());
    assertEquals("ος", new LoginUsername("ΟΣ").key()); // Context-sensitive final sigma.
    assertEquals("οσα", new LoginUsername("ΟΣΑ").key());
    Locale original = Locale.getDefault();
    try {
      Locale.setDefault(Locale.forLanguageTag("tr-TR"));
      assertEquals("input", new LoginUsername("INPUT").key());
      assertEquals("i\u0307".repeat(32), new LoginUsername("\u0130".repeat(32)).key());
      assertEquals("\u0130".repeat(32), new LoginUsername("\u0130".repeat(32)).value());
    } finally {
      Locale.setDefault(original);
    }
    assertEquals("LoginUsername[REDACTED]", new LoginUsername("synthetic").toString());
  }

  @Test
  void displayBoundaryNullBlankControlAndSurrogateContractsAreExplicit() {
    for (String text : List.of("a", "a".repeat(64), "あ".repeat(21) + "a", "😀".repeat(16))) {
      assertEquals(text, new LoginUsername(text).value());
    }
    assertThrows(NullPointerException.class, () -> new LoginUsername(null));
    for (String text :
        List.of(
            "",
            "  ",
            "\u2003",
            "a".repeat(65),
            "あ".repeat(22),
            "a\nb",
            "a\u007fb",
            "a\ud800b",
            "a\udfffb")) {
      var failure = assertThrows(IllegalArgumentException.class, () -> new LoginUsername(text));
      assertTrue(
          java.util.Set.of(
                  "username display length is invalid", "username contains an invalid character")
              .contains(failure.getMessage()));
    }
  }

  @Test
  void java25ScalarLowercaseExpansionFitsTheIndependentNinetySixByteBound() {
    int maximumNumerator = 1;
    int maximumDenominator = 1;
    int maximumScalar = 0;
    for (int scalar = 0; scalar <= Character.MAX_CODE_POINT; scalar++) {
      if (scalar >= 0xd800 && scalar <= 0xdfff) continue;
      String input = Character.toString(scalar);
      int before = input.getBytes(StandardCharsets.UTF_8).length;
      int after = input.toLowerCase(Locale.ROOT).getBytes(StandardCharsets.UTF_8).length;
      assertTrue(after * 2 <= before * 3, "JDK lowercase expansion needs SS review");
      if (after * maximumDenominator > before * maximumNumerator) {
        maximumNumerator = after;
        maximumDenominator = before;
        maximumScalar = scalar;
      }
    }
    assertEquals(3, maximumNumerator);
    assertEquals(2, maximumDenominator);
    assertEquals(0x0130, maximumScalar);
    assertEquals(
        96, new LoginUsername("\u0130".repeat(32)).key().getBytes(StandardCharsets.UTF_8).length);
  }
}
