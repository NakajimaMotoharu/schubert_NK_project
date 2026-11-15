package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.math.BigDecimal;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-CURRENTTRANSFER001..020; independent literal two-peer projection/COPY, no actual DB. */
final class CurrentMigrationTransferTest {
  private static final String SYNTHETIC = "synthetic transfer";
  private static final String ONE = "1";
  private static final String HASH =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String VOICE = "voice";
  private static final String FILE = "file.txt";
  private static final String AUDIO = "a.ogg";
  private static final String INPUT_ERROR = "migration Current transfer input is invalid";
  private static final String TARGET_ERROR = "migration Current transfer target is invalid";
  private static final String UNEXPECTED_COPY = "unexpected COPY";
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final String NORMAL_HASH =
      "43d8bbc36eb9ac1b173c2af321fbb9b411137a1927ef5a32b29e0f212755486f";
  private static final String EMPTY_HASH =
      "4444698baa3c905644477124201c2c291637b7c8441ed296c30acb231b1dcd90";
  private static final List<String> TUPLES =
      List.of(
          "speakers|1|46|7075f6a72b05c4cff3830220732aa044852d3c871eb3c016c550015c2aa501ac",
          "script_files|1|141|57621009e943ae8a6da658cc58070e0442f5af23a9300ef631e6a6fe4302e101",
          "script_entries|1|62|4ee1c9e7ad6a2571ab6716dad512d444bd3f508540340558a06d2ec8c3838384",
          "audio_files|1|135|277a531fcad75c69a6e0541784d509d8e24d92105ccb330af972d518dc4e4e42",
          "media_assets|1|169|8d47e701d4300e31892e1ee4516660581c632689da66c0cad440be50954b30fe",
          "entry_audio_links|1|39|caed946009561acc38580f847b47b139f453a88356b204b73391bcb5cc4f9eef");

  @Test
  void transfer001NormalCurrentReadPrecedesSameTargetCopyAndFinalization() throws Exception {
    var source = source();
    var target = target();
    var connection = target.connection();
    var seen = new ArrayList<String>();
    var result =
        new CurrentMigrationTransfer()
            .transfer(
                source.connection(),
                connection,
                assembler(false),
                counts(1),
                media(),
                Instant.parse(STAMP),
                (c, t, rows) -> {
                  assertSame(connection, c);
                  assertEquals(5, source.sql.size());
                  assertEquals(10, source.closes.size());
                  assertEquals(19, target.sql.size());
                  var sink = new ByteArrayOutputStream();
                  new PostgresCopyTextWriter(new PostgresCopyTextEncoder()).writeRows(rows, sink);
                  byte[] bytes = sink.toByteArray();
                  seen.add(
                      t.substring("pg_temp.nk_mig_".length())
                          + "|"
                          + rows.size()
                          + "|"
                          + bytes.length
                          + "|"
                          + HexFormat.of().formatHex(digest(bytes)));
                  return rows.size();
                });
    assertEquals(TUPLES, seen);
    assertEquals(NORMAL_HASH, result.sha256());
    assertEquals(95, target.sql.size());
  }

  @Test
  void transfer002EmptyFiveProjectionsAndSixCopiesRemainExplicit() throws Exception {
    var source = empty();
    var target = MigrationMasterTargetPublisherTest.coordinatorFixture(true);
    var tables = new ArrayList<String>();
    var result =
        new CurrentMigrationTransfer()
            .transfer(
                source.connection(),
                target.connection(),
                assembler(true),
                counts(0),
                List.of(),
                Instant.parse(STAMP),
                (c, t, rows) -> {
                  assertTrue(rows.isEmpty());
                  tables.add(t);
                  return 0;
                });
    assertEquals(6, tables.size());
    assertEquals(6, tables.stream().distinct().count());
    assertEquals(5, source.sql.size());
    assertEquals(10, source.closes.size());
    assertEquals(95, target.sql.size());
    assertEquals(EMPTY_HASH, result.sha256());
  }

  @Test
  void transfer003AllSevenNullsRejectBeforeBothPeersAreQueried() throws Exception {
    for (int missing = 0; missing < 7; missing++) {
      final int field = missing;
      var source = source();
      var target = target();
      var s = source.connection();
      var t = target.connection();
      var a = assembler(false);
      var count = counts(1);
      var media = media();
      var at = Instant.parse(STAMP);
      var failure =
          assertThrows(
              IllegalArgumentException.class,
              () ->
                  new CurrentMigrationTransfer()
                      .transfer(
                          field == 0 ? null : s,
                          field == 1 ? null : t,
                          field == 2 ? null : a,
                          field == 3 ? null : count,
                          field == 4 ? null : media,
                          field == 5 ? null : at,
                          field == 6 ? null : forbidden()));
      assertEquals(INPUT_ERROR, failure.getMessage());
      assertNull(failure.getCause());
      assertTrue(source.calls.isEmpty());
      assertTrue(target.sql.isEmpty());
    }
  }

  @Test
  void transfer004SameConnectionReferenceRejectsBeforeEitherQuery() throws Exception {
    var source = source();
    var c = source.connection();
    var a = assembler(false);
    assertEquals(
        INPUT_ERROR,
        assertThrows(
                IllegalArgumentException.class,
                () ->
                    new CurrentMigrationTransfer()
                        .transfer(c, c, a, counts(1), media(), Instant.parse(STAMP), forbidden()))
            .getMessage());
    assertTrue(source.calls.isEmpty());
  }

  @Test
  void transfer005AutocommitTargetNeverReadsSource() throws Exception {
    var source = source();
    var target = target();
    target.autoCommit = true;
    assertEquals(
        TARGET_ERROR,
        assertThrows(SQLException.class, () -> invoke(source, target, forbidden())).getMessage());
    assertTrue(source.calls.isEmpty());
    assertTrue(target.sql.isEmpty());
  }

  @Test
  void transfer006ReadOnlyTargetNeverReadsSource() throws Exception {
    var source = source();
    var target = target();
    target.readOnly = true;
    assertEquals(
        TARGET_ERROR,
        assertThrows(SQLException.class, () -> invoke(source, target, forbidden())).getMessage());
    assertTrue(source.calls.isEmpty());
    assertTrue(target.sql.isEmpty());
  }

  @Test
  void transfer007EveryTargetAttributeFailurePropagatesUntouched() throws Exception {
    for (boolean readOnly : List.of(false, true))
      for (Throwable failure : failures()) {
        var source = source();
        var target = target();
        target.attributeFailure = failure;
        target.failReadOnly = readOnly;
        assertSame(
            failure, assertThrows(Throwable.class, () -> invoke(source, target, forbidden())));
        assertTrue(source.calls.isEmpty());
        assertTrue(target.sql.isEmpty());
      }
  }

  @Test
  void transfer008SourceAttributeFailuresNeverReachTargetSql() throws Exception {
    for (String phase : List.of("auto:begin", "readonly:begin", "isolation:begin"))
      for (Throwable failure : failures()) {
        var source = source();
        var target = target();
        source.failurePhase = phase;
        source.failure = failure;
        assertSame(
            failure, assertThrows(Throwable.class, () -> invoke(source, target, forbidden())));
        assertTrue(source.sql.isEmpty());
        assertTrue(target.sql.isEmpty());
      }
  }

  @Test
  void transfer009EachSourceQueryFaultStopsAllTargetWork() throws Exception {
    for (int table = 0; table < 5; table++)
      for (Throwable failure : failures()) {
        var source = source();
        var target = target();
        source.failurePhase = "query:" + table;
        source.failure = failure;
        assertSame(
            failure, assertThrows(Throwable.class, () -> invoke(source, target, forbidden())));
        assertEquals(table + 1, source.sql.size());
        assertTrue(target.sql.isEmpty());
      }
  }

  @Test
  void transfer010EveryExpectedCountIsBoundToItsOwnReader() throws Exception {
    for (int index = 0; index < 5; index++) {
      var source = source();
      var target = target();
      final int field = index;
      var a = assembler(false);
      var count =
          new CurrentMigrationTransfer.SourceCounts(
              field == 0 ? 0 : 1,
              field == 1 ? 0 : 1,
              field == 2 ? 0 : 1,
              field == 3 ? 0 : 1,
              field == 4 ? 0 : 1);
      assertThrows(
          SQLException.class,
          () ->
              new CurrentMigrationTransfer()
                  .transfer(
                      source.connection(),
                      target.connection(),
                      a,
                      count,
                      media(),
                      Instant.parse(STAMP),
                      forbidden()));
      assertEquals(index + 1, source.sql.size());
      assertTrue(target.sql.isEmpty());
    }
  }

  @Test
  void transfer011UnknownCurrentMappingCannotMutateTarget() throws Exception {
    var source = source();
    var target = target();
    source.tables.get(0).getFirst()[0] = Long.MIN_VALUE;
    assertThrows(IllegalArgumentException.class, () -> invoke(source, target, forbidden()));
    assertEquals(5, source.sql.size());
    assertTrue(target.sql.isEmpty());
  }

  @Test
  void transfer012MediaClaimMismatchRejectsBeforeTargetPrepare() throws Exception {
    var source = source();
    var target = target();
    var a = assembler(false);
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CurrentMigrationTransfer()
                .transfer(
                    source.connection(),
                    target.connection(),
                    a,
                    counts(1),
                    List.of(),
                    Instant.parse(STAMP),
                    forbidden()));
    assertEquals(5, source.sql.size());
    assertTrue(target.sql.isEmpty());
  }

  @Test
  void transfer013InvalidSubmicrosecondTimeNeverMutatesTarget() throws Exception {
    var source = source();
    var target = target();
    var a = assembler(false);
    var at = Instant.parse(STAMP).plusNanos(1);
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CurrentMigrationTransfer()
                .transfer(
                    source.connection(),
                    target.connection(),
                    a,
                    counts(1),
                    media(),
                    at,
                    forbidden()));
    assertEquals(5, source.sql.size());
    assertTrue(target.sql.isEmpty());
  }

  @Test
  void transfer014EveryCopyFailurePreservesIdentityAndNeverFinalizes() throws Exception {
    for (int table = 0; table < 6; table++)
      for (Throwable failure : copyFailures()) {
        final int slot = table;
        var source = source();
        var target = target();
        int[] seen = {0};
        assertSame(
            failure,
            assertThrows(
                Throwable.class,
                () ->
                    invoke(
                        source,
                        target,
                        (c, t, rows) -> {
                          int index = seen[0];
                          seen[0]++;
                          if (index == slot) {
                            if (failure instanceof SQLException sql) throw sql;
                            if (failure instanceof IOException io) throw io;
                            if (failure instanceof RuntimeException runtime) throw runtime;
                            throw (Error) failure;
                          }
                          return rows.size();
                        })));
        assertEquals(table + 1, seen[0]);
        assertEquals(19, target.sql.size());
        assertEquals(5, source.sql.size());
      }
  }

  @Test
  void transfer015CountMismatchAtEveryCopyStopsWithoutRetry() throws Exception {
    for (int table = 0; table < 6; table++) {
      final int slot = table;
      var source = source();
      var target = target();
      int[] seen = {0};
      assertThrows(
          SQLException.class,
          () ->
              invoke(
                  source,
                  target,
                  (c, t, rows) -> {
                    int index = seen[0];
                    seen[0]++;
                    return index == slot ? Long.MAX_VALUE : rows.size();
                  }));
      assertEquals(table + 1, seen[0]);
      assertEquals(19, target.sql.size());
    }
  }

  @Test
  void transfer016PrepareAndFinalFailuresDoNotRepeatSourceOrCopy() throws Exception {
    for (int sql : List.of(0, 18, 19, 94))
      for (Throwable failure : failures()) {
        var source = source();
        var target = target();
        target.badSql = sql;
        target.failure = failure;
        int[] seen = {0};
        assertSame(
            failure,
            assertThrows(
                Throwable.class,
                () ->
                    invoke(
                        source,
                        target,
                        (c, t, rows) -> {
                          seen[0]++;
                          return rows.size();
                        })));
        assertEquals(sql + 1, target.sql.size());
        assertEquals(sql < 19 ? 0 : 6, seen[0]);
        assertEquals(5, source.sql.size());
      }
  }

  @Test
  void transfer017EachNegativeTypedCountRejects() {
    for (int index = 0; index < 5; index++) {
      final int field = index;
      assertEquals(
          INPUT_ERROR,
          assertThrows(
                  IllegalArgumentException.class,
                  () ->
                      new CurrentMigrationTransfer.SourceCounts(
                          field == 0 ? -1 : 0,
                          field == 1 ? -1 : 0,
                          field == 2 ? -1 : 0,
                          field == 3 ? -1 : 0,
                          field == 4 ? -1 : 0))
              .getMessage());
    }
  }

  @Test
  void transfer018TypedCountsHaveIndependentGeneratedValueContracts() {
    var one = counts(1);
    var same = counts(1);
    var zero = counts(0);
    var max = counts(Integer.MAX_VALUE);
    assertEquals(1, one.speakers());
    assertEquals(1, one.files());
    assertEquals(1, one.entries());
    assertEquals(1, one.audio());
    assertEquals(1, one.links());
    assertEquals(Integer.MAX_VALUE, max.speakers());
    assertEquals(Integer.MAX_VALUE, max.files());
    assertEquals(Integer.MAX_VALUE, max.entries());
    assertEquals(Integer.MAX_VALUE, max.audio());
    assertEquals(Integer.MAX_VALUE, max.links());
    assertEquals("SourceCounts[speakers=1, files=1, entries=1, audio=1, links=1]", one.toString());
    assertEquals(954305, one.hashCode());
    assertEquals(0, zero.hashCode());
    assertEquals(one, one);
    assertEquals(one, same);
    assertFalse(one.equals(null));
    assertFalse(one.equals(new Object()));
    for (int index = 0; index < 5; index++)
      assertNotEquals(
          one,
          new CurrentMigrationTransfer.SourceCounts(
              index == 0 ? 2 : 1,
              index == 1 ? 2 : 1,
              index == 2 ? 2 : 1,
              index == 3 ? 2 : 1,
              index == 4 ? 2 : 1));
  }

  @Test
  void transfer019StatelessReuseKeepsIndependentResourcesAndRedaction() throws Exception {
    var job = new CurrentMigrationTransfer();
    for (int i = 0; i < 2; i++) {
      var source = source();
      var target = target();
      var result =
          job.transfer(
              source.connection(),
              target.connection(),
              assembler(false),
              counts(1),
              media(),
              Instant.parse(STAMP),
              (c, t, rows) -> rows.size());
      assertEquals(NORMAL_HASH, result.sha256());
      assertEquals(95, target.sql.size());
      assertEquals(10, source.closes.size());
    }
    assertEquals("CurrentMigrationTransfer[REDACTED]", job.toString());
  }

  @Test
  void transfer020FiniteParallelCallsNeverShareConnectionsOrMutableRows() throws Exception {
    var job = new CurrentMigrationTransfer();
    var a = assembler(false);
    var media = List.copyOf(media());
    var at = Instant.parse(STAMP);
    var count = counts(1);
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<String>>();
      for (int i = 0; i < TASKS; i++)
        futures.add(
            executor.submit(
                () -> {
                  var source = source();
                  var target = target();
                  return job.transfer(
                          source.connection(),
                          target.connection(),
                          a,
                          count,
                          media,
                          at,
                          (c, t, rows) -> rows.size())
                      .sha256();
                }));
      for (var future : futures)
        assertEquals(NORMAL_HASH, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static byte[] digest(byte[] bytes) {
    try {
      return MessageDigest.getInstance("SHA-256").digest(bytes);
    } catch (NoSuchAlgorithmException missing) {
      throw new AssertionError(missing);
    }
  }

  private static MigrationCopyPort forbidden() {
    return (c, t, rows) -> {
      throw new AssertionError(UNEXPECTED_COPY);
    };
  }

  private static CurrentMigrationTransfer.SourceCounts counts(int n) {
    return new CurrentMigrationTransfer.SourceCounts(n, n, n, n, n);
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException(SYNTHETIC),
        new IllegalStateException(SYNTHETIC),
        new AssertionError(SYNTHETIC));
  }

  private static List<Throwable> copyFailures() {
    var result = new ArrayList<>(failures());
    result.add(new IOException(SYNTHETIC));
    return result;
  }

  private static MigrationMasterCopyManifest invoke(
      CurrentMigrationProjectionTest.Fixture source,
      MigrationMasterTargetPublisherTest.Fixture target,
      MigrationCopyPort copy)
      throws Exception {
    return new CurrentMigrationTransfer()
        .transfer(
            source.connection(),
            target.connection(),
            assembler(false),
            counts(1),
            media(),
            Instant.parse(STAMP),
            copy);
  }

  private static CurrentMigrationProjectionTest.Fixture empty() {
    var f = new CurrentMigrationProjectionTest.Fixture();
    for (int i = 0; i < 5; i++) f.tables.add(new ArrayList<>());
    return f;
  }

  private static CurrentMigrationProjectionTest.Fixture source() {
    var f = empty();
    f.tables.get(0).add(new Object[] {-2L, 1, "Alice", "alice", true, null});
    f.tables.get(1).add(new Object[] {10L, 1, FILE, FILE, null, "chapter", HASH, 3L});
    f.tables.get(2).add(new Object[] {20L, 1, 10L, 0, 1, "dialogue", -2L, null, "hello", "raw"});
    f.tables
        .get(3)
        .add(
            new Object[] {
              -5L, 1, AUDIO, AUDIO, "a", VOICE, "ogg", new BigDecimal("1.2"), 3L, HASH
            });
    f.tables.get(4).add(new Object[] {20L, -5L, VOICE});
    return f;
  }

  private static MigrationMasterTargetPublisherTest.Fixture target() {
    var f = MigrationMasterTargetPublisherTest.coordinatorFixture(false);
    f.transferContent.put(
        2,
        Arrays.asList(
            "900", ONE, "700", ONE, "0", ONE, "dialogue", "42", null, "hello", "raw", STAMP));
    f.transferContent.put(
        3,
        Arrays.asList(
            "500", ONE, "voice/a.ogg", AUDIO, AUDIO, "a", VOICE, "ogg", "1200", "3", HASH, STAMP));
    return f;
  }

  private static CurrentMigrationAssembler assembler(boolean empty) {
    var files =
        new ScenarioFileMigrationMap(
            empty ? List.of() : List.of(new ScenarioFileMigrationMap.FilePair(1, 10, 700)));
    var entries =
        new ScenarioEntryMigrationMap(
            empty ? List.of() : List.of(new ScenarioEntryMigrationMap.IdPair(20, 900)));
    var placement =
        new ScenarioEntryPlacementMap(
            files,
            entries,
            empty ? List.of() : List.of(new ScenarioEntryPlacementMap.Placement(1, 10, 20, 0)));
    var speakers =
        new SpeakerMigrationMap(
            empty ? List.of() : List.of(new SpeakerMigrationMap.SpeakerMapping(1, -2, 42)));
    var assets =
        new AssetMigrationManifest(
            empty
                ? List.of()
                : List.of(
                    new AssetMigrationManifest.Entry(
                        AssetMigrationManifest.Kind.SCENARIO,
                        "g1/file.txt",
                        "script/file.txt",
                        3,
                        HASH),
                    new AssetMigrationManifest.Entry(
                        AssetMigrationManifest.Kind.AUDIO, "g1/a.ogg", "voice/a.ogg", 3, HASH),
                    new AssetMigrationManifest.Entry(
                        AssetMigrationManifest.Kind.VIDEO,
                        "current/a.mp4",
                        "video/a.mp4",
                        3,
                        HASH)));
    return new CurrentMigrationAssembler(
        files,
        placement,
        speakers,
        empty ? List.of() : List.of(new AudioMigrationMap.AudioMapping(1, -5, 500)),
        empty ? List.of() : List.of(new CurrentAudioLinkMapper.LinkOrder(20, -5, VOICE, 1)),
        assets,
        "g1",
        "g2");
  }

  private static List<@Nullable MediaAssetCopyRow> media() throws NoSuchAlgorithmException {
    return List.of(
        new MediaAssetCopyRow(
            Arrays.asList(
                "600",
                "video-a",
                "VIDEO",
                "A",
                "MAIN",
                null,
                "video/a.mp4",
                "current/a.mp4",
                "a.mp4",
                "3",
                HASH,
                "video/mp4",
                null,
                null,
                null,
                ONE,
                STAMP)));
  }
}
