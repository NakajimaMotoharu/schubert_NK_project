package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import jakarta.servlet.DispatcherType;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;

/** PT-WEB-ERRORRESTORE001..008; owned attributes/display data only; no real auth or session. */
final class ErrorDispatchRestorePortTest {
  private static final String PATH = "/error";
  private static final String DISPLAY = WebDisplayContext.class.getName();
  private static final String TOKEN = CsrfToken.class.getName();
  private static final String ALIAS = "_csrf";
  private static final String HEADER = "X-CSRF-TOKEN";
  private static final String DUMMY = "0".repeat(64);
  private static final String VIEWER = "fixture-viewer";
  private static final String FAULT = "public-fixture-fault";
  private static final String GET_ATTRIBUTE = "getAttribute";
  private static final String REMOVE_ATTRIBUTE = "removeAttribute";
  private static final String SET_ATTRIBUTE = "setAttribute";
  private static final WebErrorDispatchFilter FILTER = new WebErrorDispatchFilter();

  private static final class Fixture {
    private final Map<String, Object> attributes = new HashMap<>();
    private final List<String> operations = new ArrayList<>();
    private DispatcherType dispatch = DispatcherType.ERROR;
    private String location = PATH;
    private boolean capturing;
    private @Nullable SessionPrincipal preparedPrincipal;
    private String failingMethod = "";
    private Runnable fault = () -> {};
    private int chainCalls;
    private final HttpServletRequest request = proxy(HttpServletRequest.class);
    private final HttpServletResponse response = proxy(HttpServletResponse.class);
    private final FilterChain chain =
        (req, res) -> {
          assertSame(request, req);
          assertSame(response, res);
          chainCalls++;
        };

    private <T> T proxy(Class<T> type) {
      return type.cast(
          Proxy.newProxyInstance(
              type.getClassLoader(),
              new Class<?>[] {type},
              (ignored, method, args) -> {
                String name = method.getName();
                if (name.equals(failingMethod)) fault.run();
                return switch (name) {
                  case "getDispatcherType" -> dispatch;
                  case "getRequestURI" -> location;
                  case "getUserPrincipal" -> {
                    if (!capturing)
                      throw new AssertionError("principal access forbidden during restore");
                    yield preparedPrincipal;
                  }
                  case GET_ATTRIBUTE -> {
                    operations.add(name);
                    yield attributes.get(args[0]);
                  }
                  case REMOVE_ATTRIBUTE -> {
                    operations.add(name);
                    attributes.remove(args[0]);
                    yield null;
                  }
                  case SET_ATTRIBUTE -> {
                    operations.add(name);
                    attributes.put((String) args[0], args[1]);
                    yield null;
                  }
                  default ->
                      throw new AssertionError("unexpected Servlet method or session access");
                };
              }));
    }

    private void captured(UserRole role) {
      preparedPrincipal =
          new SessionPrincipal(VIEWER, role, AuthenticationContext.of(DUMMY), Instant.EPOCH);
      attributes.put(TOKEN, new DefaultCsrfToken(HEADER, ALIAS, DUMMY));
      capturing = true;
      try {
        WebDisplayContext.capture(request);
      } finally {
        capturing = false;
        preparedPrincipal = null;
        operations.clear();
      }
      attributes.put(TOKEN, new Object());
      attributes.put(ALIAS, new Object());
    }
  }

  @Test
  void nullContractsDoNotReadRequestOrRunChain() {
    var f = new Fixture();
    assertThrows(NullPointerException.class, () -> FILTER.doFilter(null, f.response, f.chain));
    assertThrows(NullPointerException.class, () -> FILTER.doFilter(f.request, null, f.chain));
    assertThrows(NullPointerException.class, () -> FILTER.doFilter(f.request, f.response, null));
    assertEquals(0, f.chainCalls);
    assertEquals(List.of(), f.operations);
  }

  @Test
  void nonHttpRequestAndResponseRejectBeforeAttributeAccess() {
    var f = new Fixture();
    assertEquals(
        "HTTP error boundary required",
        assertThrows(
                ServletException.class,
                () -> FILTER.doFilter(f.proxy(ServletRequest.class), f.response, f.chain))
            .getMessage());
    assertEquals(
        "HTTP error boundary required",
        assertThrows(
                ServletException.class,
                () -> FILTER.doFilter(f.request, f.proxy(ServletResponse.class), f.chain))
            .getMessage());
    assertEquals(0, f.chainCalls);
    assertEquals(List.of(), f.operations);
  }

  @Test
  void onlyErrorDispatcherAndExactErrorPathCanRestore() {
    for (DispatcherType type : DispatcherType.values())
      if (type != DispatcherType.ERROR) {
        var f = new Fixture();
        f.dispatch = type;
        assertEquals(
            "internal error dispatch required",
            assertThrows(
                    ServletException.class, () -> FILTER.doFilter(f.request, f.response, f.chain))
                .getMessage());
        assertEquals(0, f.chainCalls);
        assertEquals(List.of(), f.operations);
      }
    for (String path : List.of("/", "/Error", "/error/", "/questions")) {
      var f = new Fixture();
      f.location = path;
      Object prior = new Object();
      f.attributes.put(TOKEN, prior);
      assertThrows(ServletException.class, () -> FILTER.doFilter(f.request, f.response, f.chain));
      assertSame(prior, f.attributes.get(TOKEN));
      assertEquals(List.of(), f.operations);
    }
  }

  @Test
  void anonymousRestoreRemovesBothAliasesAndNeverReadsSessionOrPrincipal() throws Exception {
    var f = new Fixture();
    Object keep = new Object();
    f.attributes.put("unrelated", keep);
    f.attributes.put(TOKEN, new Object());
    f.attributes.put(ALIAS, new Object());
    FILTER.doFilter(f.request, f.response, f.chain);
    assertFalse(f.attributes.containsKey(TOKEN));
    assertFalse(f.attributes.containsKey(ALIAS));
    assertSame(keep, f.attributes.get("unrelated"));
    assertEquals(List.of(GET_ATTRIBUTE, REMOVE_ATTRIBUTE, REMOVE_ATTRIBUTE), f.operations);
    assertEquals(1, f.chainCalls);
  }

  @Test
  void userAndAdminSnapshotsRestoreOnlyParsedDisplayToken() throws Exception {
    for (UserRole role : List.of(UserRole.USER, UserRole.ADMIN)) {
      var f = new Fixture();
      f.captured(role);
      Object snapshot = f.attributes.get(DISPLAY);
      FILTER.doFilter(f.request, f.response, f.chain);
      var token = (CsrfToken) f.attributes.get(TOKEN);
      assertSame(token, f.attributes.get(ALIAS));
      assertEquals(DUMMY, token.getToken());
      assertEquals(ALIAS, token.getParameterName());
      assertEquals(HEADER, token.getHeaderName());
      assertSame(snapshot, f.attributes.get(DISPLAY));
      var top = WebDisplayContext.existing(f.request).orElseThrow().topBar();
      assertEquals(VIEWER, top.getUsername());
      assertEquals(role == UserRole.USER ? "USER" : "ADMIN", top.getRole());
      assertEquals(
          List.of(GET_ATTRIBUTE, REMOVE_ATTRIBUTE, REMOVE_ATTRIBUTE, SET_ATTRIBUTE, SET_ATTRIBUTE),
          f.operations.subList(0, 5));
      assertEquals(1, f.chainCalls);
    }
  }

  @Test
  void corruptSnapshotNeverRestoresOrInvokesCallback() {
    var f = new Fixture();
    f.attributes.put(DISPLAY, "not-a-snapshot");
    var failure =
        assertThrows(
            SessionStoreException.class, () -> FILTER.doFilter(f.request, f.response, f.chain));
    assertNull(failure.getCause());
    assertFalse(f.attributes.containsKey(TOKEN));
    assertFalse(f.attributes.containsKey(ALIAS));
    assertEquals(List.of(GET_ATTRIBUTE), f.operations);
    assertEquals(0, f.chainCalls);
  }

  @Test
  void attributeAndCallbackFailuresPropagateWithoutFallback() {
    for (String method : List.of(GET_ATTRIBUTE, REMOVE_ATTRIBUTE, SET_ATTRIBUTE))
      for (Throwable error : List.of(new IllegalStateException(FAULT), new AssertionError(FAULT))) {
        var f = new Fixture();
        f.captured(UserRole.USER);
        f.failingMethod = method;
        f.fault =
            () -> {
              if (error instanceof RuntimeException v) throw v;
              throw (Error) error;
            };
        assertSame(
            error,
            assertThrows(error.getClass(), () -> FILTER.doFilter(f.request, f.response, f.chain)));
        assertEquals(0, f.chainCalls);
      }
    for (Throwable error :
        List.of(
            new IOException(FAULT),
            new ServletException(FAULT),
            new IllegalStateException(FAULT),
            new AssertionError(FAULT))) {
      var f = new Fixture();
      f.attributes.put(TOKEN, new Object());
      assertSame(
          error,
          assertThrows(
              error.getClass(),
              () -> FILTER.doFilter(f.request, f.response, (req, res) -> downstream(error))));
      assertFalse(f.attributes.containsKey(TOKEN));
      assertFalse(f.attributes.containsKey(ALIAS));
      assertEquals(List.of(GET_ATTRIBUTE, REMOVE_ATTRIBUTE, REMOVE_ATTRIBUTE), f.operations);
    }
  }

  @Test
  void eightConcurrentRequestsKeepRestoredAndAnonymousAttributesSeparate() throws Exception {
    var pool = Executors.newFixedThreadPool(2);
    try {
      var jobs = new ArrayList<Future<Boolean>>();
      for (int i = 0; i < 8; i++) {
        int index = i;
        jobs.add(
            pool.submit(
                () -> {
                  var f = new Fixture();
                  if (index % 2 == 0) f.captured(UserRole.ADMIN);
                  FILTER.doFilter(f.request, f.response, f.chain);
                  assertEquals(1, f.chainCalls);
                  assertEquals(f.attributes.containsKey(TOKEN), f.attributes.containsKey(ALIAS));
                  return f.attributes.containsKey(TOKEN);
                }));
      }
      for (int i = 0; i < 8; i++) assertEquals(i % 2 == 0, jobs.get(i).get(10, TimeUnit.SECONDS));
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  private static void downstream(Throwable error) throws IOException, ServletException {
    if (error instanceof IOException v) throw v;
    if (error instanceof ServletException v) throw v;
    if (error instanceof RuntimeException v) throw v;
    throw (Error) error;
  }
}
