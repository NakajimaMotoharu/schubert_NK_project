package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayOutputStream;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.postgresql.PGConnection;
import org.postgresql.copy.CopyIn;
import org.postgresql.copy.CopyManager;
import org.postgresql.core.BaseConnection;
import org.postgresql.core.Encoding;
import org.postgresql.core.QueryExecutor;
import org.postgresql.util.ByteStreamWriter;

/**
 * PT-MIG-PGCOPY001..024 FUTURE SOURCE ONLY: all NOT_RUN_HOLD in SSC417. No SDK
 * class/ABI/compiler/dynamic admission; do not run through an alternative path or stub SDK. Source
 * parsing/review is not PT PASS or measured coverage. All data below are synthetic literals.
 */
final class PostgresMigrationCopyPortTest {
  private static final String INPUT_ERROR = "migration PostgreSQL COPY input is invalid";
  private static final String TRANSPORT_ERROR =
      "migration PostgreSQL COPY transport is unavailable";
  private static final String SYNTHETIC = "synthetic copy fault";
  private static final String SPEAKERS = "pg_temp.nk_mig_speakers";
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final List<String> TABLES =
      List.of(
          "pg_temp.nk_mig_speakers",
          "pg_temp.nk_mig_script_files",
          "pg_temp.nk_mig_script_entries",
          "pg_temp.nk_mig_audio_files",
          "pg_temp.nk_mig_media_assets",
          "pg_temp.nk_mig_entry_audio_links");
  private static final List<String> SQL =
      List.of(
          "COPY pg_temp.nk_mig_speakers (id, game_id, name, normalized_name, is_protagonist, notes, created_at) FROM STDIN WITH (FORMAT text, DELIMITER E'\\t', NULL E'\\\\N', ENCODING 'UTF8')",
          "COPY pg_temp.nk_mig_script_files (id, game_id, display_order, storage_relative_path, display_path, file_name, section_code, chapter_title, sha256, byte_size, created_at) FROM STDIN WITH (FORMAT text, DELIMITER E'\\t', NULL E'\\\\N', ENCODING 'UTF8')",
          "COPY pg_temp.nk_mig_script_entries (id, game_id, script_file_id, display_order, entry_index, line_number, entry_type, speaker_id, speaker_label, body, raw_block, created_at) FROM STDIN WITH (FORMAT text, DELIMITER E'\\t', NULL E'\\\\N', ENCODING 'UTF8')",
          "COPY pg_temp.nk_mig_audio_files (id, game_id, storage_relative_path, display_path, file_name, basename, audio_role, container, duration_ms, byte_size, sha256, created_at) FROM STDIN WITH (FORMAT text, DELIMITER E'\\t', NULL E'\\\\N', ENCODING 'UTF8')",
          "COPY pg_temp.nk_mig_media_assets (id, logical_id, media_type, title, category, section, storage_relative_path, display_path, file_name, byte_size, sha256, mime_type, parent_logical_id, pair_key, pair_role, display_order, created_at) FROM STDIN WITH (FORMAT text, DELIMITER E'\\t', NULL E'\\\\N', ENCODING 'UTF8')",
          "COPY pg_temp.nk_mig_entry_audio_links (entry_id, audio_file_id, game_id, link_type, display_order, created_at) FROM STDIN WITH (FORMAT text, DELIMITER E'\\t', NULL E'\\\\N', ENCODING 'UTF8')");
  private static final List<List<@Nullable String>> ROWS =
      List.of(
          Arrays.<@Nullable String>asList(
              "42", "1", "Alice", "alice", "true", null, "2026-01-02T03:04:05Z"),
          Arrays.<@Nullable String>asList(
              "700",
              "1",
              "1",
              "script/file.txt",
              "file.txt",
              "file.txt",
              null,
              "chapter",
              "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
              "3",
              "2026-01-02T03:04:05Z"),
          Arrays.<@Nullable String>asList(
              "900",
              "1",
              "700",
              "1",
              "0",
              null,
              "dialogue",
              "42",
              null,
              "hello",
              "raw",
              "2026-01-02T03:04:05Z"),
          Arrays.<@Nullable String>asList(
              "500",
              "1",
              "voice/a.ogg",
              "表示",
              "a.ogg",
              "a",
              "voice",
              "ogg",
              "1200",
              "3",
              "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
              "2026-01-02T03:04:05Z"),
          Arrays.<@Nullable String>asList(
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
              "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
              "video/mp4",
              null,
              null,
              null,
              "1",
              "2026-01-02T03:04:05Z"),
          Arrays.<@Nullable String>asList("900", "500", "1", "voice", "1", "2026-01-02T03:04:05Z"));
  private static final List<String> WIRE =
      List.of(
          "42\t1\tAlice\talice\ttrue\t\\N\t2026-01-02T03:04:05Z\n",
          "700\t1\t1\tscript/file.txt\tfile.txt\tfile.txt\t\\N\tchapter\tba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\t3\t2026-01-02T03:04:05Z\n",
          "900\t1\t700\t1\t0\t\\N\tdialogue\t42\t\\N\thello\traw\t2026-01-02T03:04:05Z\n",
          "500\t1\tvoice/a.ogg\t表示\ta.ogg\ta\tvoice\togg\t1200\t3\tba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\t2026-01-02T03:04:05Z\n",
          "600\tvideo-a\tVIDEO\tA\tMAIN\t\\N\tvideo/a.mp4\tcurrent/a.mp4\ta.mp4\t3\tba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\tvideo/mp4\t\\N\t\\N\t\\N\t1\t2026-01-02T03:04:05Z\n",
          "900\t500\t1\tvoice\t1\t2026-01-02T03:04:05Z\n");

  @Test
  void pgcopy001FixedSixSqlAndIndependentWireBytes() throws Exception {
    var job = new PostgresMigrationCopyPort();
    for (int table = 0; table < TABLES.size(); table++) {
      var f = new Fixture();
      f.expectedSql = SQL.get(table);
      assertEquals(1L, job.copy(f.connection, TABLES.get(table), List.of(ROWS.get(table))));
      assertArrayEquals(
          WIRE.get(table).getBytes(StandardCharsets.UTF_8), f.copy.bytes.toByteArray());
      assertEquals(1, f.starts);
      assertEquals(1, f.copy.writes);
      assertEquals(1, f.copy.ends);
      assertEquals(0, f.copy.cancels);
      assertEquals(0, f.borrowedOperations);
    }
  }

  @Test
  void pgcopy002EmptyStillStartsAndEndsOneCopy() throws Exception {
    var f = new Fixture();
    f.copy.count = 0;
    assertEquals(0, new PostgresMigrationCopyPort().copy(f.connection, SPEAKERS, List.of()));
    assertEquals(1, f.starts);
    assertEquals(0, f.copy.writes);
    assertEquals(1, f.copy.ends);
    assertEquals(0, f.copy.cancels);
  }

  @Test
  void pgcopy003AllThreeNullsRejectBeforeVendorCalls() throws Exception {
    for (int missing = 0; missing < 3; missing++) {
      final int field = missing;
      var f = new Fixture();
      var rows = List.of(ROWS.getFirst());
      var x =
          assertThrows(
              IllegalArgumentException.class,
              () ->
                  new PostgresMigrationCopyPort()
                      .copy(
                          field == 0 ? null : f.connection,
                          field == 1 ? null : SPEAKERS,
                          field == 2 ? null : rows));
      assertEquals(INPUT_ERROR, x.getMessage());
      assertNull(x.getCause());
      assertEquals(0, f.portCalls);
    }
  }

  @Test
  void pgcopy004UnknownTableNeverBecomesGeneralSql() throws Exception {
    for (String table :
        List.of(
            "",
            SPEAKERS + " ",
            "PG_TEMP.NK_MIG_SPEAKERS",
            "schubert.speakers",
            SPEAKERS + ";",
            SPEAKERS + "\n")) {
      var f = new Fixture();
      assertEquals(
          INPUT_ERROR,
          assertThrows(
                  IllegalArgumentException.class,
                  () ->
                      new PostgresMigrationCopyPort()
                          .copy(f.connection, table, List.of(ROWS.getFirst())))
              .getMessage());
      assertEquals(0, f.portCalls);
      assertEquals(0, f.starts);
    }
  }

  @Test
  void pgcopy005AllWidthsAndNullRowRejectBeforeOwnership() throws Exception {
    for (int table = 0; table < TABLES.size(); table++)
      for (int delta : List.of(-1, 1)) {
        var f = new Fixture();
        final int t = table;
        var row = new ArrayList<@Nullable String>(ROWS.get(table));
        if (delta < 0) row.removeLast();
        else row.add("extra");
        assertThrows(
            IllegalArgumentException.class,
            () -> new PostgresMigrationCopyPort().copy(f.connection, TABLES.get(t), List.of(row)));
        assertEquals(0, f.portCalls);
      }
    var f = new Fixture();
    var nullRows = new ArrayList<@Nullable List<@Nullable String>>();
    nullRows.add(null);
    assertThrows(
        IllegalArgumentException.class,
        () -> new PostgresMigrationCopyPort().copy(f.connection, SPEAKERS, nullRows));
    assertEquals(0, f.portCalls);
    for (String table : TABLES) {
      var emptyRow = new Fixture();
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new PostgresMigrationCopyPort()
                  .copy(emptyRow.connection, table, List.of(List.<@Nullable String>of())));
      assertEquals(0, emptyRow.portCalls);
    }
    var changed = new Fixture();
    var row = new CaptureChangingRow(ROWS.getFirst());
    assertThrows(
        IllegalArgumentException.class,
        () -> new PostgresMigrationCopyPort().copy(changed.connection, SPEAKERS, List.of(row)));
    assertEquals(0, changed.portCalls);
  }

  @Test
  void pgcopy006AutocommitCannotStartCopy() throws Exception {
    var f = new Fixture();
    f.auto = true;
    unavailable(f);
    assertEquals(0, f.starts);
    assertEquals(0, f.copy.cancels);
  }

  @Test
  void pgcopy007ReadOnlyCannotStartCopy() throws Exception {
    var f = new Fixture();
    f.readOnly = true;
    unavailable(f);
    assertEquals(0, f.starts);
    assertEquals(0, f.copy.cancels);
  }

  @Test
  void pgcopy008AttributeFaultsKeepOriginalIdentity() throws Exception {
    for (String phase : List.of("getAutoCommit", "isReadOnly"))
      for (Throwable x : faults()) {
        var f = new Fixture();
        f.phase = phase;
        f.fault = x;
        sameFailure(f, x);
        assertEquals(0, f.starts);
        assertEquals(0, f.copy.cancels);
      }
  }

  @Test
  void pgcopy009UnwrapNullOrFaultHasNoHandleToCancel() throws Exception {
    var nil = new Fixture();
    nil.nullPg = true;
    unavailable(nil);
    assertEquals(0, nil.starts);
    for (Throwable x : faults()) {
      var f = new Fixture();
      f.phase = "unwrap";
      f.fault = x;
      sameFailure(f, x);
      assertEquals(0, f.copy.cancels);
    }
  }

  @Test
  void pgcopy010ManagerNullOrFaultHasNoHandleToCancel() throws Exception {
    var nil = new Fixture();
    nil.nullManager = true;
    unavailable(nil);
    for (Throwable x : faults()) {
      var f = new Fixture();
      f.phase = "getCopyAPI";
      f.fault = x;
      sameFailure(f, x);
      assertEquals(0, f.copy.cancels);
    }
  }

  @Test
  void pgcopy011StartNullOrFaultIsNotAnOwnedCopy() throws Exception {
    var nil = new Fixture();
    nil.nullCopy = true;
    unavailable(nil);
    assertEquals(1, nil.starts);
    assertEquals(0, nil.copy.cancels);
    for (Throwable x : faults()) {
      var f = new Fixture();
      f.phase = "startCopy";
      f.fault = x;
      sameFailure(f, x);
      assertEquals(1, f.starts);
      assertEquals(0, f.copy.cancels);
    }
  }

  @Test
  void pgcopy012InactiveInitialHandleCannotReportSuccess() throws Exception {
    var f = new Fixture();
    f.copy.active = false;
    unavailable(f);
    assertEquals(0, f.copy.writes);
    assertEquals(0, f.copy.ends);
    assertEquals(0, f.copy.cancels);
  }

  @Test
  void pgcopy013EveryWritePositionAndFaultStopsBeforeEnd() throws Exception {
    for (int index = 0; index < 2; index++)
      for (Throwable x : faults()) {
        var f = new Fixture();
        f.copy.count = 2;
        f.copy.writeFault = x;
        f.copy.writeFaultAt = index;
        var rows = List.of(ROWS.getFirst(), ROWS.getFirst());
        assertSame(
            x,
            assertThrows(
                Throwable.class,
                () -> new PostgresMigrationCopyPort().copy(f.connection, SPEAKERS, rows)));
        assertEquals(index + 1, f.copy.writes);
        assertEquals(0, f.copy.ends);
        assertEquals(1, f.copy.cancels);
        assertEquals(0, x.getSuppressed().length);
      }
  }

  @Test
  void pgcopy014EncoderRejectionCancelsWithoutRepair() throws Exception {
    for (String bad : List.of("\uD800", "\u0000")) {
      var f = new Fixture();
      var row = new ArrayList<@Nullable String>(ROWS.getFirst());
      row.set(2, bad);
      assertEquals(
          "migration COPY text data is invalid",
          assertThrows(
                  IllegalArgumentException.class,
                  () -> new PostgresMigrationCopyPort().copy(f.connection, SPEAKERS, List.of(row)))
              .getMessage());
      assertEquals(0, f.copy.writes);
      assertEquals(0, f.copy.ends);
      assertEquals(1, f.copy.cancels);
    }
  }

  @Test
  void pgcopy015EndFaultDoesNotBecomeSuccessfulRowCount() throws Exception {
    for (Throwable x : faults()) {
      var f = new Fixture();
      f.copy.endFault = x;
      sameFailure(f, x);
      assertEquals(1, f.copy.ends);
      assertEquals(1, f.copy.cancels);
    }
  }

  @Test
  void pgcopy016WrongCountsCannotQualifyEvenAfterInactiveEnd() throws Exception {
    for (long count : List.of(-1L, 0L, 2L, Long.MAX_VALUE)) {
      var f = new Fixture();
      f.copy.count = count;
      unavailable(f);
      assertEquals(1, f.copy.ends);
      assertEquals(0, f.copy.cancels);
    }
  }

  @Test
  void pgcopy017ActiveAfterEndIsCancelledAndRejected() throws Exception {
    var f = new Fixture();
    f.copy.keepAfterEnd = true;
    unavailable(f);
    assertEquals(1, f.copy.ends);
    assertEquals(1, f.copy.cancels);
    assertTrue(!f.copy.active);
  }

  @Test
  void pgcopy018CleanupFaultMatrixKeepsPrimaryAndOneSuppressed() throws Exception {
    for (int primaryKind = 0; primaryKind < 3; primaryKind++)
      for (int cleanupKind = 0; cleanupKind < 3; cleanupKind++) {
        Throwable primary = faults().get(primaryKind);
        Throwable cleanup = faults().get(cleanupKind);
        var f = new Fixture();
        f.copy.writeFault = primary;
        f.copy.writeFaultAt = 0;
        f.copy.cancelFault = cleanup;
        sameFailure(f, primary);
        assertEquals(1, f.copy.cancels);
        assertEquals(1, primary.getSuppressed().length);
        assertSame(cleanup, primary.getSuppressed()[0]);
        assertEquals(0, f.copy.ends);
      }
  }

  @Test
  void pgcopy019CleanupSelfIdentityNeverCreatesSelfSuppression() throws Exception {
    for (Throwable x : faults()) {
      var f = new Fixture();
      f.copy.writeFault = x;
      f.copy.writeFaultAt = 0;
      f.copy.cancelFault = x;
      sameFailure(f, x);
      assertEquals(0, x.getSuppressed().length);
      assertEquals(1, f.copy.cancels);
    }
  }

  @Test
  void pgcopy020ActiveQueryAndUnfinishedCancelRemainFailures() throws Exception {
    for (Throwable x :
        List.of(new IllegalStateException(SYNTHETIC), new AssertionError(SYNTHETIC))) {
      var f = new Fixture();
      f.copy.activeFault = x;
      f.copy.activeFaultAt = 0;
      sameFailure(f, x);
      assertEquals(1, f.copy.cancels);
    }
    for (Throwable cleanup :
        List.of(new IllegalStateException(SYNTHETIC), new AssertionError(SYNTHETIC))) {
      var primary = new SQLException(SYNTHETIC);
      var f = new Fixture();
      f.copy.writeFault = primary;
      f.copy.writeFaultAt = 0;
      f.copy.activeFault = cleanup;
      f.copy.activeFaultAt = 1;
      sameFailure(f, primary);
      assertEquals(0, f.copy.cancels);
      assertEquals(1, primary.getSuppressed().length);
      assertSame(cleanup, primary.getSuppressed()[0]);
    }
    var primary = new SQLException(SYNTHETIC);
    var f = new Fixture();
    f.copy.writeFault = primary;
    f.copy.writeFaultAt = 0;
    f.copy.keepAfterCancel = true;
    sameFailure(f, primary);
    assertEquals(1, f.copy.cancels);
    assertEquals(1, primary.getSuppressed().length);
    assertEquals(TRANSPORT_ERROR, primary.getSuppressed()[0].getMessage());
  }

  @Test
  void pgcopy021DeepSnapshotPrecedesVendorCallbacksAndKeepsNull() throws Exception {
    var f = new Fixture();
    var row = new ArrayList<@Nullable String>(ROWS.getFirst());
    var rows = new ArrayList<List<@Nullable String>>();
    rows.add(row);
    f.onStart =
        () -> {
          row.set(2, "changed");
          rows.clear();
        };
    assertEquals(1, new PostgresMigrationCopyPort().copy(f.connection, SPEAKERS, rows));
    assertArrayEquals(WIRE.getFirst().getBytes(StandardCharsets.UTF_8), f.copy.bytes.toByteArray());
    assertTrue(WIRE.getFirst().contains("\\N"));
  }

  @Test
  void pgcopy022BorrowedConnectionAndFacadeAreNeverClosedOrReconfigured() throws Exception {
    var job = new PostgresMigrationCopyPort();
    for (int count = 0; count < 2; count++) {
      var f = new Fixture();
      assertEquals(1, job.copy(f.connection, SPEAKERS, List.of(ROWS.getFirst())));
      assertEquals(0, f.borrowedOperations);
      assertEquals(0, f.copy.flushes);
      assertEquals(0, f.copy.cancels);
    }
  }

  @Test
  void pgcopy023RedactionAndSqlOptionsAreFixedIndependentLiterals() throws Exception {
    assertEquals("PostgresMigrationCopyPort[REDACTED]", new PostgresMigrationCopyPort().toString());
    assertEquals(List.of(7, 11, 12, 12, 17, 6), ROWS.stream().map(List::size).toList());
    for (String sql : SQL) {
      assertTrue(sql.startsWith("COPY pg_temp.nk_mig_"));
      assertTrue(
          sql.endsWith(
              " FROM STDIN WITH (FORMAT text, DELIMITER E'\\t', NULL E'\\\\N', ENCODING 'UTF8')"));
      assertTrue(!sql.contains("body_norm"));
    }
  }

  @Test
  void pgcopy024FiniteConcurrentCallsUsePrivateSdkFixtures() throws Exception {
    var job = new PostgresMigrationCopyPort();
    var rows = List.of(ROWS.getFirst());
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<Long>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(
            executor.submit(
                () -> {
                  var f = new Fixture();
                  long count = job.copy(f.connection, SPEAKERS, rows);
                  assertArrayEquals(
                      WIRE.getFirst().getBytes(StandardCharsets.UTF_8), f.copy.bytes.toByteArray());
                  assertEquals(0, f.borrowedOperations);
                  return count;
                }));
      for (var future : futures)
        assertEquals(1L, future.get(WAIT_SECONDS, TimeUnit.SECONDS).longValue());
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static List<Throwable> faults() {
    return List.of(
        new SQLException(SYNTHETIC),
        new IllegalStateException(SYNTHETIC),
        new AssertionError(SYNTHETIC));
  }

  private static void raise(Throwable fault) throws SQLException {
    if (fault instanceof SQLException sql) throw sql;
    if (fault instanceof RuntimeException runtime) throw runtime;
    throw (Error) fault;
  }

  private static void unavailable(Fixture f) throws Exception {
    assertEquals(
        TRANSPORT_ERROR,
        assertThrows(
                SQLException.class,
                () ->
                    new PostgresMigrationCopyPort()
                        .copy(f.connection, SPEAKERS, List.of(ROWS.getFirst())))
            .getMessage());
  }

  private static void sameFailure(Fixture f, Throwable fault) throws Exception {
    assertSame(
        fault,
        assertThrows(
            Throwable.class,
            () ->
                new PostgresMigrationCopyPort()
                    .copy(f.connection, SPEAKERS, List.of(ROWS.getFirst()))));
    assertEquals(0, f.borrowedOperations);
  }

  private static final class Fixture {
    final MemoryCopy copy = new MemoryCopy();
    final BaseConnection connection;
    @Nullable CopyManager manager;
    @Nullable String phase;
    @Nullable Throwable fault;
    boolean auto;
    boolean readOnly;
    boolean nullPg;
    boolean nullManager;
    boolean nullCopy;
    int starts;
    int portCalls;
    int borrowedOperations;
    String expectedSql = SQL.getFirst();
    Runnable onStart = () -> {};

    Fixture() throws SQLException {
      QueryExecutor executor =
          (QueryExecutor)
              Proxy.newProxyInstance(
                  QueryExecutor.class.getClassLoader(),
                  new Class<?>[] {QueryExecutor.class},
                  (proxy, method, args) -> {
                    if (!method.getName().equals("startCopy"))
                      throw new AssertionError("unexpected QueryExecutor");
                    starts++;
                    assertEquals(expectedSql, args[0]);
                    assertEquals(false, args[1]);
                    hit("startCopy");
                    onStart.run();
                    return nullCopy ? null : copy;
                  });
      connection =
          (BaseConnection)
              Proxy.newProxyInstance(
                  BaseConnection.class.getClassLoader(),
                  new Class<?>[] {BaseConnection.class},
                  (proxy, method, args) -> {
                    String name = method.getName();
                    if (name.equals("getEncoding")) return Encoding.getJVMEncoding("UTF-8");
                    if (name.equals("getQueryExecutor")) return executor;
                    if (List.of("close", "commit", "rollback", "setAutoCommit", "setReadOnly")
                        .contains(name)) {
                      borrowedOperations++;
                      throw new AssertionError("unexpected borrowed owner operation");
                    }
                    portCalls++;
                    hit(name);
                    return switch (name) {
                      case "getAutoCommit" -> auto;
                      case "isReadOnly" -> readOnly;
                      case "unwrap" -> {
                        assertSame(PGConnection.class, args[0]);
                        yield nullPg ? null : proxy;
                      }
                      case "getCopyAPI" -> nullManager ? null : manager;
                      default -> throw new AssertionError("unexpected connection call " + name);
                    };
                  });
      manager = new CopyManager(connection);
    }

    private void hit(String name) throws SQLException {
      if (name.equals(phase)) {
        assertTrue(fault != null);
        raise(fault);
      }
    }
  }

  private static final class CaptureChangingRow extends ArrayList<@Nullable String> {
    private static final long serialVersionUID = 1L;

    CaptureChangingRow(List<@Nullable String> values) {
      super(values);
    }

    @Override
    public Object[] toArray() {
      removeLast();
      return super.toArray();
    }
  }

  private static final class MemoryCopy implements CopyIn {
    final ByteArrayOutputStream bytes = new ByteArrayOutputStream();
    boolean active = true;
    long count = 1;
    boolean keepAfterEnd;
    boolean keepAfterCancel;
    int writes;
    int ends;
    int cancels;
    int flushes;
    int activeReads;
    int writeFaultAt = -1;
    int activeFaultAt = -1;
    @Nullable Throwable writeFault;
    @Nullable Throwable endFault;
    @Nullable Throwable cancelFault;
    @Nullable Throwable activeFault;

    @Override
    public void writeToCopy(byte[] buf, int off, int size) throws SQLException {
      int index = writes;
      writes++;
      if (index == writeFaultAt && writeFault != null) raise(writeFault);
      bytes.write(buf, off, size);
    }

    @Override
    public void writeToCopy(ByteStreamWriter from) throws SQLException {
      throw new AssertionError("unexpected ByteStreamWriter");
    }

    @Override
    public void flushCopy() throws SQLException {
      flushes++;
      throw new AssertionError("unexpected flushCopy");
    }

    @Override
    public long endCopy() throws SQLException {
      ends++;
      if (endFault != null) raise(endFault);
      active = keepAfterEnd;
      return count;
    }

    @Override
    public void cancelCopy() throws SQLException {
      cancels++;
      if (cancelFault != null) raise(cancelFault);
      active = keepAfterCancel;
    }

    @Override
    public boolean isActive() {
      int index = activeReads;
      activeReads++;
      if (index == activeFaultAt && activeFault != null) {
        if (activeFault instanceof RuntimeException runtime) throw runtime;
        throw (Error) activeFault;
      }
      return active;
    }

    @Override
    public int getFieldCount() {
      return 7;
    }

    @Override
    public int getFormat() {
      return 0;
    }

    @Override
    public int getFieldFormat(int field) {
      return 0;
    }

    @Override
    public long getHandledRowCount() {
      return count;
    }
  }
}
