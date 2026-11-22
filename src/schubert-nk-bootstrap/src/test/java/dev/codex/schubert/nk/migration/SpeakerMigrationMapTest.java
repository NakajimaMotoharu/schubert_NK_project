package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.migration.SpeakerMigrationMap.SpeakerMapping;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-SPEAKERMAP001..024; independent signed-ID/canonical/COPY/primitive-hash vectors. */
final class SpeakerMigrationMapTest {
  private static final String NORMALIZED_COLLISION = "same";
  private static final long N12_MAX = 999_999_999_999L;
  private static final String STAMP_TEXT = "2026-01-02T03:04:05Z";
  private static final Instant STAMP = Instant.parse(STAMP_TEXT);
  private static final String DIAGNOSTIC = "migration speaker mapping is invalid";
  private static final String ONE = "1";
  private static final String TWO = "2";
  private static final String NAME = "Bob";
  private static final String NORMALIZED = "b o b";
  private static final String BOOLEAN_FALSE = "false";
  private static final String HEADER = "game_id\tcurrent_speaker_id\ttarget_speaker_id\n";
  private static final String CANONICAL = HEADER + "1\t-20\t700\n2\t10\t900\n";
  private static final String COPY =
      "700\t1\t Alice / label \talice\ttrue\t\\N\t"
          + STAMP_TEXT
          + "\n900\t2\tBob\tb o b\tfalse\t\t"
          + STAMP_TEXT
          + "\n";
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test
  void speakerMap001SignedCurrentOrderAndArbitraryTargetOrder() {
    var map = normal();
    assertEquals(
        List.of(-20L, 10L), map.mappings().stream().map(SpeakerMapping::currentSpeakerId).toList());
    assertEquals(
        List.of(700L, 900L), map.mappings().stream().map(SpeakerMapping::targetSpeakerId).toList());
    assertArrayEquals(CANONICAL.getBytes(StandardCharsets.UTF_8), map.canonicalBytes());
  }

  @Test
  void speakerMap002EmptyHeaderAndExplicitValidTime() {
    var map = new SpeakerMigrationMap(List.of());
    assertArrayEquals(HEADER.getBytes(StandardCharsets.UTF_8), map.canonicalBytes());
    assertTrue(map.mappings().isEmpty());
    var copy = map.copyRows(List.of(), STAMP);
    assertTrue(copy.rows().isEmpty());
    assertArrayEquals(new byte[0], copy.copyBytes(new PostgresCopyTextEncoder()));
  }

  @Test
  void speakerMap003NullMappingCollectionFixedFailure() {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> new SpeakerMigrationMap(null))
            .getMessage());
  }

  @Test
  void speakerMap004NullMappingElementRejected() {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> new SpeakerMigrationMap(Arrays.asList((SpeakerMapping) null)))
            .getMessage());
  }

  @Test
  void speakerMap005CurrentPrimaryKeyIsGlobalAcrossGames() {
    var input = List.of(new SpeakerMapping(1, 10, 700), new SpeakerMapping(2, 10, 900));
    assertThrows(IllegalArgumentException.class, () -> new SpeakerMigrationMap(input));
  }

  @Test
  void speakerMap006TargetPrimaryKeyIsGlobalAcrossGames() {
    var input = List.of(new SpeakerMapping(1, -20, 700), new SpeakerMapping(2, 10, 700));
    assertThrows(IllegalArgumentException.class, () -> new SpeakerMigrationMap(input));
  }

  @Test
  void speakerMap007RecordDomainsKeepSignedCurrentAndPositiveN12Target() {
    for (int game : List.of(Integer.MIN_VALUE, 0, 3, Integer.MAX_VALUE))
      assertThrows(IllegalArgumentException.class, () -> new SpeakerMapping(game, 0, 1));
    for (long target : List.of(Long.MIN_VALUE, -1L, 0L, N12_MAX + 1, Long.MAX_VALUE))
      assertThrows(IllegalArgumentException.class, () -> new SpeakerMapping(1, 0, target));
    var min = new SpeakerMapping(1, Long.MIN_VALUE, 1);
    var max = new SpeakerMapping(2, Long.MAX_VALUE, N12_MAX);
    assertEquals(Long.MIN_VALUE, min.currentSpeakerId());
    assertEquals(Long.MAX_VALUE, max.currentSpeakerId());
    assertEquals(1, min.gameId());
    assertEquals(2, max.gameId());
    assertEquals(1L, min.targetSpeakerId());
    assertEquals(N12_MAX, max.targetSpeakerId());
  }

  @Test
  void speakerMap008LookupRequiresKnownGlobalIdAndMatchingGame() {
    var map = normal();
    assertEquals(700L, map.targetSpeakerId(1, -20));
    assertEquals(900L, map.targetSpeakerId(2, 10));
    for (long missing : List.of(Long.MIN_VALUE, 0L, 11L, Long.MAX_VALUE))
      assertThrows(IllegalArgumentException.class, () -> map.targetSpeakerId(1, missing));
    for (int game : List.of(-1, 0, 2, 3))
      assertThrows(IllegalArgumentException.class, () -> map.targetSpeakerId(game, -20));
  }

  @Test
  void speakerMap009ConstructorSnapshotAndReturnedMappingsImmutable() {
    var input =
        new ArrayList<>(List.of(new SpeakerMapping(2, 10, 900), new SpeakerMapping(1, -20, 700)));
    var map = new SpeakerMigrationMap(input);
    input.clear();
    assertArrayEquals(CANONICAL.getBytes(StandardCharsets.UTF_8), map.canonicalBytes());
    assertThrows(UnsupportedOperationException.class, () -> map.mappings().clear());
  }

  @Test
  void speakerMap010UnorderedCurrentColumnsAreCopiedWithoutNameReDerivation() {
    var map = normal();
    var batch = map.copyRows(currentRows(), STAMP);
    assertArrayEquals(
        COPY.getBytes(StandardCharsets.UTF_8), batch.copyBytes(new PostgresCopyTextEncoder()));
    assertEquals(" Alice / label ", batch.rows().getFirst().fields().get(2));
    assertEquals(NORMALIZED, batch.rows().get(1).fields().get(3));
    batch.validateEntries(entries(ONE, Long.toString(map.targetSpeakerId(1, -20)), STAMP_TEXT));
  }

  @Test
  void speakerMap011NullRawCollectionRowAndInstantRejected() {
    var map = normal();
    assertThrows(IllegalArgumentException.class, () -> map.copyRows(null, STAMP));
    assertThrows(IllegalArgumentException.class, () -> map.copyRows(currentRows(), null));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            map.copyRows(
                Arrays.asList((List<@Nullable String>) null, currentRows().getFirst()), STAMP));
  }

  @Test
  void speakerMap012ExactCardinalityAndSixColumnWidth() {
    var map = normal();
    for (var rows :
        List.of(
            List.<List<@Nullable String>>of(),
            List.of(currentRows().getFirst()),
            List.of(currentRows().getFirst(), currentRows().getFirst(), currentRows().getFirst())))
      assertThrows(IllegalArgumentException.class, () -> map.copyRows(rows, STAMP));
    var shortRow = mutableRows();
    shortRow.getFirst().removeLast();
    assertThrows(IllegalArgumentException.class, () -> map.copyRows(shortRow, STAMP));
    var longRow = mutableRows();
    longRow.getFirst().add("extra");
    assertThrows(IllegalArgumentException.class, () -> map.copyRows(longRow, STAMP));
  }

  @Test
  void speakerMap013UnknownAndDuplicateCurrentRowsRejected() {
    var unknown = mutableRows();
    unknown.getFirst().set(0, "11");
    assertThrows(IllegalArgumentException.class, () -> normal().copyRows(unknown, STAMP));
    var duplicate = List.of(currentRows().getFirst(), currentRows().getFirst());
    assertThrows(IllegalArgumentException.class, () -> normal().copyRows(duplicate, STAMP));
  }

  @Test
  void speakerMap014CanonicalSignedIdsAcceptZeroAndExtremesRejectMalformedOverflow() {
    for (@Nullable String value :
        Arrays.<@Nullable String>asList(
            null,
            "",
            "+10",
            "010",
            "-0",
            "-01",
            " 10",
            "10 ",
            "１",
            "9223372036854775808",
            "-9223372036854775809",
            "123456789012345678901")) {
      var rows = mutableRows();
      rows.getFirst().set(0, value);
      assertThrows(IllegalArgumentException.class, () -> normal().copyRows(rows, STAMP));
    }
    var zero = new SpeakerMigrationMap(List.of(new SpeakerMapping(1, 0, 1)));
    assertEquals(1L, zero.targetSpeakerId(1, 0));
    assertEquals(
        "1",
        zero.copyRows(List.of(row("0", ONE, NAME, NORMALIZED, BOOLEAN_FALSE, null)), STAMP)
            .rows()
            .getFirst()
            .fields()
            .getFirst());
    var extremes =
        new SpeakerMigrationMap(
            List.of(
                new SpeakerMapping(2, Long.MAX_VALUE, 2),
                new SpeakerMapping(1, Long.MIN_VALUE, 1)));
    var rows =
        List.of(
            row(Long.toString(Long.MAX_VALUE), TWO, "Max", "max", BOOLEAN_FALSE, null),
            row(Long.toString(Long.MIN_VALUE), ONE, "Min", "min", BOOLEAN_FALSE, null));
    assertEquals(
        List.of("1", "2"),
        extremes.copyRows(rows, STAMP).rows().stream()
            .map(item -> item.fields().getFirst())
            .toList());
  }

  @Test
  void speakerMap015GameMustBePresentCanonicalAndMatchMap() {
    for (@Nullable String game : Arrays.<@Nullable String>asList(null, "", ONE, "3", "02")) {
      var rows = mutableRows();
      rows.getFirst().set(1, game);
      assertThrows(IllegalArgumentException.class, () -> normal().copyRows(rows, STAMP));
    }
  }

  @Test
  void speakerMap016StoredMandatoryValuesKeepRowRejections() {
    for (int field : List.of(2, 3, 4)) {
      var rows = mutableRows();
      rows.getFirst().set(field, null);
      assertThrows(IllegalArgumentException.class, () -> normal().copyRows(rows, STAMP));
    }
    for (String value : List.of("TRUE", "t", "1", "")) {
      var rows = mutableRows();
      rows.getFirst().set(4, value);
      assertThrows(IllegalArgumentException.class, () -> normal().copyRows(rows, STAMP));
    }
    for (String value : List.of("", "x".repeat(129), "e\u0301", "bad\0")) {
      var rows = mutableRows();
      rows.getFirst().set(2, value);
      assertThrows(IllegalArgumentException.class, () -> normal().copyRows(rows, STAMP));
    }
  }

  @Test
  void speakerMap017TransactionTimestampBoundsAndMicrosecondsEvenForEmpty() {
    var map = normal();
    for (Instant invalid :
        List.of(
            Instant.parse("0000-12-31T23:59:59Z"),
            Instant.parse("+10000-01-01T00:00:00Z"),
            Instant.parse("2026-01-02T03:04:05.000000001Z")))
      assertThrows(IllegalArgumentException.class, () -> map.copyRows(currentRows(), invalid));
    for (Instant valid :
        List.of(
            Instant.parse("0001-01-01T00:00:00Z"), Instant.parse("9999-12-31T23:59:59.999999Z")))
      assertEquals(
          valid.toString(),
          map.copyRows(currentRows(), valid).rows().getFirst().fields().getLast());
    var empty = new SpeakerMigrationMap(List.of());
    assertThrows(
        IllegalArgumentException.class,
        () -> empty.copyRows(List.of(), Instant.parse("2026-01-02T03:04:05.000000001Z")));
  }

  @Test
  void speakerMap018NormalizedUkIsExactPerGameAndNeverAutoRepaired() {
    var same =
        new SpeakerMigrationMap(
            List.of(new SpeakerMapping(1, 10, 700), new SpeakerMapping(1, 20, 900)));
    var rows =
        List.of(
            row("10", ONE, "A", NORMALIZED_COLLISION, "true", null),
            row("20", ONE, "B", NORMALIZED_COLLISION, BOOLEAN_FALSE, null));
    assertThrows(IllegalArgumentException.class, () -> same.copyRows(rows, STAMP));
    var cross = mutableRows();
    cross.getFirst().set(3, NORMALIZED_COLLISION);
    cross.get(1).set(3, NORMALIZED_COLLISION);
    assertEquals(2, normal().copyRows(cross, STAMP).rows().size());
  }

  @Test
  void speakerMap019CurrentInputMutationCannotChangeReturnedRows() {
    var rows = mutableRows();
    var copied = normal().copyRows(rows, STAMP);
    rows.getFirst().set(2, "changed");
    rows.clear();
    assertArrayEquals(
        COPY.getBytes(StandardCharsets.UTF_8), copied.copyBytes(new PostgresCopyTextEncoder()));
    assertThrows(UnsupportedOperationException.class, () -> copied.rows().clear());
    assertThrows(
        UnsupportedOperationException.class, () -> copied.rows().getFirst().fields().clear());
  }

  @Test
  void speakerMap020CanonicalByteArrayIsFreshOwnedOutput() {
    var map = normal();
    var bytes = map.canonicalBytes();
    bytes[0] = 'X';
    assertArrayEquals(CANONICAL.getBytes(StandardCharsets.UTF_8), map.canonicalBytes());
  }

  @Test
  void speakerMap021GeneratedRecordEqualityHashAndRedactionIndependentVectors() {
    var first = new SpeakerMapping(1, -20, 700);
    var same = new SpeakerMapping(1, -20, 700);
    assertTrue(first.equals(first));
    assertEquals(first, same);
    assertFalse(first.equals(null));
    assertFalse(first.equals("foreign"));
    assertFalse(first.equals(new SpeakerMapping(2, -20, 700)));
    assertFalse(first.equals(new SpeakerMapping(1, -19, 700)));
    assertFalse(first.equals(new SpeakerMapping(1, -20, 701)));
    assertEquals("SpeakerMapping[REDACTED]", first.toString());
    assertEquals(2250, first.hashCode());
    assertEquals(3132, new SpeakerMapping(2, 10, 900).hashCode());
    assertEquals(1420104408, new SpeakerMapping(1, Long.MIN_VALUE, N12_MAX).hashCode());
    assertEquals(-2147481725, new SpeakerMapping(2, Long.MAX_VALUE, 1).hashCode());
  }

  @Test
  void speakerMap022LongHashCollisionNeverConfusesDistinctPrimaryKeys() {
    var map =
        new SpeakerMigrationMap(
            List.of(new SpeakerMapping(1, 4294967296L, 2), new SpeakerMapping(1, 1, 1)));
    assertEquals(1L, map.targetSpeakerId(1, 1));
    assertEquals(2L, map.targetSpeakerId(1, 4294967296L));
    var rows =
        List.of(
            row("4294967296", ONE, "B", "b", BOOLEAN_FALSE, null),
            row("1", ONE, "A", "a", "true", null));
    assertEquals(
        List.of("1", "2"),
        map.copyRows(rows, STAMP).rows().stream().map(item -> item.fields().getFirst()).toList());
  }

  @Test
  void speakerMap023FixedDiagnosticsAndFreshSuccessAfterRejection() {
    assertEquals("SpeakerMigrationMap[REDACTED]", normal().toString());
    var rows = mutableRows();
    rows.getFirst().set(0, "+10");
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> normal().copyRows(rows, STAMP))
            .getMessage());
    assertArrayEquals(
        COPY.getBytes(StandardCharsets.UTF_8),
        normal().copyRows(currentRows(), STAMP).copyBytes(new PostgresCopyTextEncoder()));
  }

  @Test
  void speakerMap024FiniteSharedMapReadersRetainIndependentRowsAndTerminate()
      throws InterruptedException, ExecutionException, TimeoutException {
    var map = normal();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<byte[]>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(
            executor.submit(
                () -> {
                  assertEquals(700L, map.targetSpeakerId(1, -20));
                  return map.copyRows(currentRows(), STAMP)
                      .copyBytes(new PostgresCopyTextEncoder());
                }));
      for (var future : futures)
        assertArrayEquals(
            COPY.getBytes(StandardCharsets.UTF_8), future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static SpeakerMigrationMap normal() {
    return new SpeakerMigrationMap(
        List.of(new SpeakerMapping(2, 10, 900), new SpeakerMapping(1, -20, 700)));
  }

  private static List<List<@Nullable String>> currentRows() {
    return List.of(
        row("10", TWO, NAME, NORMALIZED, BOOLEAN_FALSE, ""),
        row("-20", ONE, " Alice / label ", "alice", "true", null));
  }

  private static List<@Nullable String> row(
      @Nullable String id,
      @Nullable String game,
      @Nullable String name,
      @Nullable String normalized,
      @Nullable String protagonist,
      @Nullable String notes) {
    return Arrays.<@Nullable String>asList(id, game, name, normalized, protagonist, notes);
  }

  private static ArrayList<List<@Nullable String>> mutableRows() {
    var result = new ArrayList<List<@Nullable String>>();
    for (var row : currentRows()) result.add(new ArrayList<>(row));
    return result;
  }

  private static ScenarioEntryCopyBatch entries(
      String game, @Nullable String speaker, String stamp) {
    int gameId = Integer.parseInt(game);
    var files =
        new ScenarioFileMigrationMap(
            List.of(new ScenarioFileMigrationMap.FilePair(gameId, 10, 100)));
    var mapping =
        new ScenarioEntryMigrationMap(List.of(new ScenarioEntryMigrationMap.IdPair(20, 900)));
    var placement =
        new ScenarioEntryPlacementMap(
            files, mapping, List.of(new ScenarioEntryPlacementMap.Placement(gameId, 10, 20, 0)));
    var row =
        new ScenarioEntryCopyRow(
            Arrays.<@Nullable String>asList(
                "900",
                game,
                "100",
                ONE,
                "0",
                null,
                speaker == null ? "narration" : "dialogue",
                speaker,
                null,
                "hello",
                "raw",
                stamp));
    return new ScenarioEntryCopyBatch(placement, List.of(row));
  }
}
