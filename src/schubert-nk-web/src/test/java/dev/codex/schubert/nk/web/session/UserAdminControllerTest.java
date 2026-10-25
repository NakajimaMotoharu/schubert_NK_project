package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.head;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.admin.UserRecord;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import dev.codex.schubert.nk.web.config.UserMvcConfiguration;
import dev.codex.schubert.nk.web.controller.UserAdminController;
import dev.codex.schubert.nk.web.form.UserSearchForm;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.messaging.UserAdministrationWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.view.UserDetailViewModel;
import dev.codex.schubert.nk.web.view.UserListViewModel;
import jakarta.jms.JMSRuntimeException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BiFunction;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockServletContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;

/** UI232/236 byte and DOM literals, not production-generated expected. PG-D344/016053. */
class UserAdminControllerTest {
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-10-03T00:00:00Z"), ZoneOffset.UTC);
  private static WebLogDatabaseFixture db;
  @TempDir Path root;

  @BeforeAll
  static void start(@TempDir Path path) throws Exception {
    db = new WebLogDatabaseFixture(path);
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

  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(
        "reader", role, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
  }

  private static LinkedMultiValueMap<String, String> params(String... pairs) {
    var result = new LinkedMultiValueMap<String, String>();
    for (int i = 0; i < pairs.length; i += 2) result.add(pairs[i], pairs[i + 1]);
    return result;
  }

  private static MockHttpServletRequest raw() {
    var result = new MockHttpServletRequest("GET", "/admin/users");
    result.setRemoteAddr("127.0.0.1");
    return result;
  }

  private static CsrfToken csrf() {
    return new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", "b".repeat(64));
  }

  private static void configure(
      AnnotationConfigWebApplicationContext context,
      UserAdministrationWireClient client,
      ApiSessionInvalidHandler invalid) {
    context.register(UserMvcConfiguration.class);
    context.addBeanFactoryPostProcessor(
        f -> {
          f.registerSingleton("userAdministrationWireClient", client);
          f.registerSingleton("apiSessionInvalidHandler", invalid);
        });
  }

  @Test
  void user001IndependentWholeByteAndAllPageSizes() throws Exception {
    try (var f = new Fixture()) {
      for (String code : List.of("0000", "0200"))
        for (int count : new int[] {0, 1, 50}) {
          f.code = code;
          f.count = count;
          f.total = count;
          var model = new ExtendedModelMap();
          var response = new MockHttpServletResponse();
          assertEquals(
              "admin/user-list",
              f.controller.list(
                  params("username", " e\u0301 ", "role", "ADMIN", "state", "LOCKED", "page", "1"),
                  actor(UserRole.ADMIN),
                  model,
                  raw(),
                  response));
          assertEquals(200, response.getStatus());
          var page = assertInstanceOf(UserListViewModel.class, model.get("page"));
          assertEquals(count, page.getRows().size());
          assertEquals("ADMIN", page.getTopBar().getRole());
          byte[] sent = f.requests.getLast();
          assertEquals(352, sent.length);
          assertEquals("USRREQ01", ascii(sent, 11, 8));
          assertEquals("a".repeat(64), ascii(sent, 113, 64));
          assertEquals(
              f.requests.size(), UUID.fromString(ascii(sent, 24, 36)).getLeastSignificantBits());
          byte[] expected = new byte[96];
          Arrays.fill(expected, (byte) ' ');
          put(expected, 0, 64, "é");
          put(expected, 64, 5, "ADMIN");
          put(expected, 69, 8, "LOCKED");
          number(expected, 77, 6, 1);
          number(expected, 83, 3, 50);
          assertArrayEquals(expected, Arrays.copyOfRange(sent, 256, 352));
          f.erased();
        }
    }
  }

  @Test
  void user002FormDefaultsNormalizationAndImmutableInputs() {
    var empty = UserSearchForm.bind(Map.of());
    assertTrue(empty.isValid());
    assertEquals(1, empty.getPage());
    assertEquals(Optional.empty(), empty.toRequest().usernamePrefix());
    assertEquals(Optional.empty(), empty.toRequest().role());
    assertEquals(Optional.empty(), empty.toRequest().state());
    assertEquals(50, empty.toRequest().pageSize());
    for (String page : List.of("0", "-1", "-2147483648", "000001", "999999")) {
      var form =
          UserSearchForm.bind(
              params("username", " e\u0301 ", "role", " USER ", "state", " ACTIVE ", "page", page));
      assertTrue(form.isValid());
      assertEquals("é", form.getUsername());
      assertEquals("USER", form.getRole());
      assertEquals("ACTIVE", form.getState());
      assertEquals(page.equals("999999") ? 999999 : 1, form.getPage());
      assertEquals(Optional.of(UserRole.USER), form.toRequest().role());
      assertEquals(Optional.of(UserState.ACTIVE), form.toRequest().state());
    }
    var values = new ArrayList<>(List.of("first"));
    var input = new HashMap<String, List<String>>();
    input.put("username", values);
    var copy = UserSearchForm.bind(input);
    values.set(0, "changed");
    input.clear();
    assertEquals("first", copy.getUsername());
    assertEquals("UserSearchForm[REDACTED]", copy.toString());
    assertThrows(UnsupportedOperationException.class, () -> copy.getIssues().put("x", "y"));
    assertTrue(UserSearchForm.bind(params("username", "é".repeat(32))).isValid());
    assertTrue(UserSearchForm.bind(params("username", "\uD800\uDC00".repeat(16))).isValid());
  }

  @Test
  void user003InvalidBindingsNullAndWireNeverSent() throws Exception {
    try (var f = new Fixture()) {
      var bad = new ArrayList<LinkedMultiValueMap<String, String>>();
      bad.add(params("extra", "x"));
      bad.add(params("username", "one", "username", "two"));
      var noValue = params();
      noValue.put("state", List.of());
      bad.add(noValue);
      for (String value :
          List.of(
              "a\n",
              "\0",
              "\t",
              "\u007f",
              "\u0085",
              "\uD800",
              "\uDC00",
              "x".repeat(65),
              "é".repeat(33))) bad.add(params("username", value));
      for (String value : List.of("+1", "1.0", "١", "1000000", "2147483648", "-2147483649"))
        bad.add(params("page", value));
      for (String value : List.of("root", "admin")) bad.add(params("role", value));
      bad.add(params("state", "UNKNOWN"));
      for (var input : bad) {
        var form = UserSearchForm.bind(input);
        assertFalse(form.isValid());
        assertFalse(form.getIssues().isEmpty());
        assertThrows(IllegalArgumentException.class, form::toRequest);
        var r = new MockHttpServletResponse();
        var m = new ExtendedModelMap();
        assertEquals(
            "admin/user-list", f.controller.list(input, actor(UserRole.ADMIN), m, raw(), r));
        assertEquals(400, r.getStatus());
        var view = (UserListViewModel) m.get("page");
        assertTrue(view.getPage().isEmpty());
        assertTrue(view.getRows().isEmpty());
        assertTrue(view.getPreviousHref().isEmpty());
        assertTrue(view.getNextHref().isEmpty());
      }
      assertTrue(f.requests.isEmpty());
    }
    assertThrows(NullPointerException.class, () -> UserSearchForm.bind(null));
    var input = new HashMap<String, List<String>>();
    input.put(null, List.of("x"));
    assertThrows(NullPointerException.class, () -> UserSearchForm.bind(input));
    input.clear();
    input.put("username", null);
    assertThrows(NullPointerException.class, () -> UserSearchForm.bind(input));
    input.put("username", Arrays.asList((String) null));
    assertThrows(NullPointerException.class, () -> UserSearchForm.bind(input));
  }

  @Test
  void user004AdminOnlyAndExplicitBoundaryContracts() throws Exception {
    try (var f = new Fixture()) {
      var response = new MockHttpServletResponse();
      assertNull(
          f.controller.list(
              params(), actor(UserRole.USER), new ExtendedModelMap(), raw(), response));
      assertEquals(403, response.getStatus());
      assertTrue(f.requests.isEmpty());
      assertThrows(
          NullPointerException.class, () -> new UserAdminController(null, f.security.handler));
      assertThrows(NullPointerException.class, () -> new UserAdminController(f.client, null));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.list(
                  null, actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), response));
      assertThrows(
          NullPointerException.class,
          () -> f.controller.list(params(), null, new ExtendedModelMap(), raw(), response));
      assertThrows(
          NullPointerException.class,
          () -> f.controller.list(params(), actor(UserRole.ADMIN), null, raw(), response));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.list(
                  params(), actor(UserRole.ADMIN), new ExtendedModelMap(), null, response));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.list(
                  params(), actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), null));
      assertThrows(
          SessionStoreException.class,
          () ->
              f.controller.list(params(), () -> "other", new ExtendedModelMap(), raw(), response));
      assertTrue(f.requests.isEmpty());
    }
  }

  @Test
  void user005ResultAndTransportFailures() throws Exception {
    try (var f = new Fixture()) {
      Map<String, Integer> expected =
          Map.of(
              "0100", 400, "0101", 401, "0103", 403, "0104", 404, "0105", 409, "0106", 429, "0107",
              409, "9000", 503, "9001", 503);
      for (var item : expected.entrySet()) {
        f.code = item.getKey();
        var r = new MockHttpServletResponse();
        assertNull(
            f.controller.list(params(), actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), r));
        assertEquals(item.getValue(), r.getStatus());
      }
      f.code = "0000";
      f.responder =
          (id, bytes) -> {
            throw new JMSRuntimeException("synthetic secret diagnostics");
          };
      var r = new MockHttpServletResponse();
      assertNull(
          f.controller.list(params(), actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), r));
      assertEquals(503, r.getStatus());
      f.responder = (id, bytes) -> new byte[] {1};
      r = new MockHttpServletResponse();
      assertNull(
          f.controller.list(params(), actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), r));
      assertEquals(503, r.getStatus());
      for (int offset : new int[] {60, 113, 254, 303}) {
        f.responder =
            (id, bytes) -> {
              byte[] reply = f.standard(id, bytes);
              reply[offset] = (byte) 'x';
              return reply;
            };
        r = new MockHttpServletResponse();
        assertNull(
            f.controller.list(params(), actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), r));
        assertEquals(503, r.getStatus());
      }
      f.responder =
          (id, bytes) -> {
            throw new AssertionError("synthetic fatal");
          };
      assertThrows(
          AssertionError.class,
          () ->
              f.controller.list(
                  params(),
                  actor(UserRole.ADMIN),
                  new ExtendedModelMap(),
                  raw(),
                  new MockHttpServletResponse()));
      f.erased();
    }
    try (var f = new Fixture()) {
      var timeoutClient =
          new UserAdministrationWireClient(
              f.wire,
              (id, bytes) -> f.buffers.add(bytes),
              CLOCK,
              () -> new UUID(0, 999),
              Duration.ofMillis(10));
      var controller = new UserAdminController(timeoutClient, f.security.handler);
      var r = new MockHttpServletResponse();
      assertNull(
          controller.list(params(), actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), r));
      assertEquals(503, r.getStatus());
      f.erased();
    }
  }

  @Test
  void user006IndependentProjectionCountIdentityAndCOrder() throws Exception {
    var admin = actor(UserRole.ADMIN);
    var form = UserSearchForm.bind(Map.of());
    var bmp = row(1, "\uE000");
    var supplementary = row(2, "\uD800\uDC00");
    var page =
        UserListViewModel.success(
            admin, form, new PagedResponseData(1, 50, 2, 1, 1, 2), List.of(bmp, supplementary));
    assertEquals(
        List.of("\uE000", "\uD800\uDC00"),
        page.getRows().stream().map(UserListViewModel.Row::getUsername).toList());
    assertThrows(
        IllegalArgumentException.class,
        () ->
            UserListViewModel.success(
                admin,
                form,
                new PagedResponseData(1, 50, 2, 1, 1, 2),
                List.of(supplementary, bmp)));
    assertEquals(
        2,
        UserListViewModel.success(
                admin,
                form,
                new PagedResponseData(1, 50, 2, 1, 1, 2),
                List.of(row(1, "a"), row(2, "a")))
            .getRows()
            .size());
    // Same-name order is valid with ascending stable IDs, then independently reject reverse IDs.
    assertEquals(
        2,
        UserListViewModel.success(
                admin,
                form,
                new PagedResponseData(1, 50, 2, 1, 1, 2),
                List.of(row(1, "same"), row(2, "same")))
            .getRows()
            .size());
    assertThrows(
        IllegalArgumentException.class,
        () ->
            UserListViewModel.success(
                admin,
                form,
                new PagedResponseData(1, 50, 2, 1, 1, 2),
                List.of(row(2, "same"), row(1, "same"))));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            UserListViewModel.success(
                admin,
                form,
                new PagedResponseData(1, 50, 2, 1, 1, 2),
                List.of(row(1, "a"), row(1, "b"))));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            UserListViewModel.success(
                admin, form, new PagedResponseData(1, 50, 2, 1, 1, 2), List.of(bmp)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            UserListViewModel.success(
                admin, form, new PagedResponseData(1, 50, 51, 2, 1, 50), List.of(bmp)));
    try (var f = new Fixture()) {
      f.count = 2;
      f.total = 2;
      f.responder =
          (id, bytes) -> {
            byte[] reply = f.standard(id, bytes);
            number(reply, 304 + 168, 12, 1);
            return reply;
          };
      var r = new MockHttpServletResponse();
      assertNull(f.controller.list(params(), admin, new ExtendedModelMap(), raw(), r));
      assertEquals(503, r.getStatus());
      f.erased();
    }
  }

  @Test
  void user007MvcDomEscapingAndPagination() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      var result =
          mvc.perform(
                  get("/admin/users")
                      .principal(actor(UserRole.ADMIN))
                      .requestAttr(CsrfToken.class.getName(), csrf()))
              .andReturn();
      assertEquals(200, result.getResponse().getStatus());
      var dom = Jsoup.parse(result.getResponse().getContentAsString());
      assertEquals("Users", dom.title());
      assertEquals(1, dom.select(".user-row").size());
      assertEquals("user000", dom.select(".user-row .username").text());
      assertEquals("/admin/users/1", dom.select(".detail").attr("href"));
      assertEquals("2026-10-03 09:00:00.000", dom.select(".created-at").text());
      assertEquals(1, dom.select("input[name=_csrf]").size());
      assertEquals(1, dom.select("a[href='/admin/users/new']").size());
      assertEquals("/admin/users/new", dom.select("a[href='/admin/users/new']").attr("href"));
      assertEquals(
          List.of("/", "/notifications"), dom.select(".topbar .nav-links a").eachAttr("href"));
      assertEquals(
          List.of("", "USER", "ADMIN"), dom.select("select[name=role] option").eachAttr("value"));
      assertEquals(
          List.of("", "ACTIVE", "DISABLED", "LOCKED"),
          dom.select("select[name=state] option").eachAttr("value"));
      assertFalse(result.getResponse().getContentAsString().contains("a".repeat(64)));
      var head =
          mvc.perform(
                  head("/admin/users")
                      .principal(actor(UserRole.ADMIN))
                      .requestAttr(CsrfToken.class.getName(), csrf()))
              .andReturn();
      assertEquals(200, head.getResponse().getStatus());
      assertEquals(
          405,
          mvc.perform(post("/admin/users").principal(actor(UserRole.ADMIN)))
              .andReturn()
              .getResponse()
              .getStatus());
      f.total = 0;
      f.count = 0;
      dom =
          Jsoup.parse(
              mvc.perform(
                      get("/admin/users")
                          .principal(actor(UserRole.ADMIN))
                          .requestAttr(CsrfToken.class.getName(), csrf()))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals("該当するデータはありません", dom.select(".empty-results").text());
      assertTrue(dom.select(".user-row,.previous,.next").isEmpty());
      f.total = 51;
      f.count = 50;
      f.replyPage = 1;
      f.firstName = "<img src=x onerror=alert(1)>";
      var html =
          mvc.perform(
                  get("/admin/users")
                      .param("username", "a&b")
                      .param("role", "USER")
                      .param("state", "ACTIVE")
                      .principal(actor(UserRole.ADMIN))
                      .requestAttr(CsrfToken.class.getName(), csrf()))
              .andReturn()
              .getResponse()
              .getContentAsString();
      dom = Jsoup.parse(html);
      assertEquals(50, dom.select(".user-row").size());
      assertTrue(dom.select(".user-row img,.user-row script").isEmpty());
      assertEquals("<img src=x onerror=alert(1)>", dom.select(".username").first().text());
      assertEquals(
          "/admin/users?username=a%26b&role=USER&state=ACTIVE&page=2",
          dom.select(".next").attr("href"));
      f.replyPage = 2;
      f.count = 1;
      f.firstName = "user000";
      dom =
          Jsoup.parse(
              mvc.perform(
                      get("/admin/users")
                          .param("page", "999999")
                          .principal(actor(UserRole.ADMIN))
                          .requestAttr(CsrfToken.class.getName(), csrf()))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals("51 users / page 2 of 2", dom.select(".count").text());
      assertEquals(
          "/admin/users?username=&role=&state=&page=1", dom.select(".previous").attr("href"));
      assertTrue(dom.select(".next").isEmpty());
      dom =
          Jsoup.parse(
              mvc.perform(
                      get("/admin/users")
                          .param("extra", "x")
                          .principal(actor(UserRole.ADMIN))
                          .requestAttr(CsrfToken.class.getName(), csrf()))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals("入力項目を確認してください。", dom.select("#error-form").text());
      f.erased();
    }
  }

  @Test
  void user008RealSecurityAndApi0102Terminal() throws Exception {
    for (String role : List.of("USER", "ADMIN")) {
      reset();
      var api = new SessionFormLoginTest.Api("0000", role, "0000", 0);
      try (var f = new Fixture();
          var server =
              new EmbeddedWebSecurityTest.Server(
                  Files.createTempDirectory(root, "user-http-"),
                  false,
                  db,
                  Optional.of(api.provider),
                  true,
                  true,
                  (mvc, invalid) -> configure(mvc, f.client, invalid))) {
        var anonymous = server.send("GET", "/admin/users", null, null, true);
        assertEquals(302, anonymous.statusCode());
        assertTrue(f.requests.isEmpty());
        var first = server.send("GET", "/login", null, null, true);
        String initial = first.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
        var login =
            server.send(
                "POST",
                "/login",
                initial,
                "_csrf=" + first.body().substring(6) + "&username=reader&password=p",
                true);
        assertEquals(302, login.statusCode());
        String cookie = login.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
        var page = server.send("GET", "/admin/users", cookie, null, true);
        assertEquals(role.equals("ADMIN") ? 200 : 403, page.statusCode());
        if (role.equals("ADMIN")) {
          assertTrue(page.headers().firstValue("cache-control").orElseThrow().contains("no-store"));
          var head = server.send("HEAD", "/admin/users", cookie, null, true);
          assertEquals(200, head.statusCode());
          assertEquals("", head.body());
          int before = f.requests.size();
          assertEquals(
              400, server.send("GET", "/admin/users?page=bad", cookie, null, true).statusCode());
          assertEquals(before, f.requests.size());
          f.code = "0102";
          var expired = server.send("GET", "/admin/users", cookie, null, true);
          assertEquals(302, expired.statusCode());
          assertEquals(
              "/login?session-expired", expired.headers().firstValue("location").orElseThrow());
          assertTrue(
              expired.headers().firstValue("set-cookie").orElseThrow().contains("Max-Age=0"));
          assertEquals(302, server.send("GET", "/admin/users", cookie, null, true).statusCode());
          assertEquals(before + 1, f.requests.size());
        } else assertTrue(f.requests.isEmpty());
        f.erased();
        api.erased();
      }
    }
  }

  @Test
  void user009ConcurrentContextAndQueryIsolation() throws Exception {
    try (var f = new Fixture();
        var executor = Executors.newFixedThreadPool(8)) {
      var futures = new ArrayList<Future<?>>();
      for (int i = 0; i < 100; i++) {
        final int n = i;
        futures.add(
            executor.submit(
                () -> {
                  var principal =
                      new SessionPrincipal(
                          "reader" + n,
                          UserRole.ADMIN,
                          AuthenticationContext.of(String.format(Locale.ROOT, "%064x", n + 1)),
                          Instant.EPOCH);
                  var model = new ExtendedModelMap();
                  var r = new MockHttpServletResponse();
                  assertEquals(
                      "admin/user-list",
                      f.controller.list(
                          params("username", "query" + n), principal, model, raw(), r));
                  var page = (UserListViewModel) model.get("page");
                  assertEquals(200, r.getStatus());
                  assertEquals("query" + n, page.getFilters().getUsername());
                  assertEquals("reader" + n, page.getTopBar().getUsername());
                  return null;
                }));
      }
      for (var future : futures) future.get(15, TimeUnit.SECONDS);
      assertEquals(100, f.requests.size());
      assertEquals(100, f.requests.stream().map(bytes -> ascii(bytes, 24, 36)).distinct().count());
      for (int i = 0; i < 100; i++) {
        String context = String.format(Locale.ROOT, "%064x", i + 1);
        var sent =
            f.requests.stream().filter(bytes -> ascii(bytes, 113, 64).equals(context)).toList();
        assertEquals(1, sent.size());
        assertEquals("query" + i, ascii(sent.getFirst(), 256, 64).stripTrailing());
      }
      f.erased();
    }
  }

  @Test
  void user010ViewInvariantsAndAllSafeSnapshotValues() {
    var admin = actor(UserRole.ADMIN);
    var form = UserSearchForm.bind(Map.of());
    var bad = UserSearchForm.bind(params("extra", "x"));
    var data = new PagedResponseData(1, 50, 1, 1, 1, 1);
    var records = List.of(row(42, "reader"));
    assertThrows(
        NullPointerException.class, () -> UserListViewModel.success(null, form, data, records));
    assertThrows(
        NullPointerException.class, () -> UserListViewModel.success(admin, null, data, records));
    assertThrows(
        NullPointerException.class, () -> UserListViewModel.success(admin, form, null, records));
    assertThrows(
        NullPointerException.class, () -> UserListViewModel.success(admin, form, data, null));
    assertThrows(
        NullPointerException.class,
        () -> UserListViewModel.success(admin, form, data, Arrays.asList((UserRecord) null)));
    assertThrows(
        IllegalArgumentException.class,
        () -> UserListViewModel.success(actor(UserRole.USER), form, data, records));
    assertThrows(
        IllegalArgumentException.class, () -> UserListViewModel.success(admin, bad, data, records));
    assertThrows(IllegalArgumentException.class, () -> UserListViewModel.invalid(admin, form));
    assertThrows(NullPointerException.class, () -> UserListViewModel.invalid(admin, null));
    assertThrows(
        IllegalArgumentException.class, () -> UserListViewModel.invalid(actor(UserRole.USER), bad));
    var second = UserSearchForm.bind(params("page", "2"));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            UserListViewModel.success(
                admin, second, new PagedResponseData(1, 50, 51, 2, 1, 50), records));
    var page = UserListViewModel.success(admin, form, data, records);
    assertEquals("UserListViewModel[REDACTED]", page.toString());
    assertSame(form, page.getFilters());
    assertEquals(1, page.getPage().orElseThrow().getEffectivePage());
    assertTrue(page.getPreviousHref().isEmpty());
    assertTrue(page.getNextHref().isEmpty());
    var display = page.getRows().getFirst();
    assertEquals(42, display.getId());
    assertEquals("/admin/users/42", display.getDetailHref());
    assertEquals("reader", display.getUsername());
    assertEquals("ADMIN", display.getRole());
    assertEquals("LOCKED", display.getState());
    assertEquals("2026-10-03 09:00:00.000", display.getLockedUntil());
    assertEquals("2026-10-03 09:00:00.000", display.getLastLogin());
    assertEquals("2026-10-03 09:00:00.000", display.getCreatedAt());
    assertEquals("2026-10-03 09:00:00.000", display.getUpdatedAt());
    assertEquals("UserListRow[REDACTED]", display.toString());
    var empty =
        UserListViewModel.success(admin, form, new PagedResponseData(1, 50, 0, 1, 0, 0), List.of());
    assertTrue(empty.getRows().isEmpty());
    assertThrows(UnsupportedOperationException.class, () -> page.getRows().clear());
  }

  private static UserRecord row(long id, String username) {
    return new UserRecord(
        new UserId(id),
        username,
        UserRole.ADMIN,
        UserState.LOCKED,
        Optional.of(CLOCK.instant()),
        Optional.of(CLOCK.instant()),
        CLOCK.instant(),
        CLOCK.instant(),
        1);
  }

  @Test
  void detail001IndependentWireAndSafeDisplay() throws Exception {
    for (String code : List.of("0000", "0200"))
      try (var f = new Fixture()) {
        f.code = code;
        var model = new ExtendedModelMap();
        var response = new MockHttpServletResponse();
        assertEquals(
            "admin/user-detail",
            f.controller.detail(42, actor(UserRole.ADMIN), model, raw(), response));
        assertEquals(200, response.getStatus());
        var page = assertInstanceOf(UserDetailViewModel.class, model.get("page"));
        assertEquals("reader", page.getValues().get("username"));
        assertEquals("ログイン失敗によるロック", page.getValues().get("lockReason"));
        assertEquals("2026-10-03 09:00:00.000", page.getValues().get("passwordChangedAt"));
        assertEquals(2, page.getValues().get("activeSessionCount"));
        assertEquals(7L, page.getValues().get("version"));
        assertEquals("SYSTEM", page.getValues().get("createdBy"));
        assertEquals("admin", page.getValues().get("updatedBy"));
        var sent = f.requests.getFirst();
        assertEquals(268, sent.length);
        assertEquals("UDTREQ01", ascii(sent, 11, 8));
        assertArrayEquals(
            "000000000042".getBytes(StandardCharsets.US_ASCII), Arrays.copyOfRange(sent, 256, 268));
        assertEquals("a".repeat(64), ascii(sent, 113, 64));
        assertEquals(Boolean.TRUE, page.getValues().get("self"));
        f.erased();
      }
  }

  @Test
  void detail002MvcEscapingAndFixedRoutes() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      f.detailName = "<img src=x onerror=alert(1)>";
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      var result =
          mvc.perform(
                  get("/admin/users/42")
                      .principal(actor(UserRole.ADMIN))
                      .requestAttr(CsrfToken.class.getName(), csrf()))
              .andReturn();
      assertEquals(200, result.getResponse().getStatus());
      var dom = Jsoup.parse(result.getResponse().getContentAsString());
      assertEquals("User詳細", dom.title());
      assertEquals(f.detailName, dom.select(".user-detail > dl .username").text());
      assertTrue(dom.select("dl img,dl script").isEmpty());
      assertEquals("LOCKED", dom.select(".state").text());
      assertEquals("2", dom.select(".active-sessions").text());
      assertEquals("/admin/users", dom.select("a[href='/admin/users']").attr("href"));
      assertEquals(
          List.of("/", "/notifications"), dom.select(".topbar .nav-links a").eachAttr("href"));
      assertEquals(1, dom.select("input[name=_csrf]").size());
      assertTrue(dom.select("input[type=password],input[name=operation_token]").isEmpty());
      assertFalse(result.getResponse().getContentAsString().contains("a".repeat(64)));
      assertEquals(
          200,
          mvc.perform(
                  head("/admin/users/42")
                      .principal(actor(UserRole.ADMIN))
                      .requestAttr(CsrfToken.class.getName(), csrf()))
              .andReturn()
              .getResponse()
              .getStatus());
      int count = f.requests.size();
      for (String path : List.of("0", "1000000000000", "bad", "４２"))
        assertEquals(
            404,
            mvc.perform(get("/admin/users/" + path).principal(actor(UserRole.ADMIN)))
                .andReturn()
                .getResponse()
                .getStatus());
      assertEquals(
          503,
          mvc.perform(post("/admin/users/42").principal(actor(UserRole.ADMIN)))
              .andReturn()
              .getResponse()
              .getStatus());
      assertEquals(count, f.requests.size());
      f.erased();
    }
  }

  @Test
  void detail003RolesInvalidTargetsAndNullBoundaries() throws Exception {
    try (var f = new Fixture()) {
      var response = new MockHttpServletResponse();
      assertNull(
          f.controller.detail(42, actor(UserRole.USER), new ExtendedModelMap(), raw(), response));
      assertEquals(403, response.getStatus());
      for (long id : List.of(0L, -1L, 1_000_000_000_000L)) {
        response = new MockHttpServletResponse();
        assertNull(
            f.controller.detail(
                id, actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), response));
        assertEquals(404, response.getStatus());
      }
      assertThrows(
          SessionStoreException.class,
          () ->
              f.controller.detail(
                  42,
                  () -> "reader",
                  new ExtendedModelMap(),
                  raw(),
                  new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.detail(
                  42, null, new ExtendedModelMap(), raw(), new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.detail(
                  42, actor(UserRole.ADMIN), null, raw(), new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.detail(
                  42,
                  actor(UserRole.ADMIN),
                  new ExtendedModelMap(),
                  null,
                  new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.detail(42, actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), null));
      assertTrue(f.requests.isEmpty());
    }
  }

  @Test
  void detail004ErrorsAndMalformedWire() throws Exception {
    var codes = List.of("0100", "0101", "0103", "0104", "0105", "0106", "0107", "9000", "9001");
    var statuses = List.of(400, 401, 403, 404, 409, 429, 409, 503, 503);
    for (int i = 0; i < codes.size(); i++)
      try (var f = new Fixture()) {
        f.code = codes.get(i);
        var r = new MockHttpServletResponse();
        assertNull(
            f.controller.detail(42, actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), r));
        assertEquals(statuses.get(i), r.getStatus());
        f.erased();
      }
    for (int offset : List.of(60, 113, 212, 570))
      try (var f = new Fixture()) {
        f.responder =
            (id, bytes) -> {
              byte[] result = f.standard(id, bytes);
              result[offset] = (byte) 'x';
              return result;
            };
        var r = new MockHttpServletResponse();
        assertNull(
            f.controller.detail(42, actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), r));
        assertEquals(503, r.getStatus());
        f.erased();
      }
    try (var f = new Fixture()) {
      f.responder =
          (id, bytes) -> {
            throw new JMSRuntimeException("synthetic secret canary");
          };
      var r = new MockHttpServletResponse();
      assertNull(f.controller.detail(42, actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), r));
      assertEquals(503, r.getStatus());
      assertFalse(r.getContentAsString().contains("canary"));
      f.erased();
      f.responder =
          (id, bytes) -> {
            throw new AssertionError("explicit error propagation");
          };
      assertThrows(
          AssertionError.class,
          () ->
              f.controller.detail(
                  42,
                  actor(UserRole.ADMIN),
                  new ExtendedModelMap(),
                  raw(),
                  new MockHttpServletResponse()));
      f.erased();
    }
    try (var f = new Fixture()) {
      var client =
          new UserAdministrationWireClient(
              f.wire,
              (id, bytes) -> f.buffers.add(bytes),
              CLOCK,
              () -> new UUID(0, 999),
              Duration.ofMillis(10));
      var controller = new UserAdminController(client, f.security.handler);
      var r = new MockHttpServletResponse();
      assertNull(controller.detail(42, actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), r));
      assertEquals(503, r.getStatus());
      f.erased();
    }
  }

  @Test
  void detail009ZeroAndMaximumVersionAreValidIndependentWireValues() throws Exception {
    for (long version : List.of(0L, 999999999L))
      try (var f = new Fixture()) {
        f.detailVersion = version;
        var model = new ExtendedModelMap();
        var response = new MockHttpServletResponse();
        assertEquals(
            "admin/user-detail",
            f.controller.detail(42, actor(UserRole.ADMIN), model, raw(), response));
        assertEquals(200, response.getStatus());
        assertEquals(
            version,
            assertInstanceOf(UserDetailViewModel.class, model.get("page"))
                .getValues()
                .get("version"));
        f.erased();
      }
  }

  @Test
  void detail005ProjectionRejectionsDoNotRepairResponse() throws Exception {
    for (int kind = 0; kind < 3; kind++)
      try (var f = new Fixture()) {
        if (kind == 0) f.detailId = 43;
        if (kind == 1) f.detailSessions = 3;
        if (kind == 2)
          f.responder =
              (id, bytes) -> {
                var reply = f.standard(id, bytes);
                Arrays.fill(reply, 379, 396, (byte) ' ');
                return reply;
              };
        var r = new MockHttpServletResponse();
        assertNull(
            f.controller.detail(42, actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), r));
        assertEquals(503, r.getStatus());
        f.erased();
      }
  }

  @Test
  void detail006AllSafeValuesAndFactoryInvariants() throws Exception {
    for (String state : List.of("ACTIVE", "DISABLED", "LOCKED"))
      for (boolean optional : List.of(true, false))
        for (int count : List.of(0, 1, 2))
          try (var f = new Fixture()) {
            f.detailState = state;
            f.detailOptional = optional;
            f.detailSessions = count;
            f.detailName = "other";
            var model = new ExtendedModelMap();
            assertEquals(
                "admin/user-detail",
                f.controller.detail(
                    42, actor(UserRole.ADMIN), model, raw(), new MockHttpServletResponse()));
            var page = (UserDetailViewModel) model.get("page");
            assertEquals("reader", page.getTopBar().getUsername());
            assertEquals("ADMIN", page.getValues().get("role"));
            assertEquals(state, page.getValues().get("state"));
            assertEquals(
                state.equals("LOCKED") ? "ログイン失敗によるロック" : "", page.getValues().get("lockReason"));
            assertEquals(
                optional ? "2026-10-03 09:00:00.000" : "", page.getValues().get("lockedUntil"));
            assertEquals(
                optional ? "2026-10-03 09:00:00.000" : "", page.getValues().get("lastLogin"));
            assertEquals("2026-10-03 09:00:00.000", page.getValues().get("createdAt"));
            assertEquals("2026-10-03 09:00:00.000", page.getValues().get("updatedAt"));
            assertEquals(count, page.getValues().get("activeSessionCount"));
            assertEquals(42L, page.getValues().get("id"));
            assertEquals(Boolean.FALSE, page.getValues().get("self"));
            assertEquals("UserDetailViewModel[REDACTED]", page.toString());
            assertThrows(UnsupportedOperationException.class, () -> page.getValues().clear());
            assertFalse(page.getValues().toString().contains("a".repeat(64)));
            f.erased();
          }
    var detail =
        new UserDetailResponseData(
            new UserId(42),
            "reader",
            UserRole.ADMIN,
            UserState.ACTIVE,
            Optional.empty(),
            Optional.empty(),
            CLOCK.instant(),
            CLOCK.instant(),
            CLOCK.instant(),
            0,
            1,
            "SYSTEM",
            "admin");
    assertThrows(
        IllegalArgumentException.class,
        () -> UserDetailViewModel.from(actor(UserRole.USER), new UserId(42), detail));
    // Wire validation rejects count3 first; the public projection factory must also reject it.
    var tooManySessions =
        new UserDetailResponseData(
            new UserId(42),
            "reader",
            UserRole.ADMIN,
            UserState.ACTIVE,
            Optional.empty(),
            Optional.empty(),
            CLOCK.instant(),
            CLOCK.instant(),
            CLOCK.instant(),
            3,
            1,
            "SYSTEM",
            "admin");
    var failure =
        assertThrows(
            IllegalArgumentException.class,
            () -> UserDetailViewModel.from(actor(UserRole.ADMIN), new UserId(42), tooManySessions));
    assertEquals("invalid user detail projection", failure.getMessage());
    assertThrows(
        NullPointerException.class, () -> UserDetailViewModel.from(null, new UserId(42), detail));
    assertThrows(
        NullPointerException.class,
        () -> UserDetailViewModel.from(actor(UserRole.ADMIN), null, detail));
    assertThrows(
        NullPointerException.class,
        () -> UserDetailViewModel.from(actor(UserRole.ADMIN), new UserId(42), null));
  }

  @Test
  void detail007ConcurrentActorIsolation() throws Exception {
    try (var f = new Fixture();
        var executor = Executors.newFixedThreadPool(8)) {
      var futures = new ArrayList<Future<?>>();
      for (int i = 0; i < 100; i++) {
        int n = i;
        futures.add(
            executor.submit(
                () -> {
                  var actor =
                      new SessionPrincipal(
                          "reader" + n,
                          UserRole.ADMIN,
                          AuthenticationContext.of(String.format(Locale.ROOT, "%064x", n + 1)),
                          Instant.EPOCH);
                  var model = new ExtendedModelMap();
                  assertEquals(
                      "admin/user-detail",
                      f.controller.detail(42, actor, model, raw(), new MockHttpServletResponse()));
                  assertEquals(
                      "reader" + n,
                      ((UserDetailViewModel) model.get("page")).getTopBar().getUsername());
                  return null;
                }));
      }
      for (var future : futures) future.get(15, TimeUnit.SECONDS);
      assertEquals(100, f.requests.size());
      assertEquals(100, f.requests.stream().map(bytes -> ascii(bytes, 24, 36)).distinct().count());
      assertEquals(100, f.requests.stream().map(bytes -> ascii(bytes, 113, 64)).distinct().count());
      for (var bytes : f.requests) assertEquals("000000000042", ascii(bytes, 256, 12));
      f.erased();
    }
  }

  @Test
  void detail008RealSecurityAndApiInvalidTermination() throws Exception {
    for (String role : List.of("USER", "ADMIN")) {
      reset();
      var api = new SessionFormLoginTest.Api("0000", role, "0000", 0);
      try (var f = new Fixture();
          var server =
              new EmbeddedWebSecurityTest.Server(
                  Files.createTempDirectory(root, "user-detail-http-"),
                  false,
                  db,
                  Optional.of(api.provider),
                  true,
                  true,
                  (mvc, invalid) -> configure(mvc, f.client, invalid))) {
        assertEquals(302, server.send("GET", "/admin/users/42", null, null, true).statusCode());
        assertTrue(f.requests.isEmpty());
        var first = server.send("GET", "/login", null, null, true);
        String initial = first.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
        var login =
            server.send(
                "POST",
                "/login",
                initial,
                "_csrf=" + first.body().substring(6) + "&username=reader&password=p",
                true);
        assertEquals(302, login.statusCode());
        String cookie = login.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
        var response = server.send("GET", "/admin/users/42", cookie, null, true);
        assertEquals(role.equals("ADMIN") ? 200 : 403, response.statusCode());
        if (role.equals("ADMIN")) {
          assertTrue(
              response.headers().firstValue("cache-control").orElseThrow().contains("no-store"));
          var head = server.send("HEAD", "/admin/users/42", cookie, null, true);
          assertEquals(200, head.statusCode());
          assertEquals("", head.body());
          f.code = "0102";
          var expired = server.send("GET", "/admin/users/42", cookie, null, true);
          assertEquals(302, expired.statusCode());
          assertEquals(
              "/login?session-expired", expired.headers().firstValue("location").orElseThrow());
          assertTrue(
              expired.headers().firstValue("set-cookie").orElseThrow().contains("Max-Age=0"));
          int before = f.requests.size();
          assertEquals(302, server.send("GET", "/admin/users/42", cookie, null, true).statusCode());
          assertEquals(before, f.requests.size());
        } else assertTrue(f.requests.isEmpty());
        f.erased();
        api.erased();
      }
    }
  }

  private static final class Fixture implements AutoCloseable {
    final ApiSessionInvalidTest.Harness security = new ApiSessionInvalidTest.Harness(db);
    final AtomicLong ids = new AtomicLong();
    final List<byte[]> requests = new CopyOnWriteArrayList<>();
    final List<byte[]> buffers = new CopyOnWriteArrayList<>();
    final JmsRequestReplyClient wire =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    volatile String code = "0000";
    volatile String firstName = "user000";
    volatile int count = 1;
    volatile int total = 1;
    volatile int replyPage = 1;
    volatile long detailId = 42;
    volatile long detailVersion = 7;
    volatile int detailSessions = 2;
    volatile String detailName = "reader";
    volatile String detailState = "LOCKED";
    volatile boolean detailOptional = true;
    volatile BiFunction<UUID, byte[], byte[]> responder = this::standard;
    final UserAdministrationWireClient client =
        new UserAdministrationWireClient(
            wire,
            (id, bytes) -> {
              requests.add(bytes.clone());
              buffers.add(bytes);
              assertTrue(wire.onReply(id, responder.apply(id, bytes)));
            },
            CLOCK,
            () -> new UUID(0, ids.incrementAndGet()),
            Duration.ofSeconds(1));
    final UserAdminController controller = new UserAdminController(client, security.handler);

    byte[] standard(UUID id, byte[] request) {
      if (ascii(request, 11, 8).equals("UDTREQ01"))
        return detailResponse(
            id,
            ascii(request, 113, 64),
            code,
            detailId,
            detailName,
            detailState,
            detailSessions,
            detailVersion,
            detailOptional);
      return response(id, ascii(request, 113, 64), code, replyPage, count, total, firstName);
    }

    AnnotationConfigWebApplicationContext mvc() {
      var context = new AnnotationConfigWebApplicationContext();
      context.setServletContext(new MockServletContext());
      configure(context, client, security.handler);
      context.refresh();
      return context;
    }

    void erased() {
      assertEquals(0, wire.pendingCount());
      for (byte[] buffer : buffers) assertArrayEquals(new byte[buffer.length], buffer);
    }

    @Override
    public void close() {
      for (byte[] bytes : requests) Arrays.fill(bytes, (byte) 0);
      security.close();
    }
  }

  // Independent UI232/236 fixed positions, no production codec or method generates expected.
  private static byte[] detailResponse(
      UUID id,
      String context,
      String code,
      long target,
      String username,
      String state,
      int sessions,
      long version,
      boolean optional) {
    boolean success = code.equals("0000") || code.equals("0200");
    byte[] bytes = new byte[576];
    Arrays.fill(bytes, (byte) ' ');
    put(bytes, 0, 8, "SCHBNK01");
    put(bytes, 8, 3, "001");
    put(bytes, 11, 8, "UDTRSP01");
    put(bytes, 19, 3, "001");
    put(bytes, 22, 1, "S");
    put(bytes, 23, 1, "S");
    put(bytes, 24, 36, new UUID(1, id.getLeastSignificantBits()).toString());
    put(bytes, 60, 36, id.toString());
    put(bytes, 96, 17, "20261003090000000");
    put(bytes, 113, 64, context);
    number(bytes, 177, 4, 256);
    number(bytes, 181, 6, 320);
    number(bytes, 187, 6, 0);
    number(bytes, 193, 6, 0);
    number(bytes, 199, 9, 576);
    put(bytes, 208, 4, code);
    number(bytes, 256, 12, success ? target : 0);
    for (int offset : List.of(379, 396, 413))
      number(bytes, offset, 17, success ? 20261003090000000L : 0);
    number(bytes, 430, 3, success ? sessions : 0);
    number(bytes, 433, 9, success ? version : 0);
    if (success) {
      put(bytes, 268, 64, username);
      put(bytes, 332, 5, "ADMIN");
      put(bytes, 337, 8, state);
      if (optional) {
        put(bytes, 345, 17, "20261003090000000");
        put(bytes, 362, 17, "20261003090000000");
      }
      put(bytes, 442, 64, "SYSTEM");
      put(bytes, 506, 64, "admin");
    }
    return bytes;
  }

  private static byte[] response(
      UUID id, String context, String code, int page, int rows, int total, String firstName) {
    boolean success = code.equals("0000") || code.equals("0200");
    int count = success ? rows : 0;
    byte[] bytes = new byte[304 + 168 * count];
    Arrays.fill(bytes, (byte) ' ');
    put(bytes, 0, 8, "SCHBNK01");
    put(bytes, 8, 3, "001");
    put(bytes, 11, 8, "USRRSP01");
    put(bytes, 19, 3, "001");
    put(bytes, 22, 1, "S");
    put(bytes, 23, 1, "S");
    put(bytes, 24, 36, new UUID(1, id.getLeastSignificantBits()).toString());
    put(bytes, 60, 36, id.toString());
    put(bytes, 96, 17, "20261003090000000");
    put(bytes, 113, 64, context);
    number(bytes, 177, 4, 256);
    number(bytes, 181, 6, 48);
    number(bytes, 187, 6, 168);
    number(bytes, 193, 6, count);
    number(bytes, 199, 9, bytes.length);
    put(bytes, 208, 4, code);
    number(bytes, 256, 6, success ? page : 0);
    number(bytes, 262, 3, success ? 50 : 0);
    number(bytes, 265, 9, success ? total : 0);
    number(bytes, 274, 6, success ? Math.max(1, (total + 49) / 50) : 0);
    number(bytes, 280, 9, count == 0 ? 0 : (page - 1L) * 50 + 1);
    number(bytes, 289, 9, count == 0 ? 0 : (page - 1L) * 50 + count);
    for (int i = 0; i < count; i++) {
      int at = 304 + i * 168;
      number(bytes, at, 12, i + 1);
      put(bytes, at + 12, 64, i == 0 ? firstName : String.format(Locale.ROOT, "user%03d", i));
      put(bytes, at + 76, 5, "ADMIN");
      put(bytes, at + 81, 8, "ACTIVE");
      put(bytes, at + 123, 17, "20261003090000000");
      put(bytes, at + 140, 17, "20261003090000000");
      number(bytes, at + 157, 9, 1);
    }
    return bytes;
  }

  private static void put(byte[] bytes, int offset, int length, String value) {
    byte[] text = value.getBytes(StandardCharsets.UTF_8);
    assertTrue(text.length <= length);
    Arrays.fill(bytes, offset, offset + length, (byte) ' ');
    System.arraycopy(text, 0, bytes, offset, text.length);
  }

  private static void number(byte[] bytes, int offset, int length, long value) {
    put(bytes, offset, length, String.format(Locale.ROOT, "%0" + length + "d", value));
  }

  private static String ascii(byte[] bytes, int offset, int length) {
    return new String(bytes, offset, length, StandardCharsets.US_ASCII);
  }
}
