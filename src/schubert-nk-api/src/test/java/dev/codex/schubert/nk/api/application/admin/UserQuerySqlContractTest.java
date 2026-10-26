package dev.codex.schubert.nk.api.application.admin;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.persistence.UserQueryRepository;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.AuthorizationException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.admin.UserRecord;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
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

/**
 * NK-ADM-001/UI225/236/SS323/332; PT-ADM-SQL001..008; specification NK-ADM077. JDK interface
 * proxies only; no driver, DB, error-graph fault injection or private reflection.
 */
class UserQuerySqlContractTest {
  private static final String COLUMN_TOTAL = "total";
  private static final String ROLE_USER = "USER";
  private static final String STATE_ACTIVE = "ACTIVE";
  private static final String STATE_LOCKED = "LOCKED";
  private static final String PAGE_ONE = "000001";
  private static final int TYPED_GETTER_ARGUMENTS = 2;
  private static final String SEARCH_LAYOUT = "USRREQ01";
  private static final String DETAIL_LAYOUT = "UDTREQ01";
  private static final Instant NOW = Instant.parse("2026-09-08T00:01:00Z");
  private static final OffsetDateTime UTC_NOW = OffsetDateTime.parse("2026-09-08T00:01:00Z");
  private static final Instant CREATED = Instant.parse("2026-01-01T00:00:00Z");
  private static final Instant UPDATED = Instant.parse("2026-09-01T00:00:00Z");
  private static final Instant LAST_LOGIN = Instant.parse("2026-09-07T00:00:00.123Z");
  private static final Instant LOCKED_UNTIL = Instant.parse("2026-09-09T00:00:00.456Z");
  private static final String USERNAME = "u3";
  private static final AuthenticatedActor ADMIN = new AuthenticatedActor(7, "operator", Role.ADMIN);

  @Test
  void sql001EmptySearchUsesOneReadOnlySnapshotAndRetainsOriginalPage() {
    var jdbc = new Jdbc(List.of(emptyRow()));
    var request = search("", "", "", "999999");
    var result =
        request.query(new UserQueryRepository(), jdbc.connection(), ADMIN, NOW).orElseThrow();
    assertEquals("USRRSP01", result.layoutId().value());
    assertEquals(new PagedResponseData(1, 50, 0, 1, 0, 0), result.data());
    assertTrue(result.records().isEmpty());
    assertDoesNotThrow(() -> request.validateResponse(result));
    assertEquals(Map.of(1, UTC_NOW, 2, 999999), jdbc.parameters);
    searchSql(jdbc.sql);
    assertFalse(jdbc.sql.contains("username ilike"));
    assertFalse(jdbc.sql.contains("role=?"));
    assertFalse(jdbc.sql.contains("state=?"));
    jdbc.assertReleased();
  }

  @Test
  void sql002PrefixNormalizationAndLiteralWildcardEscapingStayInBinds() {
    var jdbc = new Jdbc(List.of(emptyRow()));
    var request = search(" É_%\\ ", ROLE_USER, STATE_ACTIVE, PAGE_ONE);
    var result =
        request.query(new UserQueryRepository(), jdbc.connection(), ADMIN, NOW).orElseThrow();
    assertEquals(new PagedResponseData(1, 50, 0, 1, 0, 0), result.data());
    // UI literal: trim prefix, then quote underscore, percent and backslash, then append wildcard.
    String expectedPrefix = "É" + "\\_" + "\\%" + "\\\\" + "%";
    assertEquals(
        Map.of(1, UTC_NOW, 2, expectedPrefix, 3, ROLE_USER, 4, STATE_ACTIVE, 5, 1),
        jdbc.parameters);
    searchSql(jdbc.sql);
    assertTrue(jdbc.sql.contains("username ilike ? escape '\\'"));
    assertTrue(jdbc.sql.contains("role=? and state=?"));
    assertFalse(jdbc.sql.contains("É"));
    jdbc.assertReleased();
  }

  @Test
  void sql003OneMappedRowKeepsTypedColumnsAndMillisecondProjection() {
    var jdbc = new Jdbc(List.of(userRow(false)));
    var request = search("u", ROLE_USER, STATE_ACTIVE, PAGE_ONE);
    var result =
        request.query(new UserQueryRepository(), jdbc.connection(), ADMIN, NOW).orElseThrow();
    assertEquals(new PagedResponseData(1, 50, 1, 1, 1, 1), result.data());
    assertEquals(1, result.records().size());
    var actual = assertInstanceOf(UserRecord.class, result.records().getFirst());
    assertEquals(
        new UserRecord(
            new UserId(3),
            USERNAME,
            UserRole.USER,
            UserState.ACTIVE,
            Optional.empty(),
            Optional.of(LAST_LOGIN),
            CREATED,
            UPDATED,
            4),
        actual);
    assertDoesNotThrow(() -> request.validateResponse(result));
    assertEquals(Map.of(1, UTC_NOW, 2, "u%", 3, ROLE_USER, 4, STATE_ACTIVE, 5, 1), jdbc.parameters);
    jdbc.assertReleased();
  }

  @Test
  void sql004MissingDetailIsAbsenceAndStillClosesOwnedStatementAndRows() {
    var jdbc = new Jdbc(List.of());
    var found = detail().query(new UserQueryRepository(), jdbc.connection(), ADMIN, NOW);
    assertTrue(found.isEmpty());
    assertEquals(Map.of(1, UTC_NOW, 2, UTC_NOW, 3, 3L), jdbc.parameters);
    detailSql(jdbc.sql);
    jdbc.assertReleased();
  }

  @Test
  void sql005DetailProjectsTwoActiveSessionsWithoutSelectingCredentials() {
    var row = userRow(false);
    row.put("active_sessions", 2L);
    row.put("password_changed_at", OffsetDateTime.parse("2026-08-31T00:00:00.123456Z"));
    row.put("created_by_name", "SYSTEM");
    row.put("updated_by_name", "operator");
    var jdbc = new Jdbc(List.of(row));
    var request = detail();
    var result =
        request.query(new UserQueryRepository(), jdbc.connection(), ADMIN, NOW).orElseThrow();
    assertEquals("UDTRSP01", result.layoutId().value());
    assertEquals(
        new UserDetailResponseData(
            new UserId(3),
            USERNAME,
            UserRole.USER,
            UserState.ACTIVE,
            Optional.empty(),
            Optional.of(LAST_LOGIN),
            Instant.parse("2026-08-31T00:00:00.123Z"),
            CREATED,
            UPDATED,
            2,
            4,
            "SYSTEM",
            "operator"),
        result.data());
    assertTrue(result.records().isEmpty());
    assertDoesNotThrow(() -> request.validateResponse(result));
    detailSql(jdbc.sql);
    jdbc.assertReleased();
  }

  @Test
  void sql006LockedProjectionPreservesOptionalTimeAndAbsentLastLogin() {
    var jdbc = new Jdbc(List.of(userRow(true)));
    var request = search("u", ROLE_USER, STATE_LOCKED, PAGE_ONE);
    var result =
        request.query(new UserQueryRepository(), jdbc.connection(), ADMIN, NOW).orElseThrow();
    var actual = assertInstanceOf(UserRecord.class, result.records().getFirst());
    assertEquals(
        new UserRecord(
            new UserId(3),
            USERNAME,
            UserRole.USER,
            UserState.LOCKED,
            Optional.of(LOCKED_UNTIL),
            Optional.empty(),
            CREATED,
            UPDATED,
            4),
        actual);
    assertDoesNotThrow(() -> request.validateResponse(result));
    assertEquals(STATE_LOCKED, jdbc.parameters.get(4));
    jdbc.assertReleased();
  }

  @Test
  void sql007UserRoleIsDeniedBeforeAnyConnectionMethod() {
    var jdbc = new Jdbc(List.of(emptyRow()));
    var user = new AuthenticatedActor(8, "ordinary", Role.USER);
    var request = search("", "", "", PAGE_ONE);
    var failure =
        assertThrows(
            AuthorizationException.class,
            () -> request.query(new UserQueryRepository(), jdbc.connection(), user, NOW));
    assertEquals(ResultCode.FORBIDDEN, failure.resultCode());
    assertEquals(0, jdbc.connectionCalls);
    assertTrue(jdbc.closed.isEmpty());
  }

  @Test
  void sql008IndependentNullArgumentsNeverReachTheBorrowedInterface() {
    var jdbc = new Jdbc(List.of(emptyRow()));
    var repository = new UserQueryRepository();
    var request = detail();
    assertThrows(NullPointerException.class, () -> request.query(repository, null, ADMIN, NOW));
    assertThrows(
        NullPointerException.class, () -> request.query(repository, jdbc.connection(), null, NOW));
    assertThrows(
        NullPointerException.class,
        () -> request.query(repository, jdbc.connection(), ADMIN, null));
    assertEquals(0, jdbc.connectionCalls);
    assertTrue(jdbc.closed.isEmpty());
  }

  @Test
  void sql009FullPagePreservesAllFiftyRowsAndRequestedPage() {
    var rows = new ArrayList<Map<String, @Nullable Object>>();
    var expected = new ArrayList<Long>();
    for (long id = 1; id <= 50; id++) {
      var row = userRow(false);
      row.put(COLUMN_TOTAL, 50L);
      row.put("id", id);
      row.put("username", "u" + (100 + id));
      rows.add(row);
      expected.add(id);
    }
    var jdbc = new Jdbc(rows);
    var request = search("", "", "", "999999");
    var result =
        request.query(new UserQueryRepository(), jdbc.connection(), ADMIN, NOW).orElseThrow();
    assertEquals(new PagedResponseData(1, 50, 50, 1, 1, 50), result.data());
    assertEquals(
        expected,
        result.records().stream().map(row -> ((UserRecord) row).userId().value()).toList());
    assertEquals(Map.of(1, UTC_NOW, 2, 999999), jdbc.parameters);
    assertDoesNotThrow(() -> request.validateResponse(result));
    searchSql(jdbc.sql);
    jdbc.assertReleased();
  }

  private static void searchSql(String sql) {
    assertTrue(sql.contains("filtered as materialized"));
    assertTrue(sql.contains("count(*) as total"));
    assertTrue(sql.contains("greatest(1,(total+49)/50)"));
    assertTrue(sql.contains("limit 50 offset (p.effective-1)*50"));
    assertTrue(sql.contains("order by username collate \"C\",id"));
    assertTrue(sql.contains("order by x.username collate \"C\",x.id"));
    noCredentialColumns(sql);
  }

  private static void detailSql(String sql) {
    assertTrue(sql.contains("s.user_id=p.id and s.revoked=false and s.expires_at > ?"));
    assertTrue(sql.contains("where p.id=?"));
    noCredentialColumns(sql);
  }

  private static void noCredentialColumns(String sql) {
    assertFalse(sql.contains("password_hash"));
    assertFalse(sql.contains("password_salt"));
    assertFalse(sql.contains("token_digest"));
    assertFalse(sql.contains("for update"));
  }

  private static Map<String, @Nullable Object> emptyRow() {
    var row = new HashMap<String, @Nullable Object>();
    row.put(COLUMN_TOTAL, 0L);
    row.put("pages", 1L);
    row.put("effective", 1L);
    row.put("id", null);
    return row;
  }

  private static Map<String, @Nullable Object> userRow(boolean locked) {
    var row = emptyRow();
    row.put(COLUMN_TOTAL, 1L);
    row.put("id", 3L);
    row.put("username", USERNAME);
    row.put("role", ROLE_USER);
    row.put("state", locked ? STATE_LOCKED : STATE_ACTIVE);
    row.put("locked_until", locked ? OffsetDateTime.parse("2026-09-09T00:00:00.456789Z") : null);
    row.put("last_login_at", locked ? null : OffsetDateTime.parse("2026-09-07T00:00:00.123456Z"));
    row.put("created_at", OffsetDateTime.parse("2026-01-01T00:00:00Z"));
    row.put("updated_at", OffsetDateTime.parse("2026-09-01T00:00:00Z"));
    row.put("version", 4L);
    return row;
  }

  @FunctionalInterface
  private interface Call {
    @Nullable Object invoke(String method, Object[] arguments);
  }

  private static <T> T proxy(Class<T> type, Call call) {
    return type.cast(
        Proxy.newProxyInstance(
            UserQuerySqlContractTest.class.getClassLoader(),
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
                case "setObject", "setString", "setInt", "setLong" -> {
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
                  if (args.length == TYPED_GETTER_ARGUMENTS)
                    assertEquals(OffsetDateTime.class, args[1]);
                  yield value((String) args[0]);
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

  private static UserQueryRequest search(String prefix, String role, String state, String page) {
    byte[] bytes = new byte[96];
    Arrays.fill(bytes, (byte) 32);
    put(bytes, 0, prefix);
    put(bytes, 64, role);
    put(bytes, 69, state);
    put(bytes, 77, page + "050");
    return UserQueryRequest.decode(wire(SEARCH_LAYOUT, bytes));
  }

  private static UserQueryRequest detail() {
    return UserQueryRequest.decode(
        wire(DETAIL_LAYOUT, "000000000003".getBytes(StandardCharsets.US_ASCII)));
  }

  private static void put(byte[] bytes, int offset, String value) {
    byte[] text = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(text, 0, bytes, offset, text.length);
  }

  private static WireMessage<FixedPayload> wire(String layout, byte[] bytes) {
    UUID id = new UUID(2024, 1);
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(layout),
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
    return new WireMessage<>(header, new FixedPayload(bytes, 0, List.of()));
  }
}
