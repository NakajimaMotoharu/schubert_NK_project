package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-FCOPY001..014; independent DDL/literal expectations, no DB or actual assets. */
final class ScenarioFileCopyBatchTest {
  private static final String ORACLE_MAXIMUM_N12 = "999999999999";
  private static final String SHA =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String DIAGNOSTIC = "migration file COPY batch is invalid";
  private static final String FIRST_STORAGE_PATH = "first.ks";
  private static final String MUTATED_VALUE = "changed";
  private static final String GOLDEN =
      "900\t1\t1\tfirst.ks\t表示/一\tfirst.ks\t\\N\t第一章\t"
          + SHA
          + "\t3\t"
          + STAMP
          + "\n"
          + "100\t1\t2\tsecond.ks\t表示/二\tsecond.ks\t\t\\N\t"
          + SHA
          + "\t0\t"
          + STAMP
          + "\n"
          + "50\t2\t1\tfirst.ks\t別/一\tfirst.ks\ts\t章\t"
          + SHA
          + "\t999999999999\t"
          + STAMP
          + "\n";

  @Test
  void independentThreeRowGoldenUsesMappingOrderAndExplicitElevenColumns() {
    var input = fixture();
    Collections.reverse(input);
    var batch = new ScenarioFileCopyBatch(mapping(), input);
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), batch.copyBytes(encoder()));
    assertEquals(
        List.of(
            "id",
            "game_id",
            "display_order",
            "storage_relative_path",
            "display_path",
            "file_name",
            "section_code",
            "chapter_title",
            "sha256",
            "byte_size",
            "created_at"),
        batch.columnNames());
    assertThrows(UnsupportedOperationException.class, () -> batch.columnNames().add("invalid"));
  }

  @Test
  void emptyAndCountAndFieldShapeBoundariesAreExplicit() {
    var empty = new ScenarioFileCopyBatch(new ScenarioFileMigrationMap(List.of()), List.of());
    assertEquals(List.of(), empty.rows());
    assertArrayEquals(new byte[0], empty.copyBytes(encoder()));
    var missing = fixture();
    missing.remove(0);
    reject(missing);
    var extra = fixture();
    extra.add(new ArrayList<>(extra.get(0)));
    reject(extra);
    var shortRow = fixture();
    shortRow.get(0).remove(10);
    reject(shortRow);
    var longRow = fixture();
    longRow.get(0).add(null);
    reject(longRow);
  }

  @Test
  void duplicateTargetIsRejectedEvenWhenOtherFieldsDiffer() {
    var input = fixture();
    input.get(1).set(0, "900");
    reject(input);
  }

  @Test
  void unknownTargetAndEachDeclaredMappingColumnMustMatchExactly() {
    var unknown = fixture();
    unknown.get(0).set(0, "901");
    reject(unknown);
    var game = fixture();
    game.get(0).set(1, "2");
    game.get(0).set(3, "unique.ks");
    reject(game);
    var order = fixture();
    order.get(0).set(2, "2");
    reject(order);
    var badGame = fixture();
    badGame.get(0).set(1, "3");
    reject(badGame);
    for (int column : List.of(0, 2)) {
      for (String invalid : List.of("0", "00", "01", "-1", "1000000000000")) {
        var input = fixture();
        input.get(0).set(column, invalid);
        reject(input);
      }
    }
    var maximum = new ArrayList<@Nullable String>(fixture().get(0));
    maximum.set(0, ORACLE_MAXIMUM_N12);
    var maximumMap =
        new ScenarioFileMigrationMap(
            List.of(new ScenarioFileMigrationMap.FilePair(1, 0, 999999999999L)));
    assertEquals(
        ORACLE_MAXIMUM_N12,
        new ScenarioFileCopyBatch(maximumMap, List.of(maximum)).rows().get(0).get(0));
  }

  @Test
  void storageUniquenessIsPerGameAndNeverChangesDeclaredNames() {
    // Same first.ks is independently legal in the two distinct games in GOLDEN.
    assertArrayEquals(
        GOLDEN.getBytes(StandardCharsets.UTF_8),
        new ScenarioFileCopyBatch(mapping(), fixture()).copyBytes(encoder()));
    var duplicate = fixture();
    duplicate.get(1).set(3, FIRST_STORAGE_PATH);
    reject(duplicate);
    var spaces = fixture();
    spaces.get(0).set(3, " preserved .ks");
    assertEquals(
        " preserved .ks", new ScenarioFileCopyBatch(mapping(), spaces).rows().get(0).get(3));
  }

  @Test
  void storageRejectsAbsoluteBackslashEmptyAndDotSegments() {
    for (String invalid : List.of("", "/a", "a\\b", "a//b", "a/", ".", "..", "a/./b", "a/../b")) {
      var input = fixture();
      input.get(0).set(3, invalid);
      reject(input);
    }
  }

  @Test
  void everyTextColumnRejectsNonNfcMalformedSurrogateAndControl() {
    for (int column : List.of(3, 4, 5, 6, 7)) {
      for (String invalid :
          List.of("e\u0301", "\ud800", "\udc00", "a\u0000b", "a\tb", "a\nb", "a\rb", "a\u007fb")) {
        var input = fixture();
        input.get(0).set(column, invalid);
        reject(input);
      }
    }
  }

  @Test
  void byteCeilingsAndSectionUnicodeCodepointsUseDdlUnits() {
    int[] columns = {3, 4, 5, 7};
    int[] limits = {512, 512, 256, 256};
    for (int index = 0; index < columns.length; index++) {
      var exact = fixture();
      String value = "é".repeat(limits[index] / 2);
      exact.get(0).set(columns[index], value);
      assertEquals(
          value, new ScenarioFileCopyBatch(mapping(), exact).rows().get(0).get(columns[index]));
      var overflow = fixture();
      overflow.get(0).set(columns[index], value + "x");
      reject(overflow);
    }
    for (int column : List.of(4, 5)) {
      var empty = fixture();
      empty.get(0).set(column, "");
      reject(empty);
    }
    for (String value : List.of("", "😀".repeat(64))) {
      var input = fixture();
      input.get(0).set(6, value);
      input.get(0).set(7, "");
      assertEquals(value, new ScenarioFileCopyBatch(mapping(), input).rows().get(0).get(6));
    }
    var tooMany = fixture();
    tooMany.get(0).set(6, "a".repeat(65));
    reject(tooMany);
  }

  @Test
  void shaRequiresExactlyLowercaseSixtyFourHexCharacters() {
    for (String invalid :
        List.of(
            "",
            SHA.toUpperCase(java.util.Locale.ROOT),
            "g".repeat(64),
            "0".repeat(63),
            "0".repeat(65))) {
      var input = fixture();
      input.get(0).set(8, invalid);
      reject(input);
    }
  }

  @Test
  void byteSizeRejectsSignsLeadingZeroAndOverflowWhileZeroAndMaximumRemainExact() {
    for (String invalid :
        List.of("-1", "+1", "00", "01", "1.0", " 1", "1000000000000", "9223372036854775808")) {
      var input = fixture();
      input.get(0).set(9, invalid);
      reject(input);
    }
    var batch = new ScenarioFileCopyBatch(mapping(), fixture());
    assertEquals("0", batch.rows().get(1).get(9));
    assertEquals(ORACLE_MAXIMUM_N12, batch.rows().get(2).get(9));
  }

  @Test
  void timestampRequiresSharedCanonicalUtcMicrosecondsWithinDeclaredYears() {
    for (String stamp :
        List.of(
            "0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z", "2026-01-02T03:04:05.000001Z")) {
      var input = fixture();
      for (var row : input) row.set(10, stamp);
      assertEquals(stamp, new ScenarioFileCopyBatch(mapping(), input).rows().get(0).get(10));
    }
    for (String invalid :
        List.of(
            "not-a-date",
            "0000-01-01T00:00:00Z",
            "+10000-01-01T00:00:00Z",
            "2026-01-02T03:04:05.000000001Z",
            "2026-01-02T03:04:05+00:00")) {
      var input = fixture();
      input.get(0).set(10, invalid);
      reject(input);
    }
    var mixed = fixture();
    mixed.get(0).set(10, "2026-01-02T03:04:06Z");
    reject(mixed);
  }

  @Test
  void nullBoundariesAndRedactionUseOneFixedNonSecretDiagnostic() {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> new ScenarioFileCopyBatch(null, fixture()))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> new ScenarioFileCopyBatch(mapping(), null))
            .getMessage());
    var nullRow = fixture();
    nullRow.set(0, null);
    reject(nullRow);
    for (int column : List.of(0, 1, 2, 3, 4, 5, 8, 9, 10)) {
      var input = fixture();
      input.get(0).set(column, null);
      reject(input);
    }
    var batch = new ScenarioFileCopyBatch(mapping(), fixture());
    assertEquals("ScenarioFileCopyBatch[REDACTED]", batch.toString());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> batch.copyBytes(null)).getMessage());
  }

  @Test
  void snapshotsAreDeepAndReturnedRowsColumnsAndBytesCannotMutateState() {
    var input = fixture();
    var alias = input.get(0);
    var batch = new ScenarioFileCopyBatch(mapping(), input);
    alias.set(4, MUTATED_VALUE);
    input.clear();
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), batch.copyBytes(encoder()));
    assertThrows(UnsupportedOperationException.class, () -> batch.rows().clear());
    assertThrows(
        UnsupportedOperationException.class, () -> batch.rows().get(0).set(4, MUTATED_VALUE));
    byte[] bytes = batch.copyBytes(encoder());
    Arrays.fill(bytes, (byte) 0);
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), batch.copyBytes(encoder()));
  }

  @Test
  void ownedFiniteConcurrentCopiesAllMatchIndependentGolden() throws Exception {
    var batch = new ScenarioFileCopyBatch(mapping(), fixture());
    var pool = Executors.newFixedThreadPool(8);
    try {
      var futures = new ArrayList<Future<byte[]>>();
      for (int index = 0; index < 64; index++)
        futures.add(pool.submit(() -> batch.copyBytes(encoder())));
      for (var future : futures)
        assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), future.get(5, TimeUnit.SECONDS));
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  private static void reject(List<List<@Nullable String>> input) {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> new ScenarioFileCopyBatch(mapping(), input))
            .getMessage());
  }

  private static ScenarioFileMigrationMap mapping() {
    return new ScenarioFileMigrationMap(
        List.of(
            new ScenarioFileMigrationMap.FilePair(2, -3, 50),
            new ScenarioFileMigrationMap.FilePair(1, 10, 100),
            new ScenarioFileMigrationMap.FilePair(1, 2, 900)));
  }

  private static List<List<@Nullable String>> fixture() {
    var rows = new ArrayList<List<@Nullable String>>();
    rows.add(
        new ArrayList<>(
            Arrays.asList(
                "900",
                "1",
                "1",
                FIRST_STORAGE_PATH,
                "表示/一",
                FIRST_STORAGE_PATH,
                null,
                "第一章",
                SHA,
                "3",
                STAMP)));
    rows.add(
        new ArrayList<>(
            Arrays.asList(
                "100", "1", "2", "second.ks", "表示/二", "second.ks", "", null, SHA, "0", STAMP)));
    rows.add(
        new ArrayList<>(
            List.of(
                "50",
                "2",
                "1",
                FIRST_STORAGE_PATH,
                "別/一",
                FIRST_STORAGE_PATH,
                "s",
                "章",
                SHA,
                ORACLE_MAXIMUM_N12,
                STAMP)));
    return rows;
  }

  private static PostgresCopyTextEncoder encoder() {
    return new PostgresCopyTextEncoder();
  }
}
