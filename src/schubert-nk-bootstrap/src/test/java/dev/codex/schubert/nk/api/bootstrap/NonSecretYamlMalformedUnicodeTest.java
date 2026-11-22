package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrowsExactly;

import dev.codex.schubert.nk.web.bootstrap.WebNonSecretConfig;
import java.security.NoSuchAlgorithmException;
import org.junit.jupiter.api.Test;

/** SS343 shared YAML input. PT-OPS-APICFG009 / PT-OPS-WEBCFG009. */
final class NonSecretYamlMalformedUnicodeTest {
  private static final String MODE = "nk.monitoring.mode";

  @Test
  void apiRejectsIsolatedUtf16Surrogates() throws NoSuchAlgorithmException {
    assertEquals("DEBUG", ApiNonSecretConfig.parse(yaml("\uD83D\uDE42"), "").value(MODE));
    for (char isolated : new char[] {'\uD800', '\uDFFF'}) {
      var failure =
          assertThrowsExactly(
              IllegalArgumentException.class,
              () -> ApiNonSecretConfig.parse(yaml(String.valueOf(isolated)), ""));
      assertDiagnostic("API non-secret configuration unavailable", failure);
    }
  }

  @Test
  void webRejectsIsolatedUtf16Surrogates() throws NoSuchAlgorithmException {
    assertEquals("DEBUG", WebNonSecretConfig.parse(yaml("\uD83D\uDE42"), "").value(MODE));
    for (char isolated : new char[] {'\uD800', '\uDFFF'}) {
      var failure =
          assertThrowsExactly(
              IllegalArgumentException.class,
              () -> WebNonSecretConfig.parse(yaml(String.valueOf(isolated)), ""));
      assertDiagnostic("Web non-secret configuration unavailable", failure);
    }
  }

  private static String yaml(String comment) {
    return MODE + ": DEBUG\n# " + comment + "\n";
  }

  private static void assertDiagnostic(String expected, IllegalArgumentException failure) {
    assertEquals(expected, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
