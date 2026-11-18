package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrowsExactly;

import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-OPS-CREDLOC-006; SS343 §6.2 fixed location diagnostic. */
final class ServiceCredentialLocationDiagnosticTest {
  @Test
  void opsCredloc006RejectsUnencodableLocationWithOnlyFixedDiagnostic() {
    var environment = Map.of("CREDENTIALS_DIRECTORY", "/unit/" + Character.MIN_HIGH_SURROGATE);

    var failure =
        assertThrowsExactly(
            IllegalArgumentException.class, () -> ServiceCredentialLocation.read(environment));

    assertEquals("service credential location unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
