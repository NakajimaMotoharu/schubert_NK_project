package dev.codex.schubert.nk.api.persistence;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.AuthorizationException;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.admin.UserRecord;
import dev.codex.schubert.nk.protocol.layout.admin.UserSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** NK-ADM-001; UI225/236 literal bytes and production PostgreSQL DDL. PT-ADM-001..007. */
class UserQueryRepositoryTest {
  @TempDir static Path root;
  static ApiLogDatabaseFixture database;
  static final Instant NOW = Instant.parse("2026-09-08T00:01:00Z");
  static final AuthenticatedActor ADMIN = new AuthenticatedActor(999, "operator", Role.ADMIN);
  static final UserQueryRepository QUERIES = new UserQueryRepository();

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @BeforeEach
  void clear() throws Exception {
    seed(0);
  }

  @Test
  void adm001SearchFiltersLiteralPrefixesAndStablePages() throws Exception {
    for (int count : new int[] {0, 1, 50, 51, 101}) {
      seed(count);
      for (int requested : new int[] {1, 2, 3, 999999}) {
        try (var c = read()) {
          var actual = QUERIES.search(c, ADMIN, request(null, null, null, requested), NOW);
          int pages = Math.max(1, (count + 49) / 50);
          int page = Math.min(requested, pages);
          int first = count == 0 ? 0 : (page - 1) * 50 + 1;
          int last = Math.min(page * 50, count);
          assertPage(actual, page, count, pages, first, last);
          assertEquals(count == 0 ? 0 : last - first + 1, actual.records().size());
          for (int i = first; i > 0 && i <= last; i++) {
            var row = (UserRecord) actual.records().get(i - first);
            assertArrayEquals(
                userBytes(i, String.format(Locale.ROOT, "u%03d", i), "USER", "ACTIVE"),
                PayloadCodec.standard().encodeRecord(new LayoutId("USRRSP01"), row.fields()));
          }
          assertFalse(c.isClosed());
          assertTrue(c.isReadOnly());
          assertFalse(c.getAutoCommit());
        }
      }
    }
    seed(6);
    String[] names = {"A_%", "a_x", "b%", "bq", "c\\q", "c'q"};
    try (var c = database.api();
        var s =
            c.prepareStatement(
                "update schubert.app_users set username=?,username_key=? where id=?")) {
      for (int i = 0; i < names.length; i++) {
        s.setString(1, names[i]);
        s.setString(2, names[i].toLowerCase(Locale.ROOT));
        s.setInt(3, i + 1);
        s.executeUpdate();
      }
    }
    for (var pair :
        Map.of(
                "a_",
                List.of(1L, 2L),
                "b%",
                List.of(3L),
                "c\\",
                List.of(5L),
                "c'",
                List.of(6L),
                "' OR 1=1 --",
                List.<Long>of())
            .entrySet()) {
      try (var c = read()) {
        assertEquals(
            pair.getValue(),
            ids(QUERIES.search(c, ADMIN, request(pair.getKey(), null, null, 1), NOW)));
      }
    }
    sql(
        "update schubert.app_users set username='équipe',username_key='équipe',role='ADMIN',status='DISABLED' where id=6");
    try (var c = read()) {
      assertEquals(
          List.of(6L),
          ids(
              QUERIES.search(
                  c, ADMIN, request("  e\u0301q  ", UserRole.ADMIN, UserState.DISABLED, 1), NOW)));
      assertEquals(
          List.of(),
          ids(QUERIES.search(c, ADMIN, request(null, UserRole.ADMIN, UserState.ACTIVE, 1), NOW)));
      assertEquals(
          6, QUERIES.search(c, ADMIN, request("   ", null, null, 1), NOW).records().size());
    }
  }

  @Test
  void adm002DetailProjectsActorsTimesAndActiveSessions() throws Exception {
    seed(2);
    try (var c = read()) {
      var value =
          QUERIES.detail(c, ADMIN, new UserDetailRequestData(new UserId(1)), NOW).orElseThrow();
      byte[] expected = detailBytes(1, "u001", "USER", "ACTIVE", 0, "SYSTEM", "SYSTEM");
      assertArrayEquals(expected, fixed(value).copyData());
      assertTrue(
          QUERIES.detail(c, ADMIN, new UserDetailRequestData(new UserId(99)), NOW).isEmpty());
      assertFalse(c.isClosed());
    }
    sql(
        "update schubert.app_users set created_by=2,updated_by=2,last_login_at='2026-09-08T00:00:59Z',locked_until='2026-09-08T00:00:59Z' where id=1");
    for (int i = 1; i <= 2; i++) {
      session(i, "2026-09-08T00:01:00.000001Z", false);
      try (var c = read()) {
        var value =
            QUERIES.detail(c, ADMIN, new UserDetailRequestData(new UserId(1)), NOW).orElseThrow();
        byte[] expected = detailBytes(1, "u001", "USER", "ACTIVE", Math.min(i, 2), "u002", "u002");
        put(expected, 89, "20260908090059000");
        put(expected, 106, "20260908090059000");
        assertArrayEquals(expected, fixed(value).copyData());
      }
    }
    session(3, "2026-09-08T00:01:00Z", false);
    session(4, "2026-09-08T00:00:59.999999Z", false);
    session(5, "2026-09-08T00:01:00.000001Z", true);
    try (var c = read()) {
      var data =
          (UserDetailResponseData)
              QUERIES
                  .detail(c, ADMIN, new UserDetailRequestData(new UserId(1)), NOW)
                  .orElseThrow()
                  .data();
      assertEquals(2, data.activeSessionCount());
      assertEquals(Optional.of(Instant.parse("2026-09-08T00:00:59Z")), data.lastLogin());
    }
  }

  @Test
  void bizUserTime001SubMillisecondDatabaseTimesProjectWithoutChangingSqlValues() throws Exception {
    seed(1);
    sql(
        "update schubert.app_users set password_changed_at='2026-09-08T00:01:00.123456Z',created_at='2026-09-08T00:00:59.999999Z',updated_at='2026-09-08T00:01:00.999999Z',last_login_at='2026-09-08T00:00:59.000001Z',locked_until='2026-09-08T00:02:00.000001Z' where id=1");
    try (var c = read()) {
      var detail =
          QUERIES.detail(c, ADMIN, new UserDetailRequestData(new UserId(1)), NOW).orElseThrow();
      byte[] expected = detailBytes(1, "u001", "USER", "LOCKED", 0, "SYSTEM", "SYSTEM");
      put(expected, 89, "20260908090200000");
      put(expected, 106, "20260908090059000");
      put(expected, 123, "20260908090100123");
      put(expected, 140, "20260908090059999");
      put(expected, 157, "20260908090100999");
      assertArrayEquals(expected, fixed(detail).copyData());
      var list = QUERIES.search(c, ADMIN, request(null, null, null, 1), NOW);
      assertEquals(1, list.records().size());
      var record = assertInstanceOf(UserRecord.class, list.records().getFirst());
      assertEquals(Optional.of(Instant.parse("2026-09-08T00:02:00Z")), record.lockedUntil());
      assertEquals(Optional.of(Instant.parse("2026-09-08T00:00:59Z")), record.lastLogin());
      assertEquals(Instant.parse("2026-09-08T00:00:59.999Z"), record.createdAt());
      assertEquals(Instant.parse("2026-09-08T00:01:00.999Z"), record.updatedAt());
    }
    try (var c = database.api();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select password_changed_at,created_at,updated_at,last_login_at,locked_until from schubert.app_users where id=1")) {
      assertTrue(r.next());
      assertEquals(
          Instant.parse("2026-09-08T00:01:00.123456Z"),
          r.getObject(1, java.time.OffsetDateTime.class).toInstant());
      assertEquals(
          Instant.parse("2026-09-08T00:00:59.999999Z"),
          r.getObject(2, java.time.OffsetDateTime.class).toInstant());
      assertEquals(
          Instant.parse("2026-09-08T00:01:00.999999Z"),
          r.getObject(3, java.time.OffsetDateTime.class).toInstant());
      assertEquals(
          Instant.parse("2026-09-08T00:00:59.000001Z"),
          r.getObject(4, java.time.OffsetDateTime.class).toInstant());
      assertEquals(
          Instant.parse("2026-09-08T00:02:00.000001Z"),
          r.getObject(5, java.time.OffsetDateTime.class).toInstant());
    }
  }

  @Test
  void adm003DisabledAndLockBoundariesUseOneFixedInstant() throws Exception {
    seed(1);
    sql("update schubert.app_users set locked_until='2026-09-08T00:01:00Z'");
    for (boolean disabled : List.of(false, true)) {
      sql("update schubert.app_users set status='" + (disabled ? "DISABLED" : "ACTIVE") + "'");
      for (Instant now : List.of(NOW.minusNanos(1000), NOW, NOW.plusNanos(1000))) {
        UserState expected =
            disabled ? UserState.DISABLED : now.isBefore(NOW) ? UserState.LOCKED : UserState.ACTIVE;
        try (var c = read()) {
          var list = QUERIES.search(c, ADMIN, request(null, null, null, 1), now);
          assertEquals(expected, ((UserRecord) list.records().getFirst()).state());
          var detail =
              (UserDetailResponseData)
                  QUERIES
                      .detail(c, ADMIN, new UserDetailRequestData(new UserId(1)), now)
                      .orElseThrow()
                      .data();
          assertEquals(expected, detail.state());
          assertEquals(Optional.of(NOW), detail.lockedUntil());
          for (UserState state : UserState.values()) {
            assertEquals(
                state == expected ? List.of(1L) : List.of(),
                ids(QUERIES.search(c, ADMIN, request(null, null, state, 1), now)));
          }
        }
      }
    }
    try (var c = database.api();
        var s = c.createStatement();
        var r = s.executeQuery("select locked_until,version from schubert.app_users where id=1")) {
      assertTrue(r.next());
      assertEquals(NOW, r.getObject(1, java.time.OffsetDateTime.class).toInstant());
      assertEquals(0, r.getLong(2));
    }
  }

  @Test
  void adm004AuthorizationNullAndInputContractsRejectBeforeSql() throws Exception {
    try (var c = read()) {
      var faults = new UserQueryFaults();
      Connection wrapped = faults.wrap(c);
      var query = request(null, null, null, 1);
      var target = new UserDetailRequestData(new UserId(1));
      var user = new AuthenticatedActor(1, "reader", Role.USER);
      for (Executable action :
          List.<Executable>of(
              () -> QUERIES.search(wrapped, user, query, NOW),
              () -> QUERIES.detail(wrapped, user, target, NOW))) {
        assertEquals(
            ResultCode.FORBIDDEN, assertThrows(AuthorizationException.class, action).resultCode());
      }
      for (Executable action :
          List.<Executable>of(
              () -> QUERIES.search(null, ADMIN, query, NOW),
                  () -> QUERIES.search(wrapped, null, query, NOW),
              () -> QUERIES.search(wrapped, ADMIN, null, NOW),
                  () -> QUERIES.search(wrapped, ADMIN, query, null),
              () -> QUERIES.detail(null, ADMIN, target, NOW),
                  () -> QUERIES.detail(wrapped, null, target, NOW),
              () -> QUERIES.detail(wrapped, ADMIN, null, NOW),
                  () -> QUERIES.detail(wrapped, ADMIN, target, null))) {
        assertThrows(NullPointerException.class, action);
      }
      for (var invalid :
          List.of(
              request("界".repeat(22), null, null, 1),
              request("a\nb", null, null, 1),
              request(null, null, null, 0),
              new UserSearchRequestData(
                  Optional.empty(), Optional.empty(), Optional.empty(), 1, 49))) {
        assertThrows(
            IllegalArgumentException.class, () -> QUERIES.search(wrapped, ADMIN, invalid, NOW));
      }
      assertEquals(0, faults.statements);
      for (boolean auto : List.of(true, false)) {
        faults.wrongAutoCommit = auto;
        faults.wrongReadOnly = !auto;
        temporary(() -> QUERIES.search(wrapped, ADMIN, query, NOW));
        temporary(() -> QUERIES.detail(wrapped, ADMIN, target, NOW));
      }
      assertEquals(0, faults.statements);
      assertFalse(c.isClosed());
    }
  }

  @Test
  void adm005JdbcNullUnknownAndCloseFailuresNeverBecomeMissing() throws Exception {
    seed(1);
    // BUG169/YKT130: both query entry points preserve the fixed infrastructure contract.
    for (Instant invalid : List.of(Instant.MIN, Instant.MAX))
      try (var c = read()) {
        temporary(() -> QUERIES.search(c, ADMIN, request(null, null, null, 1), invalid));
        temporary(
            () -> QUERIES.detail(c, ADMIN, new UserDetailRequestData(new UserId(1)), invalid));
        assertFalse(c.isClosed());
        c.rollback();
      }
    for (String point : List.of("setString", "getObject")) {
      try (var c = read()) {
        var fault = new UserQueryFaults();
        fault.fault = point;
        temporary(() -> QUERIES.search(fault.wrap(c), ADMIN, request("u", null, null, 1), NOW));
        assertFalse(c.isClosed());
      }
    }
    for (String point : List.of("resultClose", "statementClose")) {
      try (var c = read()) {
        var fault = new UserQueryFaults();
        fault.fault = point;
        temporary(
            () ->
                QUERIES.detail(
                    fault.wrap(c), ADMIN, new UserDetailRequestData(new UserId(99)), NOW));
        assertFalse(c.isClosed());
      }
    }
    for (boolean detail : List.of(false, true)) {
      for (String point :
          List.of(
              "getAutoCommit",
              "isReadOnly",
              "prepareStatement",
              "setObject",
              detail ? "setLong" : "setInt",
              "executeQuery",
              "next",
              "getLong",
              "getString",
              "getObject",
              "wasNull",
              "resultClose",
              "statementClose")) {
        try (var c = read()) {
          var fault = new UserQueryFaults();
          fault.fault = point;
          temporary(() -> query(detail, fault.wrap(c)));
          assertFalse(c.isClosed());
        }
      }
      for (String column :
          List.of("id", "username", "role", "state", "created_at", "updated_at", "version")) {
        try (var c = read()) {
          var fault = new UserQueryFaults();
          fault.columns.put(column, null);
          temporary(() -> query(detail, fault.wrap(c)));
          assertEquals(1, fault.resultCloses);
          assertEquals(1, fault.statementCloses);
          assertFalse(c.isClosed());
        }
      }
      for (var change :
          Map.<String, Object>of(
                  "role",
                  "OTHER",
                  "state",
                  "OTHER",
                  "username",
                  "\n",
                  "id",
                  0L,
                  "version",
                  1_000_000_000L,
                  "created_at",
                  Instant.parse("+10000-01-01T00:00:00Z").atOffset(java.time.ZoneOffset.UTC))
              .entrySet()) {
        try (var c = read()) {
          var fault = new UserQueryFaults();
          fault.columns.put(change.getKey(), change.getValue());
          temporary(() -> query(detail, fault.wrap(c)));
          assertFalse(c.isClosed());
        }
      }
    }
    for (String column :
        List.of("password_changed_at", "active_sessions", "created_by_name", "updated_by_name")) {
      try (var c = read()) {
        var fault = new UserQueryFaults();
        fault.columns.put(column, null);
        temporary(() -> query(true, fault.wrap(c)));
      }
    }
    for (long active : new long[] {-1, 3, Integer.MAX_VALUE + 1L}) {
      try (var c = read()) {
        var fault = new UserQueryFaults();
        fault.columns.put("active_sessions", active);
        temporary(() -> query(true, fault.wrap(c)));
      }
    }
    try (var c = read()) {
      var duplicate = new UserQueryFaults();
      duplicate.duplicate = true;
      temporary(() -> query(true, duplicate.wrap(c)));
    }
    for (int i = 1; i <= 3; i++) session(i, "2026-09-08T00:02:00Z", false);
    try (var c = read()) {
      temporary(() -> query(true, c));
    }
  }

  @Test
  void adm006CapacityAndPageMetadataRejectTruncation() throws Exception {
    seed(51);
    try (var c = read()) {
      var fault = new UserQueryFaults();
      fault.columns.put("total", 49_999_950L);
      fault.columns.put("pages", 999999L);
      var value = (TypedPayloadValues) query(false, fault.wrap(c));
      assertPage(value, 1, 49_999_950, 999999, 1, 50);
      assertEquals(50, value.records().size());
    }
    for (String close : List.of("none", "resultClose", "statementClose")) {
      try (var c = read()) {
        var fault = new UserQueryFaults();
        fault.columns.put("total", 49_999_951L);
        fault.fault = close;
        var error = assertThrows(UserQueryException.class, () -> query(false, fault.wrap(c)));
        assertEquals(
            close.equals("none") ? ResultCode.RESOURCE_LIMIT : ResultCode.TEMPORARY_FAILURE,
            error.resultCode());
        redacted(error);
        assertFalse(c.isClosed());
      }
    }
    for (String field : List.of("total", "pages", "effective")) {
      for (Object value : Arrays.asList(null, -1L, Integer.MAX_VALUE + 1L)) {
        if (field.equals("total") && value != null && ((Long) value) > 0) continue;
        try (var c = read()) {
          var fault = new UserQueryFaults();
          fault.columns.put(field, value);
          temporary(() -> query(false, fault.wrap(c)));
        }
      }
      try (var c = read()) {
        var fault = new UserQueryFaults();
        fault.columns.put(field, 777L);
        fault.changedRow = 2;
        temporary(() -> query(false, fault.wrap(c)));
      }
    }
    try (var c = read()) {
      var fault = new UserQueryFaults();
      fault.empty = true;
      temporary(() -> query(false, fault.wrap(c)));
    }
    try (var c = read()) {
      var fault = new UserQueryFaults();
      fault.columns.put("id", null);
      fault.changedRow = 2;
      temporary(() -> query(false, fault.wrap(c)));
    }
  }

  @Test
  void adm007ConcurrentReadOnlyQueriesNeverMutateOrLock() throws Exception {
    seed(51);
    try (var writer = database.transaction();
        var lock = writer.createStatement();
        var rows = lock.executeQuery("select id from schubert.app_users order by id for update");
        var pool = Executors.newFixedThreadPool(10)) {
      int locked = 0;
      while (rows.next()) locked++;
      assertEquals(51, locked);
      CountDownLatch start = new CountDownLatch(1);
      List<Future<Void>> futures = new ArrayList<>();
      for (int i = 0; i < 100; i++)
        futures.add(
            pool.submit(
                () -> {
                  assertTrue(start.await(5, TimeUnit.SECONDS));
                  try (var c = read()) {
                    var tracking = new UserQueryFaults();
                    var wrapped = tracking.wrap(c);
                    var result = QUERIES.search(wrapped, ADMIN, request(null, null, null, 2), NOW);
                    assertPage(result, 2, 51, 2, 51, 51);
                    assertEquals(List.of(51L), ids(result));
                    assertEquals(1, tracking.statements);
                    var detail =
                        QUERIES
                            .detail(wrapped, ADMIN, new UserDetailRequestData(new UserId(1)), NOW)
                            .orElseThrow();
                    assertArrayEquals(
                        detailBytes(1, "u001", "USER", "ACTIVE", 0, "SYSTEM", "SYSTEM"),
                        fixed(detail).copyData());
                    assertEquals(2, tracking.statements);
                    assertEquals(2, tracking.statementCloses);
                    assertEquals(2, tracking.resultCloses);
                    assertFalse(c.isClosed());
                  }
                  return null;
                }));
      start.countDown();
      for (var future : futures) future.get(10, TimeUnit.SECONDS);
      writer.rollback();
    }
    try (var c = database.api();
        var s = c.createStatement();
        var rows =
            s.executeQuery(
                "select count(*),sum(version),count(*) filter(where status='ACTIVE' and role='USER' and locked_until is null and last_login_at is null and created_at=updated_at) from schubert.app_users")) {
      assertTrue(rows.next());
      assertEquals(51, rows.getInt(1));
      assertEquals(0, rows.getLong(2));
      assertEquals(51, rows.getInt(3));
    }
  }

  static Object query(boolean detail, Connection c) {
    return detail
        ? QUERIES.detail(c, ADMIN, new UserDetailRequestData(new UserId(1)), NOW)
        : QUERIES.search(c, ADMIN, request(null, null, null, 1), NOW);
  }

  static void temporary(Executable action) {
    var error = assertThrows(UserQueryException.class, action);
    assertEquals(ResultCode.TEMPORARY_FAILURE, error.resultCode());
    redacted(error);
  }

  static void redacted(UserQueryException error) {
    assertEquals("user query is unavailable", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  static UserSearchRequestData request(String prefix, UserRole role, UserState state, int page) {
    return new UserSearchRequestData(
        Optional.ofNullable(prefix),
        Optional.ofNullable(role),
        Optional.ofNullable(state),
        page,
        50);
  }

  static List<Long> ids(TypedPayloadValues result) {
    return result.records().stream().map(r -> ((UserRecord) r).userId().value()).toList();
  }

  static FixedPayload fixed(TypedPayloadValues value) {
    return PayloadCodec.standard().encode(PayloadTypeCatalog.encode(value), false);
  }

  static void assertPage(
      TypedPayloadValues actual, int page, int total, int pages, int first, int last) {
    byte[] expected = spaces(48);
    put(
        expected,
        0,
        String.format(Locale.ROOT, "%06d050%09d%06d%09d%09d", page, total, pages, first, last));
    assertArrayEquals(expected, fixed(actual).copyData());
    assertEquals(new PagedResponseData(page, 50, total, pages, first, last), actual.data());
  }

  static byte[] userBytes(long id, String name, String role, String state) {
    byte[] bytes = spaces(168);
    put(bytes, 0, String.format(Locale.ROOT, "%012d", id));
    put(bytes, 12, name);
    put(bytes, 76, role);
    put(bytes, 81, state);
    put(bytes, 123, "20260908090100000");
    put(bytes, 140, "20260908090100000");
    put(bytes, 157, "000000000");
    return bytes;
  }

  static byte[] detailBytes(
      long id,
      String name,
      String role,
      String state,
      int sessions,
      String createdBy,
      String updatedBy) {
    byte[] bytes = spaces(320);
    put(bytes, 0, String.format(Locale.ROOT, "%012d", id));
    put(bytes, 12, name);
    put(bytes, 76, role);
    put(bytes, 81, state);
    for (int offset : new int[] {123, 140, 157}) put(bytes, offset, "20260908090100000");
    put(bytes, 174, String.format(Locale.ROOT, "%03d", sessions));
    put(bytes, 177, "000000000");
    put(bytes, 186, createdBy);
    put(bytes, 250, updatedBy);
    return bytes;
  }

  static byte[] spaces(int length) {
    byte[] bytes = new byte[length];
    Arrays.fill(bytes, (byte) 32);
    return bytes;
  }

  static void put(byte[] bytes, int offset, String value) {
    byte[] source = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(source, 0, bytes, offset, source.length);
  }

  static Connection read() throws SQLException {
    Connection c = database.transaction();
    c.setReadOnly(true);
    return c;
  }

  static void sql(String sql) throws SQLException {
    try (var c = database.api();
        var s = c.createStatement()) {
      s.execute(sql);
    }
  }

  static void seed(int count) throws SQLException {
    // Fixture reset alone uses the isolated test administrator; queries remain schubert_app.
    try (var c = database.admin();
        var s = c.createStatement()) {
      s.execute("truncate schubert.app_users cascade");
    }
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) select i,'u'||lpad(i::text,3,'0'),'u'||lpad(i::text,3,'0'),'unusable-test-hash','USER','ACTIVE','2026-09-08T00:01:00Z','2026-09-08T00:01:00Z','2026-09-08T00:01:00Z' from generate_series(1,"
            + count
            + ")i");
  }

  static void session(int id, String expires, boolean revoked) throws SQLException {
    try (var c = database.api();
        var s =
            c.prepareStatement(
                "insert into schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,revoked,revoked_at,revoke_reason,client_address,created_message_id) values (?,1,?,decode(repeat('00',29),'hex'),'test','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z',?,?,?,?,'127.0.0.1',?)")) {
      s.setObject(1, new UUID(0, id));
      s.setString(2, String.format(Locale.ROOT, "%064x", id));
      s.setObject(3, Instant.parse(expires).atOffset(java.time.ZoneOffset.UTC));
      s.setBoolean(4, revoked);
      s.setObject(5, revoked ? NOW.atOffset(java.time.ZoneOffset.UTC) : null);
      s.setString(6, revoked ? "ADMIN" : null);
      s.setObject(7, new UUID(1, id));
      s.executeUpdate();
    }
  }
}
