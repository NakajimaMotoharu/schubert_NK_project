package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
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

/** PT-MIG-SPEAKERBATCH001..016: independent literal PK/UK/FK and two COPY lines. */
final class SpeakerCopyBatchTest {
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String OTHER_STAMP = "2026-01-02T03:04:06Z";
  private static final String DIAGNOSTIC = "migration speaker COPY batch is invalid";
  private static final String NORMALIZED = "宣言名";
  private static final String FIRST_NAME = "話者A";
  private static final String SECOND_NAME = "話者B";
  private static final String GAME_ONE = "1";
  private static final String GAME_TWO = "2";
  private static final String FIRST_ID = "700";
  private static final String SECOND_ID = "600";
  private static final String GOLDEN =
      "700\t1\t話者A\t宣言名\ttrue\t\\N\t2026-01-02T03:04:05Z\n"
          + "600\t2\t話者B\t宣言名\tfalse\t\\N\t2026-01-02T03:04:05Z\n";
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test
  void speakerBatch001TwoLiteralRowsKeepDeclaredOrderAndBorrowedSink() throws IOException {
    var batch = normal();
    var sink = new MemorySink();
    batch.writeTo(writer(), sink);
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), sink.toByteArray());
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), batch.copyBytes(encoder()));
    assertEquals(FIRST_ID, batch.rows().get(0).fields().get(0));
    assertEquals(SECOND_ID, batch.rows().get(1).fields().get(0));
    assertEquals(0, sink.closes);
    assertEquals(0, sink.flushes);
  }

  @Test
  void speakerBatch002EmptyBatchAndEmptyReferencesStayEmpty() throws IOException {
    var batch = new SpeakerCopyBatch(List.of());
    assertTrue(batch.rows().isEmpty());
    assertArrayEquals(new byte[0], batch.copyBytes(encoder()));
    var sink = new MemorySink();
    batch.writeTo(writer(), sink);
    assertArrayEquals(new byte[0], sink.toByteArray());
    batch.validateEntries(emptyEntries());
  }

  @Test
  void speakerBatch003NullOuterAndElementsHaveFixedDiagnostic() {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> new SpeakerCopyBatch(null))
            .getMessage());
    var missing = new ArrayList<@Nullable SpeakerCopyRow>();
    missing.add(null);
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> new SpeakerCopyBatch(missing))
            .getMessage());
  }

  @Test
  void speakerBatch004PrimaryIdsAreUniqueAcrossBothGames() {
    var first = row(FIRST_ID, GAME_ONE, FIRST_NAME, NORMALIZED, STAMP);
    for (String game : List.of(GAME_ONE, GAME_TWO)) {
      var duplicate = row(FIRST_ID, game, SECOND_NAME, "別名", STAMP);
      assertThrows(
          IllegalArgumentException.class, () -> new SpeakerCopyBatch(List.of(first, duplicate)));
    }
  }

  @Test
  void speakerBatch005GameNormalizedKeyUsesExactTupleValues() {
    var first = row(FIRST_ID, GAME_ONE, FIRST_NAME, NORMALIZED, STAMP);
    var duplicate = row(SECOND_ID, GAME_ONE, SECOND_NAME, NORMALIZED, STAMP);
    assertThrows(
        IllegalArgumentException.class, () -> new SpeakerCopyBatch(List.of(first, duplicate)));
    assertEquals(2, normal().rows().size());
    var exact =
        new SpeakerCopyBatch(
            List.of(
                row(FIRST_ID, GAME_ONE, FIRST_NAME, "Name", STAMP),
                row(SECOND_ID, GAME_ONE, SECOND_NAME, "name", STAMP)));
    assertEquals(
        List.of("Name", "name"), exact.rows().stream().map(x -> x.fields().get(3)).toList());
    var collision =
        new SpeakerCopyBatch(
            List.of(
                row(FIRST_ID, GAME_ONE, FIRST_NAME, "Aa", STAMP),
                row(SECOND_ID, GAME_ONE, SECOND_NAME, "BB", STAMP)));
    assertEquals(2, collision.rows().size());
  }

  @Test
  void speakerBatch006MixedTimestampCannotPassAsOneTransaction() {
    var first = row(FIRST_ID, GAME_ONE, FIRST_NAME, NORMALIZED, STAMP);
    var second = row(SECOND_ID, GAME_TWO, SECOND_NAME, NORMALIZED, OTHER_STAMP);
    assertThrows(
        IllegalArgumentException.class, () -> new SpeakerCopyBatch(List.of(first, second)));
    assertEquals(2, normal().rows().size());
  }

  @Test
  void speakerBatch007CallerListAndOutputBuffersHaveSeparateOwnership() {
    var input = new ArrayList<@Nullable SpeakerCopyRow>(normal().rows());
    var batch = new SpeakerCopyBatch(input);
    input.clear();
    assertEquals(2, batch.rows().size());
    assertThrows(UnsupportedOperationException.class, () -> batch.rows().clear());
    byte[] first = batch.copyBytes(encoder());
    byte[] second = batch.copyBytes(encoder());
    assertNotSame(first, second);
    first[0] = 0;
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), second);
  }

  @Test
  void speakerBatch008EveryNullableWriteBoundaryFailsBeforeBytes() {
    var batch = normal();
    var sink = new MemorySink();
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> batch.copyBytes(null)).getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> batch.writeTo(null, sink)).getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> batch.writeTo(writer(), null))
            .getMessage());
    assertArrayEquals(new byte[0], sink.toByteArray());
    assertEquals(0, sink.closes);
  }

  @Test
  void speakerBatch009PartialIoHasOneFailureAndNoAutomaticReplay() {
    var failure = new IOException("synthetic speaker COPY failure");
    var sink = new FailingSink(failure);
    try (sink) {
      assertSame(failure, assertThrows(IOException.class, () -> normal().writeTo(writer(), sink)));
      assertEquals("70", sink.output.toString(StandardCharsets.UTF_8));
      assertEquals(1, sink.failures);
      assertEquals(0, sink.closes);
      assertEquals(0, sink.flushes);
    }
    assertEquals(1, sink.closes);
  }

  @Test
  void speakerBatch010RuntimeAndErrorPropagateIdenticalInstances() {
    var runtime = new IllegalStateException("synthetic runtime");
    assertUncheckedBorrowedFailure(
        runtime,
        () -> {
          throw runtime;
        });
    var error = new AssertionError("synthetic error");
    assertUncheckedBorrowedFailure(
        error,
        () -> {
          throw error;
        });
  }

  private static void assertUncheckedBorrowedFailure(Throwable failure, Runnable throwOnWrite) {
    var batch = normal();
    var sink =
        new ByteArrayOutputStream() {
          private int closes;
          private int flushes;

          @Override
          public synchronized void write(byte[] bytes, int offset, int length) {
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
    try (sink) {
      assertSame(failure, assertThrows(failure.getClass(), () -> batch.writeTo(writer(), sink)));
      assertEquals(0, sink.closes);
      assertEquals(0, sink.flushes);
    }
    assertEquals(1, sink.closes);
  }

  @Test
  void speakerBatch011MissingReferencesAndNarrationWithoutSpeakers() {
    var batch = normal();
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> batch.validateEntries(null))
            .getMessage());
    var empty = new SpeakerCopyBatch(List.of());
    empty.validateEntries(entries(GAME_ONE, null, STAMP));
    assertTrue(empty.rows().isEmpty());
  }

  @Test
  void speakerBatch012KnownDialogueSpeakersMustBelongToSameGame() {
    var batch = normal();
    batch.validateEntries(entries(GAME_ONE, FIRST_ID, STAMP));
    batch.validateEntries(entries(GAME_TWO, SECOND_ID, STAMP));
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), batch.copyBytes(encoder()));
  }

  @Test
  void speakerBatch013UnknownAndCrossGameSpeakersAreRejected() {
    var batch = normal();
    var unknown = entries(GAME_ONE, "999", STAMP);
    var otherGame = entries(GAME_TWO, FIRST_ID, STAMP);
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> batch.validateEntries(unknown))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> batch.validateEntries(otherGame))
            .getMessage());
  }

  @Test
  void speakerBatch014EvenNarrationSharesOneTimestampAcrossSets() {
    var batch = normal();
    var narration = entries(GAME_ONE, null, OTHER_STAMP);
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> batch.validateEntries(narration))
            .getMessage());
    batch.validateEntries(emptyEntries());
    batch.validateEntries(entries(GAME_ONE, null, STAMP));
  }

  @Test
  void speakerBatch015FixedRedactionAndIndependentSuccessAfterRejection() {
    assertThrows(IllegalArgumentException.class, () -> new SpeakerCopyBatch(null));
    var batch = normal();
    assertEquals("SpeakerCopyBatch[REDACTED]", batch.toString());
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.UTF_8), batch.copyBytes(encoder()));
  }

  @Test
  void speakerBatch016FiniteSharedReadersKeepIndependentCopies()
      throws InterruptedException, ExecutionException, TimeoutException {
    var batch = normal();
    var references = entries(GAME_ONE, FIRST_ID, STAMP);
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<byte[]>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(
            executor.submit(
                () -> {
                  batch.validateEntries(references);
                  return batch.copyBytes(encoder());
                }));
      for (var future : futures)
        assertArrayEquals(
            GOLDEN.getBytes(StandardCharsets.UTF_8), future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static SpeakerCopyBatch normal() {
    return new SpeakerCopyBatch(
        List.of(
            row(FIRST_ID, GAME_ONE, FIRST_NAME, NORMALIZED, STAMP),
            row(SECOND_ID, GAME_TWO, SECOND_NAME, NORMALIZED, STAMP)));
  }

  private static SpeakerCopyRow row(
      String id, String game, String name, String normalized, String stamp) {
    return new SpeakerCopyRow(
        Arrays.<@Nullable String>asList(
            id, game, name, normalized, game.equals(GAME_ONE) ? "true" : "false", null, stamp));
  }

  private static ScenarioEntryCopyBatch entries(
      String game, @Nullable String speaker, String stamp) {
    int gameId = Integer.parseInt(game);
    var files =
        new ScenarioFileMigrationMap(
            List.of(new ScenarioFileMigrationMap.FilePair(gameId, 10, 100)));
    var mapping =
        new ScenarioEntryMigrationMap(List.of(new ScenarioEntryMigrationMap.IdPair(20, 900)));
    var placement =
        new ScenarioEntryPlacementMap(
            files, mapping, List.of(new ScenarioEntryPlacementMap.Placement(gameId, 10, 20, 0)));
    var row =
        new ScenarioEntryCopyRow(
            Arrays.<@Nullable String>asList(
                "900",
                game,
                "100",
                GAME_ONE,
                "0",
                null,
                speaker == null ? "narration" : "dialogue",
                speaker,
                null,
                "hello",
                "raw",
                stamp));
    return new ScenarioEntryCopyBatch(placement, List.of(row));
  }

  private static ScenarioEntryCopyBatch emptyEntries() {
    var files = new ScenarioFileMigrationMap(List.of());
    var mapping = new ScenarioEntryMigrationMap(List.of());
    return new ScenarioEntryCopyBatch(
        new ScenarioEntryPlacementMap(files, mapping, List.of()), List.of());
  }

  private static PostgresCopyTextEncoder encoder() {
    return new PostgresCopyTextEncoder();
  }

  private static PostgresCopyTextWriter writer() {
    return new PostgresCopyTextWriter(encoder());
  }

  private static final class MemorySink extends ByteArrayOutputStream {
    private int closes;
    private int flushes;

    @Override
    public void close() {
      closes++;
    }

    @Override
    public void flush() {
      flushes++;
    }
  }

  private static final class FailingSink extends OutputStream {
    private static final int PREFIX_BYTES = 2;
    private final ByteArrayOutputStream output = new ByteArrayOutputStream();
    private final IOException failure;
    private int failures;
    private int closes;
    private int flushes;

    private FailingSink(IOException failure) {
      this.failure = failure;
    }

    @Override
    public void write(int value) throws IOException {
      if (output.size() == PREFIX_BYTES) {
        failures++;
        throw failure;
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
  }
}
