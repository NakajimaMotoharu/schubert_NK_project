package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.config.RequestLogMvcConfiguration;
import dev.codex.schubert.nk.web.security.CaddyClientAddressResolver;
import dev.codex.schubert.nk.web.security.CaddyTransportContextFilter;
import dev.codex.schubert.nk.web.security.WebRequestContext;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import jakarta.servlet.DispatcherType;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.web.servlet.HandlerMapping;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;

/** Independent UI/actual mapping inventory and thread ownership; REQ004006007008/BUG573574. */
final class WebRequestTraceTest {
  private static final String FIXTURE_LOGIN_ROUTE = "/login";
  private static final String FIXTURE_ERROR_ROUTE = "/error";
  private static final String FIXTURE_ATTRIBUTE_FAILURE = "synthetic-private-attribute-canary";

  private static final Set<String> ROUTES =
      Set.of(
          "/",
          FIXTURE_LOGIN_ROUTE,
          "/logout",
          FIXTURE_ERROR_ROUTE,
          "/search",
          "/logs",
          "/scenarios",
          "/scenarios/{id:[0-9]{1,12}}",
          "/scenarios/{game:NUKITASHI[12]}",
          "/scenarios/{game:NUKITASHI[12]}/{prefix:[0-9]{2}}",
          "/animation",
          "/animation/main",
          "/animation/ova",
          "/animation/opening",
          "/animation/videos/{id}",
          "/animation/media/{id}",
          "/music",
          "/music/{category}",
          "/music/{category}/{section}",
          "/music/media/{id}",
          "/music/download/{id}",
          "/audio/{id}",
          "/audio/{id}/download",
          "/admin/users",
          "/admin/users/new",
          "/admin/users/{id:[0-9]{1,12}}",
          "/questions",
          "/questions/new",
          "/questions/accepted/{receiptId}",
          "/questions/{id:[0-9]{1,12}}",
          "/notifications",
          "/notifications/{id:[0-9]{1,12}}",
          "/css/**",
          "/js/**");

  @Test
  void req004ActualInventoryAndEveryClosedRouteRejectUnknown() throws Exception {
    Path controllers =
        Path.of(System.getProperty("nk.pt.repository"))
            .resolve("src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/controller");
    var actual = new HashSet<String>();
    int annotations = 0;
    var pattern = Pattern.compile("@(Get|Post|Request)Mapping\\(\"([^\"]+)\"\\)");
    try (var files = Files.list(controllers)) {
      for (Path file : files.filter(p -> p.toString().endsWith(".java")).toList()) {
        var matcher = pattern.matcher(Files.readString(file));
        while (matcher.find()) {
          actual.add(matcher.group(2));
          annotations++;
        }
      }
    }
    // UI224/236 SCR018/019: GET new, POST new and GET accepted are three mappings,
    // but the two /questions/new methods share one safe registered pattern.
    // NTC/QDL add two POST annotations on already registered safe detail patterns.
    assertEquals(37, annotations);
    var mapped = new HashSet<>(ROUTES);
    mapped.removeAll(Set.of("/css/**", "/js/**"));
    assertEquals(mapped, actual);
    String mvc =
        Files.readString(controllers.getParent().resolve("config/WebMvcConfiguration.java"));
    assertTrue(mvc.contains("addResourceHandler(\"/css/**\")"));
    assertTrue(mvc.contains("addResourceHandler(\"/js/**\")"));
    for (String route : ROUTES) {
      var trace = trace(new MockHttpServletRequest(), 1);
      trace.captureRoute(route);
      trace.captureRoute(FIXTURE_ERROR_ROUTE);
      assertEquals(route, trace.route(), "first registered route must remain authoritative");
    }
    for (String unknown :
        List.of(
            "",
            "/questions/new?question=canary",
            "/logout?context=canary",
            "/questions/accepted",
            "/music/secret-id",
            "/admin/users/{id:[0-9]+}",
            "/login?password=canary",
            "/canary\r\n",
            "/scenarios/{game}/{prefix}")) {
      var trace = trace(new MockHttpServletRequest(), 2);
      trace.captureRoute(unknown);
      assertEquals("/**", trace.route());
    }
  }

  @Test
  void req004ReceiptProjectionUsesRegisteredPatternAndNeverRawLocator() {
    var interceptor = new WebRequestRouteInterceptor();
    for (String pattern : List.of("/questions/new", "/questions/accepted/{receiptId}")) {
      var request = new MockHttpServletRequest("GET", "/questions/accepted/canary-private-locator");
      request.setQueryString("question=canary-body");
      var trace = trace(request, 1);
      request.setAttribute(HandlerMapping.BEST_MATCHING_PATTERN_ATTRIBUTE, pattern);
      assertTrue(interceptor.preHandle(request, new MockHttpServletResponse(), this));
      assertEquals(pattern, trace.route());
      assertFalse(trace.route().contains("canary"));
      trace.captureRoute(FIXTURE_ERROR_ROUTE);
      assertEquals(pattern, trace.route());
    }
  }

  @Test
  void req006ServerIdentityIsStableAndDoesNotGrantTransport() throws Exception {
    var request = new MockHttpServletRequest();
    request.addHeader("X-Request-ID", "not-server-id");
    var trace = trace(request, 3);
    assertEquals(new UUID(0, 3), trace.requestId());
    assertEquals(new UUID(1, 3), trace.eventId());
    assertEquals(trace.eventId(), trace.correlationId());
    assertTrue(WebRequestContext.existing(request).isEmpty());
    assertSame(
        trace,
        WebRequestTrace.ensure(
            request,
            () -> {
              throw new AssertionError("regenerated");
            }));
    request.setRemoteAddr("127.0.0.1");
    request.addHeader("X-Forwarded-Proto", "https");
    request.addHeader("X-Forwarded-For", "203.0.113.7");
    var audit =
        new WebSecurityAudit(System.getLogger("pt-request-context"), Clock.systemUTC(), "pt", "pt");
    new CaddyTransportContextFilter(
            () -> {
              throw new AssertionError("regenerated");
            },
            new CaddyClientAddressResolver(),
            audit)
        .doFilter(request, new MockHttpServletResponse(), (req, res) -> {});
    assertEquals(trace.requestId(), WebRequestContext.require(request).requestId());
    assertEquals("203.0.113.7", WebRequestContext.require(request).clientAddress().value());
    assertEquals("WebRequestContext[REDACTED]", WebRequestContext.require(request).toString());
    request.removeAttribute(WebRequestContext.class.getName() + ".requestId");
    assertEquals(
        new UUID(0, 3),
        WebRequestContext.identify(
            request,
            () -> {
              throw new AssertionError("unexpected request identity allocation");
            }));
    var other = new MockHttpServletRequest();
    trace(other, 4);
    other.setAttribute(WebRequestTrace.class.getName(), trace);
    assertThrows(
        IllegalStateException.class, () -> WebRequestTrace.ensure(other, UUID::randomUUID));
    request.setAttribute(WebRequestContext.class.getName() + ".requestId", new UUID(0, 8));
    assertThrows(
        IllegalStateException.class, () -> WebRequestTrace.ensure(request, UUID::randomUUID));
    request.setAttribute(WebRequestContext.class.getName() + ".requestId", "bad-type");
    assertThrows(
        IllegalStateException.class, () -> WebRequestContext.identify(request, UUID::randomUUID));
  }

  @Test
  void req007ActorIsSafeDisplaySnapshotNotPrincipalAndMissingTraceIsNoOp() {
    var request = new MockHttpServletRequest();
    var trace = trace(request, 5);
    for (UserRole role : UserRole.values()) {
      WebRequestTrace.captureActor(
          request,
          Optional.of(
              new SessionPrincipal(
                  "e\u0301quipe", role, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH)));
      assertEquals("équipe", trace.actor().orElseThrow().getUsername());
      assertEquals(role.name(), trace.actor().orElseThrow().getRole());
      assertEquals("TopBarViewModel[REDACTED]", trace.actor().orElseThrow().toString());
    }
    WebRequestTrace.captureActor(request, Optional.empty());
    assertTrue(trace.actor().isEmpty());
    WebRequestTrace.captureActor(new MockHttpServletRequest(), Optional.empty());
    assertEquals("WebRequestTrace[REDACTED]", trace.toString());
    assertTrue(trace.claimCompletion());
    assertFalse(trace.claimCompletion());
  }

  @Test
  void req008NestedScopesRestoreOnlyFirstBusinessMessageAndDoNotInherit() throws Exception {
    var first = trace(new MockHttpServletRequest(), 6);
    var second = trace(new MockHttpServletRequest(), 7);
    var counter = new AtomicInteger(10);
    var ids = WebRequestTrace.businessIdentifiers(() -> new UUID(2, counter.getAndIncrement()));
    assertEquals(new UUID(2, 10), ids.get());
    var outer = first.enter();
    try {
      assertEquals(new UUID(2, 11), ids.get());
      var inner = second.enter();
      try {
        assertEquals(new UUID(2, 12), ids.get());
      } finally {
        inner.close();
        inner.close();
      }
      ids.get();
      try (var pool = Executors.newVirtualThreadPerTaskExecutor()) {
        assertEquals(new UUID(2, 14), pool.submit(ids::get).get(5, TimeUnit.SECONDS));
        assertThrows(
            ExecutionException.class,
            () ->
                pool.submit(
                        () -> {
                          outer.close();
                          return 0;
                        })
                    .get(5, TimeUnit.SECONDS));
      }
    } finally {
      outer.close();
      outer.close();
    }
    ids.get();
    assertEquals(new UUID(2, 11), first.correlationId());
    assertEquals(new UUID(2, 12), second.correlationId());
    assertThrows(
        NullPointerException.class, () -> WebRequestTrace.businessIdentifiers(() -> null).get());
  }

  @Test
  void req008HundredConcurrentRequestsDoNotCrossContaminate() throws Exception {
    try (var pool = Executors.newVirtualThreadPerTaskExecutor()) {
      var jobs = new ArrayList<Future<Integer>>();
      for (int i = 1; i <= 100; i++) {
        final int owner = i;
        jobs.add(
            pool.submit(
                () -> {
                  var trace = trace(new MockHttpServletRequest(), owner);
                  var ids = WebRequestTrace.businessIdentifiers(() -> new UUID(2, owner));
                  var scope = trace.enter();
                  try {
                    ids.get();
                  } finally {
                    scope.close();
                  }
                  WebRequestTrace.businessIdentifiers(() -> new UUID(9, owner)).get();
                  assertEquals(new UUID(2, owner), trace.correlationId());
                  assertEquals(new UUID(0, owner), trace.requestId());
                  return owner;
                }));
      }
      for (int i = 0; i < jobs.size(); i++)
        assertEquals(i + 1, jobs.get(i).get(5, TimeUnit.SECONDS));
    }
  }

  @Test
  void req004InterceptorAcceptsOnlyRegisteredStringAndNeverErrorOverwrite() {
    var interceptor = new WebRequestRouteInterceptor();
    var request = new MockHttpServletRequest();
    var response = new MockHttpServletResponse();
    assertTrue(interceptor.preHandle(request, response, this));
    request.setAttribute(HandlerMapping.BEST_MATCHING_PATTERN_ATTRIBUTE, FIXTURE_LOGIN_ROUTE);
    assertTrue(
        interceptor.preHandle(request, response, this)); // Legacy isolated assembly: no trace.
    var trace = trace(request, 9);
    request.setAttribute(HandlerMapping.BEST_MATCHING_PATTERN_ATTRIBUTE, 123);
    interceptor.preHandle(request, response, this);
    assertEquals("/**", trace.route());
    request.setDispatcherType(DispatcherType.ERROR);
    request.setAttribute(HandlerMapping.BEST_MATCHING_PATTERN_ATTRIBUTE, FIXTURE_ERROR_ROUTE);
    interceptor.preHandle(request, response, this);
    assertEquals("/**", trace.route());
    request.setDispatcherType(DispatcherType.ASYNC);
    request.setAttribute(HandlerMapping.BEST_MATCHING_PATTERN_ATTRIBUTE, FIXTURE_LOGIN_ROUTE);
    interceptor.preHandle(request, response, this);
    assertEquals(FIXTURE_LOGIN_ROUTE, trace.route());
    var configuration = new RequestLogMvcConfiguration();
    configuration.addInterceptors(new InterceptorRegistry());
    assertThrows(NullPointerException.class, () -> configuration.addInterceptors(null));
    assertThrows(NullPointerException.class, () -> interceptor.preHandle(null, response, this));
    assertThrows(NullPointerException.class, () -> interceptor.preHandle(request, null, this));
    assertThrows(NullPointerException.class, () -> interceptor.preHandle(request, response, null));
  }

  @Test
  void req006AllNullAndMistypedMetadataAreRejected() {
    assertThrows(
        IllegalStateException.class, () -> WebRequestContext.require(new MockHttpServletRequest()));
    assertThrows(NullPointerException.class, () -> WebRequestContext.require(null));
    var mistypedContext = new MockHttpServletRequest();
    mistypedContext.setAttribute(WebRequestContext.class.getName(), "not-context");
    var contextFailure =
        assertThrows(
            IllegalStateException.class, () -> WebRequestContext.existing(mistypedContext));
    assertEquals("web request context is unavailable", contextFailure.getMessage());
    assertNull(contextFailure.getCause());
    assertEquals(0, contextFailure.getSuppressed().length);
    var request = new MockHttpServletRequest();
    assertThrows(NullPointerException.class, () -> WebRequestTrace.ensure(null, UUID::randomUUID));
    assertThrows(NullPointerException.class, () -> WebRequestTrace.ensure(request, null));
    assertThrows(NullPointerException.class, () -> WebRequestTrace.ensure(request, () -> null));
    assertThrows(NullPointerException.class, () -> WebRequestTrace.existing(null));
    assertThrows(
        NullPointerException.class, () -> WebRequestContext.identify(null, UUID::randomUUID));
    assertThrows(NullPointerException.class, () -> WebRequestContext.identify(request, null));
    var calls = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            WebRequestTrace.ensure(
                new MockHttpServletRequest(),
                () -> calls.getAndIncrement() == 0 ? new UUID(0, 1) : null));
    var trace = trace(request, 8);
    assertThrows(NullPointerException.class, () -> trace.captureRoute(null));
    assertThrows(NullPointerException.class, () -> WebRequestTrace.captureActor(request, null));
    assertThrows(
        NullPointerException.class, () -> WebRequestTrace.captureActor(null, Optional.empty()));
    assertThrows(NullPointerException.class, () -> WebRequestTrace.businessIdentifiers(null));
    request.setAttribute(WebRequestTrace.class.getName(), "not-trace");
    assertThrows(IllegalStateException.class, () -> WebRequestTrace.existing(request));
  }

  @Test
  void req006AllFourAttributeBoundariesRedactFrameworkFaults() {
    for (String attribute :
        List.of(
            WebRequestTrace.class.getName(), WebRequestContext.class.getName() + ".requestId")) {
      for (boolean set : List.of(false, true)) {
        for (boolean state : List.of(false, true)) {
          var request =
              new MockHttpServletRequest() {
                @Override
                public Object getAttribute(String name) {
                  if (!set && attribute.equals(name)) {
                    if (state) throw new IllegalStateException(FIXTURE_ATTRIBUTE_FAILURE);
                    throw new IllegalArgumentException(FIXTURE_ATTRIBUTE_FAILURE);
                  }
                  return super.getAttribute(name);
                }

                @Override
                public void setAttribute(String name, Object value) {
                  if (set && attribute.equals(name)) {
                    if (state) throw new IllegalStateException(FIXTURE_ATTRIBUTE_FAILURE);
                    throw new IllegalArgumentException(FIXTURE_ATTRIBUTE_FAILURE);
                  }
                  super.setAttribute(name, value);
                }
              };
          var failure =
              assertThrows(
                  IllegalStateException.class,
                  () -> WebRequestTrace.ensure(request, UUID::randomUUID));
          assertEquals(
              attribute.equals(WebRequestTrace.class.getName())
                  ? "request audit metadata is unavailable"
                  : "web request context is unavailable",
              failure.getMessage());
          assertNull(failure.getCause());
          assertEquals(0, failure.getSuppressed().length);
        }
      }
    }
  }

  @Test
  void req008OutOfOrderNestedCloseCannotPublishAClosedTrace() {
    for (boolean same : List.of(false, true)) {
      var first = trace(new MockHttpServletRequest(), 90);
      var second = same ? first : trace(new MockHttpServletRequest(), 91);
      var outer = first.enter();
      var inner = second.enter();
      try {
        var failure = assertThrows(IllegalStateException.class, outer::close);
        assertEquals("request audit scope order mismatch", failure.getMessage());
        WebRequestTrace.businessIdentifiers(() -> new UUID(2, 91)).get();
        assertEquals(new UUID(2, 91), second.correlationId());
      } finally {
        inner.close();
        outer.close();
      }
      WebRequestTrace.businessIdentifiers(() -> new UUID(9, 92)).get();
      assertEquals(same ? new UUID(2, 91) : new UUID(1, 90), first.correlationId());
      assertEquals(new UUID(2, 91), second.correlationId());
    }
  }

  static WebRequestTrace trace(MockHttpServletRequest request, int id) {
    var calls = new AtomicInteger();
    return WebRequestTrace.ensure(
        request, () -> calls.getAndIncrement() == 0 ? new UUID(0, id) : new UUID(1, id));
  }
}
