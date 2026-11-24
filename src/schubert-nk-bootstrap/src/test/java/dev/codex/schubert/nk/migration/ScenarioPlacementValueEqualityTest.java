package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.migration.ScenarioEntryPlacementMap.PlacedEntry;
import dev.codex.schubert.nk.migration.ScenarioEntryPlacementMap.Placement;
import java.util.HashSet;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

final class ScenarioPlacementValueEqualityTest {
  @Test
  @DisplayName("PT-MIG-PLACE013 identical placement values are the same logical output")
  void equivalentPlacementsIdentifyTheSameLogicalOutput() {
    var inputs = new HashSet<Placement>();
    assertTrue(inputs.add(new Placement(1, 101, 201, 3)));
    assertFalse(inputs.add(new Placement(1, 101, 201, 3)));
    assertTrue(inputs.add(new Placement(1, 101, 201, 4)));
    assertEquals(2, inputs.size());

    var outputs = new HashSet<PlacedEntry>();
    assertTrue(outputs.add(new PlacedEntry(201, 301, 1, 1, 401, 3)));
    assertFalse(outputs.add(new PlacedEntry(201, 301, 1, 1, 401, 3)));
    assertTrue(outputs.add(new PlacedEntry(201, 301, 1, 1, 402, 3)));
    assertEquals(2, outputs.size());
  }
}
