package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-VIDEO001..024; independent primary-document TSV and synthetic-claim COPY golden. */
final class VideoMigrationCatalogueTest {
  private static final String METADATA_RESOURCE = "/fixtures/migration-video-catalogue-20.tsv";
  private static final String WIRE_RESOURCE = "/fixtures/migration-video-copy-20.wire";
  private static final String SHA =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String MICRO_STAMP = "2026-01-02T03:04:05.000001Z";
  private static final String FIRST_ID = "main-01";
  private static final String SECOND_ID = "main-01-subtrack";
  private static final String LAST_ID = "opening";
  private static final String UNKNOWN_ID = "unknown-video";
  private static final String UNKNOWN_PATH = "unknown.mp4";
  private static final String DIAGNOSTIC = "migration video catalogue input is invalid";
  private static final String ROW_DIAGNOSTIC = "migration media asset COPY row is invalid";
  private static final String MAIN_CATEGORY = "メインパート";
  private static final String OVA_CATEGORY = "OVA";
  private static final String OPENING_CATEGORY = "オープニング";
  private static final int COUNT = 20;
  private static final int TARGET_BASE = 1000;
  private static final int TASKS = 64;
  private static final int WORKERS = 8;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final long MAX_N12 = 999999999999L;

  @Test
  void allTwentyMetadataValuesEqualTheIndependentPrimaryDocumentGolden() throws IOException {
    assertEquals(
        new String(resource(METADATA_RESOURCE), StandardCharsets.UTF_8),
        canonical(new VideoMigrationCatalogue()));
  }

  @Test
  void everyFixedLogicalIdLooksUpTheSameImmutableValue() throws IOException {
    var catalogue = new VideoMigrationCatalogue();
    for (var expected : primaryRows()) {
      var video = catalogue.find(expected.get(1)).orElseThrow();
      assertEquals(expected.get(2), video.title());
      assertEquals(expected.get(3), video.category());
      assertEquals(expected.get(4), video.sourceRelativePath());
      assertSame(catalogue.videos().get(Integer.parseInt(expected.get(0)) - 1), video);
    }
  }

  @Test
  void bothEndpointLookupsRetainTheApprovedNumbersAndPaths() {
    var catalogue = new VideoMigrationCatalogue();
    var first = catalogue.find(FIRST_ID).orElseThrow();
    var last = catalogue.find(LAST_ID).orElseThrow();
    assertEquals(1, first.displayOrder());
    assertEquals("main_part/NUKITASHI_THE_ANIMATION_01.mp4", first.sourceRelativePath());
    assertEquals(COUNT, last.displayOrder());
    assertEquals("op.mp4", last.sourceRelativePath());
  }

  @Test
  void unknownEmptyCaseAndWhitespaceIdsNeverSelectAnotherEntry() {
    var catalogue = new VideoMigrationCatalogue();
    for (String id : List.of(UNKNOWN_ID, "", "MAIN-01", FIRST_ID + " ", " " + FIRST_ID, "未登録"))
      assertTrue(catalogue.find(id).isEmpty());
  }

  @Test
  void nullLookupIsAnExplicitFixedInputFailure() {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> new VideoMigrationCatalogue().find(null))
            .getMessage());
  }

  @Test
  void categoryCountsAreExactlyFifteenFourAndOne() {
    var counts = new LinkedHashMap<String, Integer>();
    for (var video : new VideoMigrationCatalogue().videos())
      counts.merge(video.category(), 1, Integer::sum);
    assertEquals(Map.of(MAIN_CATEGORY, 15, OVA_CATEGORY, 4, OPENING_CATEGORY, 1), counts);
  }

  @Test
  void allFourSubtracksReferToTheFixedMainIdsAndOtherParentsAreAbsent() {
    var expected =
        Map.of(
            SECOND_ID,
            FIRST_ID,
            "main-04-subtrack",
            "main-04",
            "main-10-subtrack",
            "main-10",
            "main-11-subtrack",
            "main-11");
    var catalogue = new VideoMigrationCatalogue();
    for (var video : catalogue.videos()) {
      if (expected.containsKey(video.logicalId())) {
        assertEquals(expected.get(video.logicalId()), video.parentLogicalId().orElseThrow());
        assertTrue(catalogue.find(video.parentLogicalId().orElseThrow()).isPresent());
      } else assertTrue(video.parentLogicalId().isEmpty());
    }
  }

  @Test
  void fixedIdsPathsAndDenseDisplayOrdersHaveNoDuplicates() {
    var ids = new HashSet<String>();
    var paths = new HashSet<String>();
    var videos = new VideoMigrationCatalogue().videos();
    assertEquals(COUNT, videos.size());
    for (int index = 0; index < COUNT; index++) {
      var video = videos.get(index);
      assertTrue(ids.add(video.logicalId()));
      assertTrue(paths.add(video.sourceRelativePath()));
      assertEquals(index + 1, video.displayOrder());
      assertFalse(video.sourceRelativePath().startsWith("/"));
      assertTrue(video.sourceRelativePath().endsWith(".mp4"));
    }
  }

  @Test
  void catalogueListCannotBeMutatedOrPoisonAnotherInstance() throws IOException {
    var catalogue = new VideoMigrationCatalogue();
    assertThrows(UnsupportedOperationException.class, () -> catalogue.videos().clear());
    assertThrows(
        UnsupportedOperationException.class,
        () -> catalogue.videos().set(0, catalogue.videos().get(1)));
    assertEquals(
        new String(resource(METADATA_RESOURCE), StandardCharsets.UTF_8),
        canonical(new VideoMigrationCatalogue()));
  }

  @Test
  void bothPublicValueStringsAreFixedAndRedacted() {
    var catalogue = new VideoMigrationCatalogue();
    assertEquals("VideoMigrationCatalogue[REDACTED]", catalogue.toString());
    for (var video : catalogue.videos()) assertEquals("MigrationVideo[REDACTED]", video.toString());
  }

  @Test
  void allTwentySeventeenColumnRowsEqualTheIndependentCopyWireGolden()
      throws IOException, NoSuchAlgorithmException {
    var inputs = inputs();
    var rows = new VideoMigrationCatalogue().copyRows(inputs.targetMap, inputs.manifest(), STAMP);
    assertEquals(COUNT, rows.size());
    assertArrayEquals(resource(WIRE_RESOURCE), wire(rows));
  }

  @Test
  void mapAndManifestOrderingNeverReplaceTheApprovedDisplayOrder()
      throws IOException, NoSuchAlgorithmException {
    var inputs = inputs();
    Collections.reverse(inputs.fileClaims);
    var reversed = new LinkedHashMap<@Nullable String, @Nullable Long>();
    var metadata = new ArrayList<>(primaryRows());
    Collections.reverse(metadata);
    for (var row : metadata) reversed.put(row.get(1), 2021L - Integer.parseInt(row.get(0)));
    var rows = new VideoMigrationCatalogue().copyRows(reversed, inputs.manifest(), STAMP);
    assertEquals("2020", rows.get(0).fields().get(0));
    assertEquals(FIRST_ID, rows.get(0).fields().get(1));
    assertEquals("2001", rows.get(COUNT - 1).fields().get(0));
    assertEquals(LAST_ID, rows.get(COUNT - 1).fields().get(1));
    for (int index = 0; index < COUNT; index++)
      assertEquals(Integer.toString(index + 1), rows.get(index).fields().get(15));
  }

  @Test
  void missingOrExtraTargetMapEntriesAreRejected() throws IOException {
    var missing = inputs();
    missing.targetMap.remove(FIRST_ID);
    reject(missing);
    var extra = inputs();
    extra.targetMap.put(UNKNOWN_ID, 2000L);
    reject(extra);
  }

  @Test
  void unknownOrNullKeyCannotReplaceAKnownTargetAtTheSameCount() throws IOException {
    var unknown = inputs();
    unknown.targetMap.remove(FIRST_ID);
    unknown.targetMap.put(UNKNOWN_ID, 1001L);
    reject(unknown);
    var nullKey = inputs();
    nullKey.targetMap.remove(FIRST_ID);
    nullKey.targetMap.put(null, 1001L);
    reject(nullKey);
  }

  @Test
  void targetValuesAreNonNullPositiveN12AndGloballyUnique()
      throws IOException, NoSuchAlgorithmException {
    var nullValue = inputs();
    nullValue.targetMap.put(FIRST_ID, null);
    reject(nullValue);
    for (long id : List.of(-1L, 0L, MAX_N12 + 1, Long.MAX_VALUE)) {
      var invalid = inputs();
      invalid.targetMap.put(FIRST_ID, id);
      reject(invalid);
    }
    var duplicate = inputs();
    duplicate.targetMap.put(FIRST_ID, 1002L);
    reject(duplicate);
    for (long id : List.of(1L, MAX_N12)) {
      var boundary = inputs();
      boundary.targetMap.put(FIRST_ID, id);
      var row =
          new VideoMigrationCatalogue()
              .copyRows(boundary.targetMap, boundary.manifest(), STAMP)
              .get(0);
      assertEquals(Long.toString(id), row.fields().get(0));
    }
  }

  @Test
  void manifestMustDeclareExactlyTwentyFiles() throws IOException {
    var missing = inputs();
    missing.fileClaims.removeLast();
    reject(missing);
    var extra = inputs();
    extra.fileClaims.add(
        new AssetMigrationManifest.Entry(
            AssetMigrationManifest.Kind.VIDEO, UNKNOWN_PATH, "video/extra.mp4", 3, SHA));
    reject(extra);
  }

  @Test
  void unknownAndCaseChangedCurrentPathsCannotReplaceAnApprovedFile() throws IOException {
    for (String path : List.of(UNKNOWN_PATH, "MAIN_PART/NUKITASHI_THE_ANIMATION_01.mp4")) {
      var invalid = inputs();
      var old = invalid.fileClaims.get(0);
      invalid.fileClaims.set(
          0,
          new AssetMigrationManifest.Entry(
              old.kind(), path, old.targetPath(), old.byteLength(), old.sha256()));
      reject(invalid);
    }
  }

  @Test
  void everyOtherAssetKindIsRejectedRatherThanSilentlyFiltered() throws IOException {
    for (var kind :
        List.of(
            AssetMigrationManifest.Kind.SCENARIO,
            AssetMigrationManifest.Kind.AUDIO,
            AssetMigrationManifest.Kind.MUSIC)) {
      var invalid = inputs();
      var old = invalid.fileClaims.get(0);
      invalid.fileClaims.set(
          0,
          new AssetMigrationManifest.Entry(
              kind, old.currentPath(), old.targetPath(), old.byteLength(), old.sha256()));
      reject(invalid);
    }
  }

  @Test
  void claimByteSizeIsForwardedToTheCurrentMediaRowContract()
      throws IOException, NoSuchAlgorithmException {
    for (long size : List.of(0L, MAX_N12 + 1)) {
      var invalid = inputs();
      replaceFirstSize(invalid, size);
      assertEquals(
          ROW_DIAGNOSTIC,
          assertThrows(
                  IllegalArgumentException.class,
                  () ->
                      new VideoMigrationCatalogue()
                          .copyRows(invalid.targetMap, invalid.manifest(), STAMP))
              .getMessage());
    }
    var maximum = inputs();
    replaceFirstSize(maximum, MAX_N12);
    assertEquals(
        Long.toString(MAX_N12),
        new VideoMigrationCatalogue()
            .copyRows(maximum.targetMap, maximum.manifest(), STAMP)
            .get(0)
            .fields()
            .get(9));
  }

  @Test
  void timestampValidationAndOneCommonMicrosecondValueArePreserved()
      throws IOException, NoSuchAlgorithmException {
    var inputs = inputs();
    for (String stamp : List.of("", "2026-01-02T03:04:05.000Z", "2026-01-02T03:04:05+00:00")) {
      assertEquals(
          ROW_DIAGNOSTIC,
          assertThrows(
                  IllegalArgumentException.class,
                  () ->
                      new VideoMigrationCatalogue()
                          .copyRows(inputs.targetMap, inputs.manifest(), stamp))
              .getMessage());
    }
    var rows =
        new VideoMigrationCatalogue().copyRows(inputs.targetMap, inputs.manifest(), MICRO_STAMP);
    for (var row : rows) assertEquals(MICRO_STAMP, row.fields().get(16));
  }

  @Test
  void allThreeNullableFactoryInputsHaveFixedDiagnostics() throws IOException {
    var inputs = inputs();
    var catalogue = new VideoMigrationCatalogue();
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> catalogue.copyRows(null, inputs.manifest(), STAMP))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> catalogue.copyRows(inputs.targetMap, null, STAMP))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> catalogue.copyRows(inputs.targetMap, inputs.manifest(), null))
            .getMessage());
  }

  @Test
  void returnedRowsAndBytesDoNotAliasMutableInputCollections()
      throws IOException, NoSuchAlgorithmException {
    var inputs = inputs();
    var rows = new VideoMigrationCatalogue().copyRows(inputs.targetMap, inputs.manifest(), STAMP);
    inputs.targetMap.clear();
    inputs.fileClaims.clear();
    assertThrows(UnsupportedOperationException.class, () -> rows.clear());
    assertThrows(UnsupportedOperationException.class, () -> rows.get(0).fields().clear());
    byte[] first = rows.get(0).copyBytes(new PostgresCopyTextEncoder());
    first[0] = 0;
    assertArrayEquals(resource(WIRE_RESOURCE), wire(rows));
  }

  @Test
  void aRejectedClaimDoesNotRepairOrPoisonIndependentNormalInput()
      throws IOException, NoSuchAlgorithmException {
    var invalid = inputs();
    replaceFirstSize(invalid, 0);
    assertThrows(
        IllegalArgumentException.class,
        () -> new VideoMigrationCatalogue().copyRows(invalid.targetMap, invalid.manifest(), STAMP));
    assertEquals(0, invalid.fileClaims.get(0).byteLength());
    var normal = inputs();
    assertArrayEquals(
        resource(WIRE_RESOURCE),
        wire(new VideoMigrationCatalogue().copyRows(normal.targetMap, normal.manifest(), STAMP)));
  }

  @Test
  void finiteWorkersBindTheSameImmutableClaimsWithoutSharedOutput()
      throws IOException, InterruptedException, ExecutionException, TimeoutException {
    var inputs = inputs();
    var manifest = inputs.manifest();
    var catalogue = new VideoMigrationCatalogue();
    byte[] expected = resource(WIRE_RESOURCE);
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var results = new ArrayList<Future<byte[]>>();
      for (int index = 0; index < TASKS; index++)
        results.add(
            executor.submit(() -> wire(catalogue.copyRows(inputs.targetMap, manifest, STAMP))));
      for (var result : results)
        assertArrayEquals(expected, result.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static FixtureInputs inputs() throws IOException {
    var ids = new LinkedHashMap<@Nullable String, @Nullable Long>();
    var claims = new ArrayList<AssetMigrationManifest.Entry>();
    for (var row : primaryRows()) {
      int order = Integer.parseInt(row.get(0));
      ids.put(row.get(1), (long) TARGET_BASE + order);
      claims.add(
          new AssetMigrationManifest.Entry(
              AssetMigrationManifest.Kind.VIDEO,
              row.get(4),
              "video/fixture-" + order + ".mp4",
              3,
              SHA));
    }
    return new FixtureInputs(ids, claims);
  }

  private static void replaceFirstSize(FixtureInputs inputs, long size) {
    var old = inputs.fileClaims.get(0);
    inputs.fileClaims.set(
        0,
        new AssetMigrationManifest.Entry(
            old.kind(), old.currentPath(), old.targetPath(), size, old.sha256()));
  }

  private static void reject(FixtureInputs inputs) {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () ->
                    new VideoMigrationCatalogue()
                        .copyRows(inputs.targetMap, inputs.manifest(), STAMP))
            .getMessage());
  }

  private static List<List<String>> primaryRows() throws IOException {
    return new String(resource(METADATA_RESOURCE), StandardCharsets.UTF_8)
        .lines()
        .map(line -> List.of(line.split("\t", -1)))
        .toList();
  }

  private static byte[] resource(String name) throws IOException {
    @Nullable InputStream found = VideoMigrationCatalogueTest.class.getResourceAsStream(name);
    if (found == null) throw new AssertionError("Independent fixture is absent");
    try (InputStream input = found) {
      return input.readAllBytes();
    }
  }

  private static String canonical(VideoMigrationCatalogue catalogue) {
    var result = new StringBuilder();
    for (var video : catalogue.videos())
      result
          .append(video.displayOrder())
          .append('\t')
          .append(video.logicalId())
          .append('\t')
          .append(video.title())
          .append('\t')
          .append(video.category())
          .append('\t')
          .append(video.sourceRelativePath())
          .append('\t')
          .append(video.parentLogicalId().orElse("-"))
          .append('\n');
    return result.toString();
  }

  private static byte[] wire(List<MediaAssetCopyRow> rows) {
    var output = new ByteArrayOutputStream();
    var encoder = new PostgresCopyTextEncoder();
    for (var row : rows) output.writeBytes(row.copyBytes(encoder));
    return output.toByteArray();
  }

  private static final class FixtureInputs {
    private final Map<@Nullable String, @Nullable Long> targetMap;
    private final List<AssetMigrationManifest.Entry> fileClaims;

    private FixtureInputs(
        Map<@Nullable String, @Nullable Long> ids, List<AssetMigrationManifest.Entry> claims) {
      targetMap = ids;
      fileClaims = claims;
    }

    private AssetMigrationManifest manifest() {
      return new AssetMigrationManifest(fileClaims);
    }
  }
}
