package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
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

/**
 * PT-DB-INBOX-033..040: real least-privilege PG and independent JCE/wire, never production capture.
 */
final class AuthenticationInboxCleanupTest {
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_0101_F2D4F761 = "0101";
  private static final String FIXTURE_INSPECTION_HEALTH_F475CF78 = "inspection_health";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static final UUID MESSAGE = new UUID(0, 101);
  private static final UUID SESSION = new UUID(0, 104);
  private static final InspectionRun RUN =
      new InspectionRun(new UUID(0, 42), Instant.parse("2026-09-17T00:00:00.123Z"));
  private static final ResponseSnapshotIdentity LOGIN =
      ResponseSnapshotIdentity.anonymous(MESSAGE, "LGNRSP01", "001");
  private static final ResponseSnapshotIdentity LOGOUT =
      ResponseSnapshotIdentity.authenticated(MESSAGE, "LOGRSP01", "001", 7);

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
        List.of("request_inbox", "auth_sessions", "app_logs", "batch_runs", "app_users"))
      sql("delete from schubert." + table);
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) values(7,'Learner','learner','synthetic-unused','USER','ACTIVE','2026-09-09','2026-09-09','2026-09-09')");
    try (var c = db.api();
        var s =
            c.prepareStatement(
                "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status) values (?,'2026-09-17',?,1,'2026-09-17T00:00:00Z','2026-09-17T00:00:01Z','SUCCESS')")) {
      for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG")) {
        s.setObject(1, RUN.id());
        s.setString(2, step);
        assertEquals(1, s.executeUpdate());
      }
    }
  }

  @Test
  void validAuthRowsDeleteAtomically() throws Exception {
    for (var id : List.of(LOGIN, LOGOUT)) {
      for (String code :
          id.equals(LOGIN)
              ? List.of(FIXTURE_0000_876EEFE0, FIXTURE_0101_F2D4F761, "0106")
              : List.of(FIXTURE_0000_876EEFE0, "0200", "0102")) {
        reset();
        try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
          seed(f, id, code);
          String before = references();
          var service = service(f);
          assertEquals(
              new InspectionStep(InspectionStep.Outcome.DELETED, Optional.of(MESSAGE)),
              service.inspectNext(RUN, Optional.empty()));
          assertEquals("0", count());
          assertEquals(before, references());
          assertEquals(
              new InspectionStep(InspectionStep.Outcome.END, Optional.empty()),
              service.inspectNext(RUN, Optional.empty()));
        }
      }
    }
  }

  @Test
  void invalidRowsAreProtectedWithoutMutation() throws Exception {
    for (String mutation :
        List.of(
            "update schubert.request_inbox set response_body_encrypted=decode(repeat('00',30),'hex')",
            "update schubert.request_inbox set response_key_version='unknown'",
            "delete from schubert.auth_sessions",
            "update schubert.auth_sessions set context_hash=repeat('b',64)",
            "update schubert.request_inbox set fingerprint_key_version='unknown'",
            "update schubert.request_inbox set request_version='002'",
            "update schubert.request_inbox set response_version='002'",
            "update schubert.request_inbox set response_layout_id='LOGRSP01'",
            "update schubert.request_inbox set expires_at=completed_at+interval '1 hour'",
            "update schubert.request_inbox set response_body_encrypted=null,response_key_version=null")) {
      reset();
      try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
        seed(f, LOGIN, FIXTURE_0000_876EEFE0);
        sql(mutation);
        assertEquals(
            InspectionStep.Outcome.PROTECTED,
            service(f).inspectNext(RUN, Optional.empty()).outcome(),
            mutation);
        assertEquals("1", count());
      }
    }
    for (String mutation :
        List.of(
            "expires_at='2026-09-17T00:00:00.123Z'",
            "request_layout_id='GAMREQ01',owner_user_id=7,response_layout_id='GAMRSP01'",
            "processing_state='PROCESSING',completed_at=null,result_ref_type=null,result_ref_uuid=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null")) {
      reset();
      try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
        seed(f, LOGIN, FIXTURE_0000_876EEFE0);
        sql("update schubert.request_inbox set " + mutation);
        assertEquals(
            mutation.contains("GAMREQ01")
                ? InspectionStep.Outcome.PROTECTED
                : InspectionStep.Outcome.END,
            service(f).inspectNext(RUN, Optional.empty()).outcome());
        assertEquals("1", count());
      }
    }
  }

  @Test
  void nullUnknownAndFactoryContracts() throws Exception {
    assertThrows(NullPointerException.class, () -> new InspectionRun(null, RUN.cutoff()));
    assertThrows(NullPointerException.class, () -> new InspectionRun(RUN.id(), null));
    for (Instant cutoff : List.of(Instant.MIN, Instant.MAX, RUN.cutoff().plusNanos(1)))
      assertThrows(IllegalArgumentException.class, () -> new InspectionRun(RUN.id(), cutoff));
    for (Instant cutoff :
        List.of(
            Instant.parse("0001-01-01T00:00:00Z"), Instant.parse("9999-12-31T23:59:59.999999Z")))
      assertEquals(cutoff, new InspectionRun(RUN.id(), cutoff).cutoff());
    assertThrows(NullPointerException.class, () -> new InspectionStep(null, Optional.empty()));
    assertThrows(
        NullPointerException.class, () -> new InspectionStep(InspectionStep.Outcome.END, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new InspectionStep(InspectionStep.Outcome.END, Optional.of(MESSAGE)));
    assertThrows(
        IllegalArgumentException.class,
        () -> new InspectionStep(InspectionStep.Outcome.PROTECTED, Optional.empty()));
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      assertThrows(
          NullPointerException.class,
          () ->
              new InboxCleanup(
                  null,
                  f.inspector,
                  new NonAuthenticationInboxInspector(f.snapshots),
                  Set.of("v1")));
      assertThrows(
          NullPointerException.class,
          () ->
              new InboxCleanup(
                  AuthenticationInboxCleanupTest::connection,
                  null,
                  new NonAuthenticationInboxInspector(f.snapshots),
                  Set.of("v1")));
      assertThrows(
          NullPointerException.class,
          () ->
              new InboxCleanup(
                  AuthenticationInboxCleanupTest::connection,
                  f.inspector,
                  new NonAuthenticationInboxInspector(f.snapshots),
                  null));
      var nullElement = new HashSet<String>();
      nullElement.add(null);
      assertThrows(
          NullPointerException.class,
          () ->
              new InboxCleanup(
                  AuthenticationInboxCleanupTest::connection,
                  f.inspector,
                  new NonAuthenticationInboxInspector(f.snapshots),
                  nullElement));
      for (Set<String> versions :
          List.of(Set.<String>of(), Set.of(""), Set.of("v1", "bad secret value")))
        assertThrows(
            IllegalArgumentException.class,
            () ->
                new InboxCleanup(
                    AuthenticationInboxCleanupTest::connection,
                    f.inspector,
                    new NonAuthenticationInboxInspector(f.snapshots),
                    versions));
      var versions = new HashSet<>(Set.of("v1", "previous"));
      var cleanup =
          new InboxCleanup(
              AuthenticationInboxCleanupTest::connection,
              f.inspector,
              new NonAuthenticationInboxInspector(f.snapshots),
              versions);
      versions.clear();
      assertThrows(NullPointerException.class, () -> cleanup.inspectNext(null, Optional.empty()));
      assertThrows(NullPointerException.class, () -> cleanup.inspectNext(RUN, null));
      seed(f, LOGIN, FIXTURE_0101_F2D4F761);
      assertEquals(
          InspectionStep.Outcome.DELETED, cleanup.inspectNext(RUN, Optional.empty()).outcome());
    }
    for (String column :
        List.of(
            "message_id",
            "request_layout_id",
            "response_layout_id",
            "correlation_id",
            "created_at",
            "expires_at",
            "request_version",
            "response_version",
            "request_fingerprint_hmac",
            "fingerprint_key_version",
            "result_ref_type",
            "processing_state",
            "response_key_version",
            "completed_at",
            "inspection_xact",
            "inspection_hash")) {
      reset();
      try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
        seed(f, LOGIN, FIXTURE_0101_F2D4F761);
        var probe = new MaintenanceJdbcProbe();
        probe.columns.put(column, null);
        redacted(() -> probed(f, probe).inspectNext(RUN, Optional.empty()));
        assertEquals("1", count(), column);
        assertEquals(1, probe.closes);
      }
    }
    Map<String, Object> malformed =
        Map.ofEntries(
            Map.entry("request_layout_id", "UNKNOWN1"),
            Map.entry("operation_token", new UUID(0, 77)),
            Map.entry("request_fingerprint_hmac", "Z".repeat(64)),
            Map.entry("owner_user_id", 7L),
            Map.entry("result_ref_type", "UNKNOWN"),
            Map.entry("processing_state", "UNKNOWN"),
            Map.entry("response_body_encrypted", new byte[1]),
            Map.entry("response_key_version", "bad key"),
            Map.entry("result_ref_id", 7L));
    for (var bad : malformed.entrySet()) {
      reset();
      try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
        seed(f, LOGIN, FIXTURE_0101_F2D4F761);
        var probe = new MaintenanceJdbcProbe();
        probe.columns.put(bad.getKey(), bad.getValue());
        assertEquals(
            InspectionStep.Outcome.PROTECTED,
            probed(f, probe).inspectNext(RUN, Optional.empty()).outcome(),
            bad.getKey());
        assertEquals("1", count());
      }
    }
  }

  @Test
  void ownsTransactionAndKeepsLocks() throws Exception {
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      seed(f, LOGIN, FIXTURE_0000_876EEFE0);
      var probe = new MaintenanceJdbcProbe();
      probe.beforeDelete =
          c -> {
            assertFalse(c.getAutoCommit());
            assertEquals(0, probe.commits);
            assertEquals(0, probe.closes);
            for (String query :
                List.of(
                    "select message_id from schubert.request_inbox for update nowait",
                    "select id from schubert.auth_sessions for update nowait",
                    "select id from schubert.batch_runs for update nowait")) {
              try (var other = db.api();
                  var s = other.createStatement()) {
                assertEquals(
                    "55P03",
                    assertThrows(SQLException.class, () -> s.execute(query)).getSQLState());
              }
            }
          };
      assertEquals(
          InspectionStep.Outcome.DELETED,
          probed(f, probe).inspectNext(RUN, Optional.empty()).outcome());
      assertEquals(1, probe.commits);
      assertEquals(1, probe.closes);
      assertEquals(0, probe.rollbacks);
      assertEquals(0, probe.saves);
      assertEquals(1, probe.deletes);
    }
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      var probe = new MaintenanceJdbcProbe();
      probe.fresh = false;
      redacted(() -> probed(f, probe).inspectNext(RUN, Optional.empty()));
      assertEquals(1, probe.closes);
      assertEquals(0, probe.deletes);
    }
  }

  @Test
  void failuresRollbackAndRemainRedacted() throws Exception {
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      seed(f, LOGIN, FIXTURE_0101_F2D4F761);
      var probe = new MaintenanceJdbcProbe();
      probe.columns.put("message_id", null);
      probe.fault = "rollback";
      redacted(() -> probed(f, probe).inspectNext(RUN, Optional.empty()));
      assertEquals(1, probe.rollbacks);
      assertEquals(1, probe.closes);
      assertEquals("1", count());
    }
    for (String fault :
        List.of(
            "getAutoCommit",
            "setAutoCommit",
            "prepareStatement",
            "setObject",
            "setObject#2",
            "executeQuery",
            "next",
            "getString",
            "getObject",
            "getBytes",
            "resultClose",
            "statementClose",
            "commit",
            "close")) {
      reset();
      try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
        seed(f, LOGIN, FIXTURE_0101_F2D4F761);
        var probe = new MaintenanceJdbcProbe();
        probe.fault = fault;
        redacted(() -> probed(f, probe).inspectNext(RUN, Optional.empty()));
        assertEquals(1, probe.closes, fault);
        assertEquals(fault.equals("close") ? "0" : "1", count(), fault);
      }
    }
    for (String selected :
        List.of(
            "maintenance_next_inbox",
            "maintenance_delete_inbox",
            FIXTURE_INSPECTION_HEALTH_F475CF78)) {
      for (String fault : List.of("executeQuery", "resultClose", "statementClose")) {
        reset();
        try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
          seed(f, LOGIN, FIXTURE_0101_F2D4F761);
          var p = new MaintenanceJdbcProbe();
          p.selectedSql = selected;
          p.fault = fault;
          redacted(() -> probed(f, p).inspectNext(RUN, Optional.empty()));
          assertTrue(p.selectedStatements >= 1, selected);
          assertEquals("1", count());
          assertEquals(1, p.rollbacks);
          assertEquals(1, p.closes);
        }
      }
      for (String mode : List.of("empty", "duplicate", "null")) {
        reset();
        try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
          seed(f, LOGIN, FIXTURE_0101_F2D4F761);
          var p = new MaintenanceJdbcProbe();
          p.selectedSql = selected;
          p.empty = mode.equals("empty");
          p.duplicate = mode.equals("duplicate");
          if (mode.equals("null"))
            p.columns.put(
                selected.equals(FIXTURE_INSPECTION_HEALTH_F475CF78)
                    ? FIXTURE_INSPECTION_HEALTH_F475CF78
                    : selected.contains("delete") ? "deleted" : "message_id",
                null);
          if (selected.contains("next") && mode.equals("empty"))
            assertEquals(
                InspectionStep.Outcome.END,
                probed(f, p).inspectNext(RUN, Optional.empty()).outcome());
          else redacted(() -> probed(f, p).inspectNext(RUN, Optional.empty()));
          assertTrue(p.selectedStatements >= 1, selected);
          assertEquals("1", count());
          assertEquals(1, p.closes);
        }
      }
    }
    reset();
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      seed(f, LOGIN, FIXTURE_0000_876EEFE0);
      var p = new MaintenanceJdbcProbe();
      p.selectedSql = "from schubert.auth_sessions";
      p.fault = "aborted";
      redacted(() -> probed(f, p).inspectNext(RUN, Optional.empty()));
      assertEquals("1", count());
      assertEquals(1, p.rollbacks);
      var commitAfter = new MaintenanceJdbcProbe();
      commitAfter.fault = "commit";
      commitAfter.commitAfter = true;
      redacted(() -> probed(f, commitAfter).inspectNext(RUN, Optional.empty()));
      assertEquals("0", count());
      assertEquals(
          InspectionStep.Outcome.END, service(f).inspectNext(RUN, Optional.empty()).outcome());
      redacted(
          () ->
              new InboxCleanup(
                      () -> {
                        throw new SQLException("synthetic-private-provider-marker");
                      },
                      f.inspector,
                      new NonAuthenticationInboxInspector(f.snapshots),
                      Set.of("v1"))
                  .inspectNext(RUN, Optional.empty()));
      redacted(
          () ->
              new InboxCleanup(
                      () -> null,
                      f.inspector,
                      new NonAuthenticationInboxInspector(f.snapshots),
                      Set.of("v1"))
                  .inspectNext(RUN, Optional.empty()));
    }
  }

  /**
   * PT-DB-INBOX-267: provider failure is not a malformed saved row or a committed PROTECTED step.
   */
  @Test
  void providerIllegalArgumentInCandidateReadCannotCommitProtectedProgress() throws Exception {
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      for (String column :
          List.of(
              "result_ref_id",
              "result_ref_type",
              "result_ref_uuid",
              "processing_state",
              "response_key_version",
              "completed_at",
              "inspection_xact",
              "inspection_hash")) {
        reset();
        seed(f, LOGIN, FIXTURE_0101_F2D4F761);
        var probe = new MaintenanceJdbcProbe();
        probe.runtimeColumn = column;
        redacted(() -> probed(f, probe).inspectNext(RUN, Optional.empty()));
        assertEquals(0, probe.commits, column);
        assertEquals(1, probe.rollbacks, column);
        assertEquals(1, probe.closes, column);
        assertEquals("1", count(), column);
      }
    }
  }

  @Test
  void orderedCursorAndFixedRunReplay() throws Exception {
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      seed(f, LOGIN, FIXTURE_0101_F2D4F761);
      sql(
          "insert into schubert.request_inbox select '"
              + new UUID(0, 100)
              + "'::uuid,correlation_id,request_layout_id,request_version,owner_user_id,operation_token,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,result_ref_id,result_ref_uuid,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at from schubert.request_inbox");
      var cleanup = service(f);
      var first = cleanup.inspectNext(RUN, Optional.empty());
      assertEquals(InspectionStep.Outcome.PROTECTED, first.outcome());
      assertEquals(Optional.of(new UUID(0, 100)), first.cursor());
      var second = cleanup.inspectNext(RUN, first.cursor());
      assertEquals(InspectionStep.Outcome.DELETED, second.outcome());
      assertEquals(Optional.of(MESSAGE), second.cursor());
      assertEquals(InspectionStep.Outcome.END, cleanup.inspectNext(RUN, second.cursor()).outcome());
      assertEquals("1", count());
      redacted(
          () ->
              cleanup.inspectNext(
                  new InspectionRun(new UUID(0, 99), RUN.cutoff()), Optional.empty()));
      redacted(
          () ->
              cleanup.inspectNext(
                  new InspectionRun(RUN.id(), RUN.cutoff().plusSeconds(86400)), Optional.empty()));
    }
  }

  @Test
  void concurrentAttemptsCannotDoubleDelete() throws Exception {
    try (var f = new AuthenticationInboxInspectorTest.Fixture();
        var pool = Executors.newFixedThreadPool(8)) {
      seed(f, LOGIN, FIXTURE_0101_F2D4F761);
      var observed = new ThreadLocal<MaintenanceJdbcProbe>();
      var cleanup =
          new InboxCleanup(
              () -> observed.get().wrap(connection()),
              f.inspector,
              new NonAuthenticationInboxInspector(f.snapshots),
              Set.of("v1"));
      var tasks = new ArrayList<Callable<String>>();
      for (int i = 0; i < 100; i++)
        tasks.add(
            () -> {
              var probe = new MaintenanceJdbcProbe();
              observed.set(probe);
              try {
                return cleanup.inspectNext(RUN, Optional.empty()).outcome().name();
              } catch (InboxMaintenanceException busy) {
                assertNull(busy.getCause());
                expectedContention(probe.lastSqlState);
                return "EXPECTED_CONTENTION";
              } finally {
                observed.remove();
                assertEquals(1, probe.closes);
                assertEquals(0, probe.saves);
              }
            });
      var outcomes = new ArrayList<String>();
      for (var future : pool.invokeAll(tasks)) outcomes.add(future.get());
      assertEquals(100, outcomes.size());
      assertEquals(1, Collections.frequency(outcomes, "DELETED"));
      assertFalse(outcomes.contains("PROTECTED"));
      assertEquals("0", count());
      assertEquals(
          InspectionStep.Outcome.END, service(f).inspectNext(RUN, Optional.empty()).outcome());
      assertThrows(AssertionError.class, () -> expectedContention("08006"));
      assertThrows(AssertionError.class, () -> expectedContention("unobserved"));
    }
  }

  @Test
  void keysAndResultsNeverEscape() throws Exception {
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      seed(f, LOGIN, FIXTURE_0101_F2D4F761);
      var p = new MaintenanceJdbcProbe();
      p.selectedSql = FIXTURE_INSPECTION_HEALTH_F475CF78;
      p.columns.put(FIXTURE_INSPECTION_HEALTH_F475CF78, 0);
      redacted(() -> probed(f, p).inspectNext(RUN, Optional.empty()));
      assertEquals("1", count());
      var step = service(f).inspectNext(RUN, Optional.empty());
      assertFalse(step.toString().contains(MESSAGE.toString()));
      assertFalse(RUN.toString().contains(RUN.id().toString()));
      assertTrue(step.toString().contains("DELETED"));
      reset();
      seed(f, LOGIN, FIXTURE_0101_F2D4F761);
      f.snapshots.close();
      assertEquals(
          InspectionStep.Outcome.PROTECTED,
          service(f).inspectNext(RUN, Optional.empty()).outcome());
      assertEquals("1", count());
    }
    for (boolean previous : List.of(false, true)) {
      reset();
      try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
        seed(f, LOGIN, FIXTURE_0000_876EEFE0);
        byte[] newKey = new byte[32];
        new java.security.SecureRandom().nextBytes(newKey);
        try (var snapshots =
                new ResponseSnapshotCodec(
                    previous ? "s2" : "s1",
                    previous ? newKey : f.key,
                    previous ? "s1" : null,
                    previous ? f.key : null);
            var contexts =
                new dev.codex.schubert.nk.api.security.AuthContextCodec(
                    previous ? "a2" : "a1",
                    previous ? newKey : f.contextKey,
                    previous ? "a1" : null,
                    previous ? f.contextKey : null)) {
          var inspector =
              new AuthenticationInboxInspector(
                  snapshots, contexts, new dev.codex.schubert.nk.api.security.ContextHash());
          var cleanup =
              new InboxCleanup(
                  AuthenticationInboxCleanupTest::connection,
                  inspector,
                  new NonAuthenticationInboxInspector(snapshots),
                  Set.of("v1"));
          assertEquals(
              InspectionStep.Outcome.DELETED, cleanup.inspectNext(RUN, Optional.empty()).outcome());
          assertEquals("0", count());
        } finally {
          Arrays.fill(newKey, (byte) 0);
        }
      }
    }
  }

  private static void expectedContention(String sqlState) {
    assertEquals("55P03", sqlState);
  }

  @Test
  void inbox269ParentGuardBoundsSqlAndOwnsEveryDeleteCommitBoundary() throws Exception {
    try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
      seed(f, LOGIN, FIXTURE_0000_876EEFE0);
      var probe = new MaintenanceJdbcProbe();
      probe.beforeDelete =
          connection -> {
            try (var query = connection.createStatement();
                var row =
                    query.executeQuery("select current_setting('statement_timeout') as actual")) {
              assertTrue(row.next());
              assertEquals("5s", row.getString("actual")); // Independent SQL postcondition.
              assertFalse(row.next());
            }
          };
      int[] observations = {0};
      var result =
          guarded(
                  f,
                  probe,
                  () -> {
                    observations[0]++;
                    return 6_123_456_789L;
                  })
              .inspectNext(RUN, Optional.empty());
      assertEquals(InspectionStep.Outcome.DELETED, result.outcome());
      assertEquals("0", count());
      assertEquals(8, observations[0]);
      assertEquals(1, probe.deletes);
      assertEquals(1, probe.commits);
      assertEquals(0, probe.rollbacks);
      assertEquals(1, probe.closes);
    }
  }

  @Test
  void inbox270ExpiredOwnerNeverClaimsRollbackAfterConfirmedCommit() throws Exception {
    for (int failAt = 1; failAt <= 8; failAt++) {
      reset();
      try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
        seed(f, LOGIN, FIXTURE_0000_876EEFE0);
        int position = failAt;
        int[] calls = {0};
        var probe = new MaintenanceJdbcProbe();
        var cleanup =
            guarded(
                f,
                probe,
                () -> {
                  if (++calls[0] == position) throw new IOException("PRIVATE owner diagnostic");
                  return 6_123_456_789L;
                });
        assertThrows(
            InboxMaintenanceException.class, () -> cleanup.inspectNext(RUN, Optional.empty()));
        assertEquals(failAt, calls[0]);
        assertEquals(failAt == 8 ? "0" : "1", count());
        assertEquals(failAt == 8 ? 1 : 0, probe.commits);
        assertEquals(failAt >= 3 && failAt < 8 ? 1 : 0, probe.rollbacks);
        assertEquals(failAt == 1 ? 0 : 1, probe.closes);
        assertEquals(failAt <= 5 ? 0 : 1, probe.deletes);
      }
    }
  }

  @Test
  void inbox271SqlTimeoutReadbackMustBeExactAndNeverMissing() throws Exception {
    for (String fault : List.of("wrong", "missing", "extra", "io")) {
      reset();
      try (var f = new AuthenticationInboxInspectorTest.Fixture()) {
        seed(f, LOGIN, FIXTURE_0000_876EEFE0);
        var probe = new MaintenanceJdbcProbe();
        probe.selectedSql = "set_config";
        if (fault.equals("wrong")) probe.columns.put("bound_timeout", "5001");
        if (fault.equals("missing")) probe.empty = true;
        if (fault.equals("extra")) probe.duplicate = true;
        if (fault.equals("io")) probe.fault = "executeQuery";
        assertThrows(
            InboxMaintenanceException.class,
            () -> guarded(f, probe, () -> 6_123_456_789L).inspectNext(RUN, Optional.empty()));
        assertEquals("1", count());
        assertEquals(0, probe.commits);
        assertEquals(0, probe.deletes);
        assertEquals(1, probe.rollbacks);
        assertEquals(1, probe.closes);
      }
    }
  }

  private static InboxCleanup guarded(
      AuthenticationInboxInspectorTest.Fixture f,
      MaintenanceJdbcProbe probe,
      MaintenanceOwnerFrame.Guard guard) {
    return new InboxCleanup(
        () -> probe.wrap(connection()),
        f.inspector,
        new NonAuthenticationInboxInspector(f.snapshots),
        Set.of("v1"),
        guard);
  }

  private static InboxCleanup service(AuthenticationInboxInspectorTest.Fixture f) {
    return new InboxCleanup(
        AuthenticationInboxCleanupTest::connection,
        f.inspector,
        new NonAuthenticationInboxInspector(f.snapshots),
        Set.of("v1"));
  }

  private static InboxCleanup probed(
      AuthenticationInboxInspectorTest.Fixture f, MaintenanceJdbcProbe p) {
    return new InboxCleanup(
        () -> p.wrap(connection()),
        f.inspector,
        new NonAuthenticationInboxInspector(f.snapshots),
        Set.of("v1"));
  }

  private static Connection connection() throws SQLException {
    return DriverManager.getConnection(url, "schubert_inbox_inspector", "");
  }

  private static void seed(
      AuthenticationInboxInspectorTest.Fixture f, ResponseSnapshotIdentity id, String code)
      throws Exception {
    boolean success = code.equals(FIXTURE_0000_876EEFE0) || code.equals("0200");
    var saved =
        f.saved(
            id,
            code,
            success ? InboxResultReference.authSession(SESSION) : InboxResultReference.none());
    try (var c = db.api()) {
      f.seed(c, id.equals(LOGOUT));
      try (var s =
          c.prepareStatement(
              "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,owner_user_id,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,result_ref_uuid,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at) values(?,?,?,'001',?,repeat('a',64),'v1',?,?,?,?,?,?,?,'2026-09-09T00:00:00Z','2026-09-09T00:00:00.123Z','2026-09-16T00:00:00.123Z')")) {
        s.setObject(1, MESSAGE);
        s.setObject(2, MESSAGE);
        s.setString(3, id.equals(LOGIN) ? "LGNREQ01" : "LOGREQ01");
        s.setObject(4, id.equals(LOGIN) ? null : 7L);
        s.setString(5, success ? "COMPLETED" : "ERROR");
        s.setString(6, success ? "AUTH_SESSION" : "NONE");
        s.setObject(7, success ? SESSION : null);
        s.setString(8, id.responseLayoutId());
        s.setString(9, "001");
        s.setBytes(10, saved.responseSnapshot().orElseThrow().ciphertext());
        s.setString(11, "s1");
        assertEquals(1, s.executeUpdate());
      }
    }
  }

  private static void sql(String command) throws SQLException {
    try (var c = db.api();
        var s = c.createStatement()) {
      s.execute(command);
    }
  }

  private static String count() throws SQLException {
    try (var c = db.api();
        var s = c.createStatement();
        var r = s.executeQuery("select count(*) from schubert.request_inbox")) {
      assertTrue(r.next());
      return r.getString(1);
    }
  }

  private static String references() throws SQLException {
    try (var c = db.api();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select (select count(*) from schubert.batch_runs)||'|'||count(*)||'|'||min(revoked::text)||'|'||min(last_accessed_at::text) from schubert.auth_sessions")) {
      assertTrue(r.next());
      return r.getString(1);
    }
  }

  private static void redacted(Runnable call) {
    var error = assertThrows(InboxMaintenanceException.class, call::run);
    assertEquals("Inbox maintenance did not complete; resume the same run", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }
}
