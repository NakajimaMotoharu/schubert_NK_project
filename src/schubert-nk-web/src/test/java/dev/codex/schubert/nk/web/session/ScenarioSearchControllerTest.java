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
import dev.codex.schubert.nk.web.config.ScenarioMvcConfiguration;
import dev.codex.schubert.nk.web.controller.ScenarioController;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.messaging.ScenarioWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.view.ScenarioSearchViewModel;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
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
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;

/** NK-WEB002/FUN003/AUT/TST/UI223,234/SS313,314,323/SSC072/PG203/PT-SCR034..045. */
class ScenarioSearchControllerTest {
  private static final String FIXTURE_SUCCESS_CODE = "0000";
  private static final String EXPECTED_SECOND_GAME_CODE = "NUKITASHI2";
  private static final String EXPECTED_PAGE_ATTRIBUTE = "page";
  private static final String EXPECTED_SEARCH_VIEW = "search";
  private static final String FIXTURE_SEARCH_PREFIX = "SRC";
  private static final String FIXTURE_GAME_PREFIX = "GAM";
  private static final String FIXTURE_SPEAKER_PREFIX = "SPK";
  private static final String FIXTURE_INVALID_INPUT = "bad";
  private static final String FIXTURE_HTTP_GET = "GET";
  private static final String FIXTURE_SEARCH_PATH = "/search";

  private static WebLogDatabaseFixture db;
  @TempDir Path root;
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-20T00:00:00Z"), ZoneOffset.UTC);

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
        "reader",
        role,
        AuthenticationContext.of("a".repeat(64)),
        Instant.parse("2026-09-19T00:00:00Z"));
  }

  private static LinkedMultiValueMap<String, String> params(String... values) {
    var result = new LinkedMultiValueMap<String, String>();
    for (int i = 0; i < values.length; i += 2) result.add(values[i], values[i + 1]);
    return result;
  }

  @Test
  void search034SuccessAndWire() throws Exception {
    try (var f = new Fixture()) {
      for (var role : UserRole.values())
        for (String code : List.of(FIXTURE_SUCCESS_CODE, "0200"))
          for (int count : new int[] {0, 1, 100}) {
            f.code = code;
            f.count = count;
            for (var input :
                List.of(
                    params(),
                    params(
                        "q",
                        "  e\u0301本文  ",
                        "game",
                        EXPECTED_SECOND_GAME_CODE,
                        "speaker",
                        "話者",
                        "chapter",
                        "章",
                        "entry_type",
                        "dialogue",
                        "voice",
                        "with",
                        EXPECTED_PAGE_ATTRIBUTE,
                        "0"))) {
              int before = f.requests.size();
              var model = new ExtendedModelMap();
              var response = new MockHttpServletResponse();
              assertEquals(
                  EXPECTED_SEARCH_VIEW,
                  f.controller.search(input, actor(role), model, raw(), response));
              assertEquals(200, response.getStatus());
              assertEquals(Set.of(EXPECTED_PAGE_ATTRIBUTE), model.keySet());
              var page =
                  assertInstanceOf(
                      ScenarioSearchViewModel.class, model.get(EXPECTED_PAGE_ATTRIBUTE));
              assertEquals(
                  switch (role) {
                    case USER -> "USER";
                    case ADMIN -> "ADMIN";
                  },
                  page.getTopBar().getRole());
              assertEquals(count, page.getResults().orElseThrow().getRows().size());
              assertEquals(List.of("NUKITASHI1", EXPECTED_SECOND_GAME_CODE), page.getGames());
              assertEquals(List.of("話者", "別話者"), page.getSpeakers());
              var sent = f.requests.subList(before, before + 3);
              assertEquals(
                  List.of(FIXTURE_SEARCH_PREFIX, FIXTURE_GAME_PREFIX, FIXTURE_SPEAKER_PREFIX),
                  sent.stream().map(b -> ascii(b, 11, 3)).toList());
              byte[] expected = new byte[672];
              Arrays.fill(expected, (byte) ' ');
              put(expected, 0, 256, input.isEmpty() ? "" : "é本文");
              put(expected, 256, 12, input.isEmpty() ? "" : EXPECTED_SECOND_GAME_CODE);
              put(expected, 268, 128, input.isEmpty() ? "" : "話者");
              put(expected, 396, 256, input.isEmpty() ? "" : "章");
              put(expected, 652, 10, input.isEmpty() ? "" : "dialogue");
              put(expected, 662, 1, input.isEmpty() ? "" : "1");
              put(expected, 663, 6, "000001");
              put(expected, 669, 3, "100");
              assertArrayEquals(expected, Arrays.copyOfRange(sent.get(0), 256, 928));
              assertEquals(256, sent.get(1).length);
              String speakerGame = input.isEmpty() ? "            " : "NUKITASHI2  ";
              assertEquals(12, speakerGame.getBytes(StandardCharsets.US_ASCII).length);
              assertEquals(268, sent.get(2).length);
              assertEquals(speakerGame, ascii(sent.get(2), 256, 12));
              for (byte[] b : sent) assertEquals("a".repeat(64), ascii(b, 113, 64));
              f.erased();
            }
          }
    }
  }

  @Test
  void search035InvalidNoMq() throws Exception {
    try (var f = new Fixture()) {
      for (var input :
          List.of(
              params("q", "one", "q", "two"),
              params("unknown", "private"),
              params("game", FIXTURE_INVALID_INPUT),
              params("speaker", "あ".repeat(43)),
              params("q", "a".repeat(257)),
              params("chapter", "a".repeat(257)),
              params("entry_type", FIXTURE_INVALID_INPUT),
              params("voice", FIXTURE_INVALID_INPUT),
              params(EXPECTED_PAGE_ATTRIBUTE, "+1"),
              params("q", "\n"))) {
        var model = new ExtendedModelMap();
        var response = new MockHttpServletResponse();
        assertEquals(
            EXPECTED_SEARCH_VIEW,
            f.controller.search(input, actor(UserRole.USER), model, raw(), response));
        assertEquals(400, response.getStatus());
        var page =
            assertInstanceOf(ScenarioSearchViewModel.class, model.get(EXPECTED_PAGE_ATTRIBUTE));
        assertFalse(page.getErrors().isEmpty());
        assertTrue(page.getResults().isEmpty());
        assertEquals(0, f.requests.size());
      }
    }
  }

  @Test
  void search036ResultErrorsAtEveryStage() throws Exception {
    try (var f = new Fixture()) {
      String[] codes = {"0100", "0101", "0103", "0104", "0105", "0106", "0107", "9000", "9001"};
      int[] statuses = {400, 401, 403, 404, 409, 429, 409, 503, 503};
      for (String stage :
          List.of(FIXTURE_SEARCH_PREFIX, FIXTURE_GAME_PREFIX, FIXTURE_SPEAKER_PREFIX))
        for (int i = 0; i < codes.length; i++) {
          f.failureStage = stage;
          f.code = codes[i];
          int before = f.requests.size();
          var model = new ExtendedModelMap();
          var response = new MockHttpServletResponse();
          assertNull(f.controller.search(params(), actor(UserRole.USER), model, raw(), response));
          assertEquals(statuses[i], response.getStatus());
          assertTrue(model.isEmpty());
          assertEquals(
              List.of(FIXTURE_SEARCH_PREFIX, FIXTURE_GAME_PREFIX, FIXTURE_SPEAKER_PREFIX)
                      .indexOf(stage)
                  + 1,
              f.requests.size() - before);
          f.erased();
        }
    }
  }

  @Test
  void search037SessionInvalidAtEveryStage() throws Exception {
    try (var f = new Fixture()) {
      for (String stage :
          List.of(FIXTURE_SEARCH_PREFIX, FIXTURE_GAME_PREFIX, FIXTURE_SPEAKER_PREFIX)) {
        f.failureStage = stage;
        f.code = "0102";
        int before = f.requests.size();
        var request = f.security.mock(FIXTURE_HTTP_GET, FIXTURE_SEARCH_PATH);
        var response = new MockHttpServletResponse();
        SecurityContextHolder.getContext()
            .setAuthentication(
                UsernamePasswordAuthenticationToken.authenticated(
                    actor(UserRole.USER), null, List.of(new SimpleGrantedAuthority("ROLE_USER"))));
        var model = new ExtendedModelMap();
        assertNull(f.controller.search(params(), actor(UserRole.USER), model, request, response));
        assertEquals(302, response.getStatus());
        assertEquals("/login?session-expired", response.getRedirectedUrl());
        assertNull(SecurityContextHolder.getContext().getAuthentication());
        assertNull(request.getSession(false));
        assertTrue(model.isEmpty());
        assertEquals(
            List.of(FIXTURE_SEARCH_PREFIX, FIXTURE_GAME_PREFIX, FIXTURE_SPEAKER_PREFIX)
                    .indexOf(stage)
                + 1,
            f.requests.size() - before);
        f.erased();
      }
    }
  }

  @Test
  void search038MalformedAndTransport() throws Exception {
    try (var f = new Fixture()) {
      for (String stage :
          List.of(FIXTURE_SEARCH_PREFIX, FIXTURE_GAME_PREFIX, FIXTURE_SPEAKER_PREFIX))
        for (boolean transport : new boolean[] {false, true}) {
          f.responder =
              (id, b) -> {
                if (ascii(b, 11, 3).equals(stage)) {
                  if (transport) throw new jakarta.jms.JMSRuntimeException("synthetic");
                  return new byte[] {0};
                }
                return f.standard(id, b);
              };
          int before = f.requests.size();
          var model = new ExtendedModelMap();
          var response = new MockHttpServletResponse();
          assertNull(f.controller.search(params(), actor(UserRole.USER), model, raw(), response));
          assertEquals(503, response.getStatus());
          assertTrue(model.isEmpty());
          assertEquals(
              List.of(FIXTURE_SEARCH_PREFIX, FIXTURE_GAME_PREFIX, FIXTURE_SPEAKER_PREFIX)
                      .indexOf(stage)
                  + 1,
              f.requests.size() - before);
          f.erased();
        }
    }
  }

  @Test
  void search039ResponseBinding() throws Exception {
    try (var f = new Fixture()) {
      f.count = 1;
      for (boolean valid : new boolean[] {true, false}) {
        f.responder =
            (id, b) -> {
              byte[] result = f.standard(id, b);
              if (!valid && ascii(b, 11, 3).equals(FIXTURE_SEARCH_PREFIX)) {
                number(result, 256, 6, 2);
                number(result, 265, 9, 101);
                number(result, 274, 6, 2);
                number(result, 280, 9, 101);
                number(result, 289, 9, 101);
              }
              return result;
            };
        var model = new ExtendedModelMap();
        var response = new MockHttpServletResponse();
        String view =
            f.controller.search(
                params(EXPECTED_PAGE_ATTRIBUTE, valid ? "999999" : "1"),
                actor(UserRole.USER),
                model,
                raw(),
                response);
        if (valid) {
          assertEquals(EXPECTED_SEARCH_VIEW, view);
          assertEquals(200, response.getStatus());
          assertEquals(
              1,
              ((ScenarioSearchViewModel) model.get(EXPECTED_PAGE_ATTRIBUTE))
                  .getResults()
                  .orElseThrow()
                  .getPage()
                  .getEffectivePage());
        } else {
          assertNull(view);
          assertEquals(503, response.getStatus());
          assertTrue(model.isEmpty());
        }
      }
      f.erased();
    }
  }

  @Test
  void search040NullAndFailurePropagation() throws Exception {
    try (var f = new Fixture()) {
      var p = actor(UserRole.USER);
      var m = new ExtendedModelMap();
      var r = raw();
      var s = new MockHttpServletResponse();
      assertThrows(NullPointerException.class, () -> f.controller.search(null, p, m, r, s));
      assertThrows(NullPointerException.class, () -> f.controller.search(params(), null, m, r, s));
      assertThrows(NullPointerException.class, () -> f.controller.search(params(), p, null, r, s));
      assertThrows(NullPointerException.class, () -> f.controller.search(params(), p, m, null, s));
      assertThrows(NullPointerException.class, () -> f.controller.search(params(), p, m, r, null));
      assertThrows(
          SessionStoreException.class,
          () -> f.controller.search(params(), () -> "foreign", m, r, s));
      assertEquals(0, f.requests.size());
      var failure = new IllegalArgumentException("synthetic model failure");
      var broken =
          new ExtendedModelMap() {
            @Override
            public ExtendedModelMap addAttribute(String name, Object value) {
              throw failure;
            }
          };
      for (var input : List.of(params(), params(EXPECTED_PAGE_ATTRIBUTE, FIXTURE_INVALID_INPUT)))
        assertSame(
            failure,
            assertThrows(
                IllegalArgumentException.class, () -> f.controller.search(input, p, broken, r, s)));
      var unknown = new AssertionError("synthetic");
      f.responder =
          (id, b) -> {
            throw unknown;
          };
      assertSame(
          unknown,
          assertThrows(AssertionError.class, () -> f.controller.search(params(), p, m, r, s)));
      f.responder = f::standard;
      f.failureStage = FIXTURE_SEARCH_PREFIX;
      f.code = "9000";
      var io = new IOException("synthetic response failure");
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
              IOException.class, () -> f.controller.search(params(), p, m, r, brokenResponse)));
      f.erased();
    }
  }

  @Test
  void search041MvcGetHeadAndMethod() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      var p = actor(UserRole.USER);
      var result = mvc.perform(pageRequest(p)).andReturn();
      assertEquals(200, result.getResponse().getStatus());
      assertEquals(
          "schubert NK - 検索", Jsoup.parse(result.getResponse().getContentAsString()).title());
      int before = f.requests.size();
      var h =
          mvc.perform(
                  head(FIXTURE_SEARCH_PATH)
                      .principal(p)
                      .requestAttr(CsrfToken.class.getName(), csrf()))
              .andReturn();
      assertEquals(200, h.getResponse().getStatus());
      // BUG220: MockMvc observes rendering; real transport HEAD body suppression is SCR042.
      assertEquals(EXPECTED_SEARCH_VIEW, Objects.requireNonNull(h.getModelAndView()).getViewName());
      assertEquals("schubert NK - 検索", Jsoup.parse(h.getResponse().getContentAsString()).title());
      assertEquals(before + 3, f.requests.size());
      before = f.requests.size();
      assertEquals(
          405,
          mvc.perform(post(FIXTURE_SEARCH_PATH).principal(p))
              .andReturn()
              .getResponse()
              .getStatus());
      assertEquals(before, f.requests.size());
      for (var builder :
          List.of(pageRequest(p).param("unknown", "x"), pageRequest(p).param("q", "a", "b"))) {
        var bad = mvc.perform(builder).andReturn();
        assertEquals(400, bad.getResponse().getStatus());
        var dom = Jsoup.parse(bad.getResponse().getContentAsString());
        assertFalse(dom.select("#search-errors li").isEmpty());
        assertTrue(dom.select(".result,.count").isEmpty());
        assertEquals(before, f.requests.size());
      }
      f.erased();
    }
  }

  @Test
  void search042RealHttpSecurity() throws Exception {
    for (String role : List.of("USER", "ADMIN")) {
      reset();
      var api = new SessionFormLoginTest.Api(FIXTURE_SUCCESS_CODE, role, FIXTURE_SUCCESS_CODE, 0);
      try (var f = new Fixture();
          var server =
              new EmbeddedWebSecurityTest.Server(
                  Files.createTempDirectory(root, "search-"),
                  false,
                  db,
                  Optional.of(api.provider),
                  true,
                  true,
                  (mvc, invalid) -> configure(mvc, f.client, invalid))) {
        var anonymous = server.send(FIXTURE_HTTP_GET, FIXTURE_SEARCH_PATH, null, null, true);
        assertEquals(302, anonymous.statusCode());
        assertEquals("/login", anonymous.headers().firstValue("location").orElseThrow());
        assertEquals(0, f.requests.size());
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
        var result = server.send(FIXTURE_HTTP_GET, "/search?q=hello", cookie, null, true);
        assertEquals(200, result.statusCode());
        var dom = Jsoup.parse(result.body());
        assertEquals(role, dom.select(".login-role").text());
        assertEquals("hello", dom.select("input[name=q]").attr("value"));
        assertEquals(1, dom.select("input[name=_csrf]").size());
        assertTrue(result.headers().firstValue("cache-control").orElseThrow().contains("no-store"));
        assertEquals(
            "nosniff", result.headers().firstValue("x-content-type-options").orElseThrow());
        int beforeHead = f.requests.size();
        var head = server.send("HEAD", "/search?q=hello", cookie, null, true);
        assertEquals(200, head.statusCode());
        assertEquals("", head.body());
        assertTrue(head.headers().firstValue("cache-control").orElseThrow().contains("no-store"));
        assertEquals(beforeHead + 3, f.requests.size());
        int before = f.requests.size();
        assertEquals(
            400,
            server.send(FIXTURE_HTTP_GET, "/search?page=bad", cookie, null, true).statusCode());
        assertEquals(before, f.requests.size());
        f.failureStage = FIXTURE_GAME_PREFIX;
        f.code = "0102";
        var expired = server.send(FIXTURE_HTTP_GET, FIXTURE_SEARCH_PATH, cookie, null, true);
        assertEquals(302, expired.statusCode());
        assertEquals(
            "/login?session-expired", expired.headers().firstValue("location").orElseThrow());
        assertTrue(expired.headers().firstValue("set-cookie").orElseThrow().contains("Max-Age=0"));
        assertEquals(before + 2, f.requests.size());
        assertEquals(
            302,
            server.send(FIXTURE_HTTP_GET, FIXTURE_SEARCH_PATH, cookie, null, true).statusCode());
        assertEquals(before + 2, f.requests.size());
        assertEquals(0, server.context.getManager().getActiveSessions());
        f.erased();
        api.erased();
      }
    }
  }

  @Test
  void search043EscapingAndIsolation() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      String canary = "<img src=x onerror=alert(1)>";
      var p =
          new SessionPrincipal(
              canary,
              UserRole.ADMIN,
              actor(UserRole.USER).authenticationContext(),
              actor(UserRole.USER).loginAt());
      var result =
          MockMvcBuilders.webAppContextSetup(context)
              .build()
              .perform(
                  pageRequest(p)
                      .param("q", canary)
                      .param("speaker", canary)
                      .param("chapter", canary))
              .andReturn();
      assertEquals(200, result.getResponse().getStatus());
      var dom = Jsoup.parse(result.getResponse().getContentAsString());
      assertEquals(canary, dom.select(".login-user").text());
      assertEquals(canary, dom.select("input[name=q]").attr("value"));
      assertEquals(canary, dom.select("input[name=chapter]").attr("value"));
      assertTrue(dom.select("img,[onerror],script:not([src])").isEmpty());
      assertFalse(result.getResponse().getContentAsString().contains("a".repeat(64)));
      assertEquals("/scenarios/7#entry-1", dom.select(".result a[href*='#entry-1']").attr("href"));
      f.erased();
    }
  }

  @Test
  void search044ConcurrentRequests() throws Exception {
    try (var f = new Fixture();
        var executor = Executors.newFixedThreadPool(8)) {
      var tasks = new ArrayList<Future<?>>();
      for (int i = 0; i < 64; i++) {
        final int n = i;
        tasks.add(
            executor.submit(
                () -> {
                  var p =
                      new SessionPrincipal(
                          "reader" + n,
                          UserRole.USER,
                          AuthenticationContext.of(String.format(Locale.ROOT, "%064x", n + 1)),
                          actor(UserRole.USER).loginAt());
                  var model = new ExtendedModelMap();
                  var response = new MockHttpServletResponse();
                  assertEquals(
                      EXPECTED_SEARCH_VIEW,
                      f.controller.search(params("q", "query" + n), p, model, raw(), response));
                  var page = (ScenarioSearchViewModel) model.get(EXPECTED_PAGE_ATTRIBUTE);
                  assertEquals("reader" + n, page.getTopBar().getUsername());
                  assertEquals("query" + n, page.getFilters().getQ());
                  return null;
                }));
      }
      for (var task : tasks) task.get(10, TimeUnit.SECONDS);
      assertEquals(192, f.requests.size());
      assertEquals(192, f.correlations.size());
      for (int i = 0; i < 64; i++) {
        String context = String.format(Locale.ROOT, "%064x", i + 1);
        var requests = f.requests.stream().filter(b -> ascii(b, 113, 64).equals(context)).toList();
        assertEquals(
            List.of(FIXTURE_SEARCH_PREFIX, FIXTURE_GAME_PREFIX, FIXTURE_SPEAKER_PREFIX),
            requests.stream().map(b -> ascii(b, 11, 3)).toList());
        assertEquals(
            "query" + i,
            new String(requests.getFirst(), 256, 256, StandardCharsets.UTF_8).stripTrailing());
      }
      f.erased();
    }
  }

  @Test
  void search045CompatibilityTrace() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      var dom =
          Jsoup.parse(
              mvc.perform(pageRequest(actor(UserRole.USER)))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals(List.of("本文1", "本文2"), dom.select(".result-body > p").eachText());
      assertEquals(
          List.of("/scenarios/7#entry-1", "/scenarios/7#entry-2"),
          dom.select(".result a[href*='#entry-']").eachAttr("href"));
      assertEquals(1, dom.select("audio").size());
      assertEquals("/audio/9", dom.select("audio").attr("src"));
      assertEquals("/audio/9/download", dom.select("a.download").attr("href"));
      assertEquals("2 results / page 1 of 1", dom.select(".count").text());
      f.count = 0;
      dom =
          Jsoup.parse(
              mvc.perform(pageRequest(actor(UserRole.USER)))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals("該当するデータはありません", dom.select(".empty-results").text());
      assertTrue(dom.select(".result,.pagination").isEmpty());
      Path directory = Path.of("target/scenario-screen-traces");
      Files.createDirectories(directory);
      Files.writeString(
          directory.resolve("PT-SCR-045.txt"),
          "screen=SCR003\n"
              + "fixture=public-synthetic\n"
              + "requestOrder=SRC|GAM|SPK\n"
              + "results=2\n"
              + "representativeAudio=1\n"
              + "empty=PASS\n"
              + "actualNkGate=false\n",
          StandardCharsets.US_ASCII);
      f.erased();
    }
  }

  private static MockHttpServletRequest raw() {
    var r = new MockHttpServletRequest(FIXTURE_HTTP_GET, FIXTURE_SEARCH_PATH);
    r.setRemoteAddr("127.0.0.1");
    return r;
  }

  private static CsrfToken csrf() {
    return new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", "b".repeat(64));
  }

  private static org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder
      pageRequest(SessionPrincipal p) {
    return get(FIXTURE_SEARCH_PATH).principal(p).requestAttr(CsrfToken.class.getName(), csrf());
  }

  private static void configure(
      AnnotationConfigWebApplicationContext context,
      ScenarioWireClient client,
      ApiSessionInvalidHandler invalid) {
    context.register(ScenarioMvcConfiguration.class);
    context.addBeanFactoryPostProcessor(
        factory -> {
          factory.registerSingleton("scenarioWireClient", client);
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
    volatile String failureStage = "";
    volatile BiFunction<UUID, byte[], byte[]> responder = this::standard;
    final JmsRequestReplyClient wire =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    final ScenarioWireClient client =
        new ScenarioWireClient(
            wire,
            (id, b) -> {
              assertTrue(correlations.add(id));
              buffers.add(b);
              requests.add(b.clone());
              String type = ascii(b, 11, 3);
              int length =
                  switch (type) {
                    case FIXTURE_SEARCH_PREFIX -> 672;
                    case FIXTURE_GAME_PREFIX -> 0;
                    case FIXTURE_SPEAKER_PREFIX -> 12;
                    default -> throw new AssertionError();
                  };
              assertEquals(256 + length, b.length);
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
    final ScenarioController controller = new ScenarioController(client, security.handler);

    AnnotationConfigWebApplicationContext mvc() {
      var context = new AnnotationConfigWebApplicationContext();
      context.setServletContext(new MockServletContext());
      configure(context, client, security.handler);
      context.refresh();
      return context;
    }

    byte[] standard(UUID id, byte[] request) {
      String type = ascii(request, 11, 3);
      String result =
          failureStage.isEmpty() || failureStage.equals(type) ? code : FIXTURE_SUCCESS_CODE;
      return response(type, result, count, id, ascii(request, 113, 64));
    }

    void erased() {
      assertEquals(0, wire.pendingCount());
      for (byte[] b : buffers) assertArrayEquals(new byte[b.length], b);
    }

    @Override
    public void close() {
      for (byte[] b : requests) Arrays.fill(b, (byte) 0);
      security.close();
    }
  }

  // Independent UI232/234 byte positions. No Production encoder/mapper constructs expectations.
  private static byte[] response(
      String type, String code, int searchCount, UUID id, String context) {
    boolean success = code.equals(FIXTURE_SUCCESS_CODE) || code.equals("0200");
    int count = success ? (type.equals(FIXTURE_SEARCH_PREFIX) ? searchCount : 2) : 0;
    int data = type.equals(FIXTURE_SEARCH_PREFIX) ? 48 : 9;
    int record =
        switch (type) {
          case FIXTURE_SEARCH_PREFIX -> 5584;
          case FIXTURE_GAME_PREFIX -> 272;
          case FIXTURE_SPEAKER_PREFIX -> 152;
          default -> throw new AssertionError();
        };
    byte[] b = new byte[256 + data + record * count];
    Arrays.fill(b, (byte) ' ');
    put(b, 0, 8, "SCHBNK01");
    put(b, 8, 3, "001");
    put(b, 11, 8, type + "RSP01");
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
    if (type.equals(FIXTURE_SEARCH_PREFIX)) {
      number(b, 256, 6, success ? 1 : 0);
      number(b, 262, 3, success ? 100 : 0);
      number(b, 265, 9, count);
      number(b, 274, 6, success ? 1 : 0);
      number(b, 280, 9, count == 0 ? 0 : 1);
      number(b, 289, 9, count);
    } else number(b, 256, 9, count);
    for (int n = 0; n < count; n++) {
      int o = 256 + data + n * record;
      switch (type) {
        case FIXTURE_GAME_PREFIX -> {
          put(b, o, 12, n == 0 ? "NUKITASHI1" : EXPECTED_SECOND_GAME_CODE);
          put(b, o + 12, 256, n == 0 ? "NUKITASHI" : EXPECTED_SECOND_GAME_CODE);
          number(b, o + 268, 3, n + 1);
        }
        case FIXTURE_SPEAKER_PREFIX -> {
          number(b, o, 12, n + 1);
          put(b, o + 12, 128, n == 0 ? "話者" : "別話者");
          number(b, o + 140, 9, 20 - n);
        }
        case FIXTURE_SEARCH_PREFIX -> {
          number(b, o, 12, n + 1);
          number(b, o + 12, 12, 7);
          put(b, o + 24, 12, "NUKITASHI1");
          put(b, o + 36, 256, "章");
          number(b, o + 292, 8, n + 1);
          put(b, o + 300, 10, "dialogue");
          put(b, o + 310, 128, "話者");
          put(b, o + 438, 4096, "本文" + (n + 1));
          put(b, o + 4534, 1, n == 0 ? "1" : "0");
          put(b, o + 4535, 12, n == 0 ? "9" : "");
          put(b, o + 4547, 512, "game/file.txt");
          put(b, o + 5059, 512, n == 0 ? "voice/9.ogg" : "");
        }
        default -> throw new AssertionError();
      }
    }
    return b;
  }

  private static String ascii(byte[] b, int offset, int length) {
    return new String(b, offset, length, StandardCharsets.US_ASCII);
  }

  private static void put(byte[] b, int offset, int length, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    assertTrue(bytes.length <= length);
    Arrays.fill(b, offset, offset + length, (byte) ' ');
    System.arraycopy(bytes, 0, b, offset, bytes.length);
  }

  private static void number(byte[] b, int offset, int length, long value) {
    put(b, offset, length, String.format(Locale.ROOT, "%0" + length + "d", value));
  }
}
