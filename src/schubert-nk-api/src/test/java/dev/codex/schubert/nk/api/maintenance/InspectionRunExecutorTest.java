package dev.codex.schubert.nk.api.maintenance;

import static dev.codex.schubert.nk.api.maintenance.InspectionExecution.Status.INTERRUPTED;
import static dev.codex.schubert.nk.api.maintenance.InspectionExecution.Status.STORAGE_FAILURE;
import static dev.codex.schubert.nk.api.maintenance.InspectionExecution.Status.SUCCESS;
import static dev.codex.schubert.nk.api.maintenance.InspectionExecution.Status.TIME_LIMIT;
import static dev.codex.schubert.nk.api.maintenance.InspectionExecution.Status.WARNING;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.messaging.outbound.SqlConnectionProvider;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.LongSupplier;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-DB-INBOX-097..104; PG-D-130; real PG, independent JCE and literal clock/SQL postconditions.
 */
final class InspectionRunExecutorTest {
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static final InspectionRun RUN =
      new InspectionRun(new UUID(0, 91), Instant.parse("2026-09-17T00:00:00Z"));
  private static final long LIMIT = 1_800_000_000_000L;

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
  void reset() throws Exception {
    sql("delete from schubert.inbox_inspection_progress");
    sql("delete from schubert.request_inbox");
    sql("delete from schubert.batch_runs");
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) values(7,'Learner','learner','synthetic-unused','USER','ACTIVE','2026-09-01','2026-09-01','2026-09-01') on conflict(id) do nothing");
    for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG"))
      sql(
          "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status) values('"
              + RUN.id()
              + "','2026-09-17','"
              + step
              + "',1,'2026-09-17','2026-09-17','SUCCESS')");
  }

  @Test
  void own001ParentCheckSuccessAndLossHaveIndependentSqlPostconditions() throws Exception {
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      AtomicInteger checked = new AtomicInteger();
      var guarded =
          new InspectionRunExecutor(
              service(f, InspectionRunExecutorTest::connection),
              () -> 0,
              Optional.of(
                  () -> {
                    checked.incrementAndGet();
                    return LIMIT;
                  }));
      assertEquals(
          new InspectionExecution(SUCCESS, Optional.of(progress(0, 0, true))), guarded.run(RUN));
      assertEquals(2, checked.get());
      assertEquals("0|0|0|true", stored());
      reset();
      AtomicInteger connections = new AtomicInteger();
      var denied =
          new InspectionRunExecutor(
              service(
                  f,
                  () -> {
                    connections.incrementAndGet();
                    return connection();
                  }),
              () -> 0,
              Optional.of(
                  () -> {
                    throw new java.io.IOException("synthetic parent unavailable");
                  }));
      assertEquals(new InspectionExecution(TIME_LIMIT, Optional.empty()), denied.run(RUN));
      assertEquals(0, connections.get());
      assertEquals("0", progressCount());
      assertEquals("0", inboxCount());
      assertThrows(
          NullPointerException.class,
          () ->
              new InspectionRunExecutor(
                  service(f, InspectionRunExecutorTest::connection), () -> 0, null));
    }
  }

  @Test
  void emptyAndCompletedRunsSucceed() throws Exception {
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      var result = executor(f, () -> 0).run(RUN);
      assertEquals(new InspectionExecution(SUCCESS, Optional.of(progress(0, 0, true))), result);
      assertEquals(0, result.exitCode());
      assertEquals("0|0|0|true", stored());
      var probe = new MaintenanceJdbcProbe();
      probe.fault = "executeQuery";
      assertEquals(
          result,
          new InspectionRunExecutor(service(f, () -> probe.wrap(connection())), () -> 0).run(RUN));
      assertEquals(0, probe.selectedStatements);
      assertEquals(1, probe.commits);
      assertEquals(1, probe.closes);
      reset();
      validLoginError(f);
      result = executor(f, () -> 0).run(RUN);
      assertEquals(SUCCESS, result.status());
      assertEquals(1, result.lastConfirmed().orElseThrow().deleted());
      assertEquals("1|1|0|true", stored());
      assertEquals("0", inboxCount());
    }
  }

  @Test
  void protectedRowsEndWithWarning() throws Exception {
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      invalidRows(2);
      sql(
          "update schubert.request_inbox set request_layout_id='ZZZREQ01',response_layout_id='ZZZRSP01' where message_id='"
              + new UUID(0, 2)
              + "'");
      var result = executor(f, () -> 0).run(RUN);
      assertEquals(new InspectionExecution(WARNING, Optional.of(progress(2, 2, true))), result);
      assertEquals(10, result.exitCode());
      assertEquals("2", inboxCount());
      assertEquals("2|0|2|true", stored());
    }
  }

  @Test
  void moreThanOneChunkCompletes() throws Exception {
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      invalidRows(1001);
      AtomicInteger opened = new AtomicInteger();
      var runner =
          new InspectionRunExecutor(
              service(
                  f,
                  () -> {
                    opened.incrementAndGet();
                    return connection();
                  }),
              () -> 0);
      var result = runner.run(RUN);
      assertEquals(WARNING, result.status());
      assertEquals(1002, opened.get());
      assertEquals(progress(1001, 1001, true), result.lastConfirmed().orElseThrow());
      assertEquals("1001|0|1001|true", stored());
      assertEquals("1001", inboxCount());
    }
  }

  @Test
  void deadlineAndClockBoundaries() throws Exception {
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      for (long boundary : new long[] {LIMIT, LIMIT + 1, -1}) {
        var result = executor(f, ticks(0, boundary)).run(RUN);
        assertEquals(new InspectionExecution(TIME_LIMIT, Optional.empty()), result);
        assertEquals(50, result.exitCode());
        assertEquals("0", progressCount());
      }
      assertEquals(SUCCESS, executor(f, ticks(0, 0, LIMIT - 1)).run(RUN).status());
      for (long boundary : new long[] {LIMIT, LIMIT + 1, -1}) {
        var result = executor(f, ticks(0, 0, boundary)).run(RUN);
        assertEquals(TIME_LIMIT, result.status());
        assertEquals(progress(0, 0, true), result.lastConfirmed().orElseThrow());
      }
      assertEquals(
          SUCCESS,
          executor(f, ticks(Long.MAX_VALUE - 5, Long.MAX_VALUE - 1, Long.MIN_VALUE + 5))
              .run(RUN)
              .status());
      reset();
      invalidRows(1001);
      var result = executor(f, ticks(0, 0, 1, LIMIT)).run(RUN);
      assertEquals(TIME_LIMIT, result.status());
      assertEquals(progress(1000, 1000, false), result.lastConfirmed().orElseThrow());
      assertEquals("1000|0|1000|false", stored());
      assertEquals("1001", inboxCount());
      assertEquals(WARNING, executor(f, () -> 0).run(RUN).status());
      assertEquals("1001|0|1001|true", stored());
    }
  }

  @Test
  void interruptionRemainsVisible() throws Exception {
    // BUG186/YKT146: empty run uses start, pre-chunk and final post-chunk clock.
    for (int point = 1; point <= 3; point++) {
      reset();
      int selected = point;
      AtomicInteger calls = new AtomicInteger();
      try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
        LongSupplier time =
            () -> {
              if (calls.incrementAndGet() == selected) Thread.currentThread().interrupt();
              return 0;
            };
        try {
          var result = executor(f, time).run(RUN);
          assertEquals(INTERRUPTED, result.status());
          assertEquals(50, result.exitCode());
          assertEquals(
              selected == 3 ? Optional.of(progress(0, 0, true)) : Optional.empty(),
              result.lastConfirmed());
          assertTrue(Thread.currentThread().isInterrupted());
          assertEquals(selected, calls.get());
        } finally {
          Thread.interrupted();
        }
      }
      assertEquals(point == 3 ? "1" : "0", progressCount());
    }
    reset();
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      try {
        Thread.currentThread().interrupt();
        var result = executor(f, () -> 0).run(RUN);
        assertEquals(new InspectionExecution(INTERRUPTED, Optional.empty()), result);
        assertEquals(50, result.exitCode());
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        assertTrue(Thread.interrupted());
      }
      assertEquals("0", progressCount());
      var probe = new MaintenanceJdbcProbe();
      probe.afterClose = () -> Thread.currentThread().interrupt();
      try {
        var result =
            new InspectionRunExecutor(service(f, () -> probe.wrap(connection())), () -> 0).run(RUN);
        assertEquals(INTERRUPTED, result.status());
        assertEquals(progress(0, 0, true), result.lastConfirmed().orElseThrow());
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        assertTrue(Thread.interrupted());
      }
      assertEquals(1, probe.closes);
      assertEquals("0|0|0|true", stored());
    }
  }

  @Test
  void storageFailurePreservesLastConfirmedOnly() throws Exception {
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      var result =
          new InspectionRunExecutor(
                  service(
                      f,
                      () -> {
                        throw new SQLException("public fault marker", "08006");
                      }),
                  () -> 0)
              .run(RUN);
      assertEquals(new InspectionExecution(STORAGE_FAILURE, Optional.empty()), result);
      assertEquals(50, result.exitCode());
      assertEquals("0", progressCount());
      invalidRows(1001);
      AtomicInteger opened = new AtomicInteger();
      result =
          new InspectionRunExecutor(
                  service(
                      f,
                      () -> {
                        if (opened.incrementAndGet() == 1002)
                          throw new SQLException("public fault marker", "08006");
                        return connection();
                      }),
                  () -> 0)
              .run(RUN);
      assertEquals(STORAGE_FAILURE, result.status());
      assertEquals(1002, opened.get());
      assertEquals(progress(1000, 1000, false), result.lastConfirmed().orElseThrow());
      // The failed chunk had one successful transaction. Never mislabel the lower checkpoint as
      // current state.
      assertEquals("1001|0|1001|false", stored());
      result = executor(f, () -> 0).run(RUN);
      assertEquals(WARNING, result.status());
      assertEquals(progress(1001, 1001, true), result.lastConfirmed().orElseThrow());
      assertEquals("1001|0|1001|true", stored());
    }
  }

  @Test
  void resultAndNullContracts() throws Exception {
    assertThrows(NullPointerException.class, () -> new InspectionExecution(null, Optional.empty()));
    assertThrows(NullPointerException.class, () -> new InspectionExecution(SUCCESS, null));
    for (var status : List.of(SUCCESS, WARNING)) {
      assertThrows(
          IllegalArgumentException.class, () -> new InspectionExecution(status, Optional.empty()));
      assertThrows(
          IllegalArgumentException.class,
          () -> new InspectionExecution(status, Optional.of(progress(0, 0, false))));
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> new InspectionExecution(SUCCESS, Optional.of(progress(1, 1, true))));
    assertThrows(
        IllegalArgumentException.class,
        () -> new InspectionExecution(WARNING, Optional.of(progress(0, 0, true))));
    for (var status : List.of(TIME_LIMIT, INTERRUPTED, STORAGE_FAILURE)) {
      assertEquals(50, new InspectionExecution(status, Optional.empty()).exitCode());
      assertEquals(
          50, new InspectionExecution(status, Optional.of(progress(0, 0, true))).exitCode());
    }
    assertEquals(5, InspectionExecution.Status.values().length);
    assertEquals(SUCCESS, InspectionExecution.Status.valueOf("SUCCESS"));
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      assertThrows(NullPointerException.class, () -> new InspectionRunExecutor(null, () -> 0));
      assertThrows(
          NullPointerException.class,
          () -> new InspectionRunExecutor(service(f, InspectionRunExecutorTest::connection), null));
      assertThrows(NullPointerException.class, () -> executor(f, () -> 0).run(null));
      assertEquals("0", progressCount());
    }
  }

  @Test
  void failuresDoNotLeakOrBecomeSuccess() throws Exception {
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      var result = executor(f, ticks(0, LIMIT)).run(RUN);
      assertEquals(
          "InspectionExecution[status=TIME_LIMIT, lastConfirmed=unavailable]", result.toString());
      result = executor(f, ticks(0, 0, LIMIT)).run(RUN);
      assertEquals(
          "InspectionExecution[status=TIME_LIMIT, lastConfirmed=InspectionProgress[inspected=0, deleted=0, protected=0, complete=true]]",
          result.toString());
      assertFalse(result.toString().contains(RUN.id().toString()));
      assertFalse(result.toString().contains(RUN.cutoff().toString()));
      assertFalse(result.toString().contains(f.raw));
      assertEquals(SUCCESS, executor(f, () -> 0).run(RUN).status());
      var failure = new UnsupportedOperationException("public clock failure");
      assertSame(
          failure,
          assertThrows(
              UnsupportedOperationException.class,
              () ->
                  executor(
                          f,
                          () -> {
                            throw failure;
                          })
                      .run(RUN)));
      AtomicInteger calls = new AtomicInteger();
      assertSame(
          failure,
          assertThrows(
              UnsupportedOperationException.class,
              () ->
                  executor(
                          f,
                          () -> {
                            if (calls.incrementAndGet() == 2) throw failure;
                            return 0;
                          })
                      .run(RUN)));
      var probe = new MaintenanceJdbcProbe();
      probe.fault = "close";
      result =
          new InspectionRunExecutor(service(f, () -> probe.wrap(connection())), () -> 0).run(RUN);
      assertEquals(STORAGE_FAILURE, result.status());
      assertTrue(result.lastConfirmed().isEmpty());
      assertFalse(result.toString().contains("public fault"));
      assertEquals("0|0|0|true", stored()); // DB complete is not proof that resource close passed.
    }
  }

  private static InspectionRunExecutor executor(
      AuthenticationInboxInspectorTest.Fixture f, LongSupplier clock) {
    return new InspectionRunExecutor(service(f, InspectionRunExecutorTest::connection), clock);
  }

  private static InboxCleanup service(
      AuthenticationInboxInspectorTest.Fixture f, SqlConnectionProvider provider) {
    return new InboxCleanup(
        provider, f.inspector, new NonAuthenticationInboxInspector(f.snapshots), Set.of("v1"));
  }

  private static InspectionProgress progress(long count, long held, boolean complete) {
    return new InspectionProgress(
        RUN,
        count == 0 ? Optional.empty() : Optional.of(new UUID(0, count)),
        count,
        count - held,
        held,
        complete);
  }

  private static LongSupplier ticks(long... values) {
    AtomicInteger index = new AtomicInteger();
    return () -> {
      int i = index.getAndIncrement();
      assertTrue(i < values.length, "clock sequence exhausted");
      return values[i];
    };
  }

  private static Connection connection() throws SQLException {
    return DriverManager.getConnection(url, "schubert_inbox_inspector", "");
  }

  private static void sql(String query) throws SQLException {
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute(query);
    }
  }

  private static String scalar(String query) throws SQLException {
    try (var c = db.admin();
        var s = c.createStatement();
        var row = s.executeQuery(query)) {
      assertTrue(row.next());
      String value = row.getString(1);
      assertNotNull(value);
      assertFalse(row.next());
      return value;
    }
  }

  private static String progressCount() throws SQLException {
    return scalar("select count(*) from schubert.inbox_inspection_progress");
  }

  private static String inboxCount() throws SQLException {
    return scalar("select count(*) from schubert.request_inbox");
  }

  private static String stored() throws SQLException {
    return scalar(
        "select inspected_count||'|'||deleted_count||'|'||protected_count||'|'||(completed_at is not null)::text from schubert.inbox_inspection_progress");
  }

  private static void invalidRows(int count) throws SQLException {
    sql(
        "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,owner_user_id,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at) "
            + "select ('00000000-0000-0000-0000-'||lpad(to_hex(g),12,'0'))::uuid,('00000000-0000-0000-0000-'||lpad(to_hex(g),12,'0'))::uuid,'GAMREQ01','001',7,repeat('a',64),'v1','ERROR','NONE','GAMRSP01','001',decode(repeat('00',30),'hex'),'unknown','2026-09-09','2026-09-09','2026-09-10' from generate_series(1,"
            + count
            + ") g");
  }

  private static void validLoginError(AuthenticationInboxInspectorTest.Fixture f) throws Exception {
    UUID id = new UUID(0, 101);
    var identity = ResponseSnapshotIdentity.anonymous(id, "LGNRSP01", "001");
    var saved = f.saved(identity, "0101", InboxResultReference.none());
    byte[] bytes = saved.responseSnapshot().orElseThrow().ciphertext();
    try (var c = db.admin();
        var s =
            c.prepareStatement(
                "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at) values(?,?,'LGNREQ01','001',repeat('a',64),'v1','ERROR','NONE','LGNRSP01','001',?,'s1','2026-09-09 00:00:00.122+00','2026-09-09 00:00:00.123+00','2026-09-16 00:00:00.123+00')")) {
      s.setObject(1, id);
      s.setObject(2, id);
      s.setBytes(3, bytes);
      assertEquals(1, s.executeUpdate());
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }
}
