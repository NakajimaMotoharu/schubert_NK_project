package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-MIG-COPYMAN001..012; independently framed tuples/Python SHA, no data/DB IO. */
final class MigrationMasterCopyManifestTest {
  private static final String CLAIM_HASH =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String DIAGNOSTIC = "migration COPY manifest input is invalid";
  private static final int SPEAKER_PART = 2;
  private static final int AUDIO_PART = 3;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final String NORMAL =
      "NKMIGCOPY1\nMAPPING\ta9dd686885362b4e2455c9ada4770fcbafd983819fee70ca02a0177323bd0500\nspeakers\t1\t46\t7075f6a72b05c4cff3830220732aa044852d3c871eb3c016c550015c2aa501ac\nscript_files\t1\t141\t57621009e943ae8a6da658cc58070e0442f5af23a9300ef631e6a6fe4302e101\nscript_entries\t1\t63\tae22539e017a3b2884b3cd62b362ad1738ce54a5d2459693d8c670c9c0eafe95\naudio_files\t1\t136\t5916f31fc39b26175b3383fc5944e9972fb532fa30e76ac8f70e0de18070cbe3\nmedia_assets\t1\t169\t8d47e701d4300e31892e1ee4516660581c632689da66c0cad440be50954b30fe\nentry_audio_links\t1\t39\tcaed946009561acc38580f847b47b139f453a88356b204b73391bcb5cc4f9eef\n";
  private static final String NORMAL_HASH =
      "744f7e0bd0a7dd16ab4454db3c0852c244101d25b22692de2cf167adb5dbdc90";
  private static final String EMPTY =
      "NKMIGCOPY1\nMAPPING\t83b87552a2f59f743b0c28ad12ed8bbb5e0f38c4a3794c68a29f35a3974284e9\nspeakers\t0\t0\te3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\nscript_files\t0\t0\te3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\nscript_entries\t0\t0\te3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\naudio_files\t0\t0\te3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\nmedia_assets\t0\t0\te3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\nentry_audio_links\t0\t0\te3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\n";
  private static final String EMPTY_HASH =
      "4444698baa3c905644477124201c2c291637b7c8441ed296c30acb231b1dcd90";
  private static final String NORMAL_MAPPING_HASH =
      "a9dd686885362b4e2455c9ada4770fcbafd983819fee70ca02a0177323bd0500";
  private static final String DIFFERENT =
      "NKMIGCOPY1\nMAPPING\t72b30638441593e9069a088afaca956ce235dfb5c8a2edd795732eaa41f3ea44\nspeakers\t1\t46\t7075f6a72b05c4cff3830220732aa044852d3c871eb3c016c550015c2aa501ac\nscript_files\t1\t141\t57621009e943ae8a6da658cc58070e0442f5af23a9300ef631e6a6fe4302e101\nscript_entries\t1\t63\tae22539e017a3b2884b3cd62b362ad1738ce54a5d2459693d8c670c9c0eafe95\naudio_files\t1\t136\t5916f31fc39b26175b3383fc5944e9972fb532fa30e76ac8f70e0de18070cbe3\nmedia_assets\t1\t169\t8d47e701d4300e31892e1ee4516660581c632689da66c0cad440be50954b30fe\nentry_audio_links\t1\t39\tcaed946009561acc38580f847b47b139f453a88356b204b73391bcb5cc4f9eef\n";
  private static final String DIFFERENT_HASH =
      "e377044a13ed472d31cb6b1518f7004b8661a7330102b82d8e929a903d8d5cde";

  @Test
  void copyman001IndependentNormalSixTuples() throws Exception {
    var result = normal();
    assertArrayEquals(NORMAL.getBytes(StandardCharsets.US_ASCII), result.canonicalBytes());
    assertEquals(NORMAL_HASH, result.sha256());
    assertEquals(NORMAL_MAPPING_HASH, result.mappingSha256());
  }

  @Test
  void copyman002EmptySixStreamsHaveFixedEmptySha() throws Exception {
    var result = new MigrationMasterCopyManifest(emptyMappings(), empty());
    assertArrayEquals(EMPTY.getBytes(StandardCharsets.US_ASCII), result.canonicalBytes());
    assertEquals(EMPTY_HASH, result.sha256());
    assertEquals(
        Map.of(
            "speakers",
            0L,
            "script_files",
            0L,
            "script_entries",
            0L,
            "audio_files",
            0L,
            "media_assets",
            0L,
            "entry_audio_links",
            0L),
        result.rowCounts());
  }

  @Test
  void copyman003NullBoundaries() throws Exception {
    var data = MigrationMasterCopyFingerprintTest.normal();
    assertThrows(IllegalArgumentException.class, () -> new MigrationMasterCopyManifest(null, data));
    assertThrows(
        IllegalArgumentException.class,
        () -> new MigrationMasterCopyManifest(mappings(-1, -2), null));
  }

  @Test
  void copyman004FileCountMismatch() throws Exception {
    rejectCount(0);
  }

  @Test
  void copyman005EntryCountMismatch() throws Exception {
    rejectCount(1);
  }

  @Test
  void copyman006SpeakerCountMismatch() throws Exception {
    rejectCount(2);
  }

  @Test
  void copyman007AudioCountMismatch() throws Exception {
    rejectCount(3);
  }

  @Test
  void copyman008BytesAreDefensive() throws Exception {
    var result = normal();
    var bytes = result.canonicalBytes();
    bytes[0] = 0;
    assertNotSame(bytes, result.canonicalBytes());
    assertArrayEquals(NORMAL.getBytes(StandardCharsets.US_ASCII), result.canonicalBytes());
    assertEquals(NORMAL_HASH, result.sha256());
  }

  @Test
  void copyman009SixCountsAreImmutable() throws Exception {
    var result = normal();
    assertEquals(
        Map.of(
            "speakers",
            1L,
            "script_files",
            1L,
            "script_entries",
            1L,
            "audio_files",
            1L,
            "media_assets",
            1L,
            "entry_audio_links",
            1L),
        result.rowCounts());
    assertThrows(UnsupportedOperationException.class, () -> result.rowCounts().put("speakers", 2L));
  }

  @Test
  void copyman010SameCopyTuplesDifferentDeclaredMappingChangesBinding() throws Exception {
    var result =
        new MigrationMasterCopyManifest(
            mappings(-1, -3), MigrationMasterCopyFingerprintTest.normal());
    assertArrayEquals(DIFFERENT.getBytes(StandardCharsets.US_ASCII), result.canonicalBytes());
    assertEquals(DIFFERENT_HASH, result.sha256());
    assertNotEquals(NORMAL_HASH, result.sha256());
  }

  @Test
  void copyman011FiniteConcurrentImmutableSource() throws Exception {
    var mapping = mappings(-1, -2);
    var data = MigrationMasterCopyFingerprintTest.normal();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<Void>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(
            executor.submit(
                () -> {
                  var result = new MigrationMasterCopyManifest(mapping, data);
                  assertEquals(NORMAL_HASH, result.sha256());
                  assertArrayEquals(
                      NORMAL.getBytes(StandardCharsets.US_ASCII), result.canonicalBytes());
                  return null;
                }));
      for (var future : futures) assertNull(future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  @Test
  void copyman012FixedRedactionAndRepeatedSnapshot() throws Exception {
    assertEquals("MigrationMasterCopyManifest[REDACTED]", normal().toString());
    assertEquals(NORMAL_HASH, normal().sha256());
    var failure =
        assertThrows(
            IllegalArgumentException.class, () -> new MigrationMasterCopyManifest(null, null));
    assertEquals(DIAGNOSTIC, failure.getMessage());
    assertNull(failure.getCause());
  }

  private static MigrationMasterCopyManifest normal() throws Exception {
    return new MigrationMasterCopyManifest(
        mappings(-1, -2), MigrationMasterCopyFingerprintTest.normal());
  }

  private static void rejectCount(int part) throws Exception {
    var data = MigrationMasterCopyFingerprintTest.normal();
    var failure =
        assertThrows(
            IllegalArgumentException.class,
            () -> new MigrationMasterCopyManifest(mappings(part, -2), data));
    assertEquals(DIAGNOSTIC, failure.getMessage());
    assertNull(failure.getCause());
  }

  private static CurrentMigrationMappingManifest mappings(int extra, long currentSpeaker)
      throws Exception {
    var files = new ArrayList<ScenarioFileMigrationMap.FilePair>();
    files.add(new ScenarioFileMigrationMap.FilePair(1, 10, 700));
    if (extra == 0) files.add(new ScenarioFileMigrationMap.FilePair(2, 11, 701));
    var fm = new ScenarioFileMigrationMap(files);
    var ids = new ArrayList<ScenarioEntryMigrationMap.IdPair>();
    var placement = new ArrayList<ScenarioEntryPlacementMap.Placement>();
    ids.add(new ScenarioEntryMigrationMap.IdPair(20, 900));
    placement.add(new ScenarioEntryPlacementMap.Placement(1, 10, 20, 0));
    if (extra == 1) {
      ids.add(new ScenarioEntryMigrationMap.IdPair(21, 901));
      placement.add(new ScenarioEntryPlacementMap.Placement(1, 10, 21, 1));
    }
    var speakers = new ArrayList<SpeakerMigrationMap.SpeakerMapping>();
    speakers.add(new SpeakerMigrationMap.SpeakerMapping(1, currentSpeaker, 42));
    if (extra == SPEAKER_PART) speakers.add(new SpeakerMigrationMap.SpeakerMapping(2, 4, 43));
    var audio = new ArrayList<AudioMigrationMap.AudioMapping>();
    var assets = new ArrayList<AssetMigrationManifest.Entry>();
    audio.add(new AudioMigrationMap.AudioMapping(1, -5, 500));
    assets.add(
        new AssetMigrationManifest.Entry(
            AssetMigrationManifest.Kind.AUDIO, "g1/a.ogg", "voice/a.ogg", 3, CLAIM_HASH));
    if (extra == AUDIO_PART) {
      audio.add(new AudioMigrationMap.AudioMapping(2, 6, 501));
      assets.add(
          new AssetMigrationManifest.Entry(
              AssetMigrationManifest.Kind.AUDIO, "g2/b.ogg", "voice/b.ogg", 3, CLAIM_HASH));
    }
    return new CurrentMigrationMappingManifest(
        fm,
        new ScenarioEntryPlacementMap(fm, new ScenarioEntryMigrationMap(ids), placement),
        new SpeakerMigrationMap(speakers),
        new AudioMigrationMap(audio, new AssetMigrationManifest(assets), "g1", "g2"));
  }

  private static CurrentMigrationMappingManifest emptyMappings() throws Exception {
    var files = new ScenarioFileMigrationMap(List.of());
    return new CurrentMigrationMappingManifest(
        files,
        new ScenarioEntryPlacementMap(files, new ScenarioEntryMigrationMap(List.of()), List.of()),
        new SpeakerMigrationMap(List.of()),
        new AudioMigrationMap(List.of(), new AssetMigrationManifest(List.of()), "g1", "g2"));
  }

  private static MigrationMasterCopyDataset empty() throws Exception {
    var files = new ScenarioFileMigrationMap(List.of());
    var scenario =
        new ScenarioCopyDataset(
            new ScenarioFileCopyBatch(files, List.of()),
            new ScenarioEntryCopyBatch(
                new ScenarioEntryPlacementMap(
                    files, new ScenarioEntryMigrationMap(List.of()), List.of()),
                List.of()));
    return new MigrationMasterCopyDataset(
        new SpeakerCopyBatch(List.of()),
        new MigrationCopyDataset(
            scenario,
            List.of(),
            List.of(),
            new MediaAssetCopyBatch(new AssetMigrationManifest(List.of()), List.of())));
  }
}
