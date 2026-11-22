package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-FINGER001..020; fixed Python UTF8/COPY/SHA256 vectors independent of production code. */
final class MigrationMasterCopyFingerprintTest {
  private static final String EXPECTED_SPEAKER_TABLE = "speakers";
  private static final String NORMAL_NAME = "Alice";
  private static final String NORMAL_SPEAKER_VECTOR =
      "speakers|1|46|7075f6a72b05c4cff3830220732aa044852d3c871eb3c016c550015c2aa501ac";
  private static final String NORMAL_FILE_VECTOR =
      "script_files|1|141|57621009e943ae8a6da658cc58070e0442f5af23a9300ef631e6a6fe4302e101";
  private static final String NORMAL_ENTRY_VECTOR =
      "script_entries|1|63|ae22539e017a3b2884b3cd62b362ad1738ce54a5d2459693d8c670c9c0eafe95";
  private static final String NORMAL_AUDIO_VECTOR =
      "audio_files|1|136|5916f31fc39b26175b3383fc5944e9972fb532fa30e76ac8f70e0de18070cbe3";
  private static final String NORMAL_MEDIA_VECTOR =
      "media_assets|1|169|8d47e701d4300e31892e1ee4516660581c632689da66c0cad440be50954b30fe";
  private static final String NORMAL_LINK_VECTOR =
      "entry_audio_links|1|39|caed946009561acc38580f847b47b139f453a88356b204b73391bcb5cc4f9eef";
  private static final String EMPTY_LINK_VECTOR =
      "entry_audio_links|0|0|e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";

  private static final String SHA =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String ONE = "1";
  private static final String THREE = "3";
  private static final String SOURCE_VIDEO = "current/a.mp4";
  private static final String TARGET_VIDEO = "video/a.mp4";
  private static final String VIDEO = "VIDEO";
  private static final String SPEAKER_ID = "42";
  private static final String DIAGNOSTIC = "migration COPY fingerprint input is invalid";
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final List<String> TABLES =
      List.of(
          EXPECTED_SPEAKER_TABLE,
          "script_files",
          "script_entries",
          "audio_files",
          "media_assets",
          "entry_audio_links");
  static final List<String> NORMAL_METADATA =
      List.of(
          NORMAL_SPEAKER_VECTOR,
          NORMAL_FILE_VECTOR,
          NORMAL_ENTRY_VECTOR,
          NORMAL_AUDIO_VECTOR,
          NORMAL_MEDIA_VECTOR,
          NORMAL_LINK_VECTOR);
  static final List<String> EMPTY_METADATA =
      List.of(
          "speakers|0|0|e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "script_files|0|0|e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "script_entries|0|0|e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "audio_files|0|0|e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "media_assets|0|0|e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          EMPTY_LINK_VECTOR);
  private static final List<String> JAPANESE_METADATA =
      List.of(
          "speakers|1|50|1bbf8f3149c430700c3373ac0ac8318c20c00c84b5568a643642a564360baebb",
          NORMAL_FILE_VECTOR,
          NORMAL_ENTRY_VECTOR,
          NORMAL_AUDIO_VECTOR,
          NORMAL_MEDIA_VECTOR,
          NORMAL_LINK_VECTOR);
  private static final List<String> LITERAL_NULL_METADATA =
      List.of(
          "speakers|1|47|68b504fc7b5b7921e46c90967fe5b15021ace2f3c26e8d6a3a438bb58f5911b0",
          NORMAL_FILE_VECTOR,
          NORMAL_ENTRY_VECTOR,
          NORMAL_AUDIO_VECTOR,
          NORMAL_MEDIA_VECTOR,
          NORMAL_LINK_VECTOR);
  private static final List<String> CONTROLS_METADATA =
      List.of(
          "speakers|1|56|e2d31eac53fba2811b0e58148a95f91275a523f7c176a47a36854c203441285e",
          NORMAL_FILE_VECTOR,
          NORMAL_ENTRY_VECTOR,
          NORMAL_AUDIO_VECTOR,
          NORMAL_MEDIA_VECTOR,
          NORMAL_LINK_VECTOR);
  private static final List<String> LONGER_METADATA =
      List.of(
          "speakers|1|47|ddee4e52583b07416cba8457453f3d3c2c66e71e8a4039001554665006928287",
          NORMAL_FILE_VECTOR,
          NORMAL_ENTRY_VECTOR,
          NORMAL_AUDIO_VECTOR,
          NORMAL_MEDIA_VECTOR,
          NORMAL_LINK_VECTOR);
  private static final List<String> SAME_BYTES_METADATA =
      List.of(
          "speakers|1|46|9897abf9dcc3be43398cfd77f98f68fac21455d8a82bf801cf63fb0e502f5f6e",
          NORMAL_FILE_VECTOR,
          NORMAL_ENTRY_VECTOR,
          NORMAL_AUDIO_VECTOR,
          NORMAL_MEDIA_VECTOR,
          NORMAL_LINK_VECTOR);
  private static final List<String> TWO_SPEAKERS_METADATA =
      List.of(
          "speakers|2|89|ce3a31c727b0451ad10b61a19392f063f0f63c070831425bae39477fca958abf",
          NORMAL_FILE_VECTOR,
          NORMAL_ENTRY_VECTOR,
          NORMAL_AUDIO_VECTOR,
          NORMAL_MEDIA_VECTOR,
          NORMAL_LINK_VECTOR);
  private static final List<String> REVERSE_SPEAKERS_METADATA =
      List.of(
          "speakers|2|89|08a6641f22d33129a26e5780b2669a1db979fc3255f38701222e3d78712ae41e",
          NORMAL_FILE_VECTOR,
          NORMAL_ENTRY_VECTOR,
          NORMAL_AUDIO_VECTOR,
          NORMAL_MEDIA_VECTOR,
          NORMAL_LINK_VECTOR);
  private static final List<String> NO_LINKS_METADATA =
      List.of(
          NORMAL_SPEAKER_VECTOR,
          NORMAL_FILE_VECTOR,
          NORMAL_ENTRY_VECTOR,
          NORMAL_AUDIO_VECTOR,
          NORMAL_MEDIA_VECTOR,
          EMPTY_LINK_VECTOR);
  private static final List<String> NO_AUDIO_LINKS_METADATA =
      List.of(
          NORMAL_SPEAKER_VECTOR,
          NORMAL_FILE_VECTOR,
          NORMAL_ENTRY_VECTOR,
          "audio_files|0|0|e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          NORMAL_MEDIA_VECTOR,
          EMPTY_LINK_VECTOR);
  private static final List<String> NO_MEDIA_METADATA =
      List.of(
          NORMAL_SPEAKER_VECTOR,
          NORMAL_FILE_VECTOR,
          NORMAL_ENTRY_VECTOR,
          NORMAL_AUDIO_VECTOR,
          "media_assets|0|0|e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          NORMAL_LINK_VECTOR);
  private static final List<String> NO_ENTRIES_LINKS_METADATA =
      List.of(
          NORMAL_SPEAKER_VECTOR,
          NORMAL_FILE_VECTOR,
          "script_entries|0|0|e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          NORMAL_AUDIO_VECTOR,
          NORMAL_MEDIA_VECTOR,
          EMPTY_LINK_VECTOR);
  private static final List<String> NO_FILES_ENTRIES_LINKS_METADATA =
      List.of(
          NORMAL_SPEAKER_VECTOR,
          "script_files|0|0|e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "script_entries|0|0|e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          NORMAL_AUDIO_VECTOR,
          NORMAL_MEDIA_VECTOR,
          EMPTY_LINK_VECTOR);
  private static final List<String> CHANGED_TIME_METADATA =
      List.of(
          "speakers|1|46|c92a61b48cce1b9d80241699d0f2dcec9092a595f3de7a962c163644d0071d89",
          "script_files|1|141|f7b0c369356844eb541c8b5011c12d262e244ae4247ba406608d5d26184ce233",
          "script_entries|1|63|5add116c0fc49d1459741fa4613635dea5668cd90d2acb3d4a2c7b2de7c2c54e",
          "audio_files|1|136|f22fcc6ab7ed7fb9447735e226a1d6c4ff09b5e17ae1ba2c66a0e77c1fb1ab5b",
          "media_assets|1|169|497c5851bfae0280f2883d3401c6bd61c6637f721ad840bc976146a271baad91",
          "entry_audio_links|1|39|61373bdf3db56554603cf93197cc4c65dbe7cd0ba45a99577ff2a564b1bae4b8");

  @Test
  void finger001IndependentSixRowsByteCountsAndShaVectors() throws Exception {
    assertEquals(
        NORMAL_METADATA, metadata(new MigrationMasterCopyFingerprint().fingerprint(normal())));
  }

  @Test
  void finger002AllEmptyFixedSha256AndZeroRowsBytes() throws IOException, NoSuchAlgorithmException {
    assertEquals(
        EMPTY_METADATA, metadata(new MigrationMasterCopyFingerprint().fingerprint(emptyMaster())));
  }

  @Test
  void finger003NullMasterHasFixedFailureBeforeAnyStream() {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationMasterCopyFingerprint().fingerprint(null))
            .getMessage());
  }

  @Test
  void finger004ImmutableMetadataListAndAllStableGetters() throws Exception {
    var result = new MigrationMasterCopyFingerprint().fingerprint(normal());
    assertThrows(UnsupportedOperationException.class, () -> result.clear());
    assertEquals(
        TABLES,
        result.stream().map(MigrationMasterCopyFingerprint.TableFingerprint::table).toList());
    assertEquals(NORMAL_METADATA, metadata(result));
    for (var item : result) assertEquals("TableFingerprint[REDACTED]", item.toString());
  }

  @Test
  void finger005JapaneseNameCountsUtf8BytesNotCharacters() throws Exception {
    assertEquals(
        JAPANESE_METADATA,
        metadata(new MigrationMasterCopyFingerprint().fingerprint(withSpeaker("アリス", null))));
  }

  @Test
  void finger006NullAndLiteralBackslashNRemainDifferentBytes() throws Exception {
    var fingerprint = new MigrationMasterCopyFingerprint();
    assertEquals(
        LITERAL_NULL_METADATA, metadata(fingerprint.fingerprint(withSpeaker(NORMAL_NAME, "\\N"))));
    assertEquals(
        List.of(EXPECTED_SPEAKER_TABLE),
        fingerprint.difference(normal(), withSpeaker(NORMAL_NAME, "\\N")));
  }

  @Test
  void finger007CopyEscapingHasIndependentControlAndSlashVector() throws Exception {
    assertEquals(
        CONTROLS_METADATA,
        metadata(
            new MigrationMasterCopyFingerprint()
                .fingerprint(withSpeaker(NORMAL_NAME, "\t\n\r\\\b\f"))));
  }

  @Test
  void finger008DeclaredSpeakerOrderIsNeverSortedForHash() throws Exception {
    var fingerprint = new MigrationMasterCopyFingerprint();
    assertEquals(TWO_SPEAKERS_METADATA, metadata(fingerprint.fingerprint(twoSpeakers(false))));
    assertEquals(REVERSE_SPEAKERS_METADATA, metadata(fingerprint.fingerprint(twoSpeakers(true))));
  }

  @Test
  void finger009AddedSpeakerChangesOnlyItsCountBytesAndHash() throws Exception {
    assertEquals(
        TWO_SPEAKERS_METADATA,
        metadata(new MigrationMasterCopyFingerprint().fingerprint(twoSpeakers(false))));
    assertEquals(
        2L, new MigrationMasterCopyFingerprint().fingerprint(twoSpeakers(false)).getFirst().rows());
  }

  @Test
  void finger010NoLinksHasOnlyLinkEmptyHash() throws Exception {
    var source = normal();
    var content = source.content();
    var changed =
        new MigrationMasterCopyDataset(
            source.speakers(),
            new MigrationCopyDataset(
                content.scenario(), content.audio().audioRows(), List.of(), content.media()));
    assertEquals(
        NO_LINKS_METADATA, metadata(new MigrationMasterCopyFingerprint().fingerprint(changed)));
  }

  @Test
  void finger011NoAudioAndLinksHaveIndependentEmptyMetadata() throws Exception {
    var source = normal();
    var content = source.content();
    var changed =
        new MigrationMasterCopyDataset(
            source.speakers(),
            new MigrationCopyDataset(content.scenario(), List.of(), List.of(), content.media()));
    assertEquals(
        NO_AUDIO_LINKS_METADATA,
        metadata(new MigrationMasterCopyFingerprint().fingerprint(changed)));
  }

  @Test
  void finger012NoMediaOnlyChangesMediaHashAndCounts() throws Exception {
    var source = normal();
    var content = source.content();
    var changed =
        new MigrationMasterCopyDataset(
            source.speakers(),
            new MigrationCopyDataset(
                content.scenario(),
                content.audio().audioRows(),
                content.audio().linkRows(),
                emptyMedia()));
    assertEquals(
        NO_MEDIA_METADATA, metadata(new MigrationMasterCopyFingerprint().fingerprint(changed)));
  }

  @Test
  void finger013NoEntriesAndLinksPreserveOtherFourTables() throws Exception {
    var source = normal();
    var content = source.content();
    var changed =
        new MigrationMasterCopyDataset(
            source.speakers(),
            new MigrationCopyDataset(
                scenario(false, null, ONE, STAMP),
                content.audio().audioRows(),
                List.of(),
                content.media()));
    assertEquals(
        NO_ENTRIES_LINKS_METADATA,
        metadata(new MigrationMasterCopyFingerprint().fingerprint(changed)));
  }

  @Test
  void finger014NoFilesEntriesLinksPreserveRemainingTables() throws Exception {
    var source = normal();
    var content = source.content();
    var changed =
        new MigrationMasterCopyDataset(
            source.speakers(),
            new MigrationCopyDataset(
                emptyScenario(), content.audio().audioRows(), List.of(), content.media()));
    assertEquals(
        NO_FILES_ENTRIES_LINKS_METADATA,
        metadata(new MigrationMasterCopyFingerprint().fingerprint(changed)));
  }

  @Test
  void finger015RepeatedOwnedDigestsNeverAccumulateOrExposeInput() throws Exception {
    var fingerprint = new MigrationMasterCopyFingerprint();
    var source = normal();
    var first = fingerprint.fingerprint(source);
    var second = fingerprint.fingerprint(source);
    assertNotSame(first.getFirst(), second.getFirst());
    assertEquals(NORMAL_METADATA, metadata(first));
    assertEquals(NORMAL_METADATA, metadata(second));
    assertEquals("MigrationMasterCopyFingerprint[REDACTED]", fingerprint.toString());
  }

  @Test
  void finger016FiniteParallelFingerprintsHaveNoSharedDigestState() throws Exception {
    var fingerprint = new MigrationMasterCopyFingerprint();
    var source = normal();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<List<String>>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(executor.submit(() -> metadata(fingerprint.fingerprint(source))));
      for (var future : futures)
        assertEquals(NORMAL_METADATA, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  @Test
  void finger017IdenticalDifferenceIsEmptyImmutableAndFresh() throws Exception {
    var fingerprint = new MigrationMasterCopyFingerprint();
    var source = normal();
    var result = fingerprint.difference(source, source);
    assertTrue(result.isEmpty());
    assertThrows(UnsupportedOperationException.class, () -> result.add("unexpected"));
    assertEquals(NORMAL_METADATA, metadata(fingerprint.fingerprint(source)));
  }

  @Test
  void finger018RowsDifferBeforeByteAndHashConditions() throws Exception {
    var fingerprint = new MigrationMasterCopyFingerprint();
    assertEquals(
        List.of(EXPECTED_SPEAKER_TABLE), fingerprint.difference(normal(), twoSpeakers(false)));
    assertEquals(TABLES, fingerprint.difference(normal(), emptyMaster()));
  }

  @Test
  void finger019ByteDifferenceAndSameByteHashDifferenceAreDetected() throws Exception {
    var fingerprint = new MigrationMasterCopyFingerprint();
    var longer = withSpeaker("Alicee", null);
    var sameBytes = withSpeaker("ALICE", null);
    assertEquals(LONGER_METADATA, metadata(fingerprint.fingerprint(longer)));
    assertEquals(SAME_BYTES_METADATA, metadata(fingerprint.fingerprint(sameBytes)));
    assertEquals(List.of(EXPECTED_SPEAKER_TABLE), fingerprint.difference(normal(), longer));
    assertEquals(List.of(EXPECTED_SPEAKER_TABLE), fingerprint.difference(normal(), sameBytes));
  }

  @Test
  void finger020DifferenceNullBoundariesAndSixTableTimestampChange() throws Exception {
    var fingerprint = new MigrationMasterCopyFingerprint();
    var source = normal();
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> fingerprint.difference(null, source))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> fingerprint.difference(source, null))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> fingerprint.difference(null, null))
            .getMessage());
    var changed =
        new MigrationMasterCopyDataset(
            speakers("2026-01-02T03:04:06Z"), content("2026-01-02T03:04:06Z"));
    assertEquals(CHANGED_TIME_METADATA, metadata(fingerprint.fingerprint(changed)));
    assertEquals(TABLES, fingerprint.difference(source, changed));
  }

  private static List<String> metadata(
      List<MigrationMasterCopyFingerprint.TableFingerprint> actual) {
    return actual.stream()
        .map(item -> item.table() + "|" + item.rows() + "|" + item.bytes() + "|" + item.sha256())
        .toList();
  }

  private static MigrationMasterCopyDataset emptyMaster() {
    return new MigrationMasterCopyDataset(new SpeakerCopyBatch(List.of()), emptyContent());
  }

  private static MigrationMasterCopyDataset withSpeaker(String name, @Nullable String notes)
      throws Exception {
    return new MigrationMasterCopyDataset(
        new SpeakerCopyBatch(
            List.of(
                new SpeakerCopyRow(
                    Arrays.<@Nullable String>asList(
                        SPEAKER_ID, ONE, name, "alice", "true", notes, STAMP)))),
        content(STAMP));
  }

  private static MigrationMasterCopyDataset twoSpeakers(boolean reverse) throws Exception {
    var alice = speakers(STAMP).rows().getFirst();
    var bob =
        new SpeakerCopyRow(
            Arrays.<@Nullable String>asList("43", ONE, "Bob", "bob", "false", null, STAMP));
    return new MigrationMasterCopyDataset(
        new SpeakerCopyBatch(reverse ? List.of(bob, alice) : List.of(alice, bob)), content(STAMP));
  }

  static MigrationMasterCopyDataset normal() throws Exception {
    return new MigrationMasterCopyDataset(speakers(STAMP), content(STAMP));
  }

  private static MigrationCopyDataset content(String stamp) throws Exception {
    return new MigrationCopyDataset(
        scenario(true, SPEAKER_ID, ONE, stamp),
        List.of(audio(stamp)),
        List.of(Arrays.<@Nullable String>asList("900", "500", ONE, "voice", ONE, stamp)),
        media(stamp));
  }

  private static MigrationCopyDataset emptyContent() {
    return new MigrationCopyDataset(emptyScenario(), List.of(), List.of(), emptyMedia());
  }

  private static SpeakerCopyBatch speakers(String stamp) {
    return new SpeakerCopyBatch(
        List.of(
            new SpeakerCopyRow(
                Arrays.<@Nullable String>asList(
                    SPEAKER_ID, ONE, NORMAL_NAME, "alice", "true", null, stamp))));
  }

  private static ScenarioCopyDataset scenario(
      boolean withEntry, @Nullable String speaker, String game, String stamp) {
    var files =
        new ScenarioFileMigrationMap(
            List.of(new ScenarioFileMigrationMap.FilePair(Integer.parseInt(game), 10, 700)));
    var entries =
        new ScenarioEntryMigrationMap(
            withEntry ? List.of(new ScenarioEntryMigrationMap.IdPair(20, 900)) : List.of());
    var placement =
        new ScenarioEntryPlacementMap(
            files,
            entries,
            withEntry
                ? List.of(
                    new ScenarioEntryPlacementMap.Placement(Integer.parseInt(game), 10, 20, 0))
                : List.of());
    var fileRows =
        new ScenarioFileCopyBatch(
            files,
            List.of(
                Arrays.<@Nullable String>asList(
                    "700",
                    game,
                    ONE,
                    "script/file.txt",
                    "file.txt",
                    "file.txt",
                    null,
                    "chapter",
                    SHA,
                    THREE,
                    stamp)));
    var entryRows =
        withEntry
            ? List.of(
                new ScenarioEntryCopyRow(
                    Arrays.<@Nullable String>asList(
                        "900",
                        game,
                        "700",
                        ONE,
                        "0",
                        null,
                        speaker == null ? "narration" : "dialogue",
                        speaker,
                        null,
                        "hello",
                        "raw",
                        stamp)))
            : List.<ScenarioEntryCopyRow>of();
    return new ScenarioCopyDataset(fileRows, new ScenarioEntryCopyBatch(placement, entryRows));
  }

  private static ScenarioCopyDataset emptyScenario() {
    var files = new ScenarioFileMigrationMap(List.of());
    var entries = new ScenarioEntryMigrationMap(List.of());
    return new ScenarioCopyDataset(
        new ScenarioFileCopyBatch(files, List.of()),
        new ScenarioEntryCopyBatch(
            new ScenarioEntryPlacementMap(files, entries, List.of()), List.of()));
  }

  private static AudioFileCopyRow audio(String stamp) {
    return new AudioFileCopyRow(
        Arrays.<@Nullable String>asList(
            "500",
            ONE,
            "voice/a.ogg",
            "表示",
            "a.ogg",
            "a",
            "voice",
            "ogg",
            "1200",
            THREE,
            SHA,
            stamp));
  }

  private static MediaAssetCopyBatch media(String stamp) throws NoSuchAlgorithmException {
    var manifest =
        new AssetMigrationManifest(
            List.of(
                new AssetMigrationManifest.Entry(
                    AssetMigrationManifest.Kind.VIDEO, SOURCE_VIDEO, TARGET_VIDEO, 3, SHA)));
    var row =
        new MediaAssetCopyRow(
            Arrays.<@Nullable String>asList(
                "600",
                "video-a",
                VIDEO,
                "A",
                "MAIN",
                null,
                TARGET_VIDEO,
                SOURCE_VIDEO,
                "a.mp4",
                THREE,
                SHA,
                "video/mp4",
                null,
                null,
                null,
                ONE,
                stamp));
    return new MediaAssetCopyBatch(manifest, List.of(row));
  }

  private static MediaAssetCopyBatch emptyMedia() {
    return new MediaAssetCopyBatch(new AssetMigrationManifest(List.of()), List.of());
  }
}
