package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-IDEM-CANONVALUE007, SSC-458, SS351 §12 and PT-P01810-CATALOG-006/007. */
final class CanonicalValueDiagnosticTest {
  @Test
  void canonicalValue007DifferentLayoutAndFieldMetadataHaveTheSameFixedDiagnostic() {
    var one = new CanonicalField("sampleOne", "V1", new byte[] {1});
    var two = new CanonicalField("sampleTwo", "V2", new byte[] {2});
    try (var first = new CanonicalRequest("synthetic-1", "SYNTEST1", "013", "left", List.of(one));
        var second =
            new CanonicalRequest("synthetic-2", "SYNTEST2", "029", "right", List.of(two))) {
      assertEquals("CanonicalField[<redacted>]", one.toString());
      assertEquals("CanonicalField[<redacted>]", two.toString());
      assertEquals("CanonicalRequest[<redacted>]", first.toString());
      assertEquals("CanonicalRequest[<redacted>]", second.toString());
      assertNotEquals(one.name(), two.name());
      assertNotEquals(one.typeVersion(), two.typeVersion());
      assertNotEquals(first.layoutId(), second.layoutId());
      assertNotEquals(first.layoutVersion(), second.layoutVersion());
    }
  }
}
