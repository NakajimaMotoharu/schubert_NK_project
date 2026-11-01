package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** SS343 injected environment gate only; no credential lookup, descriptor adoption or startup. */
final class WebEnvironmentGateContractTest {
  @Test
  void environmentGate001FixedConfigRootAndNamespaceAreCheckedWithoutSourceRead() {
    var reads = new AtomicInteger();
    NonSecretConfigSource source =
        service -> {
          reads.incrementAndGet();
          throw new AssertionError("environment validation must not read a config source");
        };
    var environment = new HashMap<String, String>();
    environment.put("CREDENTIALS_DIRECTORY", "/run/credentials/schubert-nk-web.service");
    environment.put("SCHUBERT_NK_CONFIG_DIR", "/etc/schubert-nk");
    assertDoesNotThrow(new WebStartupInputs(source, environment)::validateEnvironment);
    environment.put("LANG", "C.UTF-8");
    assertDoesNotThrow(new WebStartupInputs(source, environment)::validateEnvironment);
    for (String wrong : new String[] {"", "/other", "/etc/schubert-nk/", "/etc/../etc/schubert-nk"}) {
      environment.put("SCHUBERT_NK_CONFIG_DIR", wrong);
      rejected(new WebStartupInputs(source, environment));
    }
    environment.remove("SCHUBERT_NK_CONFIG_DIR");
    rejected(new WebStartupInputs(source, environment));
    environment.put("SCHUBERT_NK_CONFIG_DIR", null);
    rejected(new WebStartupInputs(source, environment));
    environment.put("SCHUBERT_NK_CONFIG_DIR", "/etc/schubert-nk");
    environment.put("SCHUBERT_NK_UNKNOWN", "PUBLIC_VALUE");
    rejected(new WebStartupInputs(source, environment));
    assertEquals(0, reads.get());
    assertEquals("PUBLIC_VALUE", environment.get("SCHUBERT_NK_UNKNOWN"));
    assertEquals("/etc/schubert-nk", environment.get("SCHUBERT_NK_CONFIG_DIR"));
    assertEquals(4, environment.size());
    assertEquals(
        Map.of(
            "CREDENTIALS_DIRECTORY", "/run/credentials/schubert-nk-web.service",
            "SCHUBERT_NK_CONFIG_DIR", "/etc/schubert-nk",
            "LANG", "C.UTF-8",
            "SCHUBERT_NK_UNKNOWN", "PUBLIC_VALUE"),
        environment);
  }

  private static void rejected(WebStartupInputs input) {
    var failure = assertThrows(IllegalArgumentException.class, input::validateEnvironment);
    assertEquals("Web non-secret environment unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
