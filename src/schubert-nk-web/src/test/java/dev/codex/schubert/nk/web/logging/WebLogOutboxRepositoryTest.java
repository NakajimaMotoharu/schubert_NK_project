package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-IDEM-012: SS 324/331/332 SQL after-conditions independent of production query generation. */
final class WebLogOutboxRepositoryTest {
  private static final Instant NOW = Instant.parse("2026-09-06T00:00:00Z");
  private static final UUID CORRELATION = new UUID(4, 5);
  private static final EncryptedWebLogPayload PAYLOAD =
      new EncryptedWebLogPayload("test", new byte[64]);
  private static WebLogDatabaseFixture db;

  @BeforeAll
  static void start(@TempDir Path root) throws Exception {
    db = new WebLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) {
      db.stop();
    }
  }

  @BeforeEach
  void reset() throws SQLException {
    db.reset();
  }

  @Test
  void encryptedInsertIsCallerAtomicDuplicateRetainsFirstAndWebCannotReachBusiness()
      throws Exception {
    WebLogOutboxRepository repository = new WebLogOutboxRepository(() -> 0);
    WebLogPayloadIdentity identity = identity(1);
    try (Connection connection = db.transaction()) {
      assertTrue(repository.enqueue(connection, identity, PAYLOAD, NOW));
      assertEquals(0, count());
      connection.rollback();
    }
    assertEquals(0, count());
    try (Connection connection = db.transaction()) {
      assertTrue(repository.enqueue(connection, identity, PAYLOAD, NOW));
      assertFalse(
          repository.enqueue(
              connection,
              identity,
              new EncryptedWebLogPayload("changed", new byte[65]),
              NOW.plusSeconds(4)));
      connection.commit();
    }
    assertEquals(1, count());
    try (Connection connection = db.transaction()) {
      ClaimedWebLog row = repository.claim(connection, "writer", NOW, 1).getFirst();
      assertEquals(identity, row.identity());
      assertArrayEquals(new byte[64], row.payload().ciphertext());
      assertEquals("test", row.payload().keyVersion());
      assertEquals(NOW, row.createdAt());
      assertEquals(NOW, row.nextAttemptAt());
      assertEquals(NOW.plusSeconds(10), row.leaseUntil());
      assertEquals("writer", row.leaseOwner());
      assertEquals(0, row.attemptCount());
      assertEquals("ClaimedWebLog[identity/payload/lease=<redacted>]", row.toString());
      connection.rollback();
    }
    try (Connection connection = db.web();
        var statement = connection.createStatement()) {
      SQLException denied =
          assertThrows(
              SQLException.class, () -> statement.executeQuery("select id from schubert.app_logs"));
      assertEquals("42501", denied.getSQLState());
    }
  }

  @Test
  void dueAndStrictLeaseBoundariesSkipLocksLimit100AndNeverClaimSent() throws Exception {
    WebLogOutboxRepository repository = new WebLogOutboxRepository(() -> 0);
    insert(1, NOW);
    insert(2, NOW);
    insert(3, NOW.plusMillis(1));
    update(
        "update schubert_web_session.web_log_outbox set lease_owner='busy',lease_until=timestamp with time zone '2026-09-06 00:00:00Z' where message_id='"
            + identity(2).messageId()
            + "'");
    try (Connection first = db.transaction();
        Connection second = db.transaction()) {
      List<ClaimedWebLog> one = repository.claim(first, "first", NOW, 100);
      assertEquals(List.of(identity(1)), one.stream().map(ClaimedWebLog::identity).toList());
      assertTrue(repository.claim(second, "second", NOW, 100).isEmpty());
      assertTrue(repository.markSent(first, one.getFirst(), NOW));
      first.commit();
      second.commit();
    }
    try (Connection connection = db.transaction()) {
      List<ClaimedWebLog> rows = repository.claim(connection, "expiry", NOW.plusMillis(1), 100);
      assertEquals(
          List.of(identity(2), identity(3)), rows.stream().map(ClaimedWebLog::identity).toList());
      connection.rollback();
    }
    db.reset();
    for (int id = 1; id <= 102; id++) {
      insert(id, NOW);
    }
    try (Connection first = db.transaction();
        Connection second = db.transaction()) {
      List<ClaimedWebLog> hundred = repository.claim(first, "first", NOW, 100);
      List<ClaimedWebLog> two = repository.claim(second, "second", NOW, 100);
      assertEquals(100, hundred.size());
      assertEquals(2, two.size());
      assertEquals(
          102,
          java.util.stream.Stream.concat(hundred.stream(), two.stream())
              .map(ClaimedWebLog::id)
              .distinct()
              .count());
      assertThrows(UnsupportedOperationException.class, () -> hundred.add(two.getFirst()));
      first.rollback();
      second.rollback();
    }
  }

  @Test
  void resultUpdatesProtectOwnerAndPersistExactJitterAllStagesIncludingAttemptCap()
      throws Exception {
    long[][] expected = {
      {900, 1000, 1100},
      {4500, 5000, 5500},
      {27000, 30000, 33000},
      {54000, 60000, 66000},
      {270000, 300000, 330000},
      {270000, 300000, 330000},
      {270000, 300000, 330000}
    };
    int[] attempts = {0, 1, 2, 3, 4, 99, 100};
    for (int index = 0; index < attempts.length; index++) {
      for (int boundary = 0; boundary < 3; boundary++) {
        db.reset();
        int jitter = (boundary - 1) * 100;
        WebLogOutboxRepository repository = new WebLogOutboxRepository(() -> jitter);
        insert(1, NOW);
        update("update schubert_web_session.web_log_outbox set attempt_count=" + attempts[index]);
        try (Connection connection = db.transaction()) {
          ClaimedWebLog row = repository.claim(connection, "owner", NOW, 1).getFirst();
          ClaimedWebLog wrong = withOwner(row, "other");
          assertFalse(repository.markSent(connection, wrong, NOW));
          assertFalse(repository.markFailure(connection, wrong, NOW, "JMS_FAILURE"));
          assertTrue(repository.markFailure(connection, row, NOW.plusSeconds(3), "JMS_FAILURE"));
          connection.commit();
        }
        try (Connection connection = db.web();
            var statement = connection.createStatement();
            var rows =
                statement.executeQuery(
                    "select status,attempt_count,next_attempt_at,lease_owner,lease_until,sent_at,last_error_code from schubert_web_session.web_log_outbox")) {
          assertTrue(rows.next());
          assertEquals("ERROR", rows.getString(1));
          assertEquals(Math.min(100, attempts[index] + 1), rows.getInt(2));
          assertEquals(
              NOW.plusMillis(3000 + expected[index][boundary]),
              rows.getObject(3, java.time.OffsetDateTime.class).toInstant());
          assertNull(rows.getString(4));
          assertNull(rows.getObject(5, java.time.OffsetDateTime.class));
          assertNull(rows.getObject(6, java.time.OffsetDateTime.class));
          assertEquals("JMS_FAILURE", rows.getString(7));
        }
      }
    }
    db.reset();
    insert(1, NOW);
    WebLogOutboxRepository random = new WebLogOutboxRepository();
    try (Connection connection = db.transaction()) {
      ClaimedWebLog row = random.claim(connection, "random", NOW, 1).getFirst();
      assertTrue(random.markFailure(connection, row, NOW, "JMS_FAILURE"));
      ClaimedWebLog retried = random.claim(connection, "random", NOW.plusSeconds(2), 1).getFirst();
      assertFalse(retried.nextAttemptAt().isBefore(NOW.plusMillis(900)));
      assertFalse(retried.nextAttemptAt().isAfter(NOW.plusMillis(1100)));
      assertTrue(random.markSent(connection, retried, NOW.plusSeconds(3)));
      assertFalse(random.markSent(connection, retried, NOW.plusSeconds(4)));
      assertFalse(random.markFailure(connection, retried, NOW.plusSeconds(4), "JMS_FAILURE"));
      connection.commit();
    }
    assertEquals("SENT", scalar("status"));
    assertNull(scalar("last_error_code"));
    assertNull(scalar("lease_owner"));
  }

  @Test
  void nullInvalidDatabaseRowsAndBoundsFailClosedWithoutNpeRecovery() throws Exception {
    WebLogOutboxRepository repository = new WebLogOutboxRepository(() -> 0);
    assertThrows(NullPointerException.class, () -> new WebLogOutboxRepository(null));
    assertThrows(
        NullPointerException.class, () -> repository.enqueue(null, identity(1), PAYLOAD, NOW));
    try (Connection auto = db.web()) {
      assertThrows(IllegalStateException.class, () -> repository.claim(auto, "w", NOW, 1));
    }
    insert(1, NOW);
    try (Connection connection = db.transaction()) {
      ClaimedWebLog row = repository.claim(connection, "worker", NOW, 1).getFirst();
      assertThrows(
          NullPointerException.class, () -> repository.enqueue(connection, null, PAYLOAD, NOW));
      assertThrows(
          NullPointerException.class, () -> repository.enqueue(connection, identity(2), null, NOW));
      assertThrows(
          NullPointerException.class,
          () -> repository.enqueue(connection, identity(2), PAYLOAD, null));
      assertThrows(NullPointerException.class, () -> repository.claim(connection, null, NOW, 1));
      assertThrows(NullPointerException.class, () -> repository.claim(connection, "w", null, 1));
      for (String worker : List.of("", " ", "bad\nowner", "x".repeat(65))) {
        assertThrows(
            IllegalArgumentException.class, () -> repository.claim(connection, worker, NOW, 1));
      }
      for (int limit : new int[] {0, 101}) {
        assertThrows(
            IllegalArgumentException.class, () -> repository.claim(connection, "w", NOW, limit));
      }
      assertThrows(NullPointerException.class, () -> repository.markSent(connection, null, NOW));
      assertThrows(NullPointerException.class, () -> repository.markSent(connection, row, null));
      assertThrows(
          NullPointerException.class, () -> repository.markFailure(connection, null, NOW, "X"));
      assertThrows(
          NullPointerException.class, () -> repository.markFailure(connection, row, null, "X"));
      assertThrows(
          NullPointerException.class, () -> repository.markFailure(connection, row, NOW, null));
      for (String error : List.of("", " ", "X\n", "x".repeat(65))) {
        assertThrows(
            IllegalArgumentException.class,
            () -> repository.markFailure(connection, row, NOW, error));
      }
      for (int jitter : new int[] {-101, 101}) {
        assertThrows(
            IllegalArgumentException.class,
            () -> new WebLogOutboxRepository(() -> jitter).markFailure(connection, row, NOW, "X"));
      }
      assertEquals("worker", ClaimedWebLog.requireWorker("worker"));
      for (long id : new long[] {0, 1_000_000_000_000L}) {
        assertThrows(
            IllegalArgumentException.class,
            () -> model(id, 0, row.identity(), row.payload(), NOW, NOW, "w", NOW));
      }
      assertEquals(
          999_999_999_999L,
          model(999_999_999_999L, 100, row.identity(), row.payload(), NOW, NOW, "x".repeat(64), NOW)
              .id());
      for (int attempt : new int[] {-1, 101}) {
        assertThrows(
            IllegalArgumentException.class,
            () -> model(1, attempt, row.identity(), row.payload(), NOW, NOW, "w", NOW));
      }
      assertThrows(
          NullPointerException.class, () -> model(1, 0, null, PAYLOAD, NOW, NOW, "w", NOW));
      assertThrows(
          NullPointerException.class, () -> model(1, 0, identity(1), null, NOW, NOW, "w", NOW));
      assertThrows(
          NullPointerException.class, () -> model(1, 0, identity(1), PAYLOAD, null, NOW, "w", NOW));
      assertThrows(
          NullPointerException.class, () -> model(1, 0, identity(1), PAYLOAD, NOW, null, "w", NOW));
      assertThrows(
          NullPointerException.class, () -> model(1, 0, identity(1), PAYLOAD, NOW, NOW, "w", null));
      connection.rollback();
    }
    Map<String, Object> fields =
        new HashMap<>(
            Map.ofEntries(
                Map.entry("id", 1L),
                Map.entry("message_id", identity(1).messageId()),
                Map.entry("correlation_id", CORRELATION),
                Map.entry("layout_id", "WLGEVT01"),
                Map.entry("layout_version", "001"),
                Map.entry("key_version", "test"),
                Map.entry("payload_ciphertext", new byte[64]),
                Map.entry("attempt_count", 0),
                Map.entry("next_attempt_at", NOW.atOffset(java.time.ZoneOffset.UTC)),
                Map.entry("created_at", NOW.atOffset(java.time.ZoneOffset.UTC)),
                Map.entry("lease_owner", "worker"),
                Map.entry("lease_until", NOW.plusSeconds(10).atOffset(java.time.ZoneOffset.UTC))));
    assertEquals(1, WebLogOutboxRepository.read(result(fields)).id());
    for (String column : fields.keySet()) {
      Map<String, Object> altered = new HashMap<>(fields);
      altered.put(column, null);
      assertThrows(
          SQLDataException.class, () -> WebLogOutboxRepository.read(result(altered)), column);
    }
    fields.put("layout_id", "QWKREQ01");
    assertEquals(
        "22000",
        assertThrows(SQLDataException.class, () -> WebLogOutboxRepository.read(result(fields)))
            .getSQLState());
  }

  private static ClaimedWebLog model(
      long id,
      int count,
      WebLogPayloadIdentity identity,
      EncryptedWebLogPayload payload,
      Instant due,
      Instant created,
      String owner,
      Instant until) {
    return new ClaimedWebLog(id, identity, payload, count, due, created, owner, until);
  }

  private static ClaimedWebLog withOwner(ClaimedWebLog row, String owner) {
    return model(
        row.id(),
        row.attemptCount(),
        row.identity(),
        row.payload(),
        row.nextAttemptAt(),
        row.createdAt(),
        owner,
        row.leaseUntil());
  }

  private static ResultSet result(Map<String, Object> fields) {
    return (ResultSet)
        Proxy.newProxyInstance(
            ResultSet.class.getClassLoader(),
            new Class<?>[] {ResultSet.class},
            (proxy, method, arguments) -> fields.get((String) arguments[0]));
  }

  private static WebLogPayloadIdentity identity(long id) {
    return new WebLogPayloadIdentity(new UUID(3, id), CORRELATION);
  }

  private static void insert(long id, Instant due) throws SQLException {
    try (Connection connection = db.transaction()) {
      assertTrue(
          new WebLogOutboxRepository(() -> 0).enqueue(connection, identity(id), PAYLOAD, due));
      connection.commit();
    }
  }

  private static void update(String sql) throws SQLException {
    try (Connection connection = db.web();
        var statement = connection.createStatement()) {
      statement.executeUpdate(sql);
    }
  }

  private static long count() throws SQLException {
    try (Connection connection = db.web();
        var statement = connection.createStatement();
        var result =
            statement.executeQuery("select count(*) from schubert_web_session.web_log_outbox")) {
      assertTrue(result.next());
      return result.getLong(1);
    }
  }

  private static String scalar(String column) throws SQLException {
    try (Connection connection = db.web();
        var statement = connection.createStatement();
        var result =
            statement.executeQuery(
                "select " + column + "::text from schubert_web_session.web_log_outbox")) {
      assertTrue(result.next());
      return result.getString(1);
    }
  }
}
