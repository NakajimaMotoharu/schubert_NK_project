package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
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
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/**
 * PT-MIG-AUDIODATA001..020; independent two-stream literals, composite keys and owned finite
 * workers.
 */
final class AudioCopyDatasetTest {
  private static final String SHA =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String OTHER_STAMP = "2026-01-02T03:04:06Z";
  private static final String DIAGNOSTIC = "migration audio COPY dataset is invalid";
  private static final String AUDIO_GOLDEN =
      "500\t1\tvoice/a.ogg\t表示\ta.ogg\ta\tvoice\togg\t1200\t3\t" + SHA + "\t" + STAMP + "\n";
  private static final String LINK_GOLDEN = "900\t500\t1\tvoice\t1\t" + STAMP + "\n";
  private static final String VOICE_PATH = "voice/a.ogg";
  private static final String VOICE = "voice";
  private static final String ONE = "1";
  private static final String TWO = "2";
  private static final String ENTRY_ID = "900";
  private static final String AUDIO_ID = "500";
  private static final String ZERO = "0";
  private static final String SECOND_PATH = "b.ogg";
  private static final int TASKS = 64;
  private static final int WORKERS = 8;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final int LINK_LIMIT = 999;
  private static final long MAX_N12 = 999999999999L;

  @Test
  void independentAudioAndLinkGoldenHaveExactSeparateStreams() throws IOException {
    var dataset = normal();
    var audio = new MemorySink();
    var links = new MemorySink();
    dataset.writeAudio(writer(), audio);
    dataset.writeLinks(writer(), links);
    assertArrayEquals(AUDIO_GOLDEN.getBytes(StandardCharsets.UTF_8), audio.toByteArray());
    assertArrayEquals(LINK_GOLDEN.getBytes(StandardCharsets.UTF_8), links.toByteArray());
    assertEquals(1, dataset.audioRows().size());
    assertEquals(1, dataset.linkRows().size());
  }

  @Test
  void emptyAudioOnlyAndEntryOnlyDeclareNoImaginaryLinks() throws IOException {
    for (var dataset :
        List.of(
            new AudioCopyDataset(emptyEntries(), List.of(), List.of()),
            new AudioCopyDataset(
                emptyEntries(), List.of(audio(500, 1, VOICE_PATH, STAMP)), List.of()),
            new AudioCopyDataset(entries(1, STAMP), List.of(), List.of()))) {
      var sink = new MemorySink();
      dataset.writeLinks(writer(), sink);
      assertArrayEquals(new byte[0], sink.toByteArray());
      assertTrue(dataset.linkRows().isEmpty());
    }
    var empty = new AudioCopyDataset(emptyEntries(), List.of(), List.of());
    var sink = new MemorySink();
    empty.writeAudio(writer(), sink);
    assertArrayEquals(new byte[0], sink.toByteArray());
  }

  @Test
  void audioPrimaryIdsAreGloballyUniqueAcrossGamesAndPaths() {
    reject(
        entries(1, STAMP),
        List.of(audio(500, 1, VOICE_PATH, STAMP), audio(500, 1, SECOND_PATH, STAMP)),
        List.of());
    reject(
        entries(1, STAMP),
        List.of(audio(500, 1, VOICE_PATH, STAMP), audio(500, 2, SECOND_PATH, STAMP)),
        List.of());
  }

  @Test
  void storagePathUniquenessIncludesGameRatherThanChangingPaths() {
    reject(
        entries(1, STAMP),
        List.of(audio(500, 1, VOICE_PATH, STAMP), audio(501, 1, VOICE_PATH, STAMP)),
        List.of());
    var dataset =
        new AudioCopyDataset(
            entries(1, STAMP),
            List.of(audio(500, 1, VOICE_PATH, STAMP), audio(501, 2, VOICE_PATH, STAMP)),
            List.of());
    assertEquals(2, dataset.audioRows().size());
    assertEquals(TWO, dataset.audioRows().get(1).fields().get(1));
  }

  @Test
  void bothUnknownReferenceDirectionsAreRejected() {
    var unknownEntry = link(500, VOICE, ONE, 1, STAMP);
    unknownEntry.set(0, "901");
    reject(entries(1, STAMP), List.of(audio(500, 1, VOICE_PATH, STAMP)), List.of(unknownEntry));
    reject(
        entries(1, STAMP),
        List.of(audio(500, 1, VOICE_PATH, STAMP)),
        List.of(link(501, VOICE, ONE, 1, STAMP)));
    reject(emptyEntries(), List.of(), List.of(link(500, VOICE, ONE, 1, STAMP)));
  }

  @Test
  void entryCompositeForeignKeyIncludesTheDeclaredGame() {
    reject(
        entries(2, STAMP),
        List.of(audio(500, 1, VOICE_PATH, STAMP)),
        List.of(link(500, VOICE, ONE, 1, STAMP)));
    var dataset =
        new AudioCopyDataset(
            entries(2, STAMP),
            List.of(audio(500, 2, VOICE_PATH, STAMP)),
            List.of(link(500, VOICE, ONE, 2, STAMP)));
    assertEquals(TWO, dataset.linkRows().get(0).get(2));
  }

  @Test
  void audioCompositeForeignKeyIncludesTheDeclaredGame() {
    reject(
        entries(1, STAMP),
        List.of(audio(500, 2, VOICE_PATH, STAMP)),
        List.of(link(500, VOICE, ONE, 1, STAMP)));
  }

  @Test
  void linkColumnGrammarIsIndependentOfAnyAvailableReference() {
    for (int index : List.of(0, 1)) {
      for (String value : List.of(ZERO, "-1", "01", "+1", "1000000000000", ""))
        rejectLinkField(index, value);
    }
    for (String value : List.of(ZERO, "3", "01", "")) rejectLinkField(2, value);
    for (String value : List.of("VOICE", "unknown", "")) rejectLinkField(3, value);
    for (String value : List.of(ZERO, "1000", "01", "-1", "")) rejectLinkField(4, value);
    var shortRow = link(500, VOICE, ONE, 1, STAMP);
    shortRow.removeLast();
    reject(entries(1, STAMP), List.of(audio(500, 1, VOICE_PATH, STAMP)), List.of(shortRow));
    var longRow = link(500, VOICE, ONE, 1, STAMP);
    longRow.add("extra");
    reject(entries(1, STAMP), List.of(audio(500, 1, VOICE_PATH, STAMP)), List.of(longRow));
    for (int index = 0; index < 6; index++) rejectLinkField(index, null);
  }

  @Test
  void primaryKeyIncludesTypeButRejectsSameEntryAudioTypeTwice() {
    var first = link(500, VOICE, ONE, 1, STAMP);
    reject(
        entries(1, STAMP),
        List.of(audio(500, 1, VOICE_PATH, STAMP)),
        List.of(first, link(500, VOICE, TWO, 1, STAMP)));
    var links = new ArrayList<List<@Nullable String>>();
    for (String type : List.of(VOICE, "se", "bgm", "other"))
      links.add(link(500, type, ONE, 1, STAMP));
    var dataset =
        new AudioCopyDataset(entries(1, STAMP), List.of(audio(500, 1, VOICE_PATH, STAMP)), links);
    assertEquals(4, dataset.linkRows().size());
  }

  @Test
  void uniqueDisplayOrderIncludesEntryAndType() {
    reject(
        entries(1, STAMP),
        List.of(audio(500, 1, VOICE_PATH, STAMP), audio(501, 1, SECOND_PATH, STAMP)),
        List.of(link(500, VOICE, ONE, 1, STAMP), link(501, VOICE, ONE, 1, STAMP)));
  }

  @Test
  void allThreeSourcesHaveOneCommonTransactionTimestamp() {
    reject(entries(1, STAMP), List.of(audio(500, 1, VOICE_PATH, OTHER_STAMP)), List.of());
    reject(entries(1, OTHER_STAMP), List.of(audio(500, 1, VOICE_PATH, STAMP)), List.of());
    reject(
        entries(1, STAMP),
        List.of(audio(500, 1, VOICE_PATH, STAMP)),
        List.of(link(500, VOICE, ONE, 1, OTHER_STAMP)));
    reject(
        emptyEntries(),
        List.of(audio(500, 1, VOICE_PATH, STAMP), audio(501, 1, SECOND_PATH, OTHER_STAMP)),
        List.of());
  }

  @Test
  void linkTimestampsHaveIndependentCanonicalUtcMicrosecondBoundaries() {
    for (String value :
        List.of(
            "0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z", "2026-01-02T03:04:05.000001Z")) {
      var dataset =
          new AudioCopyDataset(
              entries(1, value),
              List.of(audio(500, 1, VOICE_PATH, value)),
              List.of(link(500, VOICE, ONE, 1, value)));
      assertEquals(value, dataset.linkRows().get(0).get(5));
    }
    for (String value :
        List.of(
            "0000-01-01T00:00:00Z",
            "+10000-01-01T00:00:00Z",
            "2026-01-02T03:04:05.000000001Z",
            "2026-01-02T03:04:05.000Z",
            "2026-01-02T03:04:05+00:00",
            "invalid")) rejectLinkField(5, value);
  }

  @Test
  void nullableInputsAndElementsFailExplicitlyWithoutBorrowingAnything() {
    reject(null, List.of(), List.of());
    reject(emptyEntries(), null, List.of());
    reject(emptyEntries(), List.of(), null);
    var nullAudio = new ArrayList<@Nullable AudioFileCopyRow>();
    nullAudio.add(null);
    reject(emptyEntries(), nullAudio, List.of());
    var nullLinks = new ArrayList<@Nullable List<@Nullable String>>();
    nullLinks.add(null);
    reject(emptyEntries(), List.of(), nullLinks);
  }

  @Test
  void inputAndReturnedCollectionsHaveDeepIndependentOwnership() {
    var audioInput = new ArrayList<AudioFileCopyRow>();
    audioInput.add(audio(500, 1, VOICE_PATH, STAMP));
    var row = link(500, VOICE, ONE, 1, STAMP);
    var linkInput = new ArrayList<List<@Nullable String>>();
    linkInput.add(row);
    var dataset = new AudioCopyDataset(entries(1, STAMP), audioInput, linkInput);
    audioInput.clear();
    linkInput.clear();
    row.clear();
    assertEquals(AUDIO_ID, dataset.audioRows().get(0).fields().get(0));
    assertEquals(List.of(ENTRY_ID, AUDIO_ID, ONE, VOICE, ONE, STAMP), dataset.linkRows().get(0));
    assertThrows(UnsupportedOperationException.class, () -> dataset.audioRows().clear());
    assertThrows(UnsupportedOperationException.class, () -> dataset.linkRows().clear());
    assertThrows(UnsupportedOperationException.class, () -> dataset.linkRows().get(0).clear());
  }

  @Test
  void bothOutputBoundariesRejectNullWriterOrSinkAndNeverCloseOrFlush() throws IOException {
    var dataset = normal();
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> dataset.writeAudio(null, new MemorySink()))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> dataset.writeLinks(null, new MemorySink()))
            .getMessage());
    assertThrows(IllegalArgumentException.class, () -> dataset.writeAudio(writer(), null));
    assertThrows(IllegalArgumentException.class, () -> dataset.writeLinks(writer(), null));
    var sink = new MemorySink();
    dataset.writeAudio(writer(), sink);
    dataset.writeLinks(writer(), sink);
    assertFalse(sink.closed);
    assertFalse(sink.flushed);
  }

  @Test
  void bothOriginalIoFailuresAreRetainedWithoutClosingOrMutatingDataset() throws IOException {
    var dataset = normal();
    var original = new IOException("synthetic IO");
    var sink = new FailingSink(original);
    try (sink) {
      assertSame(
          original, assertThrows(IOException.class, () -> dataset.writeAudio(writer(), sink)));
      assertSame(
          original, assertThrows(IOException.class, () -> dataset.writeLinks(writer(), sink)));
      assertEquals(0, sink.closes);
      assertFalse(sink.flushed);
    }
    assertEquals(1, sink.closes);
    var retry = new MemorySink();
    dataset.writeLinks(writer(), retry);
    assertArrayEquals(LINK_GOLDEN.getBytes(StandardCharsets.UTF_8), retry.toByteArray());
  }

  @Test
  void uniqueOrderDomainHasExactly999PossibleLinksPerEntryType() {
    var audioRows = new ArrayList<AudioFileCopyRow>();
    var links = new ArrayList<List<@Nullable String>>();
    for (int index = 1; index <= LINK_LIMIT; index++) {
      audioRows.add(audio(index, 1, "a/" + index, STAMP));
      links.add(link(index, VOICE, Integer.toString(index), 1, STAMP));
    }
    var dataset = new AudioCopyDataset(entries(1, STAMP), audioRows, links);
    assertEquals(LINK_LIMIT, dataset.linkRows().size());
    assertEquals("999", dataset.linkRows().get(LINK_LIMIT - 1).get(4));
    audioRows.add(audio(1000, 1, "a/1000", STAMP));
    links.add(link(1000, VOICE, "1000", 1, STAMP));
    reject(entries(1, STAMP), audioRows, links);
    links.set(LINK_LIMIT, link(1000, VOICE, "999", 1, STAMP));
    reject(entries(1, STAMP), audioRows, links);
  }

  @Test
  void declarationOrderAndPositiveTargetExtremesAreNotRenumbered() {
    var dataset =
        new AudioCopyDataset(
            entries(1, STAMP),
            List.of(audio(501, 1, SECOND_PATH, STAMP), audio(500, 1, VOICE_PATH, STAMP)),
            List.of(link(501, VOICE, TWO, 1, STAMP), link(500, VOICE, ONE, 1, STAMP)));
    assertEquals("501", dataset.audioRows().get(0).fields().get(0));
    assertEquals(TWO, dataset.linkRows().get(0).get(4));
    for (long id : List.of(1L, MAX_N12)) {
      var row = link(id, VOICE, ONE, 1, STAMP);
      row.set(0, Long.toString(id));
      var boundary =
          new AudioCopyDataset(
              entryRows(1, STAMP, id), List.of(audio(id, 1, VOICE_PATH, STAMP)), List.of(row));
      assertEquals(Long.toString(id), boundary.linkRows().get(0).get(0));
      assertEquals(Long.toString(id), boundary.linkRows().get(0).get(1));
    }
  }

  @Test
  void finiteWorkersObserveIndependentGoldenStreamsFromTheImmutableDataset()
      throws InterruptedException, ExecutionException, TimeoutException {
    var dataset = normal();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var results = new ArrayList<Future<List<byte[]>>>();
      for (int index = 0; index < TASKS; index++)
        results.add(
            executor.submit(
                () -> {
                  var audio = new MemorySink();
                  var links = new MemorySink();
                  dataset.writeAudio(writer(), audio);
                  dataset.writeLinks(writer(), links);
                  return List.of(audio.toByteArray(), links.toByteArray());
                }));
      for (var result : results) {
        var pair = result.get(WAIT_SECONDS, TimeUnit.SECONDS);
        assertArrayEquals(AUDIO_GOLDEN.getBytes(StandardCharsets.UTF_8), pair.get(0));
        assertArrayEquals(LINK_GOLDEN.getBytes(StandardCharsets.UTF_8), pair.get(1));
      }
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  @Test
  void fixedRedactionAndIndependentSuccessDoNotRetainRejectedValues() throws IOException {
    rejectLinkField(3, "private invalid type");
    var dataset = normal();
    assertEquals("AudioCopyDataset[REDACTED]", dataset.toString());
    var sink = new MemorySink();
    dataset.writeLinks(writer(), sink);
    assertArrayEquals(LINK_GOLDEN.getBytes(StandardCharsets.UTF_8), sink.toByteArray());
  }

  private static AudioCopyDataset normal() {
    return new AudioCopyDataset(
        entries(1, STAMP),
        List.of(audio(500, 1, VOICE_PATH, STAMP)),
        List.of(link(500, VOICE, ONE, 1, STAMP)));
  }

  private static AudioFileCopyRow audio(long id, int game, String path, String stamp) {
    return new AudioFileCopyRow(
        new ArrayList<>(
            Arrays.asList(
                Long.toString(id),
                Integer.toString(game),
                path,
                "表示",
                "a.ogg",
                "a",
                VOICE,
                "ogg",
                "1200",
                "3",
                SHA,
                stamp)));
  }

  private static ArrayList<@Nullable String> link(
      long audioId, String type, String order, int game, String stamp) {
    return new ArrayList<>(
        Arrays.asList(
            ENTRY_ID, Long.toString(audioId), Integer.toString(game), type, order, stamp));
  }

  private static ScenarioEntryCopyBatch entries(int game, String stamp) {
    return entryRows(game, stamp, 900);
  }

  private static ScenarioEntryCopyBatch entryRows(int game, String stamp, long target) {
    var files =
        new ScenarioFileMigrationMap(List.of(new ScenarioFileMigrationMap.FilePair(game, 10, 700)));
    var mapping =
        new ScenarioEntryMigrationMap(List.of(new ScenarioEntryMigrationMap.IdPair(20, target)));
    var placement =
        new ScenarioEntryPlacementMap(
            files, mapping, List.of(new ScenarioEntryPlacementMap.Placement(game, 10, 20, 0)));
    var row =
        new ScenarioEntryCopyRow(
            new ArrayList<>(
                Arrays.asList(
                    Long.toString(target),
                    Integer.toString(game),
                    "700",
                    ONE,
                    ZERO,
                    null,
                    "narration",
                    null,
                    null,
                    "hello",
                    "raw",
                    stamp)));
    return new ScenarioEntryCopyBatch(placement, List.of(row));
  }

  private static ScenarioEntryCopyBatch emptyEntries() {
    var files = new ScenarioFileMigrationMap(List.of());
    var mapping = new ScenarioEntryMigrationMap(List.of());
    return new ScenarioEntryCopyBatch(
        new ScenarioEntryPlacementMap(files, mapping, List.of()), List.of());
  }

  private static void rejectLinkField(int index, @Nullable String value) {
    var row = link(500, VOICE, ONE, 1, STAMP);
    row.set(index, value);
    reject(entries(1, STAMP), List.of(audio(500, 1, VOICE_PATH, STAMP)), List.of(row));
  }

  private static void reject(
      @Nullable ScenarioEntryCopyBatch entries,
      @Nullable List<? extends @Nullable AudioFileCopyRow> audio,
      @Nullable List<? extends @Nullable List<@Nullable String>> links) {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> new AudioCopyDataset(entries, audio, links))
            .getMessage());
  }

  private static PostgresCopyTextWriter writer() {
    return new PostgresCopyTextWriter(new PostgresCopyTextEncoder());
  }

  private static final class MemorySink extends ByteArrayOutputStream {
    private boolean closed;
    private boolean flushed;

    @Override
    public void close() {
      closed = true;
    }

    @Override
    public void flush() {
      flushed = true;
    }
  }

  private static final class FailingSink extends OutputStream {
    private final IOException failure;
    private int closes;
    private boolean flushed;

    private FailingSink(IOException failure) {
      this.failure = failure;
    }

    @Override
    public void write(int value) throws IOException {
      throw failure;
    }

    @Override
    public void close() {
      closes++;
    }

    @Override
    public void flush() {
      flushed = true;
    }
  }
}
