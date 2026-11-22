package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-MUSICCAT001..024; independent Python metadata/IDs and literal role/order golden. */
final class MusicMigrationCatalogueTest {
  private static final String DIAGNOSTIC = "migration music catalogue input is invalid";
  private static final String ROW_DIAGNOSTIC = "migration media asset COPY row is invalid";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String SHA =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String MAX_N12 = "999999999999";
  private static final String REPLACE_PATH = "BGM/ゲーム/filler-000.ogg";
  private static final String REPLACE_SECOND = "BGM/ゲーム/filler-001.ogg";
  private static final String ALONE_PATH = "曲/ゲーム/01-05 Alone.ogg";
  private static final String MUSIC_TARGET = "music/replaced.ogg";
  private static final String MUSIC_WIRE = "/fixtures/migration-music-copy-129.wire";
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final int KEY_COLUMN = 13;
  private static final int ROLE_COLUMN = 14;
  private static final int ORDER_COLUMN = 15;

  @Test
  void full129RowsMatchEveryIndependentGoldenByte() throws IOException, NoSuchAlgorithmException {
    var rows = copy(inputs());
    assertEquals(129, rows.size());
    assertArrayEquals(resource(MUSIC_WIRE), wire(rows));
  }

  @Test
  void video20AndMusic129JoinAll149RowsAndBorrowedStream()
      throws IOException, NoSuchAlgorithmException {
    var input = inputs();
    var claims = new ArrayList<>(input.claims);
    var videoClaims = new ArrayList<AssetMigrationManifest.Entry>();
    var videoIds = new HashMap<String, Long>();
    for (var fields : lines("/fixtures/migration-video-catalogue-20.tsv")) {
      int order = Integer.parseInt(fields[0]);
      videoIds.put(fields[1], 1000L + order);
      videoClaims.add(
          new AssetMigrationManifest.Entry(
              AssetMigrationManifest.Kind.VIDEO,
              fields[4],
              "video/fixture-" + order + ".mp4",
              3,
              SHA));
    }
    claims.addAll(videoClaims);
    var rows =
        new ArrayList<@Nullable MediaAssetCopyRow>(
            new VideoMigrationCatalogue()
                .copyRows(videoIds, new AssetMigrationManifest(videoClaims), STAMP));
    rows.addAll(copy(input));
    var batch = new MediaAssetCopyBatch(new AssetMigrationManifest(claims), rows);
    var expected = new ByteArrayOutputStream();
    expected.writeBytes(resource("/fixtures/migration-video-copy-20.wire"));
    expected.writeBytes(resource(MUSIC_WIRE));
    assertEquals(149, batch.rows().size());
    assertArrayEquals(expected.toByteArray(), batch.copyBytes(new PostgresCopyTextEncoder()));
    var sink = new TrackingSink();
    batch.writeTo(new PostgresCopyTextWriter(new PostgresCopyTextEncoder()), sink);
    assertArrayEquals(expected.toByteArray(), sink.toByteArray());
    assertEquals(0, sink.closes);
    assertEquals(0, sink.flushes);
  }

  @Test
  void onlyTheApproved129DeclarationCountCanEnterTheFactory() throws IOException {
    var input = inputs();
    input.claims.clear();
    reject(input);
    input = inputs();
    input.claims.remove(0);
    reject(input);
    input = inputs();
    input.claims.add(
        new AssetMigrationManifest.Entry(
            AssetMigrationManifest.Kind.MUSIC, "extra.ogg", "music/extra.ogg", 3, SHA));
    reject(input);
  }

  @Test
  void allOtherManifestKindsAreRejected() throws IOException {
    for (var kind :
        List.of(
            AssetMigrationManifest.Kind.VIDEO,
            AssetMigrationManifest.Kind.SCENARIO,
            AssetMigrationManifest.Kind.AUDIO)) {
      var input = inputs();
      var old = input.claims.get(0);
      input.claims.set(
          0,
          new AssetMigrationManifest.Entry(
              kind, old.currentPath(), old.targetPath(), old.byteLength(), old.sha256()));
      reject(input);
    }
  }

  @Test
  void targetMapCardinalityAndUnknownKeysCannotReplaceTheKnownLogicalIds() throws IOException {
    var input = inputs();
    input.ids.clear();
    reject(input);
    input = inputs();
    input.ids.remove(input.logicalByPath.get(REPLACE_PATH));
    reject(input);
    input = inputs();
    input.ids.put("unknown", 1L);
    reject(input);
    input = inputs();
    Long value = input.ids.remove(input.logicalByPath.get(REPLACE_PATH));
    input.ids.put("unknown", value);
    reject(input);
  }

  @Test
  void nullableAndNonPositiveOrOversizedTargetValuesAreRejected()
      throws IOException, NoSuchAlgorithmException {
    for (Long id : new Long[] {null, 0L, -1L, 1000000000000L}) {
      var input = inputs();
      input.ids.put(input.logicalByPath.get(REPLACE_PATH), id);
      reject(input);
    }
    var input = inputs();
    Long value = input.ids.remove(input.logicalByPath.get(REPLACE_PATH));
    input.ids.put(null, value);
    reject(input);
    input = inputs();
    input.ids.put(input.logicalByPath.get(REPLACE_PATH), 999999999999L);
    assertEquals(MAX_N12, find(copy(input), REPLACE_PATH).id());
  }

  @Test
  void targetIdCannotBeReusedAcrossDifferentGroups() throws IOException {
    var input = inputs();
    input.ids.put(
        input.logicalByPath.get(REPLACE_PATH), input.ids.get(input.logicalByPath.get(ALONE_PATH)));
    reject(input);
  }

  @Test
  void inputMapAndManifestOrderDoNotChangeCanonicalSourceOrder()
      throws IOException, NoSuchAlgorithmException {
    var input = inputs();
    Collections.reverse(input.claims);
    var keys = new ArrayList<>(input.ids.keySet());
    Collections.reverse(keys);
    var reversed = new LinkedHashMap<@Nullable String, @Nullable Long>();
    for (var key : keys) reversed.put(key, input.ids.get(key));
    assertArrayEquals(
        resource(MUSIC_WIRE),
        wire(new MusicMigrationCatalogue().copyRows(reversed, input.manifest(), STAMP)));
  }

  @Test
  void categoriesAndSectionsRemainSeparatedAndLocalOrdersRestart()
      throws IOException, NoSuchAlgorithmException {
    var rows = copy(inputs());
    var anime = find(rows, "曲/アニメ/01-01 Anime.m4a");
    assertEquals("アニメ", anime.fields().get(5));
    assertEquals("1", anime.fields().get(ORDER_COLUMN));
    var character = find(rows, "曲/キャラクターソング/01-01 Character.flac");
    assertEquals("キャラクターソング", character.fields().get(5));
    assertEquals("1", character.fields().get(ORDER_COLUMN));
    var other = find(rows, "AOther/ZZZ/03.wav");
    assertEquals("AOther", other.fields().get(4));
    assertEquals("ZZZ", other.fields().get(5));
    assertEquals("1", other.fields().get(ORDER_COLUMN));
  }

  @Test
  void exactFuzzyAndBothMissingSidesFreezeApprovedKeysRolesAndOrders()
      throws IOException, NoSuchAlgorithmException {
    var rows = copy(inputs());
    assertPair(rows, "曲/ゲーム/01-01 Alpha.ogg", "alpha", "M", "1");
    assertPair(rows, "曲/ゲーム/01-02 Alpha inst.ogg", "alpha", "I", "1");
    assertPair(rows, "曲/ゲーム/01-03 Beta.ogg", "beta", "M", "2");
    assertPair(rows, "曲/ゲーム/01-04 Beto inst.ogg", "beta", "I", "2");
    assertPair(rows, ALONE_PATH, "alone", "M", "3");
    assertPair(rows, "曲/ゲーム/01-06 Zzzzzzz inst.ogg", "zzzzzzz", "I", "4");
    assertEquals("01-04 Beto inst", find(rows, "曲/ゲーム/01-04 Beto inst.ogg").fields().get(3));
  }

  @Test
  void nonSongTracksHaveNoKeyAndUnicodeCodepointLocalPathOrder()
      throws IOException, NoSuchAlgorithmException {
    var input = inputs();
    replacePath(input, REPLACE_PATH, "BGM/ゲーム/😀.ogg", MUSIC_TARGET);
    replacePath(input, REPLACE_SECOND, "BGM/ゲーム/\ue000.ogg", "music/second.ogg");
    var rows = copy(input);
    var bmp = find(rows, "BGM/ゲーム/\ue000.ogg");
    var supplementary = find(rows, "BGM/ゲーム/😀.ogg");
    assertEquals("116", bmp.fields().get(ORDER_COLUMN));
    assertEquals("117", supplementary.fields().get(ORDER_COLUMN));
    assertEquals(null, bmp.fields().get(KEY_COLUMN));
    assertEquals("N", bmp.fields().get(ROLE_COLUMN));
    assertTrue(rows.indexOf(bmp) < rows.indexOf(supplementary));
  }

  @Test
  void currentOneAndTwoComponentPathsAndLeadingDotTitleArePreserved()
      throws IOException, NoSuchAlgorithmException {
    var input = inputs();
    replacePath(input, REPLACE_PATH, "Solo.ogg", MUSIC_TARGET);
    var row = find(copy(input), "Solo.ogg");
    assertEquals("Solo.ogg", row.fields().get(4));
    assertEquals("", row.fields().get(5));
    assertEquals("Solo", row.fields().get(3));
    input = inputs();
    replacePath(input, REPLACE_PATH, "BGM/a.ogg", MUSIC_TARGET);
    row = find(copy(input), "BGM/a.ogg");
    assertEquals("a.ogg", row.fields().get(5));
    input = inputs();
    replacePath(input, REPLACE_PATH, "BGM/ゲーム/.ogg", MUSIC_TARGET);
    row = find(copy(input), "BGM/ゲーム/.ogg");
    assertEquals(".ogg", row.fields().get(3));
  }

  @Test
  void allFiveMimeMappingsAndUnknownExtensionsAreExplicit()
      throws IOException, NoSuchAlgorithmException {
    var rows = copy(inputs());
    assertEquals("audio/mp4", find(rows, "曲/アニメ/01-01 Anime.m4a").fields().get(11));
    assertEquals("audio/mpeg", find(rows, "BGM/アニメ/02.mp3").fields().get(11));
    assertEquals("audio/ogg", find(rows, REPLACE_PATH).fields().get(11));
    assertEquals("audio/wav", find(rows, "AOther/ZZZ/03.wav").fields().get(11));
    assertEquals("audio/flac", find(rows, "😀Other/😀Sec/04.flac").fields().get(11));
    for (var path : List.of("BGM/ゲーム/bad.xyz", "BGM/ゲーム/noextension", "BGM/ゲーム/UPPER.OGG")) {
      var input = inputs();
      replacePath(input, REPLACE_PATH, path, MUSIC_TARGET);
      reject(input);
    }
  }

  @Test
  void targetExtensionCannotMisrepresentTheDeclaredSourceFormat() throws IOException {
    var input = inputs();
    var old = claim(input, REPLACE_PATH);
    replaceClaim(
        input,
        old,
        new AssetMigrationManifest.Entry(
            old.kind(), old.currentPath(), "music/replaced.mp3", 3, SHA));
    assertEquals(
        ROW_DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> copy(input)).getMessage());
  }

  @Test
  void byteSizeBoundariesAndDeclaredHashAreNotReobservedOrRepaired()
      throws IOException, NoSuchAlgorithmException {
    for (long size : new long[] {0, 1000000000000L}) {
      var input = inputs();
      var old = claim(input, REPLACE_PATH);
      replaceClaim(
          input,
          old,
          new AssetMigrationManifest.Entry(
              old.kind(), old.currentPath(), old.targetPath(), size, SHA));
      assertEquals(
          ROW_DIAGNOSTIC,
          assertThrows(IllegalArgumentException.class, () -> copy(input)).getMessage());
    }
    var input = inputs();
    var old = claim(input, REPLACE_PATH);
    replaceClaim(
        input,
        old,
        new AssetMigrationManifest.Entry(
            old.kind(), old.currentPath(), old.targetPath(), 999999999999L, "0".repeat(64)));
    var row = find(copy(input), REPLACE_PATH);
    assertEquals(MAX_N12, row.byteSize());
    assertEquals("0".repeat(64), row.sha256());
  }

  @Test
  void timestampInvalidFormsAreRejectedByTheExistingRowContract()
      throws IOException, NoSuchAlgorithmException {
    var input = inputs();
    for (var stamp : List.of("bad", "2026-01-02T03:04:05+00:00", "2026-01-02T03:04:05.000000001Z"))
      assertEquals(
          ROW_DIAGNOSTIC,
          assertThrows(
                  IllegalArgumentException.class,
                  () -> new MusicMigrationCatalogue().copyRows(input.ids, input.manifest(), stamp))
              .getMessage());
    var rows =
        new MusicMigrationCatalogue()
            .copyRows(input.ids, input.manifest(), "9999-12-31T23:59:59.999999Z");
    assertEquals("9999-12-31T23:59:59.999999Z", rows.get(0).createdAt());
  }

  @Test
  void duplicateNormalizedKeysCannotSilentlyDropEitherRole() throws IOException {
    for (var path : List.of("曲/ゲーム/01-07 Alpha.ogg", "曲/ゲーム/01-07 Alpha inst.ogg")) {
      var input = inputs();
      replacePath(input, ALONE_PATH, path, MUSIC_TARGET);
      reject(input);
    }
  }

  @Test
  void emptyDerivedPairKeysAreNotInventedOrChangedToNone() throws IOException {
    var input = inputs();
    replacePath(input, ALONE_PATH, "曲/ゲーム/!!!.ogg", MUSIC_TARGET);
    reject(input);
  }

  @Test
  void allThreeNullableArgumentsHaveFixedDiagnostics() throws IOException {
    var input = inputs();
    var catalogue = new MusicMigrationCatalogue();
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> catalogue.copyRows(null, input.manifest(), STAMP))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> catalogue.copyRows(input.ids, null, STAMP))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> catalogue.copyRows(input.ids, input.manifest(), null))
            .getMessage());
  }

  @Test
  void sourceMetadataBoundsDoNotTruncateFilenameTitles() throws IOException {
    var input = inputs();
    replacePath(input, REPLACE_PATH, "BGM/ゲーム/" + "a".repeat(257) + ".ogg", MUSIC_TARGET);
    assertEquals(
        ROW_DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> copy(input)).getMessage());
  }

  @Test
  void mutableInputsAndReturnedListsAndRowsDoNotShareOwnership()
      throws IOException, NoSuchAlgorithmException {
    var input = inputs();
    var rows = copy(input);
    input.ids.clear();
    input.claims.clear();
    assertArrayEquals(resource(MUSIC_WIRE), wire(rows));
    assertThrows(UnsupportedOperationException.class, () -> rows.clear());
    assertThrows(UnsupportedOperationException.class, () -> rows.get(0).fields().clear());
  }

  @Test
  void encodedBytesAreIndependentAndMatchTheSeparateFirstGoldenRow()
      throws IOException, NoSuchAlgorithmException {
    var row = copy(inputs()).get(0);
    var encoder = new PostgresCopyTextEncoder();
    byte[] first = row.copyBytes(encoder);
    byte[] second = row.copyBytes(encoder);
    assertNotSame(first, second);
    first[0] = 0;
    String whole = new String(resource(MUSIC_WIRE), StandardCharsets.UTF_8);
    assertArrayEquals(
        whole.substring(0, whole.indexOf('\n') + 1).getBytes(StandardCharsets.UTF_8), second);
  }

  @Test
  void rejectionDoesNotPoisonNormalCatalogueAndDiagnosticsStayRedacted()
      throws IOException, NoSuchAlgorithmException {
    var invalid = inputs();
    invalid.ids.clear();
    reject(invalid);
    assertArrayEquals(resource(MUSIC_WIRE), wire(copy(inputs())));
    assertEquals("MusicMigrationCatalogue[REDACTED]", new MusicMigrationCatalogue().toString());
  }

  @Test
  void finiteWorkersProduceTheSameIndependent129RowGolden()
      throws IOException, InterruptedException, ExecutionException, TimeoutException {
    var input = inputs();
    var manifest = input.manifest();
    var catalogue = new MusicMigrationCatalogue();
    byte[] expected = resource(MUSIC_WIRE);
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var results = new ArrayList<Future<byte[]>>();
      for (int i = 0; i < TASKS; i++)
        results.add(executor.submit(() -> wire(catalogue.copyRows(input.ids, manifest, STAMP))));
      for (var result : results)
        assertArrayEquals(expected, result.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static Inputs inputs() throws IOException {
    var input = new Inputs();
    for (var row : lines("/fixtures/migration-music-catalogue-129.tsv")) {
      input.claims.add(
          new AssetMigrationManifest.Entry(
              AssetMigrationManifest.Kind.MUSIC, row[0], row[1], 3, SHA));
      input.ids.put(row[3], Long.parseLong(row[2]));
      input.logicalByPath.put(row[0], row[3]);
    }
    for (var row : lines("/fixtures/migration-music-extra-id-vectors.tsv"))
      input.logicalByPath.put(row[0], row[1]);
    return input;
  }

  private static void replacePath(Inputs input, String previous, String next, String target) {
    var old = claim(input, previous);
    String oldLogical = input.logicalByPath.get(previous);
    String nextLogical = input.logicalByPath.get(next);
    assertNotNull(nextLogical);
    Long id = input.ids.remove(oldLogical);
    assertNotNull(id);
    input.ids.put(nextLogical, id);
    replaceClaim(
        input,
        old,
        new AssetMigrationManifest.Entry(old.kind(), next, target, old.byteLength(), old.sha256()));
  }

  private static AssetMigrationManifest.Entry claim(Inputs input, String path) {
    return input.claims.stream()
        .filter(entry -> entry.currentPath().equals(path))
        .findFirst()
        .orElseThrow();
  }

  private static void replaceClaim(
      Inputs input, AssetMigrationManifest.Entry old, AssetMigrationManifest.Entry next) {
    input.claims.set(input.claims.indexOf(old), next);
  }

  private static List<MediaAssetCopyRow> copy(Inputs input) throws NoSuchAlgorithmException {
    return new MusicMigrationCatalogue().copyRows(input.ids, input.manifest(), STAMP);
  }

  private static void reject(Inputs input) {
    assertEquals(
        DIAGNOSTIC, assertThrows(IllegalArgumentException.class, () -> copy(input)).getMessage());
  }

  private static MediaAssetCopyRow find(List<MediaAssetCopyRow> rows, String path) {
    return rows.stream().filter(row -> row.displayPath().equals(path)).findFirst().orElseThrow();
  }

  private static void assertPair(
      List<MediaAssetCopyRow> rows, String path, String key, String role, String order) {
    var row = find(rows, path);
    assertEquals(key, row.fields().get(KEY_COLUMN));
    assertEquals(role, row.fields().get(ROLE_COLUMN));
    assertEquals(order, row.fields().get(ORDER_COLUMN));
  }

  private static List<String[]> lines(String name) throws IOException {
    return new String(resource(name), StandardCharsets.UTF_8)
        .lines()
        .map(line -> line.split("\t", -1))
        .toList();
  }

  private static byte[] resource(String name) throws IOException {
    try (var input = MusicMigrationCatalogueTest.class.getResourceAsStream(name)) {
      if (input == null) throw new AssertionError("independent fixture absent");
      return input.readAllBytes();
    }
  }

  private static byte[] wire(List<MediaAssetCopyRow> rows) {
    var output = new ByteArrayOutputStream();
    var encoder = new PostgresCopyTextEncoder();
    for (var row : rows) output.writeBytes(row.copyBytes(encoder));
    return output.toByteArray();
  }

  private static final class Inputs {
    private final ArrayList<AssetMigrationManifest.Entry> claims = new ArrayList<>();
    private final HashMap<@Nullable String, @Nullable Long> ids = new HashMap<>();
    private final HashMap<String, String> logicalByPath = new HashMap<>();

    private AssetMigrationManifest manifest() {
      return new AssetMigrationManifest(claims);
    }
  }

  private static final class TrackingSink extends ByteArrayOutputStream {
    private int closes;
    private int flushes;

    @Override
    public void close() {
      closes++;
    }

    @Override
    public void flush() {
      flushes++;
    }
  }
}
