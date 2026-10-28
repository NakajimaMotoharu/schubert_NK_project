package dev.codex.schubert.nk.api.database;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.HexFormat;
import java.util.List;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.io.TempDir;

/** PT-QST-STATE-001..003; UI242/SS331/SSC152/BUG422/YKT333. Independent legacy DB oracle. */
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
final class NotificationStateMigrationTest {
  private static final String FIXTURE_VALUE_E91D96ED = "','";
  private static final String FIXTURE_ACCEPTED_E50B782C = "ACCEPTED";
  private static final String FIXTURE_ERROR_F717E7D8 = "ERROR";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;
  private static String url;
  private static Path resources;
  private static String history;
  private static final String TIME = "2026-09-01 00:00:00+00";

  @BeforeAll
  static void startLegacy() throws Exception {
    database = new ApiLogDatabaseFixture(root, "023");
    resources =
        Path.of(System.getProperty("nk.pt.repository"))
            .resolve("src/schubert-nk-api/src/main/resources/db");
    try (var c = database.admin()) {
      url = c.getMetaData().getURL();
      sql(
          c,
          "insert into schubert.app_users(id,username,username_key,password_hash,role,status,"
              + "password_changed_at,created_at,updated_at) values(7,'Learner','learner','synthetic-unused',"
              + "'USER','ACTIVE','"
              + TIME
              + FIXTURE_VALUE_E91D96ED
              + TIME
              + FIXTURE_VALUE_E91D96ED
              + TIME
              + "')");
      sql(
          c,
          "insert into schubert.questions(id,receipt_id,owner_user_id,body,operation_token,submitted_at) "
              + "values(9,'00000000000000000000000000',7,'independent question',"
              + "'00000000-0000-0000-0000-000000000011','"
              + TIME
              + "')");
      sql(
          c,
          "insert into schubert.async_jobs(id,question_id,owner_user_id,state,message_id,"
              + "correlation_id,received_at,state_changed_at) values(11,9,7,'RECEIVED',"
              + "'00000000-0000-0000-0000-000000000021','00000000-0000-0000-0000-000000000021',"
              + "'"
              + TIME
              + FIXTURE_VALUE_E91D96ED
              + TIME
              + "')");
      sql(
          c,
          "insert into schubert.notifications(id,job_id,question_id,owner_user_id,notification_type,"
              + "state,accepted_at,state_changed_at,created_at,updated_at) values(12,11,9,7,'ACCEPTED',"
              + "'ACCEPTED','"
              + TIME
              + FIXTURE_VALUE_E91D96ED
              + TIME
              + FIXTURE_VALUE_E91D96ED
              + TIME
              + FIXTURE_VALUE_E91D96ED
              + TIME
              + "')");
      history =
          value(
              c,
              "select string_agg(version||':'||checksum,',' order by installed_rank) "
                  + "from schubert_meta.flyway_schema_history where version is not null");
      assertEquals(
          "23",
          value(
              c,
              "select count(*) from schubert_meta.flyway_schema_history where version is not null"));
    }
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  private static Flyway upgrade() {
    return Flyway.configure()
        .dataSource(url, "schubert_migration", "")
        .defaultSchema("schubert_meta")
        .schemas("schubert_meta")
        .createSchemas(true)
        .initSql("SET ROLE nk_owner")
        .locations("filesystem:" + resources.resolve("migration"))
        .validateOnMigrate(true)
        .cleanDisabled(true)
        .target("024")
        .load();
  }

  @Test
  @Order(1)
  void inconsistentLegacyJobStopsWholeMigrationWithoutGuessingState() throws Exception {
    try (var c = database.admin()) {
      sql(
          c,
          "update schubert.async_jobs set state='PROCESSING',started_at='"
              + TIME
              + "',processing_message_id='00000000-0000-0000-0000-000000000031' where id=11");
      var failure =
          assertThrows(org.flywaydb.core.api.FlywayException.class, () -> upgrade().migrate());
      assertTrue(failure.getMessage().contains("LEGACY_NOTIFICATION_STATE"));
      assertEquals(
          FIXTURE_ACCEPTED_E50B782C,
          value(c, "select state from schubert.notifications where id=12"));
      assertEquals(
          history,
          value(
              c,
              "select string_agg(version||':'||checksum,',' order by installed_rank) "
                  + "from schubert_meta.flyway_schema_history where version is not null"));
      assertEquals(
          "0",
          value(c, "select count(*) from schubert_meta.flyway_schema_history where not success"));
      assertTrue(
          value(
                  c,
                  "select pg_get_constraintdef(oid) from pg_constraint "
                      + "where conrelid='schubert.notifications'::regclass and conname='ck_notifications_state'")
              .contains(FIXTURE_ACCEPTED_E50B782C));
      sql(
          c,
          "update schubert.async_jobs set state='RECEIVED',started_at=null,processing_message_id=null where id=11");
    }
  }

  @Test
  @Order(2)
  void realUpgradePreservesAllOldHistoryAndLegacyIdentityContentTimes() throws Exception {
    assertEquals(1, upgrade().migrate().migrationsExecuted);
    assertEquals(0, upgrade().migrate().migrationsExecuted);
    assertTrue(upgrade().validateWithResult().validationSuccessful);
    try (var c = database.admin()) {
      assertEquals(
          history,
          value(
              c,
              "select string_agg(version||':'||checksum,',' order by installed_rank) "
                  + "from schubert_meta.flyway_schema_history where version is not null and version<>'024'"));
      assertEquals(
          "24",
          value(
              c,
              "select count(*) from schubert_meta.flyway_schema_history where version is not null"));
      assertEquals(
          "12|11|9|7|ACCEPTED|RECEIVED|2026-09-01 00:00:00|2026-09-01 00:00:00|2026-09-01 00:00:00|2026-09-01 00:00:00",
          value(
              c,
              "select id||'|'||job_id||'|'||question_id||'|'||owner_user_id||'|'||notification_type||'|'||state"
                  + "||'|'||(accepted_at at time zone 'UTC')||'|'||(state_changed_at at time zone 'UTC')"
                  + "||'|'||(created_at at time zone 'UTC')||'|'||(updated_at at time zone 'UTC') from schubert.notifications where id=12"));
      assertEquals(
          "9|00000000000000000000000000|7|independent question|00000000-0000-0000-0000-000000000011|false|0",
          value(
              c,
              "select id||'|'||receipt_id||'|'||owner_user_id||'|'||body||'|'||operation_token||'|'||is_deleted||'|'||version from schubert.questions where id=9"));
      assertEquals(
          "11|9|7|RECEIVED|00000000-0000-0000-0000-000000000021|00000000-0000-0000-0000-000000000021|0",
          value(
              c,
              "select id||'|'||question_id||'|'||owner_user_id||'|'||state||'|'||message_id||'|'||correlation_id||'|'||version from schubert.async_jobs where id=11"));
    }
    assertEquals(
        "85f05cda30be1dd7856fb1eee3b25f42c6513641ab5d30b92410210f5460aa5e",
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(
                        Files.readAllBytes(
                            resources.resolve(
                                "migration/V003__business_message_log_and_web_tables.sql")))));
  }

  @Test
  @Order(3)
  void exactStateAllowlistAndLeastPrivilegeRemainEnforced() throws Exception {
    try (var c = database.api()) {
      c.setAutoCommit(false);
      for (String state :
          List.of("RECEIVED", "PROCESSING", "COMPLETED", FIXTURE_ERROR_F717E7D8, "CANCELLED")) {
        String code = state.equals(FIXTURE_ERROR_F717E7D8) ? "'PROCESS_FAILED'" : "null";
        String detail =
            state.equals(FIXTURE_ERROR_F717E7D8) ? "'independent public error'" : "null";
        String type =
            state.equals(FIXTURE_ERROR_F717E7D8) || state.equals("COMPLETED")
                ? state
                : FIXTURE_ACCEPTED_E50B782C;
        sql(
            c,
            "update schubert.notifications set state='"
                + state
                + "',notification_type='"
                + type
                + "',error_code="
                + code
                + ",error_message="
                + detail
                + " where id=12");
        assertEquals(state, value(c, "select state from schubert.notifications where id=12"));
        assertEquals(
            type, value(c, "select notification_type from schubert.notifications where id=12"));
      }
      for (String invalid : List.of(FIXTURE_ACCEPTED_E50B782C, "UNKNOWN", "", "received")) {
        var point = c.setSavepoint();
        assertEquals(
            "23514",
            assertThrows(
                    SQLException.class,
                    () ->
                        sql(
                            c,
                            "update schubert.notifications set state='"
                                + invalid
                                + "' where id=12"))
                .getSQLState());
        c.rollback(point);
      }
      // SS331/V005 grants API DML, not DDL/TRUNCATE. Do not change the approved grants for this
      // fix.
      for (String privilege : List.of("SELECT", "INSERT", "UPDATE", "DELETE"))
        assertEquals(
            "true",
            value(
                c,
                "select has_table_privilege(current_user,'schubert.notifications','"
                    + privilege
                    + "')::text"));
      assertEquals(
          "false",
          value(
              c,
              "select has_table_privilege(current_user,'schubert.notifications','TRUNCATE')::text"));
      assertEquals(
          "false",
          value(
              c,
              "select has_table_privilege('schubert_batch','schubert.notifications','SELECT')::text"));
      c.rollback();
    }
    try (var c = DriverManager.getConnection(url, "schubert_web_session", "")) {
      assertEquals(
          "false", value(c, "select has_schema_privilege(current_user,'schubert','USAGE')::text"));
      assertEquals(
          "42501",
          assertThrows(
                  SQLException.class, () -> value(c, "select state from schubert.notifications"))
              .getSQLState());
    }
  }

  private static String value(Connection c, String query) throws SQLException {
    try (var s = c.createStatement();
        var rows = s.executeQuery(query)) {
      assertTrue(rows.next());
      var result = rows.getString(1);
      assertNotNull(result);
      assertFalse(rows.next());
      return result;
    }
  }

  private static void sql(Connection c, String command) throws SQLException {
    try (var s = c.createStatement()) {
      s.execute(command);
    }
  }
}
