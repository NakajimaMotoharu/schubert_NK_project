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
import java.security.NoSuchAlgorithmException;
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

/** PT-MIG-FIVE001..020; independent five-stream literals and memory-only failure injection. */
final class MigrationCopyDatasetTest {
  private static final String SHA =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String OTHER_STAMP = "2026-01-02T03:04:06Z";
  private static final String DIAGNOSTIC = "migration five-table COPY dataset is invalid";
  private static final String ONE = "1";
  private static final String THREE = "3";
  private static final String SOURCE_VIDEO = "current/a.mp4";
  private static final String TARGET_VIDEO = "video/a.mp4";
  private static final String VIDEO = "VIDEO";
  private static final int STREAMS = 5;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final List<String> GOLDEN =
      List.of(
          "700\t1\t1\tscript/file.txt\tfile.txt\tfile.txt\t\\N\tchapter\t"
              + SHA
              + "\t3\t"
              + STAMP
              + "\n",
          "900\t1\t700\t1\t0\t\\N\tnarration\t\\N\t\\N\thello\traw\t" + STAMP + "\n",
          "500\t1\tvoice/a.ogg\t表示\ta.ogg\ta\tvoice\togg\t1200\t3\t" + SHA + "\t" + STAMP + "\n",
          "600\tvideo-a\tVIDEO\tA\tMAIN\t\\N\tvideo/a.mp4\tcurrent/a.mp4\ta.mp4\t3\t"
              + SHA
              + "\tvideo/mp4\t\\N\t\\N\t\\N\t1\t"
              + STAMP
              + "\n",
          "900\t500\t1\tvoice\t1\t" + STAMP + "\n");

  @Test
  void five001IndependentFiveStreamsOrderAndBorrowedOwnership()
      throws IOException, NoSuchAlgorithmException {
    var sinks = sinks();
    write(normal(), writer(), sinks);
    expected(sinks, GOLDEN);
    assertEquals(List.of(0, 1, 2, 3, 4), sinks.getFirst().order);
    for (var sink : sinks) {
      assertEquals(0, sink.closes);
      assertEquals(0, sink.flushes);
    }
  }

  @Test
  void five002AllEmptyNoInventedRows() throws IOException {
    var sinks = sinks();
    write(
        new MigrationCopyDataset(emptyScenario(), List.of(), List.of(), emptyMedia()),
        writer(),
        sinks);
    expected(sinks, List.of("", "", "", "", ""));
    assertTrue(sinks.getFirst().order.isEmpty());
  }

  @Test
  void five003NullScenarioAndMedia() throws NoSuchAlgorithmException {
    var scenario = scenario(true, STAMP);
    var media = media(STAMP);
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationCopyDataset(null, List.of(), List.of(), media))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationCopyDataset(scenario, List.of(), List.of(), null))
            .getMessage());
  }

  @Test
  void five004NullAudioOrLinkCollections() throws NoSuchAlgorithmException {
    var scenario = scenario(true, STAMP);
    var media = media(STAMP);
    assertThrows(
        IllegalArgumentException.class,
        () -> new MigrationCopyDataset(scenario, null, List.of(), media));
    assertThrows(
        IllegalArgumentException.class,
        () -> new MigrationCopyDataset(scenario, List.of(), null, media));
  }

  @Test
  void five005MissingCollectionElementsRemainInvalid() throws NoSuchAlgorithmException {
    var scenario = scenario(true, STAMP);
    var media = media(STAMP);
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MigrationCopyDataset(
                scenario, Arrays.asList((AudioFileCopyRow) null), List.of(), media));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MigrationCopyDataset(
                scenario, List.of(), Arrays.asList((List<@Nullable String>) null), media));
  }

  @Test
  void five006LinkMustBelongToThisScenario() throws NoSuchAlgorithmException {
    var scenario = scenario(false, STAMP);
    var audio = List.of(audio(STAMP));
    var media = media(STAMP);
    assertThrows(
        IllegalArgumentException.class,
        () -> new MigrationCopyDataset(scenario, audio, List.of(link()), media));
  }

  @Test
  void five007UnreferencedAudioDoesNotInventLink() throws IOException {
    var dataset =
        new MigrationCopyDataset(
            scenario(true, STAMP), List.of(audio(STAMP)), List.of(), emptyMedia());
    assertEquals(1, dataset.audio().audioRows().size());
    assertTrue(dataset.audio().linkRows().isEmpty());
    var sinks = sinks();
    write(dataset, writer(), sinks);
    assertEquals(GOLDEN.get(2), sinks.get(2).text());
    assertEquals("", sinks.get(4).text());
  }

  @Test
  void five008FileAndAudioTimestampMustAgreeWithoutEntries() {
    var scenario = scenario(false, STAMP);
    var audio = List.of(audio(OTHER_STAMP));
    var media = emptyMedia();
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationCopyDataset(scenario, audio, List.of(), media))
            .getMessage());
  }

  @Test
  void five009MediaAndScenarioTimestampMustAgree() throws NoSuchAlgorithmException {
    var scenario = scenario(true, STAMP);
    var media = media(OTHER_STAMP);
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationCopyDataset(scenario, List.of(), List.of(), media))
            .getMessage());
  }

  @Test
  void five010FileAndAudioOnlyCommonStampIsValid() throws IOException {
    var dataset =
        new MigrationCopyDataset(
            scenario(false, STAMP), List.of(audio(STAMP)), List.of(), emptyMedia());
    var sinks = sinks();
    write(dataset, writer(), sinks);
    expected(sinks, List.of(GOLDEN.get(0), "", GOLDEN.get(2), "", ""));
  }

  @Test
  void five011MediaOnlyHasItsOwnSingleStamp() throws IOException, NoSuchAlgorithmException {
    var dataset = new MigrationCopyDataset(emptyScenario(), List.of(), List.of(), media(STAMP));
    var sinks = sinks();
    write(dataset, writer(), sinks);
    expected(sinks, List.of("", "", "", GOLDEN.get(3), ""));
  }

  @Test
  void five012GettersRetainImmutableValidatedValues() throws NoSuchAlgorithmException {
    var scenario = scenario(true, STAMP);
    var media = media(STAMP);
    var dataset = new MigrationCopyDataset(scenario, List.of(audio(STAMP)), List.of(link()), media);
    assertSame(scenario, dataset.scenario());
    assertSame(media, dataset.media());
    assertThrows(UnsupportedOperationException.class, () -> dataset.audio().audioRows().clear());
    assertThrows(UnsupportedOperationException.class, () -> dataset.audio().linkRows().clear());
    assertThrows(
        UnsupportedOperationException.class, () -> dataset.audio().linkRows().getFirst().clear());
  }

  @Test
  void five013EveryNullWriteArgumentFailsBeforeAnyByte() throws NoSuchAlgorithmException {
    var dataset = normal();
    var sinks = sinks();
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> write(dataset, null, sinks))
            .getMessage());
    for (int index = 0; index < STREAMS; index++) {
      var incomplete = new ArrayList<@Nullable OutputStream>(sinks);
      incomplete.set(index, null);
      assertEquals(
          DIAGNOSTIC,
          assertThrows(IllegalArgumentException.class, () -> write(dataset, writer(), incomplete))
              .getMessage());
    }
    expected(sinks, List.of("", "", "", "", ""));
  }

  @Test
  void five014EachIoFailureStopsLaterStreamsAndPreservesInstance() throws NoSuchAlgorithmException {
    var dataset = normal();
    for (int failedIndex = 0; failedIndex < STREAMS; failedIndex++) {
      var sinks = sinks();
      var failure = new IOException("synthetic five-stream IO");
      var faulty = new MemorySink(failedIndex, sinks.getFirst().order, 0, failure);
      var outputs = new ArrayList<OutputStream>(sinks);
      outputs.set(failedIndex, faulty);
      assertSame(failure, assertThrows(IOException.class, () -> write(dataset, writer(), outputs)));
      for (int index = 0; index < STREAMS; index++)
        assertEquals(index < failedIndex ? GOLDEN.get(index) : "", sinks.get(index).text());
      assertEquals(0, faulty.closes);
      assertEquals(0, faulty.flushes);
    }
  }

  @Test
  void five015RuntimeAndErrorAreNotWrapped() throws NoSuchAlgorithmException {
    var dataset = normal();
    var runtime = new IllegalStateException("synthetic runtime");
    assertBorrowedUncheckedFailure(
        dataset,
        runtime,
        () -> {
          throw runtime;
        });
    var error = new AssertionError("synthetic error");
    assertBorrowedUncheckedFailure(
        dataset,
        error,
        () -> {
          throw error;
        });
  }

  private static void assertBorrowedUncheckedFailure(
      MigrationCopyDataset dataset, Throwable failure, Runnable throwOnWrite) {
    var sinks = sinks();
    var outputs = new ArrayList<OutputStream>(sinks);
    var failing =
        new OutputStream() {
          private int closes;
          private int flushes;

          @Override
          public void write(int value) {
            throwOnWrite.run();
          }

          @Override
          public void close() {
            closes++;
          }

          @Override
          public void flush() {
            flushes++;
          }
        };
    try (failing) {
      outputs.set(0, failing);
      assertSame(
          failure, assertThrows(failure.getClass(), () -> write(dataset, writer(), outputs)));
      assertEquals(0, failing.closes);
      assertEquals(0, failing.flushes);
      expected(sinks, List.of("", "", "", "", ""));
    }
    assertEquals(1, failing.closes);
  }

  @Test
  void five016PartialBytesRemainAndNoAutomaticReplay() throws NoSuchAlgorithmException {
    var dataset = normal();
    var sinks = sinks();
    var failure = new IOException("synthetic partial");
    var faulty = new MemorySink(0, sinks.getFirst().order, 2, failure);
    var outputs = new ArrayList<OutputStream>(sinks);
    outputs.set(0, faulty);
    assertSame(failure, assertThrows(IOException.class, () -> write(dataset, writer(), outputs)));
    assertEquals("70", faulty.text());
    assertEquals(1, faulty.failures);
    expected(sinks, List.of("", "", "", "", ""));
  }

  @Test
  void five017CallerCollectionMutationsDoNotChangeSnapshot()
      throws IOException, NoSuchAlgorithmException {
    var audio = new ArrayList<@Nullable AudioFileCopyRow>(List.of(audio(STAMP)));
    var links = new ArrayList<@Nullable List<@Nullable String>>();
    var row = new ArrayList<@Nullable String>(link());
    links.add(row);
    var dataset = new MigrationCopyDataset(scenario(true, STAMP), audio, links, media(STAMP));
    row.clear();
    audio.clear();
    links.clear();
    var sinks = sinks();
    write(dataset, writer(), sinks);
    expected(sinks, GOLDEN);
  }

  @Test
  void five018ImmutableValuesCanWriteToSeparateIndependentSinks()
      throws IOException, NoSuchAlgorithmException {
    var dataset = normal();
    for (int attempt = 0; attempt < 2; attempt++) {
      var sinks = sinks();
      write(dataset, writer(), sinks);
      expected(sinks, GOLDEN);
    }
  }

  @Test
  void five019FixedRedactionAndSuccessAfterRejection() throws NoSuchAlgorithmException {
    assertThrows(
        IllegalArgumentException.class, () -> new MigrationCopyDataset(null, null, null, null));
    assertEquals("MigrationCopyDataset[REDACTED]", normal().toString());
  }

  @Test
  void five020FiniteParallelReadersHaveIndependentMemorySinks()
      throws NoSuchAlgorithmException, InterruptedException, ExecutionException, TimeoutException {
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

  private static MigrationCopyDataset normal() throws NoSuchAlgorithmException {
    return new MigrationCopyDataset(
        scenario(true, STAMP), List.of(audio(STAMP)), List.of(link()), media(STAMP));
  }

  private static ScenarioCopyDataset scenario(boolean withEntry, String stamp) {
    var files =
        new ScenarioFileMigrationMap(List.of(new ScenarioFileMigrationMap.FilePair(1, 10, 700)));
    var entries =
        new ScenarioEntryMigrationMap(
            withEntry ? List.of(new ScenarioEntryMigrationMap.IdPair(20, 900)) : List.of());
    var placement =
        new ScenarioEntryPlacementMap(
            files,
            entries,
            withEntry ? List.of(new ScenarioEntryPlacementMap.Placement(1, 10, 20, 0)) : List.of());
    var fileRows =
        new ScenarioFileCopyBatch(
            files,
            List.of(
                Arrays.<@Nullable String>asList(
                    "700",
                    ONE,
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
                        ONE,
                        "700",
                        ONE,
                        "0",
                        null,
                        "narration",
                        null,
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

  private static List<@Nullable String> link() {
    return Arrays.<@Nullable String>asList("900", "500", ONE, "voice", ONE, STAMP);
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

  private static PostgresCopyTextWriter writer() {
    return new PostgresCopyTextWriter(new PostgresCopyTextEncoder());
  }

  private static void write(
      MigrationCopyDataset dataset,
      @Nullable PostgresCopyTextWriter writer,
      List<? extends @Nullable OutputStream> sinks)
      throws IOException {
    dataset.writeAll(writer, sinks.get(0), sinks.get(1), sinks.get(2), sinks.get(3), sinks.get(4));
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

  private static final class MemorySink extends OutputStream {
    private final ByteArrayOutputStream output = new ByteArrayOutputStream();
    private final int index;
    private final List<Integer> order;
    private final int failAt;
    private final IOException failure;
    private int failures;
    private int closes;
    private int flushes;

    private MemorySink(int index, List<Integer> order, int failAt, IOException failure) {
      this.index = index;
      this.order = order;
      this.failAt = failAt;
      this.failure = failure;
    }

    @Override
    public void write(int value) throws IOException {
      if (output.size() == failAt) {
        failures++;
        throw failure;
      }
      if (order.isEmpty() || order.getLast() != index) order.add(index);
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
