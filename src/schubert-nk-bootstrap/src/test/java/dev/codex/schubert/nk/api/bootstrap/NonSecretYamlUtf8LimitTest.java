package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrowsExactly;

import dev.codex.schubert.nk.web.bootstrap.WebNonSecretConfig;
import java.nio.charset.StandardCharsets;
import java.security.NoSuchAlgorithmException;
import org.junit.jupiter.api.Test;

/** PT-OPS-APICFG008 and PT-OPS-WEBCFG008 exercise the SS343 shared YAML byte bound. */
final class NonSecretYamlUtf8LimitTest {
  private static final String CONFIG = "nk.monitoring.mode: DEBUG\n";
  private static final String FOUR_BYTE_CHAR = "\uD83D\uDE42";
  private static final int MAX_BYTES = 16_384;

  @Test
  void opsApiCfg008Utf8ByteLimit() throws NoSuchAlgorithmException {
    assertEquals(
        "DEBUG", ApiNonSecretConfig.parse(yaml(MAX_BYTES), "").value("nk.monitoring.mode"));
    var failure =
        assertThrowsExactly(
            IllegalArgumentException.class,
            () -> ApiNonSecretConfig.parse(yaml(MAX_BYTES + 1), ""));
    assertRejection("API non-secret configuration unavailable", failure);
  }

  @Test
  void opsWebCfg008Utf8ByteLimit() throws NoSuchAlgorithmException {
    assertEquals(
        "DEBUG", WebNonSecretConfig.parse(yaml(MAX_BYTES), "").value("nk.monitoring.mode"));
    var failure =
        assertThrowsExactly(
            IllegalArgumentException.class,
            () -> WebNonSecretConfig.parse(yaml(MAX_BYTES + 1), ""));
    assertRejection("Web non-secret configuration unavailable", failure);
  }

  private static String yaml(int bytes) {
    // Each four-byte scalar is in a comment. The rest is a fixed ASCII mapping and LF.
    String input = CONFIG + "# " + FOUR_BYTE_CHAR.repeat(4_000) + "x".repeat(bytes - 16_029) + "\n";
    assertEquals(bytes, input.getBytes(StandardCharsets.UTF_8).length);
    return input;
  }

  private static void assertRejection(String message, IllegalArgumentException failure) {
    assertEquals(message, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
