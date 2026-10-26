package dev.codex.schubert.nk.api.application.log;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.persistence.LogQueryRepository;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.AuthorizationException;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.log.LogRecord;
import dev.codex.schubert.nk.protocol.layout.log.LogSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.ElapsedMilliseconds;
import dev.codex.schubert.nk.protocol.layout.semantic.HttpStatusCode;
import dev.codex.schubert.nk.protocol.layout.semantic.LogId;
import dev.codex.schubert.nk.protocol.layout.semantic.LogLevel;
import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** NK-ADM-001/UI235/SS323332; PT-LOG-SQL001..008; spec079. Public JDBC interfaces, no backend. */
class LogSqlContractTest {
  private static final String COLUMN_TOTAL = "total";
  private static final String SEARCH_LAYOUT = "LGSREQ01";
  private static final String RESPONSE_LAYOUT = "LGSRSP01";
  private static final String CATEGORY = "SECURITY";
  private static final String LEVEL = "WARN";
  private static final String ACTION = "Read";
  private static final String MESSAGE = "safe event";
  private static final String DETAILS = "{\"count\":1}";
  private static final String METHOD = "GET";
  private static final String PATH = "/safe";
  private static final String ADDRESS = "2001:db8::1";
  private static final int OPTIONAL_MASKS = 128;
  private static final int PAGE_SIZE = 100;
  private static final int LAST_PAGE = 999999;
  private static final int TYPED_ARGUMENTS = 2;
  private static final Instant NOW = Instant.parse("2026-10-01T00:00:00.123Z");
  private static final AuthenticatedActor ADMIN = new AuthenticatedActor(8, "unit8", Role.ADMIN);
  private static final List<String> FILTERS =
      List.of("é_%\\", CATEGORY, ACTION, "/a_%\\", LEVEL, "20261001090000123", "20261001090001123");
  private static final int[] OFFSETS = {0, 256, 272, 336, 592, 600, 617};

  @Test
  void sql001EmptySearchRetainsRequestedPageAndStableSql() {
    var jdbc = new Jdbc(List.of(emptyRow()));
    var request = request(0, LAST_PAGE);
    var result = request.query(new LogQueryRepository(), jdbc.connection(), ADMIN);
    assertEquals(RESPONSE_LAYOUT, result.layoutId().value());
    assertEquals(new PagedResponseData(1, PAGE_SIZE, 0, 1, 0, 0), result.data());
    assertTrue(result.records().isEmpty());
    assertEquals(Map.of(1, LAST_PAGE), jdbc.parameters);
    assertDoesNotThrow(() -> request.validateResponse(result));
    try (var canonical = request.canonical(ADMIN)) {
      assertArrayEquals(
          "999999".getBytes(StandardCharsets.US_ASCII), canonical.fields().get(7).value());
    }
    commonSql(jdbc.sql);
    assertFalse(jdbc.sql.contains("category=?"));
    jdbc.assertReleased();
  }

  @Test
  void sql002AllFilterMasksBindLiteralWildcardsAndUtcBounds() {
    for (int mask = 0; mask < OPTIONAL_MASKS; mask++) {
      var jdbc = new Jdbc(List.of(emptyRow()));
      var request = request(mask, 1);
      var result = request.query(new LogQueryRepository(), jdbc.connection(), ADMIN);
      assertEquals(new PagedResponseData(1, PAGE_SIZE, 0, 1, 0, 0), result.data());
      List<Object> expected = new ArrayList<>();
      String keyword = "%é\\_\\%\\\\%";
      String path = "%/a\\_\\%\\\\%";
      if ((mask & 1) != 0) {
        expected.add(keyword);
        expected.add(keyword);
      }
      if ((mask & 2) != 0) expected.add(CATEGORY);
      if ((mask & 4) != 0) expected.add(ACTION);
      if ((mask & 8) != 0) expected.add(path);
      if ((mask & 16) != 0) expected.add(LEVEL);
      if ((mask & 32) != 0) expected.add(OffsetDateTime.parse("2026-10-01T00:00:00.123Z"));
      if ((mask & 64) != 0) expected.add(OffsetDateTime.parse("2026-10-01T00:00:01.123Z"));
      expected.add(1);
      assertEquals(expected.size(), jdbc.parameters.size());
      for (int i = 0; i < expected.size(); i++)
        assertEquals(expected.get(i), jdbc.parameters.get(i + 1));
      var fragments =
          List.of(
              "(message ilike ? escape '\\' or details::text ilike ? escape '\\')",
              "category=?",
              "action=?",
              "request_uri ilike ? escape '\\'",
              "level=?",
              "logged_at>=?",
              "logged_at<=?");
      for (int i = 0; i < fragments.size(); i++)
        assertEquals((mask & (1 << i)) != 0, jdbc.sql.contains(fragments.get(i)));
      assertFalse(jdbc.sql.contains("é"));
      commonSql(jdbc.sql);
      jdbc.assertReleased();
    }
  }

  @Test
  void sql003MinimalMappedRowKeepsOptionalAbsenceAndMilliseconds() {
    var jdbc = new Jdbc(List.of(logRow(false)));
    var result = request(0, 1).query(new LogQueryRepository(), jdbc.connection(), ADMIN);
    assertEquals(new PagedResponseData(1, PAGE_SIZE, 1, 1, 1, 1), result.data());
    assertEquals(List.of(expectedRecord(false, 3)), result.records());
    var actual = assertInstanceOf(LogRecord.class, result.records().getFirst());
    assertEquals(NOW, actual.occurredAt());
    assertEquals(Optional.empty(), actual.httpStatus());
    assertEquals(Optional.empty(), actual.elapsedMs());
    jdbc.assertReleased();
  }

  @Test
  void sql004FullMappedRowMatchesIndependentFixedWidthGolden() {
    var jdbc = new Jdbc(List.of(logRow(true)));
    var request = request(0, 1);
    var result = request.query(new LogQueryRepository(), jdbc.connection(), ADMIN);
    assertEquals(List.of(expectedRecord(true, 3)), result.records());
    assertDoesNotThrow(() -> request.validateResponse(result));
    byte[] golden = new byte[2088];
    Arrays.fill(golden, (byte) 32);
    put(golden, 0, "000000000003");
    put(golden, 12, "20261001090000123");
    put(golden, 29, CATEGORY);
    put(golden, 45, LEVEL);
    put(golden, 53, ACTION);
    put(golden, 117, MESSAGE);
    put(golden, 629, "00000000-0000-0000-0000-000000000001");
    put(golden, 665, "00000000-0000-0000-0000-000000000002");
    put(golden, 701, "00000000-0000-0000-0000-000000000003");
    put(golden, 737, METHOD);
    put(golden, 745, PATH);
    put(golden, 1001, "200");
    put(golden, 1004, "0");
    put(golden, 1013, ADDRESS);
    put(golden, 1058, DETAILS);
    assertArrayEquals(
        golden,
        PayloadCodec.standard()
            .encode(PayloadTypeCatalog.encode(result), false)
            .copyRecords()
            .getFirst());
    jdbc.assertReleased();
  }

  @Test
  void sql005FinalPageClampHasExactHundredRowBoundaries() {
    var row = logRow(false);
    row.put(COLUMN_TOTAL, 101L);
    row.put("pages", 2L);
    row.put("effective", 2L);
    row.put("id", 101L);
    var jdbc = new Jdbc(List.of(row));
    var request = request(0, LAST_PAGE);
    var result = request.query(new LogQueryRepository(), jdbc.connection(), ADMIN);
    assertEquals(new PagedResponseData(2, PAGE_SIZE, 101, 2, 101, 101), result.data());
    assertEquals(List.of(expectedRecord(false, 101)), result.records());
    assertDoesNotThrow(() -> request.validateResponse(result));
    assertEquals(Map.of(1, LAST_PAGE), jdbc.parameters);
    commonSql(jdbc.sql);
    jdbc.assertReleased();
  }

  @Test
  void sql006InvalidInputStopsBeforeBorrowedReadOnlyBlock() {
    var jdbc = new Jdbc(List.of(emptyRow()));
    var repository = new LogQueryRepository();
    for (var data :
        List.of(
            typed(0, PAGE_SIZE, Optional.empty(), Optional.empty()),
            typed(1, 99, Optional.empty(), Optional.empty()),
            typed(
                1,
                PAGE_SIZE,
                Optional.of(NOW),
                Optional.of(Instant.parse("2026-11-02T00:00:00.123Z"))))) {
      assertThrows(
          IllegalArgumentException.class, () -> repository.search(jdbc.connection(), ADMIN, data));
    }
    assertEquals(0, jdbc.connectionCalls);
    assertEquals(0, jdbc.prepares);
    assertTrue(jdbc.closed.isEmpty());
  }

  @Test
  void sql007UserRoleDeniedBeforeAnyJdbcMethod() {
    var jdbc = new Jdbc(List.of(emptyRow()));
    var actor = new AuthenticatedActor(9, "unit9", Role.USER);
    var failure =
        assertThrows(
            AuthorizationException.class,
            () -> request(0, 1).query(new LogQueryRepository(), jdbc.connection(), actor));
    assertEquals(dev.codex.schubert.nk.protocol.header.ResultCode.FORBIDDEN, failure.resultCode());
    assertEquals(0, jdbc.connectionCalls);
    assertEquals(0, jdbc.prepares);
    assertTrue(jdbc.closed.isEmpty());
  }

  @Test
  void sql008NullArgumentsStopWithoutInterfaceCalls() {
    var jdbc = new Jdbc(List.of(emptyRow()));
    var request = request(0, 1);
    var repository = new LogQueryRepository();
    var data = typed(1, PAGE_SIZE, Optional.empty(), Optional.empty());
    assertThrows(NullPointerException.class, () -> request.query(null, jdbc.connection(), ADMIN));
    assertThrows(NullPointerException.class, () -> request.query(repository, null, ADMIN));
    assertThrows(
        NullPointerException.class, () -> request.query(repository, jdbc.connection(), null));
    assertThrows(NullPointerException.class, () -> repository.search(null, ADMIN, data));
    assertThrows(
        NullPointerException.class, () -> repository.search(jdbc.connection(), null, data));
    assertThrows(
        NullPointerException.class, () -> repository.search(jdbc.connection(), ADMIN, null));
    assertEquals(0, jdbc.connectionCalls);
    assertEquals(0, jdbc.prepares);
    assertTrue(jdbc.closed.isEmpty());
  }

  @Test
  void sql009FullHundredRowPageKeepsDescendingIds() {
    var rows = new ArrayList<Map<String, @Nullable Object>>();
    var expected = new ArrayList<LogRecord>();
    for (long id = 100; id >= 1; id--) {
      var row = logRow(false);
      row.put(COLUMN_TOTAL, 100L);
      row.put("id", id);
      rows.add(row);
      expected.add(expectedRecord(false, id));
    }
    var jdbc = new Jdbc(rows);
    var request = request(0, LAST_PAGE);
    var result = request.query(new LogQueryRepository(), jdbc.connection(), ADMIN);
    assertEquals(new PagedResponseData(1, PAGE_SIZE, 100, 1, 1, 100), result.data());
    assertEquals(expected, result.records());
    assertDoesNotThrow(() -> request.validateResponse(result));
    assertEquals(Map.of(1, LAST_PAGE), jdbc.parameters);
    commonSql(jdbc.sql);
    jdbc.assertReleased();
  }

  private static LogSearchRequestData typed(
      int page, int size, Optional<Instant> from, Optional<Instant> to) {
    return new LogSearchRequestData(
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        from,
        to,
        page,
        size);
  }

  private static LogRecord expectedRecord(boolean full, long id) {
    return new LogRecord(
        new LogId(id),
        NOW,
        LogType.SECURITY,
        LogLevel.WARN,
        Optional.of(ACTION),
        MESSAGE,
        full
            ? Optional.of(UUID.fromString("00000000-0000-0000-0000-000000000001"))
            : Optional.empty(),
        full
            ? Optional.of(UUID.fromString("00000000-0000-0000-0000-000000000002"))
            : Optional.empty(),
        full
            ? Optional.of(UUID.fromString("00000000-0000-0000-0000-000000000003"))
            : Optional.empty(),
        full ? Optional.of(METHOD) : Optional.empty(),
        full ? Optional.of(PATH) : Optional.empty(),
        full ? Optional.of(new HttpStatusCode(200)) : Optional.empty(),
        full ? Optional.of(new ElapsedMilliseconds(0)) : Optional.empty(),
        full ? Optional.of(ADDRESS) : Optional.empty(),
        Optional.of(DETAILS));
  }

  private static void commonSql(String sql) {
    assertTrue(sql.contains("with filtered as materialized"));
    assertTrue(sql.contains("level in ('INFO','WARN','ERROR')"));
    assertTrue(sql.contains("totals as (select count(*) as total from filtered)"));
    assertTrue(sql.contains("greatest(1,(total+99)/100)"));
    assertTrue(sql.contains("limit 100 offset (p.effective-1)*100"));
    assertTrue(sql.contains("order by logged_at desc,id desc"));
    assertTrue(sql.contains("order by x.logged_at desc,x.id desc"));
    assertTrue(sql.contains("host(x.remote_address) as remote_address"));
    for (String forbidden :
        List.of("for update", "password_hash", "token_digest", "update schubert", "delete from"))
      assertFalse(sql.contains(forbidden));
  }

  private static Map<String, @Nullable Object> emptyRow() {
    var row = new HashMap<String, @Nullable Object>();
    row.put(COLUMN_TOTAL, 0L);
    row.put("pages", 1L);
    row.put("effective", 1L);
    row.put("id", null);
    return row;
  }

  private static Map<String, @Nullable Object> logRow(boolean full) {
    var row = emptyRow();
    row.put(COLUMN_TOTAL, 1L);
    row.put("id", 3L);
    row.put("logged_at", OffsetDateTime.parse("2026-10-01T00:00:00.123456Z"));
    row.put("category", CATEGORY);
    row.put("level", LEVEL);
    row.put("action", ACTION);
    row.put("message", MESSAGE);
    row.put("details", DETAILS);
    row.put("request_id", full ? UUID.fromString("00000000-0000-0000-0000-000000000001") : null);
    row.put("message_id", full ? UUID.fromString("00000000-0000-0000-0000-000000000002") : null);
    row.put(
        "correlation_id", full ? UUID.fromString("00000000-0000-0000-0000-000000000003") : null);
    row.put("http_method", full ? METHOD : null);
    row.put("request_uri", full ? PATH : null);
    row.put("status_code", full ? 200 : null);
    row.put("duration_ms", full ? 0L : null);
    row.put("remote_address", full ? ADDRESS : null);
    return row;
  }

  @FunctionalInterface
  private interface Call {
    @Nullable Object invoke(String method, Object[] arguments);
  }

  private static <T> T proxy(Class<T> type, Call call) {
    return type.cast(
        Proxy.newProxyInstance(
            LogSqlContractTest.class.getClassLoader(),
            new Class<?>[] {type},
            (self, method, arguments) ->
                call.invoke(method.getName(), arguments == null ? new Object[0] : arguments)));
  }

  private static final class Jdbc {
    private final List<Map<String, @Nullable Object>> rows;
    private final Map<Integer, Object> parameters = new HashMap<>();
    private final List<String> closed = new ArrayList<>();
    private String sql = "";
    private int connectionCalls;
    private int prepares;
    private int queries;
    private int cursor = -1;
    private boolean wasNull;

    Jdbc(List<Map<String, @Nullable Object>> rows) {
      this.rows = List.copyOf(rows);
    }

    Connection connection() {
      return proxy(
          Connection.class,
          (method, args) -> {
            connectionCalls++;
            return switch (method) {
              case "getAutoCommit" -> false;
              case "isReadOnly" -> true;
              case "prepareStatement" -> {
                prepares++;
                assertEquals(1, prepares);
                sql = ((String) args[0]).replaceAll("\\s+", " ");
                yield statement();
              }
              default ->
                  throw new AssertionError("borrowed connection action not permitted: " + method);
            };
          });
    }

    private PreparedStatement statement() {
      return proxy(
          PreparedStatement.class,
          (method, args) ->
              switch (method) {
                case "setObject", "setInt" -> {
                  assertNull(parameters.put((Integer) args[0], args[1]));
                  yield null;
                }
                case "executeQuery" -> {
                  queries++;
                  assertEquals(1, queries);
                  yield results();
                }
                case "close" -> {
                  closed.add("PS");
                  yield null;
                }
                default -> throw new AssertionError("unexpected statement method: " + method);
              });
    }

    private ResultSet results() {
      return proxy(
          ResultSet.class,
          (method, args) ->
              switch (method) {
                case "next" -> {
                  cursor++;
                  yield cursor < rows.size();
                }
                case "wasNull" -> wasNull;
                case "getLong" -> {
                  Object value = value((String) args[0]);
                  yield value == null ? 0L : ((Number) value).longValue();
                }
                case "getString" -> (String) value((String) args[0]);
                case "getObject" -> {
                  Object value = value((String) args[0]);
                  if (args.length == TYPED_ARGUMENTS && value != null)
                    assertTrue(((Class<?>) args[1]).isInstance(value));
                  yield value;
                }
                case "close" -> {
                  closed.add("RS");
                  yield null;
                }
                default -> throw new AssertionError("unexpected result method: " + method);
              });
    }

    private @Nullable Object value(String name) {
      assertTrue(cursor >= 0 && cursor < rows.size());
      var row = rows.get(cursor);
      assertTrue(row.containsKey(name), "explicit synthetic column required");
      Object value = row.get(name);
      wasNull = value == null;
      return value;
    }

    void assertReleased() {
      assertEquals(1, prepares);
      assertEquals(1, queries);
      assertEquals(3, connectionCalls);
      assertEquals(List.of("RS", "PS"), closed);
    }
  }

  private static LogRequest request(int mask, int page) {
    byte[] bytes = new byte[656];
    Arrays.fill(bytes, (byte) 32);
    for (int i = 0; i < OFFSETS.length; i++)
      if ((mask & (1 << i)) != 0) put(bytes, OFFSETS[i], FILTERS.get(i));
    put(bytes, 634, page == 1 ? "000001100" : "999999100");
    UUID id = new UUID(79, 1);
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(SEARCH_LAYOUT),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            id,
            id,
            NOW,
            Optional.of(AuthenticationContext.of("b".repeat(64))),
            256,
            bytes.length,
            0,
            0,
            256 + bytes.length,
            Optional.empty());
    return LogRequest.decode(new WireMessage<>(header, new FixedPayload(bytes, 0, List.of())));
  }

  private static void put(byte[] bytes, int offset, String value) {
    byte[] text = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(text, 0, bytes, offset, text.length);
  }
}
