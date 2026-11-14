"""Eight focused correspondence-artifact tests plus two assembler-factory tests; fixed independent vectors."""
from pathlib import Path
import json,hashlib
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG33154-mapping958-source-v1';v=json.loads((e/'independent-golden-vectors.json').read_text());parts=v['normal']['parts'].copy();parts[2]='game_id\tcurrent_speaker_id\ttarget_speaker_id\n1\t-3\t101\n2\t4\t401\n';parts[3]='game_id\tcurrent_audio_id\ttarget_audio_id\n1\t-5\t101\n2\t8\t401\n';out=b'NKMIGMAPPING1\n'
for kind,part in zip(['FILES','ENTRIES','SPEAKERS','AUDIO'],parts):
 data=part.encode();out+=(kind+'\t2\t'+str(len(data))+'\t'+hashlib.sha256(data).hexdigest()+'\n').encode()+data
v['overlap']=dict(parts=parts,counts=[2]*4,canonical=out.decode(),length=len(out),sha256=hashlib.sha256(out).hexdigest());(e/'independent-golden-vectors.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');literal=lambda s:json.dumps(s,ensure_ascii=False);prefix='''package dev.codex.schubert.nk.migration;

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
  private static final String DIAGNOSTIC = "migration mapping manifest input is invalid";
'''
for name,k in [('NORMAL','normal'),('EMPTY','empty'),('BOUNDARY','boundary')]:prefix+='  private static final String '+name+' = '+literal(v[k]['canonical'])+';\n  private static final String '+name+'_HASH = '+literal(v[k]['sha256'])+';\n'
prefix+='  private static final String OVERLAP_HASH = '+literal(v['overlap']['sha256'])+';\n'
body='''
  @Test
  void mapman001FourExactFramesCountsLengthsAndHashes() throws Exception {
    var result = inputs(false, false, false).manifest();
    assertArrayEquals(NORMAL.getBytes(StandardCharsets.US_ASCII), result.canonicalBytes());
    assertEquals(NORMAL_HASH, result.sha256());
    assertEquals(Map.of("FILES", 2, "ENTRIES", 2, "SPEAKERS", 2, "AUDIO", 2), result.rowCounts());
  }

  @Test
  void mapman002EveryMissingMappingFailsWithoutImplicitEmpty() throws Exception {
    var f = inputs(false, false, false);
    assertEquals(DIAGNOSTIC, assertThrows(IllegalArgumentException.class,
        () -> new CurrentMigrationMappingManifest(null, f.entries(), f.speakers(), f.audio())).getMessage());
    assertEquals(DIAGNOSTIC, assertThrows(IllegalArgumentException.class,
        () -> new CurrentMigrationMappingManifest(f.files(), null, f.speakers(), f.audio())).getMessage());
    assertEquals(DIAGNOSTIC, assertThrows(IllegalArgumentException.class,
        () -> new CurrentMigrationMappingManifest(f.files(), f.entries(), null, f.audio())).getMessage());
    assertEquals(DIAGNOSTIC, assertThrows(IllegalArgumentException.class,
        () -> new CurrentMigrationMappingManifest(f.files(), f.entries(), f.speakers(), null)).getMessage());
  }

  @Test
  void mapman003EmptyPartsKeepAllFourIndependentHeaders() throws Exception {
    var files = new ScenarioFileMigrationMap(List.of());
    var entries = new ScenarioEntryPlacementMap(files, new ScenarioEntryMigrationMap(List.of()), List.of());
    var result = new CurrentMigrationMappingManifest(files, entries, new SpeakerMigrationMap(List.of()),
        new AudioMigrationMap(List.of(), new AssetMigrationManifest(List.of()), "g1", "g2"));
    assertArrayEquals(EMPTY.getBytes(StandardCharsets.US_ASCII), result.canonicalBytes());
    assertEquals(EMPTY_HASH, result.sha256());
    assertEquals(Map.of("FILES", 0, "ENTRIES", 0, "SPEAKERS", 0, "AUDIO", 0), result.rowCounts());
  }

  @Test
  void mapman004ByteSnapshotsAndCountsCannotMutateRetainedState() throws Exception {
    var result = inputs(false, false, false).manifest();
    byte[] exposed = result.canonicalBytes();
    exposed[0] = 0;
    assertArrayEquals(NORMAL.getBytes(StandardCharsets.US_ASCII), result.canonicalBytes());
    assertEquals(NORMAL_HASH, result.sha256());
    assertNotSame(result.canonicalBytes(), result.canonicalBytes());
    assertThrows(UnsupportedOperationException.class, () -> result.rowCounts().put("FILES", 99));
    assertEquals(2, result.rowCounts().get("FILES"));
    var pairs = new ArrayList<ScenarioFileMigrationMap.FilePair>();
    pairs.add(new ScenarioFileMigrationMap.FilePair(1, 9, 90));
    var files = new ScenarioFileMigrationMap(pairs);
    var entries = new ScenarioEntryPlacementMap(files, new ScenarioEntryMigrationMap(List.of()), List.of());
    var f = inputs(false, false, false);
    var snapshot = new CurrentMigrationMappingManifest(files, entries, f.speakers(), f.audio());
    byte[] before = snapshot.canonicalBytes();
    pairs.clear();
    assertArrayEquals(before, snapshot.canonicalBytes());
    assertEquals(1, snapshot.rowCounts().get("FILES"));
  }

  @Test
  void mapman005EntryTargetFileMustExistInItsDeclaredGame() throws Exception {
    var f = inputs(false, false, false);
    var missing = new ScenarioFileMigrationMap(List.of(
        new ScenarioFileMigrationMap.FilePair(1, -5, 102), new ScenarioFileMigrationMap.FilePair(2, 5, 401)));
    var wrongGame = new ScenarioFileMigrationMap(List.of(
        new ScenarioFileMigrationMap.FilePair(2, -5, 101), new ScenarioFileMigrationMap.FilePair(2, 5, 401)));
    for (var files : List.of(missing, wrongGame)) {
      assertEquals(DIAGNOSTIC, assertThrows(IllegalArgumentException.class,
          () -> new CurrentMigrationMappingManifest(files, f.entries(), f.speakers(), f.audio())).getMessage());
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
    assertEquals(Map.of("FILES", 2, "ENTRIES", 2, "SPEAKERS", 2, "AUDIO", 2), overlapping.rowCounts());
  }

  @Test
  void mapman007SharedImmutableManifestHasFiniteIndependentReaders() throws Exception {
    var result = inputs(false, false, false).manifest();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<String>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(executor.submit(() -> {
          byte[] bytes = result.canonicalBytes();
          assertArrayEquals(NORMAL.getBytes(StandardCharsets.US_ASCII), bytes);
          bytes[0] = 0;
          assertEquals(2, result.rowCounts().get("FILES"));
          return result.sha256();
        }));
      for (var future : futures) assertEquals(NORMAL_HASH, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
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
    assertEquals("CurrentMigrationMappingManifest[REDACTED]", inputs(false, false, false).manifest().toString());
  }

  private record Inputs(ScenarioFileMigrationMap files, ScenarioEntryPlacementMap entries,
      SpeakerMigrationMap speakers, AudioMigrationMap audio) {
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
    var pairs = new ArrayList<>(List.of(new ScenarioFileMigrationMap.FilePair(1, firstFile, fileOne),
        new ScenarioFileMigrationMap.FilePair(2, lastFile, fileTwo)));
    var ids = new ArrayList<>(List.of(new ScenarioEntryMigrationMap.IdPair(firstEntry, boundary ? 2 : 201),
        new ScenarioEntryMigrationMap.IdPair(lastEntry, boundary ? 999_999_999_998L : 901)));
    var placements = new ArrayList<>(List.of(new ScenarioEntryPlacementMap.Placement(1, firstFile, firstEntry, 0),
        new ScenarioEntryPlacementMap.Placement(2, lastFile, lastEntry, 0)));
    var speakers = new ArrayList<SpeakerMigrationMap.@Nullable SpeakerMapping>();
    speakers.add(new SpeakerMigrationMap.SpeakerMapping(1, boundary ? Long.MIN_VALUE : -3,
        boundary ? 3 : overlap ? fileOne : 1));
    speakers.add(new SpeakerMigrationMap.SpeakerMapping(2, boundary ? Long.MAX_VALUE : 4,
        boundary ? 999_999_999_997L : overlap ? fileTwo : 6));
    var audio = new ArrayList<AudioMigrationMap.@Nullable AudioMapping>();
    audio.add(new AudioMigrationMap.AudioMapping(1, boundary ? Long.MIN_VALUE : -5,
        boundary ? 4 : overlap ? fileOne : 21));
    audio.add(new AudioMigrationMap.AudioMapping(2, boundary ? Long.MAX_VALUE : 8,
        boundary ? 999_999_999_996L : overlap ? fileTwo : 32));
    if (reverse) {
      Collections.reverse(pairs); Collections.reverse(ids); Collections.reverse(placements);
      Collections.reverse(speakers); Collections.reverse(audio);
    }
    var files = new ScenarioFileMigrationMap(pairs);
    return new Inputs(files, new ScenarioEntryPlacementMap(files, new ScenarioEntryMigrationMap(ids), placements),
        new SpeakerMigrationMap(speakers), new AudioMigrationMap(audio, new AssetMigrationManifest(List.of()), "g1", "g2"));
  }
}
'''
newtest=r/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/CurrentMigrationMappingManifestTest.java';assert not newtest.exists();newtest.open('x').write(prefix+body)
p=newtest.with_name('CurrentMigrationAssemblerTest.java');s=p.read_text();anchor='  private static CurrentMigrationProjectionTest.Fixture fixture() {';assert s.count(anchor)==1
method='''  @Test
  void assembly021EmptyDeclaredMappingsHaveIndependentManifest() throws Exception {
    var files = new ScenarioFileMigrationMap(List.of());
    var entries = new ScenarioEntryPlacementMap(files, new ScenarioEntryMigrationMap(List.of()), List.of());
    var configured = new CurrentMigrationAssembler(files, entries, new SpeakerMigrationMap(List.of()),
        List.of(), List.of(), new AssetMigrationManifest(List.of()), "g1", "g2");
    var result = configured.mappingManifest();
    assertArrayEquals(EMPTY_VECTOR.getBytes(StandardCharsets.US_ASCII), result.canonicalBytes());
    assertEquals(EMPTY_VECTOR_HASH, result.sha256());
  }

  @Test
  void assembly022ConfiguredFileIdsAreBoundAndFreshManifestIsDefensive() throws Exception {
    var files = new ScenarioFileMigrationMap(List.of(new ScenarioFileMigrationMap.FilePair(1, 9, 90)));
    var entries = new ScenarioEntryPlacementMap(files, new ScenarioEntryMigrationMap(List.of()), List.of());
    var configured = new CurrentMigrationAssembler(files, entries, new SpeakerMigrationMap(List.of()),
        List.of(), List.of(), new AssetMigrationManifest(List.of()), "g1", "g2");
    var first = configured.mappingManifest();
    byte[] bytes = first.canonicalBytes(); bytes[0] = 0;
    var second = configured.mappingManifest();
    assertArrayEquals(ONE_FILE_VECTOR.getBytes(StandardCharsets.US_ASCII), second.canonicalBytes());
    assertEquals(ONE_FILE_VECTOR_HASH, second.sha256());
    assertEquals(1, second.rowCounts().get("FILES"));
    assertEquals(0, second.rowCounts().get("ENTRIES"));
  }

'''
constants=''
for name,k in [('EMPTY_VECTOR','empty'),('ONE_FILE_VECTOR','oneFile')]:constants+='  private static final String '+name+' = '+literal(v[k]['canonical'])+';\n  private static final String '+name+'_HASH = '+literal(v[k]['sha256'])+';\n'
s=s.replace('final class CurrentMigrationAssemblerTest {','final class CurrentMigrationAssemblerTest {\n'+constants).replace('PT-MIG-CURRENTASSEMBLY001..020','PT-MIG-CURRENTASSEMBLY001..022').replace(anchor,method+anchor);p.write_text(s);print('wrote8 +existing2 tests; no runtime or DB operation')
