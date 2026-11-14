package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-MEDIAROW001..020; current V029 pairs, independent literals and pinned Music vectors. */
final class MediaAssetCopyRowTest {
  private static final String SHA =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String MAX_N12 = "999999999999";
  private static final String VIDEO_TYPE = "VIDEO";
  private static final String MUSIC_TYPE = "MUSIC";
  private static final String VIDEO_PATH = "video/a.mp4";
  private static final String MUSIC_PATH = "music/a.ogg";
  private static final String VIDEO_MIME = "video/mp4";
  private static final String MUSIC_MIME = "audio/ogg";
  private static final String ROLE_NONE = "N";
  private static final String ROLE_MAIN = "M";
  private static final String ROLE_INSTRUMENTAL = "I";
  private static final String PAIR_KEY = "pair";
  private static final String SONG = "曲";
  private static final String ONE = "1";
  private static final String ZERO = "0";
  private static final String ASCII_X = "x";
  private static final String ASCII_A = "a";
  private static final String JAPANESE_A = "あ";
  private static final String LEADING_ZERO_ONE = "01";
  private static final String DIAGNOSTIC = "migration media asset COPY row is invalid";
  private static final String MUSIC_ID =
      "0b9886db518de3252c15cefbe0e67016379c5fea7ee12a6d9c8c7f906efd3dcf";
  private static final String VIDEO_GOLDEN =
      "700\tvideo-a\tVIDEO\tVideo\tMAIN\t\\N\tvideo/a.mp4\tvideo/a.mp4\ta.mp4\t3\t"
          + SHA
          + "\tvideo/mp4\t\\N\t\\N\t\\N\t1\t"
          + STAMP
          + "\n";
  private static final String MUSIC_GOLDEN =
      "600\t"
          + MUSIC_ID
          + "\tMUSIC\tTrack\tBGM\t\\N\tmusic/a.ogg\tmusic/a.ogg\ta.ogg\t3\t"
          + SHA
          + "\taudio/ogg\t\\N\t\\N\tN\t1\t"
          + STAMP
          + "\n";
  private static final int STORAGE_INDEX = 6;
  private static final int TASKS = 64;
  private static final int WORKERS = 8;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test
  void videoSeventeenColumnGoldenIsIndependentAndHasAllNullPairFields() throws Exception {
    var row = new MediaAssetCopyRow(video());
    assertEquals(
        List.of(
            "id",
            "logical_id",
            "media_type",
            "title",
            "category",
            "section",
            "storage_relative_path",
            "display_path",
            "file_name",
            "byte_size",
            "sha256",
            "mime_type",
            "parent_logical_id",
            "pair_key",
            "pair_role",
            "display_order",
            "created_at"),
        row.columnNames());
    assertArrayEquals(VIDEO_GOLDEN.getBytes(StandardCharsets.UTF_8), row.copyBytes(encoder()));
  }

  @Test
  void musicSeventeenColumnGoldenUsesTheIndependentFixedLogicalId() throws Exception {
    var row = new MediaAssetCopyRow(music());
    assertArrayEquals(MUSIC_GOLDEN.getBytes(StandardCharsets.UTF_8), row.copyBytes(encoder()));
    assertEquals(MUSIC_ID, row.fields().get(1));
  }

  @Test
  void positiveIdsSizeAndDisplayOrderHaveIndependentNumericBoundaries() throws Exception {
    for (int index : List.of(0, 9)) {
      for (String value : List.of(ONE, MAX_N12))
        assertEquals(value, withField(video(), index, value).fields().get(index));
      for (String value : List.of(ZERO, "-1", "+1", LEADING_ZERO_ONE, "1000000000000", ""))
        rejectField(video(), index, value);
    }
    for (String value : List.of(ONE, "9999"))
      assertEquals(value, withField(video(), 15, value).fields().get(15));
    for (String value : List.of(ZERO, "-1", "+1", LEADING_ZERO_ONE, "10000", ""))
      rejectField(video(), 15, value);
  }

  @Test
  void logicalAndParentByteLimitsAreSeparateFromActualReferenceExistence() throws Exception {
    for (int index : List.of(1, 12)) {
      for (String value : List.of(ASCII_A, ASCII_X.repeat(64), exactUtf8(64)))
        assertEquals(value, withField(video(), index, value).fields().get(index));
      rejectField(video(), index, "");
      rejectField(video(), index, ASCII_X.repeat(65));
    }
    rejectField(music(), 1, "f".repeat(64));
    rejectField(music(), 1, MUSIC_ID.toUpperCase(Locale.ROOT));
  }

  @Test
  void mediaTypeAndMusicRoleUseTheirExistingClosedSets() throws Exception {
    for (String value : List.of("video", "music", "AUDIO", "")) rejectField(video(), 2, value);
    for (String role : List.of(ROLE_MAIN, ROLE_INSTRUMENTAL, ROLE_NONE)) {
      var input = music();
      input.set(14, role);
      if (!role.equals(ROLE_NONE)) {
        input.set(4, SONG);
        input.set(13, PAIR_KEY);
      }
      assertEquals(role, new MediaAssetCopyRow(input).fields().get(14));
    }
    for (String value : List.of("X", "m", "")) rejectField(music(), 14, value);
  }

  @Test
  void mandatoryTitleCategoryAndNameLimitsCountUtf8Bytes() throws Exception {
    for (var pair : List.of(List.of(3, 256), List.of(4, 64), List.of(8, 256))) {
      int index = pair.get(0);
      int limit = pair.get(1);
      assertEquals(ASCII_X, withField(video(), index, ASCII_X).fields().get(index));
      String maximum = exactUtf8(limit);
      assertEquals(limit, maximum.getBytes(StandardCharsets.UTF_8).length);
      assertEquals(maximum, withField(video(), index, maximum).fields().get(index));
      rejectField(video(), index, "");
      rejectField(video(), index, maximum + ASCII_X);
    }
  }

  @Test
  void nullableSectionPreservesEmptyAndIts128ByteLimit() throws Exception {
    assertEquals("", withField(video(), 5, "").fields().get(5));
    String maximum = exactUtf8(128);
    assertEquals(maximum, withField(video(), 5, maximum).fields().get(5));
    rejectField(video(), 5, maximum + ASCII_X);
    assertNull(new MediaAssetCopyRow(video()).fields().get(5));
  }

  @Test
  void storageAndDisplayHave512ByteBoundsWithoutPathResolution() throws Exception {
    String storage = ASCII_X.repeat(508) + ".mp4";
    assertEquals(512, storage.getBytes(StandardCharsets.UTF_8).length);
    assertEquals(storage, withField(video(), STORAGE_INDEX, storage).fields().get(STORAGE_INDEX));
    rejectField(video(), STORAGE_INDEX, ASCII_X.repeat(509) + ".mp4");
    String display = exactUtf8(512);
    assertEquals(display, withField(video(), 7, display).fields().get(7));
    rejectField(video(), 7, display + ASCII_X);
    rejectField(video(), 7, "");
    for (String value :
        List.of(
            "", "/a.mp4", "a.mp4/", "a\\b.mp4", "a//b.mp4", ".", "..", "a/./b.mp4", "a/../b.mp4"))
      rejectField(video(), STORAGE_INDEX, value);
  }

  @Test
  void allSixMimeExtensionPairsAreExactAndNeverGuessed() throws Exception {
    var vectors =
        List.of(
            List.of(
                "music/a.m4a",
                "audio/mp4",
                "4fd7218bff36dc419e0e9a3b0d7f25170445cf063042c02e8a39c6ab0dc5f551"),
            List.of(
                "music/a.mp3",
                "audio/mpeg",
                "7a44d4660f47e2acef2b454fc5230c0202a8df59a433ee6adcd943d51b5c08bf"),
            List.of(MUSIC_PATH, MUSIC_MIME, MUSIC_ID),
            List.of(
                "music/a.wav",
                "audio/wav",
                "bc684971b5a8c32e8b78f4c25b9fccf0885204dd2c928b1ac911d2792ba90b3e"),
            List.of(
                "music/a.flac",
                "audio/flac",
                "f8674c5b67fa4c0edc5f67b3261f3323a5a9b883afb21e57f41cd28dcb3c8bb6"));
    for (var vector : vectors) {
      var input = music();
      input.set(1, vector.get(2));
      input.set(6, vector.get(0));
      input.set(7, vector.get(0));
      input.set(11, vector.get(1));
      assertEquals(vector.get(1), new MediaAssetCopyRow(input).fields().get(11));
    }
    rejectField(video(), STORAGE_INDEX, "video/a.MP4");
    rejectField(video(), 11, MUSIC_MIME);
    for (String path : List.of("music/x", "music/a.OGG", "music/a.unknown", "music.dir/x"))
      rejectField(music(), STORAGE_INDEX, path);
    for (String mime : List.of("audio/wav", "audio/OGG", "application/octet-stream", ""))
      rejectField(music(), 11, mime);
  }

  @Test
  void currentV029PairTruthRequiresEveryConditionalNonNullValue() throws Exception {
    rejectField(video(), 13, PAIR_KEY);
    rejectField(video(), 14, ROLE_MAIN);
    var both = video();
    both.set(13, PAIR_KEY);
    both.set(14, ROLE_MAIN);
    reject(both);
    rejectField(music(), 14, null);
    rejectField(music(), 13, PAIR_KEY);
    for (String role : List.of(ROLE_MAIN, ROLE_INSTRUMENTAL)) {
      var input = paired(role);
      input.set(13, null);
      reject(input);
      input.set(13, "");
      reject(input);
      input.set(13, PAIR_KEY);
      assertEquals(PAIR_KEY, new MediaAssetCopyRow(input).fields().get(13));
    }
  }

  @Test
  void assetShaIsExactlyLowercaseHex64() throws Exception {
    for (String value :
        List.of(
            SHA.toUpperCase(Locale.ROOT),
            ASCII_A.repeat(63),
            ASCII_A.repeat(65),
            "g".repeat(64),
            "")) rejectField(video(), 10, value);
    assertEquals(ZERO.repeat(64), withField(video(), 10, ZERO.repeat(64)).fields().get(10));
  }

  @Test
  void canonicalUtcYearAndMicrosecondBoundariesAreIndependent() throws Exception {
    for (String value :
        List.of(
            "0001-01-01T00:00:00Z",
            "9999-12-31T23:59:59.999999Z",
            STAMP,
            "2026-01-02T03:04:05.000001Z"))
      assertEquals(value, withField(video(), 16, value).fields().get(16));
    for (String value :
        List.of(
            "0000-01-01T00:00:00Z",
            "+10000-01-01T00:00:00Z",
            "2026-01-02T03:04:05.000000001Z",
            "2026-01-02T03:04:05.000Z",
            "2026-01-02T03:04:05+00:00",
            "invalid")) rejectField(video(), 16, value);
  }

  @Test
  void everyTextBoundaryRejectsMalformedUnicodeNonNfcAndControls() throws Exception {
    for (int index : List.of(1, 3, 4, 5, 6, 7, 8, 12)) {
      for (String value :
          List.of("e\u0301", "\ud800", "\udc00", "private\u0000", "x\t", "x\n", "x\r", "x\u007f"))
        rejectField(video(), index, value);
      String valid = index == STORAGE_INDEX ? "é.mp4" : "é";
      assertEquals(valid, withField(video(), index, valid).fields().get(index));
    }
    for (String value : List.of("e\u0301", "\ud800", "x\u0000", "x\n"))
      rejectField(paired(ROLE_MAIN), 13, value);
  }

  @Test
  void nullInputsColumnCountsRequiredElementsAndEncoderFailExplicitly() throws Exception {
    reject(null);
    var shortRow = video();
    shortRow.removeLast();
    reject(shortRow);
    var longRow = video();
    longRow.add("extra");
    reject(longRow);
    for (int index : List.of(0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 15, 16))
      rejectField(video(), index, null);
    var row = new MediaAssetCopyRow(video());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> row.copyBytes(null)).getMessage());
  }

  @Test
  void immutableDeepSnapshotAndFreshCopyBytesHaveIndependentOwnership() throws Exception {
    var input = video();
    var row = new MediaAssetCopyRow(input);
    input.clear();
    assertEquals(17, row.fields().size());
    assertThrows(UnsupportedOperationException.class, () -> row.fields().clear());
    assertThrows(UnsupportedOperationException.class, () -> row.columnNames().clear());
    byte[] first = row.copyBytes(encoder());
    byte[] second = row.copyBytes(encoder());
    assertNotSame(first, second);
    first[0] = 0;
    assertArrayEquals(VIDEO_GOLDEN.getBytes(StandardCharsets.UTF_8), second);
  }

  @Test
  void japaneseMusicLogicalIdComesFromTheIndependentFixedVector() throws Exception {
    var input = music();
    input.set(1, "ae90358a4e9bfb4593d592f221bd62411bffc9d85f997245c117dce405c47edc");
    input.set(6, "音楽/曲.flac");
    input.set(7, "音楽/曲.flac");
    input.set(8, "曲.flac");
    input.set(11, "audio/flac");
    var row = new MediaAssetCopyRow(input);
    assertEquals(
        "ae90358a4e9bfb4593d592f221bd62411bffc9d85f997245c117dce405c47edc", row.fields().get(1));
    rejectField(music(), 7, "e\u0301");
  }

  @Test
  void pairedMusicKeyHasOneTo256Utf8Bytes() throws Exception {
    for (String role : List.of(ROLE_MAIN, ROLE_INSTRUMENTAL)) {
      var input = paired(role);
      input.set(13, ASCII_A);
      assertEquals(ASCII_A, new MediaAssetCopyRow(input).fields().get(13));
      String maximum = exactUtf8(256);
      input.set(13, maximum);
      assertEquals(maximum, new MediaAssetCopyRow(input).fields().get(13));
      input.set(13, maximum + ASCII_X);
      reject(input);
    }
  }

  @Test
  void sqlLikeDisplayTextIsOnlyEscapedCopyData() throws Exception {
    var input = video();
    input.set(7, "select 'x'; \\N");
    String expected =
        "700\tvideo-a\tVIDEO\tVideo\tMAIN\t\\N\tvideo/a.mp4\tselect 'x'; \\\\N\ta.mp4\t3\t"
            + SHA
            + "\tvideo/mp4\t\\N\t\\N\t\\N\t1\t"
            + STAMP
            + "\n";
    assertArrayEquals(
        expected.getBytes(StandardCharsets.UTF_8),
        new MediaAssetCopyRow(input).copyBytes(encoder()));
  }

  @Test
  void finiteWorkersReturnIndependentExactGoldenBytes() throws Exception {
    var row = new MediaAssetCopyRow(video());
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var results = new ArrayList<Future<byte[]>>();
      for (int index = 0; index < TASKS; index++)
        results.add(executor.submit(() -> row.copyBytes(encoder())));
      for (var result : results)
        assertArrayEquals(
            VIDEO_GOLDEN.getBytes(StandardCharsets.UTF_8),
            result.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  @Test
  void fixedRedactionAndIndependentNormalValueSurviveRejectedMetadata() throws Exception {
    rejectField(video(), 3, "private\u0000metadata");
    var row = new MediaAssetCopyRow(video());
    assertEquals("MediaAssetCopyRow[REDACTED]", row.toString());
    assertArrayEquals(VIDEO_GOLDEN.getBytes(StandardCharsets.UTF_8), row.copyBytes(encoder()));
  }

  private static MediaAssetCopyRow withField(
      ArrayList<@Nullable String> input, int index, @Nullable String value)
      throws NoSuchAlgorithmException {
    input.set(index, value);
    return new MediaAssetCopyRow(input);
  }

  private static void rejectField(
      ArrayList<@Nullable String> input, int index, @Nullable String value) {
    input.set(index, value);
    reject(input);
  }

  private static void reject(@Nullable List<@Nullable String> input) {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> new MediaAssetCopyRow(input))
            .getMessage());
  }

  private static String exactUtf8(int size) {
    return JAPANESE_A.repeat(size / 3) + ASCII_X.repeat(size % 3);
  }

  private static ArrayList<@Nullable String> video() {
    return new ArrayList<>(
        Arrays.asList(
            "700",
            "video-a",
            VIDEO_TYPE,
            "Video",
            "MAIN",
            null,
            VIDEO_PATH,
            VIDEO_PATH,
            "a.mp4",
            "3",
            SHA,
            VIDEO_MIME,
            null,
            null,
            null,
            ONE,
            STAMP));
  }

  private static ArrayList<@Nullable String> music() {
    return new ArrayList<>(
        Arrays.asList(
            "600",
            MUSIC_ID,
            MUSIC_TYPE,
            "Track",
            "BGM",
            null,
            MUSIC_PATH,
            MUSIC_PATH,
            "a.ogg",
            "3",
            SHA,
            MUSIC_MIME,
            null,
            null,
            ROLE_NONE,
            ONE,
            STAMP));
  }

  private static ArrayList<@Nullable String> paired(String role) {
    var input = music();
    input.set(4, SONG);
    input.set(13, PAIR_KEY);
    input.set(14, role);
    return input;
  }

  private static PostgresCopyTextEncoder encoder() {
    return new PostgresCopyTextEncoder();
  }
}
