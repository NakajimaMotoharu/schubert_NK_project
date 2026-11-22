package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
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

/**
 * PT-MIG-AUDIOROW001..017: DDL limits, independent literals and bounded immutable-value
 * concurrency.
 */
final class AudioFileCopyRowTest {
  private static final String CURRENT_MOVIE_AUDIO_ROLE = "movie_audio";
  private static final String SHA =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String MAX_N12 = "999999999999";
  private static final String DIAGNOSTIC = "migration audio COPY row is invalid";
  private static final String GOLDEN =
      "500\t1\tvoice/a.ogg\t表示\ta.ogg\ta\tvoice\togg\t1200\t3\t" + SHA + "\t" + STAMP + "\n";
  private static final String ZERO = "0";
  private static final String ONE = "1";
  private static final String LEADING_ZERO_ONE = "01";
  private static final String ASCII_A = "a";
  private static final String ASCII_X = "x";
  private static final String JAPANESE_A = "あ";
  private static final int TASKS = 64;
  private static final int WORKERS = 8;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test
  void independentTwelveColumnGoldenHasExactOrderAndUtf8() {
    var row = new AudioFileCopyRow(fields());
    assertEquals(
        List.of(
            "id",
            "game_id",
            "storage_relative_path",
            "display_path",
            "file_name",
            "basename",
            "audio_role",
            "container",
            "duration_ms",
            "byte_size",
            "sha256",
            "created_at"),
        row.columnNames());
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), row.copyBytes(encoder()));
  }

  @Test
  void nullableContainerDurationAndEmptyContainerRemainDistinct() {
    var input = fields();
    input.set(7, null);
    input.set(8, null);
    assertArrayEquals(
        ("500\t1\tvoice/a.ogg\t表示\ta.ogg\ta\tvoice\t\\N\t\\N\t3\t" + SHA + "\t" + STAMP + "\n")
            .getBytes(StandardCharsets.UTF_8),
        new AudioFileCopyRow(input).copyBytes(encoder()));
    input.set(7, "");
    input.set(8, ZERO);
    assertArrayEquals(
        ("500\t1\tvoice/a.ogg\t表示\ta.ogg\ta\tvoice\t\t0\t3\t" + SHA + "\t" + STAMP + "\n")
            .getBytes(StandardCharsets.UTF_8),
        new AudioFileCopyRow(input).copyBytes(encoder()));
  }

  @Test
  void idPositiveN12AndTwoGamesHaveIndependentBoundaries() {
    for (String value : List.of(ONE, MAX_N12))
      assertEquals(value, rowWith(0, value).fields().get(0));
    for (String value :
        List.of(ZERO, "-1", LEADING_ZERO_ONE, "+1", "1.0", "1000000000000", "１", " 1", ""))
      reject(0, value);
    assertEquals("2", rowWith(1, "2").fields().get(1));
    for (String value : List.of(ZERO, "3", LEADING_ZERO_ONE, "", "１")) reject(1, value);
  }

  @Test
  void relativeStorageHasByteBoundariesAndRejectsAllDangerousSegments() {
    assertEquals(ASCII_A, rowWith(2, ASCII_A).fields().get(2));
    String ascii = ASCII_A.repeat(512);
    assertEquals(ascii, rowWith(2, ascii).fields().get(2));
    String utf8 = JAPANESE_A.repeat(170) + "ab";
    assertEquals(512, utf8.getBytes(StandardCharsets.UTF_8).length);
    assertEquals(utf8, rowWith(2, utf8).fields().get(2));
    reject(2, utf8 + ASCII_A);
    for (String value :
        List.of("", "/a", "a/", "a\\b", "a//b", ".", "..", "a/./b", "a/../b", ASCII_A.repeat(513)))
      reject(2, value);
  }

  @Test
  void mandatoryTextLimitsAreByteCountsWithoutInventedRoleEnum() {
    var limits = List.of(List.of(3, 512), List.of(4, 256), List.of(5, 255), List.of(6, 11));
    for (var limit : limits) {
      int index = limit.get(0);
      int size = limit.get(1);
      assertEquals(ASCII_X, rowWith(index, ASCII_X).fields().get(index));
      String maximum = ASCII_X.repeat(size);
      assertEquals(maximum, rowWith(index, maximum).fields().get(index));
      reject(index, "");
      reject(index, maximum + ASCII_X);
      String utf8 = JAPANESE_A.repeat(size / 3) + ASCII_X.repeat(size % 3);
      assertEquals(size, utf8.getBytes(StandardCharsets.UTF_8).length);
      assertEquals(utf8, rowWith(index, utf8).fields().get(index));
      reject(index, utf8 + ASCII_X);
    }
    assertEquals("custom", rowWith(6, "custom").fields().get(6));
  }

  @Test
  void containerVarcharLimitCountsCodePointsAndPreservesEmpty() {
    for (String value : List.of("", ASCII_A.repeat(16), JAPANESE_A.repeat(16), "𝄞".repeat(16))) {
      assertEquals(value, rowWith(7, value).fields().get(7));
    }
    reject(7, ASCII_A.repeat(17));
    reject(7, JAPANESE_A.repeat(17));
    reject(7, "𝄞".repeat(17));
  }

  @Test
  void durationAllowsCanonicalZeroAndMaximumWithoutNumericNormalization() {
    for (String value : List.of(ZERO, ONE, MAX_N12))
      assertEquals(value, rowWith(8, value).fields().get(8));
    for (String value :
        List.of("", "-1", "00", LEADING_ZERO_ONE, "+1", "1.0", "1e2", "1000000000000", " 0", "０"))
      reject(8, value);
  }

  @Test
  void actualFileByteSizeRequiresPositiveCanonicalN12() {
    for (String value : List.of(ONE, MAX_N12))
      assertEquals(value, rowWith(9, value).fields().get(9));
    for (String value : List.of(ZERO, "-1", LEADING_ZERO_ONE, "+1", "", "1000000000000"))
      reject(9, value);
  }

  @Test
  void shaIsExactlyLowerHexWithoutHashingProductionInputAsOracle() {
    for (String value :
        List.of(
            SHA.toUpperCase(java.util.Locale.ROOT),
            ASCII_A.repeat(63),
            ASCII_A.repeat(65),
            "g".repeat(64),
            "")) reject(10, value);
    assertEquals(ZERO.repeat(64), rowWith(10, ZERO.repeat(64)).fields().get(10));
  }

  @Test
  void timestampHasIndependentYearMicrosecondAndCanonicalBoundaries() {
    for (String value :
        List.of(
            "0001-01-01T00:00:00Z",
            "9999-12-31T23:59:59.999999Z",
            STAMP,
            "2026-01-02T03:04:05.000001Z"))
      assertEquals(value, rowWith(11, value).fields().get(11));
    for (String value :
        List.of(
            "0000-01-01T00:00:00Z",
            "+10000-01-01T00:00:00Z",
            "2026-01-02T03:04:05.000000001Z",
            "2026-01-02T03:04:05.000Z",
            "2026-01-02T03:04:05+00:00",
            "2026-99-99T00:00:00Z",
            "")) reject(11, value);
  }

  @Test
  void allTextColumnsRejectNonNfcUnpairedSurrogatesAndIsoControls() {
    for (int index : List.of(2, 3, 4, 5, 6, 7)) {
      for (String value :
          List.of("e\u0301", "\ud800", "\udc00", "x\u0000", "x\t", "x\n", "x\r", "x\u007f"))
        reject(index, value);
      assertEquals("é", rowWith(index, "é").fields().get(index));
    }
  }

  @Test
  void nullMissingAndExtraColumnsNeverBecomeNpeOrDefaultValues() {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> new AudioFileCopyRow(null))
            .getMessage());
    var shortRow = fields();
    shortRow.removeLast();
    assertThrows(IllegalArgumentException.class, () -> new AudioFileCopyRow(shortRow));
    var longRow = fields();
    longRow.add("extra");
    assertThrows(IllegalArgumentException.class, () -> new AudioFileCopyRow(longRow));
    for (int index : List.of(0, 1, 2, 3, 4, 5, 6, 9, 10, 11)) reject(index, null);
    var row = new AudioFileCopyRow(fields());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> row.copyBytes(null)).getMessage());
  }

  @Test
  void immutableSnapshotAndFreshBytesHaveSeparateOwnership() {
    var input = fields();
    var row = new AudioFileCopyRow(input);
    input.clear();
    assertEquals(12, row.fields().size());
    assertThrows(UnsupportedOperationException.class, () -> row.fields().clear());
    assertThrows(UnsupportedOperationException.class, () -> row.columnNames().clear());
    byte[] first = row.copyBytes(encoder());
    byte[] second = row.copyBytes(encoder());
    assertNotSame(first, second);
    first[0] = 0;
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), second);
  }

  @Test
  void sqlLikeLiteralIsOnlyCopyDataWithIndependentBackslashEscape() {
    var input = fields();
    input.set(3, "select 'x'; \\N");
    String expected =
        "500\t1\tvoice/a.ogg\tselect 'x'; \\\\N\ta.ogg\ta\tvoice\togg\t1200\t3\t"
            + SHA
            + "\t"
            + STAMP
            + "\n";
    assertArrayEquals(
        expected.getBytes(StandardCharsets.UTF_8),
        new AudioFileCopyRow(input).copyBytes(encoder()));
  }

  @Test
  void finiteWorkersObserveTheSameImmutableGoldenWithoutSharedByteArrays()
      throws InterruptedException, ExecutionException, TimeoutException {
    var row = new AudioFileCopyRow(fields());
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var results = new ArrayList<Future<byte[]>>();
      for (int index = 0; index < TASKS; index++)
        results.add(executor.submit(() -> row.copyBytes(encoder())));
      for (var result : results)
        assertArrayEquals(
            GOLDEN.getBytes(StandardCharsets.UTF_8), result.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  @Test
  void fixedRedactionAndIndependentValueSurviveRejectedInput() {
    reject(3, "private\u0000metadata");
    var row = new AudioFileCopyRow(fields());
    assertEquals("AudioFileCopyRow[REDACTED]", row.toString());
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), row.copyBytes(encoder()));
  }

  @Test
  void currentMovieAudioElevenBytesArePreservedWithoutRenamingOrTruncating() {
    assertEquals(11, CURRENT_MOVIE_AUDIO_ROLE.getBytes(StandardCharsets.UTF_8).length);
    var actual = rowWith(6, CURRENT_MOVIE_AUDIO_ROLE);
    assertEquals(CURRENT_MOVIE_AUDIO_ROLE, actual.fields().get(6));
    assertArrayEquals(
        GOLDEN
            .replace("\tvoice\t", "\t" + CURRENT_MOVIE_AUDIO_ROLE + "\t")
            .getBytes(StandardCharsets.UTF_8),
        actual.copyBytes(encoder()));
    String unicodeBoundary = JAPANESE_A.repeat(3) + "ab";
    assertEquals(11, unicodeBoundary.getBytes(StandardCharsets.UTF_8).length);
    assertEquals(unicodeBoundary, rowWith(6, unicodeBoundary).fields().get(6));
    reject(6, ASCII_X.repeat(12));
    reject(6, JAPANESE_A.repeat(4));
  }

  private static AudioFileCopyRow rowWith(int index, @Nullable String value) {
    var input = fields();
    input.set(index, value);
    return new AudioFileCopyRow(input);
  }

  private static void reject(int index, @Nullable String value) {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> rowWith(index, value)).getMessage());
  }

  private static ArrayList<@Nullable String> fields() {
    return new ArrayList<>(
        Arrays.asList(
            "500",
            ONE,
            "voice/a.ogg",
            "表示",
            "a.ogg",
            ASCII_A,
            "voice",
            "ogg",
            "1200",
            "3",
            SHA,
            STAMP));
  }

  private static PostgresCopyTextEncoder encoder() {
    return new PostgresCopyTextEncoder();
  }
}
