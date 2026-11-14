package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-MASTER001..020; independent V002 six-column-list wire and borrowed stream faults. */
final class MigrationMasterCopyDatasetTest {
  private static final String SHA =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String OTHER_STAMP = "2026-01-02T03:04:06Z";
  private static final String DIAGNOSTIC = "migration six-table COPY dataset is invalid";
  private static final String ONE = "1";
  private static final String THREE = "3";
  private static final String SOURCE_VIDEO = "current/a.mp4";
  private static final String TARGET_VIDEO = "video/a.mp4";
  private static final String VIDEO = "VIDEO";
  private static final String SPEAKER_ID = "42";
  private static final int STREAMS = 6;
  private static final int PREFIX_BYTES = 2;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final List<String> GOLDEN =
      List.of(
          "42\t1\tAlice\talice\ttrue\t\\N\t" + STAMP + "\n",
          "700\t1\t1\tscript/file.txt\tfile.txt\tfile.txt\t\\N\tchapter\t"
              + SHA
              + "\t3\t"
              + STAMP
              + "\n",
          "900\t1\t700\t1\t0\t\\N\tdialogue\t42\t\\N\thello\traw\t" + STAMP + "\n",
          "500\t1\tvoice/a.ogg\t表示\ta.ogg\ta\tvoice\togg\t1200\t3\t" + SHA + "\t" + STAMP + "\n",
          "600\tvideo-a\tVIDEO\tA\tMAIN\t\\N\tvideo/a.mp4\tcurrent/a.mp4\ta.mp4\t3\t"
              + SHA
              + "\tvideo/mp4\t\\N\t\\N\t\\N\t1\t"
              + STAMP
              + "\n",
          "900\t500\t1\tvoice\t1\t" + STAMP + "\n");

  @Test
  void master001SixGoldenStreamsParentOrderAndBorrowedOwnership() throws Exception {
    var sinks = sinks();
    write(normal(), writer(), sinks);
    expected(sinks, GOLDEN);
    assertEquals(List.of(0, 1, 2, 3, 4, 5), sinks.getFirst().order);
    untouchedOwnership(sinks);
  }

  @Test
  void master002AllEmptyDoesNotInventRowsOrWrites() throws Exception {
    var sinks = sinks();
    write(
        new MigrationMasterCopyDataset(new SpeakerCopyBatch(List.of()), emptyContent()),
        writer(),
        sinks);
    expected(sinks, List.of("", "", "", "", "", ""));
    assertTrue(sinks.getFirst().order.isEmpty());
    untouchedOwnership(sinks);
  }

  @Test
  void master003BothConstructorNullBoundaries() throws Exception {
    var speakers = speakers(STAMP);
    var content = content(STAMP);
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> new MigrationMasterCopyDataset(null, content))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationMasterCopyDataset(speakers, null))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> new MigrationMasterCopyDataset(null, null))
            .getMessage());
  }

  @Test
  void master004UnknownSpeakerCannotReachAssembly() throws Exception {
    var speakers = speakers(STAMP);
    var content =
        new MigrationCopyDataset(
            scenario(true, "999", ONE, STAMP), List.of(), List.of(), emptyMedia());
    assertThrows(
        IllegalArgumentException.class, () -> new MigrationMasterCopyDataset(speakers, content));
  }

  @Test
  void master005SpeakerGameMustMatchEntryGame() throws Exception {
    var speakers = speakers(STAMP);
    var content =
        new MigrationCopyDataset(
            scenario(true, SPEAKER_ID, "2", STAMP), List.of(), List.of(), emptyMedia());
    assertThrows(
        IllegalArgumentException.class, () -> new MigrationMasterCopyDataset(speakers, content));
  }

  @Test
  void master006SpeakerAndEntryHaveOneTimestamp() throws Exception {
    var speakers = speakers(OTHER_STAMP);
    var content = content(STAMP);
    assertThrows(
        IllegalArgumentException.class, () -> new MigrationMasterCopyDataset(speakers, content));
  }

  @Test
  void master007NoEntryStillChecksSpeakerAgainstFile() throws Exception {
    var speakers = speakers(OTHER_STAMP);
    var content =
        new MigrationCopyDataset(
            scenario(false, null, ONE, STAMP), List.of(), List.of(), emptyMedia());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationMasterCopyDataset(speakers, content))
            .getMessage());
  }

  @Test
  void master008NoScenarioStillChecksSpeakerAgainstAudio() throws Exception {
    var speakers = speakers(OTHER_STAMP);
    var content =
        new MigrationCopyDataset(emptyScenario(), List.of(audio(STAMP)), List.of(), emptyMedia());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationMasterCopyDataset(speakers, content))
            .getMessage());
  }

  @Test
  void master009NoScenarioOrAudioStillChecksSpeakerAgainstMedia() throws Exception {
    var speakers = speakers(OTHER_STAMP);
    var content = new MigrationCopyDataset(emptyScenario(), List.of(), List.of(), media(STAMP));
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationMasterCopyDataset(speakers, content))
            .getMessage());
  }

  @Test
  void master010EmptySpeakersAllowsNarrationAndRejectsDialogue() throws Exception {
    var speakers = new SpeakerCopyBatch(List.of());
    var narration =
        new MigrationCopyDataset(
            scenario(true, null, ONE, STAMP), List.of(), List.of(), emptyMedia());
    var accepted = new MigrationMasterCopyDataset(speakers, narration);
    assertSame(narration, accepted.content());
    var dialogue = content(STAMP);
    assertThrows(
        IllegalArgumentException.class, () -> new MigrationMasterCopyDataset(speakers, dialogue));
  }

  @Test
  void master011EveryNullArgumentFailsBeforeFirstByte() throws Exception {
    var dataset = normal();
    var all = sinks();
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> write(dataset, null, all)).getMessage());
    expected(all, List.of("", "", "", "", "", ""));
    for (int position = 0; position < STREAMS; position++) {
      var sinks = sinks();
      var inputs = new ArrayList<@Nullable OutputStream>(sinks);
      inputs.set(position, null);
      assertEquals(
          DIAGNOSTIC,
          assertThrows(IllegalArgumentException.class, () -> write(dataset, writer(), inputs))
              .getMessage());
      expected(sinks, List.of("", "", "", "", "", ""));
      untouchedOwnership(sinks);
    }
  }

  @Test
  void master012EachIoFailureKeepsIdentityAndStopsLaterOutputs() throws Exception {
    for (int position = 0; position < STREAMS; position++) {
      var failure = new IOException("synthetic io");
      fault(position, 0, failure);
    }
  }

  @Test
  void master013EachRuntimeFailureKeepsIdentityAndStopsLaterOutputs() throws Exception {
    for (int position = 0; position < STREAMS; position++) {
      var failure = new IllegalStateException("synthetic runtime");
      fault(position, 0, failure);
    }
  }

  @Test
  void master014EachErrorKeepsIdentityAndStopsLaterOutputs() throws Exception {
    for (int position = 0; position < STREAMS; position++) {
      var failure = new AssertionError("synthetic error");
      fault(position, 0, failure);
    }
  }

  @Test
  void master015EveryPartialPrefixIsRetainedWithoutRetryOrClose() throws Exception {
    for (int position = 0; position < STREAMS; position++) {
      var failure = new IOException("synthetic partial io");
      fault(position, PREFIX_BYTES, failure);
    }
  }

  @Test
  void master016ImmutableComponentsRetainOnlySnapshots() throws Exception {
    var input = new ArrayList<SpeakerCopyRow>();
    input.add(
        new SpeakerCopyRow(
            Arrays.<@Nullable String>asList(
                SPEAKER_ID, ONE, "Alice", "alice", "true", null, STAMP)));
    var speakers = new SpeakerCopyBatch(input);
    var content = content(STAMP);
    var dataset = new MigrationMasterCopyDataset(speakers, content);
    input.clear();
    assertSame(speakers, dataset.speakers());
    assertSame(content, dataset.content());
    assertThrows(UnsupportedOperationException.class, () -> dataset.speakers().rows().clear());
    assertThrows(
        UnsupportedOperationException.class,
        () -> dataset.speakers().rows().getFirst().fields().clear());
    var sinks = sinks();
    write(dataset, writer(), sinks);
    expected(sinks, GOLDEN);
  }

  @Test
  void master017DiagnosticsRemainFixedAndRedacted() throws Exception {
    assertEquals("MigrationMasterCopyDataset[REDACTED]", normal().toString());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> new MigrationMasterCopyDataset(null, null))
            .getMessage());
  }

  @Test
  void master018FreshSuccessAfterFailureHasIndependentOutputs() throws Exception {
    fault(0, PREFIX_BYTES, new IOException("synthetic failed prior"));
    var sinks = sinks();
    write(normal(), writer(), sinks);
    expected(sinks, GOLDEN);
    untouchedOwnership(sinks);
  }

  @Test
  void master019GameTwoBoundaryIdsMicrosecondsAndDeclaredOrder() throws Exception {
    String stamp = "9999-12-31T23:59:59.999999Z";
    var speakers =
        new SpeakerCopyBatch(
            List.of(speaker("999999999999", "2", stamp), speaker("1", "2", stamp)));
    var content =
        new MigrationCopyDataset(
            scenario(true, "999999999999", "2", stamp), List.of(), List.of(), emptyMedia());
    var sinks = sinks();
    write(new MigrationMasterCopyDataset(speakers, content), writer(), sinks);
    assertArrayEquals(
        ("999999999999\t2\tAlice\talice-999999999999\ttrue\t\\N\t"
                + stamp
                + "\n1\t2\tAlice\talice-1\ttrue\t\\N\t"
                + stamp
                + "\n")
            .getBytes(StandardCharsets.UTF_8),
        sinks.getFirst().output.toByteArray());
    assertArrayEquals(
        ("900\t2\t700\t1\t0\t\\N\tdialogue\t999999999999\t\\N\thello\traw\t" + stamp + "\n")
            .getBytes(StandardCharsets.UTF_8),
        sinks.get(2).output.toByteArray());
    assertEquals(List.of(0, 1, 2), sinks.getFirst().order);
    for (int index = 3; index < STREAMS; index++) assertEquals(0, sinks.get(index).output.size());
  }

  @Test
  void master020FiniteReadersUseIndependentMemoryAndTerminate() throws Exception {
    var dataset = normal();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<List<String>>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(
            executor.submit(
                () -> {
                  var sinks = sinks();
                  write(dataset, writer(), sinks);
                  return sinks.stream().map(MemorySink::text).toList();
                }));
      for (var future : futures) assertEquals(GOLDEN, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static MigrationMasterCopyDataset normal() throws Exception {
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
                    SPEAKER_ID, ONE, "Alice", "alice", "true", null, stamp))));
  }

  private static SpeakerCopyRow speaker(String id, String game, String stamp) {
    return new SpeakerCopyRow(
        Arrays.<@Nullable String>asList(id, game, "Alice", "alice-" + id, "true", null, stamp));
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

  private static MediaAssetCopyBatch media(String stamp) throws Exception {
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

  private static PostgresCopyTextWriter writer() {
    return new PostgresCopyTextWriter(new PostgresCopyTextEncoder());
  }

  private static void write(
      MigrationMasterCopyDataset dataset,
      @Nullable PostgresCopyTextWriter writer,
      List<? extends @Nullable OutputStream> sinks)
      throws IOException {
    dataset.writeAll(
        writer, sinks.get(0), sinks.get(1), sinks.get(2), sinks.get(3), sinks.get(4), sinks.get(5));
  }

  private static List<MemorySink> sinks() {
    var order = new ArrayList<Integer>();
    var result = new ArrayList<MemorySink>();
    for (int index = 0; index < STREAMS; index++)
      result.add(
          new MemorySink(
              index, order, Integer.MAX_VALUE, new IOException("unused synthetic failure")));
    return result;
  }

  private static void expected(List<MemorySink> sinks, List<String> expected) {
    for (int index = 0; index < STREAMS; index++)
      assertArrayEquals(
          expected.get(index).getBytes(StandardCharsets.UTF_8),
          sinks.get(index).output.toByteArray());
  }

  private static void untouchedOwnership(List<MemorySink> sinks) {
    for (var sink : sinks) {
      assertEquals(0, sink.closes);
      assertEquals(0, sink.flushes);
    }
  }

  private static void fault(int position, int prefix, Throwable failure) throws Exception {
    var sinks = sinks();
    var order = sinks.getFirst().order;
    sinks.set(position, new MemorySink(position, order, prefix, failure));
    var dataset = normal();
    assertSame(failure, assertThrows(failure.getClass(), () -> write(dataset, writer(), sinks)));
    for (int index = 0; index < STREAMS; index++) {
      byte[] expected = GOLDEN.get(index).getBytes(StandardCharsets.UTF_8);
      assertArrayEquals(
          index < position
              ? expected
              : index == position ? Arrays.copyOf(expected, prefix) : new byte[0],
          sinks.get(index).output.toByteArray());
      assertEquals(index == position ? 1 : 0, sinks.get(index).failures);
    }
    assertEquals(java.util.stream.IntStream.rangeClosed(0, position).boxed().toList(), order);
    untouchedOwnership(sinks);
  }

  private static final class MemorySink extends OutputStream {
    private final ByteArrayOutputStream output = new ByteArrayOutputStream();
    private final int index;
    private final List<Integer> order;
    private final int failAt;
    private final Throwable failure;
    private int failures;
    private int closes;
    private int flushes;

    private MemorySink(int index, List<Integer> order, int failAt, Throwable failure) {
      this.index = index;
      this.order = order;
      this.failAt = failAt;
      this.failure = failure;
    }

    @Override
    public void write(int value) throws IOException {
      if (order.isEmpty() || order.getLast() != index) order.add(index);
      if (output.size() == failAt) {
        failures++;
        if (failure instanceof IOException io) throw io;
        if (failure instanceof RuntimeException runtime) throw runtime;
        throw (Error) failure;
      }
      output.write(value);
    }

    @Override
    public void close() {
      closes++;
    }

    @Override
    public void flush() {
      flushes++;
    }

    private String text() {
      return output.toString(StandardCharsets.UTF_8);
    }
  }
}
