package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
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
import java.util.HashMap;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.springframework.security.core.context.SecurityContextHolder;

/** PT-WEB-ROUTERPORT001..010; inert callbacks and empty owned ThreadLocal only, no auth grant. */
final class InternalErrorRouterPortTest {
  private static final String INIT_FAILURE = "fixture-init";
  private static final String BUSINESS = "business";
  private static final String ERRORS = "errors";
  private static final String ERROR_PATH = "/error";
  private static final String INIT_B = "business:init";
  private static final String INIT_E = "errors:init";
  private static final String STOP_B = "business:stop";
  private static final String STOP_E = "errors:stop";
  private static final String CALL_B = "business:call";
  private static final String CALL_E = "errors:call";
  private static final String CHAIN = "chain";

  @FunctionalInterface
  private interface Init {
    void run(FilterConfig config) throws ServletException;
  }

  private static final class TraceFilter implements Filter {
    private final List<String> trace;
    private final String label;
    private Init initializeAction = config -> {};
    private Runnable stopAction = () -> {};
    private Filter invokeAction = (request, response, chain) -> chain.doFilter(request, response);

    private TraceFilter(List<String> trace, String label) {
      this.trace = trace;
      this.label = label;
    }

    @Override
    public void init(FilterConfig config) throws ServletException {
      trace.add(label + ":init");
      initializeAction.run(config);
    }

    @Override
    public void destroy() {
      trace.add(label + ":stop");
      stopAction.run();
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
        throws IOException, ServletException {
      trace.add(label + ":call");
      invokeAction.doFilter(request, response, chain);
    }
  }

  private static <T> T servlet(
      Class<T> type, DispatcherType dispatch, String uri, boolean context) {
    var attributes = new HashMap<String, Object>();
    if (context)
      attributes.put(
          WebRequestContext.ATTRIBUTE,
          new WebRequestContext(new UUID(0, 99), new LoginClientAddress("192.0.2.1")));
    return type.cast(
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (proxy, method, args) ->
                switch (method.getName()) {
                  case "getDispatcherType" -> dispatch;
                  case "getRequestURI" -> uri;
                  case "getAttribute" -> attributes.get(args[0]);
                  default -> throw new AssertionError("unexpected Servlet fixture method");
                }));
  }

  private static HttpServletRequest request(DispatcherType dispatch, String uri, boolean context) {
    return servlet(HttpServletRequest.class, dispatch, uri, context);
  }

  private static HttpServletResponse response() {
    return servlet(HttpServletResponse.class, DispatcherType.REQUEST, "/unused", false);
  }

  private static FilterConfig config() {
    return servlet(FilterConfig.class, DispatcherType.REQUEST, "/unused", false);
  }

  private static Object emptyContext() {
    assertEquals("MODE_THREADLOCAL", System.getProperty("spring.security.strategy"));
    var c = SecurityContextHolder.getContext();
    assertNull(c.getAuthentication());
    return c;
  }

  private static void cleared(Object prior) {
    var after = SecurityContextHolder.getContext();
    assertNotSame(prior, after);
    assertNull(after.getAuthentication());
    SecurityContextHolder.clearContext();
  }

  @Test
  void constructorAndConfigurationNullContractsReject() {
    var trace = new ArrayList<String>();
    var b = new TraceFilter(trace, BUSINESS);
    var e = new TraceFilter(trace, ERRORS);
    assertThrows(NullPointerException.class, () -> new InternalErrorDispatchRouter(null, e));
    assertThrows(NullPointerException.class, () -> new InternalErrorDispatchRouter(b, null));
    assertThrows(
        NullPointerException.class, () -> new InternalErrorDispatchRouter(b, e).init(null));
    assertEquals(List.of(), trace);
  }

  @Test
  void initializationUsesTheSameConfigAndFixedDelegateOrder() throws Exception {
    var trace = new ArrayList<String>();
    var b = new TraceFilter(trace, BUSINESS);
    var e = new TraceFilter(trace, ERRORS);
    var c = config();
    b.initializeAction = value -> assertSame(c, value);
    e.initializeAction = value -> assertSame(c, value);
    new InternalErrorDispatchRouter(b, e).init(c);
    assertEquals(List.of(INIT_B, INIT_E), trace);
  }

  @Test
  void firstDelegateFailureDoesNotInitializeOrDestroyTheSecond() {
    var checked = new ServletException(INIT_FAILURE);
    var runtime = new IllegalStateException(INIT_FAILURE);
    var fatal = new AssertionError(INIT_FAILURE);
    for (Throwable failure : List.of(checked, runtime, fatal)) {
      var trace = new ArrayList<String>();
      var b = new TraceFilter(trace, BUSINESS);
      var e = new TraceFilter(trace, ERRORS);
      b.initializeAction =
          ignored -> {
            if (failure instanceof ServletException v) throw v;
            if (failure instanceof RuntimeException v) throw v;
            throw (Error) failure;
          };
      var router = new InternalErrorDispatchRouter(b, e);
      assertSame(failure, assertThrows(failure.getClass(), () -> router.init(config())));
      assertEquals(List.of(INIT_B), trace);
    }
  }

  @Test
  void secondDelegateInitFailureStopsBothInReverseOrderAndKeepsLegacyPriority() {
    var checked = new ServletException(INIT_FAILURE);
    var runtime = new IllegalStateException(INIT_FAILURE);
    for (Throwable failure : List.of(checked, runtime)) {
      var trace = new ArrayList<String>();
      var b = new TraceFilter(trace, BUSINESS);
      var e = new TraceFilter(trace, ERRORS);
      e.initializeAction =
          ignored -> {
            if (failure instanceof ServletException v) throw v;
            throw (RuntimeException) failure;
          };
      var router = new InternalErrorDispatchRouter(b, e);
      assertSame(failure, assertThrows(failure.getClass(), () -> router.init(config())));
      assertEquals(List.of(INIT_B, INIT_E, STOP_E, STOP_B), trace);
    }
    var trace = new ArrayList<String>();
    var b = new TraceFilter(trace, BUSINESS);
    var e = new TraceFilter(trace, ERRORS);
    var stop = new IllegalStateException("fixture-stop");
    e.initializeAction =
        ignored -> {
          throw checked;
        };
    e.stopAction =
        () -> {
          throw stop;
        };
    assertSame(
        stop,
        assertThrows(
            IllegalStateException.class,
            () -> new InternalErrorDispatchRouter(b, e).init(config())));
    assertEquals(List.of(INIT_B, INIT_E, STOP_E, STOP_B), trace);
  }

  @Test
  void destructionAlwaysAttemptsBothAndPreservesFinallyExceptionPriority() {
    for (int mask = 0; mask < 4; mask++) {
      var trace = new ArrayList<String>();
      var b = new TraceFilter(trace, BUSINESS);
      var e = new TraceFilter(trace, ERRORS);
      var first = new IllegalStateException("fixture-first-stop");
      var last = new IllegalArgumentException("fixture-last-stop");
      if ((mask & 1) != 0)
        e.stopAction =
            () -> {
              throw first;
            };
      if ((mask & 2) != 0)
        b.stopAction =
            () -> {
              throw last;
            };
      var router = new InternalErrorDispatchRouter(b, e);
      if (mask == 0) router.destroy();
      else
        assertSame(
            (mask & 2) != 0 ? last : first, assertThrows(RuntimeException.class, router::destroy));
      assertEquals(List.of(STOP_E, STOP_B), trace);
    }
  }

  @Test
  void everyDispatcherAndPathCombinationInvokesExactlyOneDelegate() throws Exception {
    for (DispatcherType dispatch : DispatcherType.values())
      for (String path : List.of(ERROR_PATH, "/questions")) {
        var trace = new ArrayList<String>();
        var req = request(dispatch, path, true);
        var resp = response();
        var b = new TraceFilter(trace, BUSINESS);
        var e = new TraceFilter(trace, ERRORS);
        FilterChain chain =
            (q, s) -> {
              assertSame(req, q);
              assertSame(resp, s);
              trace.add(CHAIN);
            };
        Object prior = emptyContext();
        try {
          new InternalErrorDispatchRouter(b, e).doFilter(req, resp, chain);
          assertEquals(
              List.of(
                  dispatch == DispatcherType.ERROR && path.equals(ERROR_PATH) ? CALL_E : CALL_B,
                  CHAIN),
              trace);
          cleared(prior);
        } finally {
          SecurityContextHolder.clearContext();
        }
      }
  }

  @Test
  void internalErrorRequiresTrustedRequestContextBeforeAnyCallback() {
    for (boolean context : List.of(false, true)) {
      var trace = new ArrayList<String>();
      var req = request(DispatcherType.ERROR, ERROR_PATH, context);
      var router =
          new InternalErrorDispatchRouter(
              new TraceFilter(trace, BUSINESS), new TraceFilter(trace, ERRORS));
      Object prior = emptyContext();
      try {
        if (context) {
          router.doFilter(req, response(), (q, s) -> trace.add(CHAIN));
          assertEquals(List.of(CALL_E, CHAIN), trace);
        } else {
          var ex =
              assertThrows(
                  IllegalStateException.class,
                  () -> router.doFilter(req, response(), (q, s) -> trace.add(CHAIN)));
          assertEquals("web request context is unavailable", ex.getMessage());
          assertEquals(List.of(), trace);
        }
        cleared(prior);
      } catch (IOException | ServletException failure) {
        throw new AssertionError(failure);
      } finally {
        SecurityContextHolder.clearContext();
      }
    }
  }

  @Test
  void callbackCheckedRuntimeAndFatalFailuresPropagateAndClearOnlyEmptyContext() {
    for (DispatcherType dispatch : List.of(DispatcherType.REQUEST, DispatcherType.ERROR))
      for (Throwable failure :
          List.of(
              new IOException("fixture-io"),
              new ServletException("fixture-servlet"),
              new IllegalStateException("fixture-runtime"),
              new AssertionError("fixture-fatal"))) {
        var trace = new ArrayList<String>();
        var b = new TraceFilter(trace, BUSINESS);
        var e = new TraceFilter(trace, ERRORS);
        Filter action =
            (q, s, c) -> {
              if (failure instanceof IOException v) throw v;
              if (failure instanceof ServletException v) throw v;
              if (failure instanceof RuntimeException v) throw v;
              throw (Error) failure;
            };
        b.invokeAction = action;
        e.invokeAction = action;
        Object prior = emptyContext();
        try {
          assertSame(
              failure,
              assertThrows(
                  failure.getClass(),
                  () ->
                      new InternalErrorDispatchRouter(b, e)
                          .doFilter(
                              request(dispatch, ERROR_PATH, true),
                              response(),
                              (q, s) -> trace.add(CHAIN))));
          assertEquals(List.of(dispatch == DispatcherType.ERROR ? CALL_E : CALL_B), trace);
          cleared(prior);
        } finally {
          SecurityContextHolder.clearContext();
        }
      }
  }

  @Test
  void nullAndNonHttpBoundariesRejectWithoutAnyCallback() {
    var trace = new ArrayList<String>();
    var router =
        new InternalErrorDispatchRouter(
            new TraceFilter(trace, BUSINESS), new TraceFilter(trace, ERRORS));
    var req = request(DispatcherType.REQUEST, "/", false);
    var resp = response();
    FilterChain chain = (q, s) -> trace.add(CHAIN);
    assertThrows(NullPointerException.class, () -> router.doFilter(null, resp, chain));
    assertThrows(NullPointerException.class, () -> router.doFilter(req, null, chain));
    assertThrows(NullPointerException.class, () -> router.doFilter(req, resp, null));
    assertThrows(
        ServletException.class,
        () ->
            router.doFilter(
                servlet(ServletRequest.class, DispatcherType.REQUEST, "/", false), resp, chain));
    assertThrows(
        ServletException.class,
        () ->
            router.doFilter(
                req, servlet(ServletResponse.class, DispatcherType.REQUEST, "/", false), chain));
    assertEquals(List.of(), trace);
  }

  @Test
  void eightOwnedTasksKeepRequestsCallbacksAndEmptyContextsIsolated() throws Exception {
    try (var pool = Executors.newFixedThreadPool(2)) {
      var jobs = new ArrayList<Future<List<String>>>();
      for (int i = 0; i < 8; i++) {
        int index = i;
        jobs.add(
            pool.submit(
                () -> {
                  var trace = new ArrayList<String>();
                  Object prior = emptyContext();
                  try {
                    new InternalErrorDispatchRouter(
                            new TraceFilter(trace, BUSINESS), new TraceFilter(trace, ERRORS))
                        .doFilter(
                            request(
                                index % 2 == 0 ? DispatcherType.ERROR : DispatcherType.REQUEST,
                                ERROR_PATH,
                                true),
                            response(),
                            (q, s) -> trace.add(CHAIN));
                    cleared(prior);
                    return List.copyOf(trace);
                  } finally {
                    SecurityContextHolder.clearContext();
                  }
                }));
      }
      for (int i = 0; i < 8; i++)
        assertEquals(
            List.of(i % 2 == 0 ? CALL_E : CALL_B, CHAIN), jobs.get(i).get(10, TimeUnit.SECONDS));
    }
  }
}
