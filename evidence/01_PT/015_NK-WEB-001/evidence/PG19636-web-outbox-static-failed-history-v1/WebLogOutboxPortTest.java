package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.DateTimeException;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** WLG-PORT-001..020; NK-MSG-002/UI235242/SS324331352: memory JDBC, no DB/crypto/dispatcher. */
final class WebLogOutboxPortTest {
  private static final Instant NOW = Instant.parse("2026-11-06T00:00:00.123456Z");
  private static final String WORKER = "port-worker";
  private static final String VERSION = "PUBLIC";
  private static final String AUTO = "getAutoCommit";
  private static final String PREPARE = "prepare";
  private static final String BIND = "bind";
  private static final String UPDATE = "executeUpdate";
  private static final String QUERY = "executeQuery";
  private static final String PS_CLOSE = "ps.close";
  private static final String RS_CLOSE = "rs.close";
  private static final String ID = "id";
  private static final String MESSAGE = "message_id";
  private static final String CORRELATION = "correlation_id";
  private static final String LAYOUT = "layout_id";
  private static final String LAYOUT_VERSION = "layout_version";
  private static final String CIPHER = "payload_ciphertext";
  private static final String KEY = "key_version";
  private static final String ATTEMPT = "attempt_count";
  private static final String DUE = "next_attempt_at";
  private static final String CREATED = "created_at";
  private static final String OWNER = "lease_owner";
  private static final String UNTIL = "lease_until";
  private static final String SAFE_ERROR = "PUBLIC_FAILURE";
  private static final String CLOSE_METHOD = "close";
  private static final String NEXT = "next";
  private static final String STORED_ERROR = "web log required database value is missing";
  private static final WebLogOutboxRepository REPO = new WebLogOutboxRepository(() -> 0);
  // Independent SS324/331 SQL and postconditions; never read a production constant or method.
  private static final String ENQUEUE_SQL =
      "insert into schubert_web_session.web_log_outbox "
          + "(message_id,correlation_id,layout_id,layout_version,payload_ciphertext,key_version,"
          + "status,attempt_count,next_attempt_at,created_at) "
          + "values(?,?,'WLGEVT01','001',?,?,'PENDING',0,?,?) "
          + "on conflict(message_id) do nothing";
  private static final String CLAIM_SQL =
      "with due as (select id from schubert_web_session.web_log_outbox "
          + "where status in ('PENDING','ERROR') and next_attempt_at<=? "
          + "and (lease_until is null or lease_until<?) order by next_attempt_at,id "
          + "for update skip locked limit ?) update schubert_web_session.web_log_outbox o "
          + "set lease_owner=?,lease_until=? from due where o.id=due.id "
          + "returning o.id,o.message_id,o.correlation_id,o.layout_id,o.layout_version,"
          + "o.payload_ciphertext,o.key_version,o.attempt_count,o.next_attempt_at,o.created_at,"
          + "o.lease_owner,o.lease_until";
  private static final String SENT_SQL =
      "update schubert_web_session.web_log_outbox set status='SENT',sent_at=?,"
          + "lease_owner=null,lease_until=null,last_error_code=null "
          + "where id=? and lease_owner=? and status in ('PENDING','ERROR')";
  private static final String FAILURE_SQL =
      "update schubert_web_session.web_log_outbox set status='ERROR',attempt_count=?,"
          + "next_attempt_at=?,sent_at=null,lease_owner=null,lease_until=null,last_error_code=? "
          + "where id=? and lease_owner=? and attempt_count=? and status in ('PENDING','ERROR')";

  @Test
  void port001SupplierNullIsRejected() {
    assertEquals(
        "jitterPermille",
        assertThrows(NullPointerException.class, () -> new WebLogOutboxRepository(null))
            .getMessage());
  }

  @Test
  void port002EnqueueFirstWriteAndDuplicateUseExactSqlBindings() throws Exception {
    for (int changed : new int[] {1, 0}) {
      var f = new Jdbc();
      f.updated = changed;
      assertEquals(changed == 1, REPO.enqueue(f.connection(), identity(7), payload(), NOW));
      assertEquals(ENQUEUE_SQL, f.sql);
      assertEquals(
          List.of("setObject", "setObject", "setBytes", "setString", "setObject", "setObject"),
          f.bindMethods);
      assertEquals(new UUID(0, 7), f.binds.get(1));
      assertEquals(new UUID(0, 8), f.binds.get(2));
      assertArrayEquals(new byte[29], (byte[]) f.binds.get(3));
      assertEquals(VERSION, f.binds.get(4));
      assertEquals(NOW.atOffset(ZoneOffset.UTC), f.binds.get(5));
      assertEquals(NOW.atOffset(ZoneOffset.UTC), f.binds.get(6));
      assertEquals(6, f.binds.size());
      assertEquals(List.of(AUTO, PREPARE, UPDATE, PS_CLOSE), f.operations);
    }
  }

  @Test
  void port003EnqueueRejectsEveryRequiredArgumentBeforeSql() {
    var f = new Jdbc();
    assertThrows(
        NullPointerException.class, () -> REPO.enqueue(f.connection(), null, payload(), NOW));
    assertThrows(
        NullPointerException.class, () -> REPO.enqueue(f.connection(), identity(1), null, NOW));
    assertThrows(
        NullPointerException.class,
        () -> REPO.enqueue(f.connection(), identity(1), payload(), null));
    assertEquals(List.of(AUTO, AUTO, AUTO), f.operations);
  }

  @Test
  void port004AllPublicOperationsRequireBorrowedExplicitTransaction() {
    for (int operation = 0; operation < 4; operation++) {
      int selected = operation;
      assertThrows(NullPointerException.class, () -> operate(null, selected));
      var f = new Jdbc();
      f.autoCommit = true;
      assertEquals(
          "web log outbox requires a caller-owned transaction",
          assertThrows(IllegalStateException.class, () -> operate(f.connection(), selected))
              .getMessage());
      assertEquals(List.of(AUTO), f.operations);
    }
  }

  @Test
  void port005ClaimEmptyAndLimitBoundsBindUtcAndTenSecondLease() throws Exception {
    for (int limit : new int[] {1, 100}) {
      var f = new Jdbc();
      assertEquals(List.of(), REPO.claim(f.connection(), WORKER, NOW, limit));
      assertEquals(CLAIM_SQL, f.sql);
      assertEquals(
          Map.of(
              1,
              NOW.atOffset(ZoneOffset.UTC),
              2,
              NOW.atOffset(ZoneOffset.UTC),
              3,
              limit,
              4,
              WORKER,
              5,
              Instant.parse("2026-11-06T00:00:10.123456Z").atOffset(ZoneOffset.UTC)),
          f.binds);
      assertEquals(
          List.of("setObject", "setObject", "setInt", "setString", "setObject"), f.bindMethods);
      assertEquals(List.of(AUTO, PREPARE, QUERY, NEXT, RS_CLOSE, PS_CLOSE), f.operations);
    }
  }

  @Test
  void port006ClaimSortsDueThenIdAndReturnsIndependentImmutableRows() throws Exception {
    var f = new Jdbc();
    var later = row(3);
    later.put(DUE, NOW.plusSeconds(1).atOffset(ZoneOffset.UTC));
    f.rows.add(later);
    f.rows.add(row(2));
    f.rows.add(row(1));
    var values = REPO.claim(f.connection(), WORKER, NOW, 100);
    assertEquals(List.of(1L, 2L, 3L), values.stream().map(ClaimedWebLog::id).toList());
    var first = values.getFirst();
    assertEquals(new UUID(0, 1), first.identity().messageId());
    assertEquals(new UUID(0, 2), first.identity().correlationId());
    assertEquals(VERSION, first.payload().keyVersion());
    assertArrayEquals(new byte[29], first.payload().ciphertext());
    assertEquals(0, first.attemptCount());
    assertEquals(NOW, first.nextAttemptAt());
    assertEquals(NOW.minusSeconds(3), first.createdAt());
    assertEquals(WORKER, first.leaseOwner());
    assertEquals(NOW.plusSeconds(10), first.leaseUntil());
    assertThrows(UnsupportedOperationException.class, () -> values.add(first));
    Arrays.fill((byte[]) f.rows.getLast().get(CIPHER), (byte) 9);
    assertArrayEquals(new byte[29], first.payload().ciphertext());
    assertEquals(
        List.of(RS_CLOSE, PS_CLOSE),
        f.operations.subList(f.operations.size() - 2, f.operations.size()));
  }

  @Test
  void port007ClaimRejectsInvalidWorkerLimitAndNullTime() {
    for (String worker : List.of("", "bad worker", "x".repeat(65))) {
      var f = new Jdbc();
      assertThrows(
          IllegalArgumentException.class, () -> REPO.claim(f.connection(), worker, NOW, 1));
      assertEquals(List.of(AUTO), f.operations);
    }
    for (int limit : new int[] {Integer.MIN_VALUE, 0, 101, Integer.MAX_VALUE}) {
      var f = new Jdbc();
      assertThrows(
          IllegalArgumentException.class, () -> REPO.claim(f.connection(), WORKER, NOW, limit));
      assertEquals(List.of(AUTO), f.operations);
    }
    var f = new Jdbc();
    assertThrows(NullPointerException.class, () -> REPO.claim(f.connection(), null, NOW, 1));
    assertThrows(NullPointerException.class, () -> REPO.claim(f.connection(), WORKER, null, 1));
    assertEquals(List.of(AUTO, AUTO), f.operations);
  }

  @Test
  void port008SentUsesOwnerStatusCasAndReportsUnchangedRows() throws Exception {
    for (int changed : new int[] {0, 1}) {
      var f = new Jdbc();
      f.updated = changed;
      assertEquals(changed == 1, REPO.markSent(f.connection(), claimed(0), NOW));
      assertEquals(SENT_SQL, f.sql);
      assertEquals(Map.of(1, NOW.atOffset(ZoneOffset.UTC), 2, 11L, 3, WORKER), f.binds);
      assertEquals(List.of("setObject", "setLong", "setString"), f.bindMethods);
      assertEquals(List.of(AUTO, PREPARE, UPDATE, PS_CLOSE), f.operations);
    }
  }

  @Test
  void port009SentRejectsNullRowAndTime() {
    var f = new Jdbc();
    assertThrows(NullPointerException.class, () -> REPO.markSent(f.connection(), null, NOW));
    assertThrows(NullPointerException.class, () -> REPO.markSent(f.connection(), claimed(0), null));
    assertEquals(List.of(AUTO, AUTO), f.operations);
  }

  @Test
  void port010FailureBackoffAndSaturatedAttemptUseIndependentVectors() throws Exception {
    int[] previous = {0, 1, 2, 3, 4, 99, 100};
    int[] next = {1, 2, 3, 4, 5, 100, 100};
    long[] delays = {1000, 5000, 30000, 60000, 300000, 300000, 300000};
    for (int index = 0; index < previous.length; index++) {
      for (int jitter : new int[] {-100, 0, 100}) {
        var f = new Jdbc();
        f.updated = index % 2;
        int old = previous[index];
        int count = next[index];
        long delay = delays[index];
        assertEquals(
            f.updated == 1,
            new WebLogOutboxRepository(() -> jitter)
                .markFailure(f.connection(), claimed(old), NOW, SAFE_ERROR));
        assertEquals(FAILURE_SQL, f.sql);
        assertEquals(
            Map.of(
                1,
                count,
                2,
                NOW.plusMillis(delay + delay * jitter / 1000).atOffset(ZoneOffset.UTC),
                3,
                SAFE_ERROR,
                4,
                11L,
                5,
                WORKER,
                6,
                old),
            f.binds);
        assertEquals(
            List.of("setInt", "setObject", "setString", "setLong", "setString", "setInt"),
            f.bindMethods);
        assertEquals(List.of(AUTO, PREPARE, UPDATE, PS_CLOSE), f.operations);
      }
    }
  }

  @Test
  void port011DefaultJitterStaysWithinIndependentTenPercentBounds() throws Exception {
    var f = new Jdbc();
    assertTrue(new WebLogOutboxRepository().markFailure(f.connection(), claimed(0), NOW, "X"));
    var due = (java.time.OffsetDateTime) f.binds.get(2);
    assertFalse(due.isBefore(NOW.plusMillis(900).atOffset(ZoneOffset.UTC)));
    assertFalse(due.isAfter(NOW.plusMillis(1100).atOffset(ZoneOffset.UTC)));
    assertEquals(1, f.binds.get(1));
  }

  @Test
  void port012FailureRejectsMissingOrUnboundedErrorCode() throws Exception {
    var f = new Jdbc();
    assertThrows(
        NullPointerException.class, () -> REPO.markFailure(f.connection(), null, NOW, SAFE_ERROR));
    assertThrows(
        NullPointerException.class,
        () -> REPO.markFailure(f.connection(), claimed(0), null, SAFE_ERROR));
    assertThrows(
        NullPointerException.class, () -> REPO.markFailure(f.connection(), claimed(0), NOW, null));
    for (String error : List.of("", "lower", "X".repeat(65), "BAD\nCODE", "é", "BAD CODE"))
      assertThrows(
          IllegalArgumentException.class,
          () -> REPO.markFailure(f.connection(), claimed(0), NOW, error));
    assertTrue(f.sql.isEmpty());
    assertTrue(REPO.markFailure(f.connection(), claimed(0), NOW, "X".repeat(64)));
    assertEquals("X".repeat(64), f.binds.get(3));
  }

  @Test
  void port013FailureRejectsOutOfRangeJitterBeforeSql() {
    for (int jitter : new int[] {-101, 101, Integer.MIN_VALUE, Integer.MAX_VALUE}) {
      var f = new Jdbc();
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new WebLogOutboxRepository(() -> jitter)
                  .markFailure(f.connection(), claimed(100), NOW, SAFE_ERROR));
      assertEquals(List.of(AUTO), f.operations);
    }
  }

  @Test
  void port014EveryMissingDatabaseFieldProducesFixedSqlDataFailure() {
    for (String field :
        List.of(ID, MESSAGE, CORRELATION, CIPHER, KEY, ATTEMPT, DUE, CREATED, OWNER, UNTIL)) {
      var f = new Jdbc();
      var data = row(1);
      data.put(field, null);
      f.rows.add(data);
      var error =
          assertThrows(SQLDataException.class, () -> REPO.claim(f.connection(), WORKER, NOW, 1));
      assertEquals(STORED_ERROR, error.getMessage());
      assertEquals("22004", error.getSQLState());
      assertNull(error.getCause());
      assertEquals(0, error.getSuppressed().length);
      assertEquals(
          List.of(RS_CLOSE, PS_CLOSE),
          f.operations.subList(f.operations.size() - 2, f.operations.size()));
    }
  }

  @Test
  void port015InvalidStoredLayoutOrVersionRejectsBeforeOtherFields() {
    for (String field : List.of(LAYOUT, LAYOUT_VERSION)) {
      for (String invalid : Arrays.asList(null, "", "OTHER")) {
        var f = new Jdbc();
        var data = row(1);
        data.put(field, invalid);
        f.rows.add(data);
        var error =
            assertThrows(SQLDataException.class, () -> REPO.claim(f.connection(), WORKER, NOW, 1));
        assertEquals("web log stored layout is invalid", error.getMessage());
        assertEquals("22000", error.getSQLState());
        assertNull(error.getCause());
        assertFalse(f.operations.contains("get:" + ID));
      }
    }
  }

  @Test
  void port016StoredConstructorInvariantsAreNotNormalizedAsSuccessfulRows() {
    Map<String, Object> invalid =
        Map.of(ID, 0L, ATTEMPT, 101, OWNER, "bad worker", CIPHER, new byte[28], KEY, "bad key");
    for (var value : invalid.entrySet()) {
      var f = new Jdbc();
      var data = row(1);
      data.put(value.getKey(), value.getValue());
      f.rows.add(data);
      assertThrows(
          IllegalArgumentException.class, () -> REPO.claim(f.connection(), WORKER, NOW, 1));
      assertEquals(
          List.of(RS_CLOSE, PS_CLOSE),
          f.operations.subList(f.operations.size() - 2, f.operations.size()));
    }
  }

  @Test
  void port017TimeOverflowAndSupplierFailureKeepIdentityAndResourceOwnership() {
    var f = new Jdbc();
    assertThrows(DateTimeException.class, () -> REPO.claim(f.connection(), WORKER, Instant.MAX, 1));
    assertEquals(List.of(AUTO, PREPARE, PS_CLOSE), f.operations);
    var other = new Jdbc();
    var error = new IllegalArgumentException("public supplier fixture");
    assertSame(
        error,
        assertThrows(
            IllegalArgumentException.class,
            () ->
                new WebLogOutboxRepository(
                        () -> {
                          throw error;
                        })
                    .markFailure(other.connection(), claimed(0), NOW, SAFE_ERROR)));
    assertEquals(List.of(AUTO), other.operations);
  }

  @Test
  void port018JdbcFailuresPropagateWithoutTransactionOrConnectionOwnership() {
    for (int operation = 0; operation < 4; operation++) {
      for (String phase : List.of(AUTO, PREPARE, BIND, operation == 1 ? QUERY : UPDATE, PS_CLOSE)) {
        var f = new Jdbc();
        var fault = new SQLException(SAFE_ERROR);
        f.faults.put(phase, fault);
        int selected = operation;
        assertSame(
            fault, assertThrows(SQLException.class, () -> operate(f.connection(), selected)));
        assertEquals(
            !phase.equals(AUTO) && !phase.equals(PREPARE), f.operations.contains(PS_CLOSE));
      }
    }
    for (String phase : List.of(NEXT, "get:" + KEY, RS_CLOSE)) {
      var f = new Jdbc();
      f.rows.add(row(1));
      var fault = new SQLException(SAFE_ERROR);
      f.faults.put(phase, fault);
      assertSame(
          fault,
          assertThrows(SQLException.class, () -> REPO.claim(f.connection(), WORKER, NOW, 1)));
      assertEquals(
          List.of(RS_CLOSE, PS_CLOSE),
          f.operations.subList(f.operations.size() - 2, f.operations.size()));
    }
  }

  @Test
  void port019BorrowedConnectionRemainsUntouchedOnSuppressedAndUnknownFailure() {
    var f = new Jdbc();
    f.rows.add(row(1));
    var first = new SQLException(SAFE_ERROR);
    var second = new SQLException("public close");
    f.faults.put(NEXT, first);
    f.faults.put(RS_CLOSE, second);
    assertSame(
        first, assertThrows(SQLException.class, () -> REPO.claim(f.connection(), WORKER, NOW, 1)));
    assertArrayEquals(new Throwable[] {second}, first.getSuppressed());
    assertEquals(
        List.of(RS_CLOSE, PS_CLOSE),
        f.operations.subList(f.operations.size() - 2, f.operations.size()));
    for (Throwable fault :
        List.of(new IllegalStateException(SAFE_ERROR), new AssertionError(SAFE_ERROR))) {
      var other = new Jdbc();
      other.rows.add(row(1));
      other.faults.put(NEXT, fault);
      assertSame(
          fault,
          assertThrows(fault.getClass(), () -> REPO.claim(other.connection(), WORKER, NOW, 1)));
      assertEquals(
          List.of(RS_CLOSE, PS_CLOSE),
          other.operations.subList(other.operations.size() - 2, other.operations.size()));
    }
  }

  @Test
  void port020SharedRepositoryHasIndependentConcurrentJdbcState() throws Exception {
    try (var workers = Executors.newFixedThreadPool(2)) {
      var first = workers.submit(() -> readWorker(1));
      var second = workers.submit(() -> readWorker(2));
      var a = first.get(5, TimeUnit.SECONDS);
      var b = second.get(5, TimeUnit.SECONDS);
      assertEquals(1L, a.id());
      assertEquals(2L, b.id());
      assertEquals(new UUID(0, 1), a.identity().messageId());
      assertEquals(new UUID(0, 2), b.identity().messageId());
    }
  }

  private static ClaimedWebLog readWorker(long id) throws SQLException {
    var f = new Jdbc();
    f.rows.add(row(id));
    var values = REPO.claim(f.connection(), WORKER, NOW, 1);
    assertEquals(
        List.of(RS_CLOSE, PS_CLOSE),
        f.operations.subList(f.operations.size() - 2, f.operations.size()));
    return values.getFirst();
  }

  private static void operate(@Nullable Connection connection, int operation) throws SQLException {
    switch (operation) {
      case 0 -> REPO.enqueue(connection, identity(1), payload(), NOW);
      case 1 -> REPO.claim(connection, WORKER, NOW, 1);
      case 2 -> REPO.markSent(connection, claimed(0), NOW);
      case 3 -> REPO.markFailure(connection, claimed(0), NOW, SAFE_ERROR);
      default -> throw new AssertionError("unknown fixture operation");
    }
  }

  private static WebLogPayloadIdentity identity(long id) {
    return new WebLogPayloadIdentity(new UUID(0, id), new UUID(0, id + 1));
  }

  private static EncryptedWebLogPayload payload() {
    return new EncryptedWebLogPayload(VERSION, new byte[29]);
  }

  private static ClaimedWebLog claimed(int attempt) {
    return new ClaimedWebLog(
        11, identity(1), payload(), attempt, NOW, NOW.minusSeconds(3), WORKER, NOW.plusSeconds(10));
  }

  private static Map<String, Object> row(long id) {
    var values = new LinkedHashMap<String, Object>();
    values.put(ID, id);
    values.put(MESSAGE, new UUID(0, id));
    values.put(CORRELATION, new UUID(0, id + 1));
    values.put(LAYOUT, "WLGEVT01");
    values.put(LAYOUT_VERSION, "001");
    values.put(CIPHER, new byte[29]);
    values.put(KEY, VERSION);
    values.put(ATTEMPT, 0);
    values.put(DUE, NOW.atOffset(ZoneOffset.UTC));
    values.put(CREATED, NOW.minusSeconds(3).atOffset(ZoneOffset.UTC));
    values.put(OWNER, WORKER);
    values.put(UNTIL, NOW.plusSeconds(10).atOffset(ZoneOffset.UTC));
    return values;
  }

  @FunctionalInterface
  private interface Call {
    @Nullable Object apply(String name, Object[] args) throws Throwable;
  }

  private static <T> T proxy(Class<T> type, Call call) {
    return type.cast(
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (target, method, args) ->
                call.apply(method.getName(), args == null ? new Object[0] : args)));
  }

  private static final class Jdbc {
    final Map<Integer, Object> binds = new LinkedHashMap<>();
    final List<String> bindMethods = new ArrayList<>();
    final List<String> operations = new ArrayList<>();
    final List<Map<String, Object>> rows = new ArrayList<>();
    final Map<String, Throwable> faults = new HashMap<>();
    String sql = "";
    boolean autoCommit;
    int updated = 1;
    int cursor = -1;

    private void fail(String phase) throws Throwable {
      var fault = faults.get(phase);
      if (fault != null) throw fault;
    }

    private Connection connection() {
      return proxy(
          Connection.class,
          (name, args) -> {
            if (name.equals(AUTO)) {
              operations.add(AUTO);
              fail(AUTO);
              return autoCommit;
            }
            if (name.equals("prepareStatement")) {
              operations.add(PREPARE);
              fail(PREPARE);
              sql = (String) args[0];
              return statement();
            }
            throw new AssertionError("borrowed connection method forbidden: " + name);
          });
    }

    private PreparedStatement statement() {
      return proxy(
          PreparedStatement.class,
          (name, args) -> {
            if (name.startsWith("set")) {
              fail(BIND);
              bindMethods.add(name);
              binds.put((int) args[0], args[1]);
              return null;
            }
            if (name.equals(UPDATE)) {
              operations.add(UPDATE);
              fail(UPDATE);
              return updated;
            }
            if (name.equals(QUERY)) {
              operations.add(QUERY);
              fail(QUERY);
              return result();
            }
            if (name.equals(CLOSE_METHOD)) {
              operations.add(PS_CLOSE);
              fail(PS_CLOSE);
              return null;
            }
            throw new AssertionError("unexpected statement method " + name);
          });
    }

    private ResultSet result() {
      return proxy(
          ResultSet.class,
          (name, args) -> {
            if (name.equals(NEXT)) {
              operations.add(NEXT);
              fail(NEXT);
              cursor++;
              return cursor < rows.size();
            }
            if (name.equals("getObject") || name.equals("getString") || name.equals("getBytes")) {
              operations.add("get:" + args[0]);
              fail("get:" + args[0]);
              return rows.get(cursor).get((String) args[0]);
            }
            if (name.equals(CLOSE_METHOD)) {
              operations.add(RS_CLOSE);
              fail(RS_CLOSE);
              return null;
            }
            throw new AssertionError("unexpected result method " + name);
          });
    }
  }
}
