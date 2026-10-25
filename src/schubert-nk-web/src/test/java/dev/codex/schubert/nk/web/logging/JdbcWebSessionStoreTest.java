package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.session.EncryptedSessionPayload;
import dev.codex.schubert.nk.web.session.JdbcWebSessionStore;
import dev.codex.schubert.nk.web.session.SessionPayloadIdentity;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.session.WebSessionRow;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * NK-WEB-001/PT-WEB-024..031; FUN-001/AUT-001..004; UI226/242; SS314/331/352;
 * SSC-040/PG-D-096/BUG-056/YKT-051. Actual isolated PostgreSQL and independent nine-column SQL
 * oracle.
 */
class JdbcWebSessionStoreTest {
  private static final Instant NOW = Instant.parse("2026-09-08T00:00:00.123456Z");
  private static final List<String> COLUMNS =
      List.of(
          "id",
          "session_id_hash",
          "attributes_ciphertext",
          "key_version",
          "created_at",
          "last_accessed_at",
          "expires_at",
          "max_inactive_seconds",
          "version");
  private static final JdbcWebSessionStore STORE = new JdbcWebSessionStore();
  private static final EncryptedSessionPayload PAYLOAD =
      new EncryptedSessionPayload("v1", new byte[64]);
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
      s.executeUpdate("delete from schubert_web_session.web_http_sessions");
    }
  }

  @Test
  void web024RoundTripCiphertextAndExplicitColumns() throws Exception {
    try (var c = db.transaction()) {
      var fault = new Fault();
      assertTrue(STORE.findLocked(fault.wrap(c), hash(1)).isEmpty());
      STORE.insert(fault.wrap(c), row(1, 0));
      check(STORE.findLocked(fault.wrap(c), hash(1)).orElseThrow(), 1, 0);
      assertFalse(c.isClosed());
      assertFalse(c.getAutoCommit());
      for (String sql : fault.sql) {
        assertFalse(sql.contains("*"));
        assertFalse(sql.contains(hash(1)));
        if (sql.startsWith("select "))
          assertEquals(
              "select "
                  + String.join(",", COLUMNS)
                  + " from schubert_web_session.web_http_sessions where session_id_hash=? for update",
              sql);
      }
      try (var s =
          c.prepareStatement(
              "select "
                  + String.join(",", COLUMNS)
                  + " from schubert_web_session.web_http_sessions where id=?")) {
        s.setObject(1, new UUID(0, 1));
        try (var result = s.executeQuery()) {
          assertEquals(9, result.getMetaData().getColumnCount());
          for (int i = 0; i < 9; i++)
            assertEquals(COLUMNS.get(i), result.getMetaData().getColumnLabel(i + 1));
          assertTrue(result.next());
          assertEquals(new UUID(0, 1), result.getObject("id", UUID.class));
          assertEquals(hash(1), result.getString("session_id_hash"));
          assertArrayEquals(new byte[64], result.getBytes("attributes_ciphertext"));
          assertEquals("v1", result.getString("key_version"));
          assertEquals(
              NOW, result.getObject("created_at", java.time.OffsetDateTime.class).toInstant());
          assertEquals(
              NOW.plusSeconds(1),
              result.getObject("last_accessed_at", java.time.OffsetDateTime.class).toInstant());
          assertEquals(
              NOW.plusSeconds(28801),
              result.getObject("expires_at", java.time.OffsetDateTime.class).toInstant());
          assertEquals(28800, result.getInt("max_inactive_seconds"));
          assertEquals(0, result.getLong("version"));
          assertFalse(result.next());
        }
      }
      c.commit();
    }
    assertEquals(1, count());
  }

  @Test
  void web025CompareAndSwapNoResurrection() throws Exception {
    seed();
    try (var c = db.transaction()) {
      var original = STORE.findLocked(c, hash(1)).orElseThrow();
      for (var wrong :
          List.of(
              new SessionPayloadIdentity(new UUID(0, 2), hash(1), NOW),
              new SessionPayloadIdentity(new UUID(0, 1), hash(2), NOW),
              new SessionPayloadIdentity(new UUID(0, 1), hash(1), NOW.minusNanos(1000)))) {
        var before =
            new WebSessionRow(wrong, PAYLOAD, NOW.plusSeconds(1), NOW.plusSeconds(28801), 28800, 0);
        var after =
            new WebSessionRow(wrong, PAYLOAD, NOW.plusSeconds(2), NOW.plusSeconds(28802), 28800, 1);
        assertFalse(STORE.replace(c, before, after));
        assertFalse(STORE.delete(c, wrong, 0));
      }
      byte[] changed = new byte[65];
      Arrays.fill(changed, (byte) 7);
      var replacement =
          new WebSessionRow(
              original.identity(),
              new EncryptedSessionPayload("v2", changed),
              NOW.plusSeconds(2),
              NOW.plusSeconds(5),
              3,
              1);
      assertTrue(STORE.replace(c, original, replacement));
      var actual = STORE.findLocked(c, hash(1)).orElseThrow();
      assertArrayEquals(changed, actual.payload().ciphertext());
      assertEquals("v2", actual.payload().keyVersion());
      assertEquals(NOW.plusSeconds(2), actual.lastAccessedAt());
      assertEquals(NOW.plusSeconds(5), actual.expiresAt());
      assertEquals(3, actual.maxInactiveSeconds());
      assertEquals(1, actual.version());
      assertFalse(STORE.replace(c, original, row(1, 1)));
      assertFalse(STORE.delete(c, original.identity(), 0));
      assertThrows(IllegalArgumentException.class, () -> STORE.replace(c, original, row(2, 1)));
      assertThrows(IllegalArgumentException.class, () -> STORE.replace(c, original, row(1, 0)));
      assertThrows(IllegalArgumentException.class, () -> STORE.replace(c, original, row(1, 2)));
      assertTrue(STORE.delete(c, original.identity(), 1));
      assertFalse(STORE.delete(c, original.identity(), 1));
      assertFalse(STORE.replace(c, row(1, 1), row(1, 2)));
      assertTrue(STORE.findLocked(c, hash(1)).isEmpty());
      c.commit();
    }
    assertEquals(0, count());
  }

  @Test
  void web026CallerTransactionsRollbackFixation() throws Exception {
    try (var c = db.transaction()) {
      STORE.insert(c, row(1, 0));
      assertEquals(0, count());
      c.rollback();
    }
    assertEquals(0, count());
    seed();
    try (var c = db.transaction()) {
      assertTrue(STORE.replace(c, row(1, 0), row(1, 1)));
      c.rollback();
      check(STORE.findLocked(c, hash(1)).orElseThrow(), 1, 0);
      c.rollback();
      assertTrue(STORE.delete(c, row(1, 0).identity(), 0));
      STORE.insert(c, row(2, 0));
      assertEquals(1, count());
      c.rollback();
      check(STORE.findLocked(c, hash(1)).orElseThrow(), 1, 0);
      assertTrue(STORE.findLocked(c, hash(2)).isEmpty());
      c.rollback();
      assertTrue(STORE.delete(c, row(1, 0).identity(), 0));
      STORE.insert(c, row(2, 0));
      unavailable(() -> STORE.insert(c, row(2, 0)));
      c.rollback();
      check(STORE.findLocked(c, hash(1)).orElseThrow(), 1, 0);
      c.rollback();
      assertTrue(STORE.delete(c, row(1, 0).identity(), 0));
      STORE.insert(c, row(2, 0));
      c.commit();
      assertTrue(STORE.findLocked(c, hash(1)).isEmpty());
      check(STORE.findLocked(c, hash(2)).orElseThrow(), 2, 0);
      c.rollback();
    }
  }

  @Test
  void web027RoleIsolationAndConstraints() throws Exception {
    seed();
    for (String table : List.of("schubert.app_users", "schubert.app_logs")) {
      try (var c = db.web();
          var s = c.createStatement()) {
        assertEquals(
            "42501",
            assertThrows(SQLException.class, () -> s.executeQuery("select id from " + table))
                .getSQLState());
      }
    }
    for (String column : COLUMNS) {
      try (var c = db.transaction();
          var s = c.createStatement()) {
        assertEquals(
            "23502",
            assertThrows(
                    SQLException.class,
                    () ->
                        s.executeUpdate(
                            "update schubert_web_session.web_http_sessions set "
                                + column
                                + "=null"))
                .getSQLState());
        c.rollback();
      }
    }
    for (String assignment :
        List.of(
            "session_id_hash='bad'",
            "attributes_ciphertext=decode('00','hex')",
            "key_version='bad id'",
            "last_accessed_at=created_at-interval '1 second'",
            "expires_at=last_accessed_at-interval '1 second'",
            "max_inactive_seconds=0",
            "max_inactive_seconds=28801",
            "version=-1",
            "version=1000000000")) {
      try (var c = db.transaction();
          var s = c.createStatement()) {
        assertEquals(
            "23514",
            assertThrows(
                    SQLException.class,
                    () ->
                        s.executeUpdate(
                            "update schubert_web_session.web_http_sessions set " + assignment))
                .getSQLState());
        c.rollback();
      }
    }
    try (var c = db.transaction()) {
      unavailable(() -> STORE.insert(c, row(1, 0)));
      c.rollback();
      var duplicateHash =
          new WebSessionRow(
              new SessionPayloadIdentity(new UUID(0, 2), hash(1), NOW),
              PAYLOAD,
              NOW,
              NOW.plusSeconds(28800),
              28800,
              0);
      unavailable(() -> STORE.insert(c, duplicateHash));
      c.rollback();
      assertThrows(IllegalArgumentException.class, () -> STORE.findLocked(c, "' OR 1=1 --"));
    }
    assertEquals(1, count());
  }

  @Test
  void web028NullRowAndConfigurationBoundaries() throws Exception {
    // BUG169/YKT130: microsecond-valid but unrepresentable Instants fail at the storage boundary.
    for (Instant invalid :
        List.of(Instant.MIN, Instant.MAX.truncatedTo(java.time.temporal.ChronoUnit.MICROS))) {
      var invalidIdentity = new SessionPayloadIdentity(new UUID(0, 1), hash(1), invalid);
      var before = new WebSessionRow(invalidIdentity, PAYLOAD, invalid, invalid, 1, 0);
      var after = new WebSessionRow(invalidIdentity, PAYLOAD, invalid, invalid, 1, 1);
      try (var c = db.transaction()) {
        unavailable(() -> STORE.insert(c, before));
        unavailable(() -> STORE.replace(c, before, after));
        unavailable(() -> STORE.delete(c, invalidIdentity, 0));
        assertFalse(c.isClosed());
        c.rollback();
      }
    }
    var identity = row(1, 0).identity();
    assertThrows(
        NullPointerException.class, () -> new WebSessionRow(null, PAYLOAD, NOW, NOW, 1, 0));
    assertThrows(
        NullPointerException.class, () -> new WebSessionRow(identity, null, NOW, NOW, 1, 0));
    assertThrows(
        NullPointerException.class, () -> new WebSessionRow(identity, PAYLOAD, null, NOW, 1, 0));
    assertThrows(
        NullPointerException.class, () -> new WebSessionRow(identity, PAYLOAD, NOW, null, 1, 0));
    for (Instant last : List.of(NOW.minusNanos(1000), NOW.plusNanos(1)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new WebSessionRow(identity, PAYLOAD, last, NOW.plusSeconds(1), 1, 0));
    for (Instant expiry : List.of(NOW.minusNanos(1000), NOW.plusNanos(1)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new WebSessionRow(identity, PAYLOAD, NOW, expiry, 1, 0));
    for (int ttl : new int[] {0, 28801})
      assertThrows(
          IllegalArgumentException.class,
          () -> new WebSessionRow(identity, PAYLOAD, NOW, NOW, ttl, 0));
    for (long version : new long[] {-1, 1000000000L})
      assertThrows(
          IllegalArgumentException.class,
          () -> new WebSessionRow(identity, PAYLOAD, NOW, NOW, 1, version));
    assertEquals(1, new WebSessionRow(identity, PAYLOAD, NOW, NOW, 1, 0).maxInactiveSeconds());
    assertEquals(999999999, row(1, 999999999).version());
    assertEquals("WebSessionRow[REDACTED]", row(1, 0).toString());
    assertThrows(NullPointerException.class, () -> STORE.findLocked(null, hash(1)));
    assertThrows(NullPointerException.class, () -> STORE.insert(null, row(1, 0)));
    assertThrows(NullPointerException.class, () -> STORE.replace(null, row(1, 0), row(1, 1)));
    assertThrows(NullPointerException.class, () -> STORE.delete(null, identity, 0));
    try (var c = db.transaction()) {
      assertThrows(NullPointerException.class, () -> STORE.findLocked(c, null));
      assertThrows(NullPointerException.class, () -> STORE.insert(c, null));
      assertThrows(NullPointerException.class, () -> STORE.replace(c, null, row(1, 1)));
      assertThrows(NullPointerException.class, () -> STORE.replace(c, row(1, 0), null));
      assertThrows(NullPointerException.class, () -> STORE.delete(c, null, 0));
      for (long version : new long[] {-1, 1000000000L})
        assertThrows(IllegalArgumentException.class, () -> STORE.delete(c, identity, version));
      assertThrows(IllegalArgumentException.class, () -> STORE.insert(c, row(1, 1)));
      assertThrows(
          IllegalArgumentException.class, () -> STORE.replace(c, row(1, 999999999), row(1, 0)));
      c.setReadOnly(true);
      for (int operation = 0; operation < 4; operation++) {
        final int op = operation;
        unavailable(() -> call(op, c));
      }
    }
    try (var c = db.web()) {
      for (int operation = 0; operation < 4; operation++) {
        final int op = operation;
        unavailable(() -> call(op, c));
      }
    }
  }

  @Test
  void web029EveryJdbcFailureIsRedactedAndResourcesClose() throws Exception {
    for (String close : List.of("result.close", "statement.close")) {
      try (var c = db.transaction()) {
        var fault = new Fault();
        fault.failure = close;
        unavailable(() -> STORE.findLocked(fault.wrap(c), hash(1)));
        assertTrue(fault.hit);
        assertEquals(1, fault.resultsClosed);
        assertEquals(1, fault.statementsClosed);
        c.rollback();
      }
    }
    for (int operation = 0; operation < 4; operation++) {
      final int op = operation;
      var methods =
          new ArrayList<>(
              List.of(
                  "connection.getAutoCommit",
                  "connection.isReadOnly",
                  "connection.prepareStatement",
                  "statement.setString",
                  "statement.close"));
      if (op == 0)
        methods.addAll(
            List.of(
                "statement.executeQuery",
                "result.next",
                "result.getObject",
                "result.getString",
                "result.getBytes",
                "result.close"));
      else {
        methods.addAll(
            List.of("statement.setObject", "statement.setLong", "statement.executeUpdate"));

        if (op != 3) methods.addAll(List.of("statement.setBytes", "statement.setInt"));
        if (op == 1)
          methods.addAll(
              List.of("statement.setObject#2", "statement.setObject#3", "statement.setObject#4"));
        if (op == 2)
          methods.addAll(
              List.of("statement.setObject#2", "statement.setObject#3", "statement.setObject#4"));
        if (op == 3) methods.add("statement.setObject#2");
      }
      for (String method : methods) {
        try (var c = db.transaction()) {
          if (op != 1) STORE.insert(c, row(1, 0));
          var fault = new Fault();
          fault.failure = method;
          unavailable(() -> call(op, fault.wrap(c)));
          assertTrue(fault.hit, method);
          assertFalse(c.isClosed());
          c.rollback();
          if (method.equals("statement.close")) assertEquals(1, fault.statementsClosed);
          if (method.equals("result.close")) {
            assertEquals(1, fault.resultsClosed);
            assertEquals(1, fault.statementsClosed);
          }
        }
      }
      for (String method :
          op == 0
              ? List.of("connection.prepareStatement", "statement.executeQuery")
              : List.of("connection.prepareStatement")) {
        try (var c = db.transaction()) {
          var fault = new Fault();
          fault.nullResource = method;
          unavailable(() -> call(op, fault.wrap(c)));
          assertTrue(fault.hit);
          c.rollback();
        }
      }
      if (op != 0)
        for (int count : op == 1 ? new int[] {-1, 0, 2} : new int[] {-1, 2}) {
          try (var c = db.transaction()) {
            var fault = new Fault();
            fault.count = count;
            unavailable(() -> call(op, fault.wrap(c)));
            assertTrue(fault.hit);
            c.rollback();
          }
        }
    }
  }

  @Test
  void web030InvalidDatabaseRowsFailClosed() throws Exception {
    seed();
    for (String column : COLUMNS) {
      try (var c = db.transaction()) {
        var fault = new Fault();
        fault.columns.put(column, null);
        fault.failure = "result.close";
        unavailable(() -> STORE.findLocked(fault.wrap(c), hash(1)));
        assertTrue(fault.columnHit);
        assertEquals(1, fault.resultsClosed);
        assertEquals(1, fault.statementsClosed);
        c.rollback();
      }
    }
    var invalid = new ArrayList<Map.Entry<String, Object>>();
    invalid.add(Map.entry("session_id_hash", "a".repeat(63)));
    invalid.add(Map.entry("key_version", "bad id"));
    invalid.add(Map.entry("attributes_ciphertext", new byte[28]));
    invalid.add(Map.entry("attributes_ciphertext", new byte[16437]));
    invalid.add(Map.entry("created_at", NOW.plusSeconds(2).atOffset(ZoneOffset.UTC)));
    invalid.add(Map.entry("created_at", NOW.plusNanos(1).atOffset(ZoneOffset.UTC)));
    invalid.add(Map.entry("last_accessed_at", NOW.minusNanos(1000).atOffset(ZoneOffset.UTC)));
    invalid.add(Map.entry("last_accessed_at", NOW.plusNanos(1).atOffset(ZoneOffset.UTC)));
    invalid.add(Map.entry("expires_at", NOW.atOffset(ZoneOffset.UTC)));
    invalid.add(Map.entry("expires_at", NOW.plusSeconds(2).plusNanos(1).atOffset(ZoneOffset.UTC)));
    invalid.add(Map.entry("max_inactive_seconds", 0));
    invalid.add(Map.entry("max_inactive_seconds", 28801));
    invalid.add(Map.entry("version", -1L));
    invalid.add(Map.entry("version", 1000000000L));
    for (var entry : invalid) {
      try (var c = db.transaction()) {
        var fault = new Fault();
        fault.columns.put(entry.getKey(), entry.getValue());
        unavailable(() -> STORE.findLocked(fault.wrap(c), hash(1)));
        assertTrue(fault.columnHit);
        c.rollback();
      }
    }
    try (var c = db.transaction()) {
      var fault = new Fault();
      fault.duplicate = true;
      unavailable(() -> STORE.findLocked(fault.wrap(c), hash(1)));
      assertEquals(2, fault.nextCalls);
      c.rollback();
    }
  }

  @Test
  void web294ProviderGetterFailureNeverBecomesInvalidRow() throws Exception {
    seed();
    for (boolean closeFailure : List.of(false, true)) {
      try (var connection = db.transaction()) {
        var fault = new Fault();
        fault.runtimeFailure = "result.getObject";
        if (closeFailure) fault.failure = "result.close";
        var failure =
            assertThrows(
                SessionStoreException.class,
                () -> STORE.findLocked(fault.wrap(connection), hash(1)));
        assertEquals(SessionStoreException.class, failure.getClass());
        assertEquals("session storage is unavailable", failure.getMessage());
        assertNull(failure.getCause());
        assertEquals(0, failure.getSuppressed().length);
        assertTrue(fault.runtimeHit);
        assertEquals(closeFailure, fault.hit);
        assertEquals(1, fault.resultsClosed);
        assertEquals(1, fault.statementsClosed);
        assertFalse(connection.isClosed());
        connection.rollback();
      }
    }
    assertEquals(1, count());
  }

  @Test
  void web296MalformedRowWithResultCloseFailureIsInfrastructureNotInvalidation() throws Exception {
    seed();
    try (var connection = db.transaction()) {
      var fault = new Fault();
      fault.columns.put("id", null);
      fault.failure = "result.close";
      SessionStoreException failure =
          assertThrows(
              SessionStoreException.class, () -> STORE.findLocked(fault.wrap(connection), hash(1)));
      assertEquals(SessionStoreException.class, failure.getClass());
      assertEquals("session storage is unavailable", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
      assertTrue(fault.columnHit);
      assertTrue(fault.hit);
      assertEquals(1, fault.resultsClosed);
      assertEquals(1, fault.statementsClosed);
      assertFalse(connection.isClosed());
      connection.rollback();
    }
    assertEquals(1, count());
  }

  @Test
  void web298MalformedRowWithFatalResultClosePropagatesFatalWithoutInvalidation() throws Exception {
    seed();
    try (var connection = db.transaction()) {
      var fault = new Fault();
      fault.columns.put("id", null);
      AssertionError fatal = new AssertionError("synthetic close failure");
      fault.fatalClose = fatal;
      AssertionError observed =
          assertThrows(
              AssertionError.class, () -> STORE.findLocked(fault.wrap(connection), hash(1)));
      assertSame(fatal, observed);
      assertEquals(0, observed.getSuppressed().length);
      assertTrue(fault.columnHit);
      assertEquals(1, fault.resultsClosed);
      assertEquals(1, fault.statementsClosed);
      assertFalse(connection.isClosed());
      connection.rollback();
    }
    assertEquals(1, count());
  }

  @Test
  void web031ConcurrentLocksAndVersionsStayConsistent() throws Exception {
    seed();
    try (var pool = Executors.newFixedThreadPool(10)) {
      var jobs = new ArrayList<Callable<Void>>();
      for (int i = 0; i < 100; i++)
        jobs.add(
            () -> {
              try (var c = db.transaction()) {
                var original = STORE.findLocked(c, hash(1)).orElseThrow();
                assertTrue(STORE.replace(c, original, row(1, original.version() + 1)));
                c.commit();
              }
              return null;
            });
      for (var future : pool.invokeAll(jobs)) future.get(20, TimeUnit.SECONDS);
      try (var c = db.transaction()) {
        check(STORE.findLocked(c, hash(1)).orElseThrow(), 1, 100);
        c.rollback();
      }
      var racers = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 2; i++)
        racers.add(
            () -> {
              try (var c = db.transaction()) {
                boolean won = STORE.replace(c, row(1, 100), row(1, 101));
                c.commit();
                return won;
              }
            });
      int winners = 0;
      for (var future : pool.invokeAll(racers)) if (future.get(20, TimeUnit.SECONDS)) winners++;
      assertEquals(1, winners);
      try (var c = db.transaction()) {
        check(STORE.findLocked(c, hash(1)).orElseThrow(), 1, 101);
        assertTrue(STORE.delete(c, row(1, 101).identity(), 101));
        c.commit();
        assertFalse(STORE.replace(c, row(1, 101), row(1, 102)));
        c.commit();
      }
    }
    assertEquals(0, count());
  }

  @Test
  void rerun006JdbcEverySessionCataloguePreservesFatalAfterOwnedResourceClose() throws Exception {
    for (int operation = 0; operation < 5; operation++) {
      final int op = operation;
      try (var c = db.transaction()) {
        if (op != 1) STORE.insert(c, row(1, 0));
        var fault = new Fault();
        var fatal = new AssertionError("private-jdbc-fatal");
        fault.failure = op == 0 ? "result.getObject" : "statement.setString";
        if (op == 0) fault.fatalClose = fatal;
        else fault.fatalStatementClose = fatal;
        assertSame(
            fatal,
            assertThrows(
                AssertionError.class,
                () -> {
                  if (op == 4) STORE.deleteByHash(fault.wrap(c), hash(1));
                  else call(op, fault.wrap(c));
                }));
        assertTrue(fault.hit);
        assertEquals(1, fault.statementsClosed);
        assertEquals(op == 0 ? 1 : 0, fault.resultsClosed);
        assertFalse(c.isClosed());
        c.rollback();
      }
      assertEquals(0, count());
    }
    for (boolean marker : List.of(false, true)) {
      try (var c = db.transaction()) {
        STORE.insert(c, row(1, 0));
        var fault = new Fault();
        var fatal = new AssertionError("private-nested-jdbc-fatal");
        var closing = new SQLException("private-jdbc-close", fatal);
        fault.resultCloseFault = closing;
        if (marker) fault.columns.put("id", null);
        else fault.failure = "result.getObject";
        assertSame(
            fatal,
            assertThrows(AssertionError.class, () -> STORE.findLocked(fault.wrap(c), hash(1))));
        assertEquals(1, fault.statementsClosed);
        assertEquals(1, fault.resultsClosed);
        assertFalse(c.isClosed());
        c.rollback();
      }
      assertEquals(0, count());
    }
  }

  private static void call(int operation, Connection connection) {
    switch (operation) {
      case 0 -> STORE.findLocked(connection, hash(1));
      case 1 -> STORE.insert(connection, row(1, 0));
      case 2 -> STORE.replace(connection, row(1, 0), row(1, 1));
      case 3 -> STORE.delete(connection, row(1, 0).identity(), 0);
      default -> throw new AssertionError("unknown test operation");
    }
  }

  private static String hash(long id) {
    return String.format(Locale.ROOT, "%064x", id);
  }

  private static WebSessionRow row(long id, long version) {
    return new WebSessionRow(
        new SessionPayloadIdentity(new UUID(0, id), hash(id), NOW),
        PAYLOAD,
        NOW.plusSeconds(1 + version),
        NOW.plusSeconds(28801 + version),
        28800,
        version);
  }

  private static void check(WebSessionRow row, long id, long version) {
    assertEquals(new UUID(0, id), row.identity().id());
    assertEquals(hash(id), row.identity().sessionIdHash());
    assertEquals(NOW, row.identity().createdAt());
    assertEquals("v1", row.payload().keyVersion());
    assertArrayEquals(new byte[64], row.payload().ciphertext());
    assertEquals(NOW.plusSeconds(1 + version), row.lastAccessedAt());
    assertEquals(NOW.plusSeconds(28801 + version), row.expiresAt());
    assertEquals(28800, row.maxInactiveSeconds());
    assertEquals(version, row.version());
  }

  private static void seed() throws Exception {
    try (var c = db.transaction()) {
      STORE.insert(c, row(1, 0));
      c.commit();
    }
  }

  private static int count() throws Exception {
    try (var c = db.web();
        var s = c.createStatement();
        var r = s.executeQuery("select count(*) from schubert_web_session.web_http_sessions")) {
      assertTrue(r.next());
      return r.getInt(1);
    }
  }

  private static void unavailable(org.junit.jupiter.api.function.Executable executable) {
    var error = assertThrows(SessionStoreException.class, executable);
    assertEquals("session storage is unavailable", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  /** Intercepts only public JDBC calls, never production/private fields. */
  private static final class Fault {
    String failure = "";
    String nullResource = "";
    String runtimeFailure = "";
    Error fatalClose;
    Error fatalStatementClose;
    Throwable resultCloseFault;
    Integer count;
    boolean duplicate;
    boolean hit;
    boolean columnHit;
    boolean runtimeHit;
    int statementsClosed;
    int resultsClosed;
    int nextCalls;
    final Map<String, Integer> seen = new HashMap<>();
    final Map<String, Object> columns = new HashMap<>();
    final List<String> sql = new ArrayList<>();

    Connection wrap(Connection connection) {
      return wrap(Connection.class, connection, "connection");
    }

    private <T> T wrap(Class<T> type, T target, String kind) {
      return type.cast(
          Proxy.newProxyInstance(
              type.getClassLoader(),
              new Class<?>[] {type},
              (proxy, method, args) -> {
                String name = kind + "." + method.getName();
                if (name.equals("connection.prepareStatement")) sql.add((String) args[0]);
                if (name.equals("statement.close")) statementsClosed++;
                if (name.equals("result.close")) resultsClosed++;
                if (name.equals("result.close") && fatalClose != null) {
                  method.invoke(target, args);
                  throw fatalClose;
                }
                if (name.equals("statement.close") && fatalStatementClose != null) {
                  method.invoke(target, args);
                  throw fatalStatementClose;
                }
                if (name.equals("result.close") && resultCloseFault != null) {
                  method.invoke(target, args);
                  throw resultCloseFault;
                }
                int occurrence = seen.merge(name, 1, Integer::sum);
                if (name.equals(runtimeFailure)) {
                  runtimeHit = true;
                  throw new IllegalArgumentException("private-provider-marker");
                }
                if (name.equals(failure) || (name + "#" + occurrence).equals(failure)) {
                  hit = true;
                  if (method.getName().equals("close")) method.invoke(target, args);
                  throw new SQLDataException("private-sql-marker", "22000");
                }
                if (name.equals(nullResource)) {
                  hit = true;
                  return null;
                }
                if (name.equals("statement.executeUpdate") && count != null) {
                  hit = true;
                  return count;
                }
                if (kind.equals("result")
                    && method.getName().startsWith("get")
                    && args != null
                    && args.length > 0
                    && columns.containsKey(args[0])) {
                  columnHit = true;
                  return columns.get(args[0]);
                }
                if (name.equals("result.next")) {
                  nextCalls++;
                  if (duplicate && nextCalls == 2) return true;
                }
                try {
                  Object value = method.invoke(target, args);
                  if (value instanceof PreparedStatement statement)
                    return wrap(PreparedStatement.class, statement, "statement");
                  if (value instanceof ResultSet result)
                    return wrap(ResultSet.class, result, "result");
                  return value;
                } catch (InvocationTargetException failure) {
                  throw Objects.requireNonNull(failure.getCause());
                }
              }));
    }
  }
}
