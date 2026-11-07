package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import jakarta.servlet.DispatcherType;
import jakarta.servlet.Filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.FilterConfig;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.security.core.context.SecurityContextHolder;

/** PT-WEB-ERRROUTE001..008; UI221/222/226 SS313/314/352. Owned callbacks, no real dispatch. */
final class ErrorDispatchRouterPortTest {
  private static final String BUSINESS = "business";
  private static final String ERRORS = "errors";
  private static final String BUSINESS_INIT = "business.init";
  private static final String ERRORS_INIT = "errors.init";
  private static final String ERRORS_DESTROY = "errors.destroy";
  private static final String BUSINESS_DESTROY = "business.destroy";
  private static final String ERROR_PATH = "/error";
  private static final String PLAIN_PATH = "/fixture";
  private static final String CHAIN = "chain";

  @BeforeEach
  void verifyOnlyThisChildUsesPlainThreadLocal() {
    assertEquals("MODE_THREADLOCAL", System.getProperty("spring.security.strategy"));
    assertEquals(
        "org.springframework.security.core.context.ThreadLocalSecurityContextHolderStrategy",
        SecurityContextHolder.getContextHolderStrategy().getClass().getName());
    SecurityContextHolder.clearContext();
  }

  @AfterEach
  void clearOnlyOwnChildThread() {
    SecurityContextHolder.clearContext();
  }

  @Test
  void constructorRequiresBothIndependentCallbackPorts() {
    var frame = new Frame(DispatcherType.REQUEST, PLAIN_PATH);
    assertThrows(
        NullPointerException.class, () -> new InternalErrorDispatchRouter(null, frame.errors));
    assertThrows(
        NullPointerException.class, () -> new InternalErrorDispatchRouter(frame.business, null));
    assertEquals(List.of(), frame.events);
  }

  @Test
  void initializationIsBusinessThenErrorsAndBusinessFailureStopsImmediately() throws Exception {
    var frame = new Frame(DispatcherType.REQUEST, PLAIN_PATH);
    var config = unusedPort(FilterConfig.class);
    assertThrows(NullPointerException.class, () -> frame.router.init(null));
    assertEquals(List.of(), frame.events);
    frame.router.init(config);
    assertEquals(List.of(BUSINESS_INIT, ERRORS_INIT), frame.events);
    assertSame(config, frame.business.lastConfig);
    assertSame(config, frame.errors.lastConfig);
    for (Throwable failure :
        List.of(new ServletException(), new IllegalStateException(), new AssertionError())) {
      var failing = new Frame(DispatcherType.REQUEST, PLAIN_PATH);
      failing.business.initFailure = failure;
      assertSame(failure, assertThrows(failure.getClass(), () -> failing.router.init(config)));
      assertEquals(List.of(BUSINESS_INIT), failing.events);
    }
  }

  @Test
  void errorInitializationFailureCleansBothInReverseOrderEvenIfCleanupThrows() {
    var config = unusedPort(FilterConfig.class);
    for (Throwable failure : List.of(new ServletException(), new IllegalStateException())) {
      var frame = new Frame(DispatcherType.REQUEST, PLAIN_PATH);
      frame.errors.initFailure = failure;
      assertSame(failure, assertThrows(failure.getClass(), () -> frame.router.init(config)));
      assertEquals(
          List.of(BUSINESS_INIT, ERRORS_INIT, ERRORS_DESTROY, BUSINESS_DESTROY), frame.events);
      var cleanupFailure = new IllegalArgumentException();
      var second = new Frame(DispatcherType.REQUEST, PLAIN_PATH);
      second.errors.initFailure = failure;
      second.errors.destroyFailure = cleanupFailure;
      assertSame(
          cleanupFailure,
          assertThrows(IllegalArgumentException.class, () -> second.router.init(config)));
      assertEquals(
          List.of(BUSINESS_INIT, ERRORS_INIT, ERRORS_DESTROY, BUSINESS_DESTROY), second.events);
    }
  }

  @Test
  void destructionAlwaysInvokesBusinessAfterErrorsAndPreservesFinallyPrecedence() {
    var frame = new Frame(DispatcherType.REQUEST, PLAIN_PATH);
    frame.router.destroy();
    assertEquals(List.of(ERRORS_DESTROY, BUSINESS_DESTROY), frame.events);
    for (Throwable failure : List.of(new IllegalStateException(), new AssertionError())) {
      var failing = new Frame(DispatcherType.REQUEST, PLAIN_PATH);
      failing.errors.destroyFailure = failure;
      assertSame(failure, assertThrows(failure.getClass(), failing.router::destroy));
      assertEquals(List.of(ERRORS_DESTROY, BUSINESS_DESTROY), failing.events);
      var override = new IllegalArgumentException();
      var both = new Frame(DispatcherType.REQUEST, PLAIN_PATH);
      both.errors.destroyFailure = failure;
      both.business.destroyFailure = override;
      assertSame(override, assertThrows(IllegalArgumentException.class, both.router::destroy));
      assertEquals(List.of(ERRORS_DESTROY, BUSINESS_DESTROY), both.events);
    }
  }

  @Test
  void nullAndNonHttpBoundaryRejectBeforeRoutingOrContextCleanup() {
    var frame = new Frame(DispatcherType.REQUEST, PLAIN_PATH);
    var context = SecurityContextHolder.createEmptyContext();
    SecurityContextHolder.setContext(context);
    assertThrows(
        NullPointerException.class, () -> frame.router.doFilter(null, frame.response, frame.chain));
    assertThrows(
        NullPointerException.class, () -> frame.router.doFilter(frame.request, null, frame.chain));
    assertThrows(
        NullPointerException.class,
        () -> frame.router.doFilter(frame.request, frame.response, null));
    var plainRequest = unusedPort(ServletRequest.class);
    var plainResponse = unusedPort(ServletResponse.class);
    assertEquals(
        "HTTP routing boundary required",
        assertThrows(
                ServletException.class,
                () -> frame.router.doFilter(plainRequest, frame.response, frame.chain))
            .getMessage());
    assertThrows(
        ServletException.class,
        () -> frame.router.doFilter(frame.request, plainResponse, frame.chain));
    assertThrows(
        ServletException.class,
        () -> frame.router.doFilter(plainRequest, plainResponse, frame.chain));
    assertSame(context, SecurityContextHolder.getContext());
    assertEquals(List.of(), frame.events);
  }

  @Test
  void onlyExactInternalErrorWithSuppliedContextRoutesToErrorCallback() throws Exception {
    for (DispatcherType kind : DispatcherType.values()) {
      for (String uri : List.of(ERROR_PATH, PLAIN_PATH)) {
        var frame = new Frame(kind, uri);
        var before = SecurityContextHolder.createEmptyContext();
        SecurityContextHolder.setContext(before);
        frame.router.doFilter(frame.request, frame.response, frame.chain);
        assertEquals(
            List.of(
                kind == DispatcherType.ERROR && uri.equals(ERROR_PATH) ? ERRORS : BUSINESS, CHAIN),
            frame.events);
        assertNotSame(before, SecurityContextHolder.getContext());
      }
    }
    var nullUri = new Frame(DispatcherType.ERROR, null);
    nullUri.router.doFilter(nullUri.request, nullUri.response, nullUri.chain);
    assertEquals(List.of(BUSINESS, CHAIN), nullUri.events);
  }

  @Test
  void missingContextAndAllCallbackFailuresClearOnlyOwnThreadAndNeverRetry() {
    var missing = new Frame(DispatcherType.ERROR, ERROR_PATH);
    missing.context = null;
    var before = SecurityContextHolder.createEmptyContext();
    SecurityContextHolder.setContext(before);
    assertThrows(
        IllegalStateException.class,
        () -> missing.router.doFilter(missing.request, missing.response, missing.chain));
    assertEquals(List.of(), missing.events);
    assertNotSame(before, SecurityContextHolder.getContext());
    for (boolean errorRoute : new boolean[] {false, true}) {
      for (Throwable failure :
          List.of(
              new IOException(),
              new ServletException(),
              new IllegalStateException(),
              new AssertionError())) {
        var frame =
            new Frame(errorRoute ? DispatcherType.ERROR : DispatcherType.REQUEST, ERROR_PATH);
        if (errorRoute) frame.errors.filterFailure = failure;
        else frame.business.filterFailure = failure;
        var marker = SecurityContextHolder.createEmptyContext();
        SecurityContextHolder.setContext(marker);
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> frame.router.doFilter(frame.request, frame.response, frame.chain)));
        assertEquals(List.of(errorRoute ? ERRORS : BUSINESS), frame.events);
        assertNotSame(marker, SecurityContextHolder.getContext());
      }
    }
  }

  @Test
  void concurrentRoutesKeepEightSuppliedContextsAndCallbacksThreadLocal() throws Exception {
    try (var workers = Executors.newFixedThreadPool(2)) {
      var jobs = new ArrayList<java.util.concurrent.Future<?>>();
      for (int index = 0; index < 8; index++) {
        boolean error = index % 2 == 0;
        jobs.add(
            workers.submit(
                () -> {
                  var frame =
                      new Frame(error ? DispatcherType.ERROR : DispatcherType.REQUEST, ERROR_PATH);
                  var marker = SecurityContextHolder.createEmptyContext();
                  SecurityContextHolder.setContext(marker);
                  try {
                    frame.router.doFilter(frame.request, frame.response, frame.chain);
                    assertEquals(List.of(error ? ERRORS : BUSINESS, CHAIN), frame.events);
                    assertNotSame(marker, SecurityContextHolder.getContext());
                  } finally {
                    SecurityContextHolder.clearContext();
                  }
                  return null;
                }));
      }
      for (var job : jobs) job.get();
    }
  }

  private static <T> T unusedPort(Class<T> type) {
    return type.cast(
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (proxy, method, args) -> {
              throw new AssertionError("unexpected Servlet metadata access: " + method.getName());
            }));
  }

  private static void raise(Throwable failure) throws IOException, ServletException {
    if (failure instanceof IOException typed) throw typed;
    if (failure instanceof ServletException typed) throw typed;
    raiseUnchecked(failure);
  }

  private static void raiseUnchecked(Throwable failure) {
    if (failure == null) return;
    if (failure instanceof RuntimeException typed) throw typed;
    if (failure instanceof Error typed) throw typed;
    throw new AssertionError("unexpected checked fixture failure");
  }

  private static final class Callback implements Filter {
    final String name;
    final List<String> events;
    FilterConfig lastConfig;
    Throwable initFailure;
    Throwable destroyFailure;
    Throwable filterFailure;

    Callback(String name, List<String> events) {
      this.name = name;
      this.events = events;
    }

    @Override
    public void init(FilterConfig config) throws ServletException {
      events.add(name + ".init");
      lastConfig = config;
      if (initFailure instanceof ServletException typed) throw typed;
      raiseUnchecked(initFailure);
    }

    @Override
    public void destroy() {
      events.add(name + ".destroy");
      raiseUnchecked(destroyFailure);
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
        throws IOException, ServletException {
      events.add(name);
      raise(filterFailure);
      chain.doFilter(request, response);
    }
  }

  private static final class Frame {
    final List<String> events = new ArrayList<>();
    final Callback business = new Callback(BUSINESS, events);
    final Callback errors = new Callback(ERRORS, events);
    final InternalErrorDispatchRouter router = new InternalErrorDispatchRouter(business, errors);
    final HttpServletRequest request;
    final HttpServletResponse response = unusedPort(HttpServletResponse.class);
    final FilterChain chain;
    WebRequestContext context =
        new WebRequestContext(
            UUID.fromString("00000000-0000-0000-0000-000000000007"),
            new LoginClientAddress("192.0.2.1"));

    Frame(DispatcherType dispatcher, String uri) {
      request =
          (HttpServletRequest)
              Proxy.newProxyInstance(
                  HttpServletRequest.class.getClassLoader(),
                  new Class<?>[] {HttpServletRequest.class},
                  (proxy, method, args) ->
                      switch (method.getName()) {
                        case "getDispatcherType" -> dispatcher;
                        case "getRequestURI" -> uri;
                        case "getAttribute" -> {
                          assertEquals(WebRequestContext.ATTRIBUTE, args[0]);
                          yield context;
                        }
                        default ->
                            throw new AssertionError(
                                "unexpected request metadata: " + method.getName());
                      });
      chain =
          (suppliedRequest, suppliedResponse) -> {
            assertSame(request, suppliedRequest);
            assertSame(response, suppliedResponse);
            events.add(CHAIN);
          };
    }
  }
}
