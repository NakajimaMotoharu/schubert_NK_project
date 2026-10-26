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
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.config.AnimationMvcConfiguration;
import dev.codex.schubert.nk.web.controller.AnimationController;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.messaging.AnimationWireClient;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.view.AnimationListViewModel;
import dev.codex.schubert.nk.web.view.AnimationMenuViewModel;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.Principal;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
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
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.ui.Model;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;

/** NK-WEB002/FUN006/AUT/TST/UI223,235/SS313,314,323/PG207/PT-SCR054..065. */
class AnimationControllerTest {
  private static final String FIXTURE_MENU_PATH = "/animation";
  private static final String FIXTURE_MAIN_PATH = "/animation/main";
  private static final String FIXTURE_OVA_PATH = "/animation/ova";
  private static final String FIXTURE_SUCCESS_CODE = "0000";
  private static final String EXPECTED_MENU_VIEW = "animation";
  private static final String EXPECTED_LIST_VIEW = "animation-list";
  private static final String EXPECTED_PAGE_ATTRIBUTE = "page";
  private static final String FIXTURE_MAIN_SECTION = "main";
  private static final String FIXTURE_HTTP_GET = "GET";
  private static final String FIXTURE_FAILURE_MESSAGE = "synthetic";
  private static final String EXPECTED_HREF_ATTRIBUTE = "href";
  private static final String FIXTURE_MENU_TYPE_CODE = "ANM";
  private static final int FIXTURE_THROW_MODE = 3;
  private static final int FIXTURE_CORRELATION_MISMATCH_MODE = 1;

  private static WebLogDatabaseFixture db;
  @TempDir Path root;
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-20T00:00:00Z"), ZoneOffset.UTC);
  private static final List<String> PATHS =
      List.of(FIXTURE_MENU_PATH, FIXTURE_MAIN_PATH, FIXTURE_OVA_PATH);

  @BeforeAll
  static void start(@TempDir Path p) throws Exception {
    db = new WebLogDatabaseFixture(p);
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
        "reader",
        role,
        AuthenticationContext.of("a".repeat(64)),
        Instant.parse("2026-09-19T00:00:00Z"));
  }

  private static String call(
      AnimationController c,
      String path,
      Principal p,
      Model m,
      HttpServletRequest r,
      HttpServletResponse s)
      throws IOException {
    return switch (path) {
      case FIXTURE_MENU_PATH -> c.menu(p, m, r, s);
      case FIXTURE_MAIN_PATH -> c.main(p, m, r, s);
      case FIXTURE_OVA_PATH -> c.ova(p, m, r, s);
      default -> throw new AssertionError();
    };
  }

  @Test
  void animation054SuccessAndWire() throws Exception {
    try (var f = new Fixture()) {
      for (var role : UserRole.values())
        for (var code : List.of(FIXTURE_SUCCESS_CODE, "0200"))
          for (int count : new int[] {0, 1, 50})
            for (var path : PATHS) {
              f.code = code;
              f.count = count;
              int before = f.requests.size();
              var model = new ExtendedModelMap();
              var s = new MockHttpServletResponse();
              assertEquals(
                  path.equals(FIXTURE_MENU_PATH) ? EXPECTED_MENU_VIEW : EXPECTED_LIST_VIEW,
                  call(f.controller, path, actor(role), model, raw(path), s));
              assertEquals(200, s.getStatus());
              assertEquals(Set.of(EXPECTED_PAGE_ATTRIBUTE), model.keySet());
              if (path.equals(FIXTURE_MENU_PATH)) {
                var page =
                    assertInstanceOf(
                        AnimationMenuViewModel.class, model.get(EXPECTED_PAGE_ATTRIBUTE));
                assertEquals(15, page.getMainCount());
                assertEquals(4, page.getOvaCount());
                assertTrue(page.isOpeningPresent());
                assertEquals(20, page.getTotalCount());
                assertEquals(
                    switch (role) {
                      case USER -> "USER";
                      case ADMIN -> "ADMIN";
                    },
                    page.getTopBar().getRole());
              } else {
                var page =
                    assertInstanceOf(
                        AnimationListViewModel.class, model.get(EXPECTED_PAGE_ATTRIBUTE));
                assertEquals(count, page.getTotalCount());
                assertEquals(
                    switch (role) {
                      case USER -> "USER";
                      case ADMIN -> "ADMIN";
                    },
                    page.getTopBar().getRole());
                assertEquals(
                    path.endsWith(FIXTURE_MAIN_SECTION) ? FIXTURE_MAIN_SECTION : "ova",
                    page.getSection());
              }
              assertEquals(before + 1, f.requests.size());
              var sent = f.requests.getLast();
              assertEquals(path.equals(FIXTURE_MENU_PATH) ? 256 : 272, sent.length);
              if (!path.equals(FIXTURE_MENU_PATH))
                assertEquals(
                    path.endsWith(FIXTURE_MAIN_SECTION) ? "MAIN            " : "OVA             ",
                    ascii(sent, 256, 16));
              f.erased();
            }
    }
  }

  @Test
  void animation055ErrorMapping() throws Exception {
    String[] codes = {"0100", "0101", "0103", "0104", "0105", "0106", "0107", "9000", "9001"};
    int[] statuses = {400, 401, 403, 404, 409, 429, 409, 503, 503};
    try (var f = new Fixture()) {
      for (var path : PATHS)
        for (int i = 0; i < codes.length; i++) {
          f.code = codes[i];
          var model = new ExtendedModelMap();
          var s = new MockHttpServletResponse();
          int before = f.requests.size();
          assertNull(call(f.controller, path, actor(UserRole.USER), model, raw(path), s));
          assertEquals(statuses[i], s.getStatus());
          assertTrue(model.isEmpty());
          assertEquals(before + 1, f.requests.size());
          f.erased();
        }
    }
  }

  @Test
  void animation056SessionInvalid() throws Exception {
    try (var f = new Fixture()) {
      f.code = "0102";
      for (var path : PATHS) {
        var r = f.security.mock(FIXTURE_HTTP_GET, path);
        var s = new MockHttpServletResponse();
        var model = new ExtendedModelMap();
        SecurityContextHolder.getContext()
            .setAuthentication(
                UsernamePasswordAuthenticationToken.authenticated(
                    actor(UserRole.USER), null, List.of(new SimpleGrantedAuthority("ROLE_USER"))));
        assertNull(call(f.controller, path, actor(UserRole.USER), model, r, s));
        assertEquals(302, s.getStatus());
        assertEquals("/login?session-expired", s.getRedirectedUrl());
        assertNull(SecurityContextHolder.getContext().getAuthentication());
        assertNull(r.getSession(false));
        assertTrue(model.isEmpty());
        f.erased();
      }
    }
  }

  @Test
  void animation057MalformedAndTransport() throws Exception {
    try (var f = new Fixture()) {
      for (var path : PATHS)
        for (int mode = 0; mode < 4; mode++) {
          final int kind = mode;
          f.responder =
              (id, b) -> {
                if (kind == 0) return new byte[4];
                if (kind == FIXTURE_THROW_MODE)
                  throw new IllegalStateException(FIXTURE_FAILURE_MESSAGE);
                var reply = f.standard(id, b);
                if (kind == FIXTURE_CORRELATION_MISMATCH_MODE)
                  put(reply, 60, 36, new UUID(0, 999).toString());
                else put(reply, 113, 64, "b".repeat(64));
                return reply;
              };
          var m = new ExtendedModelMap();
          var s = new MockHttpServletResponse();
          assertNull(call(f.controller, path, actor(UserRole.USER), m, raw(path), s));
          assertEquals(503, s.getStatus());
          assertTrue(m.isEmpty());
          f.erased();
        }
    }
  }

  @Test
  void animation058ResponseBinding() throws Exception {
    try (var f = new Fixture()) {
      for (var path : PATHS)
        for (int mode = 0; mode < (path.equals(FIXTURE_MENU_PATH) ? 1 : 5); mode++) {
          final int kind = mode;
          f.responder =
              (id, b) -> {
                var reply = f.standard(id, b);
                if (path.equals(FIXTURE_MENU_PATH)) put(reply, 263, 3, "021");
                else
                  switch (kind) {
                    case 0 -> put(reply, 256, 6, "000003");
                    case 1 ->
                        put(reply, 584, 16, path.endsWith(FIXTURE_MAIN_SECTION) ? "OVA" : "MAIN");
                    case 2 -> put(reply, 1124, 64, "missing");
                    case 3 -> put(reply, 1192, 64, "video0");
                    case 4 -> put(reply, 1112, 12, "000000000000");
                    default -> throw new AssertionError();
                  }
                return reply;
              };
          var m = new ExtendedModelMap();
          var s = new MockHttpServletResponse();
          assertNull(call(f.controller, path, actor(UserRole.USER), m, raw(path), s));
          assertEquals(503, s.getStatus());
          assertTrue(m.isEmpty());
          f.erased();
        }
    }
  }

  @Test
  void animation059NullAndUnknown() throws Exception {
    try (var f = new Fixture()) {
      assertThrows(
          NullPointerException.class, () -> new AnimationController(null, f.security.handler));
      assertThrows(NullPointerException.class, () -> new AnimationController(f.client, null));
      for (var path : PATHS) {
        var p = actor(UserRole.USER);
        var m = new ExtendedModelMap();
        var r = raw(path);
        var s = new MockHttpServletResponse();
        int before = f.requests.size();
        assertThrows(NullPointerException.class, () -> call(f.controller, path, null, m, r, s));
        assertThrows(NullPointerException.class, () -> call(f.controller, path, p, null, r, s));
        assertThrows(NullPointerException.class, () -> call(f.controller, path, p, m, null, s));
        assertThrows(NullPointerException.class, () -> call(f.controller, path, p, m, r, null));
        assertThrows(
            SessionStoreException.class, () -> call(f.controller, path, () -> "foreign", m, r, s));
        assertEquals(before, f.requests.size());
        var failure = new IllegalArgumentException(FIXTURE_FAILURE_MESSAGE);
        var broken =
            new ExtendedModelMap() {
              @Override
              public ExtendedModelMap addAttribute(String n, Object v) {
                throw failure;
              }
            };
        assertSame(
            failure,
            assertThrows(
                IllegalArgumentException.class, () -> call(f.controller, path, p, broken, r, s)));
        var unknown = new AssertionError(FIXTURE_FAILURE_MESSAGE);
        f.responder =
            (id, b) -> {
              throw unknown;
            };
        assertSame(
            unknown,
            assertThrows(AssertionError.class, () -> call(f.controller, path, p, m, r, s)));
        f.responder = f::standard;
        f.code = "9000";
        var io = new IOException(FIXTURE_FAILURE_MESSAGE);
        var brokenResponse =
            new MockHttpServletResponse() {
              @Override
              public void sendError(int status) throws IOException {
                throw io;
              }
            };
        assertSame(
            io,
            assertThrows(
                IOException.class, () -> call(f.controller, path, p, m, r, brokenResponse)));
        f.code = FIXTURE_SUCCESS_CODE;
        f.erased();
      }
    }
  }

  @Test
  void animation060MvcRoutes() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      for (var path : PATHS) {
        var result = mvc.perform(pageRequest(path, actor(UserRole.USER))).andReturn();
        assertEquals(200, result.getResponse().getStatus());
        assertEquals(
            path.equals(FIXTURE_MENU_PATH) ? EXPECTED_MENU_VIEW : EXPECTED_LIST_VIEW,
            Objects.requireNonNull(result.getModelAndView()).getViewName());
        var h =
            mvc.perform(
                    head(path)
                        .principal(actor(UserRole.ADMIN))
                        .requestAttr(CsrfToken.class.getName(), csrf()))
                .andReturn();
        assertEquals(200, h.getResponse().getStatus());
        assertEquals(
            path.equals(FIXTURE_MENU_PATH) ? EXPECTED_MENU_VIEW : EXPECTED_LIST_VIEW,
            Objects.requireNonNull(h.getModelAndView()).getViewName());
        int before = f.requests.size();
        assertEquals(
            405,
            mvc.perform(post(path).principal(actor(UserRole.USER)))
                .andReturn()
                .getResponse()
                .getStatus());
        assertEquals(before, f.requests.size());
      }
      int before = f.requests.size();
      for (var path : List.of("/animation/unknown", "/animation/MAIN", "/animation/main/extra"))
        assertEquals(
            404,
            mvc.perform(pageRequest(path, actor(UserRole.USER)))
                .andReturn()
                .getResponse()
                .getStatus());
      assertEquals(before, f.requests.size());
      f.erased();
    }
  }

  @Test
  void animation061RealHttpSecurity() throws Exception {
    for (String role : List.of("USER", "ADMIN")) {
      reset();
      var api = new SessionFormLoginTest.Api(FIXTURE_SUCCESS_CODE, role, FIXTURE_SUCCESS_CODE, 0);
      try (var f = new Fixture();
          var server =
              new EmbeddedWebSecurityTest.Server(
                  Files.createTempDirectory(root, "animation-"),
                  false,
                  db,
                  Optional.of(api.provider),
                  true,
                  true,
                  (mvc, invalid) -> configure(mvc, f.client, invalid))) {
        for (var path : PATHS)
          assertEquals(302, server.send(FIXTURE_HTTP_GET, path, null, null, true).statusCode());
        assertTrue(f.requests.isEmpty());
        var first = server.send(FIXTURE_HTTP_GET, "/login", null, null, true);
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
        for (var path : PATHS) {
          int before = f.requests.size();
          var result = server.send(FIXTURE_HTTP_GET, path, cookie, null, true);
          assertEquals(200, result.statusCode());
          var dom = Jsoup.parse(result.body());
          assertEquals(role, dom.select(".login-role").text());
          assertEquals(1, dom.select("form[action='/logout'] input[name=_csrf]").size());
          assertTrue(
              result.headers().firstValue("cache-control").orElseThrow().contains("no-store"));
          assertEquals(
              "nosniff", result.headers().firstValue("x-content-type-options").orElseThrow());
          assertTrue(
              result
                  .headers()
                  .firstValue("content-security-policy")
                  .orElseThrow()
                  .contains("default-src 'self'"));
          var h = server.send("HEAD", path, cookie, null, true);
          assertEquals(200, h.statusCode());
          assertEquals("", h.body());
          assertEquals(before + 2, f.requests.size());
        }
        f.code = "0102";
        int before = f.requests.size();
        var expired = server.send(FIXTURE_HTTP_GET, FIXTURE_MAIN_PATH, cookie, null, true);
        assertEquals(302, expired.statusCode());
        assertEquals(
            "/login?session-expired", expired.headers().firstValue("location").orElseThrow());
        assertTrue(expired.headers().firstValue("set-cookie").orElseThrow().contains("Max-Age=0"));
        assertEquals(before + 1, f.requests.size());
        assertEquals(
            302, server.send(FIXTURE_HTTP_GET, FIXTURE_OVA_PATH, cookie, null, true).statusCode());
        assertEquals(before + 1, f.requests.size());
        assertEquals(0, server.context.getManager().getActiveSessions());
        f.erased();
        api.erased();
      }
    }
  }

  @Test
  void animation062EscapingAndIsolation() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var canary = "<img src=x onerror=alert(1)>";
      f.responder =
          (id, b) -> {
            var reply = f.standard(id, b);
            put(reply, 264, 64, "video ?#日本");
            put(reply, 328, 256, canary);
            put(reply, 600, 512, "videos/" + canary + ".mp4");
            return reply;
          };
      var p =
          new SessionPrincipal(
              canary,
              UserRole.ADMIN,
              actor(UserRole.USER).authenticationContext(),
              actor(UserRole.USER).loginAt());
      var result =
          MockMvcBuilders.webAppContextSetup(context)
              .build()
              .perform(pageRequest(FIXTURE_OVA_PATH, p))
              .andReturn();
      assertEquals(200, result.getResponse().getStatus());
      var dom = Jsoup.parse(result.getResponse().getContentAsString());
      assertEquals(canary, dom.select(".login-user").text());
      assertEquals(canary, dom.select(".scenario-title").first().text());
      assertEquals(
          "/animation/videos/video%20%3F%23%E6%97%A5%E6%9C%AC",
          dom.select(".scenario-link").first().attr(EXPECTED_HREF_ATTRIBUTE));
      assertTrue(dom.select("img,[onerror],script:not([src])").isEmpty());
      assertFalse(result.getResponse().getContentAsString().contains("a".repeat(64)));
      f.erased();
    }
  }

  @Test
  void animation063EmptyAndGrouping() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      f.count = 0;
      for (var path : PATHS.subList(1, 3)) {
        var result = mvc.perform(pageRequest(path, actor(UserRole.USER))).andReturn();
        assertEquals(200, result.getResponse().getStatus());
        var dom = Jsoup.parse(result.getResponse().getContentAsString());
        assertEquals("0本", dom.select(".subtitle").text());
        assertTrue(dom.select(".animation-list").text().isEmpty());
        assertTrue(dom.select(".scenario-link,.empty-results").isEmpty());
      }
      f.count = 3;
      f.responder =
          (id, b) -> {
            var reply = f.standard(id, b);
            put(reply, 584, 16, "SUBTRACK");
            put(reply, 1124, 64, "video1");
            return reply;
          };
      var dom =
          Jsoup.parse(
              mvc.perform(pageRequest(FIXTURE_MAIN_PATH, actor(UserRole.USER)))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals("3本", dom.select(".subtitle").text());
      assertEquals(
          List.of("Title1", "Title2"),
          dom.select(".animation-main-link .scenario-title").eachText());
      assertEquals(
          "/animation/videos/video0", dom.select(".subtrack-link").attr(EXPECTED_HREF_ATTRIBUTE));
      assertEquals(1, dom.select(".subtrack-placeholder").size());
      f.responder = f::standard;
      f.count = 2;
      dom =
          Jsoup.parse(
              mvc.perform(pageRequest(FIXTURE_OVA_PATH, actor(UserRole.USER)))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals(List.of("Title0", "Title1"), dom.select(".scenario-title").eachText());
      assertTrue(dom.select(".scenario-meta").first().text().contains("1.0 MB"));
      f.erased();
    }
  }

  @Test
  void animation064ConcurrentRequests() throws Exception {
    try (var f = new Fixture();
        var pool = Executors.newFixedThreadPool(8)) {
      var futures = new ArrayList<Future<?>>();
      for (int i = 0; i < 64; i++) {
        final int n = i;
        futures.add(
            pool.submit(
                () -> {
                  var p =
                      new SessionPrincipal(
                          "reader" + n,
                          UserRole.USER,
                          AuthenticationContext.of(String.format(Locale.ROOT, "%064x", n + 1)),
                          actor(UserRole.USER).loginAt());
                  var path = PATHS.get(n % 3);
                  var m = new ExtendedModelMap();
                  var s = new MockHttpServletResponse();
                  assertEquals(
                      n % 3 == 0 ? EXPECTED_MENU_VIEW : EXPECTED_LIST_VIEW,
                      call(f.controller, path, p, m, raw(path), s));
                  var page = m.get(EXPECTED_PAGE_ATTRIBUTE);
                  var bar =
                      page instanceof AnimationMenuViewModel menu
                          ? menu.getTopBar()
                          : ((AnimationListViewModel) page).getTopBar();
                  assertEquals("reader" + n, bar.getUsername());
                  assertEquals(200, s.getStatus());
                  return null;
                }));
      }
      for (var future : futures) future.get(10, TimeUnit.SECONDS);
      assertEquals(64, f.requests.size());
      assertEquals(64, f.correlations.size());
      for (int i = 0; i < 64; i++) {
        String context = String.format(Locale.ROOT, "%064x", i + 1);
        var requests = f.requests.stream().filter(b -> ascii(b, 113, 64).equals(context)).toList();
        assertEquals(1, requests.size());
        assertEquals(i % 3 == 0 ? "ANMREQ01" : "ANLREQ01", ascii(requests.getFirst(), 11, 8));
      }
      f.erased();
    }
  }

  @Test
  void animation065CompatibilityTrace() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      var dom =
          Jsoup.parse(
              mvc.perform(pageRequest(FIXTURE_MENU_PATH, actor(UserRole.USER)))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals(
          List.of("メインパート一覧", "OVA一覧", "オープニング映像"), dom.select(".menu-item strong").eachText());
      assertEquals(
          List.of("15本の映像", "4本の映像", "OP映像を再生する"), dom.select(".menu-item span").eachText());
      assertEquals(
          List.of(FIXTURE_MAIN_PATH, FIXTURE_OVA_PATH, "/animation/opening"),
          dom.select(".menu-item").eachAttr(EXPECTED_HREF_ATTRIBUTE));
      for (var path : PATHS.subList(1, 3)) {
        dom =
            Jsoup.parse(
                mvc.perform(pageRequest(path, actor(UserRole.USER)))
                    .andReturn()
                    .getResponse()
                    .getContentAsString());
        assertEquals(List.of("Title0", "Title1"), dom.select(".scenario-title").eachText());
        assertEquals("2本", dom.select(".subtitle").text());
        assertEquals(
            List.of(FIXTURE_MENU_PATH, "/search"),
            dom.select("nav[aria-label=Animationナビゲーション] a").eachAttr(EXPECTED_HREF_ATTRIBUTE));
      }
      Path directory = Path.of("target/scenario-screen-traces");
      Files.createDirectories(directory);
      Files.writeString(
          directory.resolve("PT-SCR-065.txt"),
          "screens=SCR008|SCR009\n"
              + "fixture=public-synthetic\n"
              + "routes=3\n"
              + "menuCards=3\n"
              + "listRecords=2\n"
              + "actualNkGate=false\n",
          StandardCharsets.US_ASCII);
      f.erased();
    }
  }

  private static MockHttpServletRequest raw(String path) {
    var r = new MockHttpServletRequest(FIXTURE_HTTP_GET, path);
    r.setRemoteAddr("127.0.0.1");
    return r;
  }

  private static CsrfToken csrf() {
    return new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", "b".repeat(64));
  }

  private static org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder
      pageRequest(String path, SessionPrincipal p) {
    return get(path)
        .principal(p)
        .requestAttr(CsrfToken.class.getName(), csrf())
        .locale(Locale.JAPAN);
  }

  private static void configure(
      AnnotationConfigWebApplicationContext context,
      AnimationWireClient client,
      ApiSessionInvalidHandler invalid) {
    context.register(AnimationMvcConfiguration.class);
    context.addBeanFactoryPostProcessor(
        factory -> {
          factory.registerSingleton("animationWireClient", client);
          factory.registerSingleton("apiSessionInvalidHandler", invalid);
        });
  }

  private static final class Fixture implements AutoCloseable {
    final ApiSessionInvalidTest.Harness security = new ApiSessionInvalidTest.Harness(db);
    final AtomicInteger ids = new AtomicInteger();
    final List<byte[]> requests = new CopyOnWriteArrayList<>();
    final List<byte[]> buffers = new CopyOnWriteArrayList<>();
    final Set<UUID> correlations = ConcurrentHashMap.newKeySet();
    volatile int count = 2;
    volatile String code = FIXTURE_SUCCESS_CODE;
    volatile BiFunction<UUID, byte[], byte[]> responder = this::standard;
    final JmsRequestReplyClient wire =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    final AnimationWireClient client =
        new AnimationWireClient(
            wire,
            (id, b) -> {
              assertTrue(correlations.add(id));
              buffers.add(b);
              requests.add(b.clone());
              String type = ascii(b, 11, 3);
              assertTrue(type.equals(FIXTURE_MENU_TYPE_CODE) || type.equals("ANL"));
              assertEquals(type.equals(FIXTURE_MENU_TYPE_CODE) ? 256 : 272, b.length);
              assertEquals("Q", ascii(b, 22, 1));
              assertEquals("S", ascii(b, 23, 1));
              assertEquals(id.toString(), ascii(b, 24, 36));
              assertEquals(id.toString(), ascii(b, 60, 36));
              assertEquals("20260920090000000", ascii(b, 96, 17));
              assertTrue(wire.onReply(id, responder.apply(id, b)));
            },
            CLOCK,
            () -> new UUID(0, ids.incrementAndGet()),
            Duration.ofSeconds(1));
    final AnimationController controller = new AnimationController(client, security.handler);

    AnnotationConfigWebApplicationContext mvc() {
      var context = new AnnotationConfigWebApplicationContext();
      context.setServletContext(new MockServletContext());
      configure(context, client, security.handler);
      context.refresh();
      return context;
    }

    byte[] standard(UUID id, byte[] b) {
      return response(
          ascii(b, 11, 3).equals(FIXTURE_MENU_TYPE_CODE)
              ? FIXTURE_MENU_TYPE_CODE
              : ascii(b, 256, 16).strip(),
          count,
          code,
          id,
          ascii(b, 113, 64));
    }

    void erased() {
      assertEquals(0, wire.pendingCount());
      for (var b : buffers) assertArrayEquals(new byte[b.length], b);
    }

    @Override
    public void close() {
      for (var b : requests) Arrays.fill(b, (byte) 0);
      security.close();
    }
  }

  // UI232/235 independent byte offsets; no production codec/mapper for fixtures.
  private static byte[] response(String type, int n, String code, UUID id, String context) {
    boolean menu = type.equals(FIXTURE_MENU_TYPE_CODE);
    boolean success = code.equals(FIXTURE_SUCCESS_CODE) || code.equals("0200");
    int count = menu || !success ? 0 : n;
    var b =
        header(
            menu ? "ANMRSP01" : "ANLRSP01",
            menu ? 16 : 8,
            menu ? 0 : 928,
            count,
            code,
            id,
            context);
    if (menu) {
      number(b, 256, 3, success ? 15 : 0);
      number(b, 259, 3, success ? 4 : 0);
      put(b, 262, 1, success ? "1" : "");
      number(b, 263, 3, success ? 20 : 0);
    } else {
      number(b, 256, 6, count);
      for (int i = 0; i < count; i++) {
        int start = 264 + i * 928;
        put(b, start, 64, "video" + i);
        put(b, start + 64, 256, "Title" + i);
        put(b, start + 320, 16, type);
        put(b, start + 336, 512, "videos/" + i + ".mp4");
        number(b, start + 848, 12, 1048576 + i);
        number(b, start + 924, 4, i + 1);
      }
    }
    return b;
  }

  private static byte[] header(
      String layout, int data, int record, int count, String code, UUID id, String context) {
    var b = new byte[256 + data + record * count];
    Arrays.fill(b, (byte) ' ');
    put(b, 0, 8, "SCHBNK01");
    put(b, 8, 3, "001");
    put(b, 11, 8, layout);
    put(b, 19, 3, "001");
    put(b, 22, 1, "S");
    put(b, 23, 1, "S");
    put(b, 24, 36, new UUID(1, id.getLeastSignificantBits()).toString());
    put(b, 60, 36, id.toString());
    put(b, 96, 17, "20260920090000000");
    put(b, 113, 64, context);
    number(b, 177, 4, 256);
    number(b, 181, 6, data);
    number(b, 187, 6, record);
    number(b, 193, 6, count);
    number(b, 199, 9, b.length);
    put(b, 208, 4, code);
    return b;
  }

  private static void put(byte[] b, int offset, int length, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    assertTrue(bytes.length <= length);
    Arrays.fill(b, offset, offset + length, (byte) ' ');
    System.arraycopy(bytes, 0, b, offset, bytes.length);
  }

  private static void number(byte[] b, int offset, int length, long n) {
    put(b, offset, length, String.format(Locale.ROOT, "%0" + length + "d", n));
  }

  private static String ascii(byte[] b, int start, int length) {
    return new String(b, start, length, StandardCharsets.US_ASCII);
  }
}
