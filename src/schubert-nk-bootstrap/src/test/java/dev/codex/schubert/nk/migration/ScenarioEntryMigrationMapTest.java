package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.migration.ScenarioEntryMigrationMap.IdPair;
import dev.codex.schubert.nk.migration.ScenarioEntryMigrationMap.MappedEntry;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-MIG-ORDER001..012: independent literal tuples/bytes, no real DB or Current data. */
final class ScenarioEntryMigrationMapTest {
  private static final long N12 = 999_999_999_999L;
  private static final String GOLDEN = "NKMIGSCENARIOORDER1\n2\t900\t1\n10\t100\t2\n";

  private static ScenarioEntryMigrationMap map() {
    return new ScenarioEntryMigrationMap(List.of(new IdPair(10, 100), new IdPair(2, 900)));
  }

  private static byte[] bytes(String value) {
    return value.getBytes(StandardCharsets.US_ASCII);
  }

  private static void tuple(MappedEntry actual, long current, long target, long order) {
    assertEquals(current, actual.currentId());
    assertEquals(target, actual.targetId());
    assertEquals(order, actual.displayOrder());
  }

  private static void invalid(org.junit.jupiter.api.function.Executable action) {
    var failure = assertThrows(IllegalArgumentException.class, action);
    assertEquals("migration entry mapping is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  @Test
  void order001LiteralRenumberedGolden() {
    var value = map();
    assertArrayEquals(bytes(GOLDEN), value.canonicalBytes());
    assertEquals(2, value.mappings().size());
    tuple(value.mappings().get(0), 2, 900, 1);
    tuple(value.mappings().get(1), 10, 100, 2);
    assertEquals("ScenarioEntryMigrationMap[REDACTED]", value.toString());
  }

  @Test
  void order002SignedSourcesAndN12TargetBoundaries() {
    var pair = new IdPair(Long.MIN_VALUE, N12);
    assertEquals(Long.MIN_VALUE, pair.currentId());
    assertEquals(N12, pair.targetId());
    assertEquals("ScenarioIdPair[REDACTED]", pair.toString());
    var value =
        new ScenarioEntryMigrationMap(
            List.of(new IdPair(Long.MAX_VALUE, 1), new IdPair(0, 3), pair, new IdPair(-1, 4)));
    tuple(value.mappings().get(0), Long.MIN_VALUE, N12, 1);
    tuple(value.mappings().get(1), -1, 4, 2);
    tuple(value.mappings().get(2), 0, 3, 3);
    tuple(value.mappings().get(3), Long.MAX_VALUE, 1, 4);
    assertArrayEquals(
        bytes(
            "NKMIGSCENARIOORDER1\n-9223372036854775808\t999999999999\t1\n-1\t4\t2\n0\t3\t3\n9223372036854775807\t1\t4\n"),
        value.canonicalBytes());
  }

  @Test
  void order003DuplicateSourceRejectedWithoutInputChange() {
    var original = new ArrayList<>(List.of(new IdPair(2, 10), new IdPair(2, 11)));
    invalid(() -> new ScenarioEntryMigrationMap(original));
    assertEquals(2, original.size());
    assertEquals(10, original.get(0).targetId());
    assertEquals(11, original.get(1).targetId());
  }

  @Test
  void order004DuplicateTargetRejectedIndependently() {
    invalid(() -> new ScenarioEntryMigrationMap(List.of(new IdPair(2, 10), new IdPair(3, 10))));
  }

  @Test
  void order005InvalidTargetDomains() {
    for (long target : new long[] {Long.MIN_VALUE, -1, 0, 1_000_000_000_000L, Long.MAX_VALUE}) {
      invalid(() -> new IdPair(0, target));
      invalid(() -> new MappedEntry(0, target, 1));
    }
  }

  @Test
  void order006MappedEntryOrderDomains() {
    tuple(new MappedEntry(-1, 1, 1), -1, 1, 1);
    var maximum = new MappedEntry(0, N12, N12);
    tuple(maximum, 0, N12, N12);
    assertEquals("ScenarioEntryMapping[REDACTED]", maximum.toString());
    for (long order : new long[] {Long.MIN_VALUE, -1, 0, 1_000_000_000_000L, Long.MAX_VALUE})
      invalid(() -> new MappedEntry(0, 1, order));
  }

  @Test
  void order007NullBoundaryContracts() {
    assertThrows(NullPointerException.class, () -> new ScenarioEntryMigrationMap(null));
    assertThrows(
        NullPointerException.class,
        () -> new ScenarioEntryMigrationMap(Arrays.asList(new IdPair(1, 2), null)));
  }

  @Test
  void order008ImmutableInputListAndReturnedBytes() {
    var input = new ArrayList<>(List.of(new IdPair(10, 100), new IdPair(2, 900)));
    var value = new ScenarioEntryMigrationMap(input);
    input.clear();
    assertEquals(2, value.mappings().size());
    assertThrows(UnsupportedOperationException.class, () -> value.mappings().clear());
    byte[] first = value.canonicalBytes();
    Arrays.fill(first, (byte) 0);
    assertArrayEquals(bytes(GOLDEN), value.canonicalBytes());
    tuple(value.lookup(2), 2, 900, 1);
  }

  @Test
  void order009ExactLookupAndUnknownRefusal() {
    var value = map();
    tuple(value.lookup(2), 2, 900, 1);
    tuple(value.lookup(10), 10, 100, 2);
    for (long unknown : new long[] {Long.MIN_VALUE, -1, 0, 1, 3, 900, Long.MAX_VALUE})
      invalid(() -> value.lookup(unknown));
  }

  @Test
  void order010EmptyIsAValueNotMigrationCompletion() {
    var value = new ScenarioEntryMigrationMap(List.of());
    assertEquals(0, value.mappings().size());
    assertArrayEquals(bytes("NKMIGSCENARIOORDER1\n"), value.canonicalBytes());
    invalid(() -> value.lookup(0));
  }

  @Test
  void order011DenseRanksIgnoreSourceGapsAndInputOrder() {
    var first =
        new ScenarioEntryMigrationMap(
            List.of(new IdPair(1000, 1), new IdPair(5, 30), new IdPair(99, 20)));
    var reordered =
        new ScenarioEntryMigrationMap(
            List.of(new IdPair(99, 20), new IdPair(1000, 1), new IdPair(5, 30)));
    String expected = "NKMIGSCENARIOORDER1\n5\t30\t1\n99\t20\t2\n1000\t1\t3\n";
    assertArrayEquals(bytes(expected), first.canonicalBytes());
    assertArrayEquals(bytes(expected), reordered.canonicalBytes());
    tuple(first.lookup(5), 5, 30, 1);
    tuple(first.lookup(99), 99, 20, 2);
    tuple(first.lookup(1000), 1000, 1, 3);
  }

  @Test
  void order012ConcurrentIndependentReturnOwnership() throws Exception {
    var value = map();
    var workers = Executors.newFixedThreadPool(8);
    try {
      var tasks = new ArrayList<Future<Void>>();
      for (int index = 0; index < 64; index++) {
        tasks.add(
            workers.submit(
                () -> {
                  tuple(value.lookup(2), 2, 900, 1);
                  byte[] output = value.canonicalBytes();
                  assertArrayEquals(bytes(GOLDEN), output);
                  Arrays.fill(output, (byte) 0);
                  assertArrayEquals(bytes(GOLDEN), value.canonicalBytes());
                  return null;
                }));
      }
      for (var task : tasks) task.get(5, TimeUnit.SECONDS);
    } finally {
      workers.shutdownNow();
      if (!workers.awaitTermination(10, TimeUnit.SECONDS))
        throw new AssertionError("scenario migration workers did not terminate");
    }
  }
}
