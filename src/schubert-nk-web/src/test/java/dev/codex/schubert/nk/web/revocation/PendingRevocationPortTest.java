package dev.codex.schubert.nk.web.revocation;

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
import java.time.OffsetDateTime;
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
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** OPS-RVR-PORT-001..016; QA050/SSC171/SS314331332: borrowed memory JDBC, no DB/keys/JMS. */
final class PendingRevocationPortTest {
  private static final String DATA_STATE = "22000";
  private static final String JDBC_CLOSE = "close";
  private static final int MAXIMUM_TEST_CIPHERTEXT = 116;
  private static final PendingRevocationRepository REPO = new PendingRevocationRepository();
  private static final Instant REQUESTED = Instant.parse("2026-11-05T00:00:00.123456Z");
  private static final Instant NOW = Instant.parse("2026-11-05T00:00:10.123456Z");
  private static final Instant UNTIL = Instant.parse("2026-11-05T00:00:20.123456Z");
  private static final UUID OWNER = UUID.fromString("00000000-0000-0000-0000-0000000000af");
  private static final String VERSION = "pt-synthetic";
  private static final String ID = "id";
  private static final String CIPHER = "context_ciphertext";
  private static final String SIZE = "ciphertext_length";
  private static final String KEY = "key_version";
  private static final String REQUESTED_AT = "requested_at";
  private static final String ATTEMPTS = "attempt_count";
  private static final String EXPIRY = "expires_at";
  private static final String LEASE_OWNER = "lease_owner";
  private static final String LEASE_UNTIL = "lease_until";
  private static final String PS_CLOSE = "ps.close";
  private static final String RS_CLOSE = "rs.close";
  private static final String PREPARE = "prepare";
  private static final String EXECUTE_QUERY = "executeQuery";
  private static final String EXECUTE_UPDATE = "executeUpdate";
  private static final String PUBLIC_FAULT = "public fixture";
  // Independently authored DDL/QA050 SQL contract, never extracted from production fields.
  private static final String ENQUEUE_SQL =
      "insert into schubert_web_session.pending_context_revocations"
          + " (id,context_ciphertext,key_version,requested_at,attempt_count,next_attempt_at,expires_at,last_error_code)"
          + " values(?,?,?,?,0,?,?,?)";
  private static final String CLAIM_SQL =
      "with due as (select id from schubert_web_session.pending_context_revocations where"
          + " next_attempt_at<=? and (lease_until is null or lease_until<=?) order by"
          + " next_attempt_at,requested_at,id for update skip locked limit ?) update"
          + " schubert_web_session.pending_context_revocations p set lease_owner=?,lease_until=?"
          + " from due where p.id=due.id returning p.id,octet_length(p.context_ciphertext) as"
          + " ciphertext_length,case when octet_length(p.context_ciphertext)<=116 then"
          + " p.context_ciphertext else null end as context_ciphertext,"
          + "p.key_version,p.requested_at,p.attempt_count,p.expires_at,p.lease_owner,p.lease_until";
  private static final String FAILURE_SQL =
      "update schubert_web_session.pending_context_revocations set"
          + " attempt_count=?,next_attempt_at=?,last_error_code=?,lease_owner=null,lease_until=null"
          + " where id=? and lease_owner=? and lease_until=? and attempt_count=? and lease_until>?";
  private static final String DELETE_SQL =
      "delete from schubert_web_session.pending_context_revocations "
          + "where id=? and lease_owner=? and lease_until=? and attempt_count=? and lease_until>?";

  @Test
  void enqueueBindsIndependentFiveSecondScheduleAndBothExpiryForms() throws Exception {
    for (Instant expiry : Arrays.asList(null, REQUESTED.plusSeconds(3600))) {
      Fixture f = new Fixture();
      var identity = identity(1);
      var payload = new EncryptedRevocationPayload(VERSION, new byte[101]);
      REPO.enqueue(f.connection, identity, payload, expiry, RevocationFailureCode.UNAVAILABLE);
      assertEquals(ENQUEUE_SQL, normalized(f.sql));
      assertEquals(new UUID(0, 1), f.bindings.get(1));
      assertArrayEquals(new byte[101], (byte[]) f.bindings.get(2));
      assertEquals(VERSION, f.bindings.get(3));
      assertEquals(OffsetDateTime.parse("2026-11-05T00:00:00.123456Z"), f.bindings.get(4));
      assertEquals(OffsetDateTime.parse("2026-11-05T00:00:05.123456Z"), f.bindings.get(5));
      assertEquals(expiry == null ? null : expiry.atOffset(ZoneOffset.UTC), f.bindings.get(6));
      assertEquals("UNAVAILABLE", f.bindings.get(7));
      assertEquals(7, f.bindings.size());
      assertEquals(PS_CLOSE, f.events.getLast());
      f.assertBorrowed();
    }
  }

  @Test
  void enqueueRequiresExactlyOneAffectedRowAndClosesStatement() {
    for (int updated : new int[] {0, 2, -1}) {
      Fixture f = new Fixture();
      f.updated = updated;
      var failure = assertThrows(SQLDataException.class, () -> enqueue(f));
      assertEquals("revocation insert not established", failure.getMessage());
      assertEquals(DATA_STATE, failure.getSQLState());
      assertEquals(PS_CLOSE, f.events.getLast());
      f.assertBorrowed();
    }
  }

  @Test
  void enqueueNullTransactionExpiryPrecisionAndOverflowContracts() {
    Fixture f = new Fixture();
    assertThrows(
        NullPointerException.class,
        () -> REPO.enqueue(null, identity(1), payload(), null, RevocationFailureCode.UNAVAILABLE));
    assertThrows(
        NullPointerException.class,
        () -> REPO.enqueue(f.connection, null, payload(), null, RevocationFailureCode.UNAVAILABLE));
    assertThrows(
        NullPointerException.class,
        () ->
            REPO.enqueue(f.connection, identity(1), null, null, RevocationFailureCode.UNAVAILABLE));
    assertThrows(
        NullPointerException.class,
        () -> REPO.enqueue(f.connection, identity(1), payload(), null, null));
    for (Instant expiry : List.of(REQUESTED, REQUESTED.minusSeconds(1), REQUESTED.plusNanos(1)))
      assertThrows(
          IllegalArgumentException.class,
          () ->
              REPO.enqueue(
                  f.connection, identity(1), payload(), expiry, RevocationFailureCode.UNAVAILABLE));
    var last = new RevocationPayloadIdentity(new UUID(0, 1), Instant.MAX.minusNanos(999));
    assertThrows(
        DateTimeException.class,
        () -> REPO.enqueue(f.connection, last, payload(), null, RevocationFailureCode.UNAVAILABLE));
    for (int operation = 0; operation < 4; operation++) {
      Fixture invalid = new Fixture();
      invalid.autoCommit = true;
      int selected = operation;
      assertThrows(IllegalStateException.class, () -> operate(invalid, selected));
      assertFalse(invalid.events.contains(PREPARE));
      invalid.assertBorrowed();
    }
    assertFalse(f.events.contains(PREPARE));
    f.assertBorrowed();
  }

  @Test
  void claimCapturesDueLeaseSqlAndReturnsSortedImmutableDefensiveProjection() throws Exception {
    Fixture f = new Fixture();
    Map<String, Object> later = row(2);
    later.put(REQUESTED_AT, REQUESTED.plusSeconds(1).atOffset(ZoneOffset.UTC));
    f.rows.add(later);
    f.rows.add(row(3));
    f.rows.add(row(1));
    List<ClaimedRevocation> actual = REPO.claim(f.connection, OWNER, NOW, UNTIL, 100);
    assertEquals(CLAIM_SQL, normalized(f.sql));
    assertEquals(
        Map.of(
            1,
            NOW.atOffset(ZoneOffset.UTC),
            2,
            NOW.atOffset(ZoneOffset.UTC),
            3,
            100,
            4,
            OWNER.toString(),
            5,
            UNTIL.atOffset(ZoneOffset.UTC)),
        f.bindings);
    assertEquals(
        List.of(new UUID(0, 1), new UUID(0, 3), new UUID(0, 2)),
        actual.stream().map(x -> x.identity().id()).toList());
    assertEquals(VERSION, actual.getFirst().keyVersion());
    assertEquals(0, actual.getFirst().attemptCount());
    assertNull(actual.getFirst().expiresAt());
    assertEquals(OWNER, actual.getFirst().leaseOwner());
    assertEquals(UNTIL, actual.getFirst().leaseUntil());
    assertArrayEquals(new byte[101], actual.getFirst().payload().ciphertext());
    ((byte[]) f.rows.get(2).get(CIPHER))[0] = 1;
    assertArrayEquals(new byte[101], actual.getFirst().payload().ciphertext());
    assertThrows(UnsupportedOperationException.class, () -> actual.clear());
    assertEquals(
        List.of(RS_CLOSE, PS_CLOSE), f.events.subList(f.events.size() - 2, f.events.size()));
    f.assertBorrowed();
  }

  @Test
  void claimPublicBoundsAndPrecisionRejectBeforeSqlWhileBothLimitBoundsWork() throws Exception {
    Fixture f = new Fixture();
    assertThrows(NullPointerException.class, () -> REPO.claim(null, OWNER, NOW, UNTIL, 1));
    assertThrows(NullPointerException.class, () -> REPO.claim(f.connection, null, NOW, UNTIL, 1));
    assertThrows(NullPointerException.class, () -> REPO.claim(f.connection, OWNER, null, UNTIL, 1));
    assertThrows(NullPointerException.class, () -> REPO.claim(f.connection, OWNER, NOW, null, 1));
    for (int limit : new int[] {0, 101})
      assertThrows(
          IllegalArgumentException.class, () -> REPO.claim(f.connection, OWNER, NOW, UNTIL, limit));
    for (Instant until : List.of(NOW, NOW.minusSeconds(1), UNTIL.plusNanos(1)))
      assertThrows(
          IllegalArgumentException.class, () -> REPO.claim(f.connection, OWNER, NOW, until, 1));
    assertThrows(
        IllegalArgumentException.class,
        () -> REPO.claim(f.connection, OWNER, NOW.plusNanos(1), UNTIL, 1));
    assertFalse(f.events.contains(PREPARE));
    for (int limit : new int[] {1, 100}) {
      Fixture valid = new Fixture();
      assertEquals(List.of(), REPO.claim(valid.connection, OWNER, NOW, UNTIL, limit));
      assertEquals(limit, valid.bindings.get(3));
      valid.assertBorrowed();
    }
  }

  @Test
  void boundedCiphertextCopiesSmallValuesAndNeverLoadsOversizedDatabaseBytes() throws Exception {
    for (int length : new int[] {29, 116, 117, Integer.MAX_VALUE}) {
      Fixture f = new Fixture();
      var r = row(1);
      r.put(SIZE, length);
      if (length <= MAXIMUM_TEST_CIPHERTEXT) r.put(CIPHER, new byte[length]);
      else f.faults.put("getBytes:" + CIPHER, new AssertionError("oversized data must not load"));
      r.put(EXPIRY, REQUESTED.plusSeconds(1).atOffset(ZoneOffset.UTC));
      f.rows.add(r);
      var item = REPO.claim(f.connection, OWNER, NOW, UNTIL, 1).getFirst();
      assertEquals(REQUESTED.plusSeconds(1), item.expiresAt());
      if (length <= MAXIMUM_TEST_CIPHERTEXT)
        assertEquals(length, item.payload().ciphertext().length);
      else assertNull(item.payload());
      assertEquals(VERSION, item.keyVersion());
      f.assertBorrowed();
    }
  }

  @Test
  void storedCiphertextInvalidLengthOrInconsistentBytesHasClosedDataFailure() {
    for (int size : new int[] {-1, 0, 28}) {
      var r = row(1);
      r.put(SIZE, size);
      rejectRow(r);
    }
    var shortBytes = row(1);
    shortBytes.put(CIPHER, new byte[100]);
    rejectRow(shortBytes);
    var tooLong = row(1);
    tooLong.put(SIZE, 116);
    tooLong.put(CIPHER, new byte[117]);
    rejectRow(tooLong);
  }

  @Test
  void everyRequiredDatabaseColumnRejectsNullWithoutUnexpectedNpe() {
    for (String key :
        List.of(LEASE_OWNER, KEY, SIZE, CIPHER, ID, REQUESTED_AT, ATTEMPTS, LEASE_UNTIL)) {
      Fixture f = new Fixture();
      var r = row(1);
      r.put(key, null);
      f.rows.add(r);
      SQLDataException failure =
          assertThrows(
              SQLDataException.class, () -> REPO.claim(f.connection, OWNER, NOW, UNTIL, 1));
      assertEquals("required revocation SQL value absent", failure.getMessage());
      assertEquals(DATA_STATE, failure.getSQLState());
      assertNull(failure.getCause());
      assertEquals(
          List.of(RS_CLOSE, PS_CLOSE), f.events.subList(f.events.size() - 2, f.events.size()));
      f.assertBorrowed();
    }
  }

  @Test
  void invalidIdentityLeaseKeyAttemptAndTimesAreClosedWithoutProviderText() {
    for (String lease :
        List.of("not-a-uuid", "0-0-0-0-af", OWNER.toString().toUpperCase(java.util.Locale.ROOT))) {
      var r = row(1);
      r.put(LEASE_OWNER, lease);
      rejectRow(r);
    }
    for (String version : List.of("", "bad/version", "x".repeat(17))) {
      var r = row(1);
      r.put(KEY, version);
      rejectRow(r);
    }
    for (int attempt : new int[] {-1, 101}) {
      var r = row(1);
      r.put(ATTEMPTS, attempt);
      rejectRow(r);
    }
    for (String column : List.of(REQUESTED_AT, LEASE_UNTIL, EXPIRY)) {
      var r = row(1);
      r.put(column, REQUESTED.plusNanos(1).atOffset(ZoneOffset.UTC));
      rejectRow(r);
    }
    var leaseEarly = row(1);
    leaseEarly.put(LEASE_UNTIL, REQUESTED.atOffset(ZoneOffset.UTC));
    rejectRow(leaseEarly);
    var expiryEarly = row(1);
    expiryEarly.put(EXPIRY, REQUESTED.atOffset(ZoneOffset.UTC));
    rejectRow(expiryEarly);
    Fixture f = new Fixture();
    f.rows.add(row(1));
    f.faults.put("getObject:" + EXPIRY, new DateTimeException(PUBLIC_FAULT));
    dataFailure(() -> REPO.claim(f.connection, OWNER, NOW, UNTIL, 1));
    f.assertBorrowed();
  }

  @Test
  void failureBackoffHasIndependentThirtyThreeHundredNineHundredSecondVectorsAndSaturation()
      throws Exception {
    int[] previous = {0, 1, 2, 99, 100};
    int[] next = {1, 2, 3, 100, 100};
    String[] due = {
      "2026-11-05T00:00:40.123456Z",
      "2026-11-05T00:05:10.123456Z",
      "2026-11-05T00:15:10.123456Z",
      "2026-11-05T00:15:10.123456Z",
      "2026-11-05T00:15:10.123456Z"
    };
    String[] codes = {
      "SESSION_INVALID",
      "API_REJECTED",
      "INVALID_RESPONSE",
      "UNAVAILABLE",
      "KEY_UNAVAILABLE",
      "PAYLOAD_INVALID",
      "CRYPTO_UNAVAILABLE"
    };
    for (int i = 0; i < previous.length; i++)
      for (int c = 0; c < codes.length; c++) {
        Fixture f = new Fixture();
        var item = claimed(previous[i]);
        assertTrue(
            REPO.markFailure(f.connection, item, NOW, RevocationFailureCode.valueOf(codes[c])));
        assertEquals(FAILURE_SQL, normalized(f.sql));
        assertEquals(next[i], f.bindings.get(1));
        assertEquals(OffsetDateTime.parse(due[i]), f.bindings.get(2));
        assertEquals(codes[c], f.bindings.get(3));
        assertEquals(new UUID(0, 1), f.bindings.get(4));
        assertEquals(OWNER.toString(), f.bindings.get(5));
        assertEquals(UNTIL.atOffset(ZoneOffset.UTC), f.bindings.get(6));
        assertEquals(previous[i], f.bindings.get(7));
        assertEquals(NOW.atOffset(ZoneOffset.UTC), f.bindings.get(8));
        assertEquals(8, f.bindings.size());
        f.assertBorrowed();
      }
    for (int count : new int[] {0, 2}) {
      Fixture f = new Fixture();
      f.updated = count;
      assertFalse(
          REPO.markFailure(f.connection, claimed(0), NOW, RevocationFailureCode.UNAVAILABLE));
      f.assertBorrowed();
    }
  }

  @Test
  void failureNullEarlyTimeSubmicrosecondsAndOverflowStayCallerFailures() {
    Fixture f = new Fixture();
    assertThrows(
        NullPointerException.class,
        () -> REPO.markFailure(null, claimed(0), NOW, RevocationFailureCode.UNAVAILABLE));
    assertThrows(
        NullPointerException.class,
        () -> REPO.markFailure(f.connection, null, NOW, RevocationFailureCode.UNAVAILABLE));
    assertThrows(
        NullPointerException.class,
        () -> REPO.markFailure(f.connection, claimed(0), null, RevocationFailureCode.UNAVAILABLE));
    assertThrows(
        NullPointerException.class, () -> REPO.markFailure(f.connection, claimed(0), NOW, null));
    for (Instant at : List.of(REQUESTED.minusSeconds(1), NOW.plusNanos(1)))
      assertThrows(
          IllegalArgumentException.class,
          () -> REPO.markFailure(f.connection, claimed(0), at, RevocationFailureCode.UNAVAILABLE));
    assertFalse(f.events.contains(PREPARE));
    assertThrows(
        DateTimeException.class,
        () ->
            REPO.markFailure(
                f.connection,
                claimed(0),
                Instant.MAX.minusNanos(999),
                RevocationFailureCode.UNAVAILABLE));
    assertEquals(PS_CLOSE, f.events.getLast());
    f.assertBorrowed();
  }

  @Test
  void confirmationDeletesOnlyExactOneRowWithAllFiveLeaseCasBindings() throws Exception {
    for (int count : new int[] {0, 1, 2}) {
      Fixture f = new Fixture();
      f.updated = count;
      assertEquals(count == 1, REPO.removeConfirmed(f.connection, claimed(100), NOW));
      assertEquals(DELETE_SQL, normalized(f.sql));
      assertEquals(
          Map.of(
              1,
              new UUID(0, 1),
              2,
              OWNER.toString(),
              3,
              UNTIL.atOffset(ZoneOffset.UTC),
              4,
              100,
              5,
              NOW.atOffset(ZoneOffset.UTC)),
          f.bindings);
      assertEquals(PS_CLOSE, f.events.getLast());
      f.assertBorrowed();
    }
    Fixture f = new Fixture();
    assertThrows(NullPointerException.class, () -> REPO.removeConfirmed(null, claimed(0), NOW));
    assertThrows(NullPointerException.class, () -> REPO.removeConfirmed(f.connection, null, NOW));
    assertThrows(
        NullPointerException.class, () -> REPO.removeConfirmed(f.connection, claimed(0), null));
    assertThrows(
        IllegalArgumentException.class,
        () -> REPO.removeConfirmed(f.connection, claimed(0), NOW.plusNanos(1)));
    assertFalse(f.events.contains(PREPARE));
  }

  @Test
  void allFourStatementNullsAndClaimResultNullAreExplicitDataErrors() {
    for (int operation = 0; operation < 4; operation++) {
      Fixture f = new Fixture();
      f.nullStatement = true;
      int selected = operation;
      var failure = assertThrows(SQLDataException.class, () -> operate(f, selected));
      assertEquals("required revocation SQL value absent", failure.getMessage());
      assertEquals(DATA_STATE, failure.getSQLState());
      assertFalse(f.events.contains(PS_CLOSE));
      f.assertBorrowed();
    }
    Fixture f = new Fixture();
    f.nullResult = true;
    assertThrows(SQLDataException.class, () -> REPO.claim(f.connection, OWNER, NOW, UNTIL, 1));
    assertEquals(PS_CLOSE, f.events.getLast());
    assertFalse(f.events.contains(RS_CLOSE));
    f.assertBorrowed();
  }

  @Test
  void jdbcFailuresPreservePrimarySuppressionAndReverseOwnedResourceClose() {
    for (int op = 0; op < 4; op++)
      for (String phase :
          List.of(
              "getAutoCommit",
              PREPARE,
              "set:1",
              op == 1 ? EXECUTE_QUERY : EXECUTE_UPDATE,
              PS_CLOSE)) {
        Fixture f = new Fixture();
        SQLException fault = new SQLException(PUBLIC_FAULT);
        f.faults.put(phase, fault);
        int selected = op;
        assertSame(fault, assertThrows(SQLException.class, () -> operate(f, selected)));
        f.assertBorrowed();
      }
    for (String phase : List.of("next", "getObject:" + EXPIRY, RS_CLOSE)) {
      Fixture f = new Fixture();
      f.rows.add(row(1));
      SQLException primary = new SQLException(PUBLIC_FAULT);
      SQLException secondary = new SQLException("public close fixture");
      f.faults.put(phase, primary);
      f.faults.put(PS_CLOSE, secondary);
      assertSame(
          primary,
          assertThrows(SQLException.class, () -> REPO.claim(f.connection, OWNER, NOW, UNTIL, 1)));
      assertArrayEquals(new Throwable[] {secondary}, primary.getSuppressed());
      assertEquals(
          List.of(RS_CLOSE, PS_CLOSE), f.events.subList(f.events.size() - 2, f.events.size()));
      f.assertBorrowed();
    }
  }

  @Test
  void unknownRuntimeAndErrorKeepIdentityAndStillCloseOwnedJdbcOnly() {
    for (Throwable fault :
        List.of(new IllegalStateException(PUBLIC_FAULT), new AssertionError(PUBLIC_FAULT))) {
      Fixture f = new Fixture();
      f.rows.add(row(1));
      f.faults.put("next", fault);
      assertSame(
          fault,
          assertThrows(fault.getClass(), () -> REPO.claim(f.connection, OWNER, NOW, UNTIL, 1)));
      assertEquals(
          List.of(RS_CLOSE, PS_CLOSE), f.events.subList(f.events.size() - 2, f.events.size()));
      f.assertBorrowed();
    }
  }

  @Test
  void oneRepositoryHasIndependentConcurrentBorrowedConnectionsAndImmutableRows() throws Exception {
    var executor = Executors.newFixedThreadPool(2);
    try {
      var first =
          executor.submit(
              () -> {
                Fixture f = new Fixture();
                f.rows.add(row(1));
                var result = REPO.claim(f.connection, OWNER, NOW, UNTIL, 1);
                f.assertBorrowed();
                return result;
              });
      var second =
          executor.submit(
              () -> {
                Fixture f = new Fixture();
                var secondRow = row(2);
                secondRow.put(LEASE_OWNER, new UUID(0, 2).toString());
                f.rows.add(secondRow);
                var result = REPO.claim(f.connection, new UUID(0, 2), NOW, UNTIL, 1);
                assertEquals(new UUID(0, 2).toString(), f.bindings.get(4));
                f.assertBorrowed();
                return result;
              });
      var a = first.get(5, TimeUnit.SECONDS);
      var b = second.get(5, TimeUnit.SECONDS);
      assertEquals(new UUID(0, 1), a.getFirst().identity().id());
      assertEquals(new UUID(0, 2), b.getFirst().identity().id());
      assertEquals(OWNER, a.getFirst().leaseOwner());
      assertEquals(new UUID(0, 2), b.getFirst().leaseOwner());
      assertThrows(UnsupportedOperationException.class, () -> a.add(b.getFirst()));
    } finally {
      executor.shutdownNow();
      if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
        throw new AssertionError("revocation repository workers did not terminate");
      }
    }
  }

  private static void operate(Fixture f, int operation) throws SQLException {
    switch (operation) {
      case 0 -> enqueue(f);
      case 1 -> REPO.claim(f.connection, OWNER, NOW, UNTIL, 1);
      case 2 -> REPO.markFailure(f.connection, claimed(0), NOW, RevocationFailureCode.UNAVAILABLE);
      case 3 -> REPO.removeConfirmed(f.connection, claimed(0), NOW);
      default -> throw new AssertionError("unknown fixture operation");
    }
  }

  private static void enqueue(Fixture f) throws SQLException {
    REPO.enqueue(f.connection, identity(1), payload(), null, RevocationFailureCode.UNAVAILABLE);
  }

  private static RevocationPayloadIdentity identity(long id) {
    return new RevocationPayloadIdentity(new UUID(0, id), REQUESTED);
  }

  private static EncryptedRevocationPayload payload() {
    return new EncryptedRevocationPayload(VERSION, new byte[101]);
  }

  private static ClaimedRevocation claimed(int attempts) {
    return new ClaimedRevocation(identity(1), payload(), attempts, null, OWNER, UNTIL, VERSION);
  }

  private static Map<String, Object> row(long id) {
    var r = new LinkedHashMap<String, Object>();
    r.put(ID, new UUID(0, id));
    r.put(CIPHER, new byte[101]);
    r.put(SIZE, 101);
    r.put(KEY, VERSION);
    r.put(REQUESTED_AT, REQUESTED.atOffset(ZoneOffset.UTC));
    r.put(ATTEMPTS, 0);
    r.put(EXPIRY, null);
    r.put(LEASE_OWNER, OWNER.toString());
    r.put(LEASE_UNTIL, UNTIL.atOffset(ZoneOffset.UTC));
    return r;
  }

  private static String normalized(String sql) {
    return sql.replaceAll("\\s+", " ").strip();
  }

  private static void rejectRow(Map<String, Object> row) {
    Fixture f = new Fixture();
    f.rows.add(row);
    dataFailure(() -> REPO.claim(f.connection, OWNER, NOW, UNTIL, 1));
    f.assertBorrowed();
  }

  private static void dataFailure(Executable action) {
    var failure = assertThrows(SQLDataException.class, action);
    assertEquals("stored revocation metadata is invalid", failure.getMessage());
    assertEquals(DATA_STATE, failure.getSQLState());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Fixture {
    final List<String> events = new ArrayList<>();
    final Map<Integer, Object> bindings = new LinkedHashMap<>();
    final List<Map<String, Object>> rows = new ArrayList<>();
    final Map<String, Throwable> faults = new HashMap<>();
    String sql;
    boolean autoCommit;
    boolean nullStatement;
    boolean nullResult;
    int updated = 1;
    int cursor = -1;
    final ResultSet result =
        proxy(
            ResultSet.class,
            (method, args) -> {
              String name = method;
              events.add(
                  name.equals(JDBC_CLOSE)
                      ? RS_CLOSE
                      : name + (args.length > 0 ? ":" + args[0] : ""));
              at(
                  name.equals(JDBC_CLOSE)
                      ? RS_CLOSE
                      : name + (args.length > 0 ? ":" + args[0] : ""));
              return switch (name) {
                case "next" -> {
                  cursor++;
                  yield cursor < rows.size();
                }
                case "getString", "getObject", "getBytes" -> rows.get(cursor).get((String) args[0]);
                case JDBC_CLOSE -> null;
                default -> throw new AssertionError("unexpected result method " + name);
              };
            });
    final PreparedStatement statement =
        proxy(
            PreparedStatement.class,
            (method, args) -> {
              if (method.startsWith("set")) {
                events.add("set:" + args[0]);
                at("set:" + args[0]);
                Object value = args[1];
                bindings.put(
                    (Integer) args[0], value instanceof byte[] bytes ? bytes.clone() : value);
                return null;
              }
              String event = method.equals(JDBC_CLOSE) ? PS_CLOSE : method;
              events.add(event);
              at(event);
              return switch (method) {
                case "executeUpdate" -> updated;
                case "executeQuery" -> nullResult ? null : result;
                case JDBC_CLOSE -> null;
                default -> throw new AssertionError("unexpected statement method " + method);
              };
            });
    final Connection connection =
        proxy(
            Connection.class,
            (method, args) -> {
              events.add(method.equals("prepareStatement") ? PREPARE : method);
              at(method.equals("prepareStatement") ? PREPARE : method);
              return switch (method) {
                case "getAutoCommit" -> autoCommit;
                case "prepareStatement" -> {
                  sql = (String) args[0];
                  yield nullStatement ? null : statement;
                }
                default -> throw new AssertionError("borrowed connection operation " + method);
              };
            });

    void at(String point) throws Throwable {
      Throwable fault = faults.get(point);
      if (fault != null) throw fault;
    }

    void assertBorrowed() {
      assertFalse(events.contains("commit"));
      assertFalse(events.contains("rollback"));
      assertFalse(events.contains(JDBC_CLOSE));
      assertFalse(events.contains("setAutoCommit"));
      assertFalse(events.contains("setReadOnly"));
    }
  }

  @FunctionalInterface
  private interface Call {
    Object invoke(String method, Object[] args) throws Throwable;
  }

  private static <T> T proxy(Class<T> type, Call call) {
    return type.cast(
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (object, method, args) ->
                call.invoke(method.getName(), args == null ? new Object[0] : args)));
  }
}
