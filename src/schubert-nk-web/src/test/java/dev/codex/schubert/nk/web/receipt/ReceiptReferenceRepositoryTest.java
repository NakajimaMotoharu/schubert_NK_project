package dev.codex.schubert.nk.web.receipt;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** QA048/SS331 9.4; RCPT001..003/005, independent literal SQL and tuple oracle. */
class ReceiptReferenceRepositoryTest {
  static final String ID = "00000000000000000000000001";
  static final Instant TIME = Instant.parse("2026-10-04T00:00:00.123Z");
  static WebLogDatabaseFixture db;

  @BeforeAll
  static void start(@TempDir Path root) throws Exception {
    db = new WebLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void clear() throws Exception {
    try (var c = db.web();
        var s = c.createStatement()) {
      s.executeUpdate("delete from schubert_web_session.web_receipt_references");
    }
  }

  static DataSource source() {
    return (DataSource)
        Proxy.newProxyInstance(
            DataSource.class.getClassLoader(),
            new Class<?>[] {DataSource.class},
            (proxy, method, args) -> {
              if (method.getName().equals("getConnection")) return db.web();
              throw new UnsupportedOperationException("unused fixture method");
            });
  }

  @Test
  void rcpt001LiteralBoundariesAndNullContracts() {
    var r = new ReceiptReference(ID, 1, TIME);
    assertEquals(ID, r.receiptId());
    assertEquals(1, r.questionId());
    assertEquals(TIME, r.submittedAt());
    assertEquals("ReceiptReference[redacted]", r.toString());
    assertEquals(999999999999L, new ReceiptReference(ID, 999999999999L, TIME).questionId());
    for (String bad : List.of("", "0".repeat(25), "0".repeat(27), "I".repeat(26), "a".repeat(26)))
      assertThrows(IllegalArgumentException.class, () -> new ReceiptReference(bad, 1, TIME));
    for (long bad : new long[] {Long.MIN_VALUE, 0, 1000000000000L, Long.MAX_VALUE})
      assertThrows(IllegalArgumentException.class, () -> new ReceiptReference(ID, bad, TIME));
    assertThrows(
        IllegalArgumentException.class, () -> new ReceiptReference(ID, 1, TIME.plusNanos(1)));
    assertThrows(NullPointerException.class, () -> new ReceiptReference(null, 1, TIME));
    assertThrows(NullPointerException.class, () -> new ReceiptReference(ID, 1, null));
    assertThrows(NullPointerException.class, () -> new ReceiptReferenceRepository(null));
    var repo = new ReceiptReferenceRepository(source());
    assertThrows(NullPointerException.class, () -> repo.register(null));
    assertThrows(NullPointerException.class, () -> repo.find(null));
    assertThrows(IllegalArgumentException.class, () -> repo.find("invalid"));
  }

  @Test
  void rcpt002IndependentPersistedTupleIdempotenceAndConflict() throws Exception {
    var repo = new ReceiptReferenceRepository(source());
    assertEquals(Optional.empty(), repo.find(ID));
    var original = new ReceiptReference(ID, 7, TIME);
    repo.register(original);
    repo.register(original);
    assertEquals(Optional.of(new ReceiptReference(ID, 7, TIME)), repo.find(ID));
    assertThrows(
        ReceiptReferenceException.class, () -> repo.register(new ReceiptReference(ID, 8, TIME)));
    assertThrows(
        ReceiptReferenceException.class,
        () -> repo.register(new ReceiptReference(ID, 7, TIME.plusMillis(1))));
    try (var c = db.web();
        var s = c.createStatement();
        var row =
            s.executeQuery(
                "select receipt_id,question_id,submitted_at from schubert_web_session.web_receipt_references")) {
      assertTrue(row.next());
      assertEquals(ID, row.getString(1));
      assertEquals(7, row.getLong(2));
      assertEquals(
          OffsetDateTime.parse("2026-10-04T00:00:00.123Z"), row.getObject(3, OffsetDateTime.class));
      assertFalse(row.next());
    }
    assertEquals("receipt reference unavailable", new ReceiptReferenceException().getMessage());
  }

  @Test
  void rcpt003CatalogRolesAndInvalidDdlInputs() throws Exception {
    try (var c = db.admin();
        var s = c.createStatement();
        var row =
            s.executeQuery(
                "select string_agg(column_name,',' order by ordinal_position) from information_schema.columns where table_schema='schubert_web_session' and table_name='web_receipt_references'")) {
      assertTrue(row.next());
      assertEquals("receipt_id,question_id,submitted_at", row.getString(1));
    }
    try (var c = db.web();
        var s = c.createStatement()) {
      assertThrows(
          SQLException.class,
          () -> s.execute("update schubert_web_session.web_receipt_references set question_id=1"));
      assertThrows(SQLException.class, () -> s.execute("select id from schubert.questions"));
      for (String values :
          List.of(
              "'00000000000000000000000001',0,'2026-10-04Z'",
              "'00000000000000000000000001',1000000000000,'2026-10-04Z'",
              "'00000000000000000000000001',1,'infinity'",
              "'00000000000000000000000001',1,'2026-10-04T00:00:00.000001Z'",
              "'IIIIIIIIIIIIIIIIIIIIIIIIII',1,'2026-10-04Z'",
              "NULL,1,'2026-10-04Z'",
              "'00000000000000000000000001',NULL,'2026-10-04Z'",
              "'00000000000000000000000001',1,NULL"))
        assertThrows(
            SQLException.class,
            () ->
                s.execute(
                    "insert into schubert_web_session.web_receipt_references values("
                        + values
                        + ")"));
    }
    try (var c = db.admin();
        var s = c.createStatement()) {
      for (String role : List.of("schubert_app", "schubert_batch")) {
        s.execute("set role " + role);
        assertThrows(
            SQLException.class,
            () -> s.execute("select * from schubert_web_session.web_receipt_references"));
        s.execute("reset role");
      }
      s.execute("set role schubert_backup");
      try (var row =
          s.executeQuery("select count(*) from schubert_web_session.web_receipt_references")) {
        assertTrue(row.next());
        assertEquals(0, row.getLong(1));
      }
      s.execute("reset role");
      try (var row =
          s.executeQuery(
              "select has_function_privilege('schubert_batch','schubert.maintenance_cleanup_web_receipt_references(uuid,timestamptz,integer)','EXECUTE'),has_function_privilege('schubert_web_session','schubert.maintenance_cleanup_web_receipt_references(uuid,timestamptz,integer)','EXECUTE')")) {
        assertTrue(row.next());
        assertTrue(row.getBoolean(1));
        assertFalse(row.getBoolean(2));
      }
    }
  }

  @Test
  void rcpt005HundredParallelSameTupleDoesNotOverwrite() throws Exception {
    var repo = new ReceiptReferenceRepository(source());
    try (var executor = Executors.newFixedThreadPool(10)) {
      var futures = new ArrayList<Future<?>>();
      for (int n = 0; n < 100; n++)
        futures.add(executor.submit(() -> repo.register(new ReceiptReference(ID, 7, TIME))));
      for (var future : futures) future.get(30, TimeUnit.SECONDS);
    }
    assertEquals(Optional.of(new ReceiptReference(ID, 7, TIME)), repo.find(ID));
    try (var c = db.web();
        var s = c.createStatement();
        var row =
            s.executeQuery("select count(*) from schubert_web_session.web_receipt_references")) {
      assertTrue(row.next());
      assertEquals(1, row.getLong(1));
    }
  }
}
