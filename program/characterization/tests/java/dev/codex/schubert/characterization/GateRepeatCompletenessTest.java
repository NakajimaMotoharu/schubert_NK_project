package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Independent SS355 CHR-G03 checks with two synthetic capture trees. */
final class GateRepeatCompletenessTest {
  private static final ObjectMapper JSON = new ObjectMapper();
  private static final String REPEAT_FAILED = "current repeat comparison failed";
  private static final Path FIRST_ARTIFACT = Path.of("artifacts", "case-00.json");

  @TempDir Path temporaryDirectory;

  @Test
  @DisplayName("PT-CHR-G03-REPEAT-001 equal counts cannot conceal different content")
  void fullMatchingCapturePassesAndSameSizeDifferenceFails() throws Exception {
    Path first = capture("first", 26);
    Path second = capture("second", 26);
    Path accepted = temporaryDirectory.resolve("complete-match.json");
    GateCli.compareCurrent(first, second, accepted);
    assertReport(accepted, "PASS", 28, List.of(), List.of(), List.of());

    Files.writeString(second.resolve(FIRST_ARTIFACT), "{\"value\":\"bb\"}");
    Path rejected = temporaryDirectory.resolve("complete-difference.json");
    var failure =
        assertThrows(
            IllegalStateException.class, () -> GateCli.compareCurrent(first, second, rejected));
    assertEquals(REPEAT_FAILED, failure.getMessage());
    assertReport(rejected, "FAIL", 28, List.of(), List.of(), List.of("case-00.json"));
  }

  @Test
  @DisplayName("PT-CHR-G03-REPEAT-002 an identical partial pair fails completeness")
  void equalIncompleteCaptureFailsWithoutInventingDifferences() throws Exception {
    Path first = capture("first", 25);
    Path second = capture("second", 25);
    Path output = temporaryDirectory.resolve("incomplete-match.json");
    var failure =
        assertThrows(
            IllegalStateException.class, () -> GateCli.compareCurrent(first, second, output));
    assertEquals(REPEAT_FAILED, failure.getMessage());
    assertReport(output, "FAIL", 27, List.of(), List.of(), List.of());
  }

  @Test
  @DisplayName("PT-CHR-G03-REPEAT-003 an equal-size rename reports a missing and an extra file")
  void equalCompleteCaptureWithARenameReportsEachSideOfTheDifference() throws Exception {
    Path first = capture("first", 26);
    Path second = capture("second", 26);
    Files.move(second.resolve(FIRST_ARTIFACT), second.resolve("artifacts").resolve("renamed.json"));
    Path output = temporaryDirectory.resolve("complete-rename.json");
    var failure =
        assertThrows(
            IllegalStateException.class, () -> GateCli.compareCurrent(first, second, output));
    assertEquals(REPEAT_FAILED, failure.getMessage());
    assertReport(output, "FAIL", 28, List.of("case-00.json"), List.of("renamed.json"), List.of());
  }

  private Path capture(String name, int artifactCount) throws IOException {
    Path root = temporaryDirectory.resolve(name);
    Path artifacts = Files.createDirectories(root.resolve("artifacts"));
    Path screenshots = Files.createDirectories(root.resolve("screenshots"));
    for (int i = 0; i < artifactCount; i++) {
      Files.writeString(artifacts.resolve("case-%02d.json".formatted(i)), "{\"value\":\"aa\"}");
    }
    Files.write(screenshots.resolve("synthetic.png"), new byte[] {1, 2, 3, 4});
    Files.writeString(root.resolve("inventory.json"), "{}");
    return root;
  }

  private static void assertReport(
      Path file,
      String status,
      int observedCount,
      List<String> missing,
      List<String> extra,
      List<String> changed)
      throws IOException {
    var expected = JSON.createObjectNode();
    expected.put("status", status);
    expected.put("expectedFileCount", 28);
    expected.put("firstFileCount", observedCount);
    expected.put("secondFileCount", observedCount);
    var missingItems = expected.putArray("missing");
    missing.forEach(missingItems::add);
    var extraItems = expected.putArray("extra");
    extra.forEach(extraItems::add);
    var changedItems = expected.putArray("changed");
    changed.forEach(changedItems::add);

    assertEquals(expected, JSON.readTree(file.toFile()));
  }
}
