package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

import dev.codex.schubert.nk.api.application.admin.UserApplicationAssembly;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.protocol.codec.ExpectedRoute;
import dev.codex.schubert.nk.protocol.codec.FixedWidthDecoder;
import dev.codex.schubert.nk.protocol.codec.TransportBodyType;
import dev.codex.schubert.nk.protocol.codec.TransportMetadata;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.config.UserBusinessMvcConfiguration;
import dev.codex.schubert.nk.web.controller.UserAdminController;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.messaging.UserAdministrationWireClient;
import dev.codex.schubert.nk.web.view.UserCreateViewModel;
import dev.codex.schubert.nk.web.view.UserDetailViewModel;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BiFunction;
import javax.sql.DataSource;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.mock.web.MockServletContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;

/** UI225236 literals and real encrypted SQL; SSC177/PG-D366/PT-USER-BIZ001..012. */
class UserBusinessControllerTest {
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_0200_FC9DB3AC = "0200";
  private static final String FIXTURE_ADMIN_USER_NEW_5A16DB0A = "admin/user-new";
  private static final String FIXTURE_GET_04F32A7E = "GET";
  private static final String FIXTURE_PAGE_861424BC = "page";
  private static final String FIXTURE_ROLE_2BC933AF = "role";
  private static final String FIXTURE_USER_2DED8884 = "USER";
  private static final String FIXTURE_ENABLED_6E30BC5C = "enabled";
  private static final String FIXTURE_FIELDS_D0E4C641 = "fields";
  private static final String FIXTURE_UCRREQ01_841A676A = "UCRREQ01";
  private static final String FIXTURE_POST_E46D3AE9 = "POST";
  private static final String FIXTURE_ADMIN_USERS_42_65AE9E81 = "/admin/users/42";
  private static final String FIXTURE_LOCATION_FB077BAD = "Location";
  private static final String FIXTURE_LONGPASSWORD1_DA4ADD07 = "longpassword1";
  private static final String FIXTURE_ADMIN_USER_DETAIL_CC61E128 = "admin/user-detail";
  private static final String FIXTURE_USTREQ01_D6E6CD9B = "USTREQ01";
  private static final String FIXTURE_EXPECTED_VERSION_633674D2 = "expected_version";
  private static final String FIXTURE_PASSWORD_FF2BEA10 = "password";
  private static final String FIXTURE_STATUS_0ABCCBF8 = "STATUS";
  private static final String FIXTURE_ROLE_7C85C916 = "ROLE";
  private static final String FIXTURE_PASSWORD_FC2A3EAA = "PASSWORD";
  private static final String FIXTURE_UNLOCK_351153DC = "UNLOCK";
  private static final String FIXTURE_000000000_A4DD9DF1 = "000000000";
  private static final String FIXTURE_OPERATION_063BD517 = "operation";
  private static final String FIXTURE_OPERATION_TOKEN_6C771227 = "operation_token";
  private static final String FIXTURE_UDTREQ01_DAA8B937 = "UDTREQ01";
  private static final String FIXTURE_0105_6F9AB3E4 = "0105";
  private static final String FIXTURE_ADMIN_USERS_NEW_88CAF2E8 = "/admin/users/new";
  private static final String FIXTURE_JS_OPERATION_POST_SUBMIT_JS_04D3D42D =
      "/js/operation-post-submit.js";
  private static final String FIXTURE_VALUE_A0B7821A = "value";
  private static final String FIXTURE_TRUE_18D10C7D = "true";
  private static final String FIXTURE_CREATE_4DC7E48E = "CREATE";
  private static final String FIXTURE_DELETED_67A0D0C0 = "deleted";
  private static final String FIXTURE_NEW_00A2B031 = "NEW";
  private static final String FIXTURE_DETAIL_3053326D = "DETAIL";
  static WebLogDatabaseFixture db;
  @TempDir Path root;

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
      s.executeUpdate("DELETE FROM schubert_web_session.web_http_sessions");
    }
  }

  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  static LinkedMultiValueMap<String, String> params(String... pairs) {
    var result = new LinkedMultiValueMap<String, String>();
    for (int i = 0; i < pairs.length; i += 2) result.add(pairs[i], pairs[i + 1]);
    return result;
  }

  static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(
        "admin", role, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
  }

  @Test
  void biz001NewDefaultsAndCreateSuccessIndependent372Bytes() throws Exception {
    for (String code : List.of(FIXTURE_0000_876EEFE0, FIXTURE_0200_FC9DB3AC)) {
      reset();
      try (var f = new Fixture()) {
        var model = new ExtendedModelMap();
        var r = new MockHttpServletResponse();
        assertEquals(
            FIXTURE_ADMIN_USER_NEW_5A16DB0A,
            f.controller.newForm(actor(UserRole.ADMIN), model, f.request(FIXTURE_GET_04F32A7E), r));
        assertEquals(200, r.getStatus());
        var view = assertInstanceOf(UserCreateViewModel.class, model.get(FIXTURE_PAGE_861424BC));
        assertEquals(
            Map.of(
                "username",
                "",
                FIXTURE_ROLE_2BC933AF,
                FIXTURE_USER_2DED8884,
                FIXTURE_ENABLED_6E30BC5C,
                true),
            view.getValues().get(FIXTURE_FIELDS_D0E4C641));
        UUID token = UUID.fromString((String) view.getValues().get("token"));
        assertEquals(
            List.of(FIXTURE_UCRREQ01_841A676A),
            f.retained().stream().map(SessionOperationToken::purpose).toList());
        f.code = code;
        var input = f.create(token);
        assertNull(
            f.controller.create(
                input, actor(UserRole.ADMIN), model, f.request(FIXTURE_POST_E46D3AE9), r));
        assertEquals(302, r.getStatus());
        assertEquals(FIXTURE_ADMIN_USERS_42_65AE9E81, r.getHeader(FIXTURE_LOCATION_FB077BAD));
        byte[] expected = blank(372);
        put(expected, 0, "new-user");
        put(expected, 64, FIXTURE_LONGPASSWORD1_DA4ADD07);
        put(expected, 320, FIXTURE_USER_2DED8884);
        put(expected, 325, "1");
        put(expected, 326, token.toString());
        assertEquals(628, f.sent.getLast().length);
        assertEquals(FIXTURE_UCRREQ01_841A676A, ascii(f.sent.getLast(), 11, 8));
        assertArrayEquals(expected, Arrays.copyOfRange(f.sent.getLast(), 256, 628));
        assertTrue(f.retained().getFirst().completedAt().isPresent());
        assertEquals("UserCreateViewModel[REDACTED]", view.toString());
        assertThrows(UnsupportedOperationException.class, () -> view.getValues().clear());
        f.erased();
      }
    }
  }

  @Test
  void biz002OnlyVisibleFormsAndExactCapacity() throws Exception {
    for (String username : List.of("target", "ADMIN"))
      for (String state : List.of("ACTIVE", "DISABLED", "LOCKED"))
        for (long version : List.of(0L, 999999999L)) {
          reset();
          try (var f = new Fixture()) {
            f.username = username;
            f.state = state;
            f.version = version;
            var model = new ExtendedModelMap();
            var r = new MockHttpServletResponse();
            assertEquals(
                FIXTURE_ADMIN_USER_DETAIL_CC61E128,
                f.controller.detail(
                    42, actor(UserRole.ADMIN), model, f.request(FIXTURE_GET_04F32A7E), r));
            assertEquals(200, r.getStatus());
            var forms = assertInstanceOf(List.class, model.get("forms"));
            var expected = new ArrayList<String>();
            if (username.equals("target")) {
              expected.add(FIXTURE_USTREQ01_D6E6CD9B);
              expected.add("URLREQ01");
            }
            expected.add("UPWREQ01");
            if (state.equals("LOCKED")) expected.add("ULKREQ01");
            assertEquals(expected.size(), forms.size());
            assertEquals(
                expected, f.retained().stream().map(SessionOperationToken::purpose).toList());
            for (Object value : forms) {
              var form = assertInstanceOf(Map.class, value);
              var fields = assertInstanceOf(Map.class, form.get(FIXTURE_FIELDS_D0E4C641));
              assertEquals(version, fields.get(FIXTURE_EXPECTED_VERSION_633674D2));
              assertFalse(fields.containsKey(FIXTURE_PASSWORD_FF2BEA10));
            }
          }
        }
    reset();
    try (var f = new Fixture()) {
      f.security.f.repository.mutate(
          f.session.sessionId(),
          current ->
              SessionOperationTokenLifecycleTest.tokens(
                  current, SessionOperationTokenLifecycleTest.pending(8)));
      var r = new MockHttpServletResponse();
      assertNull(
          f.controller.detail(
              42,
              actor(UserRole.ADMIN),
              new ExtendedModelMap(),
              f.request(FIXTURE_GET_04F32A7E),
              r));
      assertEquals(409, r.getStatus());
      assertEquals(8, f.retained().size());
      assertEquals(0, f.tokenIds.get());
    }
  }

  @Test
  void biz003FourMutationsLiteralBytesAndIdempotentUnlock() throws Exception {
    for (String operation :
        List.of(
            FIXTURE_STATUS_0ABCCBF8,
            FIXTURE_ROLE_7C85C916,
            FIXTURE_PASSWORD_FC2A3EAA,
            FIXTURE_UNLOCK_351153DC))
      for (String code : List.of(FIXTURE_0000_876EEFE0, FIXTURE_0200_FC9DB3AC)) {
        reset();
        try (var f = new Fixture()) {
          UUID token = f.issue(operation);
          f.code = code;
          f.updated =
              operation.equals(FIXTURE_UNLOCK_351153DC) && code.equals(FIXTURE_0200_FC9DB3AC)
                  ? 0
                  : 1;
          var r = new MockHttpServletResponse();
          assertNull(
              f.controller.change(
                  42,
                  f.change(operation, token),
                  actor(UserRole.ADMIN),
                  new ExtendedModelMap(),
                  f.request(FIXTURE_POST_E46D3AE9),
                  r));
          assertEquals(302, r.getStatus());
          assertEquals(FIXTURE_ADMIN_USERS_42_65AE9E81, r.getHeader(FIXTURE_LOCATION_FB077BAD));
          var sent = f.sent.getLast();
          byte[] expected;
          switch (operation) {
            case FIXTURE_STATUS_0ABCCBF8 -> {
              expected = blank(60);
              put(expected, 12, "0");
              put(expected, 13, FIXTURE_000000000_A4DD9DF1);
              put(expected, 22, token.toString());
            }
            case FIXTURE_ROLE_7C85C916 -> {
              expected = blank(68);
              put(expected, 12, FIXTURE_USER_2DED8884);
              put(expected, 17, FIXTURE_000000000_A4DD9DF1);
              put(expected, 26, token.toString());
            }
            case FIXTURE_PASSWORD_FC2A3EAA -> {
              expected = blank(324);
              put(expected, 12, FIXTURE_LONGPASSWORD1_DA4ADD07);
              put(expected, 268, FIXTURE_000000000_A4DD9DF1);
              put(expected, 277, token.toString());
            }
            default -> {
              expected = blank(60);
              put(expected, 12, FIXTURE_000000000_A4DD9DF1);
              put(expected, 21, token.toString());
            }
          }
          put(expected, 0, "000000000042");
          assertArrayEquals(expected, Arrays.copyOfRange(sent, 256, sent.length));
          assertEquals("a".repeat(64), ascii(sent, 113, 64));
          assertTrue(f.retained().getFirst().completedAt().isPresent());
          f.erased();
        }
      }
  }

  @Test
  void biz004InvalidOperationTokenAndBindingsNeverUpdate() throws Exception {
    try (var f = new Fixture()) {
      for (var input :
          List.of(
              params(),
              params(FIXTURE_OPERATION_063BD517, "UNKNOWN"),
              params(
                  FIXTURE_OPERATION_063BD517,
                  FIXTURE_ROLE_7C85C916,
                  FIXTURE_OPERATION_063BD517,
                  FIXTURE_STATUS_0ABCCBF8))) {
        var r = new MockHttpServletResponse();
        assertNull(
            f.controller.change(
                42,
                input,
                actor(UserRole.ADMIN),
                new ExtendedModelMap(),
                f.request(FIXTURE_POST_E46D3AE9),
                r));
        assertEquals(400, r.getStatus());
      }
      for (long id : List.of(0L, -1L, 1000000000000L)) {
        var r = new MockHttpServletResponse();
        assertNull(
            f.controller.change(
                id,
                params(FIXTURE_OPERATION_063BD517, FIXTURE_STATUS_0ABCCBF8),
                actor(UserRole.ADMIN),
                new ExtendedModelMap(),
                f.request(FIXTURE_POST_E46D3AE9),
                r));
        assertEquals(400, r.getStatus());
      }
      for (var input :
          List.of(
              params(FIXTURE_OPERATION_063BD517, FIXTURE_STATUS_0ABCCBF8),
              params(
                  FIXTURE_OPERATION_063BD517,
                  FIXTURE_STATUS_0ABCCBF8,
                  FIXTURE_OPERATION_TOKEN_6C771227,
                  "bad"),
              params(
                  FIXTURE_OPERATION_063BD517,
                  FIXTURE_STATUS_0ABCCBF8,
                  FIXTURE_OPERATION_TOKEN_6C771227,
                  UUID.randomUUID().toString(),
                  FIXTURE_OPERATION_TOKEN_6C771227,
                  UUID.randomUUID().toString()))) {
        var r = new MockHttpServletResponse();
        assertNull(
            f.controller.change(
                42,
                input,
                actor(UserRole.ADMIN),
                new ExtendedModelMap(),
                f.request(FIXTURE_POST_E46D3AE9),
                r));
        assertEquals(400, r.getStatus());
      }
      var r = new MockHttpServletResponse();
      assertNull(
          f.controller.change(
              42,
              f.change(FIXTURE_ROLE_7C85C916, new UUID(0, 999)),
              actor(UserRole.ADMIN),
              new ExtendedModelMap(),
              f.request(FIXTURE_POST_E46D3AE9),
              r));
      assertEquals(409, r.getStatus());
      assertTrue(f.sent.isEmpty());
      UUID token = f.issue(FIXTURE_ROLE_7C85C916);
      var invalid = f.change(FIXTURE_ROLE_7C85C916, token);
      invalid.set(FIXTURE_EXPECTED_VERSION_633674D2, "-1");
      r = new MockHttpServletResponse();
      var model = new ExtendedModelMap();
      assertEquals(
          FIXTURE_ADMIN_USER_DETAIL_CC61E128,
          f.controller.change(
              42, invalid, actor(UserRole.ADMIN), model, f.request(FIXTURE_POST_E46D3AE9), r));
      assertEquals(400, r.getStatus());
      assertEquals(
          List.of(FIXTURE_UDTREQ01_DAA8B937),
          f.sent.stream().map(bytes -> ascii(bytes, 11, 8)).toList());
      assertTrue(f.retained().getFirst().completedAt().isEmpty());
    }
  }

  @Test
  void biz005FreshConflictAndUnknownKeepExactToken() throws Exception {
    for (String code : List.of(FIXTURE_0105_6F9AB3E4, "9000")) {
      reset();
      try (var f = new Fixture()) {
        f.code = code;
        f.version = 7;
        UUID token = f.issue(FIXTURE_PASSWORD_FC2A3EAA);
        var model = new ExtendedModelMap();
        var r = new MockHttpServletResponse();
        assertEquals(
            FIXTURE_ADMIN_USER_DETAIL_CC61E128,
            f.controller.change(
                42,
                f.change(FIXTURE_PASSWORD_FC2A3EAA, token),
                actor(UserRole.ADMIN),
                model,
                f.request(FIXTURE_POST_E46D3AE9),
                r));
        assertEquals(code.equals(FIXTURE_0105_6F9AB3E4) ? 409 : 503, r.getStatus());
        assertEquals(
            List.of(FIXTURE_UDTREQ01_DAA8B937, "UPWREQ01", FIXTURE_UDTREQ01_DAA8B937),
            f.sent.stream().map(bytes -> ascii(bytes, 11, 8)).toList());
        assertEquals(
            7L,
            ((UserDetailViewModel) model.get(FIXTURE_PAGE_861424BC)).getValues().get("version"));
        var form = (Map<?, ?>) ((List<?>) model.get("forms")).getFirst();
        assertEquals(token.toString(), form.get("token"));
        assertEquals(
            0L,
            ((Map<?, ?>) form.get(FIXTURE_FIELDS_D0E4C641)).get(FIXTURE_EXPECTED_VERSION_633674D2));
        assertFalse(
            ((Map<?, ?>) form.get(FIXTURE_FIELDS_D0E4C641)).containsKey(FIXTURE_PASSWORD_FF2BEA10));
        assertEquals(1, f.tokenIds.get());
        assertTrue(f.retained().getFirst().completedAt().isEmpty());
      }
    }
  }

  @Test
  void biz009ActualMvcNewAndDetailFormsAreClosedAndPasswordFree() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      var csrf = new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", "b".repeat(64));
      var result =
          mvc.perform(
                  get(FIXTURE_ADMIN_USERS_NEW_88CAF2E8)
                      .principal(actor(UserRole.ADMIN))
                      .session(f.httpSession())
                      .requestAttr(CsrfToken.class.getName(), csrf))
              .andReturn();
      assertEquals(200, result.getResponse().getStatus());
      var dom = Jsoup.parse(result.getResponse().getContentAsString());
      assertEquals("User追加", dom.title());
      assertEquals(1, dom.select("form[data-operation-submit]").size());
      assertEquals(
          List.of(FIXTURE_JS_OPERATION_POST_SUBMIT_JS_04D3D42D),
          dom.select("script[src][defer]").eachAttr("src"));
      assertEquals(
          FIXTURE_USER_2DED8884,
          dom.select("select[name=role] option[selected]").attr(FIXTURE_VALUE_A0B7821A));
      assertEquals(
          FIXTURE_TRUE_18D10C7D,
          dom.select("select[name=enabled] option[selected]").attr(FIXTURE_VALUE_A0B7821A));
      assertEquals(
          FIXTURE_ADMIN_USERS_NEW_88CAF2E8,
          dom.select("form[action='/admin/users/new']").attr("action"));
      assertTrue(dom.select("input[type=password][value]").isEmpty());
      assertEquals(
          36, dom.select("input[name=operation_token]").attr(FIXTURE_VALUE_A0B7821A).length());
      f.state = "LOCKED";
      result =
          mvc.perform(
                  get(FIXTURE_ADMIN_USERS_42_65AE9E81)
                      .principal(actor(UserRole.ADMIN))
                      .session(f.httpSession())
                      .requestAttr(CsrfToken.class.getName(), csrf))
              .andReturn();
      assertEquals(200, result.getResponse().getStatus());
      dom = Jsoup.parse(result.getResponse().getContentAsString());
      assertEquals(
          List.of(
              FIXTURE_STATUS_0ABCCBF8,
              FIXTURE_ROLE_7C85C916,
              FIXTURE_PASSWORD_FC2A3EAA,
              FIXTURE_UNLOCK_351153DC),
          dom.select("form[data-operation]").eachAttr("data-operation"));
      assertEquals(4, dom.select("form[data-operation] input[name=_csrf]").size());
      assertEquals(4, dom.select("form[data-operation-submit]").size());
      assertEquals(
          List.of(FIXTURE_JS_OPERATION_POST_SUBMIT_JS_04D3D42D),
          dom.select("script[src][defer]").eachAttr("src"));
      assertEquals(
          4, dom.select("form[data-operation] input[name=expected_version][value='0']").size());
      assertTrue(dom.select("input[type=password][value]").isEmpty());
      assertFalse(result.getResponse().getContentAsString().contains("a".repeat(64)));
    }
  }

  @Test
  void biz005CreateInvalidConflictAndAllNonSuccessCodes() throws Exception {
    String[] codes = {
      "0100", "0101", "0103", "0104", FIXTURE_0105_6F9AB3E4, "0106", "0107", "9000", "9001"
    };
    int[] expected = {400, 401, 403, 404, 409, 429, 409, 503, 503};
    for (int n = 0; n < codes.length; n++) {
      reset();
      try (var f = new Fixture()) {
        UUID token = f.tokens.issue(f.session.sessionId(), FIXTURE_UCRREQ01_841A676A).token();
        f.code = codes[n];
        var model = new ExtendedModelMap();
        var response = new MockHttpServletResponse();
        String view =
            f.controller.create(
                f.create(token),
                actor(UserRole.ADMIN),
                model,
                f.request(FIXTURE_POST_E46D3AE9),
                response);
        assertEquals(expected[n], response.getStatus());
        boolean rendered = Set.of(400, 409, 503).contains(expected[n]);
        assertEquals(rendered ? FIXTURE_ADMIN_USER_NEW_5A16DB0A : null, view);
        if (rendered) {
          var page = assertInstanceOf(UserCreateViewModel.class, model.get(FIXTURE_PAGE_861424BC));
          assertEquals(token.toString(), page.getValues().get("token"));
          assertFalse(
              ((Map<?, ?>) page.getValues().get(FIXTURE_FIELDS_D0E4C641))
                  .containsKey(FIXTURE_PASSWORD_FF2BEA10));
          assertEquals(
              expected[n] == 409,
              ((Map<?, ?>) page.getValues().get("issues")).containsKey("username"));
        }
        assertTrue(f.retained().getFirst().completedAt().isEmpty());
        assertEquals(1, f.tokenIds.get());
      }
    }
    reset();
    try (var f = new Fixture()) {
      UUID token = f.tokens.issue(f.session.sessionId(), FIXTURE_UCRREQ01_841A676A).token();
      var input = f.create(token);
      input.set("password_confirmation", "different");
      var response = new MockHttpServletResponse();
      assertEquals(
          FIXTURE_ADMIN_USER_NEW_5A16DB0A,
          f.controller.create(
              input,
              actor(UserRole.ADMIN),
              new ExtendedModelMap(),
              f.request(FIXTURE_POST_E46D3AE9),
              response));
      assertEquals(400, response.getStatus());
      assertTrue(f.sent.isEmpty());
      f.responder =
          (id, bytes) -> {
            throw new jakarta.jms.JMSRuntimeException("private-mq-marker");
          };
      response = new MockHttpServletResponse();
      assertEquals(
          FIXTURE_ADMIN_USER_NEW_5A16DB0A,
          f.controller.create(
              f.create(token),
              actor(UserRole.ADMIN),
              new ExtendedModelMap(),
              f.request(FIXTURE_POST_E46D3AE9),
              response));
      assertEquals(503, response.getStatus());
      assertTrue(f.retained().getFirst().completedAt().isEmpty());
      f.erased();
    }
  }

  @Test
  void biz006MutationsRejectAllCodesMalformedTargetAndVersionWithoutConsumption() throws Exception {
    String[] codes = {
      "0100", "0101", "0103", "0104", FIXTURE_0105_6F9AB3E4, "0106", "0107", "9000", "9001"
    };
    int[] expected = {400, 401, 403, 404, 409, 429, 409, 503, 503};
    for (int n = 0; n < codes.length; n++) {
      reset();
      try (var f = new Fixture()) {
        UUID token = f.issue(FIXTURE_STATUS_0ABCCBF8);
        f.code = codes[n];
        var response = new MockHttpServletResponse();
        f.controller.change(
            42,
            f.change(FIXTURE_STATUS_0ABCCBF8, token),
            actor(UserRole.ADMIN),
            new ExtendedModelMap(),
            f.request(FIXTURE_POST_E46D3AE9),
            response);
        assertEquals(expected[n], response.getStatus());
        assertTrue(f.retained().getFirst().completedAt().isEmpty());
      }
    }
    for (String operation :
        List.of(
            FIXTURE_STATUS_0ABCCBF8,
            FIXTURE_ROLE_7C85C916,
            FIXTURE_PASSWORD_FC2A3EAA,
            FIXTURE_UNLOCK_351153DC))
      for (String code : List.of(FIXTURE_0000_876EEFE0, FIXTURE_0200_FC9DB3AC))
        for (boolean wrongTarget : List.of(false, true)) {
          reset();
          try (var f = new Fixture()) {
            UUID token = f.issue(operation);
            f.code = code;
            f.target = wrongTarget ? 43 : 42;
            f.updated = wrongTarget ? 1 : 7;
            var response = new MockHttpServletResponse();
            assertNull(
                f.controller.change(
                    42,
                    f.change(operation, token),
                    actor(UserRole.ADMIN),
                    new ExtendedModelMap(),
                    f.request(FIXTURE_POST_E46D3AE9),
                    response));
            assertEquals(503, response.getStatus());
            assertTrue(f.retained().getFirst().completedAt().isEmpty());
          }
        }
    for (int offset : List.of(11, 60, 113, 212)) {
      reset();
      try (var f = new Fixture()) {
        UUID token = f.issue(FIXTURE_ROLE_7C85C916);
        f.updated = 1;
        f.responder =
            (id, bytes) -> {
              byte[] reply = f.reply(id, bytes);
              if (!ascii(bytes, 11, 8).equals(FIXTURE_UDTREQ01_DAA8B937))
                reply[offset] = (byte) '?';
              return reply;
            };
        var response = new MockHttpServletResponse();
        assertEquals(
            FIXTURE_ADMIN_USER_DETAIL_CC61E128,
            f.controller.change(
                42,
                f.change(FIXTURE_ROLE_7C85C916, token),
                actor(UserRole.ADMIN),
                new ExtendedModelMap(),
                f.request(FIXTURE_POST_E46D3AE9),
                response));
        assertEquals(503, response.getStatus());
        assertTrue(f.retained().getFirst().completedAt().isEmpty());
      }
    }
    reset();
    try (var f = new Fixture()) {
      UUID token = f.tokens.issue(f.session.sessionId(), FIXTURE_UCRREQ01_841A676A).token();
      f.updated = 1;
      var response = new MockHttpServletResponse();
      assertNull(
          f.controller.create(
              f.create(token),
              actor(UserRole.ADMIN),
              new ExtendedModelMap(),
              f.request(FIXTURE_POST_E46D3AE9),
              response));
      assertEquals(503, response.getStatus());
      assertTrue(f.retained().getFirst().completedAt().isEmpty());
    }
  }

  @Test
  void biz008MissingSessionStoreAndCompletionFailuresNeverReportSuccess() throws Exception {
    for (String operation : List.of(FIXTURE_CREATE_4DC7E48E, FIXTURE_ROLE_7C85C916))
      for (String fault :
          List.of("connection.commit", "connection.close", FIXTURE_DELETED_67A0D0C0)) {
        reset();
        try (var f = new Fixture()) {
          UUID token =
              operation.equals(FIXTURE_CREATE_4DC7E48E)
                  ? f.tokens.issue(f.session.sessionId(), FIXTURE_UCRREQ01_841A676A).token()
                  : f.issue(FIXTURE_ROLE_7C85C916);
          f.updated = operation.equals(FIXTURE_CREATE_4DC7E48E) ? 0 : 1;
          f.responder =
              (id, bytes) -> {
                byte[] reply = f.reply(id, bytes);
                if (!ascii(bytes, 11, 8).equals(FIXTURE_UDTREQ01_DAA8B937)) {
                  if (fault.equals(FIXTURE_DELETED_67A0D0C0))
                    f.security.f.repository.invalidate(f.session.sessionId());
                  else f.security.f.failure = fault;
                }
                return reply;
              };
          var response = new MockHttpServletResponse();
          if (operation.equals(FIXTURE_CREATE_4DC7E48E))
            f.controller.create(
                f.create(token),
                actor(UserRole.ADMIN),
                new ExtendedModelMap(),
                f.request(FIXTURE_POST_E46D3AE9),
                response);
          else
            f.controller.change(
                42,
                f.change(FIXTURE_ROLE_7C85C916, token),
                actor(UserRole.ADMIN),
                new ExtendedModelMap(),
                f.request(FIXTURE_POST_E46D3AE9),
                response);
          assertEquals(fault.equals(FIXTURE_DELETED_67A0D0C0) ? 409 : 503, response.getStatus());
          f.security.f.failure = "";
          if (!fault.equals(FIXTURE_DELETED_67A0D0C0))
            assertEquals(
                fault.equals("connection.close"),
                f.retained().getFirst().completedAt().isPresent());
          assertEquals(0, f.security.f.live.get());
        }
      }
    for (String method :
        List.of(FIXTURE_NEW_00A2B031, FIXTURE_DETAIL_3053326D, FIXTURE_CREATE_4DC7E48E, "CHANGE")) {
      reset();
      try (var f = new Fixture()) {
        var response = new MockHttpServletResponse();
        var request = f.request(FIXTURE_GET_04F32A7E);
        request.setSession(null);
        switch (method) {
          case FIXTURE_NEW_00A2B031 ->
              f.controller.newForm(
                  actor(UserRole.ADMIN), new ExtendedModelMap(), request, response);
          case FIXTURE_DETAIL_3053326D ->
              f.controller.detail(
                  42, actor(UserRole.ADMIN), new ExtendedModelMap(), request, response);
          case FIXTURE_CREATE_4DC7E48E ->
              f.controller.create(
                  f.create(new UUID(0, 999)),
                  actor(UserRole.ADMIN),
                  new ExtendedModelMap(),
                  request,
                  response);
          default ->
              f.controller.change(
                  42,
                  f.change(FIXTURE_ROLE_7C85C916, new UUID(0, 999)),
                  actor(UserRole.ADMIN),
                  new ExtendedModelMap(),
                  request,
                  response);
        }
        assertEquals(409, response.getStatus());
      }
    }
    for (String method :
        List.of(FIXTURE_NEW_00A2B031, FIXTURE_DETAIL_3053326D, FIXTURE_CREATE_4DC7E48E, "CHANGE")) {
      reset();
      try (var f = new Fixture()) {
        var response = new MockHttpServletResponse();
        f.security.f.failure = "open";
        switch (method) {
          case FIXTURE_NEW_00A2B031 ->
              f.controller.newForm(
                  actor(UserRole.ADMIN),
                  new ExtendedModelMap(),
                  f.request(FIXTURE_GET_04F32A7E),
                  response);
          case FIXTURE_DETAIL_3053326D ->
              f.controller.detail(
                  42,
                  actor(UserRole.ADMIN),
                  new ExtendedModelMap(),
                  f.request(FIXTURE_GET_04F32A7E),
                  response);
          case FIXTURE_CREATE_4DC7E48E ->
              f.controller.create(
                  f.create(new UUID(0, 999)),
                  actor(UserRole.ADMIN),
                  new ExtendedModelMap(),
                  f.request(FIXTURE_POST_E46D3AE9),
                  response);
          default ->
              f.controller.change(
                  42,
                  f.change(FIXTURE_ROLE_7C85C916, new UUID(0, 999)),
                  actor(UserRole.ADMIN),
                  new ExtendedModelMap(),
                  f.request(FIXTURE_POST_E46D3AE9),
                  response);
        }
        assertEquals(503, response.getStatus());
        assertEquals(0, f.security.f.live.get());
      }
    }
  }

  @Test
  void biz012AdministratorAndNullBoundariesLegacyAssemblyAndViewContract() throws Exception {
    try (var f = new Fixture()) {
      for (var controller :
          List.of(f.controller, new UserAdminController(f.client, f.security.handler))) {
        for (UserRole role : UserRole.values()) {
          if (controller == f.controller && role == UserRole.ADMIN) continue;
          var response = new MockHttpServletResponse();
          assertNull(
              controller.newForm(
                  actor(role), new ExtendedModelMap(), f.request(FIXTURE_GET_04F32A7E), response));
          assertEquals(role == UserRole.USER ? 403 : 503, response.getStatus());
          response = new MockHttpServletResponse();
          assertNull(
              controller.create(
                  f.create(new UUID(0, 999)),
                  actor(role),
                  new ExtendedModelMap(),
                  f.request(FIXTURE_POST_E46D3AE9),
                  response));
          assertEquals(role == UserRole.USER ? 403 : 503, response.getStatus());
          response = new MockHttpServletResponse();
          assertNull(
              controller.change(
                  42,
                  f.change(FIXTURE_ROLE_7C85C916, new UUID(0, 999)),
                  actor(role),
                  new ExtendedModelMap(),
                  f.request(FIXTURE_POST_E46D3AE9),
                  response));
          assertEquals(role == UserRole.USER ? 403 : 503, response.getStatus());
        }
      }
      assertThrows(
          NullPointerException.class,
          () -> new UserAdminController(f.client, f.security.handler, null));
      assertThrows(
          NullPointerException.class,
          () -> new UserAdminController(null, f.security.handler, f.tokens));
      assertThrows(
          NullPointerException.class, () -> new UserAdminController(f.client, null, f.tokens));
      var request = f.request(FIXTURE_GET_04F32A7E);
      var response = new MockHttpServletResponse();
      var model = new ExtendedModelMap();
      assertThrows(
          SessionStoreException.class,
          () -> f.controller.newForm(() -> "foreign", model, request, response));
      assertThrows(
          NullPointerException.class, () -> f.controller.newForm(null, model, request, response));
      assertThrows(
          NullPointerException.class,
          () -> f.controller.newForm(actor(UserRole.ADMIN), null, request, response));
      assertThrows(
          NullPointerException.class,
          () -> f.controller.newForm(actor(UserRole.ADMIN), model, null, response));
      assertThrows(
          NullPointerException.class,
          () -> f.controller.newForm(actor(UserRole.ADMIN), model, request, null));
      assertThrows(
          NullPointerException.class,
          () -> f.controller.create(null, actor(UserRole.ADMIN), model, request, response));
      assertThrows(
          NullPointerException.class,
          () -> f.controller.change(42, null, actor(UserRole.ADMIN), model, request, response));
      var bad = params();
      bad.put(FIXTURE_OPERATION_063BD517, Arrays.asList((String) null));
      assertThrows(
          NullPointerException.class,
          () -> f.controller.change(42, bad, actor(UserRole.ADMIN), model, request, response));
      var nullToken = params(FIXTURE_OPERATION_063BD517, FIXTURE_ROLE_7C85C916);
      nullToken.put(FIXTURE_OPERATION_TOKEN_6C771227, Arrays.asList((String) null));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.change(42, nullToken, actor(UserRole.ADMIN), model, request, response));
      assertThrows(
          NullPointerException.class, () -> UserCreateViewModel.newForm(null, new UUID(0, 1)));
      assertThrows(
          NullPointerException.class,
          () -> UserCreateViewModel.newForm(actor(UserRole.ADMIN), null));
      assertThrows(
          NullPointerException.class,
          () ->
              UserCreateViewModel.redisplay(
                  actor(UserRole.ADMIN), null, new UUID(0, 1), "", false));
      request.setSession(new MockHttpSession(null, "invalid"));
      assertNull(f.controller.newForm(actor(UserRole.ADMIN), model, request, response));
      assertEquals(409, response.getStatus());
    }
  }

  @Test
  void biz011HundredSamePostRealApiUpdatesOnceAndConsumesOneToken() throws Exception {
    try (var f = new Fixture();
        var api = new RealApi(f)) {
      var createToken = f.tokens.issue(f.session.sessionId(), FIXTURE_UCRREQ01_841A676A).token();
      var response = new MockHttpServletResponse();
      assertNull(
          f.controller.create(
              f.create(createToken),
              actor(UserRole.ADMIN),
              new ExtendedModelMap(),
              f.request(FIXTURE_POST_E46D3AE9),
              response));
      UUID token = f.issue(FIXTURE_STATUS_0ABCCBF8);
      try (var executor = Executors.newFixedThreadPool(8)) {
        var futures = new ArrayList<Future<?>>();
        for (int n = 0; n < 100; n++)
          futures.add(
              executor.submit(
                  () -> {
                    var result = new MockHttpServletResponse();
                    assertNull(
                        f.controller.change(
                            42,
                            f.change(FIXTURE_STATUS_0ABCCBF8, token),
                            actor(UserRole.ADMIN),
                            new ExtendedModelMap(),
                            f.request(FIXTURE_POST_E46D3AE9),
                            result));
                    assertEquals(302, result.getStatus());
                    assertEquals(
                        FIXTURE_ADMIN_USERS_42_65AE9E81,
                        result.getHeader(FIXTURE_LOCATION_FB077BAD));
                    return null;
                  }));
        for (var future : futures) future.get(60, TimeUnit.SECONDS);
      }
      assertEquals(1, api.scalar("select version from schubert.app_users where id=42"));
      for (String category : List.of("ACTION", "SECURITY"))
        assertEquals(
            1,
            api.scalar(
                "select count(*) from schubert.app_logs where action='USER_STATUS_CHANGED' and category='"
                    + category
                    + "' and details->>'outcome'='SUCCESS' and details->>'targetUserId'='42'"));
      assertEquals(
          99, api.scalar("select count(*) from schubert.app_logs where action='INBOX_REPLAYED'"));
      assertEquals(
          100,
          f.sent.stream()
              .filter(bytes -> ascii(bytes, 11, 8).equals(FIXTURE_USTREQ01_D6E6CD9B))
              .map(bytes -> ascii(bytes, 24, 36))
              .distinct()
              .count());
      assertEquals(2, f.retained().size());
      assertEquals(2, f.tokenIds.get());
      assertTrue(f.retained().stream().allMatch(t -> t.completedAt().isPresent()));
      f.erased();
    }
  }

  @Test
  void biz010RealApiCreateZeroDetailFirstUpdateOneAndIdempotency() throws Exception {
    try (var f = new Fixture();
        var api = new RealApi(f)) {
      UUID token = f.tokens.issue(f.session.sessionId(), FIXTURE_UCRREQ01_841A676A).token();
      var response = new MockHttpServletResponse();
      assertNull(
          f.controller.create(
              f.create(token),
              actor(UserRole.ADMIN),
              new ExtendedModelMap(),
              f.request(FIXTURE_POST_E46D3AE9),
              response));
      assertEquals(302, response.getStatus());
      assertEquals(FIXTURE_ADMIN_USERS_42_65AE9E81, response.getHeader(FIXTURE_LOCATION_FB077BAD));
      assertEquals(0, api.scalar("select version from schubert.app_users where id=42"));
      var model = new ExtendedModelMap();
      response = new MockHttpServletResponse();
      assertEquals(
          FIXTURE_ADMIN_USER_DETAIL_CC61E128,
          f.controller.detail(
              42, actor(UserRole.ADMIN), model, f.request(FIXTURE_GET_04F32A7E), response));
      assertEquals(
          0L, ((UserDetailViewModel) model.get(FIXTURE_PAGE_861424BC)).getValues().get("version"));
      UUID statusToken =
          f.retained().stream()
              .filter(t -> t.purpose().equals(FIXTURE_USTREQ01_D6E6CD9B))
              .findFirst()
              .orElseThrow()
              .token();
      var input = f.change(FIXTURE_STATUS_0ABCCBF8, statusToken);
      response = new MockHttpServletResponse();
      assertNull(
          f.controller.change(
              42, input, actor(UserRole.ADMIN), model, f.request(FIXTURE_POST_E46D3AE9), response));
      assertEquals(302, response.getStatus());
      assertEquals(1, api.scalar("select version from schubert.app_users where id=42"));
      assertEquals(
          1,
          api.scalar("select count(*) from schubert.app_users where id=42 and status='DISABLED'"));
      response = new MockHttpServletResponse();
      assertNull(
          f.controller.change(
              42, input, actor(UserRole.ADMIN), model, f.request(FIXTURE_POST_E46D3AE9), response));
      assertEquals(302, response.getStatus());
      assertEquals(1, api.scalar("select version from schubert.app_users where id=42"));
      for (String category : List.of("ACTION", "SECURITY")) {
        assertEquals(
            1,
            api.scalar(
                "select count(*) from schubert.app_logs where action='USER_CREATED' and category='"
                    + category
                    + "' and details->>'outcome'='SUCCESS' and details->>'targetUserId'='42'"));
        assertEquals(
            1,
            api.scalar(
                "select count(*) from schubert.app_logs where action='USER_STATUS_CHANGED' and category='"
                    + category
                    + "' and details->>'outcome'='SUCCESS' and details->>'targetUserId'='42'"));
      }
      var different = f.change(FIXTURE_STATUS_0ABCCBF8, statusToken);
      different.set(FIXTURE_ENABLED_6E30BC5C, FIXTURE_TRUE_18D10C7D);
      response = new MockHttpServletResponse();
      assertEquals(
          FIXTURE_ADMIN_USER_DETAIL_CC61E128,
          f.controller.change(
              42,
              different,
              actor(UserRole.ADMIN),
              model,
              f.request(FIXTURE_POST_E46D3AE9),
              response));
      assertEquals(409, response.getStatus());
      assertEquals(1, api.scalar("select version from schubert.app_users where id=42"));
      UUID roleToken = f.issue(FIXTURE_ROLE_7C85C916);
      var role = f.change(FIXTURE_ROLE_7C85C916, roleToken);
      role.set(FIXTURE_EXPECTED_VERSION_633674D2, "1");
      role.set(FIXTURE_ROLE_2BC933AF, "ADMIN");
      response = new MockHttpServletResponse();
      assertNull(
          f.controller.change(
              42, role, actor(UserRole.ADMIN), model, f.request(FIXTURE_POST_E46D3AE9), response));
      assertEquals(302, response.getStatus());
      assertEquals(
          2, api.scalar("select version from schubert.app_users where id=42 and role='ADMIN'"));
      for (String category : List.of("ACTION", "SECURITY"))
        assertEquals(
            1,
            api.scalar(
                "select count(*) from schubert.app_logs where action='USER_ROLE_CHANGED' and category='"
                    + category
                    + "' and details->>'outcome'='SUCCESS' and details->>'targetUserId'='42'"));
      UUID unlockToken = f.issue(FIXTURE_UNLOCK_351153DC);
      var unlock = f.change(FIXTURE_UNLOCK_351153DC, unlockToken);
      unlock.set(FIXTURE_EXPECTED_VERSION_633674D2, "2");
      response = new MockHttpServletResponse();
      assertNull(
          f.controller.change(
              42,
              unlock,
              actor(UserRole.ADMIN),
              model,
              f.request(FIXTURE_POST_E46D3AE9),
              response));
      assertEquals(302, response.getStatus());
      assertEquals(2, api.scalar("select version from schubert.app_users where id=42"));
      assertEquals(
          1,
          api.scalar(
              "select count(*) from schubert.app_logs where action='USER_UNLOCKED' and category='SECURITY' and details->>'resultCode'='0200'"));
      UUID passwordToken = f.issue(FIXTURE_PASSWORD_FC2A3EAA);
      var password = f.change(FIXTURE_PASSWORD_FC2A3EAA, passwordToken);
      password.set(FIXTURE_EXPECTED_VERSION_633674D2, "2");
      response = new MockHttpServletResponse();
      assertNull(
          f.controller.change(
              42,
              password,
              actor(UserRole.ADMIN),
              model,
              f.request(FIXTURE_POST_E46D3AE9),
              response));
      assertEquals(302, response.getStatus());
      assertEquals(FIXTURE_ADMIN_USERS_42_65AE9E81, response.getHeader(FIXTURE_LOCATION_FB077BAD));
      assertEquals(3, api.scalar("select version from schubert.app_users where id=42"));
      assertEquals(
          1,
          api.scalar(
              "select count(*) from schubert.app_logs where action='USER_PASSWORD_RESET' and category='SECURITY' and details->>'targetUserId'='42'"));
      f.erased();
    }
  }

  @Test
  void biz010RealLockedUnlockAndStoredIncrementedVersion() throws Exception {
    try (var f = new Fixture();
        var api = new RealApi(f)) {
      UUID createToken = f.tokens.issue(f.session.sessionId(), FIXTURE_UCRREQ01_841A676A).token();
      var response = new MockHttpServletResponse();
      assertNull(
          f.controller.create(
              f.create(createToken),
              actor(UserRole.ADMIN),
              new ExtendedModelMap(),
              f.request(FIXTURE_POST_E46D3AE9),
              response));
      assertEquals(302, response.getStatus());
      try (var connection = db.admin();
          var statement =
              connection.prepareStatement(
                  "UPDATE schubert.app_users SET locked_until=?,failed_count=5 WHERE id=42")) {
        statement.setObject(
            1, f.security.f.clock.instant().plusSeconds(60).atOffset(ZoneOffset.UTC));
        assertEquals(1, statement.executeUpdate());
      }
      var model = new ExtendedModelMap();
      response = new MockHttpServletResponse();
      assertEquals(
          FIXTURE_ADMIN_USER_DETAIL_CC61E128,
          f.controller.detail(
              42, actor(UserRole.ADMIN), model, f.request(FIXTURE_GET_04F32A7E), response));
      UUID token =
          f.retained().stream()
              .filter(t -> t.purpose().equals("ULKREQ01"))
              .findFirst()
              .orElseThrow()
              .token();
      var input = f.change(FIXTURE_UNLOCK_351153DC, token);
      for (int attempt = 0; attempt < 2; attempt++) {
        response = new MockHttpServletResponse();
        assertNull(
            f.controller.change(
                42,
                input,
                actor(UserRole.ADMIN),
                model,
                f.request(FIXTURE_POST_E46D3AE9),
                response));
        assertEquals(302, response.getStatus());
        assertEquals(
            FIXTURE_ADMIN_USERS_42_65AE9E81, response.getHeader(FIXTURE_LOCATION_FB077BAD));
        assertEquals(
            1,
            api.scalar(
                "SELECT count(*) FROM schubert.app_users WHERE id=42 AND version=1 AND failed_count=0 AND locked_until IS NULL"));
      }
      assertEquals(
          1,
          api.scalar(
              "SELECT count(*) FROM schubert.app_logs WHERE action='USER_UNLOCKED' AND category='SECURITY' AND details->>'targetUserId'='42' AND details->>'resultCode'='0000'"));
      assertEquals(
          1, api.scalar("SELECT count(*) FROM schubert.app_logs WHERE action='INBOX_REPLAYED'"));
      assertTrue(
          f.retained().stream()
              .filter(t -> t.token().equals(token))
              .findFirst()
              .orElseThrow()
              .completedAt()
              .isPresent());
      assertEquals(0, f.security.f.live.get());
      f.erased();
    }
  }

  @Test
  void biz009RealHttpSameCoreCsrfAndVerifiedSelfReset() throws Exception {
    try (var f = new Fixture()) {
      reset(); // No second fixed fixture identity may collide with the real HTTP core.
      var loginApi =
          new SessionFormLoginTest.Api(FIXTURE_0000_876EEFE0, "ADMIN", FIXTURE_0000_876EEFE0, 0);
      try (var api = new RealApi(f);
          var server =
              new EmbeddedWebSecurityTest.Server(
                  root,
                  false,
                  db,
                  Optional.of(loginApi.provider),
                  true,
                  false,
                  (mvc, invalid) -> {
                    mvc.register(UserBusinessMvcConfiguration.class);
                    mvc.addBeanFactoryPostProcessor(
                        factory -> {
                          factory.registerSingleton("userAdministrationWireClient", f.client);
                          factory.registerSingleton("apiSessionInvalidHandler", invalid);
                        });
                  },
                  (mvc, core) ->
                      mvc.addBeanFactoryPostProcessor(
                          factory ->
                              factory.registerSingleton(
                                  "sessionOperationTokenLifecycle",
                                  new SessionOperationTokenLifecycle(
                                      core, java.time.Clock.systemUTC()))))) {
        var page = server.send(FIXTURE_GET_04F32A7E, "/login", null, null, true);
        String cookie = page.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
        assertTrue(page.body().startsWith("TOKEN:"));
        String csrf = page.body().substring(6);
        assertFalse(csrf.isEmpty());
        var login =
            server.send(
                FIXTURE_POST_E46D3AE9,
                "/login",
                cookie,
                "username=admin&password=longpassword1&_csrf=" + csrf,
                true);
        assertEquals(302, login.statusCode());
        cookie = login.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
        page =
            server.send(FIXTURE_GET_04F32A7E, FIXTURE_ADMIN_USERS_NEW_88CAF2E8, cookie, null, true);
        assertEquals(200, page.statusCode());
        var dom = Jsoup.parse(page.body());
        String token = dom.select("input[name=operation_token]").attr(FIXTURE_VALUE_A0B7821A);
        assertEquals(1, dom.select("form[data-operation-submit]").size());
        assertEquals(
            List.of(FIXTURE_JS_OPERATION_POST_SUBMIT_JS_04D3D42D),
            dom.select("script[src][defer]").eachAttr("src"));
        var asset =
            server.send(
                FIXTURE_GET_04F32A7E,
                FIXTURE_JS_OPERATION_POST_SUBMIT_JS_04D3D42D,
                cookie,
                null,
                true);
        assertEquals(200, asset.statusCode());
        assertEquals(
            Files.readString(Path.of("src/main/resources/static/js/operation-post-submit.js")),
            asset.body());
        csrf =
            dom.select("form[action='/admin/users/new'] input[name=_csrf]")
                .attr(FIXTURE_VALUE_A0B7821A);
        String body =
            "username=new-user&password=longpassword1&password_confirmation=longpassword1&role=USER&enabled=true&operation_token="
                + token;
        int before = f.sent.size();
        assertEquals(
            403,
            server
                .send(
                    FIXTURE_POST_E46D3AE9,
                    FIXTURE_ADMIN_USERS_NEW_88CAF2E8,
                    cookie,
                    body + "&_csrf=bad",
                    true)
                .statusCode());
        assertEquals(before, f.sent.size());
        assertEquals(
            302,
            server
                .send(
                    FIXTURE_POST_E46D3AE9,
                    FIXTURE_ADMIN_USERS_NEW_88CAF2E8,
                    cookie,
                    body + "&_csrf=" + csrf,
                    true)
                .statusCode());
        assertEquals(0, api.scalar("select version from schubert.app_users where id=42"));
        page = server.send(FIXTURE_GET_04F32A7E, "/admin/users/1", cookie, null, true);
        assertEquals(200, page.statusCode());
        dom = Jsoup.parse(page.body());
        assertEquals(
            List.of(FIXTURE_PASSWORD_FC2A3EAA),
            dom.select("form[data-operation]").eachAttr("data-operation"));
        token =
            dom.select("form[data-operation=PASSWORD] input[name=operation_token]")
                .attr(FIXTURE_VALUE_A0B7821A);
        csrf =
            dom.select("form[data-operation=PASSWORD] input[name=_csrf]")
                .attr(FIXTURE_VALUE_A0B7821A);
        var changed =
            server.send(
                FIXTURE_POST_E46D3AE9,
                "/admin/users/1",
                cookie,
                "operation=PASSWORD&id=1&expected_version=0&confirm=true&password=longpassword2&password_confirmation=longpassword2&operation_token="
                    + token
                    + "&_csrf="
                    + csrf,
                true);
        assertEquals(302, changed.statusCode());
        assertEquals("/login", changed.headers().firstValue("location").orElseThrow());
        assertTrue(changed.headers().firstValue("set-cookie").orElseThrow().contains("Max-Age=0"));
        assertEquals(1, api.scalar("select version from schubert.app_users where id=1"));
        assertEquals(
            1,
            api.scalar("select count(*) from schubert.auth_sessions where user_id=1 and revoked"));
        assertEquals(0, api.scalar("select count(*) from schubert_web_session.web_http_sessions"));
        assertEquals(
            1,
            api.scalar(
                "select count(*) from schubert.app_logs where action='USER_PASSWORD_RESET'"));
        assertTrue(
            server.log.events.stream()
                .noneMatch(event -> event.get("action").getAsString().equals("SESSION_EXPIRED")));
        assertEquals(
            0, f.sent.stream().filter(bytes -> ascii(bytes, 11, 8).equals("LOGREQ01")).count());
        assertEquals(
            302,
            server
                .send(FIXTURE_GET_04F32A7E, FIXTURE_ADMIN_USERS_NEW_88CAF2E8, cookie, null, true)
                .statusCode());
      }
    }
  }

  static final class RealApi implements AutoCloseable {
    final Fixture fixture;
    final FingerprintKeyRing fingerprints = new FingerprintKeyRing("pt", new byte[32], null, null);
    final ResponseSnapshotCodec snapshots =
        new ResponseSnapshotCodec("pt", new byte[32], null, null);

    RealApi(Fixture fixture) throws Exception {
      this.fixture = fixture;
      try (var c = db.admin();
          var s = c.createStatement()) {
        s.execute("TRUNCATE schubert.app_logs"); // BUG644: historical audit has no User FK.
        s.execute("TRUNCATE schubert.app_users RESTART IDENTITY CASCADE");
        s.execute(
            "INSERT INTO schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) VALUES(1,'admin','admin','unused-synthetic-hash','ADMIN','ACTIVE','2026-10-04T00:00:00Z','2026-10-04T00:00:00Z','2026-10-04T00:00:00Z')");
        s.execute("SELECT setval('schubert.app_users_id_seq',41,true)");
      }
      try (var c = db.api();
          var s =
              c.prepareStatement(
                  "INSERT INTO schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id) VALUES(?,1,?,?,'pt',?,?,?,'192.0.2.99',?)")) {
        Instant now = fixture.security.f.clock.instant();
        s.setObject(1, new UUID(901, 1));
        s.setString(
            2,
            HexFormat.of()
                .formatHex(
                    MessageDigest.getInstance("SHA-256")
                        .digest("a".repeat(64).getBytes(StandardCharsets.US_ASCII))));
        s.setBytes(3, new byte[29]);
        s.setObject(4, now.minusSeconds(60).atOffset(ZoneOffset.UTC));
        s.setObject(5, now.minusSeconds(60).atOffset(ZoneOffset.UTC));
        s.setObject(6, now.plusSeconds(28800).atOffset(ZoneOffset.UTC));
        s.setObject(7, new UUID(902, 1));
        assertEquals(1, s.executeUpdate());
      }
      DataSource source =
          (DataSource)
              Proxy.newProxyInstance(
                  DataSource.class.getClassLoader(),
                  new Class<?>[] {DataSource.class},
                  (proxy, method, args) -> {
                    if (!method.getName().equals("getConnection"))
                      throw new AssertionError("unexpected datasource call");
                    return db.api();
                  });
      var query =
          UserApplicationAssembly.queries(
              source, fingerprints, snapshots, fixture.security.f.clock);
      var mutation =
          UserApplicationAssembly.mutations(
              source, fingerprints, snapshots, fixture.security.f.clock);
      fixture.responder =
          (id, body) -> {
            var layout = new LayoutId(ascii(body, 11, 8));
            var metadata =
                new TransportMetadata(
                    TransportBodyType.BYTES,
                    "ID:synthetic-" + id,
                    id,
                    Optional.of("nk.sync.reply.web"),
                    fixture.security.f.clock.instant().plusSeconds(5).toEpochMilli(),
                    2,
                    1,
                    id,
                    layout,
                    "001",
                    "nk.sync.request");
            var route =
                new ExpectedRoute(
                    MessageKind.REQUEST,
                    InteractionKind.SYNCHRONOUS,
                    "nk.sync.request",
                    Optional.of("nk.sync.reply.web"),
                    true);
            var message = FixedWidthDecoder.standard().decode(body, metadata, route);
            assertEquals(
                0,
                fixture.security.f.threadLive.getOrDefault(Thread.currentThread(), 0),
                "no sending-thread local DB transaction while API runs");
            return layout.value().equals(FIXTURE_UDTREQ01_DAA8B937)
                ? query.process(message)
                : mutation.process(message);
          };
    }

    long scalar(String sql) throws Exception {
      try (var c = db.admin();
          var s = c.createStatement();
          var r = s.executeQuery(sql)) {
        assertTrue(r.next());
        return r.getLong(1);
      }
    }

    @Override
    public void close() {
      snapshots.close();
      fingerprints.close();
    }
  }

  @Test
  void biz007GenuineInvalidCreateAndChangeTerminateWithoutConsumption() throws Exception {
    for (String operation : List.of(FIXTURE_CREATE_4DC7E48E, FIXTURE_STATUS_0ABCCBF8)) {
      reset();
      try (var f = new Fixture()) {
        UUID token =
            operation.equals(FIXTURE_CREATE_4DC7E48E)
                ? f.tokens.issue(f.session.sessionId(), FIXTURE_UCRREQ01_841A676A).token()
                : f.issue(FIXTURE_STATUS_0ABCCBF8);
        f.code = "0102";
        var request = f.request(FIXTURE_POST_E46D3AE9);
        var response = new MockHttpServletResponse();
        var session = request.getSession(false);
        if (operation.equals(FIXTURE_CREATE_4DC7E48E))
          assertNull(
              f.controller.create(
                  f.create(token),
                  actor(UserRole.ADMIN),
                  new ExtendedModelMap(),
                  request,
                  response));
        else
          assertNull(
              f.controller.change(
                  42,
                  f.change(FIXTURE_STATUS_0ABCCBF8, token),
                  actor(UserRole.ADMIN),
                  new ExtendedModelMap(),
                  request,
                  response));
        assertEquals(401, response.getStatus());
        assertTrue(((MockHttpSession) session).isInvalid());
        assertNull(SecurityContextHolder.getContext().getAuthentication());
        assertEquals(1, f.security.log.events.size());
        assertEquals(
            "SESSION_EXPIRED", f.security.log.events.getFirst().get("action").getAsString());
        assertTrue(f.retained().getFirst().completedAt().isEmpty());
      }
    }
  }

  @Test
  void biz008UnknownReadAndMutationCannotContinueOrGenerateNewToken() throws Exception {
    for (String variant : List.of(FIXTURE_PASSWORD_FC2A3EAA, "REDISPLAY", "TRANSPORT")) {
      reset();
      try (var f = new Fixture()) {
        String operation =
            variant.equals(FIXTURE_PASSWORD_FC2A3EAA)
                ? FIXTURE_PASSWORD_FC2A3EAA
                : FIXTURE_ROLE_7C85C916;
        UUID token = f.issue(operation);
        var input = f.change(operation, token);
        if (variant.equals("REDISPLAY")) input.set(FIXTURE_ROLE_2BC933AF, "UNKNOWN");
        f.responder =
            (id, bytes) -> {
              boolean detail = ascii(bytes, 11, 8).equals(FIXTURE_UDTREQ01_DAA8B937);
              if (detail != variant.equals("TRANSPORT"))
                throw new jakarta.jms.JMSRuntimeException("private-transport-marker");
              return f.reply(id, bytes);
            };
        var response = new MockHttpServletResponse();
        String result =
            f.controller.change(
                42,
                input,
                actor(UserRole.ADMIN),
                new ExtendedModelMap(),
                f.request(FIXTURE_POST_E46D3AE9),
                response);
        assertEquals(
            variant.equals("TRANSPORT") ? FIXTURE_ADMIN_USER_DETAIL_CC61E128 : null, result);
        assertEquals(503, response.getStatus());
        assertTrue(f.retained().getFirst().completedAt().isEmpty());
        assertEquals(1, f.tokenIds.get());
        f.erased();
      }
    }
    reset();
    try (var f = new Fixture()) {
      var response = new MockHttpServletResponse();
      assertNull(
          f.controller.create(
              params(),
              actor(UserRole.ADMIN),
              new ExtendedModelMap(),
              f.request(FIXTURE_POST_E46D3AE9),
              response));
      assertEquals(400, response.getStatus());
      assertTrue(f.sent.isEmpty());
      assertEquals(0, f.tokenIds.get());
    }
  }

  static final Map<String, String> PURPOSES =
      Map.of(
          FIXTURE_STATUS_0ABCCBF8,
          FIXTURE_USTREQ01_D6E6CD9B,
          FIXTURE_ROLE_7C85C916,
          "URLREQ01",
          FIXTURE_PASSWORD_FC2A3EAA,
          "UPWREQ01",
          FIXTURE_UNLOCK_351153DC,
          "ULKREQ01");

  static final class Fixture implements AutoCloseable {
    final ApiSessionInvalidTest.Harness security = new ApiSessionInvalidTest.Harness(db);
    final WebSessionSnapshot session = security.authenticated(actor(UserRole.ADMIN));
    final AtomicLong tokenIds = new AtomicLong();
    final AtomicLong messageIds = new AtomicLong();
    final SessionOperationTokenLifecycle tokens =
        new SessionOperationTokenLifecycle(
            security.f.repository,
            security.f.clock,
            () -> new UUID(0, 100 + tokenIds.incrementAndGet()));
    final JmsRequestReplyClient wire =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), security.f.clock, 12);
    final List<byte[]> sent = new CopyOnWriteArrayList<>();
    final List<byte[]> buffers = new CopyOnWriteArrayList<>();
    String code = FIXTURE_0000_876EEFE0;
    String username = "target";
    String state = "ACTIVE";
    long version = 0;
    long updated = 0;
    long target = 42;
    BiFunction<UUID, byte[], byte[]> responder = this::reply;
    final UserAdministrationWireClient client =
        new UserAdministrationWireClient(
            wire,
            (id, bytes) -> {
              sent.add(bytes.clone());
              buffers.add(bytes);
              assertTrue(wire.onReply(id, responder.apply(id, bytes)));
            },
            security.f.clock,
            () -> new UUID(0, messageIds.incrementAndGet()),
            Duration.ofSeconds(1));
    final UserAdminController controller =
        new UserAdminController(client, security.handler, tokens);

    MockHttpSession httpSession() {
      return new MockHttpSession(null, session.sessionId().cookieValue());
    }

    MockHttpServletRequest request(String method) throws Exception {
      var request = security.mock(method, FIXTURE_ADMIN_USERS_42_65AE9E81);
      request.setSession(httpSession());
      return request;
    }

    List<SessionOperationToken> retained() {
      return security
          .f
          .repository
          .find(session.sessionId())
          .orElseThrow()
          .attributes()
          .operationTokens();
    }

    UUID issue(String operation) {
      return tokens
          .issue(session.sessionId(), Objects.requireNonNull(PURPOSES.get(operation)))
          .token();
    }

    LinkedMultiValueMap<String, String> create(UUID token) {
      return params(
          "username",
          "new-user",
          FIXTURE_PASSWORD_FF2BEA10,
          FIXTURE_LONGPASSWORD1_DA4ADD07,
          "password_confirmation",
          FIXTURE_LONGPASSWORD1_DA4ADD07,
          FIXTURE_ROLE_2BC933AF,
          FIXTURE_USER_2DED8884,
          FIXTURE_ENABLED_6E30BC5C,
          FIXTURE_TRUE_18D10C7D,
          FIXTURE_OPERATION_TOKEN_6C771227,
          token.toString());
    }

    LinkedMultiValueMap<String, String> change(String operation, UUID token) {
      var input =
          params(
              FIXTURE_OPERATION_063BD517,
              operation,
              "id",
              "42",
              FIXTURE_EXPECTED_VERSION_633674D2,
              "0",
              "confirm",
              FIXTURE_TRUE_18D10C7D,
              FIXTURE_OPERATION_TOKEN_6C771227,
              token.toString());
      switch (operation) {
        case FIXTURE_STATUS_0ABCCBF8 -> input.add(FIXTURE_ENABLED_6E30BC5C, "false");
        case FIXTURE_ROLE_7C85C916 -> input.add(FIXTURE_ROLE_2BC933AF, FIXTURE_USER_2DED8884);
        case FIXTURE_PASSWORD_FC2A3EAA -> {
          input.add(FIXTURE_PASSWORD_FF2BEA10, FIXTURE_LONGPASSWORD1_DA4ADD07);
          input.add("password_confirmation", FIXTURE_LONGPASSWORD1_DA4ADD07);
        }
        default -> {}
      }
      return input;
    }

    AnnotationConfigWebApplicationContext mvc() {
      var context = new AnnotationConfigWebApplicationContext();
      context.setServletContext(new MockServletContext());
      context.register(UserBusinessMvcConfiguration.class);
      context.addBeanFactoryPostProcessor(
          factory -> {
            factory.registerSingleton("userAdministrationWireClient", client);
            factory.registerSingleton("apiSessionInvalidHandler", security.handler);
            factory.registerSingleton("sessionOperationTokenLifecycle", tokens);
          });
      context.refresh();
      return context;
    }

    byte[] reply(UUID id, byte[] request) {
      String layout = ascii(request, 11, 8);
      boolean detail = layout.equals(FIXTURE_UDTREQ01_DAA8B937);
      String result = detail ? FIXTURE_0000_876EEFE0 : code;
      byte[] bytes = blank(detail ? 576 : 280);
      put(bytes, 0, "SCHBNK01");
      put(bytes, 8, "001");
      put(bytes, 11, layout.substring(0, 3) + "RSP01");
      put(bytes, 19, "001");
      put(bytes, 22, "SS");
      put(bytes, 24, new UUID(1, id.getLeastSignificantBits()).toString());
      put(bytes, 60, id.toString());
      put(bytes, 96, "20261004090000000");
      put(bytes, 113, ascii(request, 113, 64));
      put(bytes, 177, "0256");
      put(bytes, 181, detail ? "000320" : "000024");
      put(bytes, 187, "000000");
      put(bytes, 193, "000000");
      number(bytes, 199, 9, bytes.length);
      put(bytes, 208, result);
      if (detail) {
        number(bytes, 256, 12, 42);
        put(bytes, 268, username);
        put(bytes, 332, FIXTURE_USER_2DED8884);
        put(bytes, 337, state);
        for (int offset : List.of(379, 396, 413)) put(bytes, offset, "20261004090000000");
        put(bytes, 430, "000");
        number(bytes, 433, 9, version);
        put(bytes, 442, "SYSTEM");
        put(bytes, 506, "admin");
      } else {
        boolean success =
            result.equals(FIXTURE_0000_876EEFE0) || result.equals(FIXTURE_0200_FC9DB3AC);
        number(bytes, 256, 12, success ? target : 0);
        number(bytes, 268, 9, success ? updated : 0);
      }
      return bytes;
    }

    void erased() {
      assertEquals(0, wire.pendingCount());
      for (byte[] bytes : buffers) assertArrayEquals(new byte[bytes.length], bytes);
      assertEquals(0, security.f.live.get());
    }

    @Override
    public void close() {
      for (byte[] bytes : sent) Arrays.fill(bytes, (byte) 0);
      security.close();
    }
  }

  static byte[] blank(int count) {
    byte[] bytes = new byte[count];
    Arrays.fill(bytes, (byte) ' ');
    return bytes;
  }

  static void put(byte[] bytes, int offset, String text) {
    byte[] value = text.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(value, 0, bytes, offset, value.length);
  }

  static void number(byte[] bytes, int offset, int width, long value) {
    put(bytes, offset, String.format(Locale.ROOT, "%0" + width + "d", value));
  }

  static String ascii(byte[] bytes, int offset, int count) {
    return new String(bytes, offset, count, StandardCharsets.US_ASCII);
  }
}
