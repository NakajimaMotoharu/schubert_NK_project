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
import dev.codex.schubert.nk.web.config.MusicMvcConfiguration;
import dev.codex.schubert.nk.web.controller.MusicController;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.MusicWireClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.view.MusicCategoryViewModel;
import dev.codex.schubert.nk.web.view.MusicSectionViewModel;
import dev.codex.schubert.nk.web.view.TopBarViewModel;
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

/** NK-WEB002/FUN007/AUT/TST/UI223,235/SS313,314,323/PG211/PT-SCR072..083. */
class MusicControllerTest {
  private static final String FIXTURE_MENU_PATH = "/music";
  private static final String FIXTURE_SUCCESS_CODE = "0000";
  private static final String EXPECTED_SECTIONS_VIEW = "music-sections";
  private static final String EXPECTED_PAGE_ATTRIBUTE = "page";
  private static final String FIXTURE_HTTP_GET = "GET";
  private static final String FIXTURE_FAILURE_MESSAGE = "synthetic";
  private static final String FIXTURE_CATEGORY_PREFIX = "MCT";
  private static final String FIXTURE_ESCAPED_TEXT = "<b>&";
  private static final String EXPECTED_MENU_TITLE_SELECTOR = ".menu-item strong";
  private static final String EXPECTED_MENU_ITEM_SELECTOR = ".menu-item";
  private static final int FIXTURE_THROW_MODE = 3;
  private static final int FIXTURE_CORRELATION_MISMATCH_MODE = 1;

  private static WebLogDatabaseFixture db;
  @TempDir Path root;
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-20T00:00:00Z"), ZoneOffset.UTC);
  private static final List<String> PATHS = List.of(FIXTURE_MENU_PATH, "/music/BGM");

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
      MusicController c,
      String path,
      Principal p,
      Model m,
      HttpServletRequest r,
      HttpServletResponse s)
      throws IOException {
    return path.equals(FIXTURE_MENU_PATH)
        ? c.categories(p, m, r, s)
        : c.sections(path.substring(7), p, m, r, s);
  }

  @Test
  void music072SuccessAndWire() throws Exception {
    try (var f = new Fixture()) {
      for (var role : UserRole.values())
        for (var code : List.of(FIXTURE_SUCCESS_CODE, "0200"))
          for (int n : new int[] {1, 2})
            for (var path : PATHS) {
              f.code = code;
              f.count = n;
              int before = f.requests.size();
              var m = new ExtendedModelMap();
              var s = new MockHttpServletResponse();
              assertEquals(
                  path.equals(FIXTURE_MENU_PATH) ? "music" : EXPECTED_SECTIONS_VIEW,
                  call(f.controller, path, actor(role), m, raw(path), s));
              assertEquals(200, s.getStatus());
              assertEquals(Set.of(EXPECTED_PAGE_ATTRIBUTE), m.keySet());
              TopBarViewModel bar;
              if (path.equals(FIXTURE_MENU_PATH)) {
                var page =
                    assertInstanceOf(MusicCategoryViewModel.class, m.get(EXPECTED_PAGE_ATTRIBUTE));
                assertEquals(n, page.getCategories().size());
                assertEquals(n * (n + 1) / 2, page.getTrackCount());
                bar = page.getTopBar();
              } else {
                var page =
                    assertInstanceOf(MusicSectionViewModel.class, m.get(EXPECTED_PAGE_ATTRIBUTE));
                assertEquals(n, page.getSections().size());
                assertEquals("BGM", page.getCategory());
                assertEquals(n * (n + 1) / 2, page.getTrackCount());
                bar = page.getTopBar();
              }
              assertEquals(
                  switch (role) {
                    case USER -> "USER";
                    case ADMIN -> "ADMIN";
                  },
                  bar.getRole());
              assertEquals(before + 1, f.requests.size());
              var b = f.requests.getLast();
              assertEquals(path.equals(FIXTURE_MENU_PATH) ? 256 : 320, b.length);
              if (!path.equals(FIXTURE_MENU_PATH))
                assertEquals("BGM" + " ".repeat(61), ascii(b, 256, 64));
              f.erased();
            }
    }
  }

  @Test
  void music073ErrorMapping() throws Exception {
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
  void music074SessionInvalid() throws Exception {
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
  void music075MalformedAndTransport() throws Exception {
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
  void music076ResponseBinding() throws Exception {
    try (var f = new Fixture()) {
      for (var path : PATHS)
        for (int mode = 0; mode < 3; mode++) {
          final int kind = mode;
          f.responder =
              (id, b) -> {
                var out = f.standard(id, b);
                boolean menu = path.equals(FIXTURE_MENU_PATH);
                int width = menu ? 64 : 128;
                int record = menu ? 72 : 136;
                if (kind == 0) put(out, 264 + record, width, "name0");
                else put(out, 264, width, kind == 1 ? "." : "..");
                return out;
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
  void music077NullAndUnknown() throws Exception {
    try (var f = new Fixture()) {
      assertThrows(NullPointerException.class, () -> new MusicController(null, f.security.handler));
      assertThrows(NullPointerException.class, () -> new MusicController(f.client, null));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.sections(
                  null,
                  actor(UserRole.USER),
                  new ExtendedModelMap(),
                  raw(FIXTURE_MENU_PATH),
                  new MockHttpServletResponse()));
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
  void music078MvcRoutesAndInput() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      for (var path : PATHS) {
        var result = mvc.perform(pageRequest(path, actor(UserRole.USER))).andReturn();
        assertEquals(200, result.getResponse().getStatus());
        assertEquals(
            path.equals(FIXTURE_MENU_PATH) ? "music" : EXPECTED_SECTIONS_VIEW,
            Objects.requireNonNull(result.getModelAndView()).getViewName());
        var h =
            mvc.perform(
                    head(path)
                        .principal(actor(UserRole.ADMIN))
                        .requestAttr(CsrfToken.class.getName(), csrf()))
                .andReturn();
        assertEquals(200, h.getResponse().getStatus());
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
      for (var path : List.of("/music/BGM/extra", "/music/BGM/extra/more"))
        assertEquals(
            404,
            mvc.perform(pageRequest(path, actor(UserRole.USER)))
                .andReturn()
                .getResponse()
                .getStatus());
      assertEquals(before, f.requests.size());
      for (String value :
          List.of(
              "",
              "x".repeat(65),
              "あ".repeat(22),
              "BGM ",
              "\r",
              "\n",
              "\t",
              "\0",
              "\ud800",
              "\udc00")) {
        var s = new MockHttpServletResponse();
        var m = new ExtendedModelMap();
        assertNull(
            f.controller.sections(value, actor(UserRole.USER), m, raw(FIXTURE_MENU_PATH), s));
        assertEquals(400, s.getStatus());
        assertTrue(m.isEmpty());
      }
      assertEquals(before, f.requests.size());
      for (String value : List.of("x".repeat(64), "あ".repeat(21) + "x", "e\u0301", " BGM")) {
        var s = new MockHttpServletResponse();
        var m = new ExtendedModelMap();
        assertEquals(
            EXPECTED_SECTIONS_VIEW,
            f.controller.sections(value, actor(UserRole.USER), m, raw(FIXTURE_MENU_PATH), s));
        assertEquals(200, s.getStatus());
        var expected = new byte[64];
        Arrays.fill(expected, (byte) ' ');
        var bytes = (value.equals("e\u0301") ? "é" : value).getBytes(StandardCharsets.UTF_8);
        System.arraycopy(bytes, 0, expected, 0, bytes.length);
        assertArrayEquals(expected, Arrays.copyOfRange(f.requests.getLast(), 256, 320));
      }
      f.erased();
    }
  }

  @Test
  void music079RealHttpSecurity() throws Exception {
    for (String role : List.of("USER", "ADMIN")) {
      reset();
      var api = new SessionFormLoginTest.Api(FIXTURE_SUCCESS_CODE, role, FIXTURE_SUCCESS_CODE, 0);
      try (var f = new Fixture();
          var server =
              new EmbeddedWebSecurityTest.Server(
                  Files.createTempDirectory(root, "music-"),
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
        var expired = server.send(FIXTURE_HTTP_GET, "/music/BGM", cookie, null, true);
        assertEquals(302, expired.statusCode());
        assertEquals(
            "/login?session-expired", expired.headers().firstValue("location").orElseThrow());
        assertTrue(expired.headers().firstValue("set-cookie").orElseThrow().contains("Max-Age=0"));
        assertEquals(before + 1, f.requests.size());
        assertEquals(
            302, server.send(FIXTURE_HTTP_GET, FIXTURE_MENU_PATH, cookie, null, true).statusCode());
        assertEquals(before + 1, f.requests.size());
        assertEquals(0, server.context.getManager().getActiveSessions());
        f.erased();
        api.erased();
      }
    }
  }

  @Test
  void music080EscapingAndIsolation() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      f.count = 1;
      f.responder =
          (id, b) -> {
            var out = f.standard(id, b);
            put(
                out,
                264,
                ascii(b, 11, 3).equals(FIXTURE_CATEGORY_PREFIX) ? 64 : 128,
                FIXTURE_ESCAPED_TEXT);
            return out;
          };
      for (var path : PATHS) {
        var p =
            new SessionPrincipal(
                FIXTURE_ESCAPED_TEXT,
                UserRole.ADMIN,
                actor(UserRole.USER).authenticationContext(),
                actor(UserRole.USER).loginAt());
        var dom =
            Jsoup.parse(
                mvc.perform(pageRequest(path, p)).andReturn().getResponse().getContentAsString());
        assertEquals(FIXTURE_ESCAPED_TEXT, dom.select(".login-user").text());
        assertEquals(FIXTURE_ESCAPED_TEXT, dom.select(EXPECTED_MENU_TITLE_SELECTOR).text());
        assertEquals(
            path.equals(FIXTURE_MENU_PATH) ? "/music/%3Cb%3E%26" : "/music/BGM/%3Cb%3E%26",
            dom.select(EXPECTED_MENU_ITEM_SELECTOR).attr("href"));
        assertTrue(dom.select("b,img,script,[onerror],[onclick]").isEmpty());
        assertFalse(dom.outerHtml().contains("a".repeat(64)));
      }
      var m = new ExtendedModelMap();
      var s = new MockHttpServletResponse();
      assertEquals(
          EXPECTED_SECTIONS_VIEW,
          f.controller.sections("曲", actor(UserRole.USER), m, raw("/music/曲"), s));
      assertEquals(
          "/music/%E6%9B%B2/%3Cb%3E%26",
          ((MusicSectionViewModel) m.get(EXPECTED_PAGE_ATTRIBUTE))
              .getSections()
              .getFirst()
              .getHref());
      f.erased();
    }
  }

  @Test
  void music081EmptyAndMaximum() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      f.count = 0;
      var empty = mvc.perform(pageRequest(FIXTURE_MENU_PATH, actor(UserRole.USER))).andReturn();
      assertEquals(200, empty.getResponse().getStatus());
      var dom = Jsoup.parse(empty.getResponse().getContentAsString());
      assertEquals("0曲", dom.select(".subtitle").text());
      assertTrue(dom.select(EXPECTED_MENU_ITEM_SELECTOR).isEmpty());
      assertEquals(
          404,
          mvc.perform(pageRequest("/music/unknown", actor(UserRole.USER)))
              .andReturn()
              .getResponse()
              .getStatus());
      for (var path : PATHS) {
        f.count = path.equals(FIXTURE_MENU_PATH) ? 20 : 100;
        var result = mvc.perform(pageRequest(path, actor(UserRole.USER))).andReturn();
        assertEquals(200, result.getResponse().getStatus());
        dom = Jsoup.parse(result.getResponse().getContentAsString());
        assertEquals(f.count, dom.select(EXPECTED_MENU_ITEM_SELECTOR).size());
        assertEquals(
            path.equals(FIXTURE_MENU_PATH) ? "210曲" : "5050曲", dom.select(".subtitle").text());
        assertEquals("name0", dom.select(EXPECTED_MENU_TITLE_SELECTOR).getFirst().text());
        assertEquals(
            "name" + (f.count - 1), dom.select(EXPECTED_MENU_TITLE_SELECTOR).getLast().text());
      }
      f.erased();
    }
  }

  @Test
  void music082ConcurrentRequests() throws Exception {
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
                  var path = PATHS.get(n % 2);
                  var m = new ExtendedModelMap();
                  var s = new MockHttpServletResponse();
                  assertEquals(
                      n % 2 == 0 ? "music" : EXPECTED_SECTIONS_VIEW,
                      call(f.controller, path, p, m, raw(path), s));
                  var page = m.get(EXPECTED_PAGE_ATTRIBUTE);
                  var bar =
                      page instanceof MusicCategoryViewModel menu
                          ? menu.getTopBar()
                          : ((MusicSectionViewModel) page).getTopBar();
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
        assertEquals(i % 2 == 0 ? "MCTREQ01" : "MCSREQ01", ascii(requests.getFirst(), 11, 8));
      }
      f.erased();
    }
  }

  @Test
  void music083CompatibilityTrace() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      for (var path : PATHS) {
        var dom =
            Jsoup.parse(
                mvc.perform(pageRequest(path, actor(UserRole.USER)))
                    .andReturn()
                    .getResponse()
                    .getContentAsString());
        assertEquals(path.equals(FIXTURE_MENU_PATH) ? "Music" : "BGM", dom.title());
        assertEquals(
            List.of("name0", "name1"), dom.select(EXPECTED_MENU_TITLE_SELECTOR).eachText());
        assertEquals("3曲", dom.select(".subtitle").text());
        assertEquals(
            path.equals(FIXTURE_MENU_PATH)
                ? List.of("/music/name0", "/music/name1")
                : List.of("/music/BGM/name0", "/music/BGM/name1"),
            dom.select(EXPECTED_MENU_ITEM_SELECTOR).eachAttr("href"));
        assertEquals(
            path.equals(FIXTURE_MENU_PATH)
                ? List.of("/scenarios", "/search", "/animation")
                : List.of(FIXTURE_MENU_PATH, "/search"),
            dom.select("nav[aria-label=Musicナビゲーション] a").eachAttr("href"));
      }
      var directory = Path.of("target/scenario-screen-traces");
      Files.createDirectories(directory);
      Files.writeString(
          directory.resolve("PT-SCR-083.txt"),
          "screens=SCR011|SCR012\n"
              + "fixture=public-synthetic\n"
              + "routes=2\n"
              + "categories=2\n"
              + "sections=2\n"
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
      MusicWireClient client,
      ApiSessionInvalidHandler invalid) {
    context.register(MusicMvcConfiguration.class);
    context.addBeanFactoryPostProcessor(
        factory -> {
          factory.registerSingleton("musicWireClient", client);
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
    final MusicWireClient client =
        new MusicWireClient(
            wire,
            (id, b) -> {
              assertTrue(correlations.add(id));
              buffers.add(b);
              requests.add(b.clone());
              String type = ascii(b, 11, 3);
              assertTrue(type.equals(FIXTURE_CATEGORY_PREFIX) || type.equals("MCS"));
              assertEquals(type.equals(FIXTURE_CATEGORY_PREFIX) ? 256 : 320, b.length);
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
    final MusicController controller = new MusicController(client, security.handler);

    AnnotationConfigWebApplicationContext mvc() {
      var context = new AnnotationConfigWebApplicationContext();
      context.setServletContext(new MockServletContext());
      configure(context, client, security.handler);
      context.refresh();
      return context;
    }

    byte[] standard(UUID id, byte[] b) {
      return response(ascii(b, 11, 3), count, code, id, ascii(b, 113, 64));
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

  private static byte[] response(String type, int n, String code, UUID id, String context) {
    boolean success = code.equals(FIXTURE_SUCCESS_CODE) || code.equals("0200");
    int count = success ? n : 0;
    boolean category = type.equals(FIXTURE_CATEGORY_PREFIX);
    int record = category ? 72 : 136;
    var b = header(type + "RSP01", 8, record, count, code, id, context);
    number(b, 256, 6, count);
    for (int i = 0; i < count; i++) {
      int at = 264 + i * record;
      put(b, at, category ? 64 : 128, "name" + i);
      number(b, at + (category ? 64 : 128), 6, i + 1);
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
