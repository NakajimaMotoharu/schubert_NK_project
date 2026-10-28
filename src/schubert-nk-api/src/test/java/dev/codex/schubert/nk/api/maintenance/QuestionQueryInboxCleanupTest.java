package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.database.MigrationInventory;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.messaging.outbound.SqlConnectionProvider;
import dev.codex.schubert.nk.api.security.AuthContextCodec;
import dev.codex.schubert.nk.api.security.ContextHash;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
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

/** PT-DB-INBOX-161..168; SS324 12.8/331 3.10/PG-D-139. Independent UI byte vectors. */
final class QuestionQueryInboxCleanupTest {
  private static final String FIXTURE_NTSRSP01_420AB9AB = "NTSRSP01";
  private static final String FIXTURE_NTDRSP01_4741FF2A = "NTDRSP01";
  private static final String FIXTURE_QSSRSP01_DBC5C1ED = "QSSRSP01";
  private static final String FIXTURE_QSDRSP01_3477C62F = "QSDRSP01";
  private static final String FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC =
      "delete from schubert.request_inbox";
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_9001_351F7309 = "9001";
  private static final String FIXTURE_0104_96E1973C = "0104";
  private static final String FIXTURE_RECEIVED_35302D54 = "RECEIVED";
  private static final String FIXTURE_UNANSWERED_8B420ADF = "UNANSWERED";
  private static final String FIXTURE_COMPLETED_BA0AE16A = "COMPLETED";
  private static final String FIXTURE_ERROR_F717E7D8 = "ERROR";
  private static final String FIXTURE_ANSWERED_6CA66E97 = "ANSWERED";
  private static final String FIXTURE_001_A3FEAA64 = "001";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static final List<String> LAYOUTS =
      List.of(
          FIXTURE_NTSRSP01_420AB9AB,
          FIXTURE_NTDRSP01_4741FF2A,
          FIXTURE_QSSRSP01_DBC5C1ED,
          FIXTURE_QSDRSP01_3477C62F);
  private static final Instant TIME = Instant.parse("2026-09-09T00:00:00.123Z");
  private static final String JST = "20260909090000123";
  private static final String RECEIPT = "0".repeat(25) + "1";
  private static final UUID MESSAGE = new UUID(0, 101);
  private static final InspectionRun RUN =
      new InspectionRun(new UUID(0, 42), Instant.parse("2026-09-17T00:00:00.123Z"));
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
    sql("delete from schubert.inbox_inspection_progress");
    sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
    sql("delete from schubert.batch_runs");
    sql("delete from schubert.app_users");
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at,version) values(7,'Learner','learner','synthetic-unused','USER','ACTIVE','2026-09-09T00:00:00Z','2026-09-09T00:00:00Z','2026-09-09T00:00:00Z',0),(9,'Other','other','synthetic-unused','USER','ACTIVE','2026-09-09T00:00:00Z','2026-09-09T00:00:00Z','2026-09-09T00:00:00Z',0)");
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
  void scope004ScopedQuestionWireAndOldRawAreBothMaintenanceOnlyProfiles() throws Exception {
    try (var f = new Fixture();
        var c = connection()) {
      c.setAutoCommit(false);
      var structural = new InboxResponseInspector(f.base.codec);
      for (String layout : LAYOUTS) {
        for (String code :
            List.of(
                FIXTURE_0000_876EEFE0,
                list(layout) ? FIXTURE_9001_351F7309 : FIXTURE_0104_96E1973C)) {
          byte[] wire =
              golden(
                  layout,
                  code,
                  0,
                  FIXTURE_RECEIVED_35302D54,
                  false,
                  FIXTURE_UNANSWERED_8B420ADF,
                  "");
          var legacy = snapshot(f, layout, code, wire.clone(), NONE);
          assertTrue(structural.isStructurallyValid(identity(layout), legacy));
          assertTrue(f.inspector.isConsistent(c, identity(layout), legacy));
          for (dev.codex.schubert.nk.api.domain.Role role :
              dev.codex.schubert.nk.api.domain.Role.values()) {
            byte[] frame = new byte[wire.length + 8];
            System.arraycopy(
                java.util.HexFormat.of()
                    .parseHex(role.name().equals("USER") ? "4e4b515259310055" : "4e4b515259310041"),
                0,
                frame,
                0,
                8);
            System.arraycopy(wire, 0, frame, 8, wire.length);
            boolean expected = layout.startsWith("QS");
            var scoped = snapshot(f, layout, code, frame.clone(), NONE);
            assertEquals(expected, structural.isStructurallyValid(identity(layout), scoped));
            assertEquals(expected, f.inspector.isConsistent(c, identity(layout), scoped));
            frame[7] = 'X';
            var corrupt = snapshot(f, layout, code, frame, NONE);
            assertFalse(structural.isStructurallyValid(identity(layout), corrupt));
            assertFalse(f.inspector.isConsistent(c, identity(layout), corrupt));
          }
          Arrays.fill(wire, (byte) 0);
        }
      }
      assertFalse(c.isClosed());
      assertEquals("0", count());
      c.rollback();
    }
  }

  @Test
  void queryProfilesAndFrozenSnapshots() throws Exception {
    try (var f = new Fixture();
        var c = connection()) {
      c.setAutoCommit(false);
      for (String layout : LAYOUTS) {
        for (String code :
            List.of(
                FIXTURE_0000_876EEFE0,
                "0100",
                "0101",
                "0102",
                "0103",
                FIXTURE_0104_96E1973C,
                "0105",
                "0106",
                "0107",
                "0200",
                "9000",
                FIXTURE_9001_351F7309)) {
          boolean expected =
              code.equals(FIXTURE_0000_876EEFE0)
                  || code.equals(list(layout) ? FIXTURE_9001_351F7309 : FIXTURE_0104_96E1973C);
          var saved =
              snapshot(
                  f,
                  layout,
                  code,
                  golden(
                      layout,
                      code,
                      0,
                      FIXTURE_RECEIVED_35302D54,
                      false,
                      FIXTURE_UNANSWERED_8B420ADF,
                      ""),
                  NONE);
          assertEquals(
              expected, f.inspector.isConsistent(c, identity(layout), saved), layout + "/" + code);
        }
      }
      sql(
          "update schubert.app_users set status='DISABLED',role='ADMIN',username='Later',username_key='later',version=9 where id=7");
      for (String layout : LAYOUTS) {
        var saved =
            snapshot(
                f,
                layout,
                FIXTURE_0000_876EEFE0,
                golden(
                    layout,
                    FIXTURE_0000_876EEFE0,
                    0,
                    FIXTURE_RECEIVED_35302D54,
                    false,
                    FIXTURE_UNANSWERED_8B420ADF,
                    ""),
                NONE);
        assertTrue(f.inspector.isConsistent(c, identity(layout), saved));
      }
      assertEquals(
          "0",
          scalar(
              "select (select count(*) from schubert.questions)+(select count(*) from schubert.notifications)+(select count(*) from schubert.answers)"));
      assertFalse(c.getAutoCommit());
      assertFalse(c.isClosed());
    }
  }

  @Test
  void goldenBoundsAndSemanticDamage() throws Exception {
    try (var f = new Fixture();
        var c = connection()) {
      c.setAutoCommit(false);
      for (String layout : List.of(FIXTURE_NTSRSP01_420AB9AB, FIXTURE_QSSRSP01_DBC5C1ED))
        for (int count : new int[] {0, 1, 50})
          valid(
              f,
              c,
              layout,
              golden(
                  layout,
                  FIXTURE_0000_876EEFE0,
                  count,
                  FIXTURE_RECEIVED_35302D54,
                  false,
                  FIXTURE_UNANSWERED_8B420ADF,
                  ""),
              true);
      for (String state :
          List.of(
              FIXTURE_RECEIVED_35302D54,
              "PROCESSING",
              FIXTURE_COMPLETED_BA0AE16A,
              FIXTURE_ERROR_F717E7D8,
              "CANCELLED")) {
        valid(
            f,
            c,
            FIXTURE_NTSRSP01_420AB9AB,
            golden(
                FIXTURE_NTSRSP01_420AB9AB,
                FIXTURE_0000_876EEFE0,
                1,
                state,
                false,
                FIXTURE_UNANSWERED_8B420ADF,
                ""),
            true);
        for (boolean deleted : List.of(false, true))
          valid(
              f,
              c,
              FIXTURE_NTDRSP01_4741FF2A,
              golden(
                  FIXTURE_NTDRSP01_4741FF2A,
                  FIXTURE_0000_876EEFE0,
                  0,
                  state,
                  deleted,
                  FIXTURE_UNANSWERED_8B420ADF,
                  state.equals(FIXTURE_COMPLETED_BA0AE16A) && !deleted ? "A".repeat(4096) : ""),
              true,
              state + "/deleted=" + deleted);
      }
      // BUG567/YKT410: UI224 deletion suppresses BOTH bodies. Never call a corrupted
      // completed/deleted answer a valid historical snapshot (the old BUG562 gap).
      valid(
          f,
          c,
          FIXTURE_NTDRSP01_4741FF2A,
          golden(
              FIXTURE_NTDRSP01_4741FF2A,
              FIXTURE_0000_876EEFE0,
              0,
              FIXTURE_COMPLETED_BA0AE16A,
              true,
              FIXTURE_UNANSWERED_8B420ADF,
              "A".repeat(4096)),
          false,
          "deleted completed answer must be rejected by Inbox inspector");
      valid(
          f,
          c,
          FIXTURE_NTDRSP01_4741FF2A,
          golden(
              FIXTURE_NTDRSP01_4741FF2A,
              FIXTURE_0000_876EEFE0,
              0,
              FIXTURE_COMPLETED_BA0AE16A,
              false,
              FIXTURE_UNANSWERED_8B420ADF,
              ""),
          true);
      for (String state :
          List.of(FIXTURE_ANSWERED_6CA66E97, FIXTURE_UNANSWERED_8B420ADF, FIXTURE_ERROR_F717E7D8)) {
        valid(
            f,
            c,
            FIXTURE_QSSRSP01_DBC5C1ED,
            golden(
                FIXTURE_QSSRSP01_DBC5C1ED,
                FIXTURE_0000_876EEFE0,
                1,
                FIXTURE_RECEIVED_35302D54,
                false,
                state,
                ""),
            true);
        valid(
            f,
            c,
            FIXTURE_QSDRSP01_3477C62F,
            golden(
                FIXTURE_QSDRSP01_3477C62F,
                FIXTURE_0000_876EEFE0,
                0,
                FIXTURE_RECEIVED_35302D54,
                false,
                state,
                ""),
            true);
      }
      valid(
          f,
          c,
          FIXTURE_QSDRSP01_3477C62F,
          golden(
              FIXTURE_QSDRSP01_3477C62F,
              FIXTURE_0000_876EEFE0,
              0,
              FIXTURE_RECEIVED_35302D54,
              false,
              FIXTURE_ANSWERED_6CA66E97,
              "A".repeat(4096)),
          true);
      for (String layout : List.of(FIXTURE_NTSRSP01_420AB9AB, FIXTURE_QSSRSP01_DBC5C1ED)) {
        valid(
            f,
            c,
            layout,
            golden(
                layout,
                FIXTURE_0000_876EEFE0,
                51,
                FIXTURE_RECEIVED_35302D54,
                false,
                FIXTURE_UNANSWERED_8B420ADF,
                ""),
            false);
        byte[] bytes =
            golden(
                layout,
                FIXTURE_0000_876EEFE0,
                0,
                FIXTURE_RECEIVED_35302D54,
                false,
                FIXTURE_UNANSWERED_8B420ADF,
                "");
        put(bytes, 262, "051");
        valid(f, c, layout, bytes, false);
      }
      for (String layout : LAYOUTS) {
        byte[] bytes =
            golden(
                layout,
                FIXTURE_0000_876EEFE0,
                list(layout) ? 1 : 0,
                FIXTURE_RECEIVED_35302D54,
                false,
                FIXTURE_UNANSWERED_8B420ADF,
                "");
        bytes[bytes.length - 1] = 'x';
        valid(f, c, layout, bytes, false);
      }
      // UI236 data offsets are one-based. Mutations are independent of production schemas.
      for (var change :
          List.of(
              Map.entry(257, "000000000000"),
              Map.entry(269, "I".repeat(26)),
              Map.entry(307, "UNKNOWN"),
              Map.entry(319, "20260230090000123"),
              Map.entry(404, "1"),
              Map.entry(435, "e\u0301"),
              Map.entry(352, JST),
              Map.entry(8597, "BAD"))) {
        byte[] bytes =
            golden(
                FIXTURE_NTDRSP01_4741FF2A,
                FIXTURE_0000_876EEFE0,
                0,
                FIXTURE_RECEIVED_35302D54,
                false,
                FIXTURE_UNANSWERED_8B420ADF,
                "");
        put(bytes, change.getKey() - 1, change.getValue());
        valid(f, c, FIXTURE_NTDRSP01_4741FF2A, bytes, false);
      }
      byte[] badUtf8 =
          golden(
              FIXTURE_QSDRSP01_3477C62F,
              FIXTURE_0000_876EEFE0,
              0,
              FIXTURE_RECEIVED_35302D54,
              false,
              FIXTURE_UNANSWERED_8B420ADF,
              "");
      for (String error :
          List.of(
              "PROCESS_FAILED",
              "SYSTEM_UNAVAIL",
              "RESOURCE_LIMIT",
              "DATA_INTEGRITY",
              "PROTOCOL_ERROR",
              "UNKNOWN")) {
        byte[] wire =
            golden(
                FIXTURE_NTDRSP01_4741FF2A,
                FIXTURE_0000_876EEFE0,
                0,
                FIXTURE_ERROR_F717E7D8,
                false,
                FIXTURE_UNANSWERED_8B420ADF,
                "");
        Arrays.fill(wire, 8596, 8612, (byte) ' ');
        put(wire, 8596, error);
        valid(f, c, FIXTURE_NTDRSP01_4741FF2A, wire, !error.equals("UNKNOWN"));
      }
      badUtf8[370] = (byte) 0xff;
      valid(f, c, FIXTURE_QSDRSP01_3477C62F, badUtf8, false);
      byte[] missingDate =
          golden(
              FIXTURE_QSDRSP01_3477C62F,
              FIXTURE_0000_876EEFE0,
              0,
              FIXTURE_RECEIVED_35302D54,
              false,
              FIXTURE_ANSWERED_6CA66E97,
              "");
      Arrays.fill(missingDate, 8579, 8596, (byte) ' ');
      valid(f, c, FIXTURE_QSDRSP01_3477C62F, missingDate, false);
      byte[] unwantedAnswer =
          golden(
              FIXTURE_QSDRSP01_3477C62F,
              FIXTURE_0000_876EEFE0,
              0,
              FIXTURE_RECEIVED_35302D54,
              false,
              FIXTURE_UNANSWERED_8B420ADF,
              "not allowed");
      valid(f, c, FIXTURE_QSDRSP01_3477C62F, unwantedAnswer, false);
    }
  }

  @Test
  void canonicalIdentityReferencesAndNulls() throws Exception {
    try (var f = new Fixture();
        var c = connection()) {
      for (String layout : LAYOUTS) {
        var saved =
            snapshot(
                f,
                layout,
                FIXTURE_0000_876EEFE0,
                golden(
                    layout,
                    FIXTURE_0000_876EEFE0,
                    0,
                    FIXTURE_RECEIVED_35302D54,
                    false,
                    FIXTURE_UNANSWERED_8B420ADF,
                    ""),
                NONE);
        assertFalse(f.inspector.isConsistent(c, identity(layout), saved));
        c.setAutoCommit(false);
        assertThrows(
            NullPointerException.class,
            () -> f.inspector.isConsistent(null, identity(layout), saved));
        assertThrows(NullPointerException.class, () -> f.inspector.isConsistent(c, null, saved));
        assertThrows(
            NullPointerException.class, () -> f.inspector.isConsistent(c, identity(layout), null));
        assertFalse(
            f.inspector.isConsistent(
                c,
                ResponseSnapshotIdentity.anonymous(MESSAGE, layout, FIXTURE_001_A3FEAA64),
                saved));
        assertFalse(
            f.inspector.isConsistent(
                c,
                ResponseSnapshotIdentity.authenticated(MESSAGE, layout, FIXTURE_001_A3FEAA64, 9),
                saved));
        assertFalse(
            f.inspector.isConsistent(
                c, ResponseSnapshotIdentity.authenticated(MESSAGE, layout, "002", 7), saved));
        for (var ref :
            List.of(
                InboxResultReference.numeric(InboxResultReferenceType.USER, 7),
                InboxResultReference.numeric(InboxResultReferenceType.QUESTION, 7),
                InboxResultReference.numeric(InboxResultReferenceType.JOB, 7),
                InboxResultReference.numeric(InboxResultReferenceType.SCENARIO_FILE, 7),
                InboxResultReference.authSession(new UUID(0, 7)))) {
          var changed =
              new InboxCompletion(
                  saved.state(),
                  ref,
                  saved.responseLayoutId(),
                  saved.responseVersion(),
                  saved.responseSnapshot(),
                  saved.completedAt());
          assertFalse(f.inspector.isConsistent(c, identity(layout), changed));
        }
        assertFalse(
            f.inspector.isConsistent(
                c,
                identity(layout),
                new InboxCompletion(
                    saved.state(), NONE, layout, FIXTURE_001_A3FEAA64, Optional.empty(), TIME)));
        byte[] bytes =
            golden(
                layout,
                FIXTURE_0000_876EEFE0,
                0,
                FIXTURE_RECEIVED_35302D54,
                false,
                FIXTURE_UNANSWERED_8B420ADF,
                "");
        put(bytes, 60, new UUID(0, 99).toString());
        valid(f, c, layout, bytes, false);
        var probe = new MaintenanceJdbcProbe();
        probe.fault = "getAutoCommit";
        assertFalse(f.inspector.isConsistent(probe.wrap(c), identity(layout), saved));
        c.rollback();
        c.setAutoCommit(true);
      }
    }
  }

  @Test
  void validRowsDeleteAndRetainExactMetadata() throws Exception {
    try (var f = new Fixture()) {
      for (String layout : LAYOUTS) {
        for (String code :
            List.of(
                FIXTURE_0000_876EEFE0,
                list(layout) ? FIXTURE_9001_351F7309 : FIXTURE_0104_96E1973C)) {
          seed(f, 101, layout, code);
          assertEquals(
              InspectionStep.Outcome.DELETED,
              f.service().inspectNext(RUN, Optional.empty()).outcome());
          assertEquals("0", count());
          assertEquals(
              InspectionStep.Outcome.END, f.service().inspectNext(RUN, Optional.empty()).outcome());
        }
        seed(f, 101, layout, FIXTURE_0000_876EEFE0);
        try (var c = db.admin();
            var s = c.createStatement()) {
          assertEquals(
              "23514",
              assertThrows(
                      SQLException.class,
                      () ->
                          s.executeUpdate(
                              "update schubert.request_inbox set operation_token='00000000-0000-0000-0000-000000000001'"))
                  .getSQLState());
        }
        var probe = new MaintenanceJdbcProbe();
        probe.columns.put("operation_token", new UUID(0, 1));
        assertEquals(
            InspectionStep.Outcome.PROTECTED,
            f.service(() -> probe.wrap(connection())).inspectNext(RUN, Optional.empty()).outcome());
        assertTrue(probe.selectedStatements > 0);
        assertEquals("1", count());
        sql(
            "update schubert.request_inbox set processing_state='PROCESSING',completed_at=null,result_ref_type=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null");
        assertEquals(
            InspectionStep.Outcome.END, f.service().inspectNext(RUN, Optional.empty()).outcome());
        assertEquals("1", count());
        for (String change :
            List.of(
                "owner_user_id=9",
                "request_version='002'",
                "response_version='002'",
                "response_layout_id='GAMRSP01'",
                "fingerprint_key_version='unknown'",
                "result_ref_type='QUESTION',result_ref_id=7",
                "response_key_version='unknown'",
                "response_body_encrypted=decode(repeat('00',30),'hex')",
                "response_body_encrypted=null,response_key_version=null")) {
          sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
          seed(f, 101, layout, FIXTURE_0000_876EEFE0);
          sql("update schubert.request_inbox set " + change);
          assertEquals(
              InspectionStep.Outcome.PROTECTED,
              f.service().inspectNext(RUN, Optional.empty()).outcome(),
              layout + "/" + change);
          assertEquals("1", count());
        }
        sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
      }
      assertEquals(
          "Learner/USER/ACTIVE/0",
          scalar(
              "select username||'/'||role||'/'||status||'/'||version from schubert.app_users where id=7"));
    }
  }

  @Test
  void retentionBackupAndSqlAuthority() throws Exception {
    try (var f = new Fixture()) {
      for (String layout : LAYOUTS) {
        for (String expiry :
            List.of(
                "2026-09-10T00:00:00.122999Z",
                "2026-09-10T00:00:00.123Z",
                "2026-09-10T00:00:00.123001Z",
                "2026-09-17T00:00:00.122999Z",
                "2026-09-17T00:00:00.123Z",
                "2026-09-17T00:00:00.123001Z")) {
          sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
          seed(f, 101, layout, FIXTURE_0000_876EEFE0);
          sql("update schubert.request_inbox set expires_at='" + expiry + "'::timestamptz");
          var expected =
              Map.of(
                      "2026-09-10T00:00:00.122999Z", InspectionStep.Outcome.PROTECTED,
                      "2026-09-10T00:00:00.123Z", InspectionStep.Outcome.DELETED,
                      "2026-09-10T00:00:00.123001Z", InspectionStep.Outcome.DELETED,
                      "2026-09-17T00:00:00.122999Z", InspectionStep.Outcome.DELETED,
                      "2026-09-17T00:00:00.123Z", InspectionStep.Outcome.END,
                      "2026-09-17T00:00:00.123001Z", InspectionStep.Outcome.END)
                  .get(expiry);
          assertEquals(
              expected,
              f.service().inspectNext(RUN, Optional.empty()).outcome(),
              layout + "/" + expiry);
          assertEquals(expected == InspectionStep.Outcome.DELETED ? "0" : "1", count());
        }
      }
      sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
      seed(f, 101, FIXTURE_NTSRSP01_420AB9AB, FIXTURE_0000_876EEFE0);
      sql("update schubert.batch_runs set status='FAILED' where step='BACKUP_DB'");
      assertThrows(
          InboxMaintenanceException.class, () -> f.service().inspectNext(RUN, Optional.empty()));
      assertEquals("1", count());
      sql("delete from schubert.batch_runs where step='BACKUP_DB'");
      assertThrows(
          InboxMaintenanceException.class, () -> f.service().inspectNext(RUN, Optional.empty()));
      reset();
      seed(f, 101, FIXTURE_QSDRSP01_3477C62F, FIXTURE_0000_876EEFE0);
      try (var lock = db.api();
          var s = lock.createStatement()) {
        lock.setAutoCommit(false);
        s.execute("select * from schubert.request_inbox for update");
        var failure =
            assertThrows(
                InboxMaintenanceException.class,
                () -> f.service().inspectNext(RUN, Optional.empty()));
        assertNull(failure.getCause());
        assertEquals("1", count());
        lock.rollback();
      }
      for (String role :
          List.of(
              "schubert_app",
              "schubert_batch",
              "schubert_web_session",
              "schubert_backup",
              "schubert_ops_ro"))
        denied(role, "select schubert.maintenance_delete_inbox(null,null,null,null,null)");
      for (String query :
          List.of(
              "select body from schubert.questions",
              "select * from schubert.notifications",
              "select password_hash from schubert.app_users",
              "select schubert.maintenance_lock_inbox_backup(null,null)"))
        denied("schubert_inbox_inspector", query);
    }
  }

  @Test
  void failuresRollbackAndResume() throws Exception {
    try (var f = new Fixture()) {
      for (String layout : LAYOUTS)
        for (String fault :
            List.of(
                "executeQuery", "getObject", "resultClose", "statementClose", "commit", "close")) {
          sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
          seed(f, 101, layout, FIXTURE_0000_876EEFE0);
          var p = new MaintenanceJdbcProbe();
          p.selectedSql = "maintenance_delete_inbox";
          p.fault = fault;
          var failure =
              assertThrows(
                  InboxMaintenanceException.class,
                  () -> f.service(() -> p.wrap(connection())).inspectNext(RUN, Optional.empty()));
          assertNull(failure.getCause());
          assertEquals(0, failure.getSuppressed().length);
          assertEquals(
              "Inbox maintenance did not complete; resume the same run", failure.getMessage());
          assertEquals(1, p.closes);
          assertTrue(p.selectedStatements > 0);
          assertEquals(0, p.saves);
          assertEquals(fault.equals("close") ? "0" : "1", count());
          assertEquals(
              fault.equals("close") ? InspectionStep.Outcome.END : InspectionStep.Outcome.DELETED,
              f.service().inspectNext(RUN, Optional.empty()).outcome());
        }
      seed(f, 101, FIXTURE_NTDRSP01_4741FF2A, FIXTURE_0000_876EEFE0);
      var p = new MaintenanceJdbcProbe();
      p.fault = "commit";
      p.commitAfter = true;
      assertThrows(
          InboxMaintenanceException.class,
          () -> f.service(() -> p.wrap(connection())).inspectStoredNext(RUN));
      assertEquals("0", count());
      assertEquals(
          "1/1/0",
          scalar(
              "select inspected_count||'/'||deleted_count||'/'||protected_count from schubert.inbox_inspection_progress"));
      var resumed = f.service().runChunk(RUN, 10);
      assertEquals(new InspectionProgress(RUN, Optional.of(MESSAGE), 1, 1, 0, true), resumed);
    }
  }

  @Test
  void concurrentAndDurableMixedRuns() throws Exception {
    try (var f = new Fixture();
        var pool = Executors.newFixedThreadPool(8)) {
      var saved = new HashMap<String, InboxCompletion>();
      for (String layout : LAYOUTS)
        saved.put(
            layout,
            snapshot(
                f,
                layout,
                FIXTURE_0000_876EEFE0,
                golden(
                    layout,
                    FIXTURE_0000_876EEFE0,
                    0,
                    FIXTURE_RECEIVED_35302D54,
                    false,
                    FIXTURE_UNANSWERED_8B420ADF,
                    ""),
                NONE));
      var tasks = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 100; i++) {
        String layout = LAYOUTS.get(i % 4);
        tasks.add(
            () -> {
              try (var c = connection()) {
                c.setAutoCommit(false);
                assertTrue(f.inspector.isConsistent(c, identity(layout), saved.get(layout)));
                assertFalse(c.isClosed());
                return true;
              }
            });
      }
      var results = pool.invokeAll(tasks);
      assertEquals(100, results.size());
      for (var result : results) assertTrue(result.get());
      long seq = 101;
      for (String layout : LAYOUTS) {
        seed(f, seq++, layout, FIXTURE_0000_876EEFE0);
        seed(f, seq, layout, FIXTURE_0000_876EEFE0);
        sql(
            "update schubert.request_inbox set response_key_version='unknown' where message_id='"
                + new UUID(0, seq++)
                + "'");
      }
      for (String prefix : List.of("QSB", "NTC", "QDL")) {
        seed(f, seq, FIXTURE_QSDRSP01_3477C62F, FIXTURE_0000_876EEFE0);
        sql(
            "update schubert.request_inbox set request_layout_id='"
                + prefix
                + "REQ01',response_layout_id='"
                + prefix
                + "RSP01',operation_token='"
                + new UUID(0, seq + 1000)
                + "' where message_id='"
                + new UUID(0, seq++)
                + "'");
      }
      var first = f.service().runChunk(RUN, 5);
      assertEquals(
          new InspectionProgress(RUN, Optional.of(new UUID(0, 105)), 5, 3, 2, false), first);
      var end = f.service().runChunk(RUN, 20);
      assertEquals(new InspectionProgress(RUN, Optional.of(new UUID(0, 111)), 11, 4, 7, true), end);
      assertEquals(end, f.service().runChunk(RUN, 1));
      assertEquals("7", count());
    }
  }

  @Test
  void appendOnlyInventoryAndClosedRoutes() throws Exception {
    assertEquals(
        MigrationInventory.CSV,
        scalar(
            "select string_agg(version,',' order by installed_rank) from schubert_meta.flyway_schema_history where version is not null"));
    assertEquals(
        "24",
        scalar(
            "select count(*) from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname in ('schubert','schubert_web_session') and c.relkind='r'"));
    assertEquals(
        "159",
        scalar(
            "select count(*) from pg_constraint c join pg_namespace n on n.oid=c.connamespace where n.nspname in ('schubert','schubert_web_session') and c.contype='c'"));
    Path migrations =
        Path.of(System.getProperty("nk.pt.repository"))
            .resolve("src/schubert-nk-api/src/main/resources/db/migration");
    assertEquals(
        "d2ba884de86c59c5815559aaf17a83b7a0546fcc7f9f48649dd744d127270229",
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(
                        Files.readAllBytes(
                            migrations.resolve("V014__durable_log_cleanup_progress.sql")))));
    String previous =
        Files.readString(migrations.resolve("V010__full_inbox_scan_and_restricted_deletion.sql"));
    String current =
        Files.readString(migrations.resolve("V015__question_query_inbox_deletion.sql"));
    String signature = "schubert.maintenance_delete_inbox(";
    String before =
        previous.substring(
            previous.indexOf(signature),
            previous.indexOf("$function$;", previous.indexOf(signature)));
    String after =
        current.substring(
            current.indexOf(signature), current.indexOf("$function$;", current.indexOf(signature)));
    assertEquals(
        before, after.replace("'NTSREQ01','NTDREQ01','QSSREQ01','QSDREQ01',\n         ", ""));
    assertEquals(
        "nk_owner/true/search_path=pg_catalog, schubert,TimeZone=UTC",
        scalar(
            "select pg_get_userbyid(proowner)||'/'||prosecdef::text||'/'||array_to_string(proconfig,',') from pg_proc where oid='schubert.maintenance_delete_inbox(uuid,timestamptz,uuid,text,bytea)'::regprocedure"));
    assertEquals(
        "false",
        scalar(
            "select has_function_privilege('schubert_batch','schubert.maintenance_lock_inbox_backup(uuid,timestamptz)','EXECUTE')::text"));
  }

  private static boolean list(String layout) {
    return layout.equals(FIXTURE_NTSRSP01_420AB9AB) || layout.equals(FIXTURE_QSSRSP01_DBC5C1ED);
  }

  private static ResponseSnapshotIdentity identity(String layout) {
    return ResponseSnapshotIdentity.authenticated(MESSAGE, layout, FIXTURE_001_A3FEAA64, 7);
  }

  private static void valid(Fixture f, Connection c, String layout, byte[] bytes, boolean expected)
      throws Exception {
    valid(f, c, layout, bytes, expected, layout);
  }

  private static void valid(
      Fixture f, Connection c, String layout, byte[] bytes, boolean expected, String caseLabel)
      throws Exception {
    assertEquals(
        expected,
        f.inspector.isConsistent(
            c, identity(layout), snapshot(f, layout, FIXTURE_0000_876EEFE0, bytes, NONE)),
        caseLabel);
  }

  private static InboxCompletion snapshot(
      Fixture f, String layout, String code, byte[] wire, InboxResultReference ref)
      throws Exception {
    try {
      var s =
          f.base.saved(
              identity(layout),
              wire,
              Set.of(FIXTURE_0000_876EEFE0, "0200").contains(code)
                  ? InboxCompletionState.COMPLETED
                  : InboxCompletionState.ERROR,
              TIME);
      return new InboxCompletion(
          s.state(), ref, layout, FIXTURE_001_A3FEAA64, s.responseSnapshot(), TIME);
    } finally {
      Arrays.fill(wire, (byte) 0);
    }
  }

  /** UI236 literal values/offsets, independent of production encoder/registry/validator. */
  private static byte[] golden(
      String layout,
      String code,
      int count,
      String state,
      boolean deleted,
      String answerState,
      String answer)
      throws Exception {
    var values = new HashMap<String, String>();
    if (Set.of(FIXTURE_0000_876EEFE0, "0200").contains(code)) {
      if (list(layout)) {
        values.putAll(
            Map.of(
                "Page size",
                "50",
                "Total count",
                "" + count,
                "First result",
                count == 0 ? "0" : "1",
                "Last result",
                "" + count));
      } else {
        values.putAll(
            Map.of(
                "Question ID",
                "000000000009",
                "受付ID",
                RECEIPT,
                "受付日時",
                JST,
                "質問本文",
                "Synthetic question",
                "回答本文",
                answer));
        if (layout.equals(FIXTURE_NTDRSP01_4741FF2A)) {
          values.putAll(
              Map.of(
                  "Notification ID",
                  "11",
                  "通知区分",
                  state.equals(FIXTURE_COMPLETED_BA0AE16A)
                      ? FIXTURE_COMPLETED_BA0AE16A
                      : state.equals(FIXTURE_ERROR_F717E7D8) ? FIXTURE_ERROR_F717E7D8 : "ACCEPTED",
                  "内部状態",
                  state,
                  "質問削除済み",
                  deleted ? "1" : "0"));
          if (Set.of("PROCESSING", FIXTURE_COMPLETED_BA0AE16A, FIXTURE_ERROR_F717E7D8)
              .contains(state)) values.put("処理開始日時", JST);
          if (state.equals(FIXTURE_COMPLETED_BA0AE16A)) values.put("処理完了日時", JST);
          if (state.equals(FIXTURE_ERROR_F717E7D8))
            values.putAll(
                Map.of(
                    "Error日時",
                    JST,
                    "Error code",
                    "PROCESS_FAILED",
                    "利用者向けerror",
                    "Synthetic error"));
          if (state.equals("CANCELLED")) values.put("取消日時", JST);
          if (deleted) {
            values.put("質問本文", "");
            values.put("Question ID", "");
          }
        } else {
          values.putAll(Map.of("Username", "HistoricalOwner", "回答状態", answerState));
          if (answerState.equals(FIXTURE_ANSWERED_6CA66E97)) values.put("回答日時", JST);
        }
      }
    }
    byte[] wire = NonAuthenticationInboxInspectorTest.wire(layout, code, values, count);
    put(wire, 60, MESSAGE.toString());
    for (int i = 0; i < count; i++) {
      int length = layout.equals(FIXTURE_NTSRSP01_420AB9AB) ? 624 : 672;
      int base = 304 + i * length;
      Arrays.fill(wire, base, base + length, (byte) ' ');
      put(wire, base, String.format(Locale.ROOT, "%012d", count - i));
      put(wire, base + 12, RECEIPT);
      if (layout.equals(FIXTURE_NTSRSP01_420AB9AB)) {
        put(
            wire,
            base + 38,
            state.equals(FIXTURE_COMPLETED_BA0AE16A)
                ? FIXTURE_COMPLETED_BA0AE16A
                : state.equals(FIXTURE_ERROR_F717E7D8) ? FIXTURE_ERROR_F717E7D8 : "ACCEPTED");
        put(wire, base + 50, state);
        put(wire, base + 62, JST);
        put(wire, base + 79, JST);
        put(wire, base + 96, deleted ? "削除済み" : "Synthetic summary");
        put(wire, base + 608, deleted ? "1" : "0");
      } else {
        put(wire, base + 38, "HistoricalOwner");
        put(wire, base + 102, "Synthetic summary");
        put(wire, base + 614, answerState);
        put(wire, base + 626, JST);
        if (answerState.equals(FIXTURE_ANSWERED_6CA66E97)) put(wire, base + 643, JST);
      }
    }
    return wire;
  }

  private static void put(byte[] bytes, int offset, String value) {
    byte[] v = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(v, 0, bytes, offset, v.length);
  }

  private static void seed(Fixture f, long sequence, String layout, String code) throws Exception {
    UUID message = new UUID(0, sequence);
    var id = ResponseSnapshotIdentity.authenticated(message, layout, FIXTURE_001_A3FEAA64, 7);
    byte[] wire =
        golden(layout, code, 0, FIXTURE_RECEIVED_35302D54, false, FIXTURE_UNANSWERED_8B420ADF, "");
    put(wire, 60, message.toString());
    InboxCompletion saved;
    try {
      saved =
          f.base.saved(
              id,
              wire,
              code.equals(FIXTURE_0000_876EEFE0)
                  ? InboxCompletionState.COMPLETED
                  : InboxCompletionState.ERROR,
              TIME);
    } finally {
      Arrays.fill(wire, (byte) 0);
    }
    assertTrue(f.base.inspector.isStructurallyValid(id, saved), layout + "/golden");
    byte[] body = saved.responseSnapshot().orElseThrow().ciphertext();
    try (var c = db.api();
        var s =
            c.prepareStatement(
                "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,owner_user_id,operation_token,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at) values(?,?,?,'001',7,null,repeat('a',64),'v1',?,'NONE',?,'001',?,'v1',?,?,?)")) {
      s.setObject(1, message);
      s.setObject(2, message);
      s.setString(3, layout.substring(0, 3) + "REQ01");
      s.setString(4, saved.state().name());
      s.setString(5, layout);
      s.setBytes(6, body);
      s.setObject(7, TIME.minusMillis(1).atOffset(java.time.ZoneOffset.UTC));
      s.setObject(8, TIME.atOffset(java.time.ZoneOffset.UTC));
      s.setObject(9, TIME.plusSeconds(86400).atOffset(java.time.ZoneOffset.UTC));
      assertEquals(1, s.executeUpdate());
    } finally {
      Arrays.fill(body, (byte) 0);
    }
  }

  private static Connection connection() throws SQLException {
    return DriverManager.getConnection(url, "schubert_inbox_inspector", "");
  }

  private static void sql(String query) throws SQLException {
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.executeUpdate(query);
    }
  }

  private static String scalar(String query) throws SQLException {
    try (var c = db.admin();
        var s = c.createStatement();
        var r = s.executeQuery(query)) {
      assertTrue(r.next());
      String v = r.getString(1);
      assertFalse(r.next());
      return v;
    }
  }

  private static String count() throws SQLException {
    return scalar("select count(*) from schubert.request_inbox");
  }

  private static void denied(String role, String query) throws SQLException {
    try (var c = DriverManager.getConnection(url, role, "");
        var s = c.createStatement()) {
      assertEquals("42501", assertThrows(SQLException.class, () -> s.execute(query)).getSQLState());
    }
  }

  private static final class Fixture implements AutoCloseable {
    final InboxResponseInspectorTest.Fixture base = new InboxResponseInspectorTest.Fixture();
    final AuthContextCodec contexts = new AuthContextCodec("v1", base.key, null, null);
    final AuthenticationInboxInspector auth =
        new AuthenticationInboxInspector(base.codec, contexts, new ContextHash());
    final NonAuthenticationInboxInspector inspector =
        new NonAuthenticationInboxInspector(base.codec);

    Fixture() throws Exception {}

    InboxCleanup service() {
      return service(QuestionQueryInboxCleanupTest::connection);
    }

    InboxCleanup service(SqlConnectionProvider provider) {
      return new InboxCleanup(provider, auth, inspector, Set.of("v1"));
    }

    @Override
    public void close() {
      contexts.close();
      base.close();
    }
  }
}
