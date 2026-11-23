package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;
import org.junit.jupiter.api.Test;

/** SS355 §8 and RFC 6901 §3. Pointer grammar only, using no artifact paths or files. */
class ArtifactComparatorPointerTest {
  @Test
  void acceptsCanonicalLiteralAndEscapedTokens() {
    for (String pointer : List.of("/item", "/m~0n", "/a~1b", "/a~0~1b", "/日本語/~01", "/a//b")) {
      assertTrue(ArtifactComparator.validPointer(pointer), pointer);
    }
  }

  @Test
  void rejectsMalformedTildeEscapes() {
    for (String pointer : List.of("/item~", "/item~2", "/item~x", "/item~~0", "/a~/b")) {
      assertFalse(ArtifactComparator.validPointer(pointer), pointer);
    }
  }

  @Test
  void retainsExplicitComparisonScopeRestrictions() {
    assertFalse(ArtifactComparator.validPointer(null));
    for (String pointer : List.of("", "/", "item", "/item/", "/items/*", "/items/../item")) {
      assertFalse(ArtifactComparator.validPointer(pointer), pointer);
    }
  }
}
