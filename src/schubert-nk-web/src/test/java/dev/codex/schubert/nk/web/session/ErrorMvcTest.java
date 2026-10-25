package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.config.WebMvcConfiguration;
import dev.codex.schubert.nk.web.controller.ErrorController;
import dev.codex.schubert.nk.web.error.ProblemViewFactory;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.security.CaddyClientAddressResolver;
import dev.codex.schubert.nk.web.security.CaddyTransportContextFilter;
import dev.codex.schubert.nk.web.security.InternalErrorDispatchRouter;
import dev.codex.schubert.nk.web.security.WebCsrfDeniedHandler;
import dev.codex.schubert.nk.web.security.WebDisplayContext;
import dev.codex.schubert.nk.web.security.WebDisplayContextFilter;
import dev.codex.schubert.nk.web.security.WebErrorDispatchFilter;
import dev.codex.schubert.nk.web.security.WebInfrastructureFailureFilter;
import dev.codex.schubert.nk.web.security.WebSecurityFilterFactory;
import dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest.Fixture;
import dev.codex.schubert.nk.web.view.ErrorViewModel;
import dev.codex.schubert.nk.web.view.TopBarViewModel;
import jakarta.servlet.DispatcherType;
import jakarta.servlet.Filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.FilterConfig;
import jakarta.servlet.RequestDispatcher;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletRequestWrapper;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.ServletResponseWrapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletRequestWrapper;
import jakarta.servlet.http.HttpSession;
import java.io.IOException;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.Principal;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockFilterConfig;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockServletContext;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;

/**
 * NK-WEB-001/PT-WEB-148..157; UI221/222/226; SS313/314/351/352; SSC-047/PG-D-116; BUG-074/YKT-066.
 */
class ErrorMvcTest {
  private static WebLogDatabaseFixture db;
  @TempDir Path root;
  private static final UUID REQUEST_ID = new UUID(0, 27);
  private static final Map<Integer, String> MESSAGES =
      Map.of(
          400,
          "入力内容を確認してください。",
          401,
          "再度ログインしてください。",
          403,
          "この操作を実行する権限がありません。",
          404,
          "対象が見つかりません。",
          405,
          "この操作方法は利用できません。",
          409,
          "状態が更新されたため操作できません。再表示してください。",
          416,
          "指定された範囲を取得できません。",
          429,
          "しばらく待ってから再操作してください。",
          503,
          "現在処理できません。しばらくしてから再操作してください。");

  @AfterEach
  void clearHolder() {
    SecurityContextHolder.clearContext();
  }

  @BeforeAll
  static void start(@TempDir Path root) throws Exception {
    db = new WebLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @Test
  void web148ErrorCatalogAndModelsAreClosed() {
    var factory = new ProblemViewFactory();
    for (var expected : MESSAGES.entrySet()) {
      for (var top :
          List.of(
              Optional.<TopBarViewModel>empty(),
              Optional.of(TopBarViewModel.from(principal("reader", "USER"))),
              Optional.of(TopBarViewModel.from(principal("administrator", "ADMIN"))))) {
        var page = factory.create(expected.getKey(), REQUEST_ID, top);
        assertEquals(expected.getKey().intValue(), page.getStatus());
        assertEquals(expected.getValue(), page.getMessage());
        assertEquals("00000000-0000-0000-0000-00000000001b", page.getRequestId());
        assertEquals(top, page.getTopBar());
        assertEquals("ErrorViewModel[REDACTED]", page.toString());
      }
    }
    assertEquals(404, factory.create(null, REQUEST_ID, Optional.empty()).getStatus());
    for (Object unknown :
        List.of(
            0,
            200,
            302,
            500,
            999,
            "403",
            403L,
            new Object() {
              @Override
              public String toString() {
                throw new AssertionError("diagnostic read");
              }
            })) {
      var page = factory.create(unknown, REQUEST_ID, Optional.empty());
      assertEquals(503, page.getStatus());
      assertEquals("現在処理できません。しばらくしてから再操作してください。", page.getMessage());
    }
    assertThrows(NullPointerException.class, () -> factory.create(400, null, Optional.empty()));
    assertThrows(NullPointerException.class, () -> factory.create(400, REQUEST_ID, null));
    assertThrows(
        NullPointerException.class, () -> ErrorViewModel.of(null, REQUEST_ID, Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> ErrorViewModel.of(ErrorViewModel.Status.NOT_FOUND, null, Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> ErrorViewModel.of(ErrorViewModel.Status.NOT_FOUND, REQUEST_ID, null));
  }

  @Test
  void web149DisplaySnapshotAndCsrfRemainRequestScoped() throws Exception {
    var display = new WebDisplayContextFilter();
    var errors = new WebErrorDispatchFilter();
    filterNulls(display);
    filterNulls(errors);
    assertThrows(NullPointerException.class, () -> WebDisplayContext.existing(null));
    assertThrows(NullPointerException.class, () -> WebDisplayContext.clear(null));
    var request = request("GET", "/search");
    display.doFilter(request, new MockHttpServletResponse(), (r, s) -> assertSame(request, r));
    assertTrue(WebDisplayContext.existing(request).isEmpty());
    for (String role : List.of("USER", "ADMIN")) {
      request.setUserPrincipal(principal("reader", role));
      request.setAttribute(
          CsrfToken.class.getName(), new DefaultCsrfToken("unused", "_csrf", "b".repeat(64)));
      display.doFilter(request, new MockHttpServletResponse(), (r, s) -> {});
      var snapshot = WebDisplayContext.existing(request).orElseThrow();
      assertEquals("reader", snapshot.topBar().getUsername());
      assertEquals(role, snapshot.topBar().getRole());
      assertEquals("WebDisplayContext[REDACTED]", snapshot.toString());
      request.setUserPrincipal(principal("different", "ADMIN"));
      request.setDispatcherType(DispatcherType.ERROR);
      request.setRequestURI("/error");
      request.setAttribute(CsrfToken.class.getName(), new Object());
      request.setAttribute("_csrf", "secret-placeholder");
      var noNative = noNative(request);
      errors.doFilter(
          noNative,
          new MockHttpServletResponse(),
          (r, s) -> {
            var token = assertInstanceOf(CsrfToken.class, r.getAttribute("_csrf"));
            assertSame(token, r.getAttribute(CsrfToken.class.getName()));
            assertEquals("b".repeat(64), token.getToken());
            assertEquals("_csrf", token.getParameterName());
            assertEquals("X-CSRF-TOKEN", token.getHeaderName());
          });
      assertSame(snapshot, WebDisplayContext.existing(request).orElseThrow());
      WebDisplayContext.clear(noNative);
      assertTrue(WebDisplayContext.existing(noNative).isEmpty());
      assertNull(request.getAttribute("_csrf"));
      assertNull(request.getAttribute(CsrfToken.class.getName()));
      request.setAttribute(CsrfToken.class.getName(), new Object());
      errors.doFilter(
          noNative,
          new MockHttpServletResponse(),
          (r, s) -> assertNull(r.getAttribute(CsrfToken.class.getName())));
    }
    request.setAttribute(WebDisplayContext.class.getName(), "foreign");
    assertThrows(SessionStoreException.class, () -> WebDisplayContext.existing(request));
    WebDisplayContext.clear(request);
    request.setUserPrincipal(
        () -> {
          throw new AssertionError("foreign name read");
        });
    assertThrows(
        SessionStoreException.class,
        () -> display.doFilter(request, new MockHttpServletResponse(), (r, s) -> fail()));
    request.setUserPrincipal(principal("reader", "USER"));
    assertThrows(
        SessionStoreException.class,
        () -> display.doFilter(request, new MockHttpServletResponse(), (r, s) -> fail()));
    for (Object token :
        List.of("foreign", new DefaultCsrfToken("unused", "wrong", "b".repeat(64)))) {
      request.setAttribute(CsrfToken.class.getName(), token);
      assertThrows(
          SessionStoreException.class,
          () -> display.doFilter(request, new MockHttpServletResponse(), (r, s) -> fail()));
    }
    request.setAttribute(
        CsrfToken.class.getName(), new DefaultCsrfToken("unused", "_csrf", "invalid"));
    assertThrows(
        IllegalArgumentException.class,
        () -> display.doFilter(request, new MockHttpServletResponse(), (r, s) -> fail()));
    request.setAttribute(
        CsrfToken.class.getName(),
        new CsrfToken() {
          private static final long serialVersionUID = 1L;

          @Override
          public String getHeaderName() {
            return "unused";
          }

          @Override
          public String getParameterName() {
            return "_csrf";
          }

          @Override
          public String getToken() {
            return null;
          }
        });
    assertThrows(
        NullPointerException.class,
        () -> display.doFilter(request, new MockHttpServletResponse(), (r, s) -> fail()));
    request.setDispatcherType(DispatcherType.REQUEST);
    assertThrows(
        ServletException.class,
        () -> errors.doFilter(request, new MockHttpServletResponse(), (r, s) -> fail()));
    request.setDispatcherType(DispatcherType.ERROR);
    request.setRequestURI("/admin/users");
    assertThrows(
        ServletException.class,
        () -> errors.doFilter(request, new MockHttpServletResponse(), (r, s) -> fail()));
    var denied = new WebCsrfDeniedHandler(audit());
    for (boolean authenticated : List.of(false, true))
      for (boolean tokenPresent : List.of(false, true)) {
        SecurityContextHolder.clearContext();
        if (authenticated) set(principal("reader", "USER"));
        var r = request("POST", "/");
        context(r);
        if (tokenPresent)
          r.setAttribute(
              CsrfToken.class.getName(), new DefaultCsrfToken("unused", "_csrf", "b".repeat(64)));
        denied.handle(r, new MockHttpServletResponse(), new AccessDeniedException("private"));
        assertEquals(authenticated && tokenPresent, WebDisplayContext.existing(r).isPresent());
      }
  }

  @Test
  void web150InfrastructureFailuresDoNotLoopOrHideOtherFaults() throws Exception {
    var filter = new WebInfrastructureFailureFilter();
    filterNulls(filter);
    var request = request("GET", "/");
    var failure = new SessionStoreException();
    FilterChain failing =
        (r, s) -> {
          throw failure;
        };
    var response = new MockHttpServletResponse();
    filter.doFilter(request, response, failing);
    assertEquals(503, response.getStatus());
    assertTrue(response.isCommitted());
    var committed = new MockHttpServletResponse();
    committed.flushBuffer();
    assertSame(
        failure,
        assertThrows(
            SessionStoreException.class, () -> filter.doFilter(request, committed, failing)));
    request.setDispatcherType(DispatcherType.ERROR);
    assertSame(
        failure,
        assertThrows(
            SessionStoreException.class,
            () -> filter.doFilter(request, new MockHttpServletResponse(), failing)));
    request.setDispatcherType(DispatcherType.REQUEST);
    var io = new IOException("synthetic failure");
    var servlet = new ServletException("synthetic failure");
    var runtime = new IllegalStateException("synthetic failure");
    var npe = new NullPointerException("synthetic contract failure");
    assertSame(
        io,
        assertThrows(
            IOException.class,
            () ->
                filter.doFilter(
                    request,
                    new MockHttpServletResponse(),
                    (r, s) -> {
                      throw io;
                    })));
    assertSame(
        servlet,
        assertThrows(
            ServletException.class,
            () ->
                filter.doFilter(
                    request,
                    new MockHttpServletResponse(),
                    (r, s) -> {
                      throw servlet;
                    })));
    assertSame(
        runtime,
        assertThrows(
            IllegalStateException.class,
            () ->
                filter.doFilter(
                    request,
                    new MockHttpServletResponse(),
                    (r, s) -> {
                      throw runtime;
                    })));
    assertSame(
        npe,
        assertThrows(
            NullPointerException.class,
            () ->
                filter.doFilter(
                    request,
                    new MockHttpServletResponse(),
                    (r, s) -> {
                      throw npe;
                    })));
    var broken =
        new MockHttpServletResponse() {
          @Override
          public void sendError(int status) throws IOException {
            throw io;
          }
        };
    assertSame(
        io, assertThrows(IOException.class, () -> filter.doFilter(request, broken, failing)));
    var statusFault =
        new MockHttpServletResponse() {
          @Override
          public boolean isCommitted() {
            throw runtime;
          }
        };
    assertSame(
        runtime,
        assertThrows(
            IllegalStateException.class, () -> filter.doFilter(request, statusFault, failing)));
    var calls = new AtomicInteger();
    filter.doFilter(request, new MockHttpServletResponse(), (r, s) -> calls.incrementAndGet());
    assertEquals(1, calls.get());
  }

  @Test
  void web151ErrorControllerIgnoresUnsafeDiagnostics() throws Exception {
    var controller = new ErrorController(new ProblemViewFactory());
    assertThrows(NullPointerException.class, () -> new ErrorController(null));
    assertThrows(NullPointerException.class, () -> new WebMvcConfiguration().errorController(null));
    var request = request("GET", "/error");
    context(request);
    var response = new MockHttpServletResponse();
    var model = new ExtendedModelMap();
    assertThrows(NullPointerException.class, () -> controller.error(null, response, model));
    assertThrows(NullPointerException.class, () -> controller.error(request, null, model));
    assertThrows(NullPointerException.class, () -> controller.error(request, response, null));
    var safeOnly =
        new HttpServletRequestWrapper(noNative(request)) {
          @Override
          public Object getAttribute(String name) {
            if (List.of(
                    RequestDispatcher.ERROR_EXCEPTION,
                    RequestDispatcher.ERROR_MESSAGE,
                    RequestDispatcher.ERROR_REQUEST_URI)
                .contains(name)) throw new AssertionError("error diagnostic read");
            return super.getAttribute(name);
          }

          @Override
          public String getQueryString() {
            throw new AssertionError("query read");
          }

          @Override
          public String getParameter(String name) {
            throw new AssertionError("parameter read");
          }
        };
    assertEquals("error/error", controller.error(safeOnly, response, model));
    assertEquals(404, response.getStatus());
    assertEquals(Set.of("page"), model.keySet());
    assertEquals(404, ((ErrorViewModel) model.get("page")).getStatus());
    for (String method : List.of("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")) {
      request.setMethod(method);
      for (DispatcherType dispatcher : List.of(DispatcherType.REQUEST, DispatcherType.ERROR)) {
        request.setDispatcherType(dispatcher);
        var output = new MockHttpServletResponse();
        controller.error(safeOnly, output, new ExtendedModelMap());
        boolean allowed =
            dispatcher == DispatcherType.ERROR || method.equals("GET") || method.equals("HEAD");
        assertEquals(allowed ? 404 : 405, output.getStatus());
        assertEquals(allowed ? null : "GET, HEAD", output.getHeader("Allow"));
      }
    }
    assertThrows(
        IllegalStateException.class,
        () -> controller.error(new MockHttpServletRequest(), response, model));
    var failure = new IllegalStateException("synthetic fault");
    var brokenModel =
        new ExtendedModelMap() {
          @Override
          public ExtendedModelMap addAttribute(String key, Object value) {
            throw failure;
          }
        };
    assertSame(
        failure,
        assertThrows(
            IllegalStateException.class, () -> controller.error(safeOnly, response, brokenModel)));
    var brokenResponse =
        new MockHttpServletResponse() {
          @Override
          public void setStatus(int status) {
            throw failure;
          }
        };
    assertSame(
        failure,
        assertThrows(
            IllegalStateException.class, () -> controller.error(safeOnly, brokenResponse, model)));
    var brokenRequest =
        new HttpServletRequestWrapper(request) {
          @Override
          public Object getAttribute(String name) {
            throw failure;
          }
        };
    assertSame(
        failure,
        assertThrows(
            IllegalStateException.class, () -> controller.error(brokenRequest, response, model)));
  }

  @Test
  void web156ForgedErrorDispatchNeverBypassesBusinessSecurity() throws Exception {
    try (var f = new Fixture(db)) {
      f.clock.value = Instant.now();
      var api = new SessionFormLoginTest.Api("0000", "USER", "0000", 0);
      var filter =
          new WebSecurityFilterFactory()
              .create(
                  new SpringEncryptedSessionRepository(f.repository, f.clock),
                  api.provider,
                  new WebSecurityAudit(new EmbeddedWebSecurityTest.Log(), f.clock, "pt", "pt"),
                  () -> new UUID(0, 1));
      var request = new MockHttpServletRequest("TRACE", "/error");
      request.setDispatcherType(DispatcherType.ERROR);
      request.setAttribute(RequestDispatcher.ERROR_STATUS_CODE, 400);
      request.setRemoteAddr("127.0.0.1");
      request.addHeader("X-Forwarded-For", "203.0.113.1");
      request.addHeader("X-Forwarded-Proto", "https");
      var calls = new AtomicInteger();
      f.failure = "open";
      filter.doFilter(request, new MockHttpServletResponse(), (r, s) -> calls.incrementAndGet());
      assertEquals(
          1, calls.get(), "internal error renderer must not re-run the original method rejection");
      assertEquals(0, api.sends.get());
      f.failure = "";
      for (DispatcherType dispatcher : DispatcherType.values()) {
        for (String path : List.of("/error", "/admin/users")) {
          var r = request("GET", path);
          r.setDispatcherType(dispatcher);
          r.addHeader("Dispatcher-Type", "ERROR");
          r.setQueryString("dispatcher=ERROR&status=200");
          var response = new MockHttpServletResponse();
          var reached = new AtomicInteger();
          filter.doFilter(
              r,
              response,
              (req, res) -> {
                reached.incrementAndGet();
                boolean internal = dispatcher == DispatcherType.ERROR && path.equals("/error");
                Object repository =
                    req.getAttribute(
                        org.springframework.session.web.http.SessionRepositoryFilter
                            .SESSION_REPOSITORY_ATTR);
                if (internal) assertNull(repository);
                else assertInstanceOf(SpringEncryptedSessionRepository.class, repository);
              });
          assertEquals(path.equals("/error") ? 1 : 0, reached.get());
          if (!path.equals("/error")) assertEquals(302, response.getStatus());
        }
      }
      filter.destroy();
    }
    var business = new LifecycleFilter();
    var errors = new LifecycleFilter();
    assertThrows(NullPointerException.class, () -> new InternalErrorDispatchRouter(null, errors));
    assertThrows(NullPointerException.class, () -> new InternalErrorDispatchRouter(business, null));
    var router = new InternalErrorDispatchRouter(business, errors);
    filterNulls(router);
    assertThrows(NullPointerException.class, () -> router.init(null));
    router.init(new MockFilterConfig());
    assertEquals(1, business.initialized);
    assertEquals(1, errors.initialized);
    var missing = request("GET", "/error");
    missing.setDispatcherType(DispatcherType.ERROR);
    set(principal("reader", "USER"));
    assertThrows(
        IllegalStateException.class,
        () -> router.doFilter(missing, new MockHttpServletResponse(), (r, s) -> fail()));
    assertNull(SecurityContextHolder.getContext().getAuthentication());
    router.destroy();
    assertEquals(1, business.destroyed);
    assertEquals(1, errors.destroyed);
    for (int initFault : List.of(1, 2)) {
      var b = new LifecycleFilter();
      var e = new LifecycleFilter();
      e.initFault = initFault;
      var failed = new InternalErrorDispatchRouter(b, e);
      if (initFault == 1)
        assertThrows(ServletException.class, () -> failed.init(new MockFilterConfig()));
      else assertThrows(IllegalStateException.class, () -> failed.init(new MockFilterConfig()));
      assertEquals(1, b.destroyed);
      assertEquals(1, e.destroyed);
    }
    var b = new LifecycleFilter();
    var e = new LifecycleFilter();
    e.destroyFault = true;
    var failed = new InternalErrorDispatchRouter(b, e);
    assertThrows(IllegalStateException.class, failed::destroy);
    assertEquals(1, b.destroyed);
    e.initFault = 1;
    assertThrows(IllegalStateException.class, () -> failed.init(new MockFilterConfig()));
    assertEquals(2, b.destroyed);
  }

  @Test
  void web152ErrorTemplatesRenderExactSafeDom() throws Exception {
    try (var mvc = new AnnotationConfigWebApplicationContext()) {
      mvc.setServletContext(new MockServletContext());
      mvc.register(WebMvcConfiguration.class);
      mvc.refresh();
      var mock = MockMvcBuilders.webAppContextSetup(mvc).build();
      for (int status : MESSAGES.keySet())
        for (String role : List.of("ANONYMOUS", "USER", "ADMIN")) {
          var prepared = request("GET", "/error");
          context(prepared);
          if (!role.equals("ANONYMOUS")) {
            prepared.setUserPrincipal(principal("reader", role));
            prepared.setAttribute(
                CsrfToken.class.getName(), new DefaultCsrfToken("unused", "_csrf", "b".repeat(64)));
            new WebDisplayContextFilter()
                .doFilter(prepared, new MockHttpServletResponse(), (r, s) -> {});
          }
          prepared.setDispatcherType(DispatcherType.ERROR);
          new WebErrorDispatchFilter()
              .doFilter(prepared, new MockHttpServletResponse(), (r, s) -> {});
          var builder =
              get("/error")
                  .requestAttr(RequestDispatcher.ERROR_STATUS_CODE, status)
                  .with(
                      r -> {
                        r.setDispatcherType(DispatcherType.ERROR);
                        var names = prepared.getAttributeNames();
                        while (names.hasMoreElements()) {
                          String name = names.nextElement();
                          r.setAttribute(name, prepared.getAttribute(name));
                        }
                        return r;
                      });
          var response = mock.perform(builder).andReturn().getResponse();
          assertEquals(status, response.getStatus());
          verifyError(
              response.getContentAsString(StandardCharsets.UTF_8),
              status,
              role.equals("ANONYMOUS") ? null : "reader",
              role,
              "b".repeat(64),
              REQUEST_ID);
        }
    }
  }

  @Test
  void web153RealHttpErrorsKeepStatusHeadersAndIdentity() throws Exception {
    resetDatabase();
    var api = new SessionFormLoginTest.Api("0000", "USER", "0000", 0);
    try (var server = server(api, false)) {
      String cookie = login(server, "reader", "p");
      for (int status : new int[] {400, 401, 403, 404, 405, 409, 416, 429, 500, 503}) {
        var response = server.send("GET", "/fixture-error?status=" + status, cookie, null, true);
        int expected = status == 500 ? 503 : status;
        assertEquals(expected, response.statusCode());
        verifyError(
            response.body(),
            expected,
            "reader",
            "USER",
            "04".repeat(32),
            new UUID(0, server.ids.get()));
        safeHeaders(response);
      }
      assertEquals(1, api.sends.get());
      assertEquals(0, server.posts.get());
      assertEquals(0, server.context.getManager().getActiveSessions());
    }
    api.erased();
  }

  @Test
  void web154DatabaseFailureRendersWithoutReadingSessionAgain() throws Exception {
    for (boolean afterSnapshot : List.of(false, true)) {
      resetDatabase();
      var api = new SessionFormLoginTest.Api("0000", "USER", "0000", 0);
      try (var server = server(api, false)) {
        String cookie = login(server, "reader", "p");
        try {
          if (afterSnapshot) server.breakDatabaseBeforeError = true;
          else server.f.failure = "open";
          var response =
              server.send(
                  "GET", afterSnapshot ? "/fixture-error?status=503" : "/", cookie, null, true);
          assertEquals(503, response.statusCode());
          verifyError(
              response.body(),
              503,
              afterSnapshot ? "reader" : null,
              "USER",
              "04".repeat(32),
              new UUID(0, 3));
          safeHeaders(response);
          assertEquals(1, api.sends.get());
          assertEquals(3, server.ids.get());
          assertEquals(0, server.context.getManager().getActiveSessions());
        } finally {
          server.f.failure = "";
        }
      }
      api.erased();
    }
  }

  @Test
  void web155DeniedRequestsKeepOneAuditAndOriginalRequestId() throws Exception {
    resetDatabase();
    var api = new SessionFormLoginTest.Api("0000", "USER", "0000", 0);
    try (var server = server(api, false)) {
      String cookie = login(server, "reader", "p");
      var role = server.send("GET", "/admin/users", cookie, null, true);
      assertEquals(403, role.statusCode());
      verifyError(role.body(), 403, "reader", "USER", "04".repeat(32), new UUID(0, 3));
      assertEquals(2, server.log.events.size());
      var csrf = server.send("POST", "/", cookie, "_csrf=" + "ff".repeat(32), true);
      assertEquals(403, csrf.statusCode());
      verifyError(csrf.body(), 403, "reader", "USER", "04".repeat(32), new UUID(0, 4));
      assertEquals(3, server.log.events.size());
      assertEquals(
          "00000000-0000-0000-0000-000000000004",
          server.log.events.getLast().get("requestId").getAsString());
      var direct =
          server.send(
              "GET", "/error?status=200&exception=private-query-canary", cookie, null, true);
      assertEquals(404, direct.statusCode());
      verifyError(direct.body(), 404, "reader", "USER", "04".repeat(32), new UUID(0, 5));
      var post = server.send("POST", "/error", cookie, "_csrf=" + "04".repeat(32), true);
      assertEquals(405, post.statusCode());
      assertEquals("GET, HEAD", post.headers().firstValue("allow").orElseThrow());
      var proxy = server.send("GET", "/error", cookie, null, false);
      assertEquals(403, proxy.statusCode());
      assertEquals("", proxy.body());
      var method = server.send("TRACK", "/private", null, null, true);
      assertEquals(400, method.statusCode());
      verifyError(method.body(), 400, null, "ANONYMOUS", "", new UUID(0, 8));
      safeHeaders(method);
      assertEquals(0, server.posts.get());
    }
    api.erased();
  }

  @Test
  void web157ConcurrentErrorRenderingKeepsRequestActorsSeparate() throws Exception {
    resetDatabase();
    var api = new SessionFormLoginTest.Api("0000", "DYNAMIC", "0000", 0);
    try (var server = server(api, true);
        var pool = Executors.newFixedThreadPool(8)) {
      var futures = new ArrayList<Future<Void>>();
      var requestIds = ConcurrentHashMap.<UUID>newKeySet();
      var tokens = ConcurrentHashMap.<String>newKeySet();
      for (int i = 0; i < 100; i++) {
        int n = i;
        futures.add(
            pool.submit(
                () -> {
                  String cookie = login(server, "user" + n, "password-user" + n);
                  var response =
                      server.send(
                          "GET",
                          n % 2 == 0 ? "/admin/users" : "/fixture-error?status=503",
                          cookie,
                          null,
                          true);
                  int status = n % 2 == 0 ? 403 : 503;
                  assertEquals(status, response.statusCode());
                  var document = Jsoup.parse(response.body());
                  UUID id = UUID.fromString(document.select(".request-id").text());
                  String csrf = document.select("input[name=_csrf]").attr("value");
                  assertTrue(requestIds.add(id));
                  assertEquals(64, csrf.length());
                  assertTrue(tokens.add(csrf));
                  verifyError(
                      response.body(), status, "user" + n, n % 2 == 0 ? "USER" : "ADMIN", csrf, id);
                  return null;
                }));
      }
      for (var future : futures) future.get(30, TimeUnit.SECONDS);
      assertEquals(100, requestIds.size());
      assertEquals(100, tokens.size());
      assertEquals(100, api.sends.get());
      assertEquals(150, server.log.events.size());
      assertEquals(300, server.ids.get());
      assertEquals(0, server.context.getManager().getActiveSessions());
    }
    api.erased();
  }

  private static void verifyError(
      String html, int status, String username, String role, String csrf, UUID id) {
    var document = Jsoup.parse(html);
    assertEquals("エラー - schubert NK", document.title());
    assertEquals("ja", document.select("html").attr("lang"));
    assertEquals(Integer.toString(status), document.select(".error-status").text());
    assertEquals(MESSAGES.get(status), document.select(".error-message").text());
    assertEquals(id.toString(), document.select(".request-id").text());
    assertEquals(1, document.select("main.page section[role=alert]").size());
    if (username == null) {
      assertTrue(document.select(".login-user, .login-role, form, input").isEmpty());
      assertEquals(List.of("/", "/login"), document.select("nav a").eachAttr("href"));
    } else {
      assertEquals(username, document.select(".login-user").text());
      assertEquals(role, document.select(".login-role").text());
      assertEquals("/logout", document.select("form").attr("action"));
      assertEquals("post", document.select("form").attr("method"));
      assertEquals(1, document.select("input").size());
      assertEquals(csrf, document.select("input[name=_csrf]").attr("value"));
    }
    assertTrue(document.select("script, style, iframe, img, [style]").isEmpty());
    for (String secret :
        List.of(
            "private-",
            "SessionPrincipal",
            "Exception",
            "classpath:",
            "SCHUBERT_NK_SESSION",
            "JSESSIONID",
            "a".repeat(64))) assertFalse(html.contains(secret), "unsafe diagnostic present");
  }

  private static void resetDatabase() throws Exception {
    try (var c = db.web();
        var statement = c.createStatement()) {
      statement.executeUpdate("DELETE FROM schubert_web_session.web_http_sessions");
    }
  }

  private EmbeddedWebSecurityTest.Server server(SessionFormLoginTest.Api api, boolean random)
      throws Exception {
    return new EmbeddedWebSecurityTest.Server(
        Files.createTempDirectory(root, "error-"),
        random,
        db,
        Optional.of(api.provider),
        true,
        true);
  }

  private static String login(
      EmbeddedWebSecurityTest.Server server, String username, String password) throws Exception {
    var first = server.send("GET", "/login", null, null, true);
    String cookie = first.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
    var login =
        server.send(
            "POST",
            "/login",
            cookie,
            "_csrf="
                + first.body().substring(6)
                + "&username="
                + username
                + "&password="
                + password,
            true);
    assertEquals(302, login.statusCode());
    return login.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
  }

  private static void safeHeaders(HttpResponse<String> response) {
    assertEquals("no-store", response.headers().firstValue("cache-control").orElseThrow());
    assertEquals("DENY", response.headers().firstValue("x-frame-options").orElseThrow());
    assertEquals("nosniff", response.headers().firstValue("x-content-type-options").orElseThrow());
  }

  private static final class LifecycleFilter implements Filter {
    int initialized;
    int destroyed;
    int initFault;
    boolean destroyFault;

    @Override
    public void init(FilterConfig config) throws ServletException {
      initialized++;
      if (initFault == 1) throw new ServletException("synthetic init");
      if (initFault == 2) throw new IllegalStateException("synthetic init");
    }

    @Override
    public void destroy() {
      destroyed++;
      if (destroyFault) throw new IllegalStateException("synthetic cleanup");
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
        throws IOException, ServletException {
      chain.doFilter(request, response);
    }
  }

  private static void filterNulls(Filter filter) {
    var request = new MockHttpServletRequest();
    var response = new MockHttpServletResponse();
    FilterChain forbidden = (r, s) -> fail("boundary passed");
    assertThrows(NullPointerException.class, () -> filter.doFilter(null, response, forbidden));
    assertThrows(NullPointerException.class, () -> filter.doFilter(request, null, forbidden));
    assertThrows(NullPointerException.class, () -> filter.doFilter(request, response, null));
    assertThrows(
        ServletException.class,
        () -> filter.doFilter(new ServletRequestWrapper(request), response, forbidden));
    assertThrows(
        ServletException.class,
        () -> filter.doFilter(request, new ServletResponseWrapper(response), forbidden));
  }

  private static MockHttpServletRequest request(String method, String path) {
    var request = new MockHttpServletRequest(method, path);
    request.setRemoteAddr("127.0.0.1");
    request.addHeader("X-Forwarded-For", "203.0.113.1");
    request.addHeader("X-Forwarded-Proto", "https");
    return request;
  }

  private static WebSecurityAudit audit() {
    return new WebSecurityAudit(
        new EmbeddedWebSecurityTest.Log(),
        Clock.fixed(Instant.parse("2026-09-09T00:00:00Z"), ZoneOffset.UTC),
        "pt",
        "pt");
  }

  private static void context(MockHttpServletRequest request) throws Exception {
    new CaddyTransportContextFilter(() -> REQUEST_ID, new CaddyClientAddressResolver(), audit())
        .doFilter(request, new MockHttpServletResponse(), (r, s) -> {});
  }

  private static SessionPrincipal principal(String name, String role) {
    return new SessionPrincipal(
        name,
        UserRole.valueOf(role),
        AuthenticationContext.of("a".repeat(64)),
        Instant.parse("2026-09-09T00:00:00Z"));
  }

  private static void set(SessionPrincipal p) {
    SecurityContextHolder.getContext()
        .setAuthentication(
            UsernamePasswordAuthenticationToken.authenticated(
                p, null, List.of(new SimpleGrantedAuthority("ROLE_" + p.role().wireValue()))));
  }

  private static HttpServletRequest noNative(HttpServletRequest request) {
    return new HttpServletRequestWrapper(request) {
      @Override
      public Principal getUserPrincipal() {
        throw new AssertionError("native principal read");
      }

      @Override
      public HttpSession getSession() {
        throw new AssertionError("session read");
      }

      @Override
      public HttpSession getSession(boolean create) {
        throw new AssertionError("session read");
      }
    };
  }
}
