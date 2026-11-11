package dev.codex.schubert.nk.protocol.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.charset.StandardCharsets;
import java.util.List;
import org.junit.jupiter.api.Test;

/** UI232/235, SS322 §4.1 / SS333: independent UTF16 scalars, no actual media or file IO. */
class MediaDescriptorUnicodeBoundaryTest {
  private static final String VIDEO_PATH = "video/a.mp4";
  private static final String FILE_NAME = "a.mp4";
  private static final String SUFFIX = ".mp4";
  private static final String PUBLIC_HASH = "0".repeat(64);

  @Test // PT-PRO-003-U16-001 / BUG2648
  void rejectsMalformedLogicalIdentifierWithoutReplacement() {
    for (String invalid : malformedValues()) {
      assertThrows(
          IllegalArgumentException.class, () -> descriptor(invalid, VIDEO_PATH, FILE_NAME));
    }
  }

  @Test // PT-PRO-003-U16-002 / YKT2328
  void rejectsMalformedStoragePathWithoutReplacement() {
    for (String invalid : malformedValues()) {
      assertThrows(
          IllegalArgumentException.class,
          () -> descriptor("id", "video/" + invalid + SUFFIX, FILE_NAME));
    }
  }

  @Test // PT-PRO-003-U16-003 / YKT2328
  void rejectsMalformedDisplayFileNameWithoutReplacement() {
    for (String invalid : malformedValues()) {
      assertThrows(
          IllegalArgumentException.class, () -> descriptor("id", VIDEO_PATH, invalid + SUFFIX));
    }
  }

  @Test // PT-PRO-003-U16-004
  void supplementaryPairsKeepIndependentExactUtf8ByteBoundaries() {
    String scalar = "\ud83d\ude00";
    String logicalId = scalar.repeat(16);
    String path = "video/" + scalar.repeat(62) + "aa/" + scalar.repeat(62) + "aaa.mp4";
    String name = scalar.repeat(63) + SUFFIX;
    // Independent UTF8: scalar4, ID16*4=64, path6+250+1+255=512, name63*4+4=256.
    assertEquals(64, logicalId.getBytes(StandardCharsets.UTF_8).length);
    assertEquals(512, path.getBytes(StandardCharsets.UTF_8).length);
    assertEquals(256, name.getBytes(StandardCharsets.UTF_8).length);
    var actual = descriptor(logicalId, path, name);
    assertEquals(logicalId, actual.logicalId());
    assertEquals(path, actual.storageRelativePath());
    assertEquals(name, actual.fileName());
    assertThrows(IllegalArgumentException.class, () -> descriptor(logicalId + "a", path, name));
    assertThrows(
        IllegalArgumentException.class,
        () -> descriptor(logicalId, "video/a" + path.substring(6), name));
    assertThrows(IllegalArgumentException.class, () -> descriptor(logicalId, path, "a" + name));
    for (String edgeScalar : List.of("\ud800\udc00", "\udbff\udfff")) {
      assertEquals(edgeScalar, descriptor(edgeScalar, VIDEO_PATH, FILE_NAME).logicalId());
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

  private static MediaDescriptor descriptor(String logicalId, String path, String name) {
    return new MediaDescriptor(
        MediaType.VIDEO,
        logicalId,
        path,
        name,
        1,
        PUBLIC_HASH,
        "video/mp4",
        ContentDisposition.INLINE);
  }
}
