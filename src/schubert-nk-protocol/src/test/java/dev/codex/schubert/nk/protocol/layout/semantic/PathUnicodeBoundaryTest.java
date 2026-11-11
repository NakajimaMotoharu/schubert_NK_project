package dev.codex.schubert.nk.protocol.layout.semantic;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;
import org.junit.jupiter.api.Test;

/** UI243/SS323333 canonical value invariants, BUG2648/YKT2328; no filesystem resolution. */
class PathUnicodeBoundaryTest {
  private static final String DIRECTORY = "directory/";

  @Test // PT-PRO-PATH-U16-001
  void relativePathRejectsMalformedUtf16ButPreservesValidSupplementaryScalars() {
    for (String invalid : malformedValues()) {
      assertThrows(IllegalArgumentException.class, () -> RelativePath.of(DIRECTORY + invalid));
    }
    for (String scalar : List.of("\ud800\udc00", "\ud83d\ude00", "\udbff\udfff")) {
      assertEquals(DIRECTORY + scalar, RelativePath.of(DIRECTORY + scalar).wireValue());
    }
  }

  @Test // PT-PRO-PATH-U16-002
  void displayPathRejectsMalformedUtf16ButPreservesValidSupplementaryScalars() {
    for (String invalid : malformedValues()) {
      assertThrows(IllegalArgumentException.class, () -> DisplayPath.of(DIRECTORY + invalid));
    }
    for (String scalar : List.of("\ud800\udc00", "\ud83d\ude00", "\udbff\udfff")) {
      assertEquals(DIRECTORY + scalar, DisplayPath.of(DIRECTORY + scalar).wireValue());
    }
  }

  private static List<String> malformedValues() {
    // Deliberately invalid UTF16; integer code units keep the static analyzer's literal model
    // valid.
    String high = String.valueOf((char) 0xd800);
    String low = String.valueOf((char) 0xdfff);
    String paired = new String(new char[] {(char) 0xd83d, (char) 0xde00});
    return List.of(
        high, low, high + "x", "x" + low, high + high, low + low, low + high, paired + high);
  }
}
