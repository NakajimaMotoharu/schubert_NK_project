package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.AbstractList;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/**
 * PT-MIG-CURRENTASSEMBLY001..022; real projection input, independently literal target rows and
 * wire.
 */
final class CurrentMigrationAssemblerTest {
  private static final String EMPTY_VECTOR =
      "NKMIGMAPPING1\nFILES\t0\t16\tfee61b49e4c39e9062c2c6e845fefe03ca5160ce7b8881791b8338085d7e473a\nNKMIGFILEORDER1\nENTRIES\t0\t21\t5946c60b76d7bd7a3efa92a5bcc5d773d9e558a3b6260baea98e9e104ede6f30\nNKMIGENTRYPLACEMENT1\nSPEAKERS\t0\t45\t6ba2aea78407a77e5467625c22e68382bd06a746d097af921057a0f89a3acc13\ngame_id\tcurrent_speaker_id\ttarget_speaker_id\nAUDIO\t0\t41\t6a09be7493407eb5d1d18db65c2de8d7898eef78648b626ab8d0c81005cdede5\ngame_id\tcurrent_audio_id\ttarget_audio_id\n";
  private static final String EMPTY_VECTOR_HASH =
      "83b87552a2f59f743b0c28ad12ed8bbb5e0f38c4a3794c68a29f35a3974284e9";
  private static final String ONE_FILE_VECTOR =
      "NKMIGMAPPING1\nFILES\t1\t25\t4f704e2edf473a1a5c2cc3cb29a168f3acac78f61fc276ce87c9f9c5b1c8db6f\nNKMIGFILEORDER1\n1\t9\t90\t1\nENTRIES\t0\t21\t5946c60b76d7bd7a3efa92a5bcc5d773d9e558a3b6260baea98e9e104ede6f30\nNKMIGENTRYPLACEMENT1\nSPEAKERS\t0\t45\t6ba2aea78407a77e5467625c22e68382bd06a746d097af921057a0f89a3acc13\ngame_id\tcurrent_speaker_id\ttarget_speaker_id\nAUDIO\t0\t41\t6a09be7493407eb5d1d18db65c2de8d7898eef78648b626ab8d0c81005cdede5\ngame_id\tcurrent_audio_id\ttarget_audio_id\n";
  private static final String ONE_FILE_VECTOR_HASH =
      "ac411723896848964fb14c8fac3945bc758ffa1bdc1ffc83ac9a872775df07f5";

  private static final String TARGET_SPEAKER_ONE = "1001";
  private static final int MEDIA_STORAGE_INDEX = 6;
  private static final int MEDIA_BYTES_INDEX = 9;
  private static final int MEDIA_HASH_INDEX = 10;
  private static final int MEDIA_PARENT_INDEX = 12;
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String HASH =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String MUSIC_ID =
      "6f71a62541ab381ee0186f4f946bb6af57b0824509fc4ab61fd99b3bcac5105c";
  private static final String VOICE = "voice";
  private static final String RAW = " saved raw ";
  private static final String BODY = " Body ";
  private static final String ROOT_ONE = "g1";
  private static final String ROOT_TWO = "g2";
  private static final String MUSIC_PATH = "music/c.ogg";
  private static final String VIDEO_SOURCE = "current/b.mp4";
  private static final String VIDEO_TARGET = "video/b.mp4";
  private static final String DIAGNOSTIC = "migration Current assembly input is invalid";
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test
  void assembly001AllSixTablesHaveIndependentLiteralValues() throws Exception {
    var master = normal();
    assertEquals(
        List.of(
            Arrays.asList(TARGET_SPEAKER_ONE, "1", " Namé ", "stored_norm", "false", null, STAMP)),
        master.speakers().rows().stream().map(SpeakerCopyRow::fields).toList());
    assertEquals(
        List.of(
            Arrays.asList(
                "501", "1", "1", "scenario/f.txt", "p/f", "f", null, null, HASH, "3", STAMP)),
        master.content().scenario().files().rows());
    assertEquals(
        List.of(
            Arrays.asList(
                "601", "1", "501", "1", "0", "1", "narration", null, null, BODY, RAW, STAMP)),
        master.content().scenario().entries().rows().stream()
            .map(ScenarioEntryCopyRow::fields)
            .toList());
    assertEquals(
        List.of(
            Arrays.asList(
                "701",
                "1",
                "audio/a.ogg",
                "p/a",
                "a",
                "a_KEPT",
                "movie_audio",
                null,
                "1234",
                "3",
                HASH,
                STAMP)),
        master.content().audio().audioRows().stream().map(AudioFileCopyRow::fields).toList());
    assertEquals(
        List.of(List.of("601", "701", "1", VOICE, "7", STAMP)),
        master.content().audio().linkRows());
    assertEquals(2, master.content().media().rows().size());
  }

  @Test
  void assembly002SixBorrowedStreamsMatchHandwrittenGoldenBytes() throws Exception {
    var sinks = sinks();
    normal()
        .writeAll(
            new PostgresCopyTextWriter(new PostgresCopyTextEncoder()),
            sinks.get(0),
            sinks.get(1),
            sinks.get(2),
            sinks.get(3),
            sinks.get(4),
            sinks.get(5));
    var expected = wire();
    for (int i = 0; i < 6; i++)
      assertArrayEquals(
          expected.get(i).getBytes(StandardCharsets.UTF_8), sinks.get(i).toByteArray());
  }

  @Test
  void assembly003ConstructorNullsAndNullElementsReject() {
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CurrentMigrationAssembler(
                null,
                placement(),
                speakers(),
                audioMappings(),
                orders(),
                assets(),
                ROOT_ONE,
                ROOT_TWO));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CurrentMigrationAssembler(
                files(),
                null,
                speakers(),
                audioMappings(),
                orders(),
                assets(),
                ROOT_ONE,
                ROOT_TWO));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CurrentMigrationAssembler(
                files(),
                placement(),
                null,
                audioMappings(),
                orders(),
                assets(),
                ROOT_ONE,
                ROOT_TWO));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CurrentMigrationAssembler(
                files(), placement(), speakers(), null, orders(), assets(), ROOT_ONE, ROOT_TWO));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CurrentMigrationAssembler(
                files(),
                placement(),
                speakers(),
                audioMappings(),
                null,
                assets(),
                ROOT_ONE,
                ROOT_TWO));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CurrentMigrationAssembler(
                files(),
                placement(),
                speakers(),
                audioMappings(),
                orders(),
                null,
                ROOT_ONE,
                ROOT_TWO));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CurrentMigrationAssembler(
                files(),
                placement(),
                speakers(),
                audioMappings(),
                orders(),
                assets(),
                null,
                ROOT_TWO));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CurrentMigrationAssembler(
                files(),
                placement(),
                speakers(),
                audioMappings(),
                orders(),
                assets(),
                ROOT_ONE,
                null));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CurrentMigrationAssembler(
                files(),
                placement(),
                speakers(),
                Arrays.asList((AudioMigrationMap.AudioMapping) null),
                orders(),
                assets(),
                ROOT_ONE,
                ROOT_TWO));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CurrentMigrationAssembler(
                files(),
                placement(),
                speakers(),
                audioMappings(),
                Arrays.asList((CurrentAudioLinkMapper.LinkOrder) null),
                assets(),
                ROOT_ONE,
                ROOT_TWO));
  }

  @Test
  void assembly004AllAssembleNullsFailBeforePartialReturn() throws Exception {
    var m = assembler();
    assertEquals("CurrentMigrationAssembler[REDACTED]", m.toString());
    var source = snapshot(fixture());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> m.assemble(null, media(STAMP), at()))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> m.assemble(source, null, at()))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> m.assemble(source, media(STAMP), null))
            .getMessage());
  }

  @Test
  void assembly005AllEmptyDeclarationsAndSourcesYieldSixEmptyStreams() throws Exception {
    var f = fixture();
    for (var t : f.tables) t.clear();
    var file = new ScenarioFileMigrationMap(List.of());
    var place =
        new ScenarioEntryPlacementMap(file, new ScenarioEntryMigrationMap(List.of()), List.of());
    var m =
        new CurrentMigrationAssembler(
            file,
            place,
            new SpeakerMigrationMap(List.of()),
            List.of(),
            List.of(),
            new AssetMigrationManifest(List.of()),
            ROOT_ONE,
            ROOT_TWO);
    var master = m.assemble(snapshot(f), List.of(), at());
    var output = sinks();
    master.writeAll(
        new PostgresCopyTextWriter(new PostgresCopyTextEncoder()),
        output.get(0),
        output.get(1),
        output.get(2),
        output.get(3),
        output.get(4),
        output.get(5));
    for (var sink : output) assertEquals(0, sink.size());
  }

  @Test
  void assembly006NullableCurrentRawIsNotRepairedForTarget() throws Exception {
    var f = fixture();
    f.tables.get(2).get(0)[9] = null;
    var source = snapshot(f);
    assertThrows(
        IllegalArgumentException.class, () -> assembler().assemble(source, media(STAMP), at()));
  }

  @Test
  void assembly007SpeakerStoredMetadataAndGameStayAuthoritative() throws Exception {
    var f = fixture();
    f.tables.get(0).get(0)[2] = "Preserved 名";
    f.tables.get(0).get(0)[3] = "saved-normal";
    f.tables.get(0).get(0)[5] = "saved-note";
    var result = assembler().assemble(snapshot(f), media(STAMP), at());
    assertEquals(
        List.of(
            TARGET_SPEAKER_ONE, "1", "Preserved 名", "saved-normal", "false", "saved-note", STAMP),
        result.speakers().rows().get(0).fields());
    var bad = fixture();
    bad.tables.get(0).get(0)[1] = 2;
    reject(bad);
  }

  @Test
  void assembly008FileExactPathHashAndSizeClaimsAreEnforced() throws Exception {
    var path = fixture();
    path.tables.get(1).get(0)[2] = "p/other";
    reject(path);
    var hash = fixture();
    hash.tables.get(1).get(0)[6] = "0".repeat(64);
    reject(hash);
    var size = fixture();
    size.tables.get(1).get(0)[7] = 4L;
    reject(size);
    var matching = fixture();
    matching.tables.get(1).get(0)[6] = HASH;
    matching.tables.get(1).get(0)[7] = 3L;
    assertEquals(
        HASH,
        assembler()
            .assemble(snapshot(matching), media(STAMP), at())
            .content()
            .scenario()
            .files()
            .rows()
            .get(0)
            .get(8));
  }

  @Test
  void assembly009EntryFileIndexSpeakerAndBodyAreNotRepaired() throws Exception {
    var file = fixture();
    file.tables.get(2).get(0)[2] = -99L;
    reject(file);
    var index = fixture();
    index.tables.get(2).get(0)[3] = 1;
    reject(index);
    var body = fixture();
    body.tables.get(2).get(0)[8] = "";
    reject(body);
    var dialogue = fixture();
    dialogue.tables.get(2).get(0)[5] = "dialogue";
    dialogue.tables.get(2).get(0)[6] = -2L;
    assertEquals(
        TARGET_SPEAKER_ONE,
        assembler()
            .assemble(snapshot(dialogue), media(STAMP), at())
            .content()
            .scenario()
            .entries()
            .rows()
            .get(0)
            .fields()
            .get(7));
  }

  @Test
  void assembly010AudioExactMillisecondsRoleAndClaimBoundaries() throws Exception {
    var f = fixture();
    f.tables.get(3).get(0)[7] = new java.math.BigDecimal("0.001");
    assertEquals(
        "1",
        assembler()
            .assemble(snapshot(f), media(STAMP), at())
            .content()
            .audio()
            .audioRows()
            .get(0)
            .fields()
            .get(8));
    var negative = fixture();
    negative.tables.get(3).get(0)[7] = new java.math.BigDecimal("-1.234");
    reject(negative);
    var role = fixture();
    role.tables.get(3).get(0)[5] = "x".repeat(12);
    reject(role);
    var size = fixture();
    size.tables.get(3).get(0)[8] = 4L;
    reject(size);
    var digest = fixture();
    digest.tables.get(3).get(0)[9] = "0".repeat(64);
    reject(digest);
  }

  @Test
  void assembly011LinksUseExplicitSparseOrderAndKnownTriples() throws Exception {
    assertEquals("7", normal().content().audio().linkRows().get(0).get(4));
    var entry = fixture();
    entry.tables.get(4).get(0)[0] = -99L;
    reject(entry);
    var audio = fixture();
    audio.tables.get(4).get(0)[1] = -99L;
    reject(audio);
    var kind = fixture();
    kind.tables.get(4).get(0)[2] = "unknown";
    reject(kind);
  }

  @Test
  void assembly012MediaRebindsExactKindTargetSizeHashAndCount() throws Exception {
    var source = snapshot(fixture());
    for (int index :
        List.of(MEDIA_STORAGE_INDEX, MEDIA_BYTES_INDEX, MEDIA_HASH_INDEX, MEDIA_PARENT_INDEX)) {
      var rows = media(STAMP);
      var fields = new ArrayList<@Nullable String>(rows.get(0).fields());
      fields.set(
          index,
          index == MEDIA_STORAGE_INDEX
              ? "video/other.mp4"
              : index == MEDIA_BYTES_INDEX
                  ? "4"
                  : index == MEDIA_HASH_INDEX ? "0".repeat(64) : "absent-parent");
      rows.set(0, new MediaAssetCopyRow(fields));
      assertThrows(IllegalArgumentException.class, () -> assembler().assemble(source, rows, at()));
    }
    var few = media(STAMP);
    few.remove(0);
    assertThrows(IllegalArgumentException.class, () -> assembler().assemble(source, few, at()));
    assertThrows(
        IllegalArgumentException.class,
        () -> assembler().assemble(source, Arrays.asList((MediaAssetCopyRow) null), at()));
  }

  @Test
  void assembly013OneCommonTimestampAndYearMicrosecondBoundaries() throws Exception {
    var source = snapshot(fixture());
    for (String stamp :
        List.of(
            "0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z", "2026-01-02T03:04:05.123456Z")) {
      var result = assembler().assemble(source, media(stamp), Instant.parse(stamp));
      assertEquals(stamp, result.speakers().rows().get(0).fields().get(6));
      assertEquals(stamp, result.content().audio().linkRows().get(0).get(5));
    }
    for (var bad :
        List.of(Instant.MIN, Instant.MAX, Instant.parse("2026-01-02T03:04:05.000000001Z")))
      assertThrows(
          IllegalArgumentException.class, () -> assembler().assemble(source, media(STAMP), bad));
    assertThrows(
        IllegalArgumentException.class,
        () -> assembler().assemble(source, media("2026-01-02T03:04:06Z"), at()));
  }

  @Test
  void assembly014FourAssetKindsAreSeparatedWithoutMetadataLoss() throws Exception {
    var result = normal();
    assertEquals(4, assets().entries().size());
    assertEquals(1, result.content().scenario().files().rows().size());
    assertEquals(1, result.content().audio().audioRows().size());
    assertEquals(
        List.of("VIDEO", "MUSIC"),
        result.content().media().rows().stream().map(MediaAssetCopyRow::mediaType).toList());
  }

  @Test
  void assembly015MismatchedIdentityDeclarationsCannotPassAssembly() throws Exception {
    var other =
        new ScenarioFileMigrationMap(List.of(new ScenarioFileMigrationMap.FilePair(1, -3, 502)));
    var m =
        new CurrentMigrationAssembler(
            other,
            placement(),
            speakers(),
            audioMappings(),
            orders(),
            assets(),
            ROOT_ONE,
            ROOT_TWO);
    var source = snapshot(fixture());
    assertThrows(IllegalArgumentException.class, () -> m.assemble(source, media(STAMP), at()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CurrentMigrationAssembler(
                files(),
                placement(),
                speakers(),
                List.of(new AudioMigrationMap.AudioMapping(2, -5, 701)),
                orders(),
                assets(),
                ROOT_ONE,
                ROOT_TWO));
  }

  @Test
  void assembly016Utf8StoredWhitespaceAndSqlNullHaveLiteralWire() throws Exception {
    var source = fixture();
    source.tables.get(0).get(0)[5] = "\\N";
    var result = assembler().assemble(snapshot(source), media(STAMP), at());
    var sink = new ByteArrayOutputStream();
    result.speakers().writeTo(new PostgresCopyTextWriter(new PostgresCopyTextEncoder()), sink);
    assertArrayEquals(
        "1001\t1\t Namé \tstored_norm\tfalse\t\\\\N\t2026-01-02T03:04:05Z\n"
            .getBytes(StandardCharsets.UTF_8),
        sink.toByteArray());
  }

  @Test
  void assembly017ConstructorAndSourceListsAreDeepSnapshots() throws Exception {
    var audio = new ArrayList<AudioMigrationMap.@Nullable AudioMapping>(audioMappings());
    var links = new ArrayList<CurrentAudioLinkMapper.@Nullable LinkOrder>(orders());
    var m =
        new CurrentMigrationAssembler(
            files(), placement(), speakers(), audio, links, assets(), ROOT_ONE, ROOT_TWO);
    audio.clear();
    links.clear();
    var f = fixture();
    var source = snapshot(f);
    for (var table : f.tables) table.clear();
    var output = m.assemble(source, media(STAMP), at());
    assertEquals(1, output.speakers().rows().size());
    assertThrows(
        UnsupportedOperationException.class, () -> output.content().audio().linkRows().clear());
    assertThrows(
        UnsupportedOperationException.class,
        () -> output.speakers().rows().get(0).fields().clear());
  }

  @Test
  void assembly018MediaCollectionRuntimeAndErrorPropagateUnchanged() throws Exception {
    var source = snapshot(fixture());
    for (Throwable expected :
        List.of(
            new IllegalStateException("synthetic collection"),
            new AssertionError("synthetic collection"))) {
      var fault =
          new AbstractList<@Nullable MediaAssetCopyRow>() {
            @Override
            public @Nullable MediaAssetCopyRow get(int index) {
              if (expected instanceof RuntimeException runtime) throw runtime;
              throw (Error) expected;
            }

            @Override
            public int size() {
              return 1;
            }
          };
      assertSame(
          expected,
          assertThrows(expected.getClass(), () -> assembler().assemble(source, fault, at())));
    }
  }

  @Test
  void assembly019TwoGameBindingsRetainAllDeclaredIds() throws Exception {
    var f = fixture();
    f.tables.get(0).add(new Object[] {1L, 2, "Other", "saved", false, null});
    f.tables.get(1).add(new Object[] {2L, 2, "p/f2", "f2", null, null, null, null});
    f.tables.get(2).add(new Object[] {3L, 2, 2L, 0, 1, "narration", null, null, "other", RAW});
    f.tables.get(3).add(new Object[] {4L, 2, "p/b", "b", "B", VOICE, null, null, null, null});
    f.tables.get(4).add(new Object[] {3L, 4L, VOICE});
    var files =
        new ScenarioFileMigrationMap(
            List.of(
                new ScenarioFileMigrationMap.FilePair(1, -3, 501),
                new ScenarioFileMigrationMap.FilePair(2, 2, 502)));
    var placement =
        new ScenarioEntryPlacementMap(
            files,
            new ScenarioEntryMigrationMap(
                List.of(
                    new ScenarioEntryMigrationMap.IdPair(-4, 601),
                    new ScenarioEntryMigrationMap.IdPair(3, 602))),
            List.of(
                new ScenarioEntryPlacementMap.Placement(1, -3, -4, 0),
                new ScenarioEntryPlacementMap.Placement(2, 2, 3, 0)));
    var speakers =
        new SpeakerMigrationMap(
            List.of(
                new SpeakerMigrationMap.SpeakerMapping(1, -2, 1001),
                new SpeakerMigrationMap.SpeakerMapping(2, 1, 1002)));
    var a = new ArrayList<>(assets().entries());
    a.add(
        new AssetMigrationManifest.Entry(
            AssetMigrationManifest.Kind.SCENARIO, "g2/p/f2", "scenario/f2.txt", 3, HASH));
    a.add(
        new AssetMigrationManifest.Entry(
            AssetMigrationManifest.Kind.AUDIO, "g2/p/b", "audio/b.ogg", 3, HASH));
    var m =
        new CurrentMigrationAssembler(
            files,
            placement,
            speakers,
            List.of(
                new AudioMigrationMap.AudioMapping(1, -5, 701),
                new AudioMigrationMap.AudioMapping(2, 4, 702)),
            List.of(
                new CurrentAudioLinkMapper.LinkOrder(-4, -5, VOICE, 7),
                new CurrentAudioLinkMapper.LinkOrder(3, 4, VOICE, 1)),
            new AssetMigrationManifest(a),
            ROOT_ONE,
            ROOT_TWO);
    var result = m.assemble(snapshot(f), media(STAMP), at());
    assertEquals(
        List.of(
            List.of("601", "701", "1", VOICE, "7", STAMP),
            List.of("602", "702", "2", VOICE, "1", STAMP)),
        result.content().audio().linkRows());
    assertEquals(
        List.of(TARGET_SPEAKER_ONE, "1002"),
        result.speakers().rows().stream().map(row -> row.fields().get(0)).toList());
  }

  @Test
  void assembly020FiniteParallelCallsOwnSeparateSnapshots() throws Exception {
    var m = assembler();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<String>>();
      for (int i = 0; i < TASKS; i++)
        futures.add(
            executor.submit(
                () ->
                    m.assemble(snapshot(fixture()), media(STAMP), at())
                        .content()
                        .audio()
                        .linkRows()
                        .get(0)
                        .get(4)));
      for (var future : futures) assertEquals("7", future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  @Test
  void assembly021EmptyDeclaredMappingsHaveIndependentManifest() throws Exception {
    var files = new ScenarioFileMigrationMap(List.of());
    var entries =
        new ScenarioEntryPlacementMap(files, new ScenarioEntryMigrationMap(List.of()), List.of());
    var configured =
        new CurrentMigrationAssembler(
            files,
            entries,
            new SpeakerMigrationMap(List.of()),
            List.of(),
            List.of(),
            new AssetMigrationManifest(List.of()),
            "g1",
            "g2");
    var result = configured.mappingManifest();
    assertArrayEquals(EMPTY_VECTOR.getBytes(StandardCharsets.US_ASCII), result.canonicalBytes());
    assertEquals(EMPTY_VECTOR_HASH, result.sha256());
  }

  @Test
  void assembly022ConfiguredFileIdsAreBoundAndFreshManifestIsDefensive() throws Exception {
    var files =
        new ScenarioFileMigrationMap(List.of(new ScenarioFileMigrationMap.FilePair(1, 9, 90)));
    var entries =
        new ScenarioEntryPlacementMap(files, new ScenarioEntryMigrationMap(List.of()), List.of());
    var configured =
        new CurrentMigrationAssembler(
            files,
            entries,
            new SpeakerMigrationMap(List.of()),
            List.of(),
            List.of(),
            new AssetMigrationManifest(
                List.of(
                    new AssetMigrationManifest.Entry(
                        AssetMigrationManifest.Kind.SCENARIO,
                        "g1/a.nsc",
                        "scenario/a.nsc",
                        3,
                        HASH))),
            "g1",
            "g2");
    var first = configured.mappingManifest();
    byte[] bytes = first.canonicalBytes();
    bytes[0] = 0;
    var second = configured.mappingManifest();
    assertArrayEquals(ONE_FILE_VECTOR.getBytes(StandardCharsets.US_ASCII), second.canonicalBytes());
    assertEquals(ONE_FILE_VECTOR_HASH, second.sha256());
    assertEquals(1, second.rowCounts().get("FILES"));
    assertEquals(0, second.rowCounts().get("ENTRIES"));
  }

  @Test
  void assembly023EmptyCopyManifestUsesSameDeclaredAssembly() throws Exception {
    var files = new ScenarioFileMigrationMap(List.of());
    var placement =
        new ScenarioEntryPlacementMap(files, new ScenarioEntryMigrationMap(List.of()), List.of());
    var configured =
        new CurrentMigrationAssembler(
            files,
            placement,
            new SpeakerMigrationMap(List.of()),
            List.of(),
            List.of(),
            new AssetMigrationManifest(List.of()),
            "g1",
            "g2");
    var f = new CurrentMigrationProjectionTest.Fixture();
    for (int index = 0; index < 5; index++) f.tables.add(new ArrayList<>());
    var result = configured.copyManifest(snapshot(f), List.of(), at());
    assertArrayEquals(
        "NKMIGCOPY1\nMAPPING\t83b87552a2f59f743b0c28ad12ed8bbb5e0f38c4a3794c68a29f35a3974284e9\nspeakers\t0\t0\te3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\nscript_files\t0\t0\te3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\nscript_entries\t0\t0\te3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\naudio_files\t0\t0\te3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\nmedia_assets\t0\t0\te3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\nentry_audio_links\t0\t0\te3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\n"
            .getBytes(StandardCharsets.US_ASCII),
        result.canonicalBytes());
    assertEquals(
        "4444698baa3c905644477124201c2c291637b7c8441ed296c30acb231b1dcd90", result.sha256());
  }

  @Test
  void assembly024NormalCopyManifestCountsAndSameMappingBinding() throws Exception {
    var result = assembler().copyManifest(snapshot(fixture()), media(STAMP), at());
    assertEquals(
        java.util.Map.of(
            "speakers",
            1L,
            "script_files",
            1L,
            "script_entries",
            1L,
            "audio_files",
            1L,
            "media_assets",
            2L,
            "entry_audio_links",
            1L),
        result.rowCounts());
    assertEquals(
        "94e90234d64532dc9af1dd9d1361dbcee36e9ec03ba12401f10a64e444a2e254", result.mappingSha256());
  }

  private static CurrentMigrationProjectionTest.Fixture fixture() {
    var f = CurrentMigrationProjectionTest.normal();
    f.tables.get(2).get(0)[9] = RAW;
    return f;
  }

  private static CurrentMigrationProjection.SourceSnapshot snapshot(
      CurrentMigrationProjectionTest.Fixture f) throws Exception {
    return new CurrentMigrationProjection()
        .read(
            f.connection(),
            f.tables.get(0).size(),
            f.tables.get(1).size(),
            f.tables.get(2).size(),
            f.tables.get(3).size(),
            f.tables.get(4).size());
  }

  private static ScenarioFileMigrationMap files() {
    return new ScenarioFileMigrationMap(List.of(new ScenarioFileMigrationMap.FilePair(1, -3, 501)));
  }

  private static ScenarioEntryPlacementMap placement() {
    return new ScenarioEntryPlacementMap(
        files(),
        new ScenarioEntryMigrationMap(List.of(new ScenarioEntryMigrationMap.IdPair(-4, 601))),
        List.of(new ScenarioEntryPlacementMap.Placement(1, -3, -4, 0)));
  }

  private static SpeakerMigrationMap speakers() {
    return new SpeakerMigrationMap(List.of(new SpeakerMigrationMap.SpeakerMapping(1, -2, 1001)));
  }

  private static List<AudioMigrationMap.@Nullable AudioMapping> audioMappings() {
    return List.of(new AudioMigrationMap.AudioMapping(1, -5, 701));
  }

  private static List<CurrentAudioLinkMapper.@Nullable LinkOrder> orders() {
    return List.of(new CurrentAudioLinkMapper.LinkOrder(-4, -5, VOICE, 7));
  }

  private static AssetMigrationManifest assets() {
    return new AssetMigrationManifest(
        List.of(
            new AssetMigrationManifest.Entry(
                AssetMigrationManifest.Kind.SCENARIO, "g1/p/f", "scenario/f.txt", 3, HASH),
            new AssetMigrationManifest.Entry(
                AssetMigrationManifest.Kind.AUDIO, "g1/p/a", "audio/a.ogg", 3, HASH),
            new AssetMigrationManifest.Entry(
                AssetMigrationManifest.Kind.VIDEO, VIDEO_SOURCE, VIDEO_TARGET, 3, HASH),
            new AssetMigrationManifest.Entry(
                AssetMigrationManifest.Kind.MUSIC, MUSIC_PATH, MUSIC_PATH, 3, HASH)));
  }

  private static CurrentMigrationAssembler assembler() {
    return new CurrentMigrationAssembler(
        files(), placement(), speakers(), audioMappings(), orders(), assets(), ROOT_ONE, ROOT_TWO);
  }

  private static ArrayList<@Nullable MediaAssetCopyRow> media(String stamp) throws Exception {
    return new ArrayList<>(
        List.of(
            new MediaAssetCopyRow(
                Arrays.asList(
                    "2",
                    "video-b",
                    "VIDEO",
                    "B",
                    "MAIN",
                    null,
                    VIDEO_TARGET,
                    VIDEO_SOURCE,
                    "b.mp4",
                    "3",
                    HASH,
                    "video/mp4",
                    null,
                    null,
                    null,
                    "2",
                    stamp)),
            new MediaAssetCopyRow(
                Arrays.asList(
                    "3",
                    MUSIC_ID,
                    "MUSIC",
                    "C",
                    "BGM",
                    null,
                    MUSIC_PATH,
                    MUSIC_PATH,
                    "c.ogg",
                    "3",
                    HASH,
                    "audio/ogg",
                    null,
                    null,
                    "N",
                    "1",
                    stamp))));
  }

  private static MigrationMasterCopyDataset normal() throws Exception {
    return assembler().assemble(snapshot(fixture()), media(STAMP), at());
  }

  private static Instant at() {
    return Instant.parse(STAMP);
  }

  private static void reject(CurrentMigrationProjectionTest.Fixture f) throws Exception {
    var source = snapshot(f);
    assertThrows(
        IllegalArgumentException.class, () -> assembler().assemble(source, media(STAMP), at()));
  }

  private static List<ByteArrayOutputStream> sinks() {
    return List.of(
        new ByteArrayOutputStream(),
        new ByteArrayOutputStream(),
        new ByteArrayOutputStream(),
        new ByteArrayOutputStream(),
        new ByteArrayOutputStream(),
        new ByteArrayOutputStream());
  }

  private static List<String> wire() {
    return List.of(
        "1001\t1\t Namé \tstored_norm\tfalse\t\\N\t2026-01-02T03:04:05Z\n",
        "501\t1\t1\tscenario/f.txt\tp/f\tf\t\\N\t\\N\t" + HASH + "\t3\t2026-01-02T03:04:05Z\n",
        "601\t1\t501\t1\t0\t1\tnarration\t\\N\t\\N\t Body \t saved raw \t2026-01-02T03:04:05Z\n",
        "701\t1\taudio/a.ogg\tp/a\ta\ta_KEPT\tmovie_audio\t\\N\t1234\t3\t"
            + HASH
            + "\t2026-01-02T03:04:05Z\n",
        "2\tvideo-b\tVIDEO\tB\tMAIN\t\\N\tvideo/b.mp4\tcurrent/b.mp4\tb.mp4\t3\t"
            + HASH
            + "\tvideo/mp4\t\\N\t\\N\t\\N\t2\t2026-01-02T03:04:05Z\n3\t"
            + MUSIC_ID
            + "\tMUSIC\tC\tBGM\t\\N\tmusic/c.ogg\tmusic/c.ogg\tc.ogg\t3\t"
            + HASH
            + "\taudio/ogg\t\\N\t\\N\tN\t1\t2026-01-02T03:04:05Z\n",
        "601\t701\t1\tvoice\t7\t2026-01-02T03:04:05Z\n");
  }
}
