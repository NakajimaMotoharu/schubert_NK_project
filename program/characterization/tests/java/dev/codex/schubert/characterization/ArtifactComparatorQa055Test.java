package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-CHR-QA055-001: the fixed lock text and Retry-After are separate comparison fields. */
final class ArtifactComparatorQa055Test {
  private static final String DEFINITIONS = "program/characterization/tests/resources/cases";
  private static final String CASE_FILE = "CHR-A02.json";
  private static final String FIXED_MESSAGE =
      "ログイン試行回数が上限に達しました。15分ほど待ってから再度お試しください。";

  @TempDir Path root;

  @Test
  void lockedLoginTextAndRetryAfterRemainSeparateComparisonValues() throws IOException {
    Path cases = Files.createDirectories(root.resolve(DEFINITIONS));
    Path approved = Path.of(System.getProperty("chr.unitProjectRoot")).resolve(DEFINITIONS);
    for (String name : List.of("catalog.json", "dif-allowlist.json")) {
      Files.copy(approved.resolve(name), cases.resolve(name));
    }
    Path current = Files.createDirectory(root.resolve("synthetic-current"));
    Path nk = Files.createDirectory(root.resolve("synthetic-nk"));
    Path observations =
        Files.writeString(root.resolve("observations.json"), "{\"version\":1,\"observations\":[]}");
    Files.writeString(current.resolve(CASE_FILE), artifact(FIXED_MESSAGE, "27"));
    Path nkCase = Files.writeString(nk.resolve(CASE_FILE), artifact(FIXED_MESSAGE, "27"));
    var matching = ArtifactComparator.compare(root, current, nk, observations);
    assertEquals(1, matching.comparedCaseCount());
    assertTrue(matching.unregisteredDifferences().isEmpty());
    assertFalse(matching.passed());

    Files.writeString(nkCase, artifact("27秒待ってください。", "27"));
    var changedMessage = ArtifactComparator.compare(root, current, nk, observations);
    assertEquals(List.of("CHR-A02:/lockedMessage"), changedMessage.unregisteredDifferences());
    assertTrue(changedMessage.failures().contains("UNREGISTERED_DIFF:CHR-A02:/lockedMessage"));

    Files.writeString(nkCase, artifact(FIXED_MESSAGE, "28"));
    var changedHeader = ArtifactComparator.compare(root, current, nk, observations);
    assertEquals(
        List.of("CHR-A02:/lockedHeaders/Retry-After"), changedHeader.unregisteredDifferences());
    assertTrue(
        changedHeader.failures().contains("UNREGISTERED_DIFF:CHR-A02:/lockedHeaders/Retry-After"));
  }

  private static String artifact(String displayText, String retryAfter) {
    return """
        {"caseId":"CHR-A02","status":"PASS","lockedMessage":"%s","lockedHeaders":{"Retry-After":"%s"}}
        """.formatted(displayText, retryAfter);
  }
}
