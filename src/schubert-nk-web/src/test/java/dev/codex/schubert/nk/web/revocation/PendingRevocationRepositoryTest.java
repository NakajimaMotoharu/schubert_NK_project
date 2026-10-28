package dev.codex.schubert.nk.web.revocation;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.DateTimeException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** RERUN004/QA050: isolated PG, independent literal SQL/time/lease oracle, no remote calls. */
final class PendingRevocationRepositoryTest {
  private static final String FIXTURE_TEST_4D967A30 = "test";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  private static final Instant NOW = Instant.parse("2026-09-08T00:00:00.123456Z");
  private static final EncryptedRevocationPayload PAYLOAD =
      new EncryptedRevocationPayload(FIXTURE_TEST_4D967A30, new byte[101]);
  private static final UUID OWNER = new UUID(0, 101);
  private static final UUID SECOND = new UUID(0, 102);
  private static final PendingRevocationRepository REPO = new PendingRevocationRepository();
  private static WebLogDatabaseFixture db;

  @BeforeAll
  static void start(@TempDir Path root) throws Exception {
    db = new WebLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = db.web();
        var s = c.createStatement()) {
      s.executeUpdate("delete from schubert_web_session.pending_context_revocations");
    }
  }

  @Test
  void rerun004aEnqueueRollbackAndLiteralRetainedNull() throws Exception {
    try (var c = db.transaction()) {
      REPO.enqueue(c, identity(1), PAYLOAD, null, RevocationFailureCode.UNAVAILABLE);
      assertEquals(0, count());
      c.rollback();
    }
    assertEquals(0, count());
    enqueue(1, null);
    try (var c = db.web();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select id,context_ciphertext,key_version,requested_at,attempt_count,next_attempt_at,expires_at,last_error_code,lease_owner,lease_until from schubert_web_session.pending_context_revocations")) {
      assertTrue(r.next());
      assertEquals(new UUID(0, 1), r.getObject(1, UUID.class));
      assertArrayEquals(new byte[101], r.getBytes(2));
      assertEquals(FIXTURE_TEST_4D967A30, r.getString(3));
      assertEquals(
          OffsetDateTime.parse("2026-09-08T00:00:00.123456Z"),
          r.getObject(4, OffsetDateTime.class));
      assertEquals(0, r.getInt(5));
      assertEquals(
          OffsetDateTime.parse("2026-09-08T00:00:05.123456Z"),
          r.getObject(6, OffsetDateTime.class));
      assertNull(r.getObject(7));
      assertEquals("UNAVAILABLE", r.getString(8));
      assertNull(r.getObject(9));
      assertNull(r.getObject(10));
      assertFalse(r.next());
    }
    try (var c = db.transaction()) {
      assertThrows(
          SQLException.class,
          () -> REPO.enqueue(c, identity(1), PAYLOAD, null, RevocationFailureCode.API_REJECTED));
      c.rollback();
    }
    assertEquals(1, count());
  }

  @Test
  void rerun004bDueSkipLocksAndLimitOneHundredIgnoreExpiry() throws Exception {
    enqueue(2, NOW.plusSeconds(1));
    enqueue(1, null);
    Instant due = NOW.plusSeconds(5);
    try (var c = db.transaction()) {
      assertTrue(REPO.claim(c, OWNER, due.minusNanos(1000), due.plusSeconds(10), 100).isEmpty());
      c.commit();
    }
    try (var first = db.transaction();
        var second = db.transaction()) {
      var rows = REPO.claim(first, OWNER, due, due.plusSeconds(10), 100);
      assertEquals(
          List.of(new UUID(0, 1), new UUID(0, 2)),
          rows.stream().map(row -> row.identity().id()).toList());
      assertTrue(REPO.claim(second, SECOND, due, due.plusSeconds(10), 100).isEmpty());
      assertThrows(UnsupportedOperationException.class, rows::clear);
      var row = rows.getFirst();
      assertEquals(identity(1), row.identity());
      assertArrayEquals(new byte[101], row.payload().ciphertext());
      assertEquals(FIXTURE_TEST_4D967A30, row.payload().keyVersion());
      assertEquals(0, row.attemptCount());
      assertNull(row.expiresAt());
      assertEquals(OWNER, row.leaseOwner());
      assertEquals(FIXTURE_TEST_4D967A30, row.keyVersion());
      assertEquals(due.plusSeconds(10), row.leaseUntil());
      assertEquals("ClaimedRevocation[REDACTED]", row.toString());
      assertEquals(NOW.plusSeconds(1), rows.get(1).expiresAt());
      first.commit();
      second.commit();
    }
    try (var c = db.transaction()) {
      assertTrue(
          REPO.claim(c, SECOND, due.plusSeconds(10).minusNanos(1000), due.plusSeconds(20), 100)
              .isEmpty());
      var rows = REPO.claim(c, SECOND, due.plusSeconds(10), due.plusSeconds(20), 100);
      assertEquals(2, rows.size());
      assertEquals(SECOND, rows.getFirst().leaseOwner());
      c.rollback();
    }
    reset();
    for (int i = 1; i <= 101; i++) enqueue(i, null);
    try (var a = db.transaction();
        var b = db.transaction()) {
      var hundred = REPO.claim(a, OWNER, due, due.plusSeconds(10), 100);
      assertEquals(100, hundred.size());
      assertEquals(new UUID(0, 1), hundred.getFirst().identity().id());
      var last = REPO.claim(b, SECOND, due, due.plusSeconds(10), 100);
      assertEquals(
          List.of(new UUID(0, 101)), last.stream().map(row -> row.identity().id()).toList());
      a.rollback();
      b.rollback();
    }
  }

  @Test
  void rerun004cIndependentBackoffSaturationAndAllClosedWarnings() throws Exception {
    enqueue(1, null);
    Instant at = NOW.plusSeconds(5);
    int attempt = 0;
    for (long delay : new long[] {30, 300, 900, 900}) {
      ClaimedRevocation row;
      try (var c = db.transaction()) {
        row = REPO.claim(c, UUID.randomUUID(), at, at.plusSeconds(10), 1).getFirst();
        c.commit();
      }
      try (var c = db.transaction()) {
        assertTrue(REPO.markFailure(c, row, at, RevocationFailureCode.SESSION_INVALID));
        c.commit();
      }
      assertState(++attempt, at.plusSeconds(delay), "SESSION_INVALID");
      try (var c = db.transaction()) {
        assertTrue(
            REPO.claim(
                    c,
                    SECOND,
                    at.plusSeconds(delay).minusNanos(1000),
                    at.plusSeconds(delay + 10),
                    1)
                .isEmpty());
        c.rollback();
      }
      at = at.plusSeconds(delay);
    }
    sql("update schubert_web_session.pending_context_revocations set attempt_count=100");
    for (var code : RevocationFailureCode.values()) {
      ClaimedRevocation row;
      try (var c = db.transaction()) {
        row = REPO.claim(c, UUID.randomUUID(), at, at.plusSeconds(10), 1).getFirst();
        c.commit();
      }
      try (var c = db.transaction()) {
        assertTrue(REPO.markFailure(c, row, at, code));
        c.commit();
      }
      assertState(100, at.plusSeconds(900), code.name());
      at = at.plusSeconds(900);
    }
    assertEquals(1, count());
  }

  @Test
  void rerun004dSelfLeaseCasRollbackAndExpiredOwnerNeverDeletes() throws Exception {
    enqueue(1, null);
    Instant at = NOW.plusSeconds(5);
    Instant until = at.plusSeconds(10);
    ClaimedRevocation old;
    try (var c = db.transaction()) {
      old = REPO.claim(c, OWNER, at, until, 1).getFirst();
      c.commit();
    }
    try (var c = db.transaction()) {
      assertFalse(REPO.removeConfirmed(c, old, until));
      assertFalse(REPO.markFailure(c, old, until, RevocationFailureCode.UNAVAILABLE));
      c.commit();
    }
    ClaimedRevocation current;
    try (var c = db.transaction()) {
      current = REPO.claim(c, SECOND, until, until.plusSeconds(10), 1).getFirst();
      c.commit();
    }
    try (var c = db.transaction()) {
      assertFalse(REPO.removeConfirmed(c, old, until));
      assertFalse(REPO.markFailure(c, old, until, RevocationFailureCode.API_REJECTED));
      assertTrue(REPO.removeConfirmed(c, current, until));
      c.rollback();
    }
    assertEquals(1, count());
    try (var c = db.transaction()) {
      assertTrue(REPO.removeConfirmed(c, current, until.plusSeconds(10).minusNanos(1000)));
      c.commit();
    }
    assertEquals(0, count());
  }

  @Test
  void rerun004eNullBoundsExplicitTransactionAndReadContracts() throws Exception {
    var row =
        new ClaimedRevocation(
            identity(1),
            PAYLOAD,
            100,
            NOW.plusSeconds(1),
            OWNER,
            NOW.plusSeconds(10),
            FIXTURE_TEST_4D967A30);
    try (var c = db.transaction()) {
      assertThrows(
          NullPointerException.class,
          () -> REPO.enqueue(null, identity(1), PAYLOAD, null, RevocationFailureCode.UNAVAILABLE));
      assertThrows(
          NullPointerException.class,
          () -> REPO.enqueue(c, null, PAYLOAD, null, RevocationFailureCode.UNAVAILABLE));
      assertThrows(
          NullPointerException.class,
          () -> REPO.enqueue(c, identity(1), null, null, RevocationFailureCode.UNAVAILABLE));
      assertThrows(
          NullPointerException.class, () -> REPO.enqueue(c, identity(1), PAYLOAD, null, null));
      assertThrows(
          NullPointerException.class, () -> REPO.claim(c, null, NOW, NOW.plusSeconds(10), 1));
      assertThrows(
          NullPointerException.class, () -> REPO.claim(c, OWNER, null, NOW.plusSeconds(10), 1));
      assertThrows(NullPointerException.class, () -> REPO.claim(c, OWNER, NOW, null, 1));
      for (int limit : new int[] {0, 101})
        assertThrows(
            IllegalArgumentException.class,
            () -> REPO.claim(c, OWNER, NOW, NOW.plusSeconds(10), limit));
      assertThrows(IllegalArgumentException.class, () -> REPO.claim(c, OWNER, NOW, NOW, 1));
      assertThrows(
          IllegalArgumentException.class,
          () -> REPO.claim(c, OWNER, NOW.plusNanos(1), NOW.plusSeconds(10), 1));
      assertThrows(
          IllegalArgumentException.class,
          () -> REPO.claim(c, OWNER, NOW, NOW.plusSeconds(10).plusNanos(1), 1));
      for (Instant expiry : List.of(NOW.minusSeconds(1), NOW, NOW.plusNanos(1)))
        assertThrows(
            IllegalArgumentException.class,
            () -> REPO.enqueue(c, identity(1), PAYLOAD, expiry, RevocationFailureCode.UNAVAILABLE));
      assertThrows(
          NullPointerException.class,
          () -> REPO.markFailure(c, null, NOW, RevocationFailureCode.UNAVAILABLE));
      assertThrows(
          NullPointerException.class,
          () -> REPO.markFailure(c, row, null, RevocationFailureCode.UNAVAILABLE));
      assertThrows(NullPointerException.class, () -> REPO.markFailure(c, row, NOW, null));
      assertThrows(
          IllegalArgumentException.class,
          () -> REPO.markFailure(c, row, NOW.minusNanos(1000), RevocationFailureCode.UNAVAILABLE));
      assertThrows(NullPointerException.class, () -> REPO.removeConfirmed(c, null, NOW));
      assertThrows(NullPointerException.class, () -> REPO.removeConfirmed(c, row, null));
      c.rollback();
    }
    try (var c = db.web()) {
      assertThrows(
          IllegalStateException.class,
          () -> REPO.enqueue(c, identity(1), PAYLOAD, null, RevocationFailureCode.UNAVAILABLE));
      assertThrows(
          IllegalStateException.class, () -> REPO.claim(c, OWNER, NOW, NOW.plusSeconds(10), 1));
      assertThrows(
          IllegalStateException.class,
          () -> REPO.markFailure(c, row, NOW, RevocationFailureCode.UNAVAILABLE));
      assertThrows(IllegalStateException.class, () -> REPO.removeConfirmed(c, row, NOW));
    }
    assertThrows(
        NullPointerException.class,
        () ->
            new ClaimedRevocation(
                null, PAYLOAD, 0, null, OWNER, NOW.plusSeconds(10), FIXTURE_TEST_4D967A30));
    assertThrows(
        NullPointerException.class,
        () ->
            new ClaimedRevocation(
                identity(1), PAYLOAD, 0, null, null, NOW.plusSeconds(10), FIXTURE_TEST_4D967A30));
    assertThrows(
        NullPointerException.class,
        () ->
            new ClaimedRevocation(
                identity(1), PAYLOAD, 0, null, OWNER, null, FIXTURE_TEST_4D967A30));
    for (int count : new int[] {-1, 101})
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new ClaimedRevocation(
                  identity(1),
                  PAYLOAD,
                  count,
                  null,
                  OWNER,
                  NOW.plusSeconds(10),
                  FIXTURE_TEST_4D967A30));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ClaimedRevocation(
                identity(1), PAYLOAD, 0, null, OWNER, NOW, FIXTURE_TEST_4D967A30));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ClaimedRevocation(
                identity(1), PAYLOAD, 0, NOW, OWNER, NOW.plusSeconds(10), FIXTURE_TEST_4D967A30));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ClaimedRevocation(
                identity(1),
                PAYLOAD,
                0,
                NOW.plusNanos(1),
                OWNER,
                NOW.plusSeconds(10),
                FIXTURE_TEST_4D967A30));
    assertThrows(
        NullPointerException.class,
        () -> new ClaimedRevocation(identity(1), null, 0, null, OWNER, NOW.plusSeconds(10), null));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ClaimedRevocation(
                identity(1), PAYLOAD, 0, null, OWNER, NOW.plusSeconds(10), "other"));
  }

  @Test
  void rerun004fOversizedCorruptCipherIsClaimedForRetainedWarningNotWholeQueuePoison()
      throws Exception {
    enqueue(1, null);
    enqueue(2, null);
    sql(
        "update schubert_web_session.pending_context_revocations set context_ciphertext=decode(repeat('00',117),'hex') where id='00000000-0000-0000-0000-000000000001'");
    try (var c = db.transaction()) {
      var rows = REPO.claim(c, OWNER, NOW.plusSeconds(5), NOW.plusSeconds(15), 100);
      assertEquals(2, rows.size());
      assertNull(rows.getFirst().payload());
      assertEquals(FIXTURE_TEST_4D967A30, rows.getFirst().keyVersion());
      assertNotNull(rows.get(1).payload());
      assertTrue(
          REPO.markFailure(
              c, rows.getFirst(), NOW.plusSeconds(5), RevocationFailureCode.PAYLOAD_INVALID));
      c.commit();
    }
    assertEquals(2, count());
    try (var c = db.web();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select octet_length(context_ciphertext),last_error_code from schubert_web_session.pending_context_revocations where id='00000000-0000-0000-0000-000000000001'")) {
      assertTrue(r.next());
      assertEquals(117, r.getInt(1));
      assertEquals("PAYLOAD_INVALID", r.getString(2));
    }
  }

  @Test
  void rerun004gRequiredSqlNullMalformedAndResourceFaultsRollback() throws Exception {
    enqueue(1, null);
    for (String column :
        List.of(
            "id",
            "requested_at",
            "key_version",
            "context_ciphertext",
            "attempt_count",
            "lease_owner",
            "lease_until",
            "ciphertext_length")) {
      try (var c = db.transaction()) {
        var error =
            assertThrows(
                SQLDataException.class,
                () ->
                    REPO.claim(
                        fault(c, column, null, null),
                        OWNER,
                        NOW.plusSeconds(5),
                        NOW.plusSeconds(15),
                        1));
        assertEquals("22000", error.getSQLState());
        c.rollback();
      }
    }
    for (Object malformed :
        List.of(
            "not-a-uuid",
            "00000000-0000-0000-0000-0000000000AF",
            -1,
            new DateTimeException("private-time-marker"))) {
      String column =
          malformed instanceof Integer
              ? "attempt_count"
              : malformed instanceof DateTimeException ? "requested_at" : "lease_owner";
      try (var c = db.transaction()) {
        assertThrows(
            SQLDataException.class,
            () ->
                REPO.claim(
                    fault(c, column, malformed, null),
                    OWNER,
                    NOW.plusSeconds(5),
                    NOW.plusSeconds(15),
                    1));
        c.rollback();
      }
    }
    for (String kind :
        List.of("statement-null", "result-null", "execute", "next", FIXTURE_CLOSE_97959247)) {
      try (var c = db.transaction()) {
        assertThrows(
            SQLException.class,
            () ->
                REPO.claim(
                    fault(c, kind, null, null), OWNER, NOW.plusSeconds(5), NOW.plusSeconds(15), 1));
        c.rollback();
      }
    }
    var fatal = new AssertionError("private-fatal-marker");
    try (var c = db.transaction()) {
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () ->
                  REPO.claim(
                      fault(c, FIXTURE_CLOSE_97959247, null, fatal),
                      OWNER,
                      NOW.plusSeconds(5),
                      NOW.plusSeconds(15),
                      1)));
      c.rollback();
    }
    try (var c = db.transaction()) {
      assertThrows(
          SQLDataException.class,
          () ->
              REPO.enqueue(
                  fault(c, "update-zero", null, null),
                  identity(2),
                  PAYLOAD,
                  null,
                  RevocationFailureCode.UNAVAILABLE));
      c.rollback();
    }
    assertEquals(1, count());
    try (var c = db.web();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select lease_owner,lease_until from schubert_web_session.pending_context_revocations")) {
      assertTrue(r.next());
      assertNull(r.getString(1));
      assertNull(r.getObject(2));
    }
  }

  @Test
  void rerun004hCipherProjectionBoundsDistinguishOversizedFromMissingOrInconsistent()
      throws Exception {
    for (int size : new int[] {29, 116, 117, 16384}) {
      reset();
      enqueue(1, null);
      sql(
          "update schubert_web_session.pending_context_revocations set context_ciphertext=decode(repeat('00',"
              + size
              + "),'hex')");
      try (var c = db.transaction()) {
        var row = REPO.claim(c, OWNER, NOW.plusSeconds(5), NOW.plusSeconds(15), 1).getFirst();
        assertEquals(FIXTURE_TEST_4D967A30, row.keyVersion());
        if (size <= 116) assertArrayEquals(new byte[size], row.payload().ciphertext());
        else assertNull(row.payload());
        assertTrue(
            REPO.markFailure(c, row, NOW.plusSeconds(5), RevocationFailureCode.PAYLOAD_INVALID));
        c.commit();
      }
      assertEquals(1, count());
    }
    reset();
    enqueue(1, null);
    for (int size : new int[] {-1, 0, 28, 100}) {
      try (var c = db.transaction()) {
        assertThrows(
            SQLDataException.class,
            () ->
                REPO.claim(
                    fault(c, "ciphertext_length", size, null),
                    OWNER,
                    NOW.plusSeconds(5),
                    NOW.plusSeconds(15),
                    1));
        c.rollback();
      }
    }
    try (var c = db.transaction()) {
      assertThrows(
          SQLDataException.class,
          () ->
              REPO.claim(
                  fault(c, "key_version", "!", null),
                  OWNER,
                  NOW.plusSeconds(5),
                  NOW.plusSeconds(15),
                  1));
      c.rollback();
    }
  }

  @Test
  void rerun004iAllFourStatementOwnersFailClosedAndCallerRollbackRestoresRows() throws Exception {
    enqueue(1, null);
    ClaimedRevocation row;
    try (var c = db.transaction()) {
      row = REPO.claim(c, OWNER, NOW.plusSeconds(5), NOW.plusSeconds(15), 1).getFirst();
      c.commit();
    }
    for (int operation = 0; operation < 4; operation++) {
      int selected = operation;
      for (String kind : List.of("statement-null", "prepare", "statement-close", "execute-any")) {
        try (var c = db.transaction()) {
          Connection proxy = fault(c, kind, null, null);
          assertThrows(SQLException.class, () -> invokeOperation(selected, proxy, row));
          c.rollback();
        }
        assertEquals(1, count());
      }
      var fatal = new AssertionError("private-statement-close-marker");
      try (var c = db.transaction()) {
        assertSame(
            fatal,
            assertThrows(
                AssertionError.class,
                () -> invokeOperation(selected, fault(c, "statement-close", null, fatal), row)));
        c.rollback();
      }
      assertEquals(1, count());
    }
  }

  private static void invokeOperation(int selected, Connection connection, ClaimedRevocation row)
      throws SQLException {
    switch (selected) {
      case 0 ->
          REPO.enqueue(connection, identity(2), PAYLOAD, null, RevocationFailureCode.UNAVAILABLE);
      case 1 -> REPO.claim(connection, SECOND, NOW.plusSeconds(15), NOW.plusSeconds(25), 1);
      case 2 ->
          REPO.markFailure(connection, row, NOW.plusSeconds(5), RevocationFailureCode.UNAVAILABLE);
      case 3 -> REPO.removeConfirmed(connection, row, NOW.plusSeconds(5));
      default -> throw new AssertionError("invalid independent operation index");
    }
  }

  private static RevocationPayloadIdentity identity(int id) {
    return new RevocationPayloadIdentity(new UUID(0, id), NOW);
  }

  private static void enqueue(int id, Instant expiry) throws Exception {
    try (var c = db.transaction()) {
      REPO.enqueue(c, identity(id), PAYLOAD, expiry, RevocationFailureCode.UNAVAILABLE);
      c.commit();
    }
  }

  private static int count() throws Exception {
    try (var c = db.web();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select count(*) from schubert_web_session.pending_context_revocations")) {
      assertTrue(r.next());
      return r.getInt(1);
    }
  }

  private static void sql(String sql) throws Exception {
    try (var c = db.web();
        var s = c.createStatement()) {
      s.executeUpdate(sql);
    }
  }

  private static void assertState(int attempt, Instant due, String code) throws Exception {
    try (var c = db.web();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select attempt_count,next_attempt_at,expires_at,last_error_code,lease_owner,lease_until from schubert_web_session.pending_context_revocations")) {
      assertTrue(r.next());
      assertEquals(attempt, r.getInt(1));
      assertEquals(due, r.getObject(2, OffsetDateTime.class).toInstant());
      assertNull(r.getObject(3));
      assertEquals(code, r.getString(4));
      assertNull(r.getObject(5));
      assertNull(r.getObject(6));
    }
  }

  private static Connection fault(Connection c, String kind, Object replacement, Error fatal) {
    return wrap(
        Connection.class,
        c,
        (method, args) -> {
          if (!method.getName().equals("prepareStatement")) return invoke(c, method, args);
          if (kind.equals("statement-null")) return null;
          if (kind.equals("prepare")) throw new SQLException("private-prepare-marker");
          PreparedStatement s = (PreparedStatement) invoke(c, method, args);
          return wrap(
              PreparedStatement.class,
              s,
              (call, values) -> {
                if (call.getName().equals(FIXTURE_CLOSE_97959247)
                    && kind.equals("statement-close")) {
                  s.close();
                  if (fatal != null) throw fatal;
                  throw new SQLException("private-statement-close-marker");
                }
                if (List.of("executeQuery", "executeUpdate").contains(call.getName())
                    && kind.equals("execute-any")) throw new SQLException("private-execute-marker");
                if (call.getName().equals("executeUpdate") && kind.equals("update-zero")) return 0;
                if (!call.getName().equals("executeQuery")) return invoke(s, call, values);
                if (kind.equals("execute")) throw new SQLException("private-provider-marker");
                if (kind.equals("result-null")) return null;
                ResultSet r = (ResultSet) invoke(s, call, values);
                return wrap(
                    ResultSet.class,
                    r,
                    (get, columns) -> {
                      if (get.getName().equals("next") && kind.equals("next"))
                        throw new SQLException("private-provider-marker");
                      if (get.getName().equals(FIXTURE_CLOSE_97959247)
                          && kind.equals(FIXTURE_CLOSE_97959247)) {
                        r.close();
                        if (fatal != null) throw fatal;
                        throw new SQLException("private-close-marker");
                      }
                      if (List.of("getObject", "getString", "getBytes").contains(get.getName())
                          && columns[0].equals(kind)) {
                        if (replacement instanceof DateTimeException error) throw error;
                        return replacement;
                      }
                      return invoke(r, get, columns);
                    });
              });
        });
  }

  @FunctionalInterface
  interface Call {
    Object run(Method method, Object[] args) throws Throwable;
  }

  private static <T> T wrap(Class<T> type, T target, Call call) {
    return type.cast(
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (proxy, method, args) -> call.run(method, args)));
  }

  private static Object invoke(Object target, Method method, Object[] args) throws Throwable {
    try {
      return method.invoke(target, args);
    } catch (InvocationTargetException error) {
      throw error.getCause();
    }
  }
}
