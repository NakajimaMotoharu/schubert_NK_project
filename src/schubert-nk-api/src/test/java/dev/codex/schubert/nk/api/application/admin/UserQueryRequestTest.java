package dev.codex.schubert.nk.api.application.admin;

import static dev.codex.schubert.nk.api.application.admin.UserMutationRequestTest.put;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.persistence.UserQueryRepository;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.AuthorizationException;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.admin.UserRecord;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** UI236 literal request bytes and SS323 §9.4 independent LP oracle. PT-ADM-040..043. */
class UserQueryRequestTest {
  // Independent SS323/UI236 fixture literals, never aliases of Production constants.
  private static final String SEARCH_LAYOUT = "USRREQ01";
  private static final String DETAIL_LAYOUT = "UDTREQ01";
  private static final String ACTIVE_STATE = "ACTIVE";
  static final Instant NOW = Instant.parse("2026-09-08T00:01:00Z");
  static final AuthenticatedActor ADMIN = new AuthenticatedActor(1, "u1", Role.ADMIN);
  static final UUID MESSAGE = new UUID(100, 1);
  @TempDir static Path root;
  static dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture database;

  @org.junit.jupiter.api.BeforeAll
  static void start() throws Exception {
    database = new dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture(root);
  }

  @org.junit.jupiter.api.AfterAll
  static void stop() throws Exception {
    database.stop();
  }

  @Test
  void adm040DecodeAndCanonicalKeepAllOriginalQueryFields() throws Exception {
    for (String prefix : Arrays.asList(null, "équipe", " A_%\\'", "NEW", "new", "é".repeat(32)))
      for (String role : Arrays.asList(null, "USER", "ADMIN"))
        for (String state : Arrays.asList(null, ACTIVE_STATE, "DISABLED", "LOCKED"))
          for (int page : new int[] {1, 999999}) {
            var request = list(prefix, role, state, page, MESSAGE);
            check(
                request,
                ADMIN,
                SEARCH_LAYOUT,
                Arrays.asList(prefix, role, state, Integer.toString(page), "50"));
            assertFalse(request.detailRequest());
            assertEquals("USRRSP01", request.responseLayoutId().value());
            assertEquals("UserQueryRequest[REDACTED]", request.toString());
          }
    for (long target : new long[] {1, 999999999999L}) {
      var request = detail(target, MESSAGE);
      check(request, ADMIN, DETAIL_LAYOUT, List.of(Long.toString(target)));
      assertTrue(request.detailRequest());
      assertEquals("UDTRSP01", request.responseLayoutId().value());
    }
    var input =
        UserMutationRequestTest.message(SEARCH_LAYOUT, listData("new", null, null, 1), MESSAGE);
    var original = UserQueryRequest.decode(input);
    assertSame(input.header(), original.header());
    try (var a = original.canonical(ADMIN);
        var b = list("new", null, null, 1, new UUID(100, 2)).canonical(ADMIN);
        var c = list("NEW", null, null, 1, MESSAGE).canonical(ADMIN);
        var keys = UserMutationRequestTest.keys()) {
      assertArrayEquals(keys.calculate(a).digest(), keys.calculate(b).digest());
      assertFalse(Arrays.equals(keys.calculate(a).digest(), keys.calculate(c).digest()));
    }
  }

  @Test
  void adm041RealReadOnlyQueriesUseTheSameDecodedValues() throws Exception {
    try (var f = new UserApplicationFixture(database)) {
      f.seed();
      var repo = new UserQueryRepository();
      for (int page : new int[] {1, 999999})
        try (var c = f.db.transaction()) {
          c.setReadOnly(true);
          var request = list(null, null, null, page, MESSAGE);
          var response = request.query(repo, c, ADMIN, NOW).orElseThrow();
          request.validateResponse(response);
          assertEquals(new PagedResponseData(1, 50, 3, 1, 1, 3), response.data());
          assertEquals(
              List.of(1L, 2L, 3L),
              response.records().stream().map(r -> ((UserRecord) r).userId().value()).toList());
          assertTrue(c.isReadOnly());
          assertFalse(c.getAutoCommit());
          assertFalse(c.isClosed());
          c.commit();
        }
      for (String role : List.of("ADMIN", "USER"))
        try (var c = f.db.transaction()) {
          c.setReadOnly(true);
          var response =
              list(" U", role, ACTIVE_STATE, 1, MESSAGE).query(repo, c, ADMIN, NOW).orElseThrow();
          assertEquals(
              role.equals("ADMIN") ? List.of(1L, 2L) : List.of(3L),
              response.records().stream().map(r -> ((UserRecord) r).userId().value()).toList());
        }
      try (var c = f.db.transaction()) {
        c.setReadOnly(true);
        var request = detail(3, MESSAGE);
        var response = request.query(repo, c, ADMIN, NOW).orElseThrow();
        request.validateResponse(response);
        var data = (UserDetailResponseData) response.data();
        assertEquals(3, data.userId().value());
        assertEquals("u3", data.username());
        assertEquals(UserRole.USER, data.role());
        assertEquals(1, data.activeSessionCount());
        assertEquals(0, data.version());
        assertTrue(detail(999, MESSAGE).query(repo, c, ADMIN, NOW).isEmpty());
        assertTrue(
            list("' OR 1=1 --", null, null, 1, MESSAGE)
                .query(repo, c, ADMIN, NOW)
                .orElseThrow()
                .records()
                .isEmpty());
      }
      assertEquals(3, f.scalar("select count(*) from schubert.app_users"));
      assertEquals(0, f.scalar("select count(*) from schubert.request_inbox"));
      assertEquals(0, f.scalar("select count(*) from schubert.app_logs"));
      assertEquals(0, f.scalar("select sum(version) from schubert.app_users"));
    }
  }

  @Test
  void adm042NullMalformedAndResponseMismatchNeverPass() throws Exception {
    var list = list(null, null, null, 1, MESSAGE);
    var detail = detail(3, MESSAGE);
    assertThrows(NullPointerException.class, () -> UserQueryRequest.decode(null));
    assertThrows(NullPointerException.class, () -> list.canonical(null));
    assertThrows(NullPointerException.class, () -> list.validateResponse(null));
    for (int mode = 0; mode < 3; mode++) {
      var kind = mode == 0 ? MessageKind.RESPONSE : MessageKind.REQUEST;
      var interaction = mode == 1 ? InteractionKind.ASYNC_ACCEPTANCE : InteractionKind.SYNCHRONOUS;
      int recordLength = mode == 2 ? 1 : 0;
      int recordCount = mode == 2 ? 1 : 0;
      var header =
          new CommonHeader(
              "SCHBNK01",
              1,
              new LayoutId(SEARCH_LAYOUT),
              1,
              kind,
              interaction,
              MESSAGE,
              MESSAGE,
              NOW,
              Optional.of(AuthenticationContext.of("b".repeat(64))),
              256,
              96,
              recordLength,
              recordCount,
              352 + recordCount,
              mode == 0 ? Optional.of(ResultCode.SUCCESS) : Optional.empty());
      invalid(
          new WireMessage<>(
              header,
              new FixedPayload(
                  listData(null, null, null, 1),
                  recordLength,
                  mode == 2 ? List.of(new byte[] {32}) : List.of())));
    }
    assertThrows(
        LayoutValidationException.class,
        () ->
            new CommonHeader(
                "SCHBNK01",
                1,
                new LayoutId(SEARCH_LAYOUT),
                2,
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                MESSAGE,
                MESSAGE,
                NOW,
                Optional.of(AuthenticationContext.of("b".repeat(64))),
                256,
                96,
                0,
                0,
                352,
                Optional.empty()));
    for (byte[] data :
        List.of(
            new byte[95],
            listData(null, null, null, 0),
            listData(null, "ROOT", null, 1),
            listData(null, null, "UNKNOWN", 1)))
      invalid(UserMutationRequestTest.message(SEARCH_LAYOUT, data, MESSAGE));
    byte[] size = listData(null, null, null, 1);
    put(size, 83, "049");
    invalid(UserMutationRequestTest.message(SEARCH_LAYOUT, size, MESSAGE));
    byte[] reserved = listData(null, null, null, 1);
    reserved[95] = 'X';
    invalid(UserMutationRequestTest.message(SEARCH_LAYOUT, reserved, MESSAGE));
    byte[] malformed = listData(null, null, null, 1);
    malformed[0] = (byte) 0xff;
    invalid(UserMutationRequestTest.message(SEARCH_LAYOUT, malformed, MESSAGE));
    invalid(
        UserMutationRequestTest.message(
            DETAIL_LAYOUT, "000000000000".getBytes(StandardCharsets.US_ASCII), MESSAGE));
    invalid(
        UserMutationRequestTest.message(
            "ULKREQ01",
            UserMutationRequestTest.data(
                "ULKREQ01", 3, 0, true, "New", "Synthetic-12", new UUID(100, 2)),
            MESSAGE));
    for (var wrong :
        List.of(
            detailResponse(4, false),
            page(0, 0, 1, 50),
            new TypedPayloadValues(
                new LayoutId("UDTRSP01"), new PagedResponseData(1, 50, 0, 1, 0, 0), List.of())))
      assertThrows(IllegalArgumentException.class, () -> detail.validateResponse(wrong));
    assertThrows(
        IllegalArgumentException.class, () -> list.validateResponse(detailResponse(3, false)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            list.validateResponse(
                new TypedPayloadValues(
                    new LayoutId("USRRSP01"), detailResponse(3, false).data(), List.of())));
    assertThrows(
        IllegalArgumentException.class,
        () -> list(null, null, null, 2, MESSAGE).validateResponse(page(1, 51, 1, 50)));
    for (var wrong :
        List.of(page(0, 0, 0, 50), page(0, 0, 1, 49), page(1, 0, 1, 50), page(0, 1, 1, 50)))
      assertThrows(IllegalArgumentException.class, () -> list.validateResponse(wrong));
    try (var f = new UserApplicationFixture(database)) {
      f.seed();
      var repo = new UserQueryRepository();
      try (var c = f.db.transaction()) {
        var closed = f.db.transaction();
        closed.close();
        assertThrows(
            dev.codex.schubert.nk.api.persistence.UserQueryException.class,
            () -> list.query(repo, closed, ADMIN, NOW));
        assertThrows(NullPointerException.class, () -> list.query(null, c, ADMIN, NOW));
        assertThrows(NullPointerException.class, () -> list.query(repo, null, ADMIN, NOW));
        assertThrows(NullPointerException.class, () -> list.query(repo, c, null, NOW));
        assertThrows(NullPointerException.class, () -> list.query(repo, c, ADMIN, null));
        assertThrows(
            dev.codex.schubert.nk.api.persistence.UserQueryException.class,
            () -> list.query(repo, c, ADMIN, NOW));
        c.setReadOnly(true);
        for (var request : List.of(list, detail))
          assertThrows(
              AuthorizationException.class,
              () -> request.query(repo, c, new AuthenticatedActor(3, "u3", Role.USER), NOW));
      }
    }
  }

  @Test
  void adm043ConcurrentRequestsOwnIndependentCanonicalBuffers() throws Exception {
    try (var pool = Executors.newFixedThreadPool(10)) {
      var results = new ArrayList<Future<Void>>();
      for (int i = 1; i <= 100; i++) {
        int n = i;
        results.add(
            pool.submit(
                () -> {
                  var actor = new AuthenticatedActor(n, "u" + n, Role.ADMIN);
                  var request =
                      n % 2 == 0
                          ? detail(n, new UUID(100, n))
                          : list("u" + n, null, ACTIVE_STATE, n, new UUID(100, n));
                  var expected =
                      n % 2 == 0
                          ? List.of(Integer.toString(n))
                          : Arrays.asList("u" + n, null, ACTIVE_STATE, Integer.toString(n), "50");
                  String expectedLayout = n % 2 == 0 ? DETAIL_LAYOUT : SEARCH_LAYOUT;
                  check(request, actor, expectedLayout, expected);
                  var first = request.canonical(actor);
                  try (var second = request.canonical(actor);
                      var keys = UserMutationRequestTest.keys()) {
                    byte[] before = keys.calculate(second).digest();
                    first.close();
                    for (var field : first.fields())
                      if (field.value() != null)
                        assertArrayEquals(new byte[field.value().length], field.value());
                    assertArrayEquals(before, keys.calculate(second).digest());
                    check(request, actor, expectedLayout, expected);
                  } finally {
                    first.close();
                  }
                  return null;
                }));
      }
      for (var result : results) result.get(20, TimeUnit.SECONDS);
    }
  }

  static UserQueryRequest list(String prefix, String role, String state, int page, UUID message) {
    return UserQueryRequest.decode(
        UserMutationRequestTest.message(
            SEARCH_LAYOUT, listData(prefix, role, state, page), message));
  }

  static UserQueryRequest detail(long id, UUID message) {
    return UserQueryRequest.decode(
        UserMutationRequestTest.message(
            DETAIL_LAYOUT,
            String.format(Locale.ROOT, "%012d", id).getBytes(StandardCharsets.US_ASCII),
            message));
  }

  static byte[] listData(String prefix, String role, String state, int page) {
    byte[] data = new byte[96];
    Arrays.fill(data, (byte) 32);
    if (prefix != null) put(data, 0, prefix);
    if (role != null) put(data, 64, role);
    if (state != null) put(data, 69, state);
    put(data, 77, String.format(Locale.ROOT, "%06d050", page));
    return data;
  }

  static TypedPayloadValues page(int count, long total, int page, int size) {
    List<PayloadRecord> rows = new ArrayList<>();
    for (int i = 1; i <= count; i++)
      rows.add(
          new UserRecord(
              new UserId(i),
              "u" + i,
              UserRole.USER,
              UserState.ACTIVE,
              Optional.empty(),
              Optional.empty(),
              NOW,
              NOW,
              0));
    return new TypedPayloadValues(
        new LayoutId("USRRSP01"),
        new PagedResponseData(
            page,
            size,
            total,
            Math.max(1, (int) ((total + 49) / 50)),
            total == 0 ? 0 : (page - 1L) * 50 + 1,
            Math.min(page * 50L, total)),
        rows);
  }

  static TypedPayloadValues detailResponse(long id, boolean optional) {
    return new TypedPayloadValues(
        new LayoutId("UDTRSP01"),
        new UserDetailResponseData(
            new UserId(id),
            "u" + id,
            UserRole.USER,
            UserState.ACTIVE,
            optional ? Optional.of(NOW) : Optional.empty(),
            optional ? Optional.of(NOW) : Optional.empty(),
            NOW,
            NOW,
            NOW,
            optional ? 2 : 0,
            0,
            "SYSTEM",
            "SYSTEM"),
        List.of());
  }

  static void invalid(WireMessage<FixedPayload> message) {
    var e = assertThrows(PermanentProtocolException.class, () -> UserQueryRequest.decode(message));
    assertEquals("user query request is invalid", e.getMessage());
    assertNull(e.getCause());
  }

  static byte[] check(
      UserQueryRequest request,
      AuthenticatedActor actor,
      String expectedLayout,
      List<String> expected)
      throws Exception {
    // BUG1777: derive oracle metadata from the input fixture, never from the SUT branch.
    assertTrue(Set.of(SEARCH_LAYOUT, DETAIL_LAYOUT).contains(expectedLayout));
    boolean expectedDetail = expectedLayout.equals(DETAIL_LAYOUT);
    assertEquals(expectedDetail, request.detailRequest());
    try (var canonical = request.canonical(actor);
        var keys = UserMutationRequestTest.keys()) {
      String layout = expectedLayout;
      var names =
          expectedDetail
              ? List.of("userId")
              : List.of("usernamePrefix", "role", "state", "page", "pageSize");
      assertEquals(Long.toString(actor.userId()), canonical.ownerScope());
      assertEquals(layout, canonical.layoutId());
      assertEquals("001", canonical.layoutVersion());
      assertEquals("REQUEST:" + layout, canonical.target());
      assertEquals(expected.size(), canonical.fields().size());
      var bytes = new ByteArrayOutputStream();
      try (var out = new DataOutputStream(bytes)) {
        out.write("SCHUBERT-NK-OP1".getBytes(StandardCharsets.US_ASCII));
        for (String value :
            List.of(Long.toString(actor.userId()), layout, "001", "REQUEST:" + layout))
          UserMutationRequestTest.lp(out, value);
        out.writeInt(expected.size());
        for (int i = 0; i < expected.size(); i++) {
          String type = expectedDetail || i >= 3 ? "N1" : "X1";
          var actual = canonical.fields().get(i);
          assertEquals(names.get(i), actual.name());
          assertEquals(type, actual.typeVersion());
          UserMutationRequestTest.lp(out, names.get(i));
          UserMutationRequestTest.lp(out, type);
          if (expected.get(i) == null) {
            out.writeInt(-1);
            assertNull(actual.value());
          } else {
            UserMutationRequestTest.lp(out, expected.get(i));
            assertArrayEquals(expected.get(i).getBytes(StandardCharsets.UTF_8), actual.value());
          }
        }
      }
      var mac = Mac.getInstance("HmacSHA256");
      mac.init(new SecretKeySpec(new byte[32], "HmacSHA256"));
      byte[] independentlyCalculated = mac.doFinal(bytes.toByteArray());
      assertArrayEquals(independentlyCalculated, keys.calculate(canonical).digest());
      return independentlyCalculated;
    }
  }
}
