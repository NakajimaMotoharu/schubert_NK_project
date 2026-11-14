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

/** PT-MIG-DATASET001..012; independent two-stream literals and composite-FK constraints. */
final class ScenarioCopyDatasetTest {
  private static final String SHA =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String DIAGNOSTIC = "migration scenario COPY dataset is invalid";
  private static final String FILE_GOLDEN =
      "500\t1\t1\tfile.ks\t表示\tfile.ks\t\\N\t\\N\t" + SHA + "\t3\t" + STAMP + "\n";
  private static final String ENTRY_GOLDEN =
      "900\t1\t500\t1\t0\t\\N\tnarration\t\\N\t\\N\thello\traw\t" + STAMP + "\n";

  @Test
  void joinsTwoIndependentLiteralCopyStreamsWithoutHeadersOrTerminators() {
    var dataset = normal();
    assertArrayEquals(
        FILE_GOLDEN.getBytes(StandardCharsets.UTF_8), dataset.fileCopyBytes(encoder()));
    assertArrayEquals(
        ENTRY_GOLDEN.getBytes(StandardCharsets.UTF_8), dataset.entryCopyBytes(encoder()));
  }

  @Test
  void bothEmptyBatchesAreOnlyAnEmptyDeclaredValue() {
    var files = new ScenarioFileCopyBatch(new ScenarioFileMigrationMap(List.of()), List.of());
    var dataset = new ScenarioCopyDataset(files, emptyEntries());
    assertArrayEquals(new byte[0], dataset.fileCopyBytes(encoder()));
    assertArrayEquals(new byte[0], dataset.entryCopyBytes(encoder()));
  }

  @Test
  void fileWithoutEntriesIsAllowedWithoutInventingAnEntry() {
    var dataset = new ScenarioCopyDataset(files(1, 500, STAMP), emptyEntries());
    assertArrayEquals(
        FILE_GOLDEN.getBytes(StandardCharsets.UTF_8), dataset.fileCopyBytes(encoder()));
    assertArrayEquals(new byte[0], dataset.entryCopyBytes(encoder()));
  }

  @Test
  void entryOnlyAndUnknownTargetFileAreRejected() {
    reject(
        new ScenarioFileCopyBatch(new ScenarioFileMigrationMap(List.of()), List.of()),
        entries(1, 500, STAMP));
    reject(files(1, 500, STAMP), entries(1, 501, STAMP));
  }

  @Test
  void matchingFileIdCannotHideDifferentGameMapping() {
    reject(files(1, 500, STAMP), entries(2, 500, STAMP));
    reject(files(2, 500, STAMP), entries(1, 500, STAMP));
    var dataset = new ScenarioCopyDataset(files(2, 500, STAMP), entries(2, 500, STAMP));
    assertEquals("2", dataset.entries().rows().get(0).fields().get(1));
  }

  @Test
  void separatelyValidBatchesMustHaveTheSameTransactionTimestamp() {
    String other = "2026-01-02T03:04:06Z";
    reject(files(1, 500, STAMP), entries(1, 500, other));
    reject(files(1, 500, other), entries(1, 500, STAMP));
    String microsecond = "2026-01-02T03:04:05.000001Z";
    var dataset = new ScenarioCopyDataset(files(1, 500, microsecond), entries(1, 500, microsecond));
    assertEquals(microsecond, dataset.files().rows().get(0).get(10));
    assertEquals(microsecond, dataset.entries().rows().get(0).fields().get(11));
  }

  @Test
  void nullBatchBoundariesFailWithFixedNonSecretDiagnostic() {
    reject(null, entries(1, 500, STAMP));
    reject(files(1, 500, STAMP), null);
    reject(null, null);
  }

  @Test
  void bothOutputBoundariesRejectNullEncoder() {
    var dataset = normal();
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> dataset.fileCopyBytes(null))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> dataset.entryCopyBytes(null))
            .getMessage());
  }

  @Test
  void datasetRetainsOnlyImmutableBatchValuesIndependentOfMutableInput() {
    var original = fileFields(1, 500, STAMP);
    var input = new ArrayList<List<@Nullable String>>();
    input.add(original);
    var files = new ScenarioFileCopyBatch(fileMap(1, 500), input);
    var entries = entries(1, 500, STAMP);
    var dataset = new ScenarioCopyDataset(files, entries);
    input.clear();
    original.clear();
    assertSame(files, dataset.files());
    assertSame(entries, dataset.entries());
    assertThrows(UnsupportedOperationException.class, () -> dataset.files().rows().clear());
    assertThrows(UnsupportedOperationException.class, () -> dataset.entries().rows().clear());
    assertArrayEquals(
        FILE_GOLDEN.getBytes(StandardCharsets.UTF_8), dataset.fileCopyBytes(encoder()));
    assertArrayEquals(
        ENTRY_GOLDEN.getBytes(StandardCharsets.UTF_8), dataset.entryCopyBytes(encoder()));
  }

  @Test
  void eachByteResultHasSeparateOwnershipAndIndependentCallOrder() {
    var dataset = normal();
    byte[] entries = dataset.entryCopyBytes(encoder());
    byte[] files = dataset.fileCopyBytes(encoder());
    Arrays.fill(entries, (byte) 0);
    Arrays.fill(files, (byte) 0);
    assertArrayEquals(
        FILE_GOLDEN.getBytes(StandardCharsets.UTF_8), dataset.fileCopyBytes(encoder()));
    assertArrayEquals(
        ENTRY_GOLDEN.getBytes(StandardCharsets.UTF_8), dataset.entryCopyBytes(encoder()));
  }

  @Test
  void redactionAndRejectedDatasetNeverPolluteIndependentValidCopies() {
    reject(files(1, 500, STAMP), entries(2, 500, STAMP));
    var dataset = normal();
    assertEquals("ScenarioCopyDataset[REDACTED]", dataset.toString());
    assertArrayEquals(
        FILE_GOLDEN.getBytes(StandardCharsets.UTF_8), dataset.fileCopyBytes(encoder()));
    assertArrayEquals(
        ENTRY_GOLDEN.getBytes(StandardCharsets.UTF_8), dataset.entryCopyBytes(encoder()));
  }

  @Test
  void finiteOwnedConcurrentCopiesKeepBothIndependentGoldenStreams() throws Exception {
    var dataset = normal();
    var executor = Executors.newFixedThreadPool(8);
    try {
      var futures = new ArrayList<Future<List<byte[]>>>();
      for (int index = 0; index < 64; index++)
        futures.add(
            executor.submit(
                () ->
                    List.of(dataset.fileCopyBytes(encoder()), dataset.entryCopyBytes(encoder()))));
      for (var future : futures) {
        var result = future.get(5, TimeUnit.SECONDS);
        assertArrayEquals(FILE_GOLDEN.getBytes(StandardCharsets.UTF_8), result.get(0));
        assertArrayEquals(ENTRY_GOLDEN.getBytes(StandardCharsets.UTF_8), result.get(1));
      }
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  /** SSC351 / PT-MIG-DATASET013. */
  @Test
  void streamingBothPathsRetainsIndependentFullGoldenBytes() throws Exception {
    var dataset = normal();
    var writer = new PostgresCopyTextWriter(encoder());
    var files = new ByteArrayOutputStream();
    var entries = new ByteArrayOutputStream();
    dataset.writeFiles(writer, files);
    dataset.writeEntries(writer, entries);
    assertArrayEquals(FILE_GOLDEN.getBytes(StandardCharsets.UTF_8), files.toByteArray());
    assertArrayEquals(ENTRY_GOLDEN.getBytes(StandardCharsets.UTF_8), entries.toByteArray());
  }

  /** SSC351 / PT-MIG-DATASET014. */
  @Test
  void streamingNullWriterAndSinkContractsStayFixed() {
    var dataset = normal();
    var writer = new PostgresCopyTextWriter(encoder());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> dataset.writeFiles(null, new ByteArrayOutputStream()))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> dataset.writeEntries(null, new ByteArrayOutputStream()))
            .getMessage());
    assertEquals(
        "migration COPY stream input is invalid",
        assertThrows(IllegalArgumentException.class, () -> dataset.writeFiles(writer, null))
            .getMessage());
    assertEquals(
        "migration COPY stream input is invalid",
        assertThrows(IllegalArgumentException.class, () -> dataset.writeEntries(writer, null))
            .getMessage());
  }

  /** SSC351 / PT-MIG-DATASET015. */
  @Test
  void streamingBothPathsPropagateOriginalSinkFailureWithoutChangingDataset() {
    var dataset = normal();
    var writer = new PostgresCopyTextWriter(encoder());
    var failure = new IOException("synthetic dataset sink failure");
    var sink =
        new OutputStream() {
          @Override
          public void write(int value) throws IOException {
            throw failure;
          }
        };
    assertSame(failure, assertThrows(IOException.class, () -> dataset.writeFiles(writer, sink)));
    assertSame(failure, assertThrows(IOException.class, () -> dataset.writeEntries(writer, sink)));
    assertArrayEquals(
        FILE_GOLDEN.getBytes(StandardCharsets.UTF_8), dataset.fileCopyBytes(encoder()));
    assertArrayEquals(
        ENTRY_GOLDEN.getBytes(StandardCharsets.UTF_8), dataset.entryCopyBytes(encoder()));
  }

  private static void reject(
      @Nullable ScenarioFileCopyBatch files, @Nullable ScenarioEntryCopyBatch entries) {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> new ScenarioCopyDataset(files, entries))
            .getMessage());
  }

  private static ScenarioCopyDataset normal() {
    return new ScenarioCopyDataset(files(1, 500, STAMP), entries(1, 500, STAMP));
  }

  private static ScenarioFileMigrationMap fileMap(int game, long target) {
    return new ScenarioFileMigrationMap(
        List.of(new ScenarioFileMigrationMap.FilePair(game, 10, target)));
  }

  private static List<@Nullable String> fileFields(int game, long target, String stamp) {
    return new ArrayList<>(
        Arrays.asList(
            Long.toString(target),
            Integer.toString(game),
            "1",
            "file.ks",
            "表示",
            "file.ks",
            null,
            null,
            SHA,
            "3",
            stamp));
  }

  private static ScenarioFileCopyBatch files(int game, long target, String stamp) {
    return new ScenarioFileCopyBatch(
        fileMap(game, target), List.of(fileFields(game, target, stamp)));
  }

  private static ScenarioEntryCopyBatch entries(int game, long targetFile, String stamp) {
    var mapping =
        new ScenarioEntryMigrationMap(List.of(new ScenarioEntryMigrationMap.IdPair(20, 900)));
    var placement =
        new ScenarioEntryPlacementMap(
            fileMap(game, targetFile),
            mapping,
            List.of(new ScenarioEntryPlacementMap.Placement(game, 10, 20, 0)));
    var fields =
        new ArrayList<@Nullable String>(
            Arrays.asList(
                "900",
                Integer.toString(game),
                Long.toString(targetFile),
                "1",
                "0",
                null,
                "narration",
                null,
                null,
                "hello",
                "raw",
                stamp));
    return new ScenarioEntryCopyBatch(placement, List.of(new ScenarioEntryCopyRow(fields)));
  }

  private static ScenarioEntryCopyBatch emptyEntries() {
    var mapping = new ScenarioEntryMigrationMap(List.of());
    var placement =
        new ScenarioEntryPlacementMap(new ScenarioFileMigrationMap(List.of()), mapping, List.of());
    return new ScenarioEntryCopyBatch(placement, List.of());
  }

  private static PostgresCopyTextEncoder encoder() {
    return new PostgresCopyTextEncoder();
  }
}
