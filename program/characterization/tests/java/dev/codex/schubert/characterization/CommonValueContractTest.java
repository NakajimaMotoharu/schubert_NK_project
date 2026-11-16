package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-CHR-VALUE001..005 / SS355 / BUG3146: independent Java value and target contracts. */
final class CommonValueContractTest {
  @Test
  void comparisonResultKeepsValueIdentityAfterCallerListMutation() {
    List<String> original = new ArrayList<>();
    var value =
        new ArtifactComparator.ComparisonResult(
            "PASS", 24, 24, 0, 0, original, List.of(), List.of(), List.of());
    var same =
        new ArtifactComparator.ComparisonResult(
            "PASS", 24, 24, 0, 0, List.of(), List.of(), List.of(), List.of());
    original.add("not-published");
    assertEquals(List.of(), value.usedDifferences());
    assertEquals(same, value);
    assertEquals(value, same);
    assertEquals(value, value);
    assertNotEquals(null, value);
    assertNotEquals("PASS", value);
    assertNotEquals(
        new ArtifactComparator.ComparisonResult(
            "FAIL", 24, 24, 0, 0, List.of(), List.of(), List.of(), List.of()),
        value);
    assertEquals(776402513, value.hashCode());
    assertEquals(
        "ComparisonResult[status=PASS, expectedCaseCount=24, comparedCaseCount=24,"
            + " rawDifferenceCount=0, observationCount=0, usedDifferences=[], unusedDifferences=[],"
            + " unregisteredDifferences=[], failures=[]]",
        value.toString());
  }

  @Test
  void baselineNumbersUseAllThreeTypedComponentsInValueIdentity() {
    var value = new GateCli.BaselineNumbers(2, 3, 4);
    assertEquals(new GateCli.BaselineNumbers(2, 3, 4), value);
    assertEquals(value, value);
    assertNotEquals(null, value);
    assertNotEquals("metadata", value);
    assertNotEquals(new GateCli.BaselineNumbers(3, 3, 4), value);
    assertNotEquals(new GateCli.BaselineNumbers(2, 4, 4), value);
    assertNotEquals(new GateCli.BaselineNumbers(2, 3, 5), value);
    assertEquals(2019, value.hashCode());
    assertEquals(
        "BaselineNumbers[masterFileCount=2, masterBytes=3, browserRevision=4]", value.toString());
  }

  @Test
  void treeStatsPreserveOrderedSymlinkValuesInDiagnosticAndIdentity() {
    var value = new GateCli.TreeStats(2, 3, List.of("link"));
    assertEquals(new GateCli.TreeStats(2, 3, List.of("link")), value);
    assertEquals(value, value);
    assertNotEquals(null, value);
    assertNotEquals("tree", value);
    assertNotEquals(new GateCli.TreeStats(3, 3, List.of("link")), value);
    assertNotEquals(new GateCli.TreeStats(2, 4, List.of("link")), value);
    assertNotEquals(new GateCli.TreeStats(2, 3, List.of("other")), value);
    assertEquals(3323896, value.hashCode());
    assertEquals("TreeStats[fileCount=2, bytes=3, symlinks=[link]]", value.toString());
  }

  @Test
  void validationResultValueIncludesBothFailuresAndMetrics() {
    var value = new GateContractValidator.ValidationResult(List.of("x"), Map.of("count", 2));
    assertEquals(
        new GateContractValidator.ValidationResult(List.of("x"), Map.of("count", 2)), value);
    assertEquals(value, value);
    assertNotEquals(null, value);
    assertNotEquals("validation", value);
    assertNotEquals(
        new GateContractValidator.ValidationResult(List.of("y"), Map.of("count", 2)), value);
    assertNotEquals(
        new GateContractValidator.ValidationResult(List.of("x"), Map.of("count", 3)), value);
    assertFalse(value.passed());
    assertEquals(94856022, value.hashCode());
    assertEquals("ValidationResult[failures=[x], metrics={count=2}]", value.toString());
  }

  @Test
  void targetEnumerationOwnsItsArrayAndHashCollisionIsStillUnknown() {
    var values = TargetAdapter.Target.values();
    assertArrayEquals(
        new TargetAdapter.Target[] {TargetAdapter.Target.CURRENT, TargetAdapter.Target.NK}, values);
    values[0] = TargetAdapter.Target.NK;
    assertEquals(TargetAdapter.Target.CURRENT, TargetAdapter.Target.values()[0]);
    assertEquals(TargetAdapter.Target.CURRENT, TargetAdapter.Target.valueOf("CURRENT"));
    assertEquals(TargetAdapter.Target.NK, TargetAdapter.Target.valueOf("NK"));
    assertThrows(IllegalArgumentException.class, () -> TargetAdapter.Target.valueOf("OTHER"));
    // These literals have the same Java String hash as nk/current, but are different values.
    for (String unknown : List.of("m\u008a", "currem\u0093")) {
      var error =
          assertThrows(IllegalArgumentException.class, () -> TargetAdapter.Target.parse(unknown));
      assertEquals("target must be current or nk", error.getMessage());
    }
    assertTrue(TargetAdapter.Target.parse("CURRENT") == TargetAdapter.Target.CURRENT);
  }
}
