package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.messaging.outbound.SqlConnectionProvider;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-DB-INBOX-081..088; SS324 12.6/331 3.8; PG-D-128; independent wire/JCE and real SQL. */
final class InboxInspectionProgressTest {
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static final Instant TIME = Instant.parse("2026-09-09T00:00:00.123Z");
  private static final InspectionRun RUN =
      new InspectionRun(new UUID(0, 71), Instant.parse("2026-09-17T00:00:00.123Z"));
  private static final String OPEN = "maintenance_open_inbox_inspection";
  private static final String SAVE = "maintenance_record_inbox_inspection";
  private static final String TABLE = "schubert.inbox_inspection_progress";
  private static final InboxResultReference NONE = InboxResultReference.none();

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
    try (var c = db.api()) {
      url = c.getMetaData().getURL();
    }
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws SQLException {
    for (String table :
        List.of(
            TABLE,
            "schubert.request_inbox",
            "schubert.auth_sessions",
            "schubert.script_files",
            "schubert.batch_runs",
            "schubert.app_users")) sql("delete from " + table);
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at,version) values(7,'Learner','learner','synthetic-unused','USER','ACTIVE','2026-09-09','2026-09-09','2026-09-09',0),(9,'Target','target','synthetic-unused','USER','ACTIVE','2026-09-09','2026-09-09','2026-09-09',9)");
    sql(
        "insert into schubert.script_files(id,game_id,display_order,storage_relative_path,display_path,file_name,sha256,byte_size,created_at) values(11,1,1,'scenario/one.txt','one','one.txt',repeat('a',64),12,'2026-09-09')");
    for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG"))
      sql(
          "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status) values('"
              + RUN.id()
              + "','2026-09-17','"
              + step
              + "',1,'2026-09-17','2026-09-17','SUCCESS')");
  }

  @Test
  void mixedRowsPersistExactProgress() throws Exception {
    try (var f = new Fixture()) {
      seed(f, 1, "LGNRSP01", "0101", NONE, Map.of());
      seed(f, 2, "GAMRSP01", "0000", NONE, Map.of());
      seed(
          f,
          3,
          "UCRRSP01",
          "0000",
          InboxResultReference.numeric(InboxResultReferenceType.USER, 9),
          Map.of());
      seed(
          f,
          4,
          "SCNRSP01",
          "0000",
          InboxResultReference.numeric(InboxResultReferenceType.SCENARIO_FILE, 11),
          NonAuthenticationInboxInspectorTest.fileValues(1));
      seed(f, 5, "GAMRSP01", "0000", NONE, Map.of());
      seed(f, 6, "GAMRSP01", "0000", NONE, Map.of());
      sql(
          "update schubert.request_inbox set response_key_version='unknown' where message_id='"
              + id(5)
              + "'");
      sql(
          "update schubert.request_inbox set request_layout_id='ZZZREQ01',response_layout_id='ZZZRSP01' where message_id='"
              + id(6)
              + "'");
      String refs = references();
      assertEquals(progress(6, 6, 4, 2, true), f.service().runChunk(RUN, 1000));
      assertEquals(
          "5,6",
          scalar(
              "select string_agg(('x'||right(message_id::text,8))::bit(32)::int::text,',' order by message_id) from schubert.request_inbox"));
      assertEquals("6|4|2|true", stored());
      assertEquals(refs, references());
    }
  }

  @Test
  void boundedChunksResumeAndSkipCompleted() throws Exception {
    try (var f = new Fixture()) {
      seed(f, 1, "GAMRSP01", "0000", NONE, Map.of());
      seed(f, 2, "GAMRSP01", "0000", NONE, Map.of());
      assertEquals(progress(1, 1, 1, 0, false), f.service().runChunk(RUN, 1));
      assertEquals("1|1|0|false", stored());
      assertEquals(progress(2, 2, 2, 0, false), f.service().runChunk(RUN, 1));
      assertEquals(progress(2, 2, 2, 0, true), f.service().runChunk(RUN, 1000));
      var p = new MaintenanceJdbcProbe();
      p.selectedSql = "maintenance_next_inbox";
      p.fault = "executeQuery";
      assertEquals(progress(2, 2, 2, 0, true), f.service(p).runChunk(RUN, 1000));
      assertEquals(0, p.selectedStatements);
      assertEquals(1, p.commits);
      assertEquals(1, p.closes);
      reset();
      assertEquals(progress(0, 0, 0, 0, true), f.service().runChunk(RUN, 1));
      assertEquals(progress(0, 0, 0, 0, true), f.service().inspectStoredNext(RUN));
      reset();
      sql(
          "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,owner_user_id,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at) "
              + "select ('00000000-0000-0000-0000-'||lpad(to_hex(g),12,'0'))::uuid,('00000000-0000-0000-0000-'||lpad(to_hex(g),12,'0'))::uuid,'GAMREQ01','001',7,repeat('a',64),'v1','ERROR','NONE','GAMRSP01','001',decode(repeat('00',30),'hex'),'unavailable','2026-09-09','2026-09-09','2026-09-10' from generate_series(1,1001) g");
      assertEquals(progress(1000, 1000, 0, 1000, false), f.service().runChunk(RUN, 1000));
      assertEquals("1000|0|1000|false", stored());
      assertEquals(progress(1001, 1001, 0, 1001, true), f.service().runChunk(RUN, 1000));
      assertEquals("1001|0|1001|true", stored());
      assertEquals("1001", inboxCount());
    }
  }

  /** PT-DB-INBOX-268: an unknown provider getter cannot persist a PROTECTED cursor. */
  @Test
  void providerIllegalArgumentCannotAdvanceStoredProgress() throws Exception {
    try (var f = new Fixture()) {
      seed(f, 1, "GAMRSP01", "0000", NONE, Map.of());
      var probe = new MaintenanceJdbcProbe();
      probe.runtimeColumn = "result_ref_type";
      redacted(() -> f.service(probe).inspectStoredNext(RUN));
      assertEquals(0, probe.commits);
      assertEquals(1, probe.rollbacks);
      assertEquals(1, probe.closes);
      assertEquals("1", inboxCount());
      assertEquals("0", progressCount());
      assertEquals(progress(1, 1, 1, 0, true), f.service().runChunk(RUN, 10));
      assertEquals("1|1|0|true", stored());
      assertEquals("0", inboxCount());
    }
  }

  @Test
  void progressAndBoundaryContracts() throws Exception {
    assertThrows(
        NullPointerException.class,
        () -> new InspectionProgress(null, Optional.empty(), 0, 0, 0, false));
    assertThrows(
        NullPointerException.class, () -> new InspectionProgress(RUN, null, 0, 0, 0, false));
    for (long[] values :
        new long[][] {{-1, 0, 0}, {1, -1, 2}, {1, 2, 0}, {1, 1, -1}, {1, 0, 0}, {0, 0, 0}})
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new InspectionProgress(
                  RUN, Optional.of(id(1)), values[0], values[1], values[2], false));
    assertThrows(
        IllegalArgumentException.class,
        () -> new InspectionProgress(RUN, Optional.empty(), 1, 1, 0, false));
    assertEquals(
        Long.MAX_VALUE,
        new InspectionProgress(RUN, Optional.of(id(1)), Long.MAX_VALUE, Long.MAX_VALUE, 0, false)
            .inspected());
    assertEquals(
        Long.MAX_VALUE,
        new InspectionProgress(RUN, Optional.of(id(1)), Long.MAX_VALUE, 0, Long.MAX_VALUE, true)
            .protectedRows());
    try (var f = new Fixture()) {
      assertThrows(NullPointerException.class, () -> f.service().inspectStoredNext(null));
      assertThrows(NullPointerException.class, () -> f.service().runChunk(null, 1));
      for (int limit : new int[] {Integer.MIN_VALUE, 0, 1001, Integer.MAX_VALUE})
        assertThrows(IllegalArgumentException.class, () -> f.service().runChunk(RUN, limit));
      for (String selected : List.of(OPEN, SAVE)) {
        for (String column :
            List.of(
                "run_id",
                "cutoff",
                "inspected_count",
                "deleted_count",
                "protected_count",
                "inspection_xact")) {
          reset();
          seed(f, 1, "GAMRSP01", "0000", NONE, Map.of());
          var p = new MaintenanceJdbcProbe();
          p.selectedSql = selected;
          p.columns.put(column, null);
          redacted(() -> f.service(p).inspectStoredNext(RUN));
          assertTrue(p.selectedStatements > 0);
          assertEquals("1", inboxCount());
          assertEquals("0", progressCount());
        }
        for (var value :
            List.of(
                Map.entry("run_id", id(90)),
                Map.entry("cutoff", TIME.atOffset(java.time.ZoneOffset.UTC)),
                Map.entry("inspected_count", -1L),
                Map.entry("deleted_count", -1L),
                Map.entry("protected_count", -1L),
                Map.entry("inspection_xact", "x"),
                Map.entry("inspection_xact", "0".repeat(21)))) {
          reset();
          seed(f, 1, "GAMRSP01", "0000", NONE, Map.of());
          var p = new MaintenanceJdbcProbe();
          p.selectedSql = selected;
          p.columns.put(value.getKey(), value.getValue());
          redacted(() -> f.service(p).inspectStoredNext(RUN));
          assertEquals("1", inboxCount());
          assertEquals("0", progressCount());
        }
      }
    }
  }

  @Test
  void checkpointFaultsRollbackDeletion() throws Exception {
    try (var f = new Fixture()) {
      for (String selected : List.of(OPEN, SAVE)) {
        var faults =
            new ArrayList<>(
                List.of(
                    "prepareStatement",
                    "setObject",
                    "setObject#2",
                    "executeQuery",
                    "next",
                    "getObject",
                    "getObject#2",
                    "getString",
                    "resultClose",
                    "statementClose"));
        faults.addAll(
            List.of("getObject#3", "getObject#4", "getObject#5", "getObject#6", "getObject#7"));
        if (selected.equals(SAVE))
          faults.addAll(List.of("setLong", "setString", "setObject#3", "setObject#4"));
        for (String fault : faults) {
          reset();
          seed(f, 1, "GAMRSP01", "0000", NONE, Map.of());
          var p = new MaintenanceJdbcProbe();
          p.selectedSql = selected;
          p.fault = fault;
          redacted(() -> f.service(p).inspectStoredNext(RUN));
          assertTrue(p.selectedStatements > 0, selected + "/" + fault);
          assertEquals(0, p.commits);
          assertEquals(1, p.rollbacks);
          assertEquals(1, p.closes);
          assertEquals(0, p.saves);
          assertEquals("1", inboxCount());
          assertEquals("0", progressCount());
        }
        for (boolean empty : List.of(false, true)) {
          reset();
          seed(f, 1, "GAMRSP01", "0000", NONE, Map.of());
          var p = new MaintenanceJdbcProbe();
          p.selectedSql = selected;
          p.empty = empty;
          p.duplicate = !empty;
          redacted(() -> f.service(p).inspectStoredNext(RUN));
          assertEquals("1", inboxCount());
          assertEquals("0", progressCount());
          assertEquals(1, p.rollbacks);
        }
      }
    }
  }

  @Test
  void uncertainCommitReloadsDurableCounts() throws Exception {
    try (var f = new Fixture()) {
      for (String mode : List.of("before", "after", "close")) {
        reset();
        seed(f, 1, "GAMRSP01", "0000", NONE, Map.of());
        var p = new MaintenanceJdbcProbe();
        p.fault = mode.equals("close") ? "close" : "commit";
        p.commitAfter = mode.equals("after");
        redacted(() -> f.service(p).inspectStoredNext(RUN));
        assertEquals(mode.equals("before") ? "1" : "0", inboxCount());
        if (mode.equals("before")) assertEquals("0", progressCount());
        else assertEquals("1|1|0|false", stored());
        assertEquals(progress(1, 1, 1, 0, true), f.service().runChunk(RUN, 1000));
        assertEquals("1|1|0|true", stored());
        assertEquals("0", inboxCount());
      }
    }
  }

  @Test
  void ownsLocksWithoutSavepoints() throws Exception {
    try (var f = new Fixture()) {
      seed(
          f,
          1,
          "UCRRSP01",
          "0000",
          InboxResultReference.numeric(InboxResultReferenceType.USER, 9),
          Map.of());
      // First step checks candidate/reference/backup locks; the next checks the committed progress
      // row.
      var p = new MaintenanceJdbcProbe();
      p.beforeDelete =
          c -> {
            assertFalse(c.getAutoCommit());
            assertEquals(0, p.commits);
            assertEquals(0, p.saves);
            try (var other = db.admin()) {
              for (String query :
                  List.of(
                      "select id from schubert.app_users where id=9 for update nowait",
                      "select message_id from schubert.request_inbox for update nowait",
                      "select id from schubert.batch_runs where step='BACKUP_DB' for update nowait")) {
                assertEquals(
                    "55P03",
                    assertThrows(SQLException.class, () -> scalar(other, query)).getSQLState());
              }
            }
          };
      assertEquals(progress(1, 1, 1, 0, false), f.service(p).inspectStoredNext(RUN));
      assertEquals(1, p.deletes);
      assertEquals(1, p.commits);
      assertEquals(1, p.closes);
      assertEquals(0, p.saves);
      // Existing progress lock is observed while the next owned step is executing.
      seed(f, 2, "GAMRSP01", "0000", NONE, Map.of());
      var second = new MaintenanceJdbcProbe();
      second.beforeDelete =
          c -> {
            try (var other = db.admin()) {
              assertEquals(
                  "55P03",
                  assertThrows(
                          SQLException.class,
                          () -> scalar(other, "select run_id from " + TABLE + " for update nowait"))
                      .getSQLState());
            }
          };
      assertEquals(progress(2, 2, 2, 0, false), f.service(second).inspectStoredNext(RUN));
      assertEquals(1, second.commits);
      assertEquals(0, second.saves);
      for (String selected : List.of(OPEN, SAVE, "inspection_health")) {
        reset();
        seed(f, 1, "GAMRSP01", "0000", NONE, Map.of());
        var bad = new MaintenanceJdbcProbe();
        bad.selectedSql = selected;
        bad.fault = "aborted";
        redacted(() -> f.service(bad).inspectStoredNext(RUN));
        assertEquals("1", inboxCount());
        assertEquals("0", progressCount());
      }
    }
  }

  @Test
  void concurrentAttemptsNeverDoubleCount() throws Exception {
    try (var f = new Fixture();
        var pool = Executors.newFixedThreadPool(12)) {
      seed(f, 1, "GAMRSP01", "0000", NONE, Map.of());
      seed(f, 2, "GAMRSP01", "0000", NONE, Map.of());
      sql(
          "update schubert.request_inbox set response_key_version='missing' where message_id='"
              + id(2)
              + "'");
      int calls = 0;
      for (int size : new int[] {33, 33, 34}) {
        var tasks = new ArrayList<Callable<Optional<InspectionProgress>>>();
        for (int index = 0; index < size; index++)
          tasks.add(
              () -> {
                var p = new MaintenanceJdbcProbe();
                p.selectedSql = OPEN;
                try {
                  return Optional.of(f.service(p).inspectStoredNext(RUN));
                } catch (InboxMaintenanceException failure) {
                  assertEquals("55P03", p.lastSqlState);
                  return Optional.empty();
                } finally {
                  assertEquals(1, p.closes);
                  assertEquals(0, p.saves);
                }
              });
        for (var future : pool.invokeAll(tasks)) {
          var result = future.get();
          calls++;
          result.ifPresent(
              value -> {
                assertTrue(value.inspected() >= 1 && value.inspected() <= 2);
                assertEquals(1, value.deleted());
              });
        }
      }
      assertEquals(100, calls);
      assertEquals(progress(2, 2, 1, 1, true), f.service().inspectStoredNext(RUN));
      assertEquals("2|1|1|true", stored());
      assertEquals("1", inboxCount());
    }
  }

  @Test
  void runIdentityKeysAndResultsStayPrivate() throws Exception {
    try (var f = new Fixture()) {
      seed(f, 1, "GAMRSP01", "0000", NONE, Map.of());
      f.service().runChunk(RUN, 1);
      redacted(
          () ->
              f.service()
                  .inspectStoredNext(new InspectionRun(RUN.id(), RUN.cutoff().plusSeconds(1))));
      redacted(() -> f.service().inspectStoredNext(new InspectionRun(id(99), RUN.cutoff())));
      var value = f.service().inspectStoredNext(RUN);
      assertEquals(
          "InspectionProgress[inspected=1, deleted=1, protected=0, complete=true]",
          value.toString());
      assertEquals(RUN, value.run());
      assertEquals(Optional.of(id(1)), value.cursor());
      assertEquals(0, value.protectedRows());
      assertTrue(value.complete());
      assertFalse(value.toString().contains(RUN.id().toString()));
      assertFalse(value.toString().contains(f.base.raw));
      reset();
      seed(f, 1, "GAMRSP01", "0000", NONE, Map.of());
      f.base.snapshots.close();
      assertEquals(progress(1, 1, 0, 1, true), f.service().runChunk(RUN, 1000));
      assertEquals("1", inboxCount());
      assertEquals("1|0|1|true", stored());
    }
  }

  private static UUID id(long value) {
    return new UUID(0, value);
  }

  private static InspectionProgress progress(
      long after, long inspected, long deleted, long held, boolean complete) {
    return new InspectionProgress(
        RUN,
        after == 0 ? Optional.empty() : Optional.of(id(after)),
        inspected,
        deleted,
        held,
        complete);
  }

  private static Connection connection() throws SQLException {
    return DriverManager.getConnection(url, "schubert_inbox_inspector", "");
  }

  private static void sql(String q) throws SQLException {
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute(q);
    }
  }

  private static String scalar(String q) throws SQLException {
    try (var c = db.admin()) {
      return scalar(c, q);
    }
  }

  private static String scalar(Connection c, String q) throws SQLException {
    try (var s = c.createStatement();
        var r = s.executeQuery(q)) {
      assertTrue(r.next());
      String value = r.getString(1);
      assertNotNull(value);
      assertFalse(r.next());
      return value;
    }
  }

  private static String stored() throws SQLException {
    return scalar(
        "select inspected_count||'|'||deleted_count||'|'||protected_count||'|'||(completed_at is not null)::text from "
            + TABLE);
  }

  private static String progressCount() throws SQLException {
    return scalar("select count(*) from " + TABLE);
  }

  private static String inboxCount() throws SQLException {
    return scalar("select count(*) from schubert.request_inbox");
  }

  private static String references() throws SQLException {
    return scalar(
        "select (select string_agg(id||':'||version,',' order by id) from schubert.app_users)||'|'||(select count(*) from schubert.script_files)||'|'||(select count(*) from schubert.batch_runs)");
  }

  private static void redacted(Runnable action) {
    var error = assertThrows(InboxMaintenanceException.class, action::run);
    assertEquals("Inbox maintenance did not complete; resume the same run", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  private static void seed(
      Fixture f,
      long sequence,
      String layout,
      String code,
      InboxResultReference ref,
      Map<String, String> overrides)
      throws Exception {
    UUID message = id(sequence);
    boolean login = layout.equals("LGNRSP01");
    boolean mutation = layout.equals("UCRRSP01");
    var identity =
        login
            ? ResponseSnapshotIdentity.anonymous(message, layout, "001")
            : ResponseSnapshotIdentity.authenticated(message, layout, "001", 7);
    byte[] wire =
        login
            ? f.base.wire(identity, code)
            : NonAuthenticationInboxInspectorTest.wire(layout, code, overrides, 0);
    byte[] correlation = message.toString().getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(correlation, 0, wire, 60, 36);
    var saved =
        f.base.savedBytes(
            identity,
            wire,
            code.equals("0000") ? InboxCompletionState.COMPLETED : InboxCompletionState.ERROR,
            ref);
    assertTrue(
        new InboxResponseInspector(f.base.snapshots).isStructurallyValid(identity, saved),
        "independent seed wire");
    byte[] cipher = saved.responseSnapshot().orElseThrow().ciphertext();
    try (var c = db.api();
        var s =
            c.prepareStatement(
                "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,owner_user_id,operation_token,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,result_ref_id,result_ref_uuid,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at) values(?,?,?,'001',?,?,repeat('a',64),'v1',?,?,?,?,?,'001',?,'s1',?,?,?)")) {
      s.setObject(1, message);
      s.setObject(2, message);
      s.setString(3, layout.substring(0, 3) + "REQ01");
      s.setObject(4, login ? null : 7L);
      s.setObject(5, mutation ? id(1000 + sequence) : null);
      s.setString(6, saved.state().name());
      s.setString(7, ref.type().name());
      s.setObject(8, ref.numericId().isPresent() ? ref.numericId().getAsLong() : null);
      s.setObject(9, ref.uuid().orElse(null));
      s.setString(10, layout);
      s.setBytes(11, cipher);
      s.setObject(12, TIME.minusMillis(1).atOffset(java.time.ZoneOffset.UTC));
      s.setObject(13, TIME.atOffset(java.time.ZoneOffset.UTC));
      s.setObject(
          14,
          TIME.plusSeconds(login || mutation ? 604800 : 86400).atOffset(java.time.ZoneOffset.UTC));
      assertEquals(1, s.executeUpdate());
    } finally {
      Arrays.fill(cipher, (byte) 0);
    }
  }

  private static final class Fixture implements AutoCloseable {
    final AuthenticationInboxInspectorTest.Fixture base =
        new AuthenticationInboxInspectorTest.Fixture();

    Fixture() throws Exception {}

    InboxCleanup service() {
      return service(InboxInspectionProgressTest::connection);
    }

    InboxCleanup service(MaintenanceJdbcProbe probe) {
      return service(() -> probe.wrap(connection()));
    }

    InboxCleanup service(SqlConnectionProvider connections) {
      return new InboxCleanup(
          connections,
          base.inspector,
          new NonAuthenticationInboxInspector(base.snapshots),
          Set.of("v1"));
    }

    @Override
    public void close() {
      base.close();
    }
  }
}
