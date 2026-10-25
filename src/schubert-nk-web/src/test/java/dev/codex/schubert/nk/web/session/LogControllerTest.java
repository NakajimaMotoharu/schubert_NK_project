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
import dev.codex.schubert.nk.web.config.LogMvcConfiguration;
import dev.codex.schubert.nk.web.controller.LogController;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.LogSearchWireClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.view.LogSearchViewModel;
import jakarta.jms.JMSRuntimeException;
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
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;

/** NK-WEB-002/SCR014/FUN008/AUT002/UI225,232,235/SS313,314,323/PG218/PT-SCR093..103. */
class LogControllerTest {
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-20T00:00:00Z"), ZoneOffset.UTC);
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
    try (var connection = db.web();
        var statement = connection.createStatement()) {
      statement.executeUpdate("DELETE FROM schubert_web_session.web_http_sessions");
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

  private static LinkedMultiValueMap<String, String> params(String... pairs) {
    var result = new LinkedMultiValueMap<String, String>();
    for (int i = 0; i < pairs.length; i += 2) result.add(pairs[i], pairs[i + 1]);
    return result;
  }

  private static MockHttpServletRequest raw() {
    var request = new MockHttpServletRequest("GET", "/logs");
    request.setRemoteAddr("127.0.0.1");
    return request;
  }

  private static CsrfToken csrf() {
    return new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", "b".repeat(64));
  }

  private static org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder
      pageRequest(SessionPrincipal principal) {
    return get("/logs").principal(principal).requestAttr(CsrfToken.class.getName(), csrf());
  }

  private static void configure(
      AnnotationConfigWebApplicationContext context,
      LogSearchWireClient client,
      ApiSessionInvalidHandler invalid) {
    context.register(LogMvcConfiguration.class);
    context.addBeanFactoryPostProcessor(
        factory -> {
          factory.registerSingleton("logSearchWireClient", client);
          factory.registerSingleton("apiSessionInvalidHandler", invalid);
        });
  }

  @Test
  void log093SuccessAndIndependentWire() throws Exception {
    try (var f = new Fixture()) {
      for (String code : List.of("0000", "0200"))
        for (int count : new int[] {0, 1, 100}) {
          f.code = code;
          f.count = count;
          f.total = count;
          var query =
              params(
                  "q",
                  " e\u0301 ",
                  "log_type",
                  "REQUEST",
                  "action",
                  " search ",
                  "path",
                  " /search ",
                  "level",
                  "WARN",
                  "from",
                  "2026-09-20T09:00",
                  "to",
                  "2026-09-20T10:00",
                  "page",
                  "1");
          var model = new ExtendedModelMap();
          var response = new MockHttpServletResponse();
          int before = f.requests.size();
          assertEquals(
              "logs", f.controller.search(query, actor(UserRole.ADMIN), model, raw(), response));
          assertEquals(200, response.getStatus());
          assertEquals(before + 1, f.requests.size());
          var page = assertInstanceOf(LogSearchViewModel.class, model.get("page"));
          assertEquals(count, page.getResults().orElseThrow().getRows().size());
          assertEquals("ADMIN", page.getTopBar().getRole());
          byte[] sent = f.requests.getLast();
          assertEquals(912, sent.length);
          assertEquals("LGSREQ01", ascii(sent, 11, 8));
          assertEquals("a".repeat(64), ascii(sent, 113, 64));
          byte[] expected = new byte[656];
          Arrays.fill(expected, (byte) ' ');
          put(expected, 0, 256, "é");
          put(expected, 256, 16, "REQUEST");
          put(expected, 272, 64, "search");
          put(expected, 336, 256, "/search");
          put(expected, 592, 8, "WARN");
          put(expected, 600, 17, "20260920090000000");
          put(expected, 617, 17, "20260920100000000");
          number(expected, 634, 6, 1);
          number(expected, 640, 3, 100);
          assertArrayEquals(expected, Arrays.copyOfRange(sent, 256, 912));
          f.erased();
        }
    }
  }

  @Test
  void log094InvalidInputNeverSends() throws Exception {
    try (var f = new Fixture()) {
      for (var query :
          List.of(
              params("unknown", "x"),
              params("q", "a", "q", "b"),
              params("q", "あ".repeat(86)),
              params("action", "x".repeat(65)),
              params("path", "x".repeat(257)),
              params("level", "DEBUG"),
              params("log_type", "unknown"),
              params("from", "2026-02-30T00:00"),
              params("from", "2026-01-01T00:00", "to", "2026-02-02T00:00"),
              params("page", "+1"),
              params("q", "\n"))) {
        var model = new ExtendedModelMap();
        var response = new MockHttpServletResponse();
        assertEquals(
            "logs", f.controller.search(query, actor(UserRole.ADMIN), model, raw(), response));
        assertEquals(400, response.getStatus());
        var page = assertInstanceOf(LogSearchViewModel.class, model.get("page"));
        assertTrue(page.getResults().isEmpty());
        assertFalse(page.getErrors().isEmpty());
        assertTrue(f.requests.isEmpty());
      }
    }
  }

  @Test
  void log095AllResultErrors() throws Exception {
    String[] codes = {"0100", "0101", "0103", "0104", "0105", "0106", "0107", "9000", "9001"};
    int[] status = {400, 401, 403, 404, 409, 429, 409, 503, 503};
    try (var f = new Fixture()) {
      for (int i = 0; i < codes.length; i++) {
        f.code = codes[i];
        var model = new ExtendedModelMap();
        var response = new MockHttpServletResponse();
        assertNull(f.controller.search(params(), actor(UserRole.ADMIN), model, raw(), response));
        assertEquals(status[i], response.getStatus());
        assertTrue(model.isEmpty());
        f.erased();
      }
    }
  }

  @Test
  void log096SessionInvalidIsTerminal() throws Exception {
    try (var f = new Fixture()) {
      f.code = "0102";
      var request = f.security.mock("GET", "/logs");
      var response = new MockHttpServletResponse();
      SecurityContextHolder.getContext()
          .setAuthentication(
              UsernamePasswordAuthenticationToken.authenticated(
                  actor(UserRole.ADMIN), null, List.of(new SimpleGrantedAuthority("ROLE_ADMIN"))));
      assertNull(
          f.controller.search(
              params(), actor(UserRole.ADMIN), new ExtendedModelMap(), request, response));
      assertEquals(302, response.getStatus());
      assertEquals("/login?session-expired", response.getRedirectedUrl());
      assertNull(SecurityContextHolder.getContext().getAuthentication());
      assertNull(request.getSession(false));
      assertEquals(1, f.requests.size());
      f.erased();
    }
  }

  @Test
  void log097MalformedTransportAndProjection() throws Exception {
    try (var f = new Fixture()) {
      f.responder = (id, b) -> new byte[4];
      var result = new MockHttpServletResponse();
      assertNull(
          f.controller.search(
              params(), actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), result));
      assertEquals(503, result.getStatus());
      f.responder =
          (id, b) -> {
            throw new JMSRuntimeException("synthetic private");
          };
      result = new MockHttpServletResponse();
      assertNull(
          f.controller.search(
              params(), actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), result));
      assertEquals(503, result.getStatus());
      f.responder = f::standard;
      f.count = 1;
      f.total = 101;
      result = new MockHttpServletResponse();
      assertNull(
          f.controller.search(
              params(), actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), result));
      assertEquals(503, result.getStatus());
      // A byte-valid reply may still name another request page; this is a view-binding failure.
      f.responder =
          (id, bytes) ->
              response(id, ascii(bytes, 113, 64), "0000", 2, 1, 101, "public synthetic log");
      result = new MockHttpServletResponse();
      assertNull(
          f.controller.search(
              params(), actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), result));
      assertEquals(503, result.getStatus());
      f.erased();
    }
  }

  @Test
  void log098NullRoleAndUnknownFailure() throws Exception {
    try (var f = new Fixture()) {
      assertThrows(NullPointerException.class, () -> new LogController(null, f.security.handler));
      assertThrows(NullPointerException.class, () -> new LogController(f.client, null));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.search(
                  null,
                  actor(UserRole.ADMIN),
                  new ExtendedModelMap(),
                  raw(),
                  new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.search(
                  params(), null, new ExtendedModelMap(), raw(), new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.search(
                  params(), actor(UserRole.ADMIN), null, raw(), new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.search(
                  params(),
                  actor(UserRole.ADMIN),
                  new ExtendedModelMap(),
                  null,
                  new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.search(
                  params(), actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), null));
      assertThrows(
          SessionStoreException.class,
          () ->
              f.controller.search(
                  params(),
                  () -> "foreign",
                  new ExtendedModelMap(),
                  raw(),
                  new MockHttpServletResponse()));
      var denied = new MockHttpServletResponse();
      assertNull(
          f.controller.search(
              params(), actor(UserRole.USER), new ExtendedModelMap(), raw(), denied));
      assertEquals(403, denied.getStatus());
      assertTrue(f.requests.isEmpty());
      AssertionError failure = new AssertionError("synthetic unknown fault");
      f.responder =
          (id, b) -> {
            throw failure;
          };
      assertSame(
          failure,
          assertThrows(
              AssertionError.class,
              () ->
                  f.controller.search(
                      params(),
                      actor(UserRole.ADMIN),
                      new ExtendedModelMap(),
                      raw(),
                      new MockHttpServletResponse())));
      f.responder = f::standard;
      f.code = "9000";
      var io = new IOException("synthetic response failure");
      var broken =
          new MockHttpServletResponse() {
            @Override
            public void sendError(int status) throws IOException {
              throw io;
            }
          };
      assertSame(
          io,
          assertThrows(
              IOException.class,
              () ->
                  f.controller.search(
                      params(), actor(UserRole.ADMIN), new ExtendedModelMap(), raw(), broken)));
      f.erased();
    }
  }

  @Test
  void log099MvcRoutesAndBinding() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      var principal = actor(UserRole.ADMIN);
      var get = mvc.perform(pageRequest(principal)).andReturn();
      assertEquals(200, get.getResponse().getStatus());
      assertEquals("Logs", Jsoup.parse(get.getResponse().getContentAsString()).title());
      assertEquals("logs", Objects.requireNonNull(get.getModelAndView()).getViewName());
      int before = f.requests.size();
      var head =
          mvc.perform(
                  head("/logs").principal(principal).requestAttr(CsrfToken.class.getName(), csrf()))
              .andReturn();
      assertEquals(200, head.getResponse().getStatus());
      assertEquals("logs", Objects.requireNonNull(head.getModelAndView()).getViewName());
      assertEquals(before + 1, f.requests.size());
      before = f.requests.size();
      assertEquals(
          405,
          mvc.perform(post("/logs").principal(principal)).andReturn().getResponse().getStatus());
      for (var bad :
          List.of(
              pageRequest(principal).param("q", "a", "b"),
              pageRequest(principal).param("unknown", "secret"))) {
        var response = mvc.perform(bad).andReturn().getResponse();
        assertEquals(400, response.getStatus());
        var dom = Jsoup.parse(response.getContentAsString());
        assertFalse(dom.select("#log-errors li").isEmpty());
        assertTrue(dom.select(".log-row,.count").isEmpty());
      }
      assertEquals(before, f.requests.size());
      f.erased();
    }
  }

  @Test
  void log100RealHttpAuthorizationAndSession() throws Exception {
    for (String role : List.of("USER", "ADMIN")) {
      reset();
      var api = new SessionFormLoginTest.Api("0000", role, "0000", 0);
      try (var f = new Fixture();
          var server =
              new EmbeddedWebSecurityTest.Server(
                  Files.createTempDirectory(root, "log-http-"),
                  false,
                  db,
                  Optional.of(api.provider),
                  true,
                  true,
                  (mvc, invalid) -> configure(mvc, f.client, invalid))) {
        var anonymous = server.send("GET", "/logs", null, null, true);
        assertEquals(302, anonymous.statusCode());
        assertEquals("/login", anonymous.headers().firstValue("location").orElseThrow());
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
        var page = server.send("GET", "/logs?q=hello", cookie, null, true);
        assertEquals(role.equals("ADMIN") ? 200 : 403, page.statusCode());
        if (role.equals("ADMIN")) {
          var dom = Jsoup.parse(page.body());
          assertEquals("ADMIN", dom.select(".login-role").text());
          assertEquals("hello", dom.select("input[name=q]").attr("value"));
          assertEquals(
              List.of("/js/log-search-validation.js"), dom.select("script[src]").eachAttr("src"));
          assertEquals(1, dom.select("input[name=_csrf]").size());
          assertEquals(1, f.requests.size());
          assertTrue(page.headers().firstValue("cache-control").orElseThrow().contains("no-store"));
          int before = f.requests.size();
          var head = server.send("HEAD", "/logs", cookie, null, true);
          assertEquals(200, head.statusCode());
          assertEquals("", head.body());
          assertEquals(before + 1, f.requests.size());
          assertEquals(400, server.send("GET", "/logs?page=bad", cookie, null, true).statusCode());
          assertEquals(before + 1, f.requests.size());
          f.code = "0102";
          var expired = server.send("GET", "/logs", cookie, null, true);
          assertEquals(302, expired.statusCode());
          assertEquals(
              "/login?session-expired", expired.headers().firstValue("location").orElseThrow());
          assertTrue(
              expired.headers().firstValue("set-cookie").orElseThrow().contains("Max-Age=0"));
          assertEquals(302, server.send("GET", "/logs", cookie, null, true).statusCode());
          assertEquals(before + 2, f.requests.size());
        } else {
          assertTrue(f.requests.isEmpty());
        }
        f.erased();
        api.erased();
      }
    }
  }

  @Test
  void log101ConcurrentAdminContexts() throws Exception {
    try (var f = new Fixture();
        var pool = Executors.newFixedThreadPool(8)) {
      var jobs = new ArrayList<Future<?>>();
      for (int i = 0; i < 64; i++) {
        final int n = i;
        jobs.add(
            pool.submit(
                () -> {
                  var principal =
                      new SessionPrincipal(
                          "reader" + n,
                          UserRole.ADMIN,
                          AuthenticationContext.of(String.format(Locale.ROOT, "%064x", n + 1)),
                          actor(UserRole.ADMIN).loginAt());
                  var model = new ExtendedModelMap();
                  var response = new MockHttpServletResponse();
                  assertEquals(
                      "logs",
                      f.controller.search(
                          params("q", "query" + n), principal, model, raw(), response));
                  var page = (LogSearchViewModel) model.get("page");
                  assertEquals("reader" + n, page.getTopBar().getUsername());
                  assertEquals("query" + n, page.getFilters().getQ());
                  return null;
                }));
      }
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      assertEquals(64, f.requests.size());
      for (int i = 0; i < 64; i++) {
        String context = String.format(Locale.ROOT, "%064x", i + 1);
        var matching = f.requests.stream().filter(b -> ascii(b, 113, 64).equals(context)).toList();
        assertEquals(1, matching.size());
        assertEquals(
            "query" + i,
            new String(matching.getFirst(), 256, 256, StandardCharsets.UTF_8).stripTrailing());
      }
      f.erased();
    }
  }

  @Test
  void log102EscapingEmptyAndPagination() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      f.count = 0;
      f.total = 0;
      var empty =
          Jsoup.parse(
              mvc.perform(pageRequest(actor(UserRole.ADMIN)))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals("該当するデータはありません", empty.select(".empty-results").text());
      assertTrue(empty.select(".log-row,.pagination").isEmpty());
      f.count = 1;
      f.total = 101;
      f.message = "<img src=x onerror=alert(1)>";
      var page =
          Jsoup.parse(
              mvc.perform(pageRequest(actor(UserRole.ADMIN)).param("page", "2"))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals(f.message, page.select(".log-row > p").text());
      assertTrue(page.select("img,[onerror],script:not([src])").isEmpty());
      assertEquals(
          "/logs?q=&log_type=&action=&path=&level=&from=&to=&page=1",
          page.select(".pagination a").first().attr("href"));
      assertEquals("101 logs / page 2 of 2", page.select(".count").text());
      f.erased();
    }
  }

  @Test
  void log103PublicScriptIsReadOnly() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      var script = mvc.perform(get("/js/log-search-validation.js")).andReturn().getResponse();
      assertEquals(200, script.getStatus());
      assertEquals("text/javascript", script.getContentType());
      assertEquals(
          Files.readString(Path.of("src/main/resources/static/js/log-search-validation.js")),
          script.getContentAsString(StandardCharsets.UTF_8));
      var head = mvc.perform(head("/js/log-search-validation.js")).andReturn().getResponse();
      assertEquals(200, head.getStatus());
      assertEquals(0, head.getContentAsByteArray().length);
      assertEquals(404, mvc.perform(get("/js/missing.js")).andReturn().getResponse().getStatus());
      assertTrue(f.requests.isEmpty());
    }
  }

  private static final class Fixture implements AutoCloseable {
    final ApiSessionInvalidTest.Harness security = new ApiSessionInvalidTest.Harness(db);
    final AtomicLong ids = new AtomicLong();
    final List<byte[]> requests = new CopyOnWriteArrayList<>();
    final List<byte[]> buffers = new CopyOnWriteArrayList<>();
    final JmsRequestReplyClient wire =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    volatile int count = 1;
    volatile int total = 1;
    volatile String code = "0000";
    volatile String message = "public synthetic log";
    volatile BiFunction<UUID, byte[], byte[]> responder = this::standard;
    final LogSearchWireClient client =
        new LogSearchWireClient(
            wire,
            (id, bytes) -> {
              requests.add(bytes.clone());
              buffers.add(bytes);
              assertTrue(wire.onReply(id, responder.apply(id, bytes)));
            },
            CLOCK,
            () -> new UUID(0, ids.incrementAndGet()),
            Duration.ofSeconds(1));
    final LogController controller = new LogController(client, security.handler);

    AnnotationConfigWebApplicationContext mvc() {
      var context = new AnnotationConfigWebApplicationContext();
      context.setServletContext(new MockServletContext());
      configure(context, client, security.handler);
      context.refresh();
      return context;
    }

    byte[] standard(UUID id, byte[] request) {
      int page = Integer.parseInt(ascii(request, 890, 6));
      return response(id, ascii(request, 113, 64), code, page, count, total, message);
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

  // Independent UI232/235 fixed positions. Production encoder/decoder is never an oracle.
  private static byte[] response(
      UUID id, String context, String code, int page, int rows, int total, String message) {
    boolean success = code.equals("0000") || code.equals("0200");
    int count = success ? rows : 0;
    byte[] bytes = new byte[304 + 2088 * count];
    Arrays.fill(bytes, (byte) ' ');
    put(bytes, 0, 8, "SCHBNK01");
    put(bytes, 8, 3, "001");
    put(bytes, 11, 8, "LGSRSP01");
    put(bytes, 19, 3, "001");
    put(bytes, 22, 1, "S");
    put(bytes, 23, 1, "S");
    put(bytes, 24, 36, new UUID(1, id.getLeastSignificantBits()).toString());
    put(bytes, 60, 36, id.toString());
    put(bytes, 96, 17, "20260920090000000");
    put(bytes, 113, 64, context);
    number(bytes, 177, 4, 256);
    number(bytes, 181, 6, 48);
    number(bytes, 187, 6, 2088);
    number(bytes, 193, 6, count);
    number(bytes, 199, 9, bytes.length);
    put(bytes, 208, 4, code);
    number(bytes, 256, 6, success ? page : 0);
    number(bytes, 262, 3, success ? 100 : 0);
    number(bytes, 265, 9, success ? total : 0);
    number(bytes, 274, 6, success ? Math.max(1, (total + 99) / 100) : 0);
    number(bytes, 280, 9, count == 0 ? 0 : (page - 1L) * 100 + 1);
    number(bytes, 289, 9, count == 0 ? 0 : (page - 1L) * 100 + count);
    for (int i = 0; i < count; i++) {
      int at = 304 + i * 2088;
      number(bytes, at, 12, 100 - i);
      put(bytes, at + 12, 17, "20260920100203004");
      put(bytes, at + 29, 16, "REQUEST");
      put(bytes, at + 45, 8, "INFO");
      put(bytes, at + 117, 512, message);
      put(bytes, at + 53, 64, "search");
      put(bytes, at + 737, 8, "GET");
      put(bytes, at + 745, 256, "/search");
      put(bytes, at + 1001, 3, "200");
      put(bytes, at + 1004, 9, "123");
      put(bytes, at + 1013, 45, "127.0.0.1");
      put(bytes, at + 1058, 1024, "{}");
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
