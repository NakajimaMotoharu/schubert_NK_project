package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SS355, PT-CHR-CASEFILE001. */
final class GateCaseIdFilesOnlyTest {
  @TempDir Path artifacts;

  @Test
  void caseIdsListsRegularJsonFilesAndIgnoresMatchingDirectoryNames() throws IOException {
    Files.writeString(artifacts.resolve("CHR-L01.json"), "{}");
    Files.createDirectory(artifacts.resolve("CHR-A04.json"));
    Files.writeString(artifacts.resolve("CHR-A03.json"), "{}");
    Files.writeString(artifacts.resolve("notes.txt"), "synthetic test input");

    assertEquals(List.of("CHR-A03", "CHR-L01"), GateCli.caseIds(artifacts));
  }
}
