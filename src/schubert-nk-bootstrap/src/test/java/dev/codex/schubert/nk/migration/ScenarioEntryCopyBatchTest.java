package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.migration.ScenarioEntryMigrationMap.IdPair;
import dev.codex.schubert.nk.migration.ScenarioEntryPlacementMap.Placement;
import dev.codex.schubert.nk.migration.ScenarioFileMigrationMap.FilePair;
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

/** SSC348; PT-MIG-BATCH001..012, NK-MIG-001 specification021 independent literals. */
final class ScenarioEntryCopyBatchTest {
  private static final String STAMP = "2026-01-01T00:00:00Z";
  private static final String GOLDEN =
      "900\t1\t500\t1\t7\t\\N\tnarration\t\\N\t\\N\ta\ta\t2026-01-01T00:00:00Z\n"
          + "100\t1\t500\t2\t3\t\\N\tnarration\t\\N\t\\N\tb\tb\t2026-01-01T00:00:00Z\n"
          + "50\t2\t600\t3\t0\t\\N\tnarration\t\\N\t\\N\tc\tc\t2026-01-01T00:00:00Z\n";

  private static ScenarioEntryPlacementMap placement() {
    return new ScenarioEntryPlacementMap(
        new ScenarioFileMigrationMap(List.of(new FilePair(2, 7, 600), new FilePair(1, 5, 500))),
        new ScenarioEntryMigrationMap(
            List.of(new IdPair(30, 50), new IdPair(2, 900), new IdPair(10, 100))),
        List.of(new Placement(2, 7, 30, 0), new Placement(1, 5, 10, 3), new Placement(1, 5, 2, 7)));
  }

  private static ScenarioEntryCopyRow row(
      String id, String game, String file, String order, String index, String body) {
    List<@Nullable String> fields =
        Arrays.asList(
            id, game, file, order, index, null, "narration", null, null, body, body, STAMP);
    return new ScenarioEntryCopyRow(fields);
  }

  private static List<ScenarioEntryCopyRow> rows() {
    return List.of(
        row("900", "1", "500", "1", "7", "a"),
        row("100", "1", "500", "2", "3", "b"),
        row("50", "2", "600", "3", "0", "c"));
  }

  private static ScenarioEntryCopyRow changed(ScenarioEntryCopyRow row, int index, String value) {
    var fields = new ArrayList<@Nullable String>(row.fields());
    fields.set(index, value);
    return new ScenarioEntryCopyRow(fields);
  }

  private static void rejectsChangedFirst(int index, String value) {
    var input = new ArrayList<>(rows());
    input.set(0, changed(input.get(0), index, value));
    assertThrows(
        IllegalArgumentException.class, () -> new ScenarioEntryCopyBatch(placement(), input));
  }

  @Test
  void batch001IndependentFullBytesAndCurrentGlobalOrder() {
    var source = rows();
    var batch =
        new ScenarioEntryCopyBatch(
            placement(), List.of(source.get(2), source.get(0), source.get(1)));
    assertEquals(List.of(source.get(0), source.get(1), source.get(2)), batch.rows());
    assertArrayEquals(
        GOLDEN.getBytes(StandardCharsets.US_ASCII), batch.copyBytes(new PostgresCopyTextEncoder()));
  }

  @Test
  void batch002ExactCardinalityAndEmptyDeclaredBatch() {
    assertThrows(
        IllegalArgumentException.class,
        () -> new ScenarioEntryCopyBatch(placement(), rows().subList(0, 2)));
    var extra = new ArrayList<>(rows());
    extra.add(row("999", "1", "500", "4", "9", "extra"));
    assertThrows(
        IllegalArgumentException.class, () -> new ScenarioEntryCopyBatch(placement(), extra));
    var emptyPlacement =
        new ScenarioEntryPlacementMap(
            new ScenarioFileMigrationMap(List.of()),
            new ScenarioEntryMigrationMap(List.of()),
            List.of());
    var empty = new ScenarioEntryCopyBatch(emptyPlacement, List.of());
    assertTrue(empty.rows().isEmpty());
    assertArrayEquals(new byte[0], empty.copyBytes(new PostgresCopyTextEncoder()));
    assertThrows(
        IllegalArgumentException.class, () -> new ScenarioEntryCopyBatch(emptyPlacement, rows()));
  }

  @Test
  void batch003DuplicateTargetIdCannotReplaceMissingRow() {
    var input = rows();
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ScenarioEntryCopyBatch(
                placement(), List.of(input.get(0), input.get(0), input.get(2))));
  }

  @Test
  void batch004UnknownTargetEvenWithEqualCount() {
    rejectsChangedFirst(0, "901");
  }

  @Test
  void batch005GameMustMatchTheDeclaredReference() {
    rejectsChangedFirst(1, "2");
  }

  @Test
  void batch006FileMustMatchTheDeclaredReference() {
    rejectsChangedFirst(2, "999");
  }

  @Test
  void batch007GlobalDisplayOrderMustMatchTheMapping() {
    rejectsChangedFirst(3, "9");
  }

  @Test
  void batch008FileLocalIndexMustMatchTheMapping() {
    rejectsChangedFirst(4, "8");
  }

  @Test
  void batch009SingleCanonicalTransactionTimestamp() {
    rejectsChangedFirst(11, "2027-01-01T00:00:00Z");
    var input = new ArrayList<ScenarioEntryCopyRow>();
    for (ScenarioEntryCopyRow row : rows())
      input.add(changed(row, 11, "2026-01-01T00:00:00.000001Z"));
    var batch = new ScenarioEntryCopyBatch(placement(), input);
    for (ScenarioEntryCopyRow row : batch.rows())
      assertEquals("2026-01-01T00:00:00.000001Z", row.fields().get(11));
  }

  @Test
  void batch010SnapshotListAndByteOwnership() {
    var input = new ArrayList<>(rows());
    var batch = new ScenarioEntryCopyBatch(placement(), input);
    input.clear();
    assertEquals(3, batch.rows().size());
    assertThrows(UnsupportedOperationException.class, () -> batch.rows().clear());
    byte[] first = batch.copyBytes(new PostgresCopyTextEncoder());
    first[0] = 0;
    assertArrayEquals(
        GOLDEN.getBytes(StandardCharsets.US_ASCII), batch.copyBytes(new PostgresCopyTextEncoder()));
  }

  @Test
  void batch011NullContractsFixedDiagnosticsAndFailureIsolation() {
    assertThrows(NullPointerException.class, () -> new ScenarioEntryCopyBatch(null, rows()));
    assertThrows(NullPointerException.class, () -> new ScenarioEntryCopyBatch(placement(), null));
    assertThrows(
        NullPointerException.class,
        () ->
            new ScenarioEntryCopyBatch(
                placement(), Arrays.asList(rows().get(0), null, rows().get(2))));
    var failure =
        assertThrows(
            IllegalArgumentException.class,
            () -> new ScenarioEntryCopyBatch(placement(), List.of()));
    assertEquals("migration scenario COPY batch is invalid", failure.getMessage());
    assertNull(failure.getCause());
    var batch = new ScenarioEntryCopyBatch(placement(), rows());
    assertEquals("ScenarioEntryCopyBatch[REDACTED]", batch.toString());
    assertThrows(NullPointerException.class, () -> batch.copyBytes(null));
    assertArrayEquals(
        GOLDEN.getBytes(StandardCharsets.US_ASCII), batch.copyBytes(new PostgresCopyTextEncoder()));
  }

  @Test
  void batch012FiniteOwnedWorkersCompareIndependentGolden()
      throws InterruptedException, ExecutionException, TimeoutException {
    var batch = new ScenarioEntryCopyBatch(placement(), rows());
    var executor = Executors.newFixedThreadPool(8);
    try {
      var futures = new ArrayList<Future<byte[]>>();
      for (int index = 0; index < 64; index++)
        futures.add(executor.submit(() -> batch.copyBytes(new PostgresCopyTextEncoder())));
      for (Future<byte[]> future : futures)
        assertArrayEquals(
            GOLDEN.getBytes(StandardCharsets.US_ASCII), future.get(5, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
