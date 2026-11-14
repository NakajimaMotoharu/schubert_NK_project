package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.migration.ScenarioEntryMigrationMap.IdPair;
import dev.codex.schubert.nk.migration.ScenarioEntryMigrationMap.MappedEntry;
import dev.codex.schubert.nk.migration.ScenarioEntryPlacementMap.PlacedEntry;
import dev.codex.schubert.nk.migration.ScenarioEntryPlacementMap.Placement;
import dev.codex.schubert.nk.migration.ScenarioFileMigrationMap.FilePair;
import dev.codex.schubert.nk.migration.ScenarioFileMigrationMap.MappedFile;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-MIG-SCENARIOGEN001..016; BUG2901/SSC363: independent primitive value/key contracts. */
final class ScenarioGeneratedValueTest {
  private static final String DIFFERENT_TYPE = "different-type";
  private static final long N12_MAXIMUM = 999_999_999_999L;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test
  void scenarioGen001IdPairEqualityEveryComponent() {
    var value = new IdPair(1, 2);
    assertTrue(value.equals(value));
    assertEquals(value, new IdPair(1, 2));
    assertFalse(value.equals(null));
    assertFalse(value.equals(DIFFERENT_TYPE));
    assertFalse(value.equals(new IdPair(2, 2)));
    assertFalse(value.equals(new IdPair(1, 3)));
  }

  @Test
  void scenarioGen002IdPairIndependentHashes() {
    assertEquals(33, new IdPair(1, 2).hashCode());
    assertEquals(1420103447, new IdPair(-9223372036854775808L, 999999999999L).hashCode());
  }

  @Test
  void scenarioGen003MappedEntryEqualityEveryComponent() {
    var value = new MappedEntry(1, 2, 3);
    assertTrue(value.equals(value));
    assertEquals(value, new MappedEntry(1, 2, 3));
    assertFalse(value.equals(null));
    assertFalse(value.equals(DIFFERENT_TYPE));
    assertFalse(value.equals(new MappedEntry(2, 2, 3)));
    assertFalse(value.equals(new MappedEntry(1, 3, 3)));
    assertFalse(value.equals(new MappedEntry(1, 2, 4)));
  }

  @Test
  void scenarioGen004MappedEntryIndependentHashes() {
    assertEquals(1026, new MappedEntry(1, 2, 3).hashCode());
    assertEquals(
        346153696, new MappedEntry(-9223372036854775808L, 999999999999L, 999999999999L).hashCode());
  }

  @Test
  void scenarioGen005FilePairEqualityEveryComponent() {
    var value = new FilePair(1, 2, 3);
    assertTrue(value.equals(value));
    assertEquals(value, new FilePair(1, 2, 3));
    assertFalse(value.equals(null));
    assertFalse(value.equals(DIFFERENT_TYPE));
    assertFalse(value.equals(new FilePair(2, 2, 3)));
    assertFalse(value.equals(new FilePair(1, 3, 3)));
    assertFalse(value.equals(new FilePair(1, 2, 4)));
  }

  @Test
  void scenarioGen006FilePairIndependentHashes() {
    assertEquals(1026, new FilePair(1, 2, 3).hashCode());
    assertEquals(1420105369, new FilePair(2, -9223372036854775808L, 999999999999L).hashCode());
  }

  @Test
  void scenarioGen007MappedFileEqualityEveryComponent() {
    var value = new MappedFile(1, 2, 3, 4);
    assertTrue(value.equals(value));
    assertEquals(value, new MappedFile(1, 2, 3, 4));
    assertFalse(value.equals(null));
    assertFalse(value.equals(DIFFERENT_TYPE));
    assertFalse(value.equals(new MappedFile(2, 2, 3, 4)));
    assertFalse(value.equals(new MappedFile(1, 3, 3, 4)));
    assertFalse(value.equals(new MappedFile(1, 2, 4, 4)));
    assertFalse(value.equals(new MappedFile(1, 2, 3, 5)));
  }

  @Test
  void scenarioGen008MappedFileIndependentHashes() {
    assertEquals(31810, new MappedFile(1, 2, 3, 4).hashCode());
    assertEquals(
        346213278,
        new MappedFile(2, -9223372036854775808L, 999999999999L, 999999999999L).hashCode());
  }

  @Test
  void scenarioGen009PlacementEqualityEveryComponent() {
    var value = new Placement(1, 2, 3, 4);
    assertTrue(value.equals(value));
    assertEquals(value, new Placement(1, 2, 3, 4));
    assertFalse(value.equals(null));
    assertFalse(value.equals(DIFFERENT_TYPE));
    assertFalse(value.equals(new Placement(2, 2, 3, 4)));
    assertFalse(value.equals(new Placement(1, 3, 3, 4)));
    assertFalse(value.equals(new Placement(1, 2, 4, 4)));
    assertFalse(value.equals(new Placement(1, 2, 3, 5)));
  }

  @Test
  void scenarioGen010PlacementIndependentHashes() {
    assertEquals(31810, new Placement(1, 2, 3, 4).hashCode());
    assertEquals(
        -2147424067,
        new Placement(2, -9223372036854775808L, 9223372036854775807L, 2147483647).hashCode());
  }

  @Test
  void scenarioGen011PlacedEntryEqualityEveryComponent() {
    var value = new PlacedEntry(1, 2, 3, 1, 4, 5);
    assertTrue(value.equals(value));
    assertEquals(value, new PlacedEntry(1, 2, 3, 1, 4, 5));
    assertFalse(value.equals(null));
    assertFalse(value.equals(DIFFERENT_TYPE));
    assertFalse(value.equals(new PlacedEntry(2, 2, 3, 1, 4, 5)));
    assertFalse(value.equals(new PlacedEntry(1, 3, 3, 1, 4, 5)));
    assertFalse(value.equals(new PlacedEntry(1, 2, 4, 1, 4, 5)));
    assertFalse(value.equals(new PlacedEntry(1, 2, 3, 2, 4, 5)));
    assertFalse(value.equals(new PlacedEntry(1, 2, 3, 1, 5, 5)));
    assertFalse(value.equals(new PlacedEntry(1, 2, 3, 1, 4, 6)));
  }

  @Test
  void scenarioGen012PlacedEntryIndependentHashes() {
    assertEquals(30566656, new PlacedEntry(1, 2, 3, 1, 4, 5).hashCode());
    assertEquals(
        1121815658,
        new PlacedEntry(
                -9223372036854775808L, 999999999999L, 999999999999L, 2, 999999999999L, 2147483647)
            .hashCode());
  }

  @Test
  void scenarioGen013DistinctGameSourcePairHashCollision() {
    var map =
        new ScenarioFileMigrationMap(List.of(new FilePair(2, 1, 102), new FilePair(1, 32, 101)));
    assertEquals(new MappedFile(1, 32, 101, 1), map.lookup(1, 32));
    assertEquals(new MappedFile(2, 1, 102, 1), map.lookup(2, 1));
    assertEquals(map.lookup(1, 32), map.previous(2, 1).orElseThrow());
    assertEquals(map.lookup(2, 1), map.next(1, 32).orElseThrow());
    assertTrue(map.previous(1, 32).isEmpty());
    assertTrue(map.next(2, 1).isEmpty());
  }

  @Test
  void scenarioGen014SignedSourcePairBoundaryAndDuplicate() {
    var map =
        new ScenarioFileMigrationMap(
            List.of(
                new FilePair(1, Long.MIN_VALUE, 1),
                new FilePair(2, Long.MIN_VALUE, 2),
                new FilePair(1, Long.MAX_VALUE, 3)));
    assertEquals(1, map.lookup(1, Long.MIN_VALUE).targetFileId());
    assertEquals(2, map.lookup(2, Long.MIN_VALUE).targetFileId());
    assertEquals(2, map.lookup(1, Long.MAX_VALUE).displayOrder());
    assertThrows(IllegalArgumentException.class, () -> map.lookup(2, Long.MAX_VALUE));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ScenarioFileMigrationMap(
                List.of(new FilePair(1, Long.MIN_VALUE, 1), new FilePair(1, Long.MIN_VALUE, 2))));
    assertEquals(
        "NKMIGFILEORDER1\n1\t-9223372036854775808\t1\t1\n1\t9223372036854775807\t3\t2\n2\t-9223372036854775808\t2\t1\n",
        new String(map.canonicalBytes(), java.nio.charset.StandardCharsets.US_ASCII));
  }

  @Test
  void scenarioGen015FileIndexPairCollisionAndExactDuplicate() {
    var files =
        new ScenarioFileMigrationMap(List.of(new FilePair(1, 10, 1), new FilePair(1, 20, 2)));
    var entries = new ScenarioEntryMigrationMap(List.of(new IdPair(1, 101), new IdPair(2, 102)));
    var map =
        new ScenarioEntryPlacementMap(
            files, entries, List.of(new Placement(1, 10, 1, 31), new Placement(1, 20, 2, 0)));
    assertEquals(List.of(new PlacedEntry(1, 101, 1, 1, 1, 31)), map.entriesForFile(1, 10));
    assertEquals(List.of(new PlacedEntry(2, 102, 2, 1, 2, 0)), map.entriesForFile(1, 20));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ScenarioEntryPlacementMap(
                files, entries, List.of(new Placement(1, 10, 1, 31), new Placement(1, 10, 2, 31))));
  }

  @Test
  void scenarioGen016LargeIndexPairAndFiniteIsolation() throws Exception {
    var files =
        new ScenarioFileMigrationMap(
            List.of(
                new FilePair(1, Long.MIN_VALUE, N12_MAXIMUM), new FilePair(2, Long.MAX_VALUE, 1)));
    var entries = new ScenarioEntryMigrationMap(List.of(new IdPair(1, 101), new IdPair(2, 102)));
    var input =
        List.of(
            new Placement(1, Long.MIN_VALUE, 1, Integer.MAX_VALUE),
            new Placement(2, Long.MAX_VALUE, 2, Integer.MAX_VALUE));
    var expected =
        List.of(
            new PlacedEntry(1, 101, 1, 1, N12_MAXIMUM, Integer.MAX_VALUE),
            new PlacedEntry(2, 102, 2, 2, 1, Integer.MAX_VALUE));
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<List<PlacedEntry>>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(
            executor.submit(() -> new ScenarioEntryPlacementMap(files, entries, input).entries()));
      for (var future : futures) assertEquals(expected, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }
}
