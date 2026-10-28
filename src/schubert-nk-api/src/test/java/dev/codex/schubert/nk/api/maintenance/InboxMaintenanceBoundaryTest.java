package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.database.MigrationInventory;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-DB-INBOX-049..056; V010 SQL matrix, not an AES/Java-deletion/oneshot certificate. */
final class InboxMaintenanceBoundaryTest {
  private static final String FIXTURE_UST_A0082146 = "UST";
  private static final String FIXTURE_QSB_661826BD = "QSB";
  private static final String FIXTURE_NTC_1FFAAF5E = "NTC";
  private static final String FIXTURE_QDL_6EE4F4E8 = "QDL";
  private static final String FIXTURE_LGN_B0C92867 = "LGN";
  private static final String FIXTURE_LOG_EDCC8D9B = "LOG";
  private static final String FIXTURE_GAM_5BC4EFCF = "GAM";
  private static final String FIXTURE_ERROR_F717E7D8 = "ERROR";
  private static final String FIXTURE_SCHUBERT_APP_5AB151CF = "schubert_app";
  private static final String FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC =
      "delete from schubert.request_inbox";
  private static final String FIXTURE_AUTH_SESSION_97533387 = "AUTH_SESSION";
  private static final String FIXTURE_USER_2DED8884 = "USER";
  private static final String FIXTURE_SCENARIO_FILE_072D014E = "SCENARIO_FILE";
  private static final String FIXTURE_QUESTION_8F4A4C6B = "QUESTION";
  private static final String FIXTURE_JOB_804C2C2C = "JOB";
  private static final String FIXTURE_NULL_F072CBEC = "null";
  private static final String FIXTURE_NONE_C44E6DD7 = "NONE";
  private static final String FIXTURE_22023_CDCA15BB = "22023";
  private static final String FIXTURE_55P03_0FE714C6 = "55P03";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static byte[] hash;
  private static final String ROLE = "schubert_inbox_inspector";
  private static final UUID RUN = new UUID(0, 42);
  private static final UUID MESSAGE = new UUID(0, 101);
  private static final UUID SESSION = new UUID(0, 104);
  private static final Instant COMPLETED = Instant.parse("2026-09-09T00:00:00.123Z");
  private static final Instant CUTOFF = Instant.parse("2026-09-17T00:00:00.123Z");
  private static final Set<String> TOKEN =
      Set.of(
          "UCR",
          FIXTURE_UST_A0082146,
          "URL",
          "UPW",
          "ULK",
          FIXTURE_QSB_661826BD,
          FIXTURE_NTC_1FFAAF5E,
          FIXTURE_QDL_6EE4F4E8);
  private static final List<String> ROUTES =
      List.of(
          FIXTURE_LGN_B0C92867,
          FIXTURE_LOG_EDCC8D9B,
          FIXTURE_GAM_5BC4EFCF,
          "SPK",
          "RTE",
          "SCF",
          "SRC",
          "SCN",
          "AUD",
          "ANM",
          "ANL",
          "VID",
          "MCT",
          "MCS",
          "MTR",
          "MED",
          "USR",
          "UDT",
          "LGS",
          "UCR",
          FIXTURE_UST_A0082146,
          "URL",
          "UPW",
          "ULK",
          "NTS",
          "NTD",
          "QSS",
          "QSD",
          FIXTURE_QSB_661826BD,
          FIXTURE_NTC_1FFAAF5E,
          FIXTURE_QDL_6EE4F4E8);
  private static final String NEXT = "schubert.maintenance_next_inbox(uuid,timestamptz,uuid)";
  private static final String DELETE =
      "schubert.maintenance_delete_inbox(uuid,timestamptz,uuid,text,bytea)";
  private static final String HELPER = "schubert.maintenance_lock_inbox_backup(uuid,timestamptz)";

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
    try (var c = db.api()) {
      url = c.getMetaData().getURL();
    }
    // Public invalid ciphertext: SQL may delete it, but the inspection service must never do so.
    hash = MessageDigest.getInstance("SHA-256").digest(new byte[30]);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws SQLException {
    for (String table :
        List.of("request_inbox", "auth_sessions", "script_files", "batch_runs", "app_users"))
      sql("delete from schubert." + table);
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) values(7,'Learner','learner','synthetic-unused','USER','ACTIVE','2026-09-09','2026-09-09','2026-09-09'),(9,'Target','target','synthetic-unused','USER','ACTIVE','2026-09-09','2026-09-09','2026-09-09')");
    sql(
        "insert into schubert.script_files(id,game_id,display_order,storage_relative_path,display_path,file_name,sha256,byte_size,created_at) values(11,1,1,'scenario/one.txt','one','one.txt',repeat('a',64),12,'2026-09-09')");
    sql(
        "insert into schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id) values('"
            + SESSION
            + "',7,repeat('a',64),decode(repeat('00',30),'hex'),'v1','2026-09-09','2026-09-09','2026-09-10','127.0.0.1','"
            + MESSAGE
            + "')");
    backup("BACKUP_DB");
    backup("BACKUP_CONFIG");
    inbox(101, FIXTURE_GAM_5BC4EFCF, FIXTURE_ERROR_F717E7D8, COMPLETED.plusSeconds(86400));
  }

  @Test
  void catalogAndColumnCapabilities() throws Exception {
    try (var c = db.admin()) {
      for (String signature : List.of(NEXT, DELETE, HELPER)) {
        try (var s =
            c.prepareStatement(
                "select p.prosecdef,pg_get_userbyid(p.proowner) as owner,p.proconfig from pg_proc p where p.oid=?::regprocedure")) {
          s.setString(1, signature);
          try (var r = s.executeQuery()) {
            assertTrue(r.next());
            assertEquals(!signature.equals(HELPER), r.getBoolean("prosecdef"));
            assertEquals("nk_owner", r.getString("owner"));
            assertEquals(
                Set.of("search_path=pg_catalog, schubert", "TimeZone=UTC"),
                new HashSet<>(Arrays.asList((String[]) r.getArray("proconfig").getArray())));
            assertFalse(r.next());
          }
        }
        for (String role :
            List.of(
                ROLE,
                FIXTURE_SCHUBERT_APP_5AB151CF,
                "schubert_batch",
                "schubert_backup",
                "schubert_web_session",
                "schubert_ops_ro")) {
          assertEquals(
              Boolean.toString(role.equals(ROLE) && !signature.equals(HELPER)),
              scalar(
                  c,
                  "select has_function_privilege('"
                      + role
                      + "','"
                      + signature
                      + "','EXECUTE')::text"));
        }
      }
      for (String table : List.of("app_users", "script_files")) {
        assertEquals(
            "false",
            scalar(
                c,
                "select has_table_privilege('"
                    + ROLE
                    + "','schubert."
                    + table
                    + "','SELECT')::text"));
        assertEquals(
            table.equals("app_users") ? "id,version" : "game_id,id",
            scalar(
                c,
                "select string_agg(column_name,',' order by column_name) from information_schema.column_privileges where grantee='"
                    + ROLE
                    + "' and table_schema='schubert' and table_name='"
                    + table
                    + "' and privilege_type='SELECT'"));
      }
    }
    try (var c = restricted()) {
      assertEquals("2", scalar(c, "select count(id) from schubert.app_users where version=0"));
      assertEquals("1", scalar(c, "select count(id) from schubert.script_files where game_id=1"));
    }
    for (String statement :
        List.of(
            "select username from schubert.app_users",
            "select password_hash from schubert.app_users",
            "select role from schubert.app_users",
            "select status from schubert.app_users",
            "select sha256 from schubert.script_files",
            "select storage_relative_path from schubert.script_files",
            "select response_body_encrypted from schubert.request_inbox",
            "select id from schubert_web_session.web_http_sessions",
            "update schubert.app_users set version=1",
            "delete from schubert.script_files",
            FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC,
            "create table schubert.forbidden(id int)",
            "set role nk_owner",
            "set role schubert_app",
            "select schubert.maintenance_lock_inbox_backup(null,null)"))
      denied(ROLE, "42501", statement);
    for (String role :
        List.of(
            FIXTURE_SCHUBERT_APP_5AB151CF,
            "schubert_batch",
            "schubert_backup",
            "schubert_web_session",
            "schubert_ops_ro")) {
      denied(
          role, "42501", "select message_id from schubert.maintenance_next_inbox(null,null,null)");
      denied(role, "42501", "select schubert.maintenance_delete_inbox(null,null,null,null,null)");
    }
  }

  @Test
  void candidateOrderStateAndUnknownRoutes() throws Exception {
    sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
    inbox(1, "ZZZ", FIXTURE_ERROR_F717E7D8, CUTOFF.minusNanos(1000));
    inbox(2, FIXTURE_GAM_5BC4EFCF, "COMPLETED", CUTOFF.minusNanos(1000));
    inbox(3, FIXTURE_GAM_5BC4EFCF, "PROCESSING", CUTOFF.minusNanos(1000));
    inbox(4, FIXTURE_GAM_5BC4EFCF, FIXTURE_ERROR_F717E7D8, CUTOFF);
    inbox(5, FIXTURE_GAM_5BC4EFCF, FIXTURE_ERROR_F717E7D8, CUTOFF.plusNanos(1000));
    try (var c = restricted()) {
      assertEquals(List.of(new UUID(0, 1)), read(c, RUN, CUTOFF, null));
      assertFalse(remove(c, RUN, CUTOFF, new UUID(0, 1), xact(c), hash));
      assertEquals(List.of(new UUID(0, 2)), read(c, RUN, CUTOFF, new UUID(0, 1)));
      assertEquals(List.of(), read(c, RUN, CUTOFF, new UUID(0, 2)));
      assertEquals(List.of(), read(c, RUN, CUTOFF, new UUID(0, 999)));
      c.commit();
    }
    assertEquals("5", count());
  }

  @Test
  void canonicalRoutesReferencesAndTokens() throws Exception {
    for (String route : ROUTES) {
      sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
      inbox(101, route, FIXTURE_ERROR_F717E7D8, CUTOFF.minusSeconds(1));
      try (var c = restricted()) {
        assertEquals(List.of(MESSAGE), read(c, RUN, CUTOFF, null));
        assertTrue(remove(c, RUN, CUTOFF, MESSAGE, xact(c), hash), route);
        c.rollback();
      }
      for (String reference :
          List.of(
              FIXTURE_AUTH_SESSION_97533387,
              FIXTURE_USER_2DED8884,
              FIXTURE_SCENARIO_FILE_072D014E,
              FIXTURE_QUESTION_8F4A4C6B,
              FIXTURE_JOB_804C2C2C)) {
        sql(
            "update schubert.request_inbox set result_ref_type='"
                + reference
                + "',result_ref_id="
                + (reference.equals(FIXTURE_AUTH_SESSION_97533387) ? FIXTURE_NULL_F072CBEC : "9")
                + ",result_ref_uuid="
                + (reference.equals(FIXTURE_AUTH_SESSION_97533387)
                    ? "'" + SESSION + "'"
                    : FIXTURE_NULL_F072CBEC));
        boolean expected =
            reference.equals(FIXTURE_AUTH_SESSION_97533387)
                    && Set.of(FIXTURE_LGN_B0C92867, FIXTURE_LOG_EDCC8D9B).contains(route)
                || reference.equals(FIXTURE_USER_2DED8884)
                    && Set.of("UCR", FIXTURE_UST_A0082146, "URL", "UPW", "ULK").contains(route)
                || reference.equals(FIXTURE_SCENARIO_FILE_072D014E) && route.equals("SCN");
        try (var c = restricted()) {
          assertEquals(List.of(MESSAGE), read(c, RUN, CUTOFF, null));
          assertEquals(
              expected, remove(c, RUN, CUTOFF, MESSAGE, xact(c), hash), route + "/" + reference);
          c.rollback();
        }
      }
    }
    for (String route : List.of("ZZZ")) {
      sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
      inbox(101, route, FIXTURE_ERROR_F717E7D8, CUTOFF.minusSeconds(1));
      try (var c = restricted()) {
        assertEquals(List.of(MESSAGE), read(c, RUN, CUTOFF, null));
        assertFalse(remove(c, RUN, CUTOFF, MESSAGE, xact(c), hash));
      }
    }
    // V016: independent closed state/reference matrix for the three mutation routes.
    for (String route : List.of(FIXTURE_QSB_661826BD, FIXTURE_NTC_1FFAAF5E, FIXTURE_QDL_6EE4F4E8)) {
      for (String state : List.of("COMPLETED", FIXTURE_ERROR_F717E7D8)) {
        for (String reference :
            List.of(
                FIXTURE_NONE_C44E6DD7,
                FIXTURE_AUTH_SESSION_97533387,
                FIXTURE_USER_2DED8884,
                FIXTURE_SCENARIO_FILE_072D014E,
                FIXTURE_QUESTION_8F4A4C6B,
                FIXTURE_JOB_804C2C2C)) {
          sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
          inbox(101, route, state, CUTOFF.minusSeconds(1));
          sql(
              "update schubert.request_inbox set result_ref_type='"
                  + reference
                  + "',result_ref_id="
                  + (Set.of(FIXTURE_NONE_C44E6DD7, FIXTURE_AUTH_SESSION_97533387)
                          .contains(reference)
                      ? FIXTURE_NULL_F072CBEC
                      : "9")
                  + ",result_ref_uuid="
                  + (reference.equals(FIXTURE_AUTH_SESSION_97533387)
                      ? "'" + SESSION + "'"
                      : FIXTURE_NULL_F072CBEC));
          boolean expected =
              state.equals(FIXTURE_ERROR_F717E7D8)
                  ? reference.equals(FIXTURE_NONE_C44E6DD7)
                  : reference.equals(
                      route.equals(FIXTURE_NTC_1FFAAF5E)
                          ? FIXTURE_JOB_804C2C2C
                          : FIXTURE_QUESTION_8F4A4C6B);
          try (var c = restricted()) {
            assertEquals(List.of(MESSAGE), read(c, RUN, CUTOFF, null));
            assertEquals(
                expected,
                remove(c, RUN, CUTOFF, MESSAGE, xact(c), hash),
                route + "/" + state + "/" + reference);
            c.rollback();
          }
        }
      }
    }
    // Remove only constraints in a rollback-only isolated admin TX to test SQL defense in depth.
    for (String route :
        List.of(
            FIXTURE_LGN_B0C92867,
            FIXTURE_LOG_EDCC8D9B,
            FIXTURE_GAM_5BC4EFCF,
            FIXTURE_UST_A0082146)) {
      for (String mutation :
          List.of(
              "request_version='002'",
              "response_version='002'",
              "response_layout_id='AUDRSP01'",
              "owner_user_id=" + (route.equals(FIXTURE_LGN_B0C92867) ? "7" : FIXTURE_NULL_F072CBEC),
              "operation_token="
                  + (route.equals(FIXTURE_UST_A0082146)
                      ? FIXTURE_NULL_F072CBEC
                      : "'" + UUID.randomUUID() + "'"),
              "result_ref_type='NONE',result_ref_id=9",
              "result_ref_type='NONE',result_ref_uuid='" + SESSION + "'")) {
        assertProtectedMutation(route, mutation);
      }
    }
    assertEquals("2", scalarAdmin("select count(*) from schubert.app_users"));
    assertEquals("1", scalarAdmin("select count(*) from schubert.script_files"));
  }

  @Test
  void exactRetentionCutoffAndReplay() throws Exception {
    for (String route : ROUTES) {
      long seconds =
          Set.of(FIXTURE_LGN_B0C92867, FIXTURE_LOG_EDCC8D9B).contains(route)
                  || TOKEN.contains(route)
              ? 604800
              : 86400;
      for (long adjustment : List.of(-1000L, 0L, 1000L)) {
        sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
        inbox(101, route, "COMPLETED", COMPLETED.plusSeconds(seconds).plusNanos(adjustment));
        if (Set.of(FIXTURE_QSB_661826BD, FIXTURE_NTC_1FFAAF5E, FIXTURE_QDL_6EE4F4E8)
            .contains(route))
          sql(
              "update schubert.request_inbox set result_ref_type='"
                  + (route.equals(FIXTURE_NTC_1FFAAF5E)
                      ? FIXTURE_JOB_804C2C2C
                      : FIXTURE_QUESTION_8F4A4C6B)
                  + "',result_ref_id=9");
        try (var c = restricted()) {
          assertEquals(List.of(MESSAGE), read(c, RUN, CUTOFF, null));
          assertEquals(
              adjustment >= 0, remove(c, RUN, CUTOFF, MESSAGE, xact(c), hash), route + "/boundary");
          c.rollback();
        }
        assertEquals("1", count());
      }
    }
    for (String mutation :
        List.of(
            "expires_at='2026-09-17T00:00:00.123Z'",
            "expires_at='infinity'",
            "created_at='-infinity'",
            "completed_at='-infinity'",
            "completed_at='infinity'",
            "created_at='2026-09-10T00:00:00Z'"))
      assertProtectedMutation(FIXTURE_GAM_5BC4EFCF, mutation);
    sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
    inbox(101, FIXTURE_GAM_5BC4EFCF, FIXTURE_ERROR_F717E7D8, CUTOFF.minusNanos(1000));
    try (var c = restricted()) {
      try (var s = c.createStatement()) {
        s.execute("set local timezone='Asia/Tokyo'");
      }
      assertEquals(List.of(MESSAGE), read(c, RUN, CUTOFF, null));
      assertTrue(remove(c, RUN, CUTOFF, MESSAGE, xact(c), hash));
      c.commit();
      assertFalse(remove(c, RUN, CUTOFF, MESSAGE, xact(c), hash));
      c.commit();
    }
    assertEquals("0", count());
  }

  @Test
  void argumentsHashAndTransactionBinding() throws Exception {
    for (String mutation :
        List.of(
            "processing_state='PROCESSING'",
            "response_body_encrypted=null,response_key_version=null",
            "response_layout_id=null,response_version=null",
            "result_ref_type=null",
            "result_ref_type='UNKNOWN'",
            "result_ref_type='USER',result_ref_id=0",
            "result_ref_type='USER',result_ref_id=1000000000000",
            "expires_at='-infinity'")) {
      assertProtectedMutation(FIXTURE_UST_A0082146, mutation);
    }
    Object[][] invalid = {
      {null, CUTOFF, MESSAGE, "1", hash},
      {RUN, null, MESSAGE, "1", hash},
      {RUN, CUTOFF, null, "1", hash},
      {RUN, CUTOFF, MESSAGE, null, hash},
      {RUN, CUTOFF, MESSAGE, "", hash},
      {RUN, CUTOFF, MESSAGE, "-1", hash},
      {RUN, CUTOFF, MESSAGE, "1x", hash},
      {RUN, CUTOFF, MESSAGE, "1".repeat(21), hash},
      {RUN, CUTOFF, MESSAGE, "1", null},
      {RUN, CUTOFF, MESSAGE, "1", new byte[31]},
      {RUN, CUTOFF, MESSAGE, "1", new byte[33]}
    };
    for (Object[] args : invalid) {
      try (var c = restricted()) {
        assertEquals(
            FIXTURE_22023_CDCA15BB,
            assertThrows(
                    SQLException.class,
                    () ->
                        remove(
                            c,
                            (UUID) args[0],
                            (Instant) args[1],
                            (UUID) args[2],
                            (String) args[3],
                            (byte[]) args[4]))
                .getSQLState());
      }
    }
    for (String infinity : List.of("infinity", "-infinity")) {
      denied(
          ROLE,
          FIXTURE_22023_CDCA15BB,
          "select message_id from schubert.maintenance_next_inbox('"
              + RUN
              + "','"
              + infinity
              + "',null)");
      denied(
          ROLE,
          FIXTURE_22023_CDCA15BB,
          "select schubert.maintenance_delete_inbox('"
              + RUN
              + "','"
              + infinity
              + "','"
              + MESSAGE
              + "','1',decode(repeat('00',32),'hex'))");
    }
    try (var c = restricted()) {
      assertEquals(
          FIXTURE_22023_CDCA15BB,
          assertThrows(SQLException.class, () -> read(c, null, CUTOFF, null)).getSQLState());
      c.rollback();
      assertEquals(
          FIXTURE_22023_CDCA15BB,
          assertThrows(SQLException.class, () -> read(c, RUN, null, null)).getSQLState());
      c.rollback();
      assertEquals(List.of(MESSAGE), read(c, RUN, CUTOFF, null));
      String transaction = xact(c);
      assertFalse(remove(c, RUN, CUTOFF, new UUID(0, 999), transaction, hash));
      assertFalse(remove(c, RUN, CUTOFF, MESSAGE, transaction, new byte[32]));
      c.commit();
      assertFalse(remove(c, RUN, CUTOFF, MESSAGE, transaction, hash));
      c.rollback();
    }
    try (var c = db.admin()) {
      c.setAutoCommit(false);
      assertEquals(List.of(MESSAGE), read(c, RUN, CUTOFF, null));
      try (var s = c.createStatement()) {
        assertEquals(
            1,
            s.executeUpdate(
                "update schubert.request_inbox set response_body_encrypted=decode(repeat('11',30),'hex')"));
      }
      assertFalse(remove(c, RUN, CUTOFF, MESSAGE, xact(c), hash));
      c.rollback();
    }
    assertEquals("1", count());
  }

  @Test
  void referencesStayLockedUntilTransactionEnds() throws Exception {
    for (String reference :
        List.of(
            FIXTURE_AUTH_SESSION_97533387, FIXTURE_USER_2DED8884, FIXTURE_SCENARIO_FILE_072D014E)) {
      sql(
          "update schubert.request_inbox set result_ref_type='"
              + reference
              + "',result_ref_id="
              + (reference.equals(FIXTURE_AUTH_SESSION_97533387)
                  ? FIXTURE_NULL_F072CBEC
                  : reference.equals(FIXTURE_USER_2DED8884) ? "9" : "11")
              + ",result_ref_uuid="
              + (reference.equals(FIXTURE_AUTH_SESSION_97533387)
                  ? "'" + SESSION + "'"
                  : FIXTURE_NULL_F072CBEC));
      String row =
          reference.equals(FIXTURE_AUTH_SESSION_97533387)
              ? "schubert.auth_sessions where id='" + SESSION + "'"
              : reference.equals(FIXTURE_USER_2DED8884)
                  ? "schubert.app_users where id=9"
                  : "schubert.script_files where id=11";
      try (var c = restricted()) {
        assertEquals(List.of(MESSAGE), read(c, RUN, CUTOFF, null));
        denied(
            FIXTURE_SCHUBERT_APP_5AB151CF,
            FIXTURE_55P03_0FE714C6,
            "select id from " + row + " for update nowait");
        denied(
            FIXTURE_SCHUBERT_APP_5AB151CF,
            FIXTURE_55P03_0FE714C6,
            "select message_id from schubert.request_inbox for update nowait");
        denied(
            "schubert_batch",
            FIXTURE_55P03_0FE714C6,
            "select id from schubert.batch_runs for update nowait");
        assertEquals(
            "7", scalarAdmin("select id from schubert.app_users where id=7 for update nowait"));
        c.rollback();
      }
      try (var c = db.api()) {
        assertNotNull(scalar(c, "select id from " + row + " for update nowait"));
      }
      if (reference.equals(FIXTURE_AUTH_SESSION_97533387))
        sql("delete from schubert.auth_sessions");
      else if (reference.equals(FIXTURE_USER_2DED8884))
        sql("delete from schubert.app_users where id=9");
      else sql("delete from schubert.script_files where id=11");
      try (var c = restricted()) {
        assertEquals(List.of(MESSAGE), read(c, RUN, CUTOFF, null));
      }
    }
  }

  @Test
  void backupGateAndSnapshotRace() throws Exception {
    denied(FIXTURE_SCHUBERT_APP_5AB151CF, "23514", "update schubert.batch_runs set status='ERROR'");
    for (String mutation :
        List.of(
            "delete from schubert.batch_runs",
            "delete from schubert.batch_runs where step='BACKUP_CONFIG'",
            "update schubert.batch_runs set status='RUNNING'",
            "update schubert.batch_runs set status='WARNING'",
            "update schubert.batch_runs set status='FAILED'",
            "update schubert.batch_runs set status='SKIPPED'",
            "update schubert.batch_runs set ended_at=null",
            "update schubert.batch_runs set business_date='2026-09-16'",
            "update schubert.batch_runs set run_id='00000000-0000-0000-0000-000000000099'")) {
      reset();
      sql(mutation);
      try (var c = restricted()) {
        assertEquals(
            "55000",
            assertThrows(SQLException.class, () -> read(c, RUN, CUTOFF, null)).getSQLState());
        c.rollback();
        String tx = xact(c);
        assertEquals(
            "55000",
            assertThrows(SQLException.class, () -> remove(c, RUN, CUTOFF, MESSAGE, tx, hash))
                .getSQLState());
      }
    }
    reset();
    try (var held = db.admin();
        var s = held.createStatement();
        var c = restricted()) {
      s.execute("select pg_advisory_lock(71419602)");
      assertEquals(
          FIXTURE_55P03_0FE714C6,
          assertThrows(SQLException.class, () -> read(c, RUN, CUTOFF, null)).getSQLState());
      c.rollback();
      String tx = xact(c);
      assertEquals(
          FIXTURE_55P03_0FE714C6,
          assertThrows(SQLException.class, () -> remove(c, RUN, CUTOFF, MESSAGE, tx, hash))
              .getSQLState());
      c.rollback();
      s.execute("select pg_advisory_unlock(71419602)");
    }
    for (boolean deleting : List.of(false, true)) {
      reset();
      sql("delete from schubert.batch_runs where step='BACKUP_CONFIG'");
      try (var writer = db.api();
          var inspected = restricted();
          var pool = Executors.newSingleThreadExecutor()) {
        writer.setAutoCommit(false);
        try (var s = writer.createStatement()) {
          s.execute("select id from schubert.batch_runs where step='BACKUP_DB' for update");
        }
        int pid = Integer.parseInt(scalar(inspected, "select pg_backend_pid()"));
        String tx = xact(inspected);
        var future =
            pool.submit(
                () -> {
                  try {
                    if (deleting) remove(inspected, RUN, CUTOFF, MESSAGE, tx, hash);
                    else read(inspected, RUN, CUTOFF, null);
                    return "UNEXPECTED_ACCEPT";
                  } catch (SQLException failure) {
                    return failure.getSQLState();
                  } finally {
                    inspected.rollback();
                  }
                });
        awaitBlocked(pid);
        backup("BACKUP_CONFIG");
        writer.commit();
        assertEquals("55000", future.get(5, TimeUnit.SECONDS));
      }
      try (var c = restricted()) {
        assertEquals(List.of(MESSAGE), read(c, RUN, CUTOFF, null));
        assertTrue(remove(c, RUN, CUTOFF, MESSAGE, xact(c), hash));
        c.rollback();
      }
      assertEquals("1", count());
    }
  }

  @Test
  void migrationAndExistingAuthenticationRemainCompatible() throws Exception {
    assertEquals(
        MigrationInventory.COUNT_TEXT,
        scalarAdmin(
            "select count(*) from schubert_meta.flyway_schema_history where success and version is not null"));
    Path migrations =
        Path.of(System.getProperty("nk.pt.repository"))
            .resolve("src/schubert-nk-api/src/main/resources/db/migration");
    var flyway =
        Flyway.configure()
            .dataSource(url, "schubert_migration", "")
            .defaultSchema("schubert_meta")
            .schemas("schubert_meta")
            .initSql("SET ROLE nk_owner")
            .locations("filesystem:" + migrations)
            .cleanDisabled(true)
            .load();
    assertTrue(flyway.validateWithResult().validationSuccessful);
    assertEquals(0, flyway.migrate().migrationsExecuted);
    // Frozen d98961c6 inventory, captured before V010. No expectation calculated from current SQL.
    List<String> oldHashes =
        List.of(
            "f687a36d1e296d38306997808b0f4440e484e24dd37b3862476fb470e56930da",
            "23f82d08f89bf6abfb75cbf41d126b174fcef5cf77563755fc316b31fb817e8e",
            "85f05cda30be1dd7856fb1eee3b25f42c6513641ab5d30b92410210f5460aa5e",
            "fdf634ace2beef2d57e28ad65c2ed488eab493cb2b0d8b1d421eab8397b8079e",
            "daf64a15c753cea106b593e6da944db08f7b13c94d3f2aa4ec6626fcd8b56ff9",
            "79623b56b8fe9d27af75df6a5db5cf47f4b93fb7b5ae2b9eb4d19ce6d6624052",
            "3b93f98b801c967c78113f3931b89b32aa9dc821d336af6c81076efc26da0401",
            "a90b338170322bd190335d2cfd382bb36b6f8b1243410345ef35b54dda928412",
            "537c7844709ed116f23fa60c64ae378e79eadad79f2e8003bbfd688f42335312");
    try (var files = Files.list(migrations)) {
      var old = files.filter(p -> p.getFileName().toString().startsWith("V00")).sorted().toList();
      assertEquals(9, old.size());
      for (int i = 0; i < 9; i++)
        assertEquals(
            oldHashes.get(i),
            HexFormat.of()
                .formatHex(
                    MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(old.get(i)))));
    }
    sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
    inbox(101, FIXTURE_LGN_B0C92867, FIXTURE_ERROR_F717E7D8, CUTOFF.minusSeconds(1));
    try (var c = restricted()) {
      assertEquals(
          MESSAGE.toString(),
          scalar(
              c,
              "select message_id from schubert.maintenance_next_auth_inbox('"
                  + RUN
                  + "','"
                  + CUTOFF
                  + "',null)"));
      try (var s = c.prepareStatement("select schubert.maintenance_delete_auth_inbox(?,?,?,?,?)")) {
        s.setObject(1, RUN);
        s.setObject(2, CUTOFF.atOffset(java.time.ZoneOffset.UTC));
        s.setObject(3, MESSAGE);
        s.setString(4, xact(c));
        s.setBytes(5, hash);
        try (var r = s.executeQuery()) {
          assertTrue(r.next());
          assertTrue(r.getBoolean(1));
          assertFalse(r.next());
        }
      }
      c.rollback();
      assertEquals(List.of(MESSAGE), read(c, RUN, CUTOFF, null));
      assertTrue(remove(c, RUN, CUTOFF, MESSAGE, xact(c), hash));
      c.rollback();
    }
    assertEquals("1", count());
  }

  private static void assertProtectedMutation(String route, String mutation) throws SQLException {
    sql(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
    inbox(101, route, FIXTURE_ERROR_F717E7D8, CUTOFF.minusSeconds(1));
    try (var c = db.admin();
        var s = c.createStatement()) {
      c.setAutoCommit(false);
      for (String name :
          List.of("owner", "operation_token", "result_reference", "time_order", "state_fields"))
        s.execute("alter table schubert.request_inbox drop constraint ck_request_inbox_" + name);
      assertEquals(1, s.executeUpdate("update schubert.request_inbox set " + mutation));
      assertFalse(remove(c, RUN, CUTOFF, MESSAGE, xact(c), hash), route + "/protected metadata");
      c.rollback();
    }
    assertEquals("1", count());
  }

  private static Connection restricted() throws SQLException {
    var c = DriverManager.getConnection(url, ROLE, "");
    c.setAutoCommit(false);
    return c;
  }

  private static List<UUID> read(Connection c, UUID run, Instant cutoff, UUID after)
      throws SQLException {
    try (var s =
        c.prepareStatement("select message_id from schubert.maintenance_next_inbox(?,?,?)")) {
      s.setObject(1, run);
      s.setObject(2, cutoff == null ? null : cutoff.atOffset(java.time.ZoneOffset.UTC));
      s.setObject(3, after);
      try (var r = s.executeQuery()) {
        var ids = new ArrayList<UUID>();
        while (r.next()) ids.add(r.getObject(1, UUID.class));
        return ids;
      }
    }
  }

  private static boolean remove(
      Connection c, UUID run, Instant cutoff, UUID message, String tx, byte[] digest)
      throws SQLException {
    try (var s = c.prepareStatement("select schubert.maintenance_delete_inbox(?,?,?,?,?)")) {
      s.setObject(1, run);
      s.setObject(2, cutoff == null ? null : cutoff.atOffset(java.time.ZoneOffset.UTC));
      s.setObject(3, message);
      s.setString(4, tx);
      s.setBytes(5, digest);
      try (var r = s.executeQuery()) {
        assertTrue(r.next());
        boolean result = r.getBoolean(1);
        assertFalse(r.wasNull());
        assertFalse(r.next());
        return result;
      }
    }
  }

  private static String xact(Connection c) throws SQLException {
    return scalar(c, "select pg_current_xact_id()::text");
  }

  private static String count() throws SQLException {
    return scalarAdmin("select count(*) from schubert.request_inbox");
  }

  private static String scalarAdmin(String query) throws SQLException {
    try (var c = db.admin()) {
      return scalar(c, query);
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

  private static void backup(String step) throws SQLException {
    try (var c = db.api();
        var s =
            c.prepareStatement(
                "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status) values (?,'2026-09-17',?,1,'2026-09-17T00:00:00Z','2026-09-17T00:00:01Z','SUCCESS')")) {
      s.setObject(1, RUN);
      s.setString(2, step);
      assertEquals(1, s.executeUpdate());
    }
  }

  private static void inbox(long number, String route, String state, Instant expires)
      throws SQLException {
    boolean processing = state.equals("PROCESSING");
    UUID id = new UUID(0, number);
    try (var c = db.api();
        var s =
            c.prepareStatement(
                "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,owner_user_id,operation_token,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at) values (?,?,?,'001',?,?,repeat('a',64),'v1',?,?,?,?,?,?,'2026-09-09T00:00:00Z',?,?)")) {
      s.setObject(1, id);
      s.setObject(2, id);
      s.setString(3, route + "REQ01");
      s.setObject(4, route.equals(FIXTURE_LGN_B0C92867) ? null : 7L);
      s.setObject(5, TOKEN.contains(route) ? UUID.randomUUID() : null);
      s.setString(6, state);
      s.setString(7, processing ? null : FIXTURE_NONE_C44E6DD7);
      s.setString(8, processing ? null : route + "RSP01");
      s.setString(9, processing ? null : "001");
      s.setBytes(10, processing ? null : new byte[30]);
      s.setString(11, processing ? null : "v1");
      s.setObject(12, processing ? null : COMPLETED.atOffset(java.time.ZoneOffset.UTC));
      s.setObject(13, expires.atOffset(java.time.ZoneOffset.UTC));
      assertEquals(1, s.executeUpdate());
    }
  }

  private static void awaitBlocked(int pid) throws SQLException {
    long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(4);
    try (var c = db.admin();
        var s = c.prepareStatement("select cardinality(pg_blocking_pids(?))>0")) {
      s.setInt(1, pid);
      do {
        try (var r = s.executeQuery()) {
          assertTrue(r.next());
          if (r.getBoolean(1)) return;
        }
      } while (System.nanoTime() < deadline);
      fail("controlled backup snapshot lock was not reached");
    }
  }
}
