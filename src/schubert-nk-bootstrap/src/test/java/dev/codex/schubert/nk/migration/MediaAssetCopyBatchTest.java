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
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-MEDIABATCH001..020; literal SQL/golden and independent Python SHA vector. */
final class MediaAssetCopyBatchTest {
  private static final String SHA =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String MUSIC_ID =
      "6f71a62541ab381ee0186f4f946bb6af57b0824509fc4ab61fd99b3bcac5105c";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String GOLDEN =
      "1\tvideo-a\tVIDEO\tA\tMAIN\t\\N\tvideo/a.mp4\tcurrent/a.mp4\ta.mp4\t3"
          + "\tba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\tvideo/mp4\tvideo-b"
          + "\t\\N\t\\N\t1\t2026-01-02T03:04:05Z\n"
          + "2\tvideo-b\tVIDEO\tB\tMAIN\t\\N\tvideo/b.mp4\tcurrent/b.mp4\tb.mp4\t3"
          + "\tba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\tvideo/mp4\t\\N"
          + "\t\\N\t\\N\t2\t2026-01-02T03:04:05Z\n"
          + "3\t6f71a62541ab381ee0186f4f946bb6af57b0824509fc4ab61fd99b3bcac5105c\tMUSIC\tC\tBGM"
          + "\t\\N\tmusic/c.ogg\tmusic/c.ogg\tc.ogg\t3"
          + "\tba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\taudio/ogg\t\\N"
          + "\t\\N\tN\t1\t2026-01-02T03:04:05Z\n";
  private static final String DIAGNOSTIC = "migration media asset COPY batch is invalid";
  private static final String PARENT_A = "video-a";
  private static final String PARENT_B = "video-b";
  private static final String VIDEO_TYPE = "VIDEO";
  private static final String SOURCE_A = "current/a.mp4";
  private static final String SOURCE_B = "current/b.mp4";
  private static final String TARGET_A = "video/a.mp4";
  private static final String TARGET_B = "video/b.mp4";
  private static final String MUSIC_PATH = "music/c.ogg";
  private static final String VIDEO_MIME = "video/mp4";
  private static final String ONE = "1";
  private static final String TWO = "2";
  private static final String THREE = "3";
  private static final int ID_INDEX = 0;
  private static final int LOGICAL_INDEX = 1;
  private static final int STORAGE_INDEX = 6;
  private static final int DISPLAY_INDEX = 7;
  private static final int PARENT_INDEX = 12;
  private static final int STAMP_INDEX = 16;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test
  void independentMixedSeventeenColumnGoldenAndColumnOrder() throws NoSuchAlgorithmException {
    var batch = normal();
    assertArrayEquals(expected(), batch.copyBytes(new PostgresCopyTextEncoder()));
    assertEquals(
        List.of(
            "id",
            "logical_id",
            "media_type",
            "title",
            "category",
            "section",
            "storage_relative_path",
            "display_path",
            "file_name",
            "byte_size",
            "sha256",
            "mime_type",
            "parent_logical_id",
            "pair_key",
            "pair_role",
            "display_order",
            "created_at"),
        batch.columnNames());
  }

  @Test
  void emptyDeclarationRemainsEmpty() throws IOException {
    var batch = new MediaAssetCopyBatch(new AssetMigrationManifest(List.of()), List.of());
    assertEquals(List.of(), batch.rows());
    assertArrayEquals(new byte[0], batch.copyBytes(new PostgresCopyTextEncoder()));
    var sink = new TrackingSink();
    batch.writeTo(writer(), sink);
    assertEquals(0, sink.size());
    assertEquals(0, sink.closes);
    assertEquals(0, sink.flushes);
  }

  @Test
  void duplicatePrimaryIdIsRejected() throws NoSuchAlgorithmException {
    var rows = raw();
    rows.get(1).set(ID_INDEX, ONE);
    reject(rows, claims());
  }

  @Test
  void duplicateLogicalIdIsRejected() throws NoSuchAlgorithmException {
    var rows = raw();
    rows.get(1).set(LOGICAL_INDEX, PARENT_A);
    reject(rows, claims());
  }

  @Test
  void duplicateTypedStorageIsRejected() throws NoSuchAlgorithmException {
    var rows = raw();
    rows.get(1).set(STORAGE_INDEX, TARGET_A);
    reject(rows, claims());
  }

  @Test
  void transactionTimestampsMustAgree() throws NoSuchAlgorithmException {
    var rows = raw();
    rows.get(1).set(STAMP_INDEX, "2026-01-02T03:04:06Z");
    reject(rows, claims());
  }

  @Test
  void backwardAndForwardParentReferencesUseTheWholeSet() throws NoSuchAlgorithmException {
    var rows = raw();
    rows.get(0).set(PARENT_INDEX, null);
    rows.get(1).set(PARENT_INDEX, PARENT_A);
    assertEquals(
        List.of(PARENT_A, PARENT_B, MUSIC_ID),
        make(rows, claims()).rows().stream().map(MediaAssetCopyRow::logicalId).toList());
    assertTrue(normal().rows().get(0).parentLogicalId().isPresent());
  }

  @Test
  void unknownParentIsRejectedAfterBuildingTheWholeSet() throws NoSuchAlgorithmException {
    var rows = raw();
    rows.get(0).set(PARENT_INDEX, "absent");
    reject(rows, claims());
  }

  @Test
  void selfAndCyclesRemainAllowedByTheDeclaredForeignKey() throws NoSuchAlgorithmException {
    var rows = raw();
    rows.get(0).set(PARENT_INDEX, PARENT_A);
    assertEquals(PARENT_A, make(rows, claims()).rows().get(0).parentLogicalId().orElseThrow());
    rows.get(0).set(PARENT_INDEX, PARENT_B);
    rows.get(1).set(PARENT_INDEX, PARENT_A);
    assertEquals(PARENT_A, make(rows, claims()).rows().get(1).parentLogicalId().orElseThrow());
  }

  @Test
  void manifestCardinalityCannotBeSmallerOrLarger() throws NoSuchAlgorithmException {
    var less = claims();
    less.remove(0);
    reject(raw(), less);
    var more = claims();
    more.add(
        new AssetMigrationManifest.Entry(
            AssetMigrationManifest.Kind.VIDEO, "other.mp4", "video/other.mp4", 3, SHA));
    reject(raw(), more);
  }

  @Test
  void unknownOrRepeatedSourceCannotConsumeOneClaimTwice() throws NoSuchAlgorithmException {
    var rows = raw();
    rows.get(0).set(DISPLAY_INDEX, "unknown.mp4");
    reject(rows, claims());
    rows = raw();
    rows.get(1).set(DISPLAY_INDEX, SOURCE_A);
    reject(rows, claims());
  }

  @Test
  void kindsMustBeMediaAndMatchTheRow() throws NoSuchAlgorithmException {
    for (var kind :
        List.of(
            AssetMigrationManifest.Kind.SCENARIO,
            AssetMigrationManifest.Kind.AUDIO,
            AssetMigrationManifest.Kind.MUSIC)) {
      var claims = claims();
      claims.set(0, new AssetMigrationManifest.Entry(kind, SOURCE_A, TARGET_A, 3, SHA));
      reject(raw(), claims);
    }
  }

  @Test
  void targetSizeAndHashEachMatchTheExactDeclaration() throws NoSuchAlgorithmException {
    var claims = claims();
    claims.set(
        0,
        new AssetMigrationManifest.Entry(
            AssetMigrationManifest.Kind.VIDEO, SOURCE_A, "video/other.mp4", 3, SHA));
    reject(raw(), claims);
    claims = claims();
    claims.set(
        0,
        new AssetMigrationManifest.Entry(
            AssetMigrationManifest.Kind.VIDEO, SOURCE_A, TARGET_A, 4, SHA));
    reject(raw(), claims);
    claims = claims();
    claims.set(
        0,
        new AssetMigrationManifest.Entry(
            AssetMigrationManifest.Kind.VIDEO, SOURCE_A, TARGET_A, 3, "0".repeat(64)));
    reject(raw(), claims);
  }

  @Test
  void nullableBoundariesHaveFixedDiagnostics() throws NoSuchAlgorithmException {
    var manifest = new AssetMigrationManifest(claims());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> new MediaAssetCopyBatch(null, List.of()))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> new MediaAssetCopyBatch(manifest, null))
            .getMessage());
    var rows = values(raw());
    rows.set(1, null);
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> new MediaAssetCopyBatch(manifest, rows))
            .getMessage());
  }

  @Test
  void snapshotAndReturnedViewsAreImmutableAndKeepDeclaredOrder() throws NoSuchAlgorithmException {
    var input = values(raw());
    Collections.swap(input, 0, 2);
    var batch = new MediaAssetCopyBatch(new AssetMigrationManifest(claims()), input);
    input.clear();
    assertEquals(
        List.of(MUSIC_ID, PARENT_B, PARENT_A),
        batch.rows().stream().map(MediaAssetCopyRow::logicalId).toList());
    assertThrows(UnsupportedOperationException.class, () -> batch.rows().clear());
    assertThrows(UnsupportedOperationException.class, () -> batch.columnNames().clear());
    assertThrows(UnsupportedOperationException.class, () -> batch.rows().get(0).fields().clear());
  }

  @Test
  void typedAccessorsExposeValidatedValuesAndOptionalParents() throws NoSuchAlgorithmException {
    var row = normal().rows().get(0);
    assertEquals(ONE, row.id());
    assertEquals(PARENT_A, row.logicalId());
    assertEquals(VIDEO_TYPE, row.mediaType());
    assertEquals(TARGET_A, row.storageRelativePath());
    assertEquals(SOURCE_A, row.displayPath());
    assertEquals(THREE, row.byteSize());
    assertEquals(SHA, row.sha256());
    assertEquals(STAMP, row.createdAt());
    assertEquals(PARENT_B, row.parentLogicalId().orElseThrow());
    assertTrue(normal().rows().get(1).parentLogicalId().isEmpty());
  }

  @Test
  void returnedBytesAreOwnedAndNullEncoderIsRejected() throws NoSuchAlgorithmException {
    var batch = normal();
    byte[] first = batch.copyBytes(new PostgresCopyTextEncoder());
    byte[] second = batch.copyBytes(new PostgresCopyTextEncoder());
    assertNotSame(first, second);
    first[0] = 0;
    assertArrayEquals(expected(), second);
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> batch.copyBytes(null)).getMessage());
  }

  @Test
  void borrowedWriterAndSinkKeepOwnershipAndNullContract()
      throws IOException, NoSuchAlgorithmException {
    var batch = normal();
    var sink = new TrackingSink();
    batch.writeTo(writer(), sink);
    assertArrayEquals(expected(), sink.toByteArray());
    assertEquals(0, sink.closes);
    assertEquals(0, sink.flushes);
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> batch.writeTo(null, sink)).getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> batch.writeTo(writer(), null))
            .getMessage());
  }

  @Test
  void ioFailureIdentityPartialOutputAndIndependentRetryArePreserved()
      throws IOException, NoSuchAlgorithmException {
    var batch = normal();
    var sink = new FailingSink();
    try (sink) {
      assertSame(
          sink.failure, assertThrows(IOException.class, () -> batch.writeTo(writer(), sink)));
      assertArrayEquals("1\t".getBytes(StandardCharsets.UTF_8), sink.prefix.toByteArray());
      assertEquals(0, sink.closes);
      assertEquals(0, sink.flushes);
    }
    assertEquals(1, sink.closes);
    var normal = new TrackingSink();
    batch.writeTo(writer(), normal);
    assertArrayEquals(expected(), normal.toByteArray());
    assertEquals("MediaAssetCopyBatch[REDACTED]", batch.toString());
  }

  @Test
  void finiteWorkersUseOneImmutableBatchWithIndependentSinks()
      throws NoSuchAlgorithmException, InterruptedException, ExecutionException, TimeoutException {
    var batch = normal();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var results = new ArrayList<Future<byte[]>>();
      for (int i = 0; i < TASKS; i++)
        results.add(
            executor.submit(
                () -> {
                  var sink = new TrackingSink();
                  batch.writeTo(writer(), sink);
                  return sink.toByteArray();
                }));
      for (var result : results)
        assertArrayEquals(expected(), result.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static MediaAssetCopyBatch normal() throws NoSuchAlgorithmException {
    return make(raw(), claims());
  }

  private static MediaAssetCopyBatch make(
      List<List<@Nullable String>> raw, List<AssetMigrationManifest.Entry> claims)
      throws NoSuchAlgorithmException {
    return new MediaAssetCopyBatch(new AssetMigrationManifest(claims), values(raw));
  }

  private static ArrayList<@Nullable MediaAssetCopyRow> values(List<List<@Nullable String>> rows)
      throws NoSuchAlgorithmException {
    var result = new ArrayList<@Nullable MediaAssetCopyRow>();
    for (var row : rows) result.add(new MediaAssetCopyRow(row));
    return result;
  }

  private static void reject(
      List<List<@Nullable String>> rows, List<AssetMigrationManifest.Entry> claims)
      throws NoSuchAlgorithmException {
    var validRows = values(rows);
    var manifest = new AssetMigrationManifest(claims);
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> new MediaAssetCopyBatch(manifest, validRows))
            .getMessage());
  }

  private static List<List<@Nullable String>> raw() {
    return new ArrayList<>(
        List.of(
            new ArrayList<@Nullable String>(
                Arrays.<@Nullable String>asList(
                    ONE,
                    PARENT_A,
                    VIDEO_TYPE,
                    "A",
                    "MAIN",
                    null,
                    TARGET_A,
                    SOURCE_A,
                    "a.mp4",
                    THREE,
                    SHA,
                    VIDEO_MIME,
                    PARENT_B,
                    null,
                    null,
                    ONE,
                    STAMP)),
            new ArrayList<@Nullable String>(
                Arrays.<@Nullable String>asList(
                    TWO,
                    PARENT_B,
                    VIDEO_TYPE,
                    "B",
                    "MAIN",
                    null,
                    TARGET_B,
                    SOURCE_B,
                    "b.mp4",
                    THREE,
                    SHA,
                    VIDEO_MIME,
                    null,
                    null,
                    null,
                    TWO,
                    STAMP)),
            new ArrayList<@Nullable String>(
                Arrays.<@Nullable String>asList(
                    THREE,
                    MUSIC_ID,
                    "MUSIC",
                    "C",
                    "BGM",
                    null,
                    MUSIC_PATH,
                    MUSIC_PATH,
                    "c.ogg",
                    THREE,
                    SHA,
                    "audio/ogg",
                    null,
                    null,
                    "N",
                    ONE,
                    STAMP))));
  }

  private static ArrayList<AssetMigrationManifest.Entry> claims() {
    return new ArrayList<>(
        List.of(
            new AssetMigrationManifest.Entry(
                AssetMigrationManifest.Kind.VIDEO, SOURCE_A, TARGET_A, 3, SHA),
            new AssetMigrationManifest.Entry(
                AssetMigrationManifest.Kind.VIDEO, SOURCE_B, TARGET_B, 3, SHA),
            new AssetMigrationManifest.Entry(
                AssetMigrationManifest.Kind.MUSIC, MUSIC_PATH, MUSIC_PATH, 3, SHA)));
  }

  private static byte[] expected() {
    return GOLDEN.getBytes(StandardCharsets.UTF_8);
  }

  private static PostgresCopyTextWriter writer() {
    return new PostgresCopyTextWriter(new PostgresCopyTextEncoder());
  }

  private static final class TrackingSink extends ByteArrayOutputStream {
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
    private final IOException failure = new IOException("synthetic media batch failure");
    private final ByteArrayOutputStream prefix = new ByteArrayOutputStream();
    private int closes;
    private int flushes;

    @Override
    public void write(int value) throws IOException {
      if (prefix.size() == PREFIX_BYTES) throw failure;
      prefix.write(value);
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
