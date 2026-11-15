package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-MAPMAN001..008; independent SS408 frames and Python SHA256 literals, no data/DB IO. */
final class CurrentMigrationMappingManifestTest {
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final String PART_FILES = "FILES";
  private static final String CLAIM_HASH =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String DIAGNOSTIC = "migration mapping manifest input is invalid";
  private static final String NORMAL =
      "NKMIGMAPPING1\nFILES\t2\t37\t9c5820c79b521c94a56a2b07bf070756a1e7fe84f64b090740e1338483ee867a\nNKMIGFILEORDER1\n1\t-5\t101\t1\n2\t5\t401\t1\nENTRIES\t2\t56\t412afc944908b31f37ee180a3c3043262ebed7643c2d240f8b23e683ca6657cf\nNKMIGENTRYPLACEMENT1\n-10\t201\t1\t1\t101\t0\n20\t901\t2\t2\t401\t0\nSPEAKERS\t2\t58\tf07376a3f3c4c9c13d3b20eab12b5626091eeee779babebb68d74d8e1fcf6dc6\ngame_id\tcurrent_speaker_id\ttarget_speaker_id\n1\t-3\t1\n2\t4\t6\nAUDIO\t2\t56\t80b919a39739429d9c905d3a1730aba0faa88a340155c2bb0a50889b41720cb3\ngame_id\tcurrent_audio_id\ttarget_audio_id\n1\t-5\t21\n2\t8\t32\n";
  private static final String NORMAL_HASH =
      "33a5b664c4abaa54e4f2d403e70a3f2545aa6395a06ebcc7196f404749985ca4";
  private static final String EMPTY =
      "NKMIGMAPPING1\nFILES\t0\t16\tfee61b49e4c39e9062c2c6e845fefe03ca5160ce7b8881791b8338085d7e473a\nNKMIGFILEORDER1\nENTRIES\t0\t21\t5946c60b76d7bd7a3efa92a5bcc5d773d9e558a3b6260baea98e9e104ede6f30\nNKMIGENTRYPLACEMENT1\nSPEAKERS\t0\t45\t6ba2aea78407a77e5467625c22e68382bd06a746d097af921057a0f89a3acc13\ngame_id\tcurrent_speaker_id\ttarget_speaker_id\nAUDIO\t0\t41\t6a09be7493407eb5d1d18db65c2de8d7898eef78648b626ab8d0c81005cdede5\ngame_id\tcurrent_audio_id\ttarget_audio_id\n";
  private static final String EMPTY_HASH =
      "83b87552a2f59f743b0c28ad12ed8bbb5e0f38c4a3794c68a29f35a3974284e9";
  private static final String BOUNDARY =
      "NKMIGMAPPING1\nFILES\t2\t80\t88acd97c20f6df8d75afce084077141f0e712d07ecc23433e17c110ddba60aa9\nNKMIGFILEORDER1\n1\t-9223372036854775808\t1\t1\n2\t9223372036854775807\t999999999999\t1\nENTRIES\t2\t104\t9fd7e5409bb4fbe3b2f0fae72677416a00dfd435ab8b5af8497105fe4a745364\nNKMIGENTRYPLACEMENT1\n-9223372036854775808\t2\t1\t1\t1\t0\n9223372036854775807\t999999999998\t2\t2\t999999999999\t0\nSPEAKERS\t2\t105\tedb26e744dfe8422bf5e0227298e221f8ac22ca834ca4a84e9b25e1a48357c7f\ngame_id\tcurrent_speaker_id\ttarget_speaker_id\n1\t-9223372036854775808\t3\n2\t9223372036854775807\t999999999997\nAUDIO\t2\t101\tb57f5526485b2caa8e18a6d45578cfc2ad1214726ef1284a7935da83145ae37c\ngame_id\tcurrent_audio_id\ttarget_audio_id\n1\t-9223372036854775808\t4\n2\t9223372036854775807\t999999999996\n";
  private static final String BOUNDARY_HASH =
      "d2d9bfab039646d27abd0afb8694553fbd4df6eedfff93dd92e82e19acf8b0e5";
  private static final String OVERLAP_HASH =
      "1e856526747d19fa4761cccfc05dff7dc276e04dc2eb4a7ee5ef2cc1eacb0868";

  @Test
  void mapman001FourExactFramesCountsLengthsAndHashes() throws Exception {
    var result = inputs(false, false, false).manifest();
    assertArrayEquals(NORMAL.getBytes(StandardCharsets.US_ASCII), result.canonicalBytes());
    assertEquals(NORMAL_HASH, result.sha256());
    assertEquals(
        Map.of(PART_FILES, 2, "ENTRIES", 2, "SPEAKERS", 2, "AUDIO", 2), result.rowCounts());
  }

  @Test
  void mapman002EveryMissingMappingFailsWithoutImplicitEmpty() throws Exception {
    var f = inputs(false, false, false);
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () ->
                    new CurrentMigrationMappingManifest(null, f.entries(), f.speakers(), f.audio()))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> new CurrentMigrationMappingManifest(f.files(), null, f.speakers(), f.audio()))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> new CurrentMigrationMappingManifest(f.files(), f.entries(), null, f.audio()))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () ->
                    new CurrentMigrationMappingManifest(f.files(), f.entries(), f.speakers(), null))
            .getMessage());
  }

  @Test
  void mapman003EmptyPartsKeepAllFourIndependentHeaders() throws Exception {
    var files = new ScenarioFileMigrationMap(List.of());
    var entries =
        new ScenarioEntryPlacementMap(files, new ScenarioEntryMigrationMap(List.of()), List.of());
    var result =
        new CurrentMigrationMappingManifest(
            files,
            entries,
            new SpeakerMigrationMap(List.of()),
            new AudioMigrationMap(List.of(), new AssetMigrationManifest(List.of()), "g1", "g2"));
    assertArrayEquals(EMPTY.getBytes(StandardCharsets.US_ASCII), result.canonicalBytes());
    assertEquals(EMPTY_HASH, result.sha256());
    assertEquals(
        Map.of(PART_FILES, 0, "ENTRIES", 0, "SPEAKERS", 0, "AUDIO", 0), result.rowCounts());
  }

  @Test
  void mapman004ByteSnapshotsAndCountsCannotMutateRetainedState() throws Exception {
    var result = inputs(false, false, false).manifest();
    byte[] exposed = result.canonicalBytes();
    exposed[0] = 0;
    assertArrayEquals(NORMAL.getBytes(StandardCharsets.US_ASCII), result.canonicalBytes());
    assertEquals(NORMAL_HASH, result.sha256());
    assertNotSame(result.canonicalBytes(), result.canonicalBytes());
    assertThrows(UnsupportedOperationException.class, () -> result.rowCounts().put(PART_FILES, 99));
    assertEquals(2, result.rowCounts().get(PART_FILES));
    var pairs = new ArrayList<ScenarioFileMigrationMap.FilePair>();
    pairs.add(new ScenarioFileMigrationMap.FilePair(1, 9, 90));
    var files = new ScenarioFileMigrationMap(pairs);
    var entries =
        new ScenarioEntryPlacementMap(files, new ScenarioEntryMigrationMap(List.of()), List.of());
    var f = inputs(false, false, false);
    var snapshot = new CurrentMigrationMappingManifest(files, entries, f.speakers(), f.audio());
    byte[] before = snapshot.canonicalBytes();
    pairs.clear();
    assertArrayEquals(before, snapshot.canonicalBytes());
    assertEquals(1, snapshot.rowCounts().get(PART_FILES));
  }

  @Test
  void mapman005EntryTargetFileMustExistInItsDeclaredGame() throws Exception {
    var f = inputs(false, false, false);
    var missing =
        new ScenarioFileMigrationMap(
            List.of(
                new ScenarioFileMigrationMap.FilePair(1, -5, 102),
                new ScenarioFileMigrationMap.FilePair(2, 5, 401)));
    var wrongGame =
        new ScenarioFileMigrationMap(
            List.of(
                new ScenarioFileMigrationMap.FilePair(2, -5, 101),
                new ScenarioFileMigrationMap.FilePair(2, 5, 401)));
    for (var files : List.of(missing, wrongGame)) {
      assertEquals(
          DIAGNOSTIC,
          assertThrows(
                  IllegalArgumentException.class,
                  () ->
                      new CurrentMigrationMappingManifest(
                          files, f.entries(), f.speakers(), f.audio()))
              .getMessage());
      assertEquals(101, f.entries().entries().get(0).targetFileId());
      assertEquals(1, f.entries().entries().get(0).gameId());
    }
    assertEquals(NORMAL_HASH, f.manifest().sha256());
  }

  @Test
  void mapman006CanonicalSortAndIndependentTableIdSpaces() throws Exception {
    var shuffled = inputs(true, false, false).manifest();
    assertArrayEquals(NORMAL.getBytes(StandardCharsets.US_ASCII), shuffled.canonicalBytes());
    var overlapping = inputs(false, false, true).manifest();
    assertEquals(OVERLAP_HASH, overlapping.sha256());
    assertEquals(
        Map.of(PART_FILES, 2, "ENTRIES", 2, "SPEAKERS", 2, "AUDIO", 2), overlapping.rowCounts());
  }

  @Test
  void mapman007SharedImmutableManifestHasFiniteIndependentReaders() throws Exception {
    var result = inputs(false, false, false).manifest();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<String>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(
            executor.submit(
                () -> {
                  byte[] bytes = result.canonicalBytes();
                  assertArrayEquals(NORMAL.getBytes(StandardCharsets.US_ASCII), bytes);
                  bytes[0] = 0;
                  assertEquals(2, result.rowCounts().get(PART_FILES));
                  return result.sha256();
                }));
      for (var future : futures)
        assertEquals(NORMAL_HASH, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
    assertArrayEquals(NORMAL.getBytes(StandardCharsets.US_ASCII), result.canonicalBytes());
  }

  @Test
  void mapman008SignedLongAndSparseN12BoundariesFreshSnapshotAndRedaction() throws Exception {
    var one = inputs(false, true, false).manifest();
    var two = inputs(true, true, false).manifest();
    assertArrayEquals(BOUNDARY.getBytes(StandardCharsets.US_ASCII), one.canonicalBytes());
    assertArrayEquals(BOUNDARY.getBytes(StandardCharsets.US_ASCII), two.canonicalBytes());
    assertEquals(BOUNDARY_HASH, one.sha256());
    assertEquals(BOUNDARY_HASH, two.sha256());
    assertNotSame(one, two);
    assertEquals("CurrentMigrationMappingManifest[REDACTED]", one.toString());
    assertEquals(
        "CurrentMigrationMappingManifest[REDACTED]",
        inputs(false, false, false).manifest().toString());
  }

  private record Inputs(
      ScenarioFileMigrationMap files,
      ScenarioEntryPlacementMap entries,
      SpeakerMigrationMap speakers,
      AudioMigrationMap audio) {
    private CurrentMigrationMappingManifest manifest() throws NoSuchAlgorithmException {
      return new CurrentMigrationMappingManifest(files, entries, speakers, audio);
    }
  }

  private static Inputs inputs(boolean reverse, boolean boundary, boolean overlap) {
    long firstFile = boundary ? Long.MIN_VALUE : -5;
    long lastFile = boundary ? Long.MAX_VALUE : 5;
    long fileOne = boundary ? 1 : 101;
    long fileTwo = boundary ? 999_999_999_999L : 401;
    long firstEntry = boundary ? Long.MIN_VALUE : -10;
    long lastEntry = boundary ? Long.MAX_VALUE : 20;
    var pairs =
        new ArrayList<>(
            List.of(
                new ScenarioFileMigrationMap.FilePair(1, firstFile, fileOne),
                new ScenarioFileMigrationMap.FilePair(2, lastFile, fileTwo)));
    var ids =
        new ArrayList<>(
            List.of(
                new ScenarioEntryMigrationMap.IdPair(firstEntry, boundary ? 2 : 201),
                new ScenarioEntryMigrationMap.IdPair(
                    lastEntry, boundary ? 999_999_999_998L : 901)));
    var placements =
        new ArrayList<>(
            List.of(
                new ScenarioEntryPlacementMap.Placement(1, firstFile, firstEntry, 0),
                new ScenarioEntryPlacementMap.Placement(2, lastFile, lastEntry, 0)));
    var speakers = new ArrayList<SpeakerMigrationMap.@Nullable SpeakerMapping>();
    speakers.add(
        new SpeakerMigrationMap.SpeakerMapping(
            1, boundary ? Long.MIN_VALUE : -3, boundary ? 3 : overlap ? fileOne : 1));
    speakers.add(
        new SpeakerMigrationMap.SpeakerMapping(
            2, boundary ? Long.MAX_VALUE : 4, boundary ? 999_999_999_997L : overlap ? fileTwo : 6));
    var audio = new ArrayList<AudioMigrationMap.@Nullable AudioMapping>();
    audio.add(
        new AudioMigrationMap.AudioMapping(
            1, boundary ? Long.MIN_VALUE : -5, boundary ? 4 : overlap ? fileOne : 21));
    audio.add(
        new AudioMigrationMap.AudioMapping(
            2,
            boundary ? Long.MAX_VALUE : 8,
            boundary ? 999_999_999_996L : overlap ? fileTwo : 32));
    if (reverse) {
      Collections.reverse(pairs);
      Collections.reverse(ids);
      Collections.reverse(placements);
      Collections.reverse(speakers);
      Collections.reverse(audio);
    }
    var files = new ScenarioFileMigrationMap(pairs);
    return new Inputs(
        files,
        new ScenarioEntryPlacementMap(files, new ScenarioEntryMigrationMap(ids), placements),
        new SpeakerMigrationMap(speakers),
        new AudioMigrationMap(
            audio,
            new AssetMigrationManifest(
                List.of(
                    new AssetMigrationManifest.Entry(
                        AssetMigrationManifest.Kind.AUDIO,
                        "g1/a.ogg",
                        "audio/a.ogg",
                        3,
                        CLAIM_HASH),
                    new AssetMigrationManifest.Entry(
                        AssetMigrationManifest.Kind.AUDIO,
                        "g2/b.ogg",
                        "audio/b.ogg",
                        3,
                        CLAIM_HASH))),
            "g1",
            "g2"));
  }
}
