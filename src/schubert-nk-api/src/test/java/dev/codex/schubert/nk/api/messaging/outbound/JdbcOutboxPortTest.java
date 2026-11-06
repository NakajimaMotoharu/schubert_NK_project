package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-OUT-JDBC001..008; SS331/332 independent SQL/UTC/lease/retry oracle; BUG2366/YKT2111. */
final class JdbcOutboxPortTest {
  private static final Instant NOW = Instant.parse("2026-01-02T03:04:05.123456Z");
  private static final UUID MESSAGE = UUID.fromString("00000000-0000-4000-8000-000000000001");
  private static final UUID CORRELATION = UUID.fromString("00000000-0000-4000-8000-000000000002");
  private static final UUID ORIGINAL = UUID.fromString("00000000-0000-4000-8000-000000000003");
  private static final String OWNER = "owned-worker";
  private static final String CODE = "TEMPORARY";
  private static final String DETAIL = "bounded public failure";
  private static final String DLQ_CODE = "QUESTION_RETRY_EXHAUSTED";
  private static final String ATTEMPT = "attempt_count";
  private static final String NEXT = "next_attempt_at";
  private static final String CREATED = "created_at";
  private static final String LEASE_OWNER = "lease_owner";
  private static final String LEASE_UNTIL = "lease_until";
  private static final String ORIGINAL_ID = "dlq_original_message_id";
  private static final String TRANSPORT = "dlq_original_transport_id";
  private static final String DELIVERY = "dlq_delivery_count";
  private static final String ERROR_CODE = "dlq_error_code";
  private static final String DETECTED = "dlq_detected_at";

  private static OffsetDateTime utc(Instant value) {
    return value.atOffset(ZoneOffset.UTC);
  }

  private static byte[] body() {
    byte[] bytes = new byte[320];
    Arrays.fill(bytes, (byte) ' ');
    return bytes;
  }

  private static OutboxDlqMetadata dlq() {
    return new OutboxDlqMetadata(ORIGINAL, "PUBLIC-UNISSUED-ID", 7, DLQ_CODE, NOW);
  }

  private static OutboxRequest request(boolean dead) {
    return new OutboxRequest(
        MESSAGE,
        CORRELATION,
        dead ? OutboxDestination.DLQ : OutboxDestination.ASYNC_WORK,
        "QWKREQ01",
        "001",
        body(),
        NOW,
        NOW.minusSeconds(1),
        dead ? Optional.of(dlq()) : Optional.empty());
  }

  private static OutboxEntry entry(int attempt) {
    return new OutboxEntry(
        7,
        MESSAGE,
        CORRELATION,
        OutboxDestination.ASYNC_WORK,
        "QWKREQ01",
        "001",
        body(),
        attempt,
        NOW,
        NOW.minusSeconds(1),
        OWNER,
        NOW.plusSeconds(10));
  }

  private static Map<Object, Object> row(long id, Instant next) {
    Map<Object, Object> values = new HashMap<>();
    values.put("id", id);
    values.put("message_id", MESSAGE);
    values.put("correlation_id", CORRELATION);
    values.put("destination", "nk.async.work");
    values.put("layout_id", "QWKREQ01");
    values.put("layout_version", "001");
    values.put("body", body());
    values.put(ATTEMPT, 0);
    values.put(NEXT, utc(next));
    values.put(CREATED, utc(NOW.minusSeconds(1)));
    values.put(LEASE_OWNER, OWNER);
    values.put(LEASE_UNTIL, utc(NOW.plusSeconds(10)));
    return values;
  }

  private static <T> T port(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }

  private static final class Fixture {
    private final Map<Integer, Object> parameters = new HashMap<>();
    private final Map<Integer, Integer> nullTypes = new HashMap<>();
    private final List<Map<Object, Object>> rows = new ArrayList<>();
    private final List<String> calls = new ArrayList<>();
    private int index = -1;
    private int affected = 1;
    private boolean autoCommit;
    private boolean resultClosed;
    private boolean statementClosed;
    private String sql;
    private String fail = "";
    private final SQLException failure = new SQLException("public synthetic JDBC fault");

    private void check(String point) throws SQLException {
      calls.add(point);
      if (point.equals(fail)) {
        throw failure;
      }
    }

    private ResultSet result() {
      return port(
          ResultSet.class,
          (proxy, method, args) -> {
            String operation = method.getName();
            check("result." + operation);
            if (operation.equals("close")) {
              resultClosed = true;
              return null;
            }
            if (operation.equals("next")) {
              return ++index < rows.size();
            }
            if (operation.startsWith("get")) {
              Object value = rows.get(index).get(args[0]);
              if (operation.equals("getLong")) {
                return value == null ? 0L : value;
              }
              return value;
            }
            throw new AssertionError("unexpected result operation " + operation);
          });
    }

    private PreparedStatement statement() {
      return port(
          PreparedStatement.class,
          (proxy, method, args) -> {
            String operation = method.getName();
            check("statement." + operation);
            if (operation.startsWith("set")) {
              int position = (Integer) args[0];
              if (operation.equals("setNull")) {
                nullTypes.put(position, (Integer) args[1]);
                parameters.put(position, null);
              } else {
                parameters.put(position, args[1]);
              }
              return null;
            }
            return switch (operation) {
              case "executeQuery" -> result();
              case "executeUpdate" -> affected;
              case "close" -> {
                statementClosed = true;
                yield null;
              }
              default -> throw new AssertionError("unexpected statement operation " + operation);
            };
          });
    }

    private Connection connection() {
      return port(
          Connection.class,
          (proxy, method, args) -> {
            String operation = method.getName();
            check("connection." + operation);
            return switch (operation) {
              case "getAutoCommit" -> autoCommit;
              case "prepareStatement" -> {
                sql = (String) args[0];
                yield statement();
              }
              default -> throw new AssertionError("borrowed transaction changed: " + operation);
            };
          });
    }

    private void borrowed() {
      assertFalse(
          calls.stream()
              .anyMatch(
                  c ->
                      c.equals("connection.close")
                          || c.equals("connection.commit")
                          || c.equals("connection.rollback")
                          || c.equals("connection.setAutoCommit")));
    }
  }

  @Test
  void enqueueBindsExactUtcAndOptionalDlqWithoutOwningTransaction() throws Exception {
    var repository = new JdbcOutboxRepository(() -> 0);
    for (boolean dead : List.of(false, true)) {
      var f = new Fixture();
      f.rows.add(Map.of(1, 42L));
      assertEquals(42L, repository.enqueue(f.connection(), request(dead)));
      assertEquals(
          "insert into schubert.mq_outbox(message_id,correlation_id,destination,layout_id,"
              + "layout_version,body,status,attempt_count,next_attempt_at,created_at,dlq_original_message_id,dlq_original_transport_id,dlq_delivery_count,dlq_error_code,dlq_detected_at)"
              + " values(?,?,?,?,?,?,'PENDING',0,?,?,?,?,?,?,?) returning id",
          f.sql);
      assertEquals(13, f.parameters.size());
      assertEquals(MESSAGE, f.parameters.get(1));
      assertEquals(CORRELATION, f.parameters.get(2));
      assertEquals(dead ? "nk.dead.letter" : "nk.async.work", f.parameters.get(3));
      assertEquals("QWKREQ01", f.parameters.get(4));
      assertEquals("001", f.parameters.get(5));
      assertArrayEquals(body(), (byte[]) f.parameters.get(6));
      assertEquals(utc(NOW), f.parameters.get(7));
      assertEquals(utc(NOW.minusSeconds(1)), f.parameters.get(8));
      if (dead) {
        assertEquals(
            List.of(ORIGINAL, "PUBLIC-UNISSUED-ID", 7, DLQ_CODE, utc(NOW)),
            List.of(
                f.parameters.get(9),
                f.parameters.get(10),
                f.parameters.get(11),
                f.parameters.get(12),
                f.parameters.get(13)));
        assertTrue(f.nullTypes.isEmpty());
      } else {
        assertEquals(
            Map.of(
                9,
                java.sql.Types.OTHER,
                10,
                java.sql.Types.VARCHAR,
                11,
                java.sql.Types.INTEGER,
                12,
                java.sql.Types.VARCHAR,
                13,
                java.sql.Types.TIMESTAMP_WITH_TIMEZONE),
            f.nullTypes);
        for (int index = 9; index <= 13; index++) {
          assertNull(f.parameters.get(index));
        }
      }
      assertTrue(f.statementClosed && f.resultClosed);
      f.borrowed();
    }
    var absent = new Fixture();
    assertThrows(
        OutboxIntegrityException.class,
        () -> repository.enqueue(absent.connection(), request(false)));
    assertTrue(absent.resultClosed && absent.statementClosed);
  }

  @Test
  void claimUsesBoundedLeaseStableOrderAndImmutableRowBody() throws Exception {
    var repository = new JdbcOutboxRepository(() -> 0);
    for (int limit : List.of(1, 100)) {
      var f = new Fixture();
      f.rows.add(row(9, NOW));
      f.rows.add(row(7, NOW.minusSeconds(1)));
      f.rows.add(row(8, NOW));
      List<OutboxEntry> entries = repository.claim(f.connection(), OWNER, NOW, limit);
      assertEquals(List.of(7L, 8L, 9L), entries.stream().map(OutboxEntry::id).toList());
      assertTrue(f.sql.contains("next_attempt_at<=?"));
      assertTrue(f.sql.contains("lease_until is null or lease_until<?"));
      assertTrue(f.sql.contains("order by next_attempt_at,id for update skip locked limit ?"));
      assertTrue(f.sql.contains("status in ('PENDING','ERROR')"));
      assertEquals(
          Map.of(1, utc(NOW), 2, utc(NOW), 3, limit, 4, OWNER, 5, utc(NOW.plusSeconds(10))),
          f.parameters);
      assertThrows(UnsupportedOperationException.class, () -> entries.clear());
      byte[] changed = entries.getFirst().body();
      changed[0] = 0;
      assertEquals((byte) ' ', entries.getFirst().body()[0]);
      assertEquals(NOW.minusSeconds(1), entries.getFirst().createdAt());
      assertEquals(NOW.plusSeconds(10), entries.getFirst().leaseUntil());
      assertEquals(OWNER, entries.getFirst().leaseOwner());
      assertEquals(0, entries.getFirst().attemptCount());
      assertTrue(f.resultClosed && f.statementClosed);
      f.borrowed();
    }
    var empty = new Fixture();
    assertEquals(List.of(), repository.claim(empty.connection(), OWNER, NOW, 1));
    assertTrue(empty.resultClosed && empty.statementClosed);
  }

  @Test
  void requiredAndInvalidRowsFailClosedIncludingNullableAttempt() {
    var repository = new JdbcOutboxRepository(() -> 0);
    for (String column :
        List.of(
            "id",
            "message_id",
            "correlation_id",
            "destination",
            "layout_id",
            "layout_version",
            "body",
            ATTEMPT,
            NEXT,
            CREATED,
            LEASE_OWNER,
            LEASE_UNTIL)) {
      var f = new Fixture();
      var values = row(7, NOW);
      values.put(column, null);
      f.rows.add(values);
      assertThrows(
          OutboxIntegrityException.class,
          () -> repository.claim(f.connection(), OWNER, NOW, 1),
          column);
      assertTrue(f.resultClosed && f.statementClosed);
      f.borrowed();
    }
    Map<String, Object> invalid =
        Map.of(
            "id",
            -1L,
            "destination",
            "unknown",
            "layout_id",
            "bad",
            "layout_version",
            "bad",
            "body",
            new byte[0],
            ATTEMPT,
            101,
            LEASE_OWNER,
            " ");
    for (var item : invalid.entrySet()) {
      var f = new Fixture();
      var values = row(7, NOW);
      values.put(item.getKey(), item.getValue());
      f.rows.add(values);
      var thrown =
          assertThrows(
              OutboxIntegrityException.class,
              () -> repository.claim(f.connection(), OWNER, NOW, 1));
      assertInstanceOf(IllegalArgumentException.class, thrown.getCause());
    }
  }

  @Test
  void dlqMetadataIsAllOrNoneAndPreservesClosedProjection() throws Exception {
    var repository = new JdbcOutboxRepository(() -> 0);
    Map<String, Object> fields =
        Map.of(
            ORIGINAL_ID,
            ORIGINAL,
            TRANSPORT,
            "PUBLIC-UNISSUED-ID",
            DELIVERY,
            7,
            ERROR_CODE,
            DLQ_CODE,
            DETECTED,
            utc(NOW));
    for (String partial : List.of(TRANSPORT, DELIVERY, ERROR_CODE, DETECTED)) {
      var f = new Fixture();
      var values = row(7, NOW);
      values.put(partial, fields.get(partial));
      f.rows.add(values);
      assertThrows(
          OutboxIntegrityException.class, () -> repository.claim(f.connection(), OWNER, NOW, 1));
    }
    for (String missing : List.of(TRANSPORT, DELIVERY, ERROR_CODE, DETECTED)) {
      var f = new Fixture();
      var values = row(7, NOW);
      values.put("destination", "nk.dead.letter");
      values.putAll(fields);
      values.put(missing, null);
      f.rows.add(values);
      assertThrows(
          OutboxIntegrityException.class, () -> repository.claim(f.connection(), OWNER, NOW, 1));
    }
    var good = new Fixture();
    var values = row(7, NOW);
    values.put("destination", "nk.dead.letter");
    values.putAll(fields);
    good.rows.add(values);
    assertEquals(
        dlq(),
        repository.claim(good.connection(), OWNER, NOW, 1).getFirst().dlqMetadata().orElseThrow());
    var wrong = new Fixture();
    var invalid = row(7, NOW);
    invalid.putAll(fields);
    wrong.rows.add(invalid);
    assertThrows(
        OutboxIntegrityException.class, () -> repository.claim(wrong.connection(), OWNER, NOW, 1));
  }

  @Test
  void sentAndFailureCompareAndSetUseIndependentRetryTableAndCap() throws Exception {
    for (int affected : List.of(0, 1, 2)) {
      var f = new Fixture();
      f.affected = affected;
      assertEquals(
          affected == 1, new JdbcOutboxRepository(() -> 0).markSent(f.connection(), entry(0), NOW));
      assertEquals(Map.of(1, utc(NOW), 2, 7L, 3, OWNER), f.parameters);
      assertTrue(f.sql.contains("status='SENT',sent_at=?"));
      assertTrue(f.sql.contains("where id=? and lease_owner=? and status in ('PENDING','ERROR')"));
      assertTrue(f.sql.contains("lease_until=null,last_error_code=null,last_error_detail=null"));
      assertTrue(f.statementClosed);
      f.borrowed();
    }
    int[] attempts = {0, 1, 2, 3, 4, 99, 100};
    long[] baseMillis = {1000, 5000, 30000, 60000, 300000, 300000, 300000};
    for (int index = 0; index < attempts.length; index++) {
      for (int jitter : List.of(-100, 0, 100)) {
        for (int affected : List.of(0, 1, 2)) {
          var f = new Fixture();
          f.affected = affected;
          assertEquals(
              affected == 1,
              new JdbcOutboxRepository(() -> jitter)
                  .markFailure(f.connection(), entry(attempts[index]), NOW, CODE, DETAIL));
          long expectedDelay = baseMillis[index] + baseMillis[index] * jitter / 1000;
          assertEquals(
              Map.of(
                  1,
                  Math.min(100, attempts[index] + 1),
                  2,
                  utc(NOW.plusMillis(expectedDelay)),
                  3,
                  CODE,
                  4,
                  DETAIL,
                  5,
                  7L,
                  6,
                  OWNER,
                  7,
                  attempts[index]),
              f.parameters);
          assertTrue(f.sql.contains("status='ERROR',attempt_count=?,next_attempt_at=?"));
          assertTrue(f.sql.contains("lease_owner=null,lease_until=null,sent_at=null"));
          assertTrue(f.sql.contains("where id=? and lease_owner=? and attempt_count=?"));
          assertTrue(f.sql.contains("status in ('PENDING','ERROR')"));
          assertTrue(f.statementClosed);
          f.borrowed();
        }
      }
    }
    var random = new Fixture();
    assertTrue(
        new JdbcOutboxRepository().markFailure(random.connection(), entry(0), NOW, CODE, DETAIL));
    OffsetDateTime due = (OffsetDateTime) random.parameters.get(2);
    assertFalse(due.isBefore(utc(NOW.plusMillis(900))));
    assertFalse(due.isAfter(utc(NOW.plusMillis(1100))));
  }

  @Test
  void argumentsAndTransactionsPreventSqlAndRespectErrorBounds() throws Exception {
    var repository = new JdbcOutboxRepository(() -> 0);
    assertThrows(NullPointerException.class, () -> new JdbcOutboxRepository(null));
    assertThrows(NullPointerException.class, () -> repository.enqueue(null, request(false)));
    var auto = new Fixture();
    auto.autoCommit = true;
    assertThrows(
        IllegalStateException.class, () -> repository.enqueue(auto.connection(), request(false)));
    assertNull(auto.sql);
    var f = new Fixture();
    assertThrows(NullPointerException.class, () -> repository.enqueue(f.connection(), null));
    assertThrows(NullPointerException.class, () -> repository.claim(f.connection(), null, NOW, 1));
    assertThrows(
        IllegalArgumentException.class, () -> repository.claim(f.connection(), " ", NOW, 1));
    assertThrows(
        NullPointerException.class, () -> repository.claim(f.connection(), OWNER, null, 1));
    for (int limit : List.of(0, -1, 101)) {
      assertThrows(
          IllegalArgumentException.class,
          () -> repository.claim(f.connection(), OWNER, NOW, limit));
    }
    assertThrows(NullPointerException.class, () -> repository.markSent(f.connection(), null, NOW));
    assertThrows(
        NullPointerException.class, () -> repository.markSent(f.connection(), entry(0), null));
    assertThrows(
        NullPointerException.class,
        () -> repository.markFailure(f.connection(), null, NOW, CODE, DETAIL));
    assertThrows(
        NullPointerException.class,
        () -> repository.markFailure(f.connection(), entry(0), null, CODE, DETAIL));
    assertThrows(
        NullPointerException.class,
        () -> repository.markFailure(f.connection(), entry(0), NOW, null, DETAIL));
    assertThrows(
        NullPointerException.class,
        () -> repository.markFailure(f.connection(), entry(0), NOW, CODE, null));
    for (String bad : List.of("", " ", "x".repeat(65), "x\nx")) {
      assertThrows(
          IllegalArgumentException.class,
          () -> repository.markFailure(f.connection(), entry(0), NOW, bad, DETAIL));
    }
    for (String bad : List.of("", " ", "x".repeat(257), "x\tx")) {
      assertThrows(
          IllegalArgumentException.class,
          () -> repository.markFailure(f.connection(), entry(0), NOW, CODE, bad));
    }
    assertNull(f.sql);
    assertTrue(
        repository.markFailure(f.connection(), entry(0), NOW, "x".repeat(64), "x".repeat(256)));
    for (int jitter : List.of(-101, 101)) {
      var rejected = new Fixture();
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new JdbcOutboxRepository(() -> jitter)
                  .markFailure(rejected.connection(), entry(0), NOW, CODE, DETAIL));
      assertNull(rejected.sql);
    }
  }

  @Test
  void ordinarySqlFaultsCloseOnlyRepositoryResourcesAndRemainFailures() throws Exception {
    var repository = new JdbcOutboxRepository(() -> 0);
    for (String point :
        List.of(
            "connection.getAutoCommit",
            "connection.prepareStatement",
            "statement.setObject",
            "statement.setString",
            "statement.setBytes",
            "statement.setNull",
            "statement.executeQuery",
            "result.next",
            "result.getObject",
            "result.close",
            "statement.close")) {
      var f = new Fixture();
      f.rows.add(Map.of(1, 7L));
      f.fail = point;
      assertSame(
          f.failure,
          assertThrows(
              SQLException.class, () -> repository.enqueue(f.connection(), request(false))));
      f.borrowed();
    }
    for (String point :
        List.of("statement.setInt", "result.getLong", "result.getString", "result.getBytes")) {
      var f = new Fixture();
      f.rows.add(row(7, NOW));
      f.fail = point;
      assertSame(
          f.failure,
          assertThrows(SQLException.class, () -> repository.claim(f.connection(), OWNER, NOW, 1)));
      f.borrowed();
    }
    for (boolean sent : List.of(false, true)) {
      var f = new Fixture();
      f.fail = "statement.executeUpdate";
      assertSame(
          f.failure,
          assertThrows(
              SQLException.class,
              () -> {
                if (sent) {
                  repository.markSent(f.connection(), entry(0), NOW);
                } else {
                  repository.markFailure(f.connection(), entry(0), NOW, CODE, DETAIL);
                }
              }));
      assertTrue(f.statementClosed);
      f.borrowed();
    }
  }

  @Test
  void sharedRepositoryParallelCallsKeepOwnRowsBindingsAndBody() throws Exception {
    var repository = new JdbcOutboxRepository(() -> 0);
    try (var pool = Executors.newFixedThreadPool(2)) {
      var jobs = new ArrayList<java.util.concurrent.Future<Long>>();
      for (int index = 0; index < 16; index++) {
        long id = index + 1;
        jobs.add(
            pool.submit(
                () -> {
                  var f = new Fixture();
                  f.rows.add(row(id, NOW));
                  var found = repository.claim(f.connection(), OWNER + id, NOW, 1).getFirst();
                  assertEquals(OWNER + id, f.parameters.get(4));
                  assertArrayEquals(body(), found.body());
                  assertTrue(f.resultClosed && f.statementClosed);
                  f.borrowed();
                  return found.id();
                }));
      }
      for (int index = 0; index < jobs.size(); index++) {
        assertEquals(index + 1L, jobs.get(index).get(10, TimeUnit.SECONDS));
      }
    }
  }
}
