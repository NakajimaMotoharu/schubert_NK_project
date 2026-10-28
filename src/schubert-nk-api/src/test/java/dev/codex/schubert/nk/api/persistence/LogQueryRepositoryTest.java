package dev.codex.schubert.nk.api.persistence;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.log.LogRecord;
import dev.codex.schubert.nk.protocol.layout.log.LogSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.ElapsedMilliseconds;
import dev.codex.schubert.nk.protocol.layout.semantic.LogLevel;
import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
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
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** UI235 fixed offsets and actual PostgreSQL projection, SSC-036/PT-ADM-055..060. */
class LogQueryRepositoryTest {
  private static final String FIXTURE_TOTAL_714BDB4B = "total";
  private static final String FIXTURE_PAGES_41A6094E = "pages";
  private static final String FIXTURE_EFFECTIVE_392A9D00 = "effective";
  @TempDir static Path root;
  static ApiLogDatabaseFixture database;
  static final Instant NOW = Instant.parse("2026-09-08T00:00:00Z");
  static final AuthenticatedActor ADMIN = new AuthenticatedActor(1, "admin", Role.ADMIN);
  static final LogQueryRepository QUERIES = new LogQueryRepository();

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @Test
  void adm055PagesAndEveryFilterMatchIndependentRows() throws Exception {
    for (int total : new int[] {0, 1, 100, 101, 201}) {
      seed(total);
      for (int requested : new int[] {1, 2, 3, 999999})
        try (var c = read()) {
          var tracking = new UserQueryFaults();
          var result =
              QUERIES.search(
                  tracking.wrap(c),
                  ADMIN,
                  request(null, null, null, null, null, null, null, requested));
          int pages = Math.max(1, (total + 99) / 100);
          int page = Math.min(requested, pages);
          int count = Math.min(100, Math.max(0, total - (page - 1) * 100));
          assertEquals(
              new PagedResponseData(
                  page,
                  100,
                  total,
                  pages,
                  total == 0 ? 0 : (page - 1L) * 100 + 1,
                  Math.min(page * 100L, total)),
              result.data());
          assertEquals(count, result.records().size());
          for (int i = 0; i < count; i++)
            assertEquals(
                total - (page - 1L) * 100 - i,
                ((LogRecord) result.records().get(i)).logId().value());
          assertEquals(1, tracking.statements);
          assertEquals(1, tracking.resultCloses);
          assertEquals(1, tracking.statementCloses);
          assertTrue(c.isReadOnly());
          assertFalse(c.isClosed());
          assertFalse(c.getAutoCommit());
        }
    }
    seed(5);
    sql(
        "update schubert.app_logs set level=case id when 1 then 'TRACE' when 2 then 'DEBUG' when 3 then 'INFO' when 4 then 'WARN' else 'ERROR' end");
    try (var c = read()) {
      assertEquals(
          List.of(5L, 4L, 3L),
          ids(QUERIES.search(c, ADMIN, request(null, null, null, null, null, null, null, 1))));
      for (var level : LogLevel.values())
        assertEquals(
            List.of(level == LogLevel.INFO ? 3L : level == LogLevel.WARN ? 4L : 5L),
            ids(QUERIES.search(c, ADMIN, request(null, null, null, null, level, null, null, 1))));
    }
    sql("update schubert.app_logs set level='DEBUG'");
    try (var c = read()) {
      assertTrue(
          QUERIES
              .search(c, ADMIN, request(null, null, null, null, null, null, null, 1))
              .records()
              .isEmpty());
    }
    assertEquals(5, count());
    seed(3);
    sql(
        "update schubert.app_logs set message='A_%é',action='Exact',category='SECURITY',request_uri='/a_%',details='{\"marker\":\"needle\"}'::jsonb where id=2");
    for (var filter :
        List.of(
            request("_%é", null, null, null, null, null, null, 1),
            request("needle", null, null, null, null, null, null, 1),
            request(null, LogType.SECURITY, null, null, null, null, null, 1),
            request(null, null, "Exact", null, null, null, null, 1),
            request(null, null, null, "_%", null, null, null, 1),
            request(
                " A_%e\u0301", LogType.SECURITY, " Exact", " /a_%", LogLevel.INFO, null, null, 1)))
      try (var c = read()) {
        assertEquals(List.of(2L), ids(QUERIES.search(c, ADMIN, filter)));
      }
    for (String keyword : List.of("' OR 1=1 --", "\\", "missing"))
      try (var c = read()) {
        assertTrue(
            QUERIES
                .search(c, ADMIN, request(keyword, null, null, null, null, null, null, 1))
                .records()
                .isEmpty());
      }
    try (var c = read()) {
      assertEquals(
          3,
          QUERIES
              .search(c, ADMIN, request("", null, "", "", null, null, null, 1))
              .records()
              .size());
      for (String text : List.of("keyword ", "   "))
        assertThrows(
            IllegalArgumentException.class,
            () -> QUERIES.search(c, ADMIN, request(text, null, null, null, null, null, null, 1)));
    }
  }

  @Test
  void adm056ProjectionMatchesLiteralLogWireOffsets() throws Exception {
    seed(1);
    try (var c = read()) {
      var value = QUERIES.search(c, ADMIN, request(null, null, null, null, null, null, null, 1));
      assertArrayEquals(
          golden(1, false),
          PayloadCodec.standard()
              .encode(PayloadTypeCatalog.encode(value), false)
              .copyRecords()
              .getFirst());
    }
    sql(
        "update schubert.app_logs set logged_at='2026-09-08T00:00:00.123456Z',request_id='00000000-0000-0000-0000-000000000001',message_id='00000000-0000-0000-0000-000000000002',correlation_id='00000000-0000-0000-0000-000000000003',http_method='GET',request_uri='/safe',status_code=200,duration_ms=0,remote_address='2001:db8::1',details='{\"count\":1}'::jsonb");
    try (var c = read()) {
      var result = QUERIES.search(c, ADMIN, request(null, null, null, null, null, null, null, 1));
      assertArrayEquals(
          golden(1, true),
          PayloadCodec.standard()
              .encode(PayloadTypeCatalog.encode(result), false)
              .copyRecords()
              .getFirst());
      var row = (LogRecord) result.records().getFirst();
      assertEquals(Optional.of(new ElapsedMilliseconds(0)), row.elapsedMs());
      assertEquals(Instant.parse("2026-09-08T00:00:00.123Z"), row.occurredAt());
    }
  }

  @Test
  void adm057DateBoundsAndOptionalEndpointsAreExact() throws Exception {
    seed(3);
    sql(
        "update schubert.app_logs set logged_at=case id when 1 then '2026-09-08T00:00:00Z'::timestamptz when 2 then '2026-09-08T00:00:00.000001Z'::timestamptz else '2026-09-08T00:00:00.001Z'::timestamptz end");
    try (var c = read()) {
      assertEquals(
          List.of(1L),
          ids(QUERIES.search(c, ADMIN, request(null, null, null, null, null, NOW, NOW, 1))));
      assertEquals(
          List.of(3L, 2L, 1L),
          ids(
              QUERIES.search(
                  c, ADMIN, request(null, null, null, null, null, NOW, NOW.plusMillis(1), 1))));
      assertEquals(
          List.of(3L),
          ids(
              QUERIES.search(
                  c, ADMIN, request(null, null, null, null, null, NOW.plusMillis(1), null, 1))));
      assertEquals(
          List.of(1L),
          ids(QUERIES.search(c, ADMIN, request(null, null, null, null, null, null, NOW, 1))));
      assertEquals(
          List.of(3L, 2L, 1L),
          ids(
              QUERIES.search(
                  c,
                  ADMIN,
                  request(null, null, null, null, null, NOW, NOW.plusSeconds(31 * 86400L), 1))));
      for (var bad :
          List.of(
              request(null, null, null, null, null, NOW, NOW.minusMillis(1), 1),
              request(
                  null, null, null, null, null, NOW, NOW.plusSeconds(31 * 86400L).plusMillis(1), 1),
              request(null, null, null, null, null, NOW.plusNanos(1), null, 1)))
        assertThrows(IllegalArgumentException.class, () -> QUERIES.search(c, ADMIN, bad));
    }
    assertEquals(3, count());
  }

  @Test
  void adm058NullRoleTransactionAndCapacityFailClosed() throws Exception {
    seed(101);
    var request = request(null, null, null, null, null, null, null, 1);
    try (var c = read()) {
      assertThrows(NullPointerException.class, () -> QUERIES.search(null, ADMIN, request));
      assertThrows(NullPointerException.class, () -> QUERIES.search(c, null, request));
      assertThrows(NullPointerException.class, () -> QUERIES.search(c, ADMIN, null));
      assertThrows(
          dev.codex.schubert.nk.api.security.AuthorizationException.class,
          () -> QUERIES.search(c, new AuthenticatedActor(2, "user", Role.USER), request));
      assertThrows(
          IllegalArgumentException.class,
          () -> QUERIES.search(c, ADMIN, request(null, null, null, null, null, null, null, 0)));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              QUERIES.search(
                  c,
                  ADMIN,
                  new LogSearchRequestData(
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      Optional.empty(),
                      1,
                      99)));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              QUERIES.search(
                  c, ADMIN, request("é".repeat(129), null, null, null, null, null, null, 1)));
      for (boolean auto : List.of(false, true)) {
        var fault = new UserQueryFaults();
        fault.wrongAutoCommit = auto;
        fault.wrongReadOnly = !auto;
        temporary(() -> QUERIES.search(fault.wrap(c), ADMIN, request));
      }
      var max = new UserQueryFaults();
      max.columns.put(FIXTURE_TOTAL_714BDB4B, 99999900L);
      max.columns.put(FIXTURE_PAGES_41A6094E, 999999L);
      var result = QUERIES.search(max.wrap(c), ADMIN, request);
      assertEquals(new PagedResponseData(1, 100, 99999900L, 999999, 1, 100), result.data());
      for (String close : List.of("none", "resultClose", "statementClose")) {
        var fault = new UserQueryFaults();
        fault.columns.put(FIXTURE_TOTAL_714BDB4B, 99999901L);
        fault.fault = close;
        var error =
            assertThrows(
                LogQueryException.class, () -> QUERIES.search(fault.wrap(c), ADMIN, request));
        assertEquals(
            close.equals("none")
                ? dev.codex.schubert.nk.protocol.header.ResultCode.RESOURCE_LIMIT
                : dev.codex.schubert.nk.protocol.header.ResultCode.TEMPORARY_FAILURE,
            error.resultCode());
        redacted(error);
      }
      for (String field :
          List.of(
              FIXTURE_TOTAL_714BDB4B,
              FIXTURE_PAGES_41A6094E,
              FIXTURE_EFFECTIVE_392A9D00,
              "id",
              "logged_at",
              "category",
              "level",
              "action",
              "message",
              "details")) {
        var fault = new UserQueryFaults();
        fault.columns.put(field, null);
        temporary(() -> QUERIES.search(fault.wrap(c), ADMIN, request));
      }
      for (var replacement :
          Map.<String, Object>of(
                  "category",
                  "UNKNOWN",
                  "level",
                  "TRACE",
                  "status_code",
                  99,
                  "duration_ms",
                  2147483648L,
                  "id",
                  0L,
                  FIXTURE_PAGES_41A6094E,
                  2147483648L,
                  FIXTURE_EFFECTIVE_392A9D00,
                  2147483648L,
                  FIXTURE_TOTAL_714BDB4B,
                  -1L,
                  "message",
                  "")
              .entrySet()) {
        var fault = new UserQueryFaults();
        fault.columns.put(replacement.getKey(), replacement.getValue());
        temporary(() -> QUERIES.search(fault.wrap(c), ADMIN, request));
      }
      assertEquals(101, count());
    }
  }

  @Test
  void adm059JdbcAndResourceFailuresPreserveCallerState() throws Exception {
    seed(2);
    var request = request("message", LogType.ACTION, "TEST", null, LogLevel.INFO, NOW, NOW, 1);
    for (String point :
        List.of(
            "getAutoCommit",
            "isReadOnly",
            "prepareStatement",
            "setObject",
            "setInt",
            "executeQuery",
            "next",
            "getLong",
            "wasNull",
            "getObject",
            "getObject#2",
            "getString",
            "resultClose",
            "statementClose"))
      try (var c = read()) {
        var fault = new UserQueryFaults();
        fault.fault = point;
        temporary(() -> QUERIES.search(fault.wrap(c), ADMIN, request));
        assertFalse(c.isClosed());
        assertFalse(c.getAutoCommit());
        assertTrue(c.isReadOnly());
        c.rollback();
      }
    try (var c = read()) {
      var empty = new UserQueryFaults();
      empty.empty = true;
      temporary(() -> QUERIES.search(empty.wrap(c), ADMIN, request));
      for (String field :
          List.of(FIXTURE_TOTAL_714BDB4B, FIXTURE_PAGES_41A6094E, FIXTURE_EFFECTIVE_392A9D00)) {
        var fault = new UserQueryFaults();
        fault.columns.put(field, 7L);
        fault.changedRow = 2;
        temporary(() -> QUERIES.search(fault.wrap(c), ADMIN, request));
      }
      for (var entry :
          Map.of(
                  FIXTURE_PAGES_41A6094E,
                  2L,
                  FIXTURE_EFFECTIVE_392A9D00,
                  2L,
                  FIXTURE_TOTAL_714BDB4B,
                  3L)
              .entrySet()) {
        var fault = new UserQueryFaults();
        fault.columns.put(entry.getKey(), entry.getValue());
        temporary(() -> QUERIES.search(fault.wrap(c), ADMIN, request));
      }
      var partial = new UserQueryFaults();
      partial.columns.put("id", null);
      partial.changedRow = 2;
      temporary(() -> QUERIES.search(partial.wrap(c), ADMIN, request));
    }
    assertEquals(2, count());
  }

  @Test
  void adm060ConcurrentReadsDoNotBlockOrShareResults() throws Exception {
    seed(201);
    try (var writer = database.transaction();
        var statement = writer.createStatement();
        var locked =
            statement.executeQuery("select id from schubert.app_logs order by id for update");
        var pool = java.util.concurrent.Executors.newFixedThreadPool(10)) {
      int locks = 0;
      while (locked.next()) locks++;
      assertEquals(201, locks);
      var futures = new ArrayList<java.util.concurrent.Future<Void>>();
      for (int i = 1; i <= 100; i++) {
        int page = i % 3 + 1;
        futures.add(
            pool.submit(
                () -> {
                  try (var c = read()) {
                    var tracking = new UserQueryFaults();
                    var result =
                        QUERIES.search(
                            tracking.wrap(c),
                            ADMIN,
                            request(null, null, null, null, null, null, null, page));
                    assertEquals(page, ((PagedResponseData) result.data()).effectivePage());
                    assertEquals(201, ((PagedResponseData) result.data()).totalCount());
                    assertEquals(
                        201 - (page - 1L) * 100,
                        ((LogRecord) result.records().getFirst()).logId().value());
                    assertEquals(page == 3 ? 1 : 100, result.records().size());
                    assertEquals(1, tracking.statements);
                    assertTrue(c.isReadOnly());
                  }
                  return null;
                }));
      }
      for (var future : futures) future.get(20, java.util.concurrent.TimeUnit.SECONDS);
      assertEquals(201, count());
      writer.rollback();
    }
  }

  static void temporary(org.junit.jupiter.api.function.Executable action) {
    var error = assertThrows(LogQueryException.class, action);
    assertEquals(
        dev.codex.schubert.nk.protocol.header.ResultCode.TEMPORARY_FAILURE, error.resultCode());
    redacted(error);
  }

  static void redacted(LogQueryException error) {
    assertEquals("log query is unavailable", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  static LogSearchRequestData request(
      String keyword,
      LogType type,
      String action,
      String path,
      LogLevel level,
      Instant from,
      Instant to,
      int page) {
    return new LogSearchRequestData(
        Optional.ofNullable(keyword),
        Optional.ofNullable(type),
        Optional.ofNullable(action),
        Optional.ofNullable(path),
        Optional.ofNullable(level),
        Optional.ofNullable(from),
        Optional.ofNullable(to),
        page,
        100);
  }

  static Connection read() throws SQLException {
    var c = database.transaction();
    c.setReadOnly(true);
    return c;
  }

  static void seed(int count) throws SQLException {
    try (var c = database.admin();
        var s = c.createStatement()) {
      s.execute("truncate schubert.app_logs restart identity");
    }
    try (var c = database.api();
        var s =
            c.prepareStatement(
                "insert into schubert.app_logs(id,logged_at,service,category,level,action,message) select i,'2026-09-08T00:00:00Z','API','ACTION','INFO','TEST','message '||i from generate_series(1,?)i")) {
      s.setInt(1, count);
      assertEquals(count, s.executeUpdate());
    }
  }

  static void sql(String sql) throws SQLException {
    try (var c = database.api();
        var s = c.createStatement()) {
      s.executeUpdate(sql);
    }
  }

  static long count() throws SQLException {
    try (var c = database.api();
        var s = c.createStatement();
        var r = s.executeQuery("select count(*) from schubert.app_logs")) {
      assertTrue(r.next());
      return r.getLong(1);
    }
  }

  static List<Long> ids(TypedPayloadValues values) {
    return values.records().stream().map(row -> ((LogRecord) row).logId().value()).toList();
  }

  static byte[] golden(long id, boolean optional) {
    byte[] data = new byte[2088];
    Arrays.fill(data, (byte) 32);
    put(data, 0, String.format(Locale.ROOT, "%012d", id));
    put(data, 12, optional ? "20260908090000123" : "20260908090000000");
    put(data, 29, "ACTION");
    put(data, 45, "INFO");
    put(data, 53, "TEST");
    put(data, 117, "message " + id);
    put(data, 1058, optional ? "{\"count\": 1}" : "{}");
    if (optional) {
      put(data, 629, "00000000-0000-0000-0000-000000000001");
      put(data, 665, "00000000-0000-0000-0000-000000000002");
      put(data, 701, "00000000-0000-0000-0000-000000000003");
      put(data, 737, "GET");
      put(data, 745, "/safe");
      put(data, 1001, "200");
      put(data, 1004, "0");
      put(data, 1013, "2001:db8::1");
    }
    return data;
  }

  static void put(byte[] data, int offset, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, data, offset, bytes.length);
  }
}
