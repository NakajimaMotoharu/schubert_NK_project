package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-CHR-CMP001: implemented JSON boundary must reject empty input explicitly, never NPE. */
final class ArtifactComparatorEmptyInputTest {
  @TempDir Path root;

  @Test
  void emptyCatalogFailsWithDeclaredInputErrorRatherThanNullDereference() throws Exception {
    Path cases = Files.createDirectories(root.resolve("program/characterization/tests/resources/cases"));
    Files.writeString(cases.resolve("catalog.json"), "");
    Files.writeString(cases.resolve("dif-allowlist.json"), "{\"differences\":[]}");
    Path observations = root.resolve("observations.json");
    Files.writeString(observations, "{}");
    Path current = Files.createDirectory(root.resolve("synthetic-current"));
    Path nk = Files.createDirectory(root.resolve("synthetic-nk"));
    assertThrows(IOException.class, () -> ArtifactComparator.compare(root, current, nk, observations));
  }
}
