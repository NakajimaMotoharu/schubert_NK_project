package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-CHR-CMP001: empty JSON must yield an explicit failed comparison without NPE. */
final class ArtifactComparatorEmptyInputTest {
  private static final String FAILED = "FAIL";
  private static final String ITEM = "fixed-item";
  private static final String CATALOG = "catalog";

  @TempDir Path root;

  @Test
  void emptyJsonInputsFailClosedWithoutNullDereference() throws Exception {
    var positions = List.of(CATALOG, "allowlist", "observations", "current", "nk");
    for (String position : positions) {
      for (int kind = 0; kind < 2; kind++) {
        Path project = Files.createDirectory(root.resolve(position + kind));
        Path cases =
            Files.createDirectories(
                project.resolve("program/characterization/tests/resources/cases"));
        Path catalog =
            Files.writeString(
                cases.resolve("catalog.json"), "{\"cases\":[{\"id\":\"CHR-A01\",\"nk\":\"RUN\"}]}");
        Path allowlist =
            Files.writeString(cases.resolve("dif-allowlist.json"), "{\"differences\":[]}");
        Path observations =
            Files.writeString(
                project.resolve("observations.json"), "{\"version\":1,\"observations\":[]}");
        Path current = Files.createDirectory(project.resolve("synthetic-current"));
        Path nk = Files.createDirectory(project.resolve("synthetic-nk"));
        Path currentFile =
            Files.writeString(
                current.resolve("CHR-A01.json"), "{\"caseId\":\"CHR-A01\",\"status\":\"PASS\"}");
        Path nkFile =
            Files.writeString(
                nk.resolve("CHR-A01.json"), "{\"caseId\":\"CHR-A01\",\"status\":\"PASS\"}");
        Path empty =
            switch (position) {
              case CATALOG -> catalog;
              case "allowlist" -> allowlist;
              case "observations" -> observations;
              case "current" -> currentFile;
              default -> nkFile;
            };
        Files.writeString(empty, kind == 0 ? "" : "  \n");
        var result = ArtifactComparator.compare(project, current, nk, observations);
        assertFalse(result.passed());
        assertEquals(FAILED, result.status());
        String reason =
            switch (position) {
              case CATALOG -> "CATALOG_CASE_COUNT";
              case "allowlist" -> "DIF_RULE_COUNT";
              case "observations" -> "OBSERVATION_VERSION";
              case "current" -> "CURRENT_CASE_ID:CHR-A01";
              default -> "NK_CASE_ID:CHR-A01";
            };
        assertTrue(result.failures().contains(reason), position);
        assertEquals(position.equals(CATALOG) ? 0 : 1, result.comparedCaseCount());
      }
    }
  }

  @Test
  void comparisonResultOwnsImmutableNonNullListSnapshots() {
    List<List<String>> input = new ArrayList<>();
    for (int index = 0; index < 4; index++) {
      input.add(new ArrayList<>(List.of(ITEM)));
    }
    var result =
        new ArtifactComparator.ComparisonResult(
            FAILED, 24, 23, 1, 0, input.get(0), input.get(1), input.get(2), input.get(3));
    input.forEach(List::clear);
    var snapshots =
        List.of(
            result.usedDifferences(),
            result.unusedDifferences(),
            result.unregisteredDifferences(),
            result.failures());
    for (var snapshot : snapshots) {
      assertEquals(List.of(ITEM), snapshot);
      assertThrows(UnsupportedOperationException.class, () -> snapshot.add("other-item"));
    }
    for (int index = 0; index < 4; index++) {
      List<List<String>> fields = new ArrayList<>();
      for (int column = 0; column < 4; column++) {
        fields.add(List.of());
      }
      fields.set(index, null);
      assertThrows(
          NullPointerException.class,
          () ->
              new ArtifactComparator.ComparisonResult(
                  FAILED,
                  24,
                  23,
                  1,
                  0,
                  fields.get(0),
                  fields.get(1),
                  fields.get(2),
                  fields.get(3)));
      fields.set(index, Arrays.asList(ITEM, null));
      assertThrows(
          NullPointerException.class,
          () ->
              new ArtifactComparator.ComparisonResult(
                  FAILED,
                  24,
                  23,
                  1,
                  0,
                  fields.get(0),
                  fields.get(1),
                  fields.get(2),
                  fields.get(3)));
    }
  }
}
