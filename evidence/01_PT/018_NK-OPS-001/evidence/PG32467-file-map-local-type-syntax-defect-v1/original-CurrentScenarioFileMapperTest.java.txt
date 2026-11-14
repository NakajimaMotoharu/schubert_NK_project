package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
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

/** PT-MIG-FILEMAP001..024; literal roots, asset claims, target fields and COPY bytes. */
final class CurrentScenarioFileMapperTest {
  private static final String ROOT_ONE = "game1";
  private static final String ROOT_TWO = "game2";
  private static final String RELATIVE = "文章/T/a.txt";
  private static final String FILE_NAME = "a.txt";
  private static final String STORAGE_ONE = "assets/g1/a.txt";
  private static final String STORAGE_TWO = "assets/g2/a.txt";
  private static final String HASH_ONE =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String HASH_EMPTY =
      "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String DIAGNOSTIC = "migration file conversion is invalid";
  private static final String TARGET_TWO = "700";
  private static final String TARGET_ONE = "900";
  private static final String CHAPTER = "Chapter";
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test
  void fileMap001TwoGameRowsBindAllElevenFields() {
    var rows = normal();
    Collections.reverse(rows);
    var actual = mapper().copyRows(rows, at()).rows();
    assertEquals(
        List.of(
            TARGET_ONE,
            "1",
            "1",
            STORAGE_ONE,
            RELATIVE,
            FILE_NAME,
            " A ",
            CHAPTER,
            HASH_ONE,
            "3",
            STAMP),
        actual.get(0));
    assertEquals(
        Arrays.asList(
            TARGET_TWO,
            "2",
            "1",
            STORAGE_TWO,
            RELATIVE,
            FILE_NAME,
            null,
            null,
            HASH_EMPTY,
            "0",
            STAMP),
        actual.get(1));
  }

  @Test
  void fileMap002EmptySnapshotIgnoresNoOtherKindQualification() {
    var assets =
        new AssetMigrationManifest(
            List.of(
                new AssetMigrationManifest.Entry(
                    AssetMigrationManifest.Kind.AUDIO, "other/a", "out/a", 0, HASH_EMPTY)));
    var m =
        new CurrentScenarioFileMapper(
            new ScenarioFileMigrationMap(List.of()), assets, ROOT_ONE, ROOT_TWO);
    assertEquals(List.of(), m.copyRows(List.of(), at()).rows());
    assertEquals(1, assets.entries().size());
  }

  @Test
  void fileMap003AllConstructorNullsAreFixedFailures() {
    assertThrows(
        IllegalArgumentException.class,
        () -> new CurrentScenarioFileMapper(null, assets(), ROOT_ONE, ROOT_TWO));
    assertThrows(
        IllegalArgumentException.class,
        () -> new CurrentScenarioFileMapper(files(), null, ROOT_ONE, ROOT_TWO));
    assertThrows(
        IllegalArgumentException.class,
        () -> new CurrentScenarioFileMapper(files(), assets(), null, ROOT_TWO));
    assertThrows(
        IllegalArgumentException.class,
        () -> new CurrentScenarioFileMapper(files(), assets(), ROOT_ONE, null));
  }

  @Test
  void fileMap004EveryInvalidRootAndEqualRootIsRejected() {
    for (String root :
        List.of(
            "", "/a", "a/", "a\\b", "a//b", ".", "..", "a/./b", "a/../b", "e\u0301", "a\0", "a\t",
            "a\u0080", "a\ud800", "a\udfff")) {
      assertThrows(
          IllegalArgumentException.class,
          () -> new CurrentScenarioFileMapper(files(), assets(), root, ROOT_TWO));
      assertThrows(
          IllegalArgumentException.class,
          () -> new CurrentScenarioFileMapper(files(), assets(), ROOT_ONE, root));
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> new CurrentScenarioFileMapper(files(), assets(), ROOT_ONE, ROOT_ONE));
  }

  @Test
  void fileMap005RowsTimeNullAndTimePrecisionAreRejected() {
    var m = mapper();
    assertThrows(IllegalArgumentException.class, () -> m.copyRows(null, at()));
    assertThrows(IllegalArgumentException.class, () -> m.copyRows(normal(), null));
    for (var instant :
        List.of(Instant.MIN, Instant.MAX, Instant.parse("2026-01-02T03:04:05.000000001Z")))
      assertThrows(IllegalArgumentException.class, () -> m.copyRows(normal(), instant));
  }

  @Test
  void fileMap006MissingExtraNullAndWrongWidthRowsAreRejected() {
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
    shortRow.get(0).remove(7);
    reject(shortRow);
    var longRow = normal();
    longRow.get(0).add("extra");
    reject(longRow);
  }

  @Test
  void fileMap007CurrentIdsMustBeCanonicalSignedKnownValues() {
    for (String id :
        Arrays.asList(
            null, "", "+1", "01", "-0", " 1", "9223372036854775808", "-9223372036854775809", "99"))
      reject(changed(0, id));
  }

  @Test
  void fileMap008GamesMustBeCanonicalAndOwnTheirSourceIds() {
    for (String game : Arrays.asList(null, "", "01", "+1", "3", "-1", " 1", "2"))
      reject(changed(1, game));
  }

  @Test
  void fileMap009GlobalCurrentIdCannotBeDuplicatedAcrossGames() {
    var f =
        new ScenarioFileMigrationMap(
            List.of(
                new ScenarioFileMigrationMap.FilePair(1, -20, 900),
                new ScenarioFileMigrationMap.FilePair(2, -20, 700)));
    var rows = normal();
    rows.get(1).set(0, "-20");
    assertThrows(
        IllegalArgumentException.class,
        () -> new CurrentScenarioFileMapper(f, assets(), ROOT_ONE, ROOT_TWO).copyRows(rows, at()));
  }

  @Test
  void fileMap010UnknownMismatchedOrRepairedPathsAreRejected() {
    for (String path :
        Arrays.asList(
            null,
            "unknown",
            "文章/T/A.txt",
            "文章\\T\\a.txt",
            "../文章/T/a.txt",
            "./文章/T/a.txt",
            "game2/文章/T/a.txt")) reject(changed(2, path));
  }

  @Test
  void fileMap011OptionalSourceHashMustAgreeExactlyWhenPresent() {
    for (String hash : List.of("", HASH_EMPTY, HASH_ONE.toUpperCase(java.util.Locale.ROOT)))
      reject(changed(6, hash));
    assertEquals(HASH_ONE, mapper().copyRows(changed(6, null), at()).rows().get(0).get(8));
    assertEquals(HASH_ONE, mapper().copyRows(normal(), at()).rows().get(0).get(8));
  }

  @Test
  void fileMap012OptionalSizeMustBeCanonicalAndMatchDeclaredClaim() {
    for (String size :
        List.of("", "+3", "03", "-0", "-1", "4", "9223372036854775808", "-9223372036854775809"))
      reject(changed(7, size));
    assertEquals("3", mapper().copyRows(changed(7, null), at()).rows().get(0).get(9));
  }

  @Test
  void fileMap013ScenarioCardinalityAndOtherKindAreSeparate() {
    var empty = new AssetMigrationManifest(List.of());
    assertThrows(
        IllegalArgumentException.class,
        () -> new CurrentScenarioFileMapper(files(), empty, ROOT_ONE, ROOT_TWO));
    var extra = new ArrayList<>(assets().entries());
    extra.add(
        new AssetMigrationManifest.Entry(
            AssetMigrationManifest.Kind.SCENARIO, "other/b", "out/b", 0, HASH_EMPTY));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CurrentScenarioFileMapper(
                files(), new AssetMigrationManifest(extra), ROOT_ONE, ROOT_TWO));
    extra.remove(extra.size() - 1);
    extra.add(
        new AssetMigrationManifest.Entry(
            AssetMigrationManifest.Kind.AUDIO, "other/a", "out/a", 0, HASH_EMPTY));
    assertEquals(
        2,
        new CurrentScenarioFileMapper(
                files(), new AssetMigrationManifest(extra), ROOT_ONE, ROOT_TWO)
            .copyRows(normal(), at())
            .rows()
            .size());
  }

  @Test
  void fileMap014OneAssetCannotBeConsumedByTwoSourceRows() {
    var f =
        new ScenarioFileMigrationMap(
            List.of(
                new ScenarioFileMigrationMap.FilePair(1, -20, 900),
                new ScenarioFileMigrationMap.FilePair(1, 10, 700)));
    var rows = normal();
    rows.set(1, new ArrayList<>(rows.get(0)));
    rows.get(1).set(0, "10");
    assertThrows(
        IllegalArgumentException.class,
        () -> new CurrentScenarioFileMapper(f, assets(), ROOT_ONE, ROOT_TWO).copyRows(rows, at()));
  }

  @Test
  void fileMap015StoredNamesAndNullableTextArePreservedAndTargetValidated() {
    for (int column : List.of(3, 4, 5)) {
      String value = " 日本語 / LABEL ";
      var actual = mapper().copyRows(changed(column, value), at()).rows().get(0);
      assertEquals(value, actual.get(column + 2));
      reject(changed(column, "e\u0301"));
      reject(changed(column, "bad\0text"));
    }
    reject(changed(3, null));
    reject(changed(3, "a".repeat(257)));
    reject(changed(4, "a".repeat(65)));
    reject(changed(5, "a".repeat(257)));
  }

  @Test
  void fileMap016TargetN12SizeCeilingAndEmptyFilesAreEnforced() {
    long max = 999999999999L;
    var a = withSize(max);
    var rows = changed(7, "999999999999");
    assertEquals(
        "999999999999",
        new CurrentScenarioFileMapper(files(), a, ROOT_ONE, ROOT_TWO)
            .copyRows(rows, at())
            .rows()
            .get(0)
            .get(9));
    var above = withSize(1000000000000L);
    var unknown = changed(7, null);
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CurrentScenarioFileMapper(files(), above, ROOT_ONE, ROOT_TWO)
                .copyRows(unknown, at()));
    assertEquals("0", mapper().copyRows(normal(), at()).rows().get(1).get(9));
  }

  @Test
  void fileMap017InputManifestAndOutputAreIndependentImmutableValues() {
    var rows = normal();
    var a = assets();
    var m = new CurrentScenarioFileMapper(files(), a, ROOT_ONE, ROOT_TWO);
    var actual = m.copyRows(rows, at()).rows();
    rows.get(0).set(3, "mutated");
    rows.clear();
    assertEquals(FILE_NAME, actual.get(0).get(5));
    assertEquals(2, a.entries().size());
    assertThrows(UnsupportedOperationException.class, actual::clear);
    assertThrows(UnsupportedOperationException.class, () -> actual.get(0).set(0, "mutated"));
    assertEquals(2, m.copyRows(normal(), at()).rows().size());
  }

  @Test
  void fileMap018IndependentFixedCopyBytesPreserveGameRelativeDisplay() {
    String expected =
        "900\t1\t1\tassets/g1/a.txt\t文章/T/a.txt\ta.txt\t A \tChapter\tba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\t3\t2026-01-02T03:04:05Z\n700\t2\t1\tassets/g2/a.txt\t文章/T/a.txt\ta.txt\t\\N\t\\N\te3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\t0\t2026-01-02T03:04:05Z\n";
    assertEquals(
        expected,
        new String(
            mapper().copyRows(normal(), at()).copyBytes(new PostgresCopyTextEncoder()),
            StandardCharsets.UTF_8));
  }

  @Test
  void fileMap019BothTimestampBoundsAndMicrosHaveOneSharedStamp() {
    for (String stamp :
        List.of(
            "0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z", "2026-01-02T03:04:05.123456Z"))
      for (var row : mapper().copyRows(normal(), Instant.parse(stamp)).rows())
        assertEquals(stamp, row.get(10));
  }

  @Test
  void fileMap020SignedCurrentIdExtremesArePreservedForLookup() {
    var f =
        new ScenarioFileMigrationMap(
            List.of(
                new ScenarioFileMigrationMap.FilePair(1, Long.MIN_VALUE, 900),
                new ScenarioFileMigrationMap.FilePair(2, Long.MAX_VALUE, 700)));
    var rows = normal();
    rows.get(0).set(0, "-9223372036854775808");
    rows.get(1).set(0, "9223372036854775807");
    var actual =
        new CurrentScenarioFileMapper(f, assets(), ROOT_ONE, ROOT_TWO).copyRows(rows, at()).rows();
    assertEquals(TARGET_ONE, actual.get(0).get(0));
    assertEquals(TARGET_TWO, actual.get(1).get(0));
  }

  @Test
  void fileMap021CurrentOrderIsSeparateFromTargetNumericOrder() {
    var rows = normal();
    Collections.reverse(rows);
    var actual = mapper().copyRows(rows, at()).rows();
    assertEquals(List.of(TARGET_ONE, TARGET_TWO), actual.stream().map(x -> x.get(0)).toList());
    assertEquals(List.of("1", "1"), actual.stream().map(x -> x.get(2)).toList());
  }

  @Test
  void fileMap022FailureDoesNotPoisonLaterCallsAndDiagnosticIsFixed() {
    var m = mapper();
    Throwable failure =
        assertThrows(IllegalArgumentException.class, () -> m.copyRows(changed(0, "+1"), at()));
    assertEquals(DIAGNOSTIC, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertEquals("CurrentScenarioFileMapper[REDACTED]", m.toString());
    assertEquals(2, m.copyRows(normal(), at()).rows().size());
  }

  @Test
  void fileMap023UnicodeRootsAndSameRelativeNameStayGameBound() {
    for (String root : List.of("日本語", "x\ud7ff", "x\ue000", "x😀", "a/b")) {
      var entries = new ArrayList<>(assets().entries());
      entries.set(
          0,
          new AssetMigrationManifest.Entry(
              AssetMigrationManifest.Kind.SCENARIO,
              root + "/" + RELATIVE,
              STORAGE_ONE,
              3,
              HASH_ONE));
      var actual =
          new CurrentScenarioFileMapper(
                  files(), new AssetMigrationManifest(entries), root, ROOT_TWO)
              .copyRows(normal(), at())
              .rows();
      assertEquals(STORAGE_ONE, actual.get(0).get(3));
      assertEquals(STORAGE_TWO, actual.get(1).get(3));
    }
  }

  @Test
  void fileMap024FiniteParallelCallsConsumeOnlyPrivateClaimMaps() throws Exception {
    var m = mapper();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<String>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(executor.submit(() -> m.copyRows(normal(), at()).rows().get(0).get(0)));
      for (var future : futures)
        assertEquals(TARGET_ONE, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static CurrentScenarioFileMapper mapper() {
    return new CurrentScenarioFileMapper(files(), assets(), ROOT_ONE, ROOT_TWO);
  }

  private static ScenarioFileMigrationMap files() {
    return new ScenarioFileMigrationMap(
        List.of(
            new ScenarioFileMigrationMap.FilePair(1, -20, 900),
            new ScenarioFileMigrationMap.FilePair(2, 10, 700)));
  }

  private static AssetMigrationManifest assets() {
    return new AssetMigrationManifest(
        List.of(
            new AssetMigrationManifest.Entry(
                AssetMigrationManifest.Kind.SCENARIO,
                ROOT_ONE + "/" + RELATIVE,
                STORAGE_ONE,
                3,
                HASH_ONE),
            new AssetMigrationManifest.Entry(
                AssetMigrationManifest.Kind.SCENARIO,
                ROOT_TWO + "/" + RELATIVE,
                STORAGE_TWO,
                0,
                HASH_EMPTY)));
  }

  private static AssetMigrationManifest withSize(long size) {
    var entries = new ArrayList<>(assets().entries());
    entries.set(
        0,
        new AssetMigrationManifest.Entry(
            AssetMigrationManifest.Kind.SCENARIO,
            ROOT_ONE + "/" + RELATIVE,
            STORAGE_ONE,
            size,
            HASH_ONE));
    return new AssetMigrationManifest(entries);
  }

  private static Instant at() {
    return Instant.parse(STAMP);
  }

  private static List<List<@Nullable String>> normal() {
    var rows = new ArrayList<List<@Nullable String>>();
    rows.add(
        new ArrayList<>(List.of("-20", "1", RELATIVE, FILE_NAME, " A ", CHAPTER, HASH_ONE, "3")));
    rows.add(
        new ArrayList<>(Arrays.asList("10", "2", RELATIVE, FILE_NAME, null, null, null, null)));
    return rows;
  }

  private static List<List<@Nullable String>> changed(int column, @Nullable String value) {
    var rows = normal();
    rows.get(0).set(column, value);
    return rows;
  }

  private static void reject(List<? extends @Nullable List<@Nullable String>> rows) {
    assertThrows(IllegalArgumentException.class, () -> mapper().copyRows(rows, at()));
  }
}
