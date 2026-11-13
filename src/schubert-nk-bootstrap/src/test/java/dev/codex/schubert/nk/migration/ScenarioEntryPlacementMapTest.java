package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.migration.ScenarioEntryMigrationMap.IdPair;
import dev.codex.schubert.nk.migration.ScenarioEntryPlacementMap.PlacedEntry;
import dev.codex.schubert.nk.migration.ScenarioEntryPlacementMap.Placement;
import dev.codex.schubert.nk.migration.ScenarioFileMigrationMap.FilePair;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** SSC345; PT-MIG-PLACE001..012; independent literal oracles in NK-MIG-001 specification015. */
final class ScenarioEntryPlacementMapTest {
  private static final String GOLDEN =
      "NKMIGENTRYPLACEMENT1\n2\t900\t1\t1\t500\t7\n10\t100\t2\t1\t800\t3\n30\t50\t3\t2\t600\t0\n";

  private static ScenarioFileMigrationMap files() {
    return new ScenarioFileMigrationMap(
        List.of(new FilePair(2, 10, 600), new FilePair(1, 20, 500), new FilePair(1, 10, 800)));
  }

  private static ScenarioEntryMigrationMap entries() {
    return new ScenarioEntryMigrationMap(
        List.of(new IdPair(30, 50), new IdPair(10, 100), new IdPair(2, 900)));
  }

  private static List<Placement> input() {
    return List.of(
        new Placement(2, 10, 30, 0), new Placement(1, 10, 10, 3), new Placement(1, 20, 2, 7));
  }

  private static ScenarioEntryPlacementMap sample() {
    return new ScenarioEntryPlacementMap(files(), entries(), input());
  }

  private static void tuple(
      PlacedEntry actual, long source, long target, long order, int game, long file, int index) {
    assertEquals(source, actual.currentEntryId());
    assertEquals(target, actual.targetEntryId());
    assertEquals(order, actual.displayOrder());
    assertEquals(game, actual.gameId());
    assertEquals(file, actual.targetFileId());
    assertEquals(index, actual.entryIndex());
  }

  @Test
  void place001IndependentGlobalGoldenAndFileReferences() {
    var map = sample();
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.US_ASCII), map.canonicalBytes());
    assertEquals(3, map.entries().size());
    tuple(map.entries().get(0), 2, 900, 1, 1, 500, 7);
    tuple(map.entries().get(1), 10, 100, 2, 1, 800, 3);
    tuple(map.entries().get(2), 30, 50, 3, 2, 600, 0);
    assertEquals("ScenarioEntryPlacementMap[REDACTED]", map.toString());
    assertEquals("ScenarioPlacement[REDACTED]", input().get(0).toString());
    assertEquals("ScenarioPlacedEntry[REDACTED]", map.entries().get(0).toString());
  }

  @Test
  void place002FileIndexOrderIsIndependentOfGlobalOrder() {
    var map =
        new ScenarioEntryPlacementMap(
            files(),
            new ScenarioEntryMigrationMap(List.of(new IdPair(1, 10), new IdPair(2, 20))),
            List.of(new Placement(1, 20, 1, Integer.MAX_VALUE), new Placement(1, 20, 2, 0)));
    assertEquals(2, map.entriesForFile(1, 20).size());
    tuple(map.entriesForFile(1, 20).get(0), 2, 20, 2, 1, 500, 0);
    tuple(map.entriesForFile(1, 20).get(1), 1, 10, 1, 1, 500, Integer.MAX_VALUE);
    tuple(map.entries().get(0), 1, 10, 1, 1, 500, Integer.MAX_VALUE);
  }

  @Test
  void place003UnknownFileAndCrossGameMismatchRefuse() {
    var entryMap = new ScenarioEntryMigrationMap(List.of(new IdPair(2, 900)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ScenarioEntryPlacementMap(files(), entryMap, List.of(new Placement(1, 999, 2, 0))));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ScenarioEntryPlacementMap(files(), entryMap, List.of(new Placement(2, 20, 2, 0))));
    var map = sample();
    tuple(map.entriesForFile(1, 10).get(0), 10, 100, 2, 1, 800, 3);
    tuple(map.entriesForFile(2, 10).get(0), 30, 50, 3, 2, 600, 0);
    assertThrows(IllegalArgumentException.class, () -> map.entriesForFile(2, 20));
  }

  @Test
  void place004UnknownEntryCannotAcquireAPlacement() {
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ScenarioEntryPlacementMap(
                files(),
                new ScenarioEntryMigrationMap(List.of(new IdPair(2, 900))),
                List.of(new Placement(1, 20, 999, 0))));
  }

  @Test
  void place005DuplicateEntryAndFileIndexAreIndependent() {
    var entryMap = new ScenarioEntryMigrationMap(List.of(new IdPair(1, 10), new IdPair(2, 20)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ScenarioEntryPlacementMap(
                files(),
                entryMap,
                List.of(new Placement(1, 20, 1, 0), new Placement(2, 10, 1, 1))));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ScenarioEntryPlacementMap(
                files(),
                entryMap,
                List.of(new Placement(1, 20, 1, 0), new Placement(1, 20, 2, 0))));
    var map =
        new ScenarioEntryPlacementMap(
            files(), entryMap, List.of(new Placement(1, 20, 1, 0), new Placement(2, 10, 2, 0)));
    tuple(map.lookup(1), 1, 10, 1, 1, 500, 0);
    tuple(map.lookup(2), 2, 20, 2, 2, 600, 0);
  }

  @Test
  void place006ExactCardinalityAndKnownEmptyFile() {
    assertThrows(
        IllegalArgumentException.class,
        () -> new ScenarioEntryPlacementMap(files(), entries(), List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ScenarioEntryPlacementMap(
                files(), new ScenarioEntryMigrationMap(List.of()), input()));
    var empty =
        new ScenarioEntryPlacementMap(files(), new ScenarioEntryMigrationMap(List.of()), List.of());
    assertTrue(empty.entries().isEmpty());
    assertTrue(empty.entriesForFile(1, 20).isEmpty());
    assertArrayEquals(
        "NKMIGENTRYPLACEMENT1\n".getBytes(StandardCharsets.US_ASCII), empty.canonicalBytes());
    assertThrows(IllegalArgumentException.class, () -> empty.entriesForFile(1, 999));
    assertThrows(IllegalArgumentException.class, () -> empty.lookup(2));
  }

  @Test
  void place007GameDomainsAtEveryPublicBoundary() {
    var map = sample();
    for (int bad : new int[] {Integer.MIN_VALUE, -1, 0, 3, Integer.MAX_VALUE}) {
      assertThrows(IllegalArgumentException.class, () -> new Placement(bad, 0, 0, 0));
      assertThrows(IllegalArgumentException.class, () -> new PlacedEntry(0, 1, 1, bad, 1, 0));
      assertThrows(IllegalArgumentException.class, () -> map.entriesForFile(bad, 10));
    }
  }

  @Test
  void place008IndexAndIndependentN12Fields() {
    for (int bad : new int[] {Integer.MIN_VALUE, -1}) {
      assertThrows(IllegalArgumentException.class, () -> new Placement(1, 0, 0, bad));
      assertThrows(IllegalArgumentException.class, () -> new PlacedEntry(0, 1, 1, 1, 1, bad));
    }
    for (long bad : new long[] {Long.MIN_VALUE, -1, 0, 1_000_000_000_000L, Long.MAX_VALUE}) {
      assertThrows(IllegalArgumentException.class, () -> new PlacedEntry(0, bad, 1, 1, 1, 0));
      assertThrows(IllegalArgumentException.class, () -> new PlacedEntry(0, 1, bad, 1, 1, 0));
      assertThrows(IllegalArgumentException.class, () -> new PlacedEntry(0, 1, 1, 1, bad, 0));
    }
    tuple(new PlacedEntry(Long.MIN_VALUE, 1, 1, 1, 1, 0), Long.MIN_VALUE, 1, 1, 1, 1, 0);
    tuple(
        new PlacedEntry(
            Long.MAX_VALUE,
            999_999_999_999L,
            999_999_999_999L,
            2,
            999_999_999_999L,
            Integer.MAX_VALUE),
        Long.MAX_VALUE,
        999_999_999_999L,
        999_999_999_999L,
        2,
        999_999_999_999L,
        Integer.MAX_VALUE);
  }

  @Test
  void place009NullUnknownAndFixedDiagnosticContracts() {
    assertThrows(
        NullPointerException.class, () -> new ScenarioEntryPlacementMap(null, entries(), input()));
    assertThrows(
        NullPointerException.class, () -> new ScenarioEntryPlacementMap(files(), null, input()));
    assertThrows(
        NullPointerException.class, () -> new ScenarioEntryPlacementMap(files(), entries(), null));
    assertThrows(
        NullPointerException.class,
        () ->
            new ScenarioEntryPlacementMap(
                files(), entries(), Arrays.asList(input().get(0), null, input().get(2))));
    var failure = assertThrows(IllegalArgumentException.class, () -> sample().lookup(999));
    assertEquals("migration entry placement is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  @Test
  void place010SnapshotAndReturnOwnership() {
    var mutable = new ArrayList<>(input());
    var map = new ScenarioEntryPlacementMap(files(), entries(), mutable);
    mutable.clear();
    assertEquals(3, map.entries().size());
    assertThrows(UnsupportedOperationException.class, () -> map.entries().clear());
    assertThrows(UnsupportedOperationException.class, () -> map.entriesForFile(1, 20).clear());
    var bytes = map.canonicalBytes();
    Arrays.fill(bytes, (byte) 0);
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.US_ASCII), map.canonicalBytes());
    tuple(map.lookup(30), 30, 50, 3, 2, 600, 0);
  }

  @Test
  void place011SignedSourcesAndInputReordering() {
    var fileMap = new ScenarioFileMigrationMap(List.of(new FilePair(2, Long.MIN_VALUE, 1)));
    var entryMap =
        new ScenarioEntryMigrationMap(
            List.of(
                new IdPair(Long.MAX_VALUE, 2), new IdPair(0, 3), new IdPair(Long.MIN_VALUE, 4)));
    var rowA = new Placement(2, Long.MIN_VALUE, Long.MAX_VALUE, 0);
    var rowB = new Placement(2, Long.MIN_VALUE, 0, 4);
    var rowC = new Placement(2, Long.MIN_VALUE, Long.MIN_VALUE, Integer.MAX_VALUE);
    byte[] expected =
        ("NKMIGENTRYPLACEMENT1\n-9223372036854775808\t4\t1\t2\t1\t2147483647\n"
                + "0\t3\t2\t2\t1\t4\n9223372036854775807\t2\t3\t2\t1\t0\n")
            .getBytes(StandardCharsets.US_ASCII);
    assertArrayEquals(
        expected,
        new ScenarioEntryPlacementMap(fileMap, entryMap, List.of(rowA, rowB, rowC))
            .canonicalBytes());
    assertArrayEquals(
        expected,
        new ScenarioEntryPlacementMap(fileMap, entryMap, List.of(rowC, rowA, rowB))
            .canonicalBytes());
  }

  @Test
  void place012ConcurrentOwnershipAndLookup() throws Exception {
    var map = sample();
    var executor = Executors.newFixedThreadPool(8);
    var futures = new ArrayList<Future<?>>();
    try {
      for (int index = 0; index < 64; index++) {
        futures.add(
            executor.submit(
                () -> {
                  byte[] actual = map.canonicalBytes();
                  assertArrayEquals(GOLDEN.getBytes(StandardCharsets.US_ASCII), actual);
                  actual[0] = 0;
                  tuple(map.lookup(2), 2, 900, 1, 1, 500, 7);
                  tuple(map.entriesForFile(2, 10).get(0), 30, 50, 3, 2, 600, 0);
                }));
      }
      for (Future<?> future : futures) future.get(5, TimeUnit.SECONDS);
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS), "owned worker termination");
    }
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.US_ASCII), map.canonicalBytes());
  }
}
