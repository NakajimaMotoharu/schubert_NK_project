package dev.codex.schubert.nk.api.database;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.io.TempDir;

/** PT-QST-DLQ-DB; SS331/SSC155. Independent SQL values, real V024->V025, no deployed data. */
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
final class QuestionDlqMigrationTest {
  private static final String FIXTURE_VALUE_E91D96ED = "','";
  private static final String FIXTURE_NK_DEAD_LETTER_6588D12C = "nk.dead.letter";
  private static final String FIXTURE_23514_8632CD65 = "23514";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;
  private static String url;
  private static String history;
  private static final String W = "84000000-0000-4000-8000-000000000001";
  private static final String D = "84000000-0000-4000-8000-000000000002";
  private static final String C = "84000000-0000-4000-8000-000000000003";
  private static final String W2 = "84000000-0000-4000-8000-000000000004";
  private static final String TIME = "2026-10-01 00:00:00+00";

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root, "024");
    try (var c = database.admin()) {
      url = c.getMetaData().getURL();
      sql(c, legacy(1, "nk.async.work", W));
      sql(c, legacy(2, FIXTURE_NK_DEAD_LETTER_6588D12C, D));
      history =
          value(
              c,
              "select string_agg(version||':'||checksum,',' order by installed_rank) "
                  + "from schubert_meta.flyway_schema_history where version is not null");
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
        .locations(
            "filesystem:"
                + Path.of(System.getProperty("nk.pt.repository"))
                    .resolve("src/schubert-nk-api/src/main/resources/db/migration"))
        .validateOnMigrate(true)
        .cleanDisabled(true)
        .target("025")
        .load();
  }

  @Test
  @Order(1)
  void legacyDlqRejectsWholeMigrationWithoutInventingMetadataThenOrdinarySurvives()
      throws Exception {
    var failure =
        assertThrows(org.flywaydb.core.api.FlywayException.class, () -> upgrade().migrate());
    assertTrue(failure.getMessage().contains("LEGACY_DLQ_METADATA_REQUIRED"));
    try (var c = database.admin()) {
      assertEquals(
          history,
          value(
              c,
              "select string_agg(version||':'||checksum,',' order by installed_rank) "
                  + "from schubert_meta.flyway_schema_history where version is not null"));
      assertEquals(
          "0",
          value(
              c,
              "select count(*) from information_schema.columns where "
                  + "table_schema='schubert' and table_name='mq_outbox' and column_name like 'dlq_%'"));
      assertEquals("2", value(c, "select count(*) from schubert.mq_outbox"));
      assertEquals(
          "0",
          value(c, "select count(*) from schubert_meta.flyway_schema_history where not success"));
      sql(c, "delete from schubert.mq_outbox where id=2");
    }
    assertEquals(1, upgrade().migrate().migrationsExecuted);
    assertEquals(0, upgrade().migrate().migrationsExecuted);
    assertTrue(upgrade().validateWithResult().validationSuccessful);
    try (var c = database.admin()) {
      assertEquals(
          history,
          value(
              c,
              "select string_agg(version||':'||checksum,',' order by installed_rank) "
                  + "from schubert_meta.flyway_schema_history where version is not null and version<>'025'"));
    }
    try (var c = database.api()) {
      assertEquals(
          W + "|" + C + "|nk.async.work|SENT|320|0|2026-10-01 00:00:00",
          value(
              c,
              "select message_id||'|'||correlation_id||'|'||destination||'|'||status||'|'||"
                  + "octet_length(body)||'|'||attempt_count||'|'||(sent_at at time zone 'UTC') "
                  + "from schubert.mq_outbox where id=1"));
      assertEquals(
          "true",
          value(
              c,
              "select (dlq_original_message_id is null and "
                  + "dlq_original_transport_id is null and dlq_delivery_count is null and "
                  + "dlq_error_code is null and dlq_detected_at is null)::text from schubert.mq_outbox where id=1"));
    }
  }

  @Test
  @Order(2)
  void requiredProfileAllNullCombinationsBoundsAndOriginalUniqueAreDbEnforced() throws Exception {
    try (var c = database.api()) {
      c.setAutoCommit(false);
      List<String> valid = values(W2);
      for (int mask = 1; mask < 32; mask++) {
        List<String> bad = new ArrayList<>(valid);
        for (int field = 0; field < 5; field++)
          if ((mask & (1 << field)) != 0) bad.set(field, "null");
        rejectInsert(c, bad, FIXTURE_NK_DEAD_LETTER_6588D12C, FIXTURE_23514_8632CD65);
      }
      rejectInsert(c, values(D), FIXTURE_NK_DEAD_LETTER_6588D12C, FIXTURE_23514_8632CD65);
      rejectInsert(c, valid, "nk.async.work", FIXTURE_23514_8632CD65);
      for (String invalid : List.of("''", "' '", "E'\\n'", "chr(127)", "'日'")) {
        var bad = new ArrayList<>(valid);
        bad.set(1, invalid);
        rejectInsert(c, bad, FIXTURE_NK_DEAD_LETTER_6588D12C, FIXTURE_23514_8632CD65);
      }
      var tooLong = new ArrayList<>(valid);
      tooLong.set(1, "repeat('x',129)");
      rejectInsert(c, tooLong, FIXTURE_NK_DEAD_LETTER_6588D12C, "22001");
      for (String invalid : List.of("0", "-1")) {
        var bad = new ArrayList<>(valid);
        bad.set(2, invalid);
        rejectInsert(c, bad, FIXTURE_NK_DEAD_LETTER_6588D12C, FIXTURE_23514_8632CD65);
      }
      for (String invalid : List.of("'UNKNOWN'", "''", "'question_retry_exhausted'")) {
        var bad = new ArrayList<>(valid);
        bad.set(3, invalid);
        rejectInsert(c, bad, FIXTURE_NK_DEAD_LETTER_6588D12C, FIXTURE_23514_8632CD65);
      }
      for (String invalid :
          List.of("'infinity'", "'-infinity'", "'0001-01-01 BC'", "'10000-01-01+00'")) {
        var bad = new ArrayList<>(valid);
        bad.set(4, invalid);
        rejectInsert(c, bad, FIXTURE_NK_DEAD_LETTER_6588D12C, FIXTURE_23514_8632CD65);
      }
      for (String time : List.of("0001-01-01 00:00:00+00", "9999-12-31 23:59:59.999999+00")) {
        var point = c.setSavepoint();
        var bounded = new ArrayList<>(valid);
        bounded.set(1, "repeat('x',128)");
        bounded.set(2, "2147483647");
        bounded.set(4, "'" + time + "'");
        sql(c, insert(bounded, FIXTURE_NK_DEAD_LETTER_6588D12C));
        assertEquals(
            "2147483647|128",
            value(
                c,
                "select dlq_delivery_count||'|'||length(dlq_original_transport_id) from schubert.mq_outbox where id=10"));
        c.rollback(point);
      }
      sql(c, insert(values(W), FIXTURE_NK_DEAD_LETTER_6588D12C));
      var point = c.setSavepoint();
      assertEquals(
          "23505",
          assertThrows(
                  SQLException.class,
                  () ->
                      sql(
                          c,
                          insert(values(W), FIXTURE_NK_DEAD_LETTER_6588D12C)
                              .replace("values(10,", "values(11,")
                              .replace("'" + D + "'", "'84000000-0000-4000-8000-000000000005'")))
              .getSQLState());
      c.rollback(point);
      assertEquals("SENT", value(c, "select status from schubert.mq_outbox where id=1"));
      c.rollback();
    }
  }

  @Test
  @Order(3)
  void originalMetadataAndWireCannotBeRewrittenButDispatchStatusCan() throws Exception {
    try (var c = database.api()) {
      c.setAutoCommit(false);
      sql(c, insert(values(W), FIXTURE_NK_DEAD_LETTER_6588D12C));
      for (String assignment :
          List.of(
              "dlq_original_message_id='" + W2 + "'",
              "dlq_original_transport_id='OTHER'",
              "dlq_delivery_count=5",
              "dlq_error_code='UNKNOWN'",
              "dlq_detected_at='2026-10-02+00'",
              "message_id='" + W2 + "'",
              "correlation_id='" + W2 + "'",
              "destination='nk.async.work'",
              "layout_id='LOGREQ01'",
              "layout_version='002'",
              "body=decode(repeat('58',320),'hex')",
              "created_at='2026-10-02+00'")) {
        var point = c.setSavepoint();
        var failure =
            assertThrows(
                SQLException.class,
                () -> sql(c, "update schubert.mq_outbox set " + assignment + " where id=10"));
        assertEquals(FIXTURE_23514_8632CD65, failure.getSQLState());
        assertTrue(failure.getMessage().contains("IMMUTABLE_DLQ_IDENTITY"));
        c.rollback(point);
      }
      sql(
          c,
          "update schubert.mq_outbox set status='ERROR',attempt_count=1,last_error_code='JMS_SEND_FAILURE',"
              + "last_error_detail='public bounded diagnostic' where id=10");
      sql(
          c,
          "update schubert.mq_outbox set status='SENT',sent_at='"
              + TIME
              + "',last_error_code=null,last_error_detail=null where id=10");
      assertEquals(
          "SENT|4|QUESTION_RETRY_EXHAUSTED|ID:original",
          value(
              c,
              "select status||'|'||dlq_delivery_count||'|'||dlq_error_code||'|'||dlq_original_transport_id from schubert.mq_outbox where id=10"));
      assertEquals(
          "false",
          value(
              c,
              "select has_function_privilege('schubert_batch','schubert.guard_dlq_outbox_identity()','EXECUTE')::text"));
      c.rollback();
    }
  }

  private static List<String> values(String original) {
    return List.of(
        "'" + original + "'", "'ID:original'", "4", "'QUESTION_RETRY_EXHAUSTED'", "'" + TIME + "'");
  }

  @Test
  @Order(4)
  void layoutVersionBodyAndOrdinaryReclassificationAreNotRepairShortcuts() throws Exception {
    try (var c = database.api()) {
      c.setAutoCommit(false);
      String good = insert(values(W2), FIXTURE_NK_DEAD_LETTER_6588D12C);
      for (String bad :
          List.of(
              good.replace("'QWKREQ01'", "'LOGREQ01'"),
              good.replace("'001'", "'002'"),
              good.replace("repeat('57',320)", "repeat('57',319)"),
              good.replace("repeat('57',320)", "repeat('57',321)"))) {
        var point = c.setSavepoint();
        assertEquals(
            FIXTURE_23514_8632CD65,
            assertThrows(SQLException.class, () -> sql(c, bad)).getSQLState());
        c.rollback(point);
      }
      var point = c.setSavepoint();
      var failure =
          assertThrows(
              SQLException.class,
              () ->
                  sql(
                      c,
                      "update schubert.mq_outbox set destination='nk.dead.letter',dlq_original_message_id='"
                          + W2
                          + "',dlq_original_transport_id='ID:original',dlq_delivery_count=4,"
                          + "dlq_error_code='QUESTION_RETRY_EXHAUSTED',dlq_detected_at='"
                          + TIME
                          + "' where id=1"));
      assertEquals(FIXTURE_23514_8632CD65, failure.getSQLState());
      assertTrue(failure.getMessage().contains("IMMUTABLE_DLQ_IDENTITY"));
      c.rollback(point);
      assertEquals(
          "nk.async.work|SENT",
          value(c, "select destination||'|'||status from schubert.mq_outbox where id=1"));
      c.rollback();
    }
  }

  private static String legacy(int id, String destination, String message) {
    return "insert into schubert.mq_outbox(id,message_id,correlation_id,destination,layout_id,layout_version,body,status,next_attempt_at,created_at,sent_at) values("
        + id
        + ",'"
        + message
        + FIXTURE_VALUE_E91D96ED
        + C
        + FIXTURE_VALUE_E91D96ED
        + destination
        + "','QWKREQ01','001',decode(repeat('57',320),'hex'),'SENT','"
        + TIME
        + FIXTURE_VALUE_E91D96ED
        + TIME
        + FIXTURE_VALUE_E91D96ED
        + TIME
        + "')";
  }

  private static String insert(List<String> metadata, String destination) {
    return "insert into schubert.mq_outbox(id,message_id,correlation_id,destination,layout_id,layout_version,body,status,next_attempt_at,created_at,dlq_original_message_id,dlq_original_transport_id,dlq_delivery_count,dlq_error_code,dlq_detected_at) values(10,'"
        + D
        + FIXTURE_VALUE_E91D96ED
        + C
        + FIXTURE_VALUE_E91D96ED
        + destination
        + "','QWKREQ01','001',decode(repeat('57',320),'hex'),'PENDING','"
        + TIME
        + FIXTURE_VALUE_E91D96ED
        + TIME
        + "',"
        + String.join(",", metadata)
        + ")";
  }

  private static void rejectInsert(
      Connection c, List<String> values, String destination, String state) throws Exception {
    var point = c.setSavepoint();
    assertEquals(
        state,
        assertThrows(SQLException.class, () -> sql(c, insert(values, destination))).getSQLState());
    c.rollback(point);
  }

  private static void sql(Connection c, String sql) throws SQLException {
    try (var s = c.createStatement()) {
      s.execute(sql);
    }
  }

  private static String value(Connection c, String sql) throws SQLException {
    try (var s = c.createStatement();
        var r = s.executeQuery(sql)) {
      assertTrue(r.next());
      String value = r.getString(1);
      assertFalse(r.next());
      return value;
    }
  }
}
