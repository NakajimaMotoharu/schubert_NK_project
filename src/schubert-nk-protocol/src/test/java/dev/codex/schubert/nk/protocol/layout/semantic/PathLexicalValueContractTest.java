package dev.codex.schubert.nk.protocol.layout.semantic;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** UI243/SS323333354/SSC443/451: literal lexical boundaries, no filesystem resolution. */
class PathLexicalValueContractTest {
  private static final String CANONICAL_RELATIVE = "dir/café";
  private static final String DISPLAY_VALUE = "directory/声";

  @Test
  void pathValue001RelativeNormalBoundariesAndTypedHashContract() {
    for (String input :
        List.of("a", "1:x", "a..", "a/..x", "a".repeat(255), "é".repeat(127) + "a")) {
      assertEquals(input, RelativePath.of(input).wireValue(), input);
    }
    String maximum = "a".repeat(255) + "/" + "b".repeat(254) + "/c";
    assertEquals(512, maximum.length());
    assertEquals(maximum, RelativePath.of(maximum).wireValue());
    assertEquals(CANONICAL_RELATIVE, RelativePath.of("dir/cafe\u0301").wireValue());
    RelativePath value = RelativePath.of(CANONICAL_RELATIVE);
    RelativePath equal = RelativePath.of(CANONICAL_RELATIVE);
    assertTrue(value.equals(value));
    assertTrue(value.equals(equal));
    assertFalse(value.equals(RelativePath.of("other")));
    assertFalse(value.equals(null));
    assertFalse(value.equals(CANONICAL_RELATIVE));
    assertEquals(196154979, value.hashCode());
    assertEquals("RelativePath[REDACTED]", value.toString());
    Map<RelativePath, String> stored = new HashMap<>();
    stored.put(value, "retained");
    assertEquals("retained", stored.get(equal));
  }

  @Test
  void pathValue002RelativeRejectsEachRootSegmentAndByteBoundary() {
    for (String input :
        List.of(
            "",
            "/a",
            "\\a",
            "C:/a",
            "z:relative",
            "a\\b",
            "a/",
            "a".repeat(255) + "/" + "b".repeat(255) + "/c",
            "a".repeat(256),
            "a//b",
            ".",
            "..",
            "a/./b",
            "a/../b",
            "a/\u0001",
            "a/\u007f",
            "é".repeat(128))) {
      assertThrows(IllegalArgumentException.class, () -> RelativePath.of(input), input);
    }
    assertThrows(NullPointerException.class, () -> RelativePath.of(null));
  }

  @Test
  void pathValue003DisplayOnlyPathsPreservePermittedTextAndRejectTraversal() {
    for (String input :
        List.of(
            "a",
            ".",
            "a/",
            "a//b",
            "a\\b",
            "1:x",
            "a..",
            "a/..x",
            "x../a",
            "a".repeat(512),
            "é".repeat(256))) {
      assertEquals(input, DisplayPath.of(input).wireValue(), input);
    }
    for (String input :
        List.of(
            "",
            "/a",
            "\\a",
            "C:relative",
            "a".repeat(513),
            "é".repeat(257),
            "a\u0001",
            "a\u007f",
            "..",
            "../a",
            "a/..",
            "a/../b",
            "a\\..\\b")) {
      assertThrows(IllegalArgumentException.class, () -> DisplayPath.of(input), input);
    }
    assertThrows(NullPointerException.class, () -> DisplayPath.of(null));
    assertEquals(CANONICAL_RELATIVE, DisplayPath.of("dir/cafe\u0301").wireValue());
    DisplayPath value = DisplayPath.of(DISPLAY_VALUE);
    DisplayPath equal = DisplayPath.of(DISPLAY_VALUE);
    assertTrue(value.equals(value));
    assertTrue(value.equals(equal));
    assertFalse(value.equals(DisplayPath.of("other")));
    assertFalse(value.equals(null));
    assertFalse(value.equals(DISPLAY_VALUE));
    assertEquals(-1626171954, value.hashCode());
    assertEquals("DisplayPath[REDACTED]", value.toString());
    Map<DisplayPath, String> stored = new HashMap<>();
    stored.put(value, "display");
    assertEquals("display", stored.get(equal));
  }
}
