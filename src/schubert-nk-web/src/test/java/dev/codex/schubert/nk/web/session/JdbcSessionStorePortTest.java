package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
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
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-WEB-JDBCSTOREPORT001..015. Borrowed JDBC protocol only; no DB, crypto or session issuance. */
final class JdbcSessionStorePortTest {
  private static final String SET_STRING = "setString";
  private static final String SET_OBJECT = "setObject";
  private static final String SET_BYTES = "setBytes";
  private static final String SET_INT = "setInt";
  private static final String SET_LONG = "setLong";
  private static final String GET_OBJECT = "getObject";
  private static final String GET_STRING = "getString";
  private static final String GET_BYTES = "getBytes";
  private static final JdbcWebSessionStore STORE = new JdbcWebSessionStore();
  private static final UUID ID = new UUID(0, 81);
  private static final String HASH = "a".repeat(64);
  private static final String KEY_VERSION = "public-v1";
  private static final String DIAGNOSTIC = "public-jdbc-diagnostic";
  private static final String FIXED = "session storage is unavailable";
  private static final Instant CREATED = Instant.parse("2026-01-01T00:00:00.123456Z");
  private static final Instant ACCESSED = Instant.parse("2026-01-01T00:00:01.123456Z");
  private static final Instant EXPIRES = Instant.parse("2026-01-01T08:00:01.123456Z");
  private static final String TABLE = "schubert_web_session.web_http_sessions";
  private static final String COLUMNS =
      "id,session_id_hash,attributes_ciphertext,key_version,created_at,last_accessed_at,expires_at,max_inactive_seconds,version";
  private static final String SELECT_SQL =
      "select " + COLUMNS + " from " + TABLE + " where session_id_hash=? for update";
  private static final String INSERT_SQL =
      "insert into " + TABLE + " (" + COLUMNS + ") values (?,?,?,?,?,?,?,?,?)";
  private static final String UPDATE_SQL =
      "update "
          + TABLE
          + " set attributes_ciphertext=?,key_version=?,last_accessed_at=?,expires_at=?,max_inactive_seconds=?,version=?"
          + " where id=? and session_id_hash=? and created_at=? and version=?";
  private static final String DELETE_SQL =
      "delete from " + TABLE + " where id=? and session_id_hash=? and created_at=? and version=?";
  private static final String HASH_DELETE_SQL = "delete from " + TABLE + " where session_id_hash=?";
  private static final String AUTO = "connection.getAutoCommit";
  private static final String READ_ONLY = "connection.isReadOnly";
  private static final String PREPARE = "connection.prepareStatement";
  private static final String QUERY = "statement.executeQuery";
  private static final String UPDATE = "statement.executeUpdate";
  private static final String NEXT = "result.next";
  private static final String CLOSE_RESULT = "result.close";
  private static final String CLOSE_STATEMENT = "statement.close";
  private static final String ID_COLUMN = "id";
  private static final String HASH_COLUMN = "session_id_hash";
  private static final String BYTES_COLUMN = "attributes_ciphertext";
  private static final String KEY_COLUMN = "key_version";
  private static final String CREATED_COLUMN = "created_at";
  private static final String ACCESSED_COLUMN = "last_accessed_at";
  private static final String EXPIRES_COLUMN = "expires_at";
  private static final String IDLE_COLUMN = "max_inactive_seconds";
  private static final String VERSION_COLUMN = "version";

  @Test
  void publicNullHashVersionAndReplacementBoundsNeverReachJdbc() {
    var p = new Port(Op.FIND);
    assertThrows(NullPointerException.class, () -> STORE.findLocked(null, HASH));
    assertThrows(NullPointerException.class, () -> STORE.findLocked(p.connection, null));
    assertThrows(NullPointerException.class, () -> STORE.insert(null, row(0)));
    assertThrows(NullPointerException.class, () -> STORE.insert(p.connection, null));
    assertThrows(NullPointerException.class, () -> STORE.replace(null, row(0), row(1)));
    assertThrows(NullPointerException.class, () -> STORE.replace(p.connection, null, row(1)));
    assertThrows(NullPointerException.class, () -> STORE.replace(p.connection, row(0), null));
    assertThrows(NullPointerException.class, () -> STORE.delete(null, identity(), 0));
    assertThrows(NullPointerException.class, () -> STORE.delete(p.connection, null, 0));
    assertThrows(NullPointerException.class, () -> STORE.deleteByHash(null, HASH));
    assertThrows(NullPointerException.class, () -> STORE.deleteByHash(p.connection, null));
    for (String invalid :
        List.of("", "A".repeat(64), "a".repeat(63), "a".repeat(65), "z".repeat(64))) {
      assertThrows(IllegalArgumentException.class, () -> STORE.findLocked(p.connection, invalid));
      assertThrows(IllegalArgumentException.class, () -> STORE.deleteByHash(p.connection, invalid));
    }
    assertThrows(IllegalArgumentException.class, () -> STORE.insert(p.connection, row(1)));
    assertThrows(IllegalArgumentException.class, () -> STORE.replace(p.connection, row(0), row(0)));
    var different =
        new WebSessionRow(
            new SessionPayloadIdentity(new UUID(0, 82), HASH, CREATED),
            payload(),
            ACCESSED,
            EXPIRES,
            28800,
            1);
    assertThrows(
        IllegalArgumentException.class, () -> STORE.replace(p.connection, row(0), different));
    for (long invalid : new long[] {-1, 1000000000L}) {
      assertThrows(
          IllegalArgumentException.class, () -> STORE.delete(p.connection, identity(), invalid));
    }
    assertTrue(p.events.isEmpty());
  }

  @Test
  void absentFindUsesLiteralSqlAndClosesOnlyOwnedResources() {
    var p = new Port(Op.FIND);
    p.rowCount = 0;
    assertTrue(STORE.findLocked(p.connection, HASH).isEmpty());
    p.assertBinds(List.of(new Bind(SET_STRING, HASH)));
    assertEquals(
        List.of(
            AUTO,
            READ_ONLY,
            PREPARE,
            bindStage(SET_STRING, 1),
            QUERY,
            NEXT,
            CLOSE_RESULT,
            CLOSE_STATEMENT),
        p.events);
  }

  @Test
  void presentFindDetachesNineTypedColumnsAndCiphertextBeforeClosing() {
    var p = new Port(Op.FIND);
    p.columns.put(CREATED_COLUMN, CREATED.atOffset(ZoneOffset.ofHours(9)));
    var actual = STORE.findLocked(p.connection, HASH).orElseThrow();
    assertEquals(ID, actual.identity().id());
    assertEquals(HASH, actual.identity().sessionIdHash());
    assertEquals(CREATED, actual.identity().createdAt());
    assertEquals(KEY_VERSION, actual.payload().keyVersion());
    assertArrayEquals(new byte[64], actual.payload().ciphertext());
    assertEquals(ACCESSED, actual.lastAccessedAt());
    assertEquals(EXPIRES, actual.expiresAt());
    assertEquals(28800, actual.maxInactiveSeconds());
    assertEquals(0, actual.version());
    assertEquals(2, p.nextCalls);
    assertEquals(1, p.resultCloses);
    assertEquals(1, p.statementCloses);
    for (int length : new int[] {29, 16436}) {
      var boundary = new Port(Op.FIND);
      String key = "v".repeat(length == 29 ? 1 : 16);
      int idle = length == 29 ? 1 : 28800;
      long version = length == 29 ? 0L : 999999999L;
      boundary.columns.put(KEY_COLUMN, key);
      boundary.columns.put(BYTES_COLUMN, new byte[length]);
      boundary.columns.put(IDLE_COLUMN, idle);
      boundary.columns.put(VERSION_COLUMN, version);
      boundary.columns.put(ACCESSED_COLUMN, CREATED.atOffset(ZoneOffset.UTC));
      boundary.columns.put(EXPIRES_COLUMN, CREATED.atOffset(ZoneOffset.UTC));
      var found = STORE.findLocked(boundary.connection, HASH).orElseThrow();
      assertEquals(key, found.payload().keyVersion());
      assertArrayEquals(new byte[length], found.payload().ciphertext());
      assertEquals(idle, found.maxInactiveSeconds());
      assertEquals(version, found.version());
      assertEquals(CREATED, found.lastAccessedAt());
      assertEquals(CREATED, found.expiresAt());
      assertEquals(1, boundary.resultCloses);
      assertEquals(1, boundary.statementCloses);
    }
    ((byte[]) p.columns.get(BYTES_COLUMN))[0] = 99;
    assertArrayEquals(new byte[64], actual.payload().ciphertext());
    assertEquals(
        List.of(
            GET_OBJECT + ":" + ID_COLUMN,
            "getString:" + HASH_COLUMN,
            GET_OBJECT + ":" + CREATED_COLUMN,
            "getString:" + KEY_COLUMN,
            "getBytes:" + BYTES_COLUMN,
            GET_OBJECT + ":" + ACCESSED_COLUMN,
            GET_OBJECT + ":" + EXPIRES_COLUMN,
            GET_OBJECT + ":" + IDLE_COLUMN,
            GET_OBJECT + ":" + VERSION_COLUMN),
        p.reads);
  }

  @Test
  void duplicateRowsNeverEscapeAsAValidSessionProjection() {
    var p = new Port(Op.FIND);
    p.rowCount = 2;
    assertInvalid(() -> STORE.findLocked(p.connection, HASH));
    assertEquals(1, p.resultCloses);
    assertEquals(1, p.statementCloses);
    assertEquals(2, p.nextCalls);
  }

  @Test
  void eachNullOrMalformedDetachedColumnIsInvalidAfterCleanClose() {
    for (String column :
        List.of(
            ID_COLUMN,
            HASH_COLUMN,
            CREATED_COLUMN,
            KEY_COLUMN,
            BYTES_COLUMN,
            ACCESSED_COLUMN,
            EXPIRES_COLUMN,
            IDLE_COLUMN,
            VERSION_COLUMN)) {
      var p = new Port(Op.FIND);
      p.columns.put(column, null);
      assertInvalid(() -> STORE.findLocked(p.connection, HASH));
      assertEquals(1, p.resultCloses);
      assertEquals(1, p.statementCloses);
    }
    Map<String, List<Object>> invalid = new LinkedHashMap<>();
    invalid.put(HASH_COLUMN, List.of("A".repeat(64)));
    invalid.put(KEY_COLUMN, List.of("", "x".repeat(17)));
    invalid.put(BYTES_COLUMN, List.of(new byte[28], new byte[16437]));
    invalid.put(CREATED_COLUMN, List.of(CREATED.plusNanos(1).atOffset(ZoneOffset.UTC)));
    invalid.put(
        ACCESSED_COLUMN,
        List.of(
            CREATED.minusSeconds(1).atOffset(ZoneOffset.UTC),
            ACCESSED.plusNanos(1).atOffset(ZoneOffset.UTC)));
    invalid.put(
        EXPIRES_COLUMN,
        List.of(CREATED.atOffset(ZoneOffset.UTC), EXPIRES.plusNanos(1).atOffset(ZoneOffset.UTC)));
    invalid.put(IDLE_COLUMN, List.of(0, 28801));
    invalid.put(VERSION_COLUMN, List.of(-1L, 1000000000L));
    invalid.forEach(
        (column, values) ->
            values.forEach(
                value -> {
                  var p = new Port(Op.FIND);
                  p.columns.put(column, value);
                  assertInvalid(() -> STORE.findLocked(p.connection, HASH));
                  assertEquals(1, p.resultCloses);
                  assertEquals(1, p.statementCloses);
                }));
    var wrongType = new Port(Op.FIND);
    wrongType.columns.put(ID_COLUMN, DIAGNOSTIC);
    assertFixed(() -> STORE.findLocked(wrongType.connection, HASH));
  }

  @Test
  void malformedRowsWithCleanupFailureNeverGrantInvalidationClassification() {
    for (String stage : List.of(CLOSE_RESULT, CLOSE_STATEMENT)) {
      var p = new Port(Op.FIND);
      p.columns.put(ID_COLUMN, null);
      p.faults.put(stage, new SQLException(DIAGNOSTIC));
      assertFixed(() -> STORE.findLocked(p.connection, HASH));
      assertEquals(1, p.resultCloses);
      assertEquals(1, p.statementCloses);
    }
  }

  @Test
  void fatalMalformedCleanupAndGetterCauseKeepOriginalIdentityAfterClose() {
    for (boolean malformed : new boolean[] {false, true}) {
      var p = new Port(Op.FIND);
      if (malformed) p.columns.put(ID_COLUMN, null);
      var fatal = new AssertionError(DIAGNOSTIC);
      p.faults.put(CLOSE_RESULT, fatal);
      assertSame(
          fatal, assertThrows(AssertionError.class, () -> STORE.findLocked(p.connection, HASH)));
      assertEquals(1, p.resultCloses);
      assertEquals(1, p.statementCloses);
    }
    var p = new Port(Op.FIND);
    var fatal = new AssertionError(DIAGNOSTIC);
    p.faults.put(readStage(GET_OBJECT, ID_COLUMN), new SQLException(DIAGNOSTIC, fatal));
    assertSame(
        fatal, assertThrows(AssertionError.class, () -> STORE.findLocked(p.connection, HASH)));
    assertEquals(1, p.resultCloses);
    assertEquals(1, p.statementCloses);
  }

  @Test
  void insertHasNineLiteralBindsAndNeverUpdatesOrOwnsTransaction() {
    var p = new Port(Op.INSERT);
    STORE.insert(p.connection, row(0));
    p.assertBinds(insertBinds());
    assertEquals(1, p.updateCalls);
    assertEquals(1, p.statementCloses);
    assertEquals(0, p.resultCloses);
    for (int invalid : new int[] {-1, 0, 2}) {
      var failed = new Port(Op.INSERT);
      failed.updateCount = invalid;
      assertFixed(() -> STORE.insert(failed.connection, row(0)));
      assertEquals(1, failed.statementCloses);
    }
  }

  @Test
  void replaceHasExactTenCasBindsAndReturnsOnlyZeroOrOne() {
    for (int count : new int[] {0, 1}) {
      var p = new Port(Op.REPLACE);
      p.updateCount = count;
      assertEquals(count == 1, STORE.replace(p.connection, row(0), row(1)));
      p.assertBinds(replaceBinds());
      assertEquals(1, p.statementCloses);
    }
    for (int invalid : new int[] {-1, 2}) {
      var p = new Port(Op.REPLACE);
      p.updateCount = invalid;
      assertFixed(() -> STORE.replace(p.connection, row(0), row(1)));
      assertEquals(1, p.statementCloses);
    }
  }

  @Test
  void bothDeleteFormsRetainTheirDistinctIdentityPredicatesAndCountBounds() {
    for (Op op : List.of(Op.DELETE, Op.HASH_DELETE)) {
      for (int count : new int[] {0, 1, -1, 2}) {
        var p = new Port(op);
        p.updateCount = count;
        if (count < 0 || count > 1) assertFixed(() -> perform(op, p));
        else assertEquals(count == 1, perform(op, p));
        p.assertBinds(op == Op.DELETE ? deleteBinds() : List.of(new Bind(SET_STRING, HASH)));
        assertEquals(1, p.statementCloses);
        assertEquals(0, p.resultCloses);
      }
    }
  }

  @Test
  void transactionAndMissingJdbcObjectsFailBeforeUnownedEffects() {
    for (Op op : Op.values()) {
      var auto = new Port(op);
      auto.autoCommit = true;
      assertFixed(() -> perform(op, auto));
      assertEquals(List.of(AUTO), auto.events);
      var readonly = new Port(op);
      readonly.readOnly = true;
      assertFixed(() -> perform(op, readonly));
      assertEquals(List.of(AUTO, READ_ONLY), readonly.events);
      var noStatement = new Port(op);
      noStatement.statementMissing = true;
      assertFixed(() -> perform(op, noStatement));
      assertEquals(0, noStatement.statementCloses);
    }
    var noResult = new Port(Op.FIND);
    noResult.resultMissing = true;
    assertFixed(() -> STORE.findLocked(noResult.connection, HASH));
    assertEquals(0, noResult.resultCloses);
    assertEquals(1, noResult.statementCloses);
  }

  @Test
  void everyRequiredJdbcStageFaultIsFixedAndCreatedResourcesStillClose() {
    for (Op op : Op.values()) {
      var stages = new ArrayList<>(List.of(AUTO, READ_ONLY, PREPARE));
      List<Bind> binds = expectedBinds(op);
      for (int i = 0; i < binds.size(); i++) stages.add(bindStage(binds.get(i).method(), i + 1));
      stages.add(op == Op.FIND ? QUERY : UPDATE);
      stages.add(CLOSE_STATEMENT);
      if (op == Op.FIND) {
        stages.add(NEXT);
        stages.add(CLOSE_RESULT);
        for (String name :
            List.of(
                ID_COLUMN,
                CREATED_COLUMN,
                ACCESSED_COLUMN,
                EXPIRES_COLUMN,
                IDLE_COLUMN,
                VERSION_COLUMN)) stages.add(readStage(GET_OBJECT, name));
        for (String name : List.of(HASH_COLUMN, KEY_COLUMN))
          stages.add(readStage(GET_STRING, name));
        stages.add(readStage(GET_BYTES, BYTES_COLUMN));
      }
      for (String stage : stages) {
        var p = new Port(op);
        p.faults.put(stage, new SQLException(DIAGNOSTIC));
        assertFixed(() -> perform(op, p));
        assertEquals(1, p.events.stream().filter(stage::equals).count());
        assertEquals(
            p.events.contains(PREPARE) && !stage.equals(PREPARE) ? 1 : 0, p.statementCloses);
        assertEquals(
            op == Op.FIND && p.events.contains(QUERY) && !stage.equals(QUERY) ? 1 : 0,
            p.resultCloses);
      }
    }
  }

  @Test
  void directAndNestedFatalPrioritySurvivesMultipleOwnedCleanupFailures() {
    for (boolean direct : new boolean[] {false, true}) {
      var p = new Port(Op.FIND);
      var first = new AssertionError("public primary fatal");
      var later = new AssertionError("public cleanup fatal");
      p.faults.put(NEXT, direct ? first : new SQLException(DIAGNOSTIC, first));
      p.faults.put(CLOSE_RESULT, later);
      p.faults.put(CLOSE_STATEMENT, new SQLException(DIAGNOSTIC));
      assertSame(
          first, assertThrows(AssertionError.class, () -> STORE.findLocked(p.connection, HASH)));
      assertEquals(1, p.resultCloses);
      assertEquals(1, p.statementCloses);
    }
    for (Op op : List.of(Op.INSERT, Op.REPLACE, Op.DELETE, Op.HASH_DELETE)) {
      var p = new Port(op);
      var fatal = new AssertionError(DIAGNOSTIC);
      p.faults.put(UPDATE, new SQLException(DIAGNOSTIC));
      p.faults.put(CLOSE_STATEMENT, fatal);
      assertSame(fatal, assertThrows(AssertionError.class, () -> perform(op, p)));
      assertEquals(1, p.statementCloses);
    }
  }

  @Test
  void offsetDateTimeRangeFailureIsFixedAfterOwnedStatementClose() {
    Instant far = Instant.parse("+1000000000-12-31T23:59:59.999999Z");
    var identity = new SessionPayloadIdentity(ID, HASH, far);
    var original = new WebSessionRow(identity, payload(), far, far, 1, 0);
    var replacement = new WebSessionRow(identity, payload(), far, far, 1, 1);
    for (Op op : List.of(Op.INSERT, Op.REPLACE, Op.DELETE)) {
      var p = new Port(op);
      assertFixed(
          () -> {
            if (op == Op.INSERT) STORE.insert(p.connection, original);
            else if (op == Op.REPLACE) STORE.replace(p.connection, original, replacement);
            else STORE.delete(p.connection, identity, 0);
          });
      assertEquals(1, p.statementCloses);
    }
  }

  @Test
  void independentConcurrentConnectionsNeverExchangeBindsOrRows() throws Exception {
    try (var executor = Executors.newFixedThreadPool(2)) {
      var futures = new ArrayList<java.util.concurrent.Future<?>>();
      for (Op op : List.of(Op.INSERT, Op.FIND))
        futures.add(
            executor.submit(
                () -> {
                  for (int i = 0; i < 25; i++) {
                    var p = new Port(op);
                    perform(op, p);
                    p.assertBinds(expectedBinds(op));
                    assertEquals(1, p.statementCloses);
                  }
                }));
      for (var future : futures) future.get(10, TimeUnit.SECONDS);
    }
  }

  private static SessionPayloadIdentity identity() {
    return new SessionPayloadIdentity(ID, HASH, CREATED);
  }

  private static EncryptedSessionPayload payload() {
    return new EncryptedSessionPayload(KEY_VERSION, new byte[64]);
  }

  private static WebSessionRow row(long version) {
    return new WebSessionRow(identity(), payload(), ACCESSED, EXPIRES, 28800, version);
  }

  private static String bindStage(String method, int index) {
    return "statement." + method + ":" + index;
  }

  private static String readStage(String method, String name) {
    return "result." + method + ":" + name;
  }

  private static List<Bind> insertBinds() {
    return List.of(
        new Bind(SET_OBJECT, ID),
        new Bind(SET_STRING, HASH),
        new Bind(SET_BYTES, new byte[64]),
        new Bind(SET_STRING, KEY_VERSION),
        new Bind(SET_OBJECT, CREATED.atOffset(ZoneOffset.UTC)),
        new Bind(SET_OBJECT, ACCESSED.atOffset(ZoneOffset.UTC)),
        new Bind(SET_OBJECT, EXPIRES.atOffset(ZoneOffset.UTC)),
        new Bind(SET_INT, 28800),
        new Bind(SET_LONG, 0L));
  }

  private static List<Bind> replaceBinds() {
    return List.of(
        new Bind(SET_BYTES, new byte[64]),
        new Bind(SET_STRING, KEY_VERSION),
        new Bind(SET_OBJECT, ACCESSED.atOffset(ZoneOffset.UTC)),
        new Bind(SET_OBJECT, EXPIRES.atOffset(ZoneOffset.UTC)),
        new Bind(SET_INT, 28800),
        new Bind(SET_LONG, 1L),
        new Bind(SET_OBJECT, ID),
        new Bind(SET_STRING, HASH),
        new Bind(SET_OBJECT, CREATED.atOffset(ZoneOffset.UTC)),
        new Bind(SET_LONG, 0L));
  }

  private static List<Bind> deleteBinds() {
    return List.of(
        new Bind(SET_OBJECT, ID),
        new Bind(SET_STRING, HASH),
        new Bind(SET_OBJECT, CREATED.atOffset(ZoneOffset.UTC)),
        new Bind(SET_LONG, 0L));
  }

  private static List<Bind> expectedBinds(Op op) {
    return switch (op) {
      case FIND, HASH_DELETE -> List.of(new Bind(SET_STRING, HASH));
      case INSERT -> insertBinds();
      case REPLACE -> replaceBinds();
      case DELETE -> deleteBinds();
    };
  }

  private static @Nullable Object perform(Op op, Port p) {
    return switch (op) {
      case FIND -> STORE.findLocked(p.connection, HASH);
      case INSERT -> {
        STORE.insert(p.connection, row(0));
        yield null;
      }
      case REPLACE -> STORE.replace(p.connection, row(0), row(1));
      case DELETE -> STORE.delete(p.connection, identity(), 0);
      case HASH_DELETE -> STORE.deleteByHash(p.connection, HASH);
    };
  }

  private static void assertFixed(Runnable operation) {
    var x = assertThrows(SessionStoreException.class, operation::run);
    assertEquals(SessionStoreException.class, x.getClass());
    assertEquals(FIXED, x.getMessage());
    assertNull(x.getCause());
    assertEquals(0, x.getSuppressed().length);
  }

  private static void assertInvalid(Runnable operation) {
    var x = assertThrows(InvalidSessionRowException.class, operation::run);
    assertEquals(FIXED, x.getMessage());
    assertNull(x.getCause());
    assertEquals(0, x.getSuppressed().length);
  }

  private enum Op {
    FIND,
    INSERT,
    REPLACE,
    DELETE,
    HASH_DELETE
  }

  private record Bind(String method, Object value) {}

  private static final class Port {
    final Op op;
    final List<String> events = new ArrayList<>();
    final List<String> reads = new ArrayList<>();
    final Map<String, Throwable> faults = new HashMap<>();
    final Map<Integer, Bind> actualBinds = new LinkedHashMap<>();
    final Map<String, @Nullable Object> columns = new HashMap<>();
    final Connection connection;
    final PreparedStatement statement;
    final ResultSet result;
    boolean autoCommit;
    boolean readOnly;
    boolean statementMissing;
    boolean resultMissing;
    int updateCount = 1;
    int rowCount = 1;
    int nextCalls;
    int resultCloses;
    int statementCloses;
    int updateCalls;

    Port(Op op) {
      this.op = op;
      columns.put(ID_COLUMN, ID);
      columns.put(HASH_COLUMN, HASH);
      columns.put(KEY_COLUMN, KEY_VERSION);
      columns.put(BYTES_COLUMN, new byte[64]);
      columns.put(CREATED_COLUMN, CREATED.atOffset(ZoneOffset.UTC));
      columns.put(ACCESSED_COLUMN, ACCESSED.atOffset(ZoneOffset.UTC));
      columns.put(EXPIRES_COLUMN, EXPIRES.atOffset(ZoneOffset.UTC));
      columns.put(IDLE_COLUMN, 28800);
      columns.put(VERSION_COLUMN, 0L);
      connection =
          (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  handler("connection"));
      statement =
          (PreparedStatement)
              Proxy.newProxyInstance(
                  PreparedStatement.class.getClassLoader(),
                  new Class<?>[] {PreparedStatement.class},
                  handler("statement"));
      result =
          (ResultSet)
              Proxy.newProxyInstance(
                  ResultSet.class.getClassLoader(),
                  new Class<?>[] {ResultSet.class},
                  handler("result"));
    }

    void assertBinds(List<Bind> expected) {
      assertEquals(expected.size(), actualBinds.size());
      for (int i = 0; i < expected.size(); i++) {
        Bind a = actualBinds.get(i + 1);
        Bind e = expected.get(i);
        assertEquals(e.method(), a.method());
        if (e.value() instanceof byte[] bytes) assertArrayEquals(bytes, (byte[]) a.value());
        else assertEquals(e.value(), a.value());
      }
    }

    private InvocationHandler handler(String target) {
      return (proxy, method, args) -> {
        if (method.getDeclaringClass() == Object.class)
          return switch (method.getName()) {
            case "toString" -> "own-jdbc-port";
            case "hashCode" -> System.identityHashCode(proxy);
            case "equals" -> proxy == args[0];
            default -> throw new AssertionError("unexpected Object method");
          };
        String name = method.getName();
        if (target.equals("connection")) {
          String stage = "connection." + name;
          event(stage);
          return switch (name) {
            case "getAutoCommit" -> autoCommit;
            case "isReadOnly" -> readOnly;
            case "prepareStatement" -> {
              assertEquals(
                  switch (op) {
                    case FIND -> SELECT_SQL;
                    case INSERT -> INSERT_SQL;
                    case REPLACE -> UPDATE_SQL;
                    case DELETE -> DELETE_SQL;
                    case HASH_DELETE -> HASH_DELETE_SQL;
                  },
                  args[0]);
              yield statementMissing ? null : statement;
            }
            default -> throw new AssertionError("borrowed connection mutation/lifecycle forbidden");
          };
        }
        if (target.equals("statement")) {
          if (name.equals("close")) {
            statementCloses++;
            event(CLOSE_STATEMENT);
            return null;
          }
          if (name.startsWith("set")) {
            int index = (Integer) args[0];
            event(bindStage(name, index));
            assertNull(actualBinds.put(index, new Bind(name, args[1])));
            return null;
          }
          if (name.equals("executeUpdate")) {
            updateCalls++;
            event(UPDATE);
            return updateCount;
          }
          if (name.equals("executeQuery")) {
            event(QUERY);
            return resultMissing ? null : result;
          }
          throw new AssertionError("unexpected statement callback");
        }
        if (name.equals("close")) {
          resultCloses++;
          event(CLOSE_RESULT);
          return null;
        }
        if (name.equals("next")) {
          event(NEXT);
          int cursor = nextCalls;
          nextCalls++;
          return cursor < rowCount;
        }
        if (List.of(GET_OBJECT, GET_STRING, GET_BYTES).contains(name)) {
          String column = (String) args[0];
          event(readStage(name, column));
          reads.add(name + ":" + column);
          if (name.equals(GET_OBJECT)) {
            Class<?> type =
                switch (column) {
                  case ID_COLUMN -> UUID.class;
                  case CREATED_COLUMN, ACCESSED_COLUMN, EXPIRES_COLUMN -> OffsetDateTime.class;
                  case IDLE_COLUMN -> Integer.class;
                  case VERSION_COLUMN -> Long.class;
                  default -> throw new AssertionError("unexpected typed column");
                };
            assertEquals(type, args[1]);
          }
          assertTrue(columns.containsKey(column));
          return columns.get(column);
        }
        throw new AssertionError("unexpected result callback");
      };
    }

    private void event(String stage) throws Throwable {
      events.add(stage);
      Throwable failure = faults.get(stage);
      if (failure != null) throw failure;
    }
  }
}
