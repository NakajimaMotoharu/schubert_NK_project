package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.database.MigrationInventory;
import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.messaging.outbound.SqlConnectionProvider;
import dev.codex.schubert.nk.api.security.AuthContextCodec;
import dev.codex.schubert.nk.api.security.ContextHash;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-DB-INBOX-177..192; SS324 12.9/331 3.11/PG-D-141; independent wire and SQL oracle. */
final class QuestionMutationInboxInspectorTest {
  private static final String FIXTURE_VALUE_E91D96ED = "','";
  private static final String FIXTURE_QSBRSP01_9848D404 = "QSBRSP01";
  private static final String FIXTURE_NTCRSP01_CFC2AD25 = "NTCRSP01";
  private static final String FIXTURE_QDLRSP01_1746478A = "QDLRSP01";
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_0200_FC9DB3AC = "0200";
  private static final String FIXTURE_0107_BAC582DD = "0107";
  private static final String FIXTURE_9001_351F7309 = "9001";
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final String FIXTURE_002_F3F2837C = "002";
  private static final String FIXTURE_FROM_SCHUBERT_ASYNC_JOBS_53890648 =
      "from schubert.async_jobs";
  private static final String FIXTURE_FROM_SCHUBERT_QUESTIONS_FE2F38CB = "from schubert.questions";
  private static final String FIXTURE_FROM_SCHUBERT_NOTIFICATIONS_D4F7D30C =
      "from schubert.notifications";
  private static final String FIXTURE_OWNER_USER_ID_CAE361AA = "owner_user_id";
  private static final String FIXTURE_QUESTION_ID_98F02597 = "question_id";
  private static final String FIXTURE_STATE_CHANGED_AT_2B6AF503 = "state_changed_at";
  @TempDir static Path root;
  static ApiLogDatabaseFixture db;
  static String url;
  static final List<String> ROUTES =
      List.of(FIXTURE_QSBRSP01_9848D404, FIXTURE_NTCRSP01_CFC2AD25, FIXTURE_QDLRSP01_1746478A);
  static final Instant TIME = Instant.parse("2026-09-09T00:00:00.123456Z");
  static final Instant SUBMITTED = Instant.parse("2026-09-09T00:00:00.121456Z");
  static final Instant MUTATED = Instant.parse("2026-09-09T00:00:00.122456Z");
  static final String RECEIPT = "0".repeat(25) + "1";
  static final UUID WORK = new UUID(0, 104);
  static final InspectionRun RUN =
      new InspectionRun(new UUID(0, 42), Instant.parse("2026-09-17T00:00:00.123456Z"));

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
    try (var c = db.admin()) {
      url = c.getMetaData().getURL();
    }
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    for (String table :
        List.of(
            "inbox_inspection_progress",
            "request_inbox",
            "batch_runs",
            "mq_outbox",
            "notifications",
            "answers",
            "async_jobs",
            "questions",
            "app_users")) sql("delete from schubert." + table);
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at,version) values"
            + "(7,'First','first','synthetic-unused','USER','ACTIVE',now(),now(),now(),0),"
            + "(8,'Second','second','synthetic-unused','ADMIN','ACTIVE',now(),now(),now(),0)");
    sql(
        "insert into schubert.questions(id,receipt_id,owner_user_id,body,operation_token,submitted_at,is_deleted,deleted_at,deleted_by,version) values"
            + "(9,'"
            + RECEIPT
            + "',7,'Synthetic','"
            + token(FIXTURE_QSBRSP01_9848D404)
            + FIXTURE_VALUE_E91D96ED
            + SUBMITTED
            + "',true,'"
            + MUTATED
            + "',7,1)");
    sql(
        "insert into schubert.async_jobs(id,question_id,owner_user_id,state,message_id,correlation_id,received_at,state_changed_at,cancelled_at,version) values"
            + "(11,9,7,'CANCELLED','"
            + message(FIXTURE_QSBRSP01_9848D404)
            + FIXTURE_VALUE_E91D96ED
            + message(FIXTURE_QSBRSP01_9848D404)
            + FIXTURE_VALUE_E91D96ED
            + SUBMITTED
            + FIXTURE_VALUE_E91D96ED
            + MUTATED
            + FIXTURE_VALUE_E91D96ED
            + MUTATED
            + "',1)");
    sql(
        "insert into schubert.notifications(id,job_id,question_id,owner_user_id,notification_type,state,accepted_at,state_changed_at,created_at,updated_at) values"
            + "(12,11,9,7,'ACCEPTED','CANCELLED','"
            + SUBMITTED
            + FIXTURE_VALUE_E91D96ED
            + MUTATED
            + FIXTURE_VALUE_E91D96ED
            + SUBMITTED
            + FIXTURE_VALUE_E91D96ED
            + MUTATED
            + "')");
    sql(
        "insert into schubert.answers(id,question_id,body,answered_at,provider_type,is_deleted,deleted_at,deleted_by,created_at,updated_at) values"
            + "(13,9,'', '"
            + SUBMITTED
            + "','STUB',true,'"
            + MUTATED
            + "',7,'"
            + SUBMITTED
            + FIXTURE_VALUE_E91D96ED
            + MUTATED
            + "')");
    try (var c = db.admin();
        var s =
            c.prepareStatement(
                "insert into schubert.mq_outbox(id,message_id,correlation_id,destination,layout_id,layout_version,body,status,next_attempt_at,created_at,sent_at) values(14,?,?,'nk.async.work','QWKREQ01','001',?,'SENT',?,?,?)")) {
      s.setObject(1, WORK);
      s.setObject(2, message(FIXTURE_QSBRSP01_9848D404));
      s.setBytes(3, workWire());
      s.setObject(4, TIME.atOffset(java.time.ZoneOffset.UTC));
      s.setObject(5, TIME.atOffset(java.time.ZoneOffset.UTC));
      s.setObject(6, TIME.plusMillis(1).atOffset(java.time.ZoneOffset.UTC));
      assertEquals(1, s.executeUpdate());
    }
    try (var c = db.admin();
        var s =
            c.prepareStatement(
                "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status) values(?,'2026-09-17',?,1,'2026-09-17T00:00:00Z','2026-09-17T00:00:01Z','SUCCESS')")) {
      for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG")) {
        s.setObject(1, RUN.id());
        s.setString(2, step);
        assertEquals(1, s.executeUpdate());
      }
    }
  }

  @Test
  void validMutationReferences() throws Exception {
    assertEquals("SCHBNK01", new String(workWire(), 0, 8, StandardCharsets.US_ASCII));
    assertEquals(
        "0256000064000000000000000000320",
        new String(workWire(), 177, 31, StandardCharsets.US_ASCII));
    try (var f = new Fixture();
        var c = connection()) {
      c.setAutoCommit(false);
      for (String route : ROUTES)
        for (String code : List.of(FIXTURE_0000_876EEFE0, FIXTURE_0200_FC9DB3AC))
          assertTrue(check(f, c, route, code), route + code);
      assertFalse(c.getAutoCommit());
      assertFalse(c.isClosed());
      assertEquals(
          "true/7/1",
          scalar("select is_deleted||'/'||deleted_by||'/'||version from schubert.questions"));
      assertEquals("CANCELLED/1", scalar("select state||'/'||version from schubert.async_jobs"));
      assertEquals("QuestionMutationInboxInspector[REDACTED]", f.inspector.toString());
    }
  }

  @Test
  void submitReferencesAndWork() throws Exception {
    try (var f = new Fixture();
        var c = connection()) {
      c.setAutoCommit(false);
      for (String change :
          List.of(
              "update schubert.questions set owner_user_id=8",
              "update schubert.questions set operation_token='00000000-0000-0000-0000-000000000999'",
              "update schubert.questions set receipt_id=repeat('1',26)",
              "update schubert.questions set submitted_at=submitted_at+interval '1 millisecond'",
              "update schubert.async_jobs set owner_user_id=8",
              "update schubert.async_jobs set message_id='00000000-0000-0000-0000-000000000999'",
              "update schubert.async_jobs set correlation_id='00000000-0000-0000-0000-000000000999'",
              "update schubert.async_jobs set received_at=received_at-interval '1 microsecond'",
              "update schubert.mq_outbox set status='PENDING',sent_at=null",
              "update schubert.mq_outbox set status='ERROR',sent_at=null",
              "update schubert.mq_outbox set lease_owner='synthetic',lease_until=now()",
              "update schubert.mq_outbox set sent_at='2026-09-09T00:00:00.123455Z'",
              "delete from schubert.mq_outbox")) {
        sql(change);
        assertFalse(check(f, c, FIXTURE_QSBRSP01_9848D404, FIXTURE_0000_876EEFE0), change);
        reset();
      }
      for (var change :
          List.of(
              Map.entry(24, new UUID(0, 999).toString()),
              Map.entry(60, new UUID(0, 999).toString()),
              Map.entry(256, "1".repeat(26)),
              Map.entry(282, "000000000008"),
              Map.entry(294, "000000000010"),
              Map.entry(319, "X"))) {
        byte[] wire = workWire();
        put(wire, change.getKey(), change.getValue());
        workBody(wire);
        assertFalse(
            check(f, c, FIXTURE_QSBRSP01_9848D404, FIXTURE_0000_876EEFE0),
            "work offset" + change.getKey());
        reset();
      }
      sql("update schubert.app_users set role='ADMIN',status='DISABLED' where id=7");
      assertTrue(check(f, c, FIXTURE_QSBRSP01_9848D404, FIXTURE_0000_876EEFE0));
    }
  }

  @Test
  void cancellationHistory() throws Exception {
    try (var f = new Fixture();
        var c = connection()) {
      c.setAutoCommit(false);
      sql("delete from schubert.notifications");
      assertTrue(check(f, c, FIXTURE_NTCRSP01_CFC2AD25, FIXTURE_0000_876EEFE0));
      reset();
      for (String change :
          List.of(
              "update schubert.async_jobs set owner_user_id=8",
              "update schubert.async_jobs set version=0",
              "update schubert.async_jobs set state='RECEIVED',cancelled_at=null",
              "update schubert.async_jobs set state_changed_at=state_changed_at+interval '1 microsecond'",
              "update schubert.async_jobs set cancelled_at=cancelled_at+interval '1 millisecond'",
              "update schubert.notifications set owner_user_id=8",
              "update schubert.notifications set state='PROCESSING'",
              "update schubert.notifications set state_changed_at=state_changed_at+interval '1 microsecond'")) {
        sql(change);
        assertFalse(check(f, c, FIXTURE_NTCRSP01_CFC2AD25, FIXTURE_0000_876EEFE0), change);
        reset();
      }
      sql("update schubert.app_users set status='DISABLED' where id=7");
      assertTrue(check(f, c, FIXTURE_NTCRSP01_CFC2AD25, FIXTURE_0200_FC9DB3AC));
    }
  }

  @Test
  void deletionHistoryAndAnswers() throws Exception {
    try (var f = new Fixture();
        var c = connection()) {
      c.setAutoCommit(false);
      sql("delete from schubert.answers");
      assertTrue(check(f, c, FIXTURE_QDLRSP01_1746478A, FIXTURE_0000_876EEFE0));
      reset();
      sql("update schubert.questions set deleted_by=8,owner_user_id=8");
      sql("update schubert.answers set deleted_by=8");
      assertTrue(check(f, c, FIXTURE_QDLRSP01_1746478A, FIXTURE_0200_FC9DB3AC));
      assertFalse(check(f, c, FIXTURE_QDLRSP01_1746478A, FIXTURE_0000_876EEFE0));
      reset();
      for (String change :
          List.of(
              "update schubert.questions set is_deleted=false,deleted_at=null,deleted_by=null",
              "update schubert.questions set version=0",
              "update schubert.questions set deleted_at=deleted_at+interval '1 millisecond'",
              "update schubert.answers set is_deleted=false,deleted_at=null,deleted_by=null",
              "update schubert.answers set deleted_by=8",
              "update schubert.answers set deleted_at=deleted_at+interval '1 microsecond'")) {
        sql(change);
        assertFalse(check(f, c, FIXTURE_QDLRSP01_1746478A, FIXTURE_0000_876EEFE0), change);
        reset();
      }
      sql("delete from schubert.notifications");
      sql("delete from schubert.questions");
      assertFalse(check(f, c, FIXTURE_QDLRSP01_1746478A, FIXTURE_0000_876EEFE0));
      assertFalse(check(f, c, FIXTURE_NTCRSP01_CFC2AD25, FIXTURE_0000_876EEFE0));
      assertFalse(check(f, c, FIXTURE_QSBRSP01_9848D404, FIXTURE_0000_876EEFE0));
    }
  }

  @Test
  void exactStoredProfiles() throws Exception {
    try (var f = new Fixture();
        var c = connection()) {
      c.setAutoCommit(false);
      for (String route : ROUTES)
        for (String code :
            List.of(
                FIXTURE_0000_876EEFE0,
                "0100",
                "0101",
                "0102",
                "0103",
                "0104",
                "0105",
                "0106",
                FIXTURE_0107_BAC582DD,
                FIXTURE_0200_FC9DB3AC,
                "9000",
                FIXTURE_9001_351F7309)) {
          boolean expected =
              Set.of(FIXTURE_0000_876EEFE0, FIXTURE_0200_FC9DB3AC, FIXTURE_9001_351F7309)
                      .contains(code)
                  || (route.equals(FIXTURE_QSBRSP01_9848D404)
                      ? code.equals("0100")
                      : code.equals("0104"))
                  || (route.equals(FIXTURE_NTCRSP01_CFC2AD25)
                      && code.equals(FIXTURE_0107_BAC582DD));
          assertEquals(expected, check(f, c, route, code), route + code);
        }
      for (String state :
          List.of("PROCESSING", "COMPLETED", "ERROR", "RECEIVED", "CANCELLED", "UNKNOWN", "")) {
        byte[] wire =
            golden(
                FIXTURE_NTCRSP01_CFC2AD25,
                FIXTURE_0107_BAC582DD,
                message(FIXTURE_NTCRSP01_CFC2AD25));
        Arrays.fill(wire, 256, 268, (byte) ' ');
        put(wire, 256, state);
        assertEquals(
            Set.of("PROCESSING", "COMPLETED", "ERROR").contains(state),
            f.inspector.isConsistent(
                c,
                id(FIXTURE_NTCRSP01_CFC2AD25),
                snapshot(
                    f,
                    id(FIXTURE_NTCRSP01_CFC2AD25),
                    FIXTURE_0107_BAC582DD,
                    wire,
                    token(FIXTURE_NTCRSP01_CFC2AD25)),
                token(FIXTURE_NTCRSP01_CFC2AD25)),
            state);
      }
      for (String route : ROUTES) {
        var s =
            snapshot(
                f,
                id(route),
                FIXTURE_9001_351F7309,
                golden(route, FIXTURE_9001_351F7309, message(route)),
                token(route));
        var bad =
            new InboxCompletion(
                s.state(), ref(route), route, FIXTURE_001_A3FEAA64, s.responseSnapshot(), TIME);
        assertFalse(f.inspector.isConsistent(c, id(route), bad, token(route)));
      }
    }
  }

  @Test
  void wireAndMetadataDamage() throws Exception {
    try (var f = new Fixture();
        var c = connection()) {
      c.setAutoCommit(false);
      for (String route : ROUTES) {
        for (int pos :
            new int[] {
              0,
              8,
              11,
              19,
              22,
              23,
              60,
              96,
              177,
              187,
              193,
              200,
              252,
              golden(route, FIXTURE_0000_876EEFE0, message(route)).length - 1
            }) {
          byte[] wire = golden(route, FIXTURE_0000_876EEFE0, message(route));
          wire[pos] = (byte) '!';
          assertFalse(
              f.inspector.isConsistent(
                  c,
                  id(route),
                  snapshot(f, id(route), FIXTURE_0000_876EEFE0, wire, token(route)),
                  token(route)),
              route + pos);
        }
        var original =
            snapshot(
                f,
                id(route),
                FIXTURE_0000_876EEFE0,
                golden(route, FIXTURE_0000_876EEFE0, message(route)),
                token(route));
        for (var identity :
            List.of(
                ResponseSnapshotIdentity.anonymous(message(route), route, FIXTURE_001_A3FEAA64),
                ResponseSnapshotIdentity.authenticated(
                    new UUID(0, 999), route, FIXTURE_001_A3FEAA64, 7),
                ResponseSnapshotIdentity.authenticated(
                    message(route), route, FIXTURE_001_A3FEAA64, 8),
                ResponseSnapshotIdentity.authenticated(
                    message(route), route, FIXTURE_002_F3F2837C, 7),
                ResponseSnapshotIdentity.authenticated(
                    message(route), "GAMRSP01", FIXTURE_001_A3FEAA64, 7)))
          assertFalse(f.inspector.isConsistent(c, identity, original, token(route)));
        assertFalse(
            f.inspector.isConsistent(
                c,
                id(route),
                new InboxCompletion(
                    original.state(),
                    original.resultReference(),
                    route,
                    FIXTURE_002_F3F2837C,
                    original.responseSnapshot(),
                    TIME),
                token(route)));
        assertFalse(
            f.inspector.isConsistent(
                c,
                id(route),
                new InboxCompletion(
                    original.state(),
                    original.resultReference(),
                    route,
                    FIXTURE_001_A3FEAA64,
                    Optional.empty(),
                    TIME),
                token(route)));
        var old =
            f.base.saved(
                id(route),
                golden(route, FIXTURE_0000_876EEFE0, message(route)),
                InboxCompletionState.COMPLETED,
                TIME);
        assertFalse(
            f.inspector.isConsistent(
                c,
                id(route),
                new InboxCompletion(
                    old.state(),
                    ref(route),
                    route,
                    FIXTURE_001_A3FEAA64,
                    old.responseSnapshot(),
                    TIME),
                token(route)));
        byte[] cipher = original.responseSnapshot().orElseThrow().ciphertext();
        cipher[cipher.length - 1] ^= 1;
        assertFalse(
            f.inspector.isConsistent(
                c,
                id(route),
                new InboxCompletion(
                    original.state(),
                    ref(route),
                    route,
                    FIXTURE_001_A3FEAA64,
                    Optional.of(new EncryptedResponseSnapshot("v1", cipher)),
                    TIME),
                token(route)));
      }
    }
  }

  @Test
  void nullAndJdbcFailures() throws Exception {
    try (var f = new Fixture();
        var c = connection()) {
      assertThrows(NullPointerException.class, () -> new QuestionMutationInboxInspector(null));
      var saved =
          snapshot(
              f,
              id(FIXTURE_QSBRSP01_9848D404),
              FIXTURE_0000_876EEFE0,
              golden(
                  FIXTURE_QSBRSP01_9848D404,
                  FIXTURE_0000_876EEFE0,
                  message(FIXTURE_QSBRSP01_9848D404)),
              token(FIXTURE_QSBRSP01_9848D404));
      assertThrows(
          NullPointerException.class,
          () ->
              f.inspector.isConsistent(
                  null, id(FIXTURE_QSBRSP01_9848D404), saved, token(FIXTURE_QSBRSP01_9848D404)));
      assertThrows(
          NullPointerException.class,
          () -> f.inspector.isConsistent(c, null, saved, token(FIXTURE_QSBRSP01_9848D404)));
      assertThrows(
          NullPointerException.class,
          () ->
              f.inspector.isConsistent(
                  c, id(FIXTURE_QSBRSP01_9848D404), null, token(FIXTURE_QSBRSP01_9848D404)));
      assertThrows(
          NullPointerException.class,
          () -> f.inspector.isConsistent(c, id(FIXTURE_QSBRSP01_9848D404), saved, null));
      assertFalse(
          f.inspector.isConsistent(
              c, id(FIXTURE_QSBRSP01_9848D404), saved, token(FIXTURE_QSBRSP01_9848D404)));
      c.setAutoCommit(false);
      for (String route : ROUTES) {
        for (String fault :
            List.of(
                "getAutoCommit",
                "prepareStatement",
                "setObject",
                "executeQuery",
                "next",
                "getObject",
                "getString",
                "resultClose",
                "statementClose")) {
          if (route.equals(FIXTURE_QDLRSP01_1746478A) && fault.equals("getString"))
            continue; // No string projection.
          var p = new MaintenanceJdbcProbe();
          p.selectedSql =
              route.equals(FIXTURE_NTCRSP01_CFC2AD25)
                  ? FIXTURE_FROM_SCHUBERT_ASYNC_JOBS_53890648
                  : FIXTURE_FROM_SCHUBERT_QUESTIONS_FE2F38CB;
          p.fault = fault;
          assertFalse(check(f, p.wrap(c), route, FIXTURE_0000_876EEFE0), route + fault);
        }
      }
      for (var target :
          List.of(
              Map.entry(FIXTURE_QSBRSP01_9848D404, FIXTURE_FROM_SCHUBERT_QUESTIONS_FE2F38CB),
              Map.entry(FIXTURE_QSBRSP01_9848D404, FIXTURE_FROM_SCHUBERT_ASYNC_JOBS_53890648),
              Map.entry(FIXTURE_QSBRSP01_9848D404, "maintenance_read_question_work"),
              Map.entry(FIXTURE_NTCRSP01_CFC2AD25, FIXTURE_FROM_SCHUBERT_ASYNC_JOBS_53890648),
              Map.entry(FIXTURE_NTCRSP01_CFC2AD25, FIXTURE_FROM_SCHUBERT_NOTIFICATIONS_D4F7D30C),
              Map.entry(FIXTURE_QDLRSP01_1746478A, FIXTURE_FROM_SCHUBERT_QUESTIONS_FE2F38CB),
              Map.entry(FIXTURE_QDLRSP01_1746478A, "from schubert.answers"))) {
        var columns =
            switch (target.getValue()) {
              case FIXTURE_FROM_SCHUBERT_QUESTIONS_FE2F38CB ->
                  target.getKey().equals(FIXTURE_QSBRSP01_9848D404)
                      ? List.of(
                          "id",
                          FIXTURE_OWNER_USER_ID_CAE361AA,
                          "operation_token",
                          "receipt_id",
                          "submitted_at")
                      : List.of("id", "is_deleted", "deleted_by", "deleted_at", "version");
              case FIXTURE_FROM_SCHUBERT_ASYNC_JOBS_53890648 ->
                  target.getKey().equals(FIXTURE_QSBRSP01_9848D404)
                      ? List.of(
                          "id",
                          FIXTURE_QUESTION_ID_98F02597,
                          FIXTURE_OWNER_USER_ID_CAE361AA,
                          "message_id",
                          "correlation_id",
                          "received_at")
                      : List.of(
                          "id",
                          FIXTURE_QUESTION_ID_98F02597,
                          FIXTURE_OWNER_USER_ID_CAE361AA,
                          "state",
                          "cancelled_at",
                          FIXTURE_STATE_CHANGED_AT_2B6AF503,
                          "version");
              case FIXTURE_FROM_SCHUBERT_NOTIFICATIONS_D4F7D30C ->
                  List.of(
                      "job_id",
                      FIXTURE_QUESTION_ID_98F02597,
                      FIXTURE_OWNER_USER_ID_CAE361AA,
                      "state",
                      FIXTURE_STATE_CHANGED_AT_2B6AF503);
              case "from schubert.answers" ->
                  List.of(FIXTURE_QUESTION_ID_98F02597, "is_deleted", "deleted_by", "deleted_at");
              default ->
                  List.of("message_id", "correlation_id", "status", "sent_at", "leased", "body");
            };
        for (String column : columns) {
          var p = new MaintenanceJdbcProbe();
          p.selectedSql = target.getValue();
          p.columns.put(column, null);
          assertFalse(check(f, p.wrap(c), target.getKey(), FIXTURE_0000_876EEFE0), target + column);
          assertTrue(p.selectedStatements > 0);
        }
        var p = new MaintenanceJdbcProbe();
        p.selectedSql = target.getValue();
        p.duplicate = true;
        assertFalse(
            check(f, p.wrap(c), target.getKey(), FIXTURE_0000_876EEFE0), "duplicate" + target);
        for (String fault :
            List.of(
                "prepareStatement",
                "executeQuery",
                "next",
                "getObject",
                "resultClose",
                "statementClose")) {
          var failing = new MaintenanceJdbcProbe();
          failing.selectedSql = target.getValue();
          failing.fault = fault;
          assertFalse(
              check(f, failing.wrap(c), target.getKey(), FIXTURE_0000_876EEFE0), target + fault);
          assertTrue(failing.selectedStatements > 0);
        }
        for (String column : columns) {
          if (Set.of(
                  "id",
                  FIXTURE_QUESTION_ID_98F02597,
                  "job_id",
                  FIXTURE_OWNER_USER_ID_CAE361AA,
                  "deleted_by",
                  "version")
              .contains(column))
            for (long value : new long[] {0, 1_000_000_000_000L}) {
              var invalid = new MaintenanceJdbcProbe();
              invalid.selectedSql = target.getValue();
              invalid.columns.put(column, value);
              assertFalse(
                  check(f, invalid.wrap(c), target.getKey(), FIXTURE_0000_876EEFE0),
                  target + column + value);
            }
          if (column.endsWith("_at"))
            for (OffsetDateTime invalidTime :
                List.of(
                    OffsetDateTime.of(0, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC),
                    OffsetDateTime.of(10000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC),
                    OffsetDateTime.of(LocalDateTime.MAX, ZoneOffset.MIN))) {
              var invalid = new MaintenanceJdbcProbe();
              invalid.selectedSql = target.getValue();
              invalid.columns.put(column, invalidTime);
              assertFalse(
                  check(f, invalid.wrap(c), target.getKey(), FIXTURE_0000_876EEFE0),
                  target + column + invalidTime);
            }
        }
      }
      for (var changed :
          List.of(
              List.of(FIXTURE_QSBRSP01_9848D404, FIXTURE_FROM_SCHUBERT_QUESTIONS_FE2F38CB, "id"),
              List.of(
                  FIXTURE_QSBRSP01_9848D404,
                  FIXTURE_FROM_SCHUBERT_ASYNC_JOBS_53890648,
                  FIXTURE_QUESTION_ID_98F02597),
              List.of(FIXTURE_NTCRSP01_CFC2AD25, FIXTURE_FROM_SCHUBERT_ASYNC_JOBS_53890648, "id"),
              List.of(
                  FIXTURE_NTCRSP01_CFC2AD25,
                  FIXTURE_FROM_SCHUBERT_NOTIFICATIONS_D4F7D30C,
                  "job_id"),
              List.of(
                  FIXTURE_NTCRSP01_CFC2AD25,
                  FIXTURE_FROM_SCHUBERT_NOTIFICATIONS_D4F7D30C,
                  FIXTURE_QUESTION_ID_98F02597),
              List.of(FIXTURE_QDLRSP01_1746478A, FIXTURE_FROM_SCHUBERT_QUESTIONS_FE2F38CB, "id"),
              List.of(
                  FIXTURE_QDLRSP01_1746478A,
                  "from schubert.answers",
                  FIXTURE_QUESTION_ID_98F02597))) {
        var p = new MaintenanceJdbcProbe();
        p.selectedSql = changed.get(1);
        p.columns.put(changed.get(2), 8L);
        assertFalse(check(f, p.wrap(c), changed.get(0), FIXTURE_0000_876EEFE0), changed.toString());
      }
      for (String route : List.of(FIXTURE_NTCRSP01_CFC2AD25, FIXTURE_QDLRSP01_1746478A)) {
        var p = new MaintenanceJdbcProbe();
        p.selectedSql =
            route.equals(FIXTURE_NTCRSP01_CFC2AD25)
                ? FIXTURE_FROM_SCHUBERT_ASYNC_JOBS_53890648
                : FIXTURE_FROM_SCHUBERT_QUESTIONS_FE2F38CB;
        p.columns.put(
            route.equals(FIXTURE_NTCRSP01_CFC2AD25) ? "state" : "is_deleted",
            route.equals(FIXTURE_NTCRSP01_CFC2AD25) ? "RECEIVED" : false);
        assertFalse(check(f, p.wrap(c), route, FIXTURE_0000_876EEFE0));
        p.columns.clear();
        p.columns.put(
            route.equals(FIXTURE_NTCRSP01_CFC2AD25) ? "cancelled_at" : "deleted_at",
            OffsetDateTime.ofInstant(TIME.plusNanos(1000), ZoneOffset.UTC));
        if (route.equals(FIXTURE_NTCRSP01_CFC2AD25))
          p.columns.put(
              FIXTURE_STATE_CHANGED_AT_2B6AF503,
              OffsetDateTime.ofInstant(TIME.plusNanos(1000), ZoneOffset.UTC));
        assertFalse(check(f, p.wrap(c), route, FIXTURE_0000_876EEFE0));
        if (route.equals(FIXTURE_NTCRSP01_CFC2AD25)) {
          p.columns.put("cancelled_at", OffsetDateTime.ofInstant(SUBMITTED, ZoneOffset.UTC));
          p.columns.put(
              FIXTURE_STATE_CHANGED_AT_2B6AF503,
              OffsetDateTime.ofInstant(SUBMITTED, ZoneOffset.UTC));
          assertFalse(check(f, p.wrap(c), route, FIXTURE_0000_876EEFE0));
        }
      }
      for (var change :
          List.of(
              Map.entry("message_id", message(FIXTURE_QSBRSP01_9848D404)),
              Map.entry("correlation_id", new UUID(0, 999)))) {
        var p = new MaintenanceJdbcProbe();
        p.selectedSql = "maintenance_read_question_work";
        p.columns.put(change.getKey(), change.getValue());
        assertFalse(check(f, p.wrap(c), FIXTURE_QSBRSP01_9848D404, FIXTURE_0000_876EEFE0));
      }
      for (byte[] body :
          List.of(
              new byte[0],
              Arrays.copyOf(workWire(), 321),
              golden(
                  FIXTURE_QSBRSP01_9848D404,
                  FIXTURE_0000_876EEFE0,
                  message(FIXTURE_QSBRSP01_9848D404)))) {
        var p = new MaintenanceJdbcProbe();
        p.selectedSql = "maintenance_read_question_work";
        p.columns.put("body", body);
        assertFalse(check(f, p.wrap(c), FIXTURE_QSBRSP01_9848D404, FIXTURE_0000_876EEFE0));
      }
      var future = new MaintenanceJdbcProbe();
      future.selectedSql = FIXTURE_FROM_SCHUBERT_QUESTIONS_FE2F38CB;
      future.columns.put(
          "submitted_at", OffsetDateTime.ofInstant(TIME.plusNanos(1000), ZoneOffset.UTC));
      byte[] wire =
          golden(
              FIXTURE_QSBRSP01_9848D404, FIXTURE_0000_876EEFE0, message(FIXTURE_QSBRSP01_9848D404));
      put(wire, 294, "20260909090000123");
      assertFalse(
          f.inspector.isConsistent(
              future.wrap(c),
              id(FIXTURE_QSBRSP01_9848D404),
              snapshot(
                  f,
                  id(FIXTURE_QSBRSP01_9848D404),
                  FIXTURE_0000_876EEFE0,
                  wire,
                  token(FIXTURE_QSBRSP01_9848D404)),
              token(FIXTURE_QSBRSP01_9848D404)));
      c.rollback();
      f.base.codec.close();
      assertFalse(check(f, c, FIXTURE_QDLRSP01_1746478A, FIXTURE_0000_876EEFE0));
    }
  }

  @Test
  void equalTimeTargetsRemainDistinct() throws Exception {
    try (var f = new Fixture();
        var c = connection()) {
      c.setAutoCommit(false);
      for (String route : ROUTES) {
        var original =
            snapshot(
                f,
                id(route),
                FIXTURE_0000_876EEFE0,
                golden(route, FIXTURE_0000_876EEFE0, message(route)),
                token(route));
        var otherLayout =
            route.equals(FIXTURE_QSBRSP01_9848D404)
                ? FIXTURE_QDLRSP01_1746478A
                : FIXTURE_QSBRSP01_9848D404;
        assertFalse(
            f.inspector.isConsistent(
                c,
                id(route),
                new InboxCompletion(
                    original.state(),
                    original.resultReference(),
                    otherLayout,
                    FIXTURE_001_A3FEAA64,
                    original.responseSnapshot(),
                    TIME),
                token(route)));
        assertFalse(
            f.inspector.isConsistent(
                c,
                ResponseSnapshotIdentity.authenticated(
                    message(route), route, FIXTURE_002_F3F2837C, 7),
                new InboxCompletion(
                    original.state(),
                    original.resultReference(),
                    route,
                    FIXTURE_002_F3F2837C,
                    original.responseSnapshot(),
                    TIME),
                token(route)));
        for (var change :
            List.of(
                Map.entry(60, new UUID(0, 999).toString()), Map.entry(96, "20260909090000124"))) {
          byte[] wire = golden(route, FIXTURE_0000_876EEFE0, message(route));
          put(wire, change.getKey(), change.getValue());
          assertFalse(
              f.inspector.isConsistent(
                  c,
                  id(route),
                  snapshot(f, id(route), FIXTURE_0000_876EEFE0, wire, token(route)),
                  token(route)));
        }
        for (UUID token :
            List.of(new UUID(1, token(route).getLeastSignificantBits()), new UUID(0, 999)))
          assertFalse(f.inspector.isConsistent(c, id(route), original, token));
        for (var ref :
            List.of(
                InboxResultReference.none(),
                InboxResultReference.authSession(WORK),
                InboxResultReference.numeric(InboxResultReferenceType.USER, 9),
                InboxResultReference.numeric(InboxResultReferenceType.QUESTION, 8),
                InboxResultReference.numeric(InboxResultReferenceType.JOB, 8)))
          assertFalse(
              f.inspector.isConsistent(
                  c,
                  id(route),
                  new InboxCompletion(
                      original.state(),
                      ref,
                      route,
                      FIXTURE_001_A3FEAA64,
                      original.responseSnapshot(),
                      TIME),
                  token(route)));
      }
      byte[] wrongId =
          golden(
              FIXTURE_QSBRSP01_9848D404, FIXTURE_0000_876EEFE0, message(FIXTURE_QSBRSP01_9848D404));
      put(wrongId, 282, "000000000008");
      assertFalse(
          f.inspector.isConsistent(
              c,
              id(FIXTURE_QSBRSP01_9848D404),
              snapshot(
                  f,
                  id(FIXTURE_QSBRSP01_9848D404),
                  FIXTURE_0000_876EEFE0,
                  wrongId,
                  token(FIXTURE_QSBRSP01_9848D404)),
              token(FIXTURE_QSBRSP01_9848D404)));
    }
  }

  @Test
  void leastPrivilegeCatalog() throws Exception {
    assertEquals(
        "nk_owner/true/search_path=pg_catalog, schubert,TimeZone=UTC",
        scalar(
            "select pg_get_userbyid(proowner)||'/'||prosecdef::text||'/'||array_to_string(proconfig,',') from pg_proc where oid='schubert.maintenance_read_question_work(uuid)'::regprocedure"));
    for (String role :
        List.of(
            "schubert_app",
            "schubert_batch",
            "schubert_backup",
            "schubert_web_session",
            "schubert_ops_ro"))
      denied(
          role,
          "select * from schubert.maintenance_read_question_work('"
              + message(FIXTURE_QSBRSP01_9848D404)
              + "')");
    for (String query :
        List.of(
            "select body from schubert.questions",
            "select body from schubert.answers",
            "select body from schubert.mq_outbox",
            "select password_hash from schubert.app_users",
            "delete from schubert.questions",
            "update schubert.async_jobs set version=2")) denied("schubert_inbox_inspector", query);
    assertEquals(
        "false",
        scalar(
            "select has_function_privilege('schubert_batch','schubert.maintenance_delete_inbox(uuid,timestamptz,uuid,text,bytea)','EXECUTE')::text"));
  }

  @Test
  void uniqueWorkProjection() throws Exception {
    assertEquals(
        "23505",
        assertThrows(
                SQLException.class,
                () ->
                    sql(
                        "insert into schubert.mq_outbox(message_id,correlation_id,destination,layout_id,layout_version,body,status,next_attempt_at,created_at,sent_at) select '00000000-0000-0000-0000-000000000999',correlation_id,destination,layout_id,layout_version,body,status,next_attempt_at,created_at,sent_at from schubert.mq_outbox"))
            .getSQLState());
    sql(
        "insert into schubert.mq_outbox(message_id,correlation_id,destination,layout_id,layout_version,body,status,next_attempt_at,created_at,sent_at,dlq_original_message_id,dlq_original_transport_id,dlq_delivery_count,dlq_error_code,dlq_detected_at) select '00000000-0000-0000-0000-000000000999',correlation_id,'nk.dead.letter',layout_id,layout_version,body,status,next_attempt_at,created_at,sent_at,message_id,'ID:independent-original',4,'QUESTION_RETRY_EXHAUSTED',created_at from schubert.mq_outbox");
    assertEquals(
        "23514",
        assertThrows(
                SQLException.class,
                () -> sql("update schubert.mq_outbox set destination='nk.dead.letter' where id=14"))
            .getSQLState());
    try (var c = connection();
        var s = c.createStatement()) {
      assertEquals(
          "22023",
          assertThrows(
                  SQLException.class,
                  () ->
                      s.executeQuery("select * from schubert.maintenance_read_question_work(null)"))
              .getSQLState());
      for (String change :
          List.of("layout_id='GAMREQ01'", "layout_version='002'", "body=decode('00','hex')")) {
        sql("update schubert.mq_outbox set " + change + " where id=14");
        try (var r =
            s.executeQuery(
                "select count(*) from schubert.maintenance_read_question_work('"
                    + message(FIXTURE_QSBRSP01_9848D404)
                    + "')")) {
          assertTrue(r.next());
          assertEquals(0, r.getInt(1));
        }
        reset();
      }
    }
  }

  @Test
  void referencesAndPhantomsStayLocked() throws Exception {
    try (var f = new Fixture()) {
      for (String route : ROUTES) {
        seed(f, route, FIXTURE_0000_876EEFE0, message(route), token(route));
        try (var held = connection();
            var other = db.admin();
            var s =
                held.prepareStatement(
                    "select message_id from schubert.maintenance_next_inbox(?,?,null)")) {
          held.setAutoCommit(false);
          s.setObject(1, RUN.id());
          s.setObject(2, RUN.cutoff().atOffset(java.time.ZoneOffset.UTC));
          try (var rows = s.executeQuery()) {
            assertTrue(rows.next());
            assertEquals(message(route), rows.getObject(1, UUID.class));
          }
          try (var os = other.createStatement()) {
            os.execute("set lock_timeout='50ms'");
            for (String change :
                route.equals(FIXTURE_NTCRSP01_CFC2AD25)
                    ? List.of(
                        "update schubert.async_jobs set version=2",
                        "update schubert.notifications set updated_at=now()")
                    : List.of(
                        "update schubert.questions set version=2",
                        "update schubert.answers set updated_at=now()",
                        "update schubert.async_jobs set version=2"))
              assertEquals(
                  "55P03",
                  assertThrows(SQLException.class, () -> os.executeUpdate(change)).getSQLState());
          }
          held.rollback();
        }
        reset();
      }
      for (String route : List.of(FIXTURE_QDLRSP01_1746478A, FIXTURE_NTCRSP01_CFC2AD25)) {
        sql("delete from schubert.answers");
        sql("delete from schubert.notifications");
        seed(f, route, FIXTURE_0000_876EEFE0, message(route), token(route));
        try (var held = connection();
            var other = db.admin();
            var s =
                held.prepareStatement(
                    "select message_id from schubert.maintenance_next_inbox(?,?,null)")) {
          held.setAutoCommit(false);
          s.setObject(1, RUN.id());
          s.setObject(2, RUN.cutoff().atOffset(java.time.ZoneOffset.UTC));
          try (var rows = s.executeQuery()) {
            assertTrue(rows.next());
          }
          String insert =
              route.equals(FIXTURE_QDLRSP01_1746478A)
                  ? "insert into schubert.answers(question_id,body,answered_at,provider_type,created_at,updated_at) values(9,'',now(),'STUB',now(),now())"
                  : "insert into schubert.notifications(job_id,question_id,owner_user_id,notification_type,state,accepted_at,state_changed_at,created_at,updated_at) values(11,9,7,'ACCEPTED','CANCELLED',now(),now(),now(),now())";
          try (var os = other.createStatement()) {
            os.execute("set lock_timeout='50ms'");
            assertEquals(
                "55P03",
                assertThrows(SQLException.class, () -> os.executeUpdate(insert)).getSQLState());
            held.rollback();
            assertEquals(1, os.executeUpdate(insert));
          }
        }
        reset();
      }
    }
  }

  @Test
  void canonicalRoutesAndRetention() throws Exception {
    try (var f = new Fixture()) {
      for (String route : ROUTES) {
        for (long micros : new long[] {-1, 0, 1}) {
          seed(f, route, FIXTURE_0000_876EEFE0, message(route), token(route));
          sql(
              "update schubert.request_inbox set expires_at=completed_at+interval '168 hours'+interval '"
                  + micros
                  + " microseconds'");
          assertEquals(
              micros < 0 ? InspectionStep.Outcome.PROTECTED : InspectionStep.Outcome.DELETED,
              f.service().inspectNext(RUN, Optional.empty()).outcome());
          sql("delete from schubert.request_inbox");
        }
        seed(f, route, FIXTURE_0000_876EEFE0, message(route), token(route));
        sql("update schubert.request_inbox set expires_at='" + RUN.cutoff() + "'");
        assertEquals(
            InspectionStep.Outcome.END, f.service().inspectNext(RUN, Optional.empty()).outcome());
        reset();
        seed(f, route, FIXTURE_0000_876EEFE0, message(route), token(route));
        var p = new MaintenanceJdbcProbe();
        p.columns.put("operation_token", null);
        assertEquals(
            InspectionStep.Outcome.PROTECTED,
            f.service(() -> p.wrap(connection())).inspectNext(RUN, Optional.empty()).outcome());
        sql("update schubert.batch_runs set status='FAILED'");
        assertThrows(
            InboxMaintenanceException.class, () -> f.service().inspectNext(RUN, Optional.empty()));
        assertEquals("1", count());
        reset();
      }
    }
  }

  @Test
  void ownedAtomicFailures() throws Exception {
    try (var f = new Fixture()) {
      for (String route : ROUTES)
        for (String fault :
            List.of(
                "executeQuery", "getObject", "resultClose", "statementClose", "commit", "close")) {
          seed(f, route, FIXTURE_0000_876EEFE0, message(route), token(route));
          var p = new MaintenanceJdbcProbe();
          p.selectedSql = "maintenance_delete_inbox";
          p.fault = fault;
          var failure =
              assertThrows(
                  InboxMaintenanceException.class,
                  () -> f.service(() -> p.wrap(connection())).inspectStoredNext(RUN));
          assertNull(failure.getCause());
          assertEquals(0, failure.getSuppressed().length);
          assertEquals(1, p.closes);
          assertEquals(0, p.saves);
          assertEquals(fault.equals("close") ? "0" : "1", count());
          var end = f.service().runChunk(RUN, 10);
          assertTrue(end.complete());
          assertEquals(1, end.deleted());
          assertEquals(1, end.inspected());
          reset();
        }
      seed(
          f,
          FIXTURE_QDLRSP01_1746478A,
          FIXTURE_0000_876EEFE0,
          message(FIXTURE_QDLRSP01_1746478A),
          token(FIXTURE_QDLRSP01_1746478A));
      var p = new MaintenanceJdbcProbe();
      p.fault = "commit";
      p.commitAfter = true;
      assertThrows(
          InboxMaintenanceException.class,
          () -> f.service(() -> p.wrap(connection())).inspectStoredNext(RUN));
      assertEquals("0", count());
      var end = f.service().runChunk(RUN, 10);
      assertTrue(end.complete());
      assertEquals(1, end.deleted());
    }
  }

  @Test
  void durableMixedResume() throws Exception {
    try (var f = new Fixture()) {
      for (String route : ROUTES) {
        seed(f, route, FIXTURE_0000_876EEFE0, message(route), token(route));
        seed(
            f,
            route,
            FIXTURE_9001_351F7309,
            new UUID(0, message(route).getLeastSignificantBits() + 1000),
            new UUID(0, token(route).getLeastSignificantBits() + 1000));
        seed(
            f,
            route,
            FIXTURE_9001_351F7309,
            new UUID(0, message(route).getLeastSignificantBits() + 2000),
            new UUID(0, token(route).getLeastSignificantBits() + 2000));
      }
      sql(
          "update schubert.request_inbox set response_key_version='unknown' where message_id>'00000000-0000-0000-0000-0000000007d0'");
      var partial = f.service().runChunk(RUN, 4);
      assertFalse(partial.complete());
      assertEquals(4, partial.deleted());
      var end = f.service().runChunk(RUN, 10);
      assertTrue(end.complete());
      assertEquals(9, end.inspected());
      assertEquals(6, end.deleted());
      assertEquals(3, end.protectedRows());
      assertEquals(end, f.service().runChunk(RUN, 10));
      assertEquals("3", count());
    }
  }

  @Test
  void concurrentReferencesStayIndependent() throws Exception {
    try (var f = new Fixture();
        var executor = Executors.newFixedThreadPool(10)) {
      var calls = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 100; i++) {
        String route = ROUTES.get(i % 3);
        calls.add(
            () -> {
              try (var c = connection()) {
                c.setAutoCommit(false);
                return check(f, c, route, FIXTURE_0000_876EEFE0);
              }
            });
      }
      for (var future : executor.invokeAll(calls)) assertTrue(future.get());
      for (String route : ROUTES)
        seed(f, route, FIXTURE_0000_876EEFE0, message(route), token(route));
      var cleanup = new ArrayList<Callable<InspectionProgress>>();
      for (int i = 0; i < 10; i++) cleanup.add(() -> f.service().runChunk(RUN, 10));
      int completed = 0;
      for (var future : executor.invokeAll(cleanup)) {
        try {
          if (future.get().complete()) completed++;
        } catch (ExecutionException failure) {
          assertInstanceOf(InboxMaintenanceException.class, failure.getCause());
        }
      }
      assertTrue(completed > 0);
      var end = f.service().runChunk(RUN, 10);
      assertEquals(3, end.inspected());
      assertEquals(3, end.deleted());
      assertEquals(0, end.protectedRows());
    }
  }

  @Test
  void appendOnlyInventory() throws Exception {
    assertEquals(
        MigrationInventory.COUNT_TEXT,
        scalar(
            "select count(*) from schubert_meta.flyway_schema_history where success and version is not null"));
    assertEquals(
        "24",
        scalar(
            "select count(*) from information_schema.tables where table_schema in ('schubert','schubert_web_session') and table_type='BASE TABLE'"));
    assertEquals(
        "159",
        scalar(
            "select count(*) from pg_constraint where contype='c' and connamespace in ('schubert'::regnamespace,'schubert_web_session'::regnamespace)"));
    assertEquals(
        "true/true",
        scalar(
            "select indisunique||'/'||indisvalid from pg_index where indexrelid='schubert.uq_mq_outbox_question_work'::regclass"));
    String predicate =
        scalar(
            "select pg_get_expr(indpred,indrelid) from pg_index where indexrelid='schubert.uq_mq_outbox_question_work'::regclass");
    assertTrue(predicate.contains("nk.async.work"));
    assertTrue(predicate.contains("QWKREQ01"));
    Path migrations =
        Path.of(System.getProperty("nk.pt.repository"))
            .resolve("src/schubert-nk-api/src/main/resources/db/migration");
    assertEquals(
        "1c5544165e1ab8441f6edf3dcc83dbb5ac9e05a6e6bfb9a7086d0d8ea0f6396b",
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(
                        Files.readAllBytes(
                            migrations.resolve("V015__question_query_inbox_deletion.sql")))));
    String sql =
        Files.readString(migrations.resolve("V016__question_mutation_inbox_references.sql"));
    for (String required :
        List.of(
            "FOR UPDATE",
            "FOR SHARE",
            "SECURITY DEFINER",
            "interval '168 hours'",
            "i.expires_at < p_cutoff",
            "pg_current_xact_id()",
            "pg_catalog.sha256")) assertTrue(sql.contains(required), required);
    assertFalse(sql.contains("DROP "));
    assertFalse(sql.contains("GRANT SELECT ON schubert.mq_outbox"));
  }

  static UUID message(String route) {
    return new UUID(0, 101 + ROUTES.indexOf(route));
  }

  static UUID token(String route) {
    return new UUID(0, 201 + ROUTES.indexOf(route));
  }

  static ResponseSnapshotIdentity id(String route) {
    return ResponseSnapshotIdentity.authenticated(message(route), route, FIXTURE_001_A3FEAA64, 7);
  }

  static InboxResultReference ref(String route) {
    return InboxResultReference.numeric(
        route.equals(FIXTURE_NTCRSP01_CFC2AD25)
            ? InboxResultReferenceType.JOB
            : InboxResultReferenceType.QUESTION,
        route.equals(FIXTURE_NTCRSP01_CFC2AD25) ? 11 : 9);
  }

  static boolean success(String code) {
    return Set.of(FIXTURE_0000_876EEFE0, FIXTURE_0200_FC9DB3AC).contains(code);
  }

  static boolean check(Fixture f, Connection c, String route, String code) throws Exception {
    try {
      return f.inspector.isConsistent(
          c,
          id(route),
          snapshot(f, id(route), code, golden(route, code, message(route)), token(route)),
          token(route));
    } finally {
      c.rollback();
    } // Caller ends borrowed TX before independent fixture mutation.
  }

  static InboxCompletion snapshot(
      Fixture f, ResponseSnapshotIdentity id, String code, byte[] wire, UUID token)
      throws Exception {
    byte[] clear = wire;
    try {
      if (success(code)) {
        var bytes = new ByteArrayOutputStream();
        try (var out = new DataOutputStream(bytes)) {
          out.writeBytes("NKREF1");
          out.writeByte(id.responseLayoutId().equals(FIXTURE_NTCRSP01_CFC2AD25) ? 2 : 1);
          out.writeLong(id.responseLayoutId().equals(FIXTURE_NTCRSP01_CFC2AD25) ? 11 : 9);
          out.writeLong(token.getMostSignificantBits());
          out.writeLong(token.getLeastSignificantBits());
          out.writeInt(wire.length);
          out.write(wire);
        }
        clear = bytes.toByteArray();
      }
      var s =
          f.base.saved(
              id,
              clear,
              success(code) ? InboxCompletionState.COMPLETED : InboxCompletionState.ERROR,
              TIME);
      return new InboxCompletion(
          s.state(),
          success(code) ? ref(id.responseLayoutId()) : InboxResultReference.none(),
          id.responseLayoutId(),
          id.responseVersion(),
          s.responseSnapshot(),
          TIME);
    } finally {
      Arrays.fill(clear, (byte) 0);
      Arrays.fill(wire, (byte) 0);
    }
  }

  static byte[] golden(String route, String code, UUID message) throws Exception {
    var values = new HashMap<String, String>();
    if (success(code))
      switch (route) {
        case FIXTURE_QSBRSP01_9848D404 ->
            values.putAll(Map.of("受付ID", RECEIPT, "Question ID", "9", "受付日時", "20260909090000121"));
        case FIXTURE_NTCRSP01_CFC2AD25 ->
            values.putAll(Map.of("更新後状態", "CANCELLED", "取消日時", "20260909090000122"));
        default -> values.put("削除日時", "20260909090000122");
      }
    else if (route.equals(FIXTURE_NTCRSP01_CFC2AD25) && code.equals(FIXTURE_0107_BAC582DD))
      values.put("更新後状態", "PROCESSING");
    byte[] wire = NonAuthenticationInboxInspectorTest.wire(route, code, values, 0);
    if (route.equals(FIXTURE_QSBRSP01_9848D404))
      put(wire, 23, "A"); // UI236 async acceptance, not shared SS query.
    put(wire, 60, message.toString());
    put(wire, 96, "20260909090000123");
    return wire;
  }

  static byte[] workWire() {
    byte[] wire = new byte[320];
    Arrays.fill(wire, (byte) ' ');
    put(wire, 0, "SCHBNK01");
    put(wire, 8, "001QWKREQ01001EI");
    put(wire, 24, WORK.toString());
    put(wire, 60, message(FIXTURE_QSBRSP01_9848D404).toString());
    put(wire, 96, "20260909090000123");
    put(wire, 177, "0256");
    put(wire, 181, "000064");
    put(wire, 187, "000000");
    put(wire, 193, "000000");
    put(wire, 199, "000000320");
    put(wire, 256, RECEIPT);
    put(wire, 282, "000000000009");
    put(wire, 294, "000000000011");
    return wire;
  }

  static void put(byte[] wire, int offset, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, wire, offset, bytes.length);
  }

  static void workBody(byte[] bytes) throws SQLException {
    try (var c = db.admin();
        var s = c.prepareStatement("update schubert.mq_outbox set body=? where id=14")) {
      s.setBytes(1, bytes);
      assertEquals(1, s.executeUpdate());
    }
  }

  static void seed(Fixture f, String route, String code, UUID message, UUID token)
      throws Exception {
    var id = ResponseSnapshotIdentity.authenticated(message, route, FIXTURE_001_A3FEAA64, 7);
    var s = snapshot(f, id, code, golden(route, code, message), token);
    try (var c = db.admin();
        var p =
            c.prepareStatement(
                "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,owner_user_id,operation_token,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,result_ref_id,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at) values(?,?,?,'001',7,?,repeat('a',64),'v1',?,?,?,?,'001',?,'v1',?,?,?)")) {
      p.setObject(1, message);
      p.setObject(2, message);
      p.setString(3, route.substring(0, 3) + "REQ01");
      p.setObject(4, token);
      p.setString(5, s.state().name());
      p.setString(6, s.resultReference().type().name());
      p.setObject(7, success(code) ? (route.equals(FIXTURE_NTCRSP01_CFC2AD25) ? 11L : 9L) : null);
      p.setString(8, route);
      p.setBytes(9, s.responseSnapshot().orElseThrow().ciphertext());
      p.setObject(10, TIME.minusSeconds(1).atOffset(java.time.ZoneOffset.UTC));
      p.setObject(11, TIME.atOffset(java.time.ZoneOffset.UTC));
      p.setObject(12, TIME.plusSeconds(604800).atOffset(java.time.ZoneOffset.UTC));
      assertEquals(1, p.executeUpdate());
    }
  }

  static Connection connection() throws SQLException {
    return DriverManager.getConnection(url, "schubert_inbox_inspector", "");
  }

  static void sql(String query) throws SQLException {
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.executeUpdate(query);
    }
  }

  static String scalar(String query) throws SQLException {
    try (var c = db.admin();
        var s = c.createStatement();
        var r = s.executeQuery(query)) {
      assertTrue(r.next());
      String value = r.getString(1);
      assertFalse(r.next());
      return value;
    }
  }

  static String count() throws SQLException {
    return scalar("select count(*) from schubert.request_inbox");
  }

  static void denied(String role, String query) throws SQLException {
    try (var c = DriverManager.getConnection(url, role, "");
        var s = c.createStatement()) {
      assertEquals("42501", assertThrows(SQLException.class, () -> s.execute(query)).getSQLState());
    }
  }

  static final class Fixture implements AutoCloseable {
    final InboxResponseInspectorTest.Fixture base = new InboxResponseInspectorTest.Fixture();
    final QuestionMutationInboxInspector inspector = new QuestionMutationInboxInspector(base.codec);
    final AuthContextCodec contexts = new AuthContextCodec("v1", base.key, null, null);
    final AuthenticationInboxInspector auth =
        new AuthenticationInboxInspector(base.codec, contexts, new ContextHash());
    final NonAuthenticationInboxInspector nonAuth = new NonAuthenticationInboxInspector(base.codec);

    Fixture() throws Exception {}

    InboxCleanup service() {
      return service(QuestionMutationInboxInspectorTest::connection);
    }

    InboxCleanup service(SqlConnectionProvider provider) {
      return new InboxCleanup(provider, auth, nonAuth, Set.of("v1"));
    }

    @Override
    public void close() {
      contexts.close();
      base.close();
    }
  }
}
