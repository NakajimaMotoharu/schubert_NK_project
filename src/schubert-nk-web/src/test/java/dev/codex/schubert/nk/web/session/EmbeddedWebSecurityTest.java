package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.security.CaddyClientAddressResolver;
import dev.codex.schubert.nk.web.security.CaddyTransportContextFilter;
import dev.codex.schubert.nk.web.security.EncryptedSessionCsrfTokenRepository;
import dev.codex.schubert.nk.web.security.EncryptedSessionSecurityContextRepository;
import dev.codex.schubert.nk.web.security.LoginFormAuthenticationConverter;
import dev.codex.schubert.nk.web.security.LoginFormRejectedException;
import dev.codex.schubert.nk.web.security.MqAuthenticationProvider;
import dev.codex.schubert.nk.web.security.WebCsrfDeniedHandler;
import dev.codex.schubert.nk.web.security.WebCsrfFilterFactory;
import dev.codex.schubert.nk.web.security.WebRequestContext;
import dev.codex.schubert.nk.web.security.WebSecurityFilterFactory;
import dev.codex.schubert.nk.web.security.WebSecurityHeaderFilterFactory;
import dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest.Fixture;
import jakarta.servlet.Filter;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.ResourceBundle;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.catalina.Context;
import org.apache.catalina.core.StandardHost;
import org.apache.catalina.startup.Tomcat;
import org.apache.tomcat.util.descriptor.web.ErrorPage;
import org.apache.tomcat.util.descriptor.web.FilterDef;
import org.apache.tomcat.util.descriptor.web.FilterMap;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.web.context.SecurityContextHolderFilter;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.web.filter.CharacterEncodingFilter;

/**
 * Real loopback Servlet/PG boundary PT, not full MVC/production startup/IT/ST.
 * NK-WEB-001/PT-WEB-109..112; UI222/226/252; SS311/313/314/342/351/352; PG-D-109.
 */
class EmbeddedWebSecurityTest {
  private static WebLogDatabaseFixture db;

  @BeforeAll
  static void startDatabase(@TempDir Path root) throws Exception {
    db = new WebLogDatabaseFixture(root);
  }

  @AfterAll
  static void stopDatabase() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = db.web();
        var s = c.createStatement()) {
      s.executeUpdate("delete from schubert_web_session.web_http_sessions");
    }
  }

  @Test
  void web109RealHttpSessionCsrfAndHeadersMatchContract(@TempDir Path root) throws Exception {
    assertEquals(
        1,
        Collections.list(
                HttpServletRequest.class
                    .getClassLoader()
                    .getResources("jakarta/servlet/http/HttpServletRequest.class"))
            .size());
    try (var server = new Server(root)) {
      var get = server.send("GET", "/fixture", null, null, true);
      assertEquals(200, get.statusCode());
      assertTrue(get.body().startsWith("TOKEN:"));
      String token = get.body().substring(6);
      assertEquals("02".repeat(32), token);
      assertHeaders(get);
      String setCookie = get.headers().firstValue("set-cookie").orElseThrow();
      assertTrue(setCookie.startsWith("SCHUBERT_NK_SESSION="));
      assertTrue(setCookie.contains("Path=/"));
      assertTrue(setCookie.contains("Secure"));
      assertTrue(setCookie.contains("HttpOnly"));
      assertTrue(setCookie.contains("SameSite=Lax"));
      assertFalse(setCookie.contains("Domain="));
      assertFalse(setCookie.contains("JSESSIONID"));
      String cookie = setCookie.split(";", 2)[0];
      var ok = server.send("POST", "/fixture", cookie, "_csrf=" + token, true);
      assertEquals(200, ok.statusCode());
      assertEquals("ok", ok.body());
      assertHeaders(ok);
      var denied = server.send("POST", "/fixture", cookie, "_csrf=" + "ff".repeat(32), true);
      assertEquals(403, denied.statusCode());
      assertEquals("error:403", denied.body());
      assertHeaders(denied);
      assertEquals(0, server.context.getManager().getActiveSessions());
      assertEquals(1, rowCount());
      assertEquals(1, server.log.events.size());
      assertEquals(1, server.errorCalls.get());
      assertEquals(1, server.posts.get());
      for (var response : List.of(get, ok, denied))
        assertFalse(response.headers().map().toString().contains("JSESSIONID"));
    }
  }

  @Test
  void web110RealErrorDispatchIsBoundedAndRedacted(@TempDir Path root) throws Exception {
    try (var server = new Server(root)) {
      var proxy = server.send("GET", "/fixture", null, null, false);
      assertEquals(403, proxy.statusCode());
      // Untrusted transport must not enter session/error application or duplicate security audit.
      assertEquals("", proxy.body());
      assertEquals(0, server.errorCalls.get());
      assertEquals(1, server.log.events.size());
      assertEquals(1, server.ids.get());
      assertEquals(0, rowCount());
      assertHeaders(proxy);
      var get = server.send("GET", "/fixture", null, null, true);
      String cookie = get.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
      var denied = server.send("POST", "/fixture", cookie, "_csrf=private-invalid-value", true);
      assertEquals(403, denied.statusCode());
      assertEquals("error:403", denied.body());
      assertEquals(1, server.errorCalls.get());
      assertEquals(3, server.ids.get());
      assertEquals(2, server.log.events.size());
      assertEquals(
          server.log.events.getLast().get("requestId").getAsString(),
          server.errorIds.getLast().toString());
      assertFalse(denied.body().contains("private"));
      assertFalse(denied.body().contains("Tomcat"));
      assertFalse(denied.body().contains("Exception"));
    }
  }

  @Test
  void web111RealFormParameterMergingRejectsUnknownAndQueryCredentials(@TempDir Path root)
      throws Exception {
    try (var server = new Server(root)) {
      var get = server.send("GET", "/fixture", null, null, true);
      String token = get.body().substring(6);
      String cookie = get.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
      String body = "_csrf=" + token + "&username=reader&password=synthetic-password";
      for (String query :
          List.of(
              "?role=ADMIN",
              "?q=unknown",
              "?username=other",
              "?%75sername=other",
              "?password=other")) {
        var rejected = server.send("POST", "/login" + query, cookie, body, true);
        assertEquals(400, rejected.statusCode(), query);
        assertEquals(0, server.converted.get());
        assertFalse(rejected.body().contains("password"));
      }
      for (String suffix :
          List.of("&role=ADMIN", "&username=other", "&Password=other", "&=unknown")) {
        assertEquals(400, server.send("POST", "/login", cookie, body + suffix, true).statusCode());
        assertEquals(0, server.converted.get());
      }
      var queryCsrf = server.send("POST", "/login?%5fcsrf=" + token, cookie, body, true);
      assertEquals(403, queryCsrf.statusCode());
      assertEquals(0, server.converted.get());
      var valid = server.send("POST", "/login", cookie, body, true);
      assertEquals(204, valid.statusCode());
      assertEquals(1, server.converted.get());
      assertEquals(0, server.context.getManager().getActiveSessions());
    }
  }

  @Test
  void web112ConcurrentRealHttpRequestsKeepCookiesAndAuditSeparate(@TempDir Path root)
      throws Exception {
    try (var server = new Server(root, true);
        var pool = Executors.newFixedThreadPool(8)) {
      // Production SecureRandom avoids the deterministic byte fixture wrapping after256
      // allocations.
      var cookies = ConcurrentHashMap.<String>newKeySet();
      var tokens = ConcurrentHashMap.<String>newKeySet();
      var jobs = new ArrayList<Callable<Void>>();
      for (int i = 0; i < 100; i++) {
        jobs.add(
            () -> {
              var get = server.send("GET", "/fixture", null, null, true);
              assertEquals(200, get.statusCode());
              String token = get.body().substring(6);
              String cookie = get.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
              assertTrue(cookies.add(cookie));
              assertTrue(tokens.add(token));
              assertEquals(
                  200,
                  server.send("POST", "/fixture", cookie, "_csrf=" + token, true).statusCode());
              var denied = server.send("POST", "/fixture", cookie, "_csrf=wrong", true);
              assertEquals(403, denied.statusCode());
              assertHeaders(denied);
              return null;
            });
      }
      for (var result : pool.invokeAll(jobs)) result.get(30, TimeUnit.SECONDS);
      assertEquals(100, cookies.size());
      assertEquals(100, tokens.size());
      assertEquals(100, server.posts.get());
      assertEquals(100, server.errorCalls.get());
      assertEquals(100, server.log.events.size());
      assertEquals(300, server.ids.get());
      assertEquals(100, rowCount());
      assertEquals(0, server.context.getManager().getActiveSessions());
      Set<String> auditIds = new HashSet<>();
      for (var event : server.log.events)
        assertTrue(auditIds.add(event.get("requestId").getAsString()));
      assertEquals(auditIds, new HashSet<>(server.errorIds.stream().map(UUID::toString).toList()));
    }
  }

  private static void assertHeaders(HttpResponse<String> response) {
    Map<String, String> expected =
        Map.of(
            "cache-control",
            "no-store",
            "x-frame-options",
            "DENY",
            "x-content-type-options",
            "nosniff",
            "referrer-policy",
            "same-origin",
            "strict-transport-security",
            "max-age=31536000",
            "permissions-policy",
            "camera=(), microphone=(), geolocation=(), payment=()",
            "content-security-policy",
            "default-src 'self'; style-src 'self'; img-src 'self' data:; media-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'");
    expected.forEach(
        (name, value) -> assertEquals(List.of(value), response.headers().allValues(name), name));
    assertTrue(response.headers().allValues("x-request-id").isEmpty());
  }

  private static long rowCount() throws Exception {
    try (var c = db.web();
        var s = c.createStatement();
        var rows = s.executeQuery("select count(*) from schubert_web_session.web_http_sessions")) {
      assertTrue(rows.next());
      return rows.getLong(1);
    }
  }

  static final class Server implements AutoCloseable {
    final Tomcat tomcat = new Tomcat();
    final Fixture f;
    final Context context;
    final Log log = new Log();
    final AtomicInteger ids = new AtomicInteger();
    final AtomicInteger errorCalls = new AtomicInteger();
    final AtomicInteger posts = new AtomicInteger();
    final AtomicInteger converted = new AtomicInteger();
    volatile boolean breakDatabaseBeforeError;
    volatile String invalidationFailure = "";
    final List<UUID> errorIds = new CopyOnWriteArrayList<>();
    final HttpClient client =
        HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(2))
            .followRedirects(HttpClient.Redirect.NEVER)
            .build();
    final URI base;

    Server(Path root) throws Exception {
      this(root, false);
    }

    Server(Path root, boolean secureRandom) throws Exception {
      this(root, secureRandom, db, Optional.empty());
    }

    Server(
        Path root,
        boolean secureRandom,
        WebLogDatabaseFixture database,
        Optional<MqAuthenticationProvider> provider)
        throws Exception {
      this(root, secureRandom, database, provider, false);
    }

    Server(
        Path root,
        boolean secureRandom,
        WebLogDatabaseFixture database,
        Optional<MqAuthenticationProvider> provider,
        boolean menuMvc)
        throws Exception {
      this(root, secureRandom, database, provider, menuMvc, false);
    }

    Server(
        Path root,
        boolean secureRandom,
        WebLogDatabaseFixture database,
        Optional<MqAuthenticationProvider> provider,
        boolean menuMvc,
        boolean errorMvc)
        throws Exception {
      this(root, secureRandom, database, provider, menuMvc, errorMvc, (mvc, invalid) -> {});
    }

    Server(
        Path root,
        boolean secureRandom,
        WebLogDatabaseFixture database,
        Optional<MqAuthenticationProvider> provider,
        boolean menuMvc,
        boolean errorMvc,
        java.util.function.BiConsumer<
                org.springframework.web.context.support.AnnotationConfigWebApplicationContext,
                ApiSessionInvalidHandler>
            mvcSetup)
        throws Exception {
      this(
          root,
          secureRandom,
          database,
          provider,
          menuMvc,
          errorMvc,
          mvcSetup,
          (mvc, repository) -> {});
    }

    /** Independent full-MVC tests must borrow the exact core used by the security filter. */
    Server(
        Path root,
        boolean secureRandom,
        WebLogDatabaseFixture database,
        Optional<MqAuthenticationProvider> provider,
        boolean menuMvc,
        boolean errorMvc,
        java.util.function.BiConsumer<
                org.springframework.web.context.support.AnnotationConfigWebApplicationContext,
                ApiSessionInvalidHandler>
            mvcSetup,
        java.util.function.BiConsumer<
                org.springframework.web.context.support.AnnotationConfigWebApplicationContext,
                EncryptedWebSessionRepository>
            coreSetup)
        throws Exception {
      Objects.requireNonNull(mvcSetup);
      Objects.requireNonNull(coreSetup);
      assertFalse(errorMvc && !menuMvc);
      f = new Fixture(Objects.requireNonNull(database));
      f.clock.value = Instant.now();
      tomcat.setBaseDir(root.toString());
      tomcat.setPort(0);
      tomcat.setSilent(true);
      tomcat.setAddDefaultWebXmlToWebapp(false);
      ((StandardHost) tomcat.getHost()).setErrorReportValveClass(null);
      context = tomcat.addContext("", root.toString());
      context.setParentClassLoader(getClass().getClassLoader());
      assertTrue(tomcat.getConnector().setProperty("address", "127.0.0.1"));
      assertTrue(tomcat.getConnector().setProperty("maxThreads", "16"));
      var audit = new WebSecurityAudit(log, f.clock, "pt", "pt");
      // Fixture01 has deterministic vectors; the100-session test explicitly selects secure random
      // below.
      var repository =
          secureRandom
              ? new EncryptedWebSessionRepository(
                  f.source, f.codec, f.clock, new java.security.SecureRandom(), UUID::randomUUID)
              : f.repository;
      var adapter = new SpringEncryptedSessionRepository(repository, f.clock);
      List<Filter> filters;
      if (provider.isPresent()) {
        filters =
            List.of(
                new WebSecurityFilterFactory()
                    .create(
                        adapter,
                        provider.orElseThrow(),
                        audit,
                        () -> new UUID(0, ids.incrementAndGet())));
      } else {
        filters =
            List.of(
                new WebSecurityHeaderFilterFactory().create(),
                new CaddyTransportContextFilter(
                    () -> new UUID(0, ids.incrementAndGet()),
                    new CaddyClientAddressResolver(),
                    audit),
                new CharacterEncodingFilter("UTF-8", true, false),
                new WebSessionFilterFactory().create(adapter),
                new SecurityContextHolderFilter(
                    new EncryptedSessionSecurityContextRepository(adapter)),
                new WebCsrfFilterFactory()
                    .create(
                        new EncryptedSessionCsrfTokenRepository(),
                        new WebCsrfDeniedHandler(audit)));
      }
      for (int i = 0; i < filters.size(); i++) {
        var definition = new FilterDef();
        definition.setFilterName("filter" + i);
        definition.setFilter(filters.get(i));
        definition.setAsyncSupported("true");
        context.addFilterDef(definition);
        var mapping = new FilterMap();
        mapping.setFilterName("filter" + i);
        mapping.addURLPattern("/*");
        for (String dispatch : List.of("REQUEST", "ERROR", "ASYNC", "FORWARD"))
          mapping.setDispatcher(dispatch);
        context.addFilterMap(mapping);
      }
      Tomcat.addServlet(
              context,
              "fixture",
              new HttpServlet() {
                @Override
                protected void doGet(HttpServletRequest request, HttpServletResponse response)
                    throws IOException, ServletException {
                  if (request.getRequestURI().equals("/fixture-error")) {
                    if (breakDatabaseBeforeError) f.failure = "open";
                    int status = Integer.parseInt(request.getParameter("status"));
                    if (status == 500) throw new ServletException("private-exception-canary");
                    response.sendError(status, "private-message-canary");
                    return;
                  }
                  if (request.getRequestURI().equals("/fixture-principal")) {
                    var principal = request.getUserPrincipal();
                    response.setContentType("text/plain;charset=UTF-8");
                    response
                        .getWriter()
                        .write(principal == null ? "ANONYMOUS" : principal.getName());
                    return;
                  }
                  if (request.getRequestURI().equals("/fixture-programmatic")) {
                    var principal = request.getUserPrincipal();
                    var session = request.getSession(false);
                    assertNotNull(session);
                    var csrf = session.getAttribute("csrfToken");
                    for (ServletException denied :
                        List.of(
                            assertThrows(
                                ServletException.class, () -> request.authenticate(response)),
                            assertThrows(
                                ServletException.class,
                                () ->
                                    request.login(
                                        "private-user-canary", "private-password-canary")),
                            assertThrows(ServletException.class, request::logout))) {
                      assertEquals(
                          "programmatic authentication is prohibited", denied.getMessage());
                      assertNull(denied.getCause());
                    }
                    assertSame(principal, request.getUserPrincipal());
                    assertSame(session, request.getSession(false));
                    assertEquals(csrf, session.getAttribute("csrfToken"));
                    response.setContentType("text/plain;charset=UTF-8");
                    response
                        .getWriter()
                        .write(
                            request.getRemoteUser()
                                + ":"
                                + request.getAuthType()
                                + ":"
                                + request.isUserInRole("USER")
                                + ":"
                                + request.isUserInRole("ADMIN")
                                + ":"
                                + request.isUserInRole("ROLE_USER")
                                + ":"
                                + request.isUserInRole("ROLE_ADMIN")
                                + ":"
                                + request.isUserInRole(null));
                    return;
                  }
                  var token = (CsrfToken) request.getAttribute("_csrf");
                  response.setContentType("text/plain;charset=UTF-8");
                  response.getWriter().write("TOKEN:" + token.getToken());
                }

                @Override
                protected void doPost(HttpServletRequest request, HttpServletResponse response)
                    throws IOException {
                  if (request.getRequestURI().equals("/login")) {
                    try {
                      var auth =
                          (UsernamePasswordAuthenticationToken)
                              new LoginFormAuthenticationConverter(new CaddyClientAddressResolver())
                                  .convert(request);
                      Arrays.fill((char[]) auth.getCredentials(), '\0');
                      auth.eraseCredentials();
                      converted.incrementAndGet();
                      response.setStatus(204);
                    } catch (LoginFormRejectedException rejected) {
                      response.setStatus(400);
                    }
                  } else {
                    posts.incrementAndGet();
                    response.getWriter().write("ok");
                  }
                }
              })
          .setAsyncSupported(true);
      context.addServletMapping(menuMvc ? "/login" : "/*", "fixture");
      if (errorMvc) context.addServletMapping("/fixture-error", "fixture");
      if (errorMvc) {
        var invalid = new ApiSessionInvalidHandler(adapter, audit);
        Tomcat.addServlet(
            context,
            "expired-fixture",
            new HttpServlet() {
              @Override
              protected void service(HttpServletRequest request, HttpServletResponse response)
                  throws IOException {
                // Trusted API0102 component double, never an HTTP result-code parameter.
                f.failure = invalidationFailure;
                invalid.handle(request, response);
              }
            });
        for (String path :
            List.of(
                "/fixture-expired",
                "/audio/pt-expired",
                "/animation/media/pt-expired",
                "/music/media/pt-expired",
                "/music/download/pt-expired")) context.addServletMapping(path, "expired-fixture");
      }
      if (menuMvc) {
        var mvc =
            new org.springframework.web.context.support.AnnotationConfigWebApplicationContext();
        mvc.register(dev.codex.schubert.nk.web.config.WebMvcConfiguration.class);
        coreSetup.accept(mvc, repository);
        mvcSetup.accept(mvc, new ApiSessionInvalidHandler(adapter, audit));
        var dispatcher = new org.springframework.web.servlet.DispatcherServlet(mvc);
        var wrapper = Tomcat.addServlet(context, "mvc", dispatcher);
        wrapper.setLoadOnStartup(1);
        wrapper.setAsyncSupported(true);
        // Menu/assets use real MVC; Login and error are explicit test fixtures, not production
        // views.
        context.addServletMapping("/", "mvc");
      }
      if (!errorMvc) {
        Tomcat.addServlet(
                context,
                "error",
                new HttpServlet() {
                  @Override
                  protected void service(HttpServletRequest request, HttpServletResponse response)
                      throws IOException {
                    errorCalls.incrementAndGet();
                    errorIds.add(WebRequestContext.require(request).requestId());
                    response.setContentType("text/plain;charset=UTF-8");
                    response.getWriter().write("error:" + response.getStatus());
                  }
                })
            .setAsyncSupported(true);
        context.addServletMapping("/error", "error");
      }
      for (int status :
          errorMvc
              ? new int[] {400, 401, 403, 404, 405, 409, 416, 429, 500, 503}
              : new int[] {400, 403, 500, 503}) {
        var page = new ErrorPage();
        page.setErrorCode(status);
        page.setLocation("/error");
        context.addErrorPage(page);
      }
      tomcat.start();
      base = URI.create("http://127.0.0.1:" + tomcat.getConnector().getLocalPort());
    }

    HttpResponse<String> send(
        String method, String path, String cookie, String body, boolean trusted) throws Exception {
      var request = HttpRequest.newBuilder(base.resolve(path)).timeout(Duration.ofSeconds(5));
      if (trusted)
        request.header("X-Forwarded-For", "203.0.113.1").header("X-Forwarded-Proto", "https");
      if (cookie != null) request.header("Cookie", cookie);
      if (body != null)
        request.header("Content-Type", "application/x-www-form-urlencoded;charset=UTF-8");
      request.method(
          method,
          body == null
              ? HttpRequest.BodyPublishers.noBody()
              : HttpRequest.BodyPublishers.ofString(body, StandardCharsets.UTF_8));
      return client.send(
          request.build(), HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
    }

    @Override
    public void close() throws org.apache.catalina.LifecycleException {
      client.close();
      try {
        tomcat.stop();
      } finally {
        try {
          tomcat.destroy();
        } finally {
          f.close();
        }
      }
      assertFalse(context.getState().isAvailable());
    }
  }

  static final class Log implements Logger {
    final List<JsonObject> events = new CopyOnWriteArrayList<>();

    @Override
    public String getName() {
      return "synthetic.http.security";
    }

    @Override
    public boolean isLoggable(Level level) {
      return true;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Throwable thrown) {
      fail("secret throwable");
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String format, Object... params) {
      assertNull(bundle);
      assertNull(params);
      events.add(JsonParser.parseString(format).getAsJsonObject());
    }
  }
}
