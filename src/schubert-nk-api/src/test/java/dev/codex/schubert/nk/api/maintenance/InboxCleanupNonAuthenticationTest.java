package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.messaging.outbound.SqlConnectionProvider;
import dev.codex.schubert.nk.api.security.AuthContextCodec;
import dev.codex.schubert.nk.api.security.ContextHash;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
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
 * PT-DB-INBOX-057..064: shared owned transaction, independent wire/JCE and real least-privilege PG.
 */
final class InboxCleanupNonAuthenticationTest {
  private static final String FIXTURE_USTRSP01_19F531B7 = "USTRSP01";
  private static final String FIXTURE_GAMRSP01_D6D22C8C = "GAMRSP01";
  private static final String FIXTURE_SCNRSP01_DD42C8D5 = "SCNRSP01";
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC =
      "delete from schubert.request_inbox";
  private static final String FIXTURE_55P03_0FE714C6 = "55P03";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static final Instant TIME = Instant.parse("2026-09-09T00:00:00.123Z");
  private static final InspectionRun RUN =
      new InspectionRun(new UUID(0, 42), Instant.parse("2026-09-17T00:00:00.123Z"));
  private static final Set<String> MUTATIONS =
      Set.of("UCRRSP01", FIXTURE_USTRSP01_19F531B7, "URLRSP01", "UPWRSP01", "ULKRSP01");
  private static final List<String> QUERIES =
      List.of(
          FIXTURE_GAMRSP01_D6D22C8C,
          "SPKRSP01",
          "RTERSP01",
          "SCFRSP01",
          "SRCRSP01",
          FIXTURE_SCNRSP01_DD42C8D5,
          "AUDRSP01",
          "ANMRSP01",
          "ANLRSP01",
          "VIDRSP01",
          "MCTRSP01",
          "MCSRSP01",
          "MTRRSP01",
          "MEDRSP01",
          "USRRSP01",
          "UDTRSP01",
          "LGSRSP01");
  private static final InboxResultReference USER =
      InboxResultReference.numeric(InboxResultReferenceType.USER, 9);
  private static final InboxResultReference SCRIPT =
      InboxResultReference.numeric(InboxResultReferenceType.SCENARIO_FILE, 11);
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
    for (String table : List.of("request_inbox", "script_files", "batch_runs", "app_users"))
      sql("delete from schubert." + table);
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at,version) values(7,'Learner','learner','synthetic-unused','USER','ACTIVE','2026-09-09','2026-09-09','2026-09-09',0),(9,'Target','target','synthetic-unused','USER','ACTIVE','2026-09-09','2026-09-09','2026-09-09',9)");
    sql(
        "insert into schubert.script_files(id,game_id,display_order,storage_relative_path,display_path,file_name,sha256,byte_size,created_at) values(11,1,1,'scenario/one.txt','one','one.txt',repeat('a',64),12,'2026-09-09')");
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
  void validQueriesAndMutationsDeleteAtomically() throws Exception {
    var routes = new ArrayList<>(QUERIES);
    routes.addAll(MUTATIONS);
    try (var f = new Fixture()) {
      String before = references();
      for (String layout : routes) {
        for (String code :
            List.of(FIXTURE_0000_876EEFE0, layout.equals("UDTRSP01") ? "0104" : "9001")) {
          seed(
              f,
              101,
              layout,
              code,
              code.equals(FIXTURE_0000_876EEFE0) && MUTATIONS.contains(layout) ? USER : NONE,
              Map.of());
          assertEquals(
              new InspectionStep(InspectionStep.Outcome.DELETED, Optional.of(new UUID(0, 101))),
              f.service().inspectNext(RUN, Optional.empty()),
              layout + "/" + code);
          assertEquals("0", count());
          assertEquals(
              InspectionStep.Outcome.END, f.service().inspectNext(RUN, Optional.empty()).outcome());
          assertEquals(before, references());
        }
      }
      seed(f, 101, "ULKRSP01", "0200", USER, Map.of("更新後version", "0"));
      assertEquals(
          InspectionStep.Outcome.DELETED, f.service().inspectNext(RUN, Optional.empty()).outcome());
      seed(
          f,
          101,
          FIXTURE_SCNRSP01_DD42C8D5,
          FIXTURE_0000_876EEFE0,
          SCRIPT,
          NonAuthenticationInboxInspectorTest.fileValues(1));
      assertEquals(
          InspectionStep.Outcome.DELETED, f.service().inspectNext(RUN, Optional.empty()).outcome());
      assertEquals(before, references());
    }
  }

  @Test
  void userAndScenarioReferencesStayProtected() throws Exception {
    try (var f = new Fixture()) {
      for (String mutation :
          List.of(
              "result_ref_type='SCENARIO_FILE',result_ref_id=11",
              "result_ref_id=7",
              "response_key_version='unknown'",
              "response_body_encrypted=decode(repeat('00',30),'hex')")) {
        sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
        seed(f, 101, FIXTURE_USTRSP01_19F531B7, FIXTURE_0000_876EEFE0, USER, Map.of());
        sql("update schubert.request_inbox set " + mutation);
        protectedRow(f);
      }
      sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
      seed(
          f,
          101,
          FIXTURE_USTRSP01_19F531B7,
          FIXTURE_0000_876EEFE0,
          USER,
          Map.of("更新後version", "10"));
      protectedRow(f);
      sql(
          "update schubert.app_users set version=10,username='Later',username_key='later',status='DISABLED',role='ADMIN' where id=9");
      assertEquals(
          InspectionStep.Outcome.DELETED, f.service().inspectNext(RUN, Optional.empty()).outcome());
      seed(f, 101, FIXTURE_USTRSP01_19F531B7, FIXTURE_0000_876EEFE0, USER, Map.of());
      sql("delete from schubert.app_users where id=9");
      protectedRow(f);
      for (String mutation :
          List.of(
              "update schubert.request_inbox set result_ref_id=12",
              "update schubert.script_files set game_id=2 where id=11",
              "delete from schubert.script_files where id=11")) {
        reset();
        seed(
            f,
            101,
            FIXTURE_SCNRSP01_DD42C8D5,
            FIXTURE_0000_876EEFE0,
            SCRIPT,
            NonAuthenticationInboxInspectorTest.fileValues(1));
        sql(mutation);
        protectedRow(f);
      }
      reset();
      var invalidDate = NonAuthenticationInboxInspectorTest.fileValues(1);
      invalidDate.put("File relative path", "20260230/" + new UUID(0, 3) + ".ready");
      seed(f, 101, FIXTURE_SCNRSP01_DD42C8D5, FIXTURE_0000_876EEFE0, SCRIPT, invalidDate);
      protectedRow(f);
    }
  }

  @Test
  void canonicalMetadataAndTokensAreRequired() throws Exception {
    try (var f = new Fixture()) {
      assertThrows(
          NullPointerException.class,
          () ->
              new InboxCleanup(
                  InboxCleanupNonAuthenticationTest::connection, f.auth, null, Set.of("v1")));
      for (String layout : List.of(FIXTURE_GAMRSP01_D6D22C8C, FIXTURE_USTRSP01_19F531B7)) {
        for (String mutation :
            List.of(
                "request_version='002'",
                "response_version='002'",
                "response_layout_id='AUDRSP01'",
                "fingerprint_key_version='unknown'",
                "response_body_encrypted=null,response_key_version=null")) {
          sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
          seed(
              f,
              101,
              layout,
              FIXTURE_0000_876EEFE0,
              MUTATIONS.contains(layout) ? USER : NONE,
              Map.of());
          sql("update schubert.request_inbox set " + mutation);
          protectedRow(f);
        }
        for (boolean tokenPresent : List.of(false, true)) {
          sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
          seed(
              f,
              101,
              layout,
              FIXTURE_0000_876EEFE0,
              MUTATIONS.contains(layout) ? USER : NONE,
              Map.of());
          var p = new MaintenanceJdbcProbe();
          p.columns.put("operation_token", tokenPresent ? UUID.randomUUID() : null);
          assertEquals(
              tokenPresent == layout.equals(FIXTURE_USTRSP01_19F531B7)
                  ? InspectionStep.Outcome.DELETED
                  : InspectionStep.Outcome.PROTECTED,
              f.service(() -> p.wrap(connection())).inspectNext(RUN, Optional.empty()).outcome());
          assertEquals(
              tokenPresent == layout.equals(FIXTURE_USTRSP01_19F531B7) ? "0" : "1", count());
        }
      }
      for (String mutation :
          List.of(
              "expires_at='2026-09-17T00:00:00.123Z'",
              "processing_state='PROCESSING',completed_at=null,result_ref_type=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null")) {
        sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
        seed(f, 101, FIXTURE_GAMRSP01_D6D22C8C, FIXTURE_0000_876EEFE0, NONE, Map.of());
        sql("update schubert.request_inbox set " + mutation);
        assertEquals(
            InspectionStep.Outcome.END, f.service().inspectNext(RUN, Optional.empty()).outcome());
        assertEquals("1", count());
      }
    }
  }

  @Test
  void mixedCursorsNeverSkipUnverifiedRows() throws Exception {
    try (var f = new Fixture()) {
      seed(f, 101, FIXTURE_GAMRSP01_D6D22C8C, FIXTURE_0000_876EEFE0, NONE, Map.of());
      sql(
          "update schubert.request_inbox set request_layout_id='ZZZREQ01',response_layout_id='ZZZRSP01'");
      seed(f, 102, FIXTURE_GAMRSP01_D6D22C8C, FIXTURE_0000_876EEFE0, NONE, Map.of());
      sql(
          "update schubert.request_inbox set fingerprint_key_version='unknown' where message_id='"
              + new UUID(0, 102)
              + "'");
      seed(f, 103, "UCRRSP01", FIXTURE_0000_876EEFE0, USER, Map.of());
      seed(f, 104, FIXTURE_GAMRSP01_D6D22C8C, "9001", NONE, Map.of());
      Optional<UUID> cursor = Optional.empty();
      for (int i = 101; i <= 104; i++) {
        var step = f.service().inspectNext(RUN, cursor);
        assertEquals(
            i < 103 ? InspectionStep.Outcome.PROTECTED : InspectionStep.Outcome.DELETED,
            step.outcome());
        assertEquals(Optional.of(new UUID(0, i)), step.cursor());
        cursor = step.cursor();
      }
      assertEquals(
          new InspectionStep(InspectionStep.Outcome.END, Optional.empty()),
          f.service().inspectNext(RUN, cursor));
      assertEquals("101,102", remainingSequences());
      var first = f.service().inspectNext(RUN, Optional.empty());
      assertEquals(InspectionStep.Outcome.PROTECTED, first.outcome());
      var second = f.service().inspectNext(RUN, first.cursor());
      assertEquals(InspectionStep.Outcome.PROTECTED, second.outcome());
      assertEquals(
          InspectionStep.Outcome.END, f.service().inspectNext(RUN, second.cursor()).outcome());
    }
  }

  @Test
  void transactionFaultsRollbackAndResume() throws Exception {
    try (var f = new Fixture()) {
      for (String layout :
          List.of(
              FIXTURE_GAMRSP01_D6D22C8C, FIXTURE_USTRSP01_19F531B7, FIXTURE_SCNRSP01_DD42C8D5)) {
        for (String fault :
            List.of(
                "executeQuery", "getObject", "resultClose", "statementClose", "commit", "close")) {
          sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
          seed(f, 101, layout, FIXTURE_0000_876EEFE0, reference(layout), values(layout));
          var p = new MaintenanceJdbcProbe();
          p.selectedSql = "maintenance_delete_inbox";
          p.fault = fault;
          var failure =
              assertThrows(
                  InboxMaintenanceException.class,
                  () -> f.service(() -> p.wrap(connection())).inspectNext(RUN, Optional.empty()));
          redacted(failure);
          assertTrue(p.selectedStatements >= 1);
          assertEquals(1, p.closes);
          assertEquals(fault.equals("close") ? "0" : "1", count());
          assertEquals(
              fault.equals("close") ? InspectionStep.Outcome.END : InspectionStep.Outcome.DELETED,
              f.service().inspectNext(RUN, Optional.empty()).outcome());
        }
      }
      for (String layout : List.of(FIXTURE_USTRSP01_19F531B7, FIXTURE_SCNRSP01_DD42C8D5)) {
        for (String fault : List.of("getObject", "aborted")) {
          sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
          seed(f, 101, layout, FIXTURE_0000_876EEFE0, reference(layout), values(layout));
          var p = new MaintenanceJdbcProbe();
          p.selectedSql = "reference_value";
          p.fault = fault;
          if (fault.equals("aborted")) {
            redacted(
                assertThrows(
                    InboxMaintenanceException.class,
                    () ->
                        f.service(() -> p.wrap(connection())).inspectNext(RUN, Optional.empty())));
            assertEquals(1, p.rollbacks);
          } else
            assertEquals(
                InspectionStep.Outcome.PROTECTED,
                f.service(() -> p.wrap(connection())).inspectNext(RUN, Optional.empty()).outcome());
          assertEquals("1", count());
          assertEquals(1, p.closes);
        }
      }
      sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
      seed(f, 101, FIXTURE_USTRSP01_19F531B7, FIXTURE_0000_876EEFE0, USER, Map.of());
      var uncertain = new MaintenanceJdbcProbe();
      uncertain.fault = "commit";
      uncertain.commitAfter = true;
      redacted(
          assertThrows(
              InboxMaintenanceException.class,
              () ->
                  f.service(() -> uncertain.wrap(connection()))
                      .inspectNext(RUN, Optional.empty())));
      assertEquals("0", count());
      assertEquals(
          InspectionStep.Outcome.END, f.service().inspectNext(RUN, Optional.empty()).outcome());
    }
  }

  @Test
  void concurrentMixedRequestsStayIsolated() throws Exception {
    try (var f = new Fixture();
        var pool = Executors.newFixedThreadPool(8)) {
      seed(f, 101, FIXTURE_GAMRSP01_D6D22C8C, FIXTURE_0000_876EEFE0, NONE, Map.of());
      seed(f, 102, FIXTURE_USTRSP01_19F531B7, FIXTURE_0000_876EEFE0, USER, Map.of());
      seed(
          f,
          103,
          FIXTURE_SCNRSP01_DD42C8D5,
          FIXTURE_0000_876EEFE0,
          SCRIPT,
          values(FIXTURE_SCNRSP01_DD42C8D5));
      var local = ThreadLocal.withInitial(MaintenanceJdbcProbe::new);
      var service = f.service(() -> local.get().wrap(connection()));
      var tasks = new ArrayList<Callable<Optional<UUID>>>();
      for (int i = 0; i < 100; i++)
        tasks.add(
            () -> {
              var p = new MaintenanceJdbcProbe();
              local.set(p);
              try {
                var result = service.inspectNext(RUN, Optional.empty());
                assertNotEquals(InspectionStep.Outcome.PROTECTED, result.outcome());
                return result.cursor();
              } catch (InboxMaintenanceException failure) {
                assertEquals(FIXTURE_55P03_0FE714C6, p.lastSqlState);
                redacted(failure);
                return Optional.empty();
              } finally {
                assertEquals(1, p.closes);
                assertEquals(0, p.saves);
                local.remove();
              }
            });
      var deleted = new ArrayList<UUID>();
      int attempts = 0;
      // BUG-090: each completed wave guarantees at least one winner if a row remains.
      for (int[] wave : List.of(new int[] {0, 33}, new int[] {33, 66}, new int[] {66, 100})) {
        var results = pool.invokeAll(tasks.subList(wave[0], wave[1]));
        attempts += results.size();
        for (var result : results) result.get().ifPresent(deleted::add);
      }
      assertEquals(100, attempts);
      assertEquals(3, deleted.size());
      assertEquals(
          Set.of(new UUID(0, 101), new UUID(0, 102), new UUID(0, 103)), new HashSet<>(deleted));
      assertEquals("0", count());
      for (String unexpected : List.of("08006", "unobserved"))
        assertThrows(AssertionError.class, () -> assertEquals(FIXTURE_55P03_0FE714C6, unexpected));
    }
  }

  @Test
  void leastPrivilegeAndKeyLifetimes() throws Exception {
    try (var f = new Fixture()) {
      for (String layout : List.of(FIXTURE_USTRSP01_19F531B7, FIXTURE_SCNRSP01_DD42C8D5)) {
        seed(f, 101, layout, FIXTURE_0000_876EEFE0, reference(layout), values(layout));
        var p = new MaintenanceJdbcProbe();
        p.beforeDelete =
            c -> {
              assertEquals("schubert_inbox_inspector", scalar(c, "select current_user"));
              assertEquals(0, p.commits);
              assertEquals(0, p.saves);
              String table =
                  layout.equals(FIXTURE_USTRSP01_19F531B7)
                      ? "app_users where id=9"
                      : "script_files where id=11";
              denied(
                  "schubert_app",
                  FIXTURE_55P03_0FE714C6,
                  "select id from schubert." + table + " for update nowait");
              denied(
                  "schubert_app",
                  FIXTURE_55P03_0FE714C6,
                  "select message_id from schubert.request_inbox for update nowait");
              denied(
                  "schubert_batch",
                  FIXTURE_55P03_0FE714C6,
                  "select id from schubert.batch_runs for update nowait");
              denied(
                  "schubert_inbox_inspector",
                  "42501",
                  "select password_hash from schubert.app_users");
            };
        assertEquals(
            InspectionStep.Outcome.DELETED,
            f.service(() -> p.wrap(connection())).inspectNext(RUN, Optional.empty()).outcome());
        assertEquals(1, p.commits);
        assertEquals(1, p.closes);
        assertEquals(1, p.deletes);
        assertEquals(0, p.rollbacks);
      }
      seed(f, 101, FIXTURE_GAMRSP01_D6D22C8C, FIXTURE_0000_876EEFE0, NONE, Map.of());
      byte[] newKey = new byte[32];
      new SecureRandom().nextBytes(newKey);
      try (var rotated = new ResponseSnapshotCodec("v2", newKey, "v1", f.base.key)) {
        var service =
            new InboxCleanup(
                InboxCleanupNonAuthenticationTest::connection,
                f.auth,
                new NonAuthenticationInboxInspector(rotated),
                Set.of("v1"));
        assertEquals(
            InspectionStep.Outcome.DELETED, service.inspectNext(RUN, Optional.empty()).outcome());
      } finally {
        Arrays.fill(newKey, (byte) 0);
      }
      seed(f, 101, FIXTURE_GAMRSP01_D6D22C8C, FIXTURE_0000_876EEFE0, NONE, Map.of());
      f.base.codec.close();
      protectedRow(f);
    }
  }

  @Test
  void outcomesAndSideEffectsRemainBounded() throws Exception {
    try (var f = new Fixture()) {
      String before = references();
      for (String layout : List.of(FIXTURE_GAMRSP01_D6D22C8C, FIXTURE_USTRSP01_19F531B7)) {
        for (long adjustment : List.of(-1000L, 0L, 1000L)) {
          sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
          seed(f, 101, layout, FIXTURE_0000_876EEFE0, reference(layout), Map.of());
          Instant expires =
              TIME.plusSeconds(layout.equals(FIXTURE_GAMRSP01_D6D22C8C) ? 86400 : 604800)
                  .plusNanos(adjustment);
          try (var c = db.api();
              var s = c.prepareStatement("update schubert.request_inbox set expires_at=?")) {
            s.setObject(1, expires.atOffset(java.time.ZoneOffset.UTC));
            assertEquals(1, s.executeUpdate());
          }
          assertEquals(
              adjustment < 0 ? InspectionStep.Outcome.PROTECTED : InspectionStep.Outcome.DELETED,
              f.service().inspectNext(RUN, Optional.empty()).outcome());
          assertEquals(adjustment < 0 ? "1" : "0", count());
        }
      }
      for (String prefix : List.of("QSB", "NTS", "NTD", "NTC", "QSS", "QSD", "QDL")) {
        sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
        seed(f, 101, FIXTURE_GAMRSP01_D6D22C8C, FIXTURE_0000_876EEFE0, NONE, Map.of());
        try (var c = db.api();
            var s =
                c.prepareStatement(
                    "update schubert.request_inbox set request_layout_id=?,response_layout_id=?,operation_token=?")) {
          s.setString(1, prefix + "REQ01");
          s.setString(2, prefix + "RSP01");
          s.setObject(3, Set.of("QSB", "NTC", "QDL").contains(prefix) ? UUID.randomUUID() : null);
          assertEquals(1, s.executeUpdate());
        }
        var step = f.service().inspectNext(RUN, Optional.empty());
        assertEquals(InspectionStep.Outcome.PROTECTED, step.outcome());
        assertFalse(step.toString().contains(new UUID(0, 101).toString()));
        assertEquals("1", count());
      }
      sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
      for (int i = 0; i < 100; i++)
        assertEquals(
            new InspectionStep(InspectionStep.Outcome.END, Optional.empty()),
            f.service().inspectNext(RUN, Optional.empty()));
      assertEquals(before, references());
    }
  }

  private static InboxResultReference reference(String layout) {
    return layout.equals(FIXTURE_SCNRSP01_DD42C8D5)
        ? SCRIPT
        : MUTATIONS.contains(layout) ? USER : NONE;
  }

  private static Map<String, String> values(String layout) {
    return layout.equals(FIXTURE_SCNRSP01_DD42C8D5)
        ? NonAuthenticationInboxInspectorTest.fileValues(1)
        : Map.of();
  }

  private static void protectedRow(Fixture f) throws Exception {
    assertEquals(
        new InspectionStep(InspectionStep.Outcome.PROTECTED, Optional.of(new UUID(0, 101))),
        f.service().inspectNext(RUN, Optional.empty()));
    assertEquals("1", count());
  }

  private static void redacted(InboxMaintenanceException failure) {
    assertEquals("Inbox maintenance did not complete; resume the same run", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static String count() throws SQLException {
    try (var c = db.api()) {
      return scalar(c, "select count(*) from schubert.request_inbox");
    }
  }

  private static String remainingSequences() throws SQLException {
    try (var c = db.api();
        var s = c.createStatement();
        var r =
            s.executeQuery("select message_id from schubert.request_inbox order by message_id")) {
      var ids = new ArrayList<String>();
      while (r.next()) ids.add(Long.toString(r.getObject(1, UUID.class).getLeastSignificantBits()));
      return String.join(",", ids);
    }
  }

  private static String references() throws SQLException {
    try (var c = db.api()) {
      return scalar(
          c,
          "select (select string_agg(row(id,username,role,status,version)::text,',' order by id) from schubert.app_users)||'/'||(select string_agg(row(id,game_id,sha256)::text,',' order by id) from schubert.script_files)||'/'||(select string_agg(row(id,step,status)::text,',' order by id) from schubert.batch_runs)");
    }
  }

  private static String scalar(Connection c, String query) throws SQLException {
    try (var s = c.createStatement();
        var r = s.executeQuery(query)) {
      assertTrue(r.next());
      String value = r.getString(1);
      assertFalse(r.next());
      return value;
    }
  }

  private static void sql(String query) throws SQLException {
    try (var c = db.api();
        var s = c.createStatement()) {
      s.executeUpdate(query);
    }
  }

  private static void denied(String role, String state, String query) throws SQLException {
    try (var c = DriverManager.getConnection(url, role, "");
        var s = c.createStatement()) {
      assertEquals(state, assertThrows(SQLException.class, () -> s.execute(query)).getSQLState());
    }
  }

  private static Connection connection() throws SQLException {
    return DriverManager.getConnection(url, "schubert_inbox_inspector", "");
  }

  private static void seed(
      Fixture f,
      long sequence,
      String layout,
      String code,
      InboxResultReference reference,
      Map<String, String> values)
      throws Exception {
    UUID message = new UUID(0, sequence);
    var identity = ResponseSnapshotIdentity.authenticated(message, layout, "001", 7);
    byte[] wire = NonAuthenticationInboxInspectorTest.wire(layout, code, values, 0);
    byte[] correlation = message.toString().getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(correlation, 0, wire, 60, 36);
    InboxCompletion saved;
    try {
      saved =
          f.base.saved(
              identity,
              wire,
              Set.of(FIXTURE_0000_876EEFE0, "0200").contains(code)
                  ? InboxCompletionState.COMPLETED
                  : InboxCompletionState.ERROR,
              TIME);
    } finally {
      Arrays.fill(wire, (byte) 0);
    }
    assertTrue(
        f.base.inspector.isStructurallyValid(identity, saved),
        layout + "/independent wire fixture");
    byte[] body = saved.responseSnapshot().orElseThrow().ciphertext();
    try (var c = db.api();
        var s =
            c.prepareStatement(
                "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,owner_user_id,operation_token,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,result_ref_id,result_ref_uuid,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at) values (?,?,?,'001',7,?,repeat('a',64),'v1',?,?,?,?,?,'001',?,'v1',?,?,?)")) {
      s.setObject(1, message);
      s.setObject(2, message);
      s.setString(3, layout.substring(0, 3) + "REQ01");
      s.setObject(4, MUTATIONS.contains(layout) ? UUID.randomUUID() : null);
      s.setString(5, saved.state().name());
      s.setString(6, reference.type().name());
      s.setObject(7, reference.numericId().isPresent() ? reference.numericId().getAsLong() : null);
      s.setObject(8, reference.uuid().orElse(null));
      s.setString(9, layout);
      s.setBytes(10, body);
      s.setObject(11, TIME.minusMillis(1).atOffset(java.time.ZoneOffset.UTC));
      s.setObject(12, TIME.atOffset(java.time.ZoneOffset.UTC));
      s.setObject(
          13,
          TIME.plusSeconds(MUTATIONS.contains(layout) ? 604800 : 86400)
              .atOffset(java.time.ZoneOffset.UTC));
      assertEquals(1, s.executeUpdate());
    } finally {
      Arrays.fill(body, (byte) 0);
    }
  }

  private static final class Fixture implements AutoCloseable {
    final InboxResponseInspectorTest.Fixture base = new InboxResponseInspectorTest.Fixture();
    final AuthContextCodec contexts = new AuthContextCodec("v1", base.key, null, null);
    final AuthenticationInboxInspector auth =
        new AuthenticationInboxInspector(base.codec, contexts, new ContextHash());

    Fixture() throws Exception {}

    InboxCleanup service() {
      return service(InboxCleanupNonAuthenticationTest::connection);
    }

    InboxCleanup service(SqlConnectionProvider connections) {
      return new InboxCleanup(
          connections, auth, new NonAuthenticationInboxInspector(base.codec), Set.of("v1"));
    }

    @Override
    public void close() {
      contexts.close();
      base.close();
    }
  }
}
