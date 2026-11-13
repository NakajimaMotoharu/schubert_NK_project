package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.migration.ScenarioFileMigrationMap.FilePair;
import dev.codex.schubert.nk.migration.ScenarioFileMigrationMap.MappedFile;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** SSC344; PT-MIG-FILEORDER001..012; literal oracles in NK-MIG-001 specification 013. */
final class ScenarioFileMigrationMapTest {
  private static final String GOLDEN =
      "NKMIGFILEORDER1\n1\t2\t900\t1\n1\t10\t100\t2\n2\t1\t50\t1\n";

  private static ScenarioFileMigrationMap sample() {
    return new ScenarioFileMigrationMap(
        List.of(new FilePair(2, 1, 50), new FilePair(1, 10, 100), new FilePair(1, 2, 900)));
  }

  private static void tuple(MappedFile actual, int game, long source, long target, long order) {
    assertEquals(game, actual.gameId());
    assertEquals(source, actual.currentFileId());
    assertEquals(target, actual.targetFileId());
    assertEquals(order, actual.displayOrder());
  }

  @Test
  void file001LiteralGoldenIndependentOfRenumbering() {
    var map = sample();
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.US_ASCII), map.canonicalBytes());
    assertEquals(3, map.files().size());
    tuple(map.files().get(0), 1, 2, 900, 1);
    tuple(map.files().get(1), 1, 10, 100, 2);
    tuple(map.files().get(2), 2, 1, 50, 1);
    assertEquals("ScenarioFileMigrationMap[REDACTED]", map.toString());
    assertEquals("ScenarioFilePair[REDACTED]", new FilePair(1, 2, 900).toString());
    assertEquals("ScenarioFileMapping[REDACTED]", map.files().get(0).toString());
  }

  @Test
  void file002SignedSourcesAndMaximumTarget() {
    var map =
        new ScenarioFileMigrationMap(
            List.of(
                new FilePair(1, Long.MAX_VALUE, 999_999_999_999L),
                new FilePair(2, Long.MIN_VALUE, 4),
                new FilePair(1, 0, 2),
                new FilePair(1, Long.MIN_VALUE, 1)));
    assertArrayEquals(
        ("NKMIGFILEORDER1\n1\t-9223372036854775808\t1\t1\n1\t0\t2\t2\n"
                + "1\t9223372036854775807\t999999999999\t3\n2\t-9223372036854775808\t4\t1\n")
            .getBytes(StandardCharsets.US_ASCII),
        map.canonicalBytes());
    tuple(map.lookup(1, Long.MIN_VALUE), 1, Long.MIN_VALUE, 1, 1);
    tuple(map.lookup(2, Long.MIN_VALUE), 2, Long.MIN_VALUE, 4, 1);
  }

  @Test
  void file003DuplicateSourceIsPerGame() {
    var input = new ArrayList<>(List.of(new FilePair(1, 7, 8), new FilePair(1, 7, 9)));
    assertThrows(IllegalArgumentException.class, () -> new ScenarioFileMigrationMap(input));
    assertEquals(2, input.size());
    assertEquals(8, input.get(0).targetFileId());
    var map = new ScenarioFileMigrationMap(List.of(new FilePair(2, 7, 9), new FilePair(1, 7, 8)));
    tuple(map.lookup(1, 7), 1, 7, 8, 1);
    tuple(map.lookup(2, 7), 2, 7, 9, 1);
  }

  @Test
  void file004DuplicateTargetIsGlobal() {
    assertThrows(
        IllegalArgumentException.class,
        () -> new ScenarioFileMigrationMap(List.of(new FilePair(1, 7, 8), new FilePair(2, 7, 8))));
    assertThrows(
        IllegalArgumentException.class,
        () -> new ScenarioFileMigrationMap(List.of(new FilePair(1, 7, 8), new FilePair(1, 9, 8))));
  }

  @Test
  void file005InvalidGameDomainsAtEveryBoundary() {
    var map = sample();
    for (int invalid : new int[] {Integer.MIN_VALUE, -1, 0, 3, Integer.MAX_VALUE}) {
      assertThrows(IllegalArgumentException.class, () -> new FilePair(invalid, 1, 1));
      assertThrows(IllegalArgumentException.class, () -> new MappedFile(invalid, 1, 1, 1));
      assertThrows(IllegalArgumentException.class, () -> map.lookup(invalid, 2));
      assertThrows(IllegalArgumentException.class, () -> map.previous(invalid, 2));
      assertThrows(IllegalArgumentException.class, () -> map.next(invalid, 2));
    }
  }

  @Test
  void file006N12TargetAndOrderBoundaries() {
    for (long invalid : new long[] {Long.MIN_VALUE, -1, 0, 1_000_000_000_000L, Long.MAX_VALUE}) {
      assertThrows(IllegalArgumentException.class, () -> new FilePair(1, 0, invalid));
      assertThrows(IllegalArgumentException.class, () -> new MappedFile(1, 0, invalid, 1));
      assertThrows(IllegalArgumentException.class, () -> new MappedFile(1, 0, 1, invalid));
    }
    tuple(new MappedFile(1, Long.MIN_VALUE, 1, 1), 1, Long.MIN_VALUE, 1, 1);
    tuple(
        new MappedFile(2, Long.MAX_VALUE, 999_999_999_999L, 999_999_999_999L),
        2,
        Long.MAX_VALUE,
        999_999_999_999L,
        999_999_999_999L);
  }

  @Test
  void file007NullContractsEstablishConstructorInvariant() {
    assertThrows(NullPointerException.class, () -> new ScenarioFileMigrationMap(null));
    assertThrows(
        NullPointerException.class,
        () -> new ScenarioFileMigrationMap(Arrays.asList(new FilePair(1, 1, 1), null)));
  }

  @Test
  void file008InputListAndReturnedBytesCannotMutateSnapshot() {
    var input =
        new ArrayList<>(
            List.of(new FilePair(2, 1, 50), new FilePair(1, 10, 100), new FilePair(1, 2, 900)));
    var map = new ScenarioFileMigrationMap(input);
    input.clear();
    assertEquals(3, map.files().size());
    assertThrows(UnsupportedOperationException.class, () -> map.files().clear());
    var bytes = map.canonicalBytes();
    Arrays.fill(bytes, (byte) 0);
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.US_ASCII), map.canonicalBytes());
    tuple(map.lookup(2, 1), 2, 1, 50, 1);
  }

  @Test
  void file009UnknownIsSafeRefusalNotBoundary() {
    var map = sample();
    tuple(map.lookup(1, 2), 1, 2, 900, 1);
    for (int game : new int[] {1, 2}) {
      var failure = assertThrows(IllegalArgumentException.class, () -> map.lookup(game, 777));
      assertEquals("migration file mapping is invalid", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
      assertThrows(IllegalArgumentException.class, () -> map.previous(game, 777));
      assertThrows(IllegalArgumentException.class, () -> map.next(game, 777));
    }
  }

  @Test
  void file010WithinGameAndCrossGameNeighbors() {
    var map = sample();
    assertTrue(map.previous(1, 2).isEmpty());
    tuple(map.next(1, 2).orElseThrow(), 1, 10, 100, 2);
    tuple(map.previous(1, 10).orElseThrow(), 1, 2, 900, 1);
    tuple(map.next(1, 10).orElseThrow(), 2, 1, 50, 1);
    tuple(map.previous(2, 1).orElseThrow(), 1, 10, 100, 2);
    assertTrue(map.next(2, 1).isEmpty());
  }

  @Test
  void file011EmptyAndGapsAreExplicitValues() {
    var empty = new ScenarioFileMigrationMap(List.of());
    assertTrue(empty.files().isEmpty());
    assertArrayEquals(
        "NKMIGFILEORDER1\n".getBytes(StandardCharsets.US_ASCII), empty.canonicalBytes());
    assertThrows(IllegalArgumentException.class, () -> empty.lookup(1, 0));
    assertThrows(IllegalArgumentException.class, () -> empty.previous(1, 0));
    assertThrows(IllegalArgumentException.class, () -> empty.next(1, 0));
    var first =
        new ScenarioFileMigrationMap(List.of(new FilePair(2, 800, 5), new FilePair(2, -900, 9)));
    var second =
        new ScenarioFileMigrationMap(List.of(new FilePair(2, -900, 9), new FilePair(2, 800, 5)));
    byte[] expected =
        "NKMIGFILEORDER1\n2\t-900\t9\t1\n2\t800\t5\t2\n".getBytes(StandardCharsets.US_ASCII);
    assertArrayEquals(expected, first.canonicalBytes());
    assertArrayEquals(expected, second.canonicalBytes());
    assertTrue(first.previous(2, -900).isEmpty());
    assertTrue(first.next(2, 800).isEmpty());
  }

  @Test
  void file012ConcurrentReturnsRemainIndependentlyOwned() throws Exception {
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
                  tuple(map.lookup(1, 2), 1, 2, 900, 1);
                  tuple(map.next(1, 10).orElseThrow(), 2, 1, 50, 1);
                  assertFalse(map.previous(2, 1).isEmpty());
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
