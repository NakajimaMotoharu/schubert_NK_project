package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/**
 * PT-MIG-AUDIOMAP001..024; literal fields/bytes, independent primitive record hash and exact ms.
 */
final class AudioMigrationMapTest {
  private static final String ROOT_ONE = "game1";
  private static final String ROOT_TWO = "game2";
  private static final String RELATIVE = "音声/a.ogg";
  private static final String FILE_NAME = "saved.ogg";
  private static final String BASENAME = " Kept_Name ";
  private static final String ROLE = "movie_audio";
  private static final String STORAGE_ONE = "assets/g1/a.ogg";
  private static final String STORAGE_TWO = "assets/g2/a.ogg";
  private static final String HASH_ONE =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String HASH_TWO =
      "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String DIAGNOSTIC = "migration audio conversion is invalid";
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test
  void audioMap001TwoGameTenToTwelveValuesAreExplicit() {
    var rows = normal();
    Collections.reverse(rows);
    var actual = mapper().copyRows(rows, at());
    assertEquals(
        List.of(
            "700",
            "1",
            STORAGE_ONE,
            RELATIVE,
            FILE_NAME,
            BASENAME,
            ROLE,
            "OGG",
            "1234",
            "3",
            HASH_ONE,
            STAMP),
        actual.get(0).fields());
    assertEquals(
        Arrays.asList(
            "900",
            "2",
            STORAGE_TWO,
            RELATIVE,
            FILE_NAME,
            "KEEP2",
            "voice",
            null,
            null,
            "5",
            HASH_TWO,
            STAMP),
        actual.get(1).fields());
  }

  @Test
  void audioMap002EmptyMappingHasHeaderAndEmptyOutput() {
    var empty =
        new AudioMigrationMap(List.of(), new AssetMigrationManifest(List.of()), ROOT_ONE, ROOT_TWO);
    assertEquals(List.of(), empty.mappings());
    assertEquals(List.of(), empty.copyRows(List.of(), at()));
    assertEquals(
        "game_id\tcurrent_audio_id\ttarget_audio_id\n",
        new String(empty.canonicalBytes(), StandardCharsets.UTF_8));
  }

  @Test
  void audioMap003ConstructorNullAndElementNullAreFixedFailures() {
    assertThrows(
        IllegalArgumentException.class,
        () -> new AudioMigrationMap(null, assets(), ROOT_ONE, ROOT_TWO));
    assertThrows(
        IllegalArgumentException.class,
        () -> new AudioMigrationMap(pairs(), null, ROOT_ONE, ROOT_TWO));
    assertThrows(
        IllegalArgumentException.class,
        () -> new AudioMigrationMap(pairs(), assets(), null, ROOT_TWO));
    assertThrows(
        IllegalArgumentException.class,
        () -> new AudioMigrationMap(pairs(), assets(), ROOT_ONE, null));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new AudioMigrationMap(
                Arrays.asList(pair(1, 1, 1), null), assets(), ROOT_ONE, ROOT_TWO));
  }

  @Test
  void audioMap004MappingGameAndPositiveN12Boundaries() {
    for (int game : new int[] {Integer.MIN_VALUE, -1, 0, 3, Integer.MAX_VALUE})
      assertThrows(IllegalArgumentException.class, () -> pair(game, 0, 1));
    for (long target : new long[] {Long.MIN_VALUE, -1, 0, 1_000_000_000_000L, Long.MAX_VALUE})
      assertThrows(IllegalArgumentException.class, () -> pair(1, 0, target));
    assertEquals(1L, pair(1, Long.MIN_VALUE, 1).targetAudioId());
    assertEquals(999_999_999_999L, pair(2, Long.MAX_VALUE, 999_999_999_999L).targetAudioId());
  }

  @Test
  void audioMap005GlobalCurrentUniquenessAndStrictTargetOrder() {
    for (var invalid :
        List.of(
            List.of(pair(1, -20, 700), pair(2, -20, 900)),
            List.of(pair(1, -20, 700), pair(2, 4, 700)),
            List.of(pair(1, -20, 900), pair(2, 4, 700)))) {
      assertThrows(
          IllegalArgumentException.class,
          () -> new AudioMigrationMap(invalid, assets(), ROOT_ONE, ROOT_TWO));
    }
  }

  @Test
  void audioMap006SignedOrderSparseTargetAndSnapshot() {
    var input = new ArrayList<AudioMigrationMap.@Nullable AudioMapping>(pairs());
    Collections.reverse(input);
    var map = new AudioMigrationMap(input, assets(), ROOT_ONE, ROOT_TWO);
    input.clear();
    assertEquals(List.of(pair(1, -20, 700), pair(2, 4, 900)), map.mappings());
    assertThrows(UnsupportedOperationException.class, () -> map.mappings().clear());
    assertEquals(700L, map.targetAudioId(1, -20));
    assertEquals(900L, map.targetAudioId(2, 4));
  }

  @Test
  void audioMap007LookupRejectsUnknownAndWrongGame() {
    var map = mapper();
    for (int game : new int[] {Integer.MIN_VALUE, 0, 2, 3})
      assertThrows(IllegalArgumentException.class, () -> map.targetAudioId(game, -20));
    assertThrows(IllegalArgumentException.class, () -> map.targetAudioId(1, 99));
  }

  @Test
  void audioMap008CanonicalHasExactHeaderOrderAndFreshBytes() {
    var map = mapper();
    byte[] expected =
        "game_id\tcurrent_audio_id\ttarget_audio_id\n1\t-20\t700\n2\t4\t900\n"
            .getBytes(StandardCharsets.UTF_8);
    assertArrayEquals(expected, map.canonicalBytes());
    byte[] first = map.canonicalBytes();
    first[0] = 0;
    assertArrayEquals(expected, map.canonicalBytes());
  }

  @Test
  void audioMap009RecordFieldsEqualsHashAndFixedDisplay() {
    var first = pair(1, -20, 700);
    assertEquals(1, first.gameId());
    assertEquals(-20L, first.currentAudioId());
    assertEquals(700L, first.targetAudioId());
    assertEquals(first, pair(1, -20, 700));
    assertEquals(first, first);
    assertNotEquals(first, pair(2, -20, 700));
    assertNotEquals(first, pair(1, -19, 700));
    assertNotEquals(first, pair(1, -20, 701));
    assertFalse(first.equals(null));
    assertFalse(first.equals("other"));
    // int31 combination: ((1*31 + hashLong(-20)=19)*31 + hashLong(700)=700) = 2250.
    assertEquals(2250, first.hashCode());
    assertEquals("AudioMapping[REDACTED]", first.toString());
  }

  @Test
  void audioMap010RootScalarAndSegmentContractsAreShared() {
    for (String bad :
        List.of(
            "", "/a", "a/", "a\\b", "a//b", ".", "..", "a/./b", "a/../b", "e\u0301", "a\0", "a\t",
            "a\u0080", "a\ud800", "a\udfff")) {
      assertThrows(
          IllegalArgumentException.class,
          () -> new AudioMigrationMap(pairs(), assets(), bad, ROOT_TWO));
      assertThrows(
          IllegalArgumentException.class,
          () -> new AudioMigrationMap(pairs(), assets(), ROOT_ONE, bad));
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> new AudioMigrationMap(pairs(), assets(), ROOT_ONE, ROOT_ONE));
  }

  @Test
  void audioMap011RowsNullWidthAndCardinality() {
    var map = mapper();
    assertThrows(IllegalArgumentException.class, () -> map.copyRows(null, at()));
    assertThrows(IllegalArgumentException.class, () -> map.copyRows(normal(), null));
    var few = normal();
    few.remove(1);
    reject(few);
    var extra = normal();
    extra.add(new ArrayList<>(extra.get(0)));
    reject(extra);
    var nul = normal();
    nul.set(0, null);
    reject(nul);
    var shortRow = normal();
    shortRow.get(0).remove(9);
    reject(shortRow);
    var longRow = normal();
    longRow.get(0).add("extra");
    reject(longRow);
  }

  @Test
  void audioMap012IdGameCanonicalUnknownAndDuplicate() {
    for (String value :
        Arrays.asList(
            null, "", "+1", "01", "-0", " 1", "99", "9223372036854775808", "-9223372036854775809"))
      reject(changed(0, value));
    for (String value : Arrays.asList(null, "", "01", "+1", "0", "3", "-1", " 1", "2"))
      reject(changed(1, value));
    var duplicate = normal();
    duplicate.set(1, new ArrayList<>(duplicate.get(0)));
    reject(duplicate);
  }

  @Test
  void audioMap013ExactPathUsesSameRelativeUnderDistinctGameRoots() {
    for (String value :
        Arrays.asList(
            null,
            "unknown",
            "音声/A.ogg",
            "音声\\a.ogg",
            "../音声/a.ogg",
            "./音声/a.ogg",
            "game2/音声/a.ogg")) reject(changed(2, value));
    assertEquals(STORAGE_ONE, mapper().copyRows(normal(), at()).get(0).fields().get(2));
    assertEquals(STORAGE_TWO, mapper().copyRows(normal(), at()).get(1).fields().get(2));
  }

  @Test
  void audioMap014HashSizeOptionalClaimsAreExactWithoutFileProof() {
    for (String value : List.of("", HASH_TWO, HASH_ONE.toUpperCase(java.util.Locale.ROOT)))
      reject(changed(9, value));
    for (String value :
        List.of("", "+3", "03", "-0", "-1", "4", "9223372036854775808", "-9223372036854775809"))
      reject(changed(8, value));
    assertEquals(HASH_ONE, mapper().copyRows(changed(9, null), at()).get(0).fields().get(10));
    assertEquals("3", mapper().copyRows(changed(8, null), at()).get(0).fields().get(9));
  }

  @Test
  void audioMap015StoredNameBasenameRoleAndContainerAreNotRecomputed() {
    var out = mapper().copyRows(normal(), at()).get(0).fields();
    assertEquals(FILE_NAME, out.get(4));
    assertEquals(BASENAME, out.get(5));
    assertEquals(ROLE, out.get(6));
    assertEquals("OGG", out.get(7));
    assertEquals("", mapper().copyRows(changed(6, ""), at()).get(0).fields().get(7));
    assertEquals(
        "😀".repeat(16),
        mapper().copyRows(changed(6, "😀".repeat(16)), at()).get(0).fields().get(7));
    reject(changed(6, "x".repeat(17)));
    reject(changed(5, "x".repeat(12)));
  }

  @Test
  void audioMap016DurationNullZeroExactAndMaximumHaveLiteralMs() {
    String[][] vectors = {
      {"0", "0"},
      {"0.000", "0"},
      {"0.001", "1"},
      {"1", "1000"},
      {"1.234", "1234"},
      {"1.200", "1200"},
      {"999999999.999", "999999999999"},
      {"999999999", "999999999000"}
    };
    for (String[] vector : vectors)
      assertEquals(
          vector[1], mapper().copyRows(changed(7, vector[0]), at()).get(0).fields().get(8));
    assertNull(mapper().copyRows(changed(7, null), at()).get(0).fields().get(8));
  }

  @Test
  void audioMap017InvalidNegativeNoncanonicalAndOverscaleDuration() {
    for (String value :
        List.of(
            "",
            "-1",
            "-0.001",
            "-0",
            "-0.000",
            "+1",
            "01",
            "00.1",
            ".1",
            "1.",
            "1e3",
            "1E+3",
            "NaN",
            " 1",
            "1\n",
            "1.0000",
            "1000000000",
            "999999999.9999",
            "１",
            "1e2147483647")) reject(changed(7, value));
  }

  @Test
  void audioMap018CopyBytesUseHandwrittenTwelveColumnWire() {
    String wire =
        "700\t1\tassets/g1/a.ogg\t音声/a.ogg\tsaved.ogg\t Kept_Name \tmovie_audio\tOGG\t1234\t3\t"
            + HASH_ONE
            + "\t2026-01-02T03:04:05Z\n";
    assertArrayEquals(
        wire.getBytes(StandardCharsets.UTF_8),
        mapper().copyRows(normal(), at()).get(0).copyBytes(new PostgresCopyTextEncoder()));
    String second =
        "900\t2\tassets/g2/a.ogg\t音声/a.ogg\tsaved.ogg\tKEEP2\tvoice\t\\N\t\\N\t5\t"
            + HASH_TWO
            + "\t2026-01-02T03:04:05Z\n";
    assertArrayEquals(
        second.getBytes(StandardCharsets.UTF_8),
        mapper().copyRows(normal(), at()).get(1).copyBytes(new PostgresCopyTextEncoder()));
  }

  @Test
  void audioMap019CommonTimeYearAndMicrosecondBoundaries() {
    for (String stamp :
        List.of(
            "0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z", "2026-01-02T03:04:05.123456Z"))
      for (var row : mapper().copyRows(normal(), Instant.parse(stamp)))
        assertEquals(stamp, row.fields().get(11));
    for (var bad :
        List.of(Instant.MIN, Instant.MAX, Instant.parse("2026-01-02T03:04:05.000000001Z")))
      assertThrows(IllegalArgumentException.class, () -> mapper().copyRows(normal(), bad));
  }

  @Test
  void audioMap020DeepImmutableInputsOutputFailureDoesNotMutate() {
    var map = mapper();
    var rows = normal();
    var out = map.copyRows(rows, at());
    rows.get(0).set(3, "changed");
    rows.clear();
    assertEquals(FILE_NAME, out.get(0).fields().get(4));
    assertThrows(UnsupportedOperationException.class, out::clear);
    assertThrows(UnsupportedOperationException.class, () -> out.get(0).fields().clear());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> map.copyRows(changed(0, null), at()))
            .getMessage());
    assertEquals("AudioMigrationMap[REDACTED]", map.toString());
    assertEquals("AudioFileCopyRow[REDACTED]", out.get(0).toString());
    assertEquals(2, map.copyRows(normal(), at()).size());
  }

  @Test
  void audioMap021SignedLongExtremesAndIndependentHashCollision() {
    var map =
        new AudioMigrationMap(
            List.of(pair(1, Long.MIN_VALUE, 1), pair(2, Long.MAX_VALUE, 999_999_999_999L)),
            assets(),
            ROOT_ONE,
            ROOT_TWO);
    var rows = normal();
    rows.get(0).set(0, Long.toString(Long.MIN_VALUE));
    rows.get(1).set(0, Long.toString(Long.MAX_VALUE));
    assertEquals("1", map.copyRows(rows, at()).get(0).fields().get(0));
    assertEquals("999999999999", map.copyRows(rows, at()).get(1).fields().get(0));
    var min = pair(1, Long.MIN_VALUE, 1);
    var max = pair(1, Long.MAX_VALUE, 1);
    assertNotEquals(min, max);
    // Both signed-long hashes are 0x80000000; primitive31 calculation wraps to -2147482686.
    assertEquals(-2147482686, min.hashCode());
    assertEquals(-2147482686, max.hashCode());
    assertEquals(min, pair(1, Long.MIN_VALUE, 1));
  }

  @Test
  void audioMap022AudioCardinalityOtherKindsAndOneUseAsset() {
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new AudioMigrationMap(
                pairs(), new AssetMigrationManifest(List.of()), ROOT_ONE, ROOT_TWO));
    var entries = new ArrayList<>(assets().entries());
    entries.add(
        new AssetMigrationManifest.Entry(
            AssetMigrationManifest.Kind.AUDIO, "other/x", "out/x", 1, HASH_ONE));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new AudioMigrationMap(
                pairs(), new AssetMigrationManifest(entries), ROOT_ONE, ROOT_TWO));
    entries.remove(entries.size() - 1);
    entries.add(
        new AssetMigrationManifest.Entry(
            AssetMigrationManifest.Kind.SCENARIO, "other/x", "out/x", 1, HASH_ONE));
    var manifest = new AssetMigrationManifest(entries);
    assertEquals(
        2,
        new AudioMigrationMap(pairs(), manifest, ROOT_ONE, ROOT_TWO)
            .copyRows(normal(), at())
            .size());
    assertEquals(3, manifest.entries().size());
    var duplicatePathRows = normal();
    duplicatePathRows.get(1).set(1, "1");
    var oneGame =
        new AudioMigrationMap(
            List.of(pair(1, -20, 700), pair(1, 4, 900)), assets(), ROOT_ONE, ROOT_TWO);
    assertThrows(IllegalArgumentException.class, () -> oneGame.copyRows(duplicatePathRows, at()));
  }

  @Test
  void audioMap023RequiredFieldsAndTargetTextBoundaries() {
    for (int index : new int[] {2, 3, 4, 5}) reject(changed(index, null));
    for (int index : new int[] {3, 4, 5}) {
      reject(changed(index, ""));
      reject(changed(index, "e\u0301"));
      reject(changed(index, "x\0"));
      reject(changed(index, "\ud800"));
    }
    reject(changed(3, "x".repeat(257)));
    reject(changed(4, "x".repeat(256)));
    assertEquals(
        "x".repeat(256),
        mapper().copyRows(changed(3, "x".repeat(256)), at()).get(0).fields().get(4));
    assertEquals(
        "x".repeat(255),
        mapper().copyRows(changed(4, "x".repeat(255)), at()).get(0).fields().get(5));
  }

  @Test
  void audioMap024FiniteConcurrentCallsHaveIndependentOutputs() throws Exception {
    var map = mapper();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<String>>();
      for (int task = 0; task < TASKS; task++)
        futures.add(
            executor.submit(
                () -> {
                  var values = map.copyRows(normal(), at());
                  return values.get(0).fields().get(0)
                      + ":"
                      + values.get(1).fields().get(0)
                      + ":"
                      + map.targetAudioId(1, -20);
                }));
      for (var future : futures)
        assertEquals("700:900:700", future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static AudioMigrationMap.AudioMapping pair(int game, long current, long target) {
    return new AudioMigrationMap.AudioMapping(game, current, target);
  }

  private static List<AudioMigrationMap.@Nullable AudioMapping> pairs() {
    return List.of(pair(2, 4, 900), pair(1, -20, 700));
  }

  private static AssetMigrationManifest assets() {
    return new AssetMigrationManifest(
        List.of(
            new AssetMigrationManifest.Entry(
                AssetMigrationManifest.Kind.AUDIO,
                ROOT_ONE + "/" + RELATIVE,
                STORAGE_ONE,
                3,
                HASH_ONE),
            new AssetMigrationManifest.Entry(
                AssetMigrationManifest.Kind.AUDIO,
                ROOT_TWO + "/" + RELATIVE,
                STORAGE_TWO,
                5,
                HASH_TWO)));
  }

  private static AudioMigrationMap mapper() {
    return new AudioMigrationMap(pairs(), assets(), ROOT_ONE, ROOT_TWO);
  }

  private static Instant at() {
    return Instant.parse(STAMP);
  }

  private static List<List<@Nullable String>> normal() {
    var result = new ArrayList<List<@Nullable String>>();
    result.add(
        new ArrayList<>(
            Arrays.asList(
                "-20", "1", RELATIVE, FILE_NAME, BASENAME, ROLE, "OGG", "1.234", "3", HASH_ONE)));
    result.add(
        new ArrayList<>(
            Arrays.asList(
                "4", "2", RELATIVE, FILE_NAME, "KEEP2", "voice", null, null, "5", HASH_TWO)));
    return result;
  }

  private static List<List<@Nullable String>> changed(int column, @Nullable String value) {
    var result = normal();
    result.get(0).set(column, value);
    return result;
  }

  private static void reject(List<? extends @Nullable List<@Nullable String>> rows) {
    assertThrows(IllegalArgumentException.class, () -> mapper().copyRows(rows, at()));
  }
}
