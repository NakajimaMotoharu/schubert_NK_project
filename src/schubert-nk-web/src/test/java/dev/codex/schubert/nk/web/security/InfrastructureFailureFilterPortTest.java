package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

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
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;

/** PT-WEB-INFRA001..008; UI221/222/226 SS313/314/351/352. Supplied ports, no storage. */
final class InfrastructureFailureFilterPortTest {
  private static final String CHAIN = "chain";
  private static final String COMMITTED = "committed";
  private static final String DISPATCH = "dispatch";
  private final WebInfrastructureFailureFilter filter = new WebInfrastructureFailureFilter();

  @Test
  void nullPortsFailBeforeAnyCallback() {
    var frame = new Frame(DispatcherType.REQUEST, false);
    assertThrows(
        NullPointerException.class, () -> filter.doFilter(null, frame.response, frame.chain));
    assertThrows(
        NullPointerException.class, () -> filter.doFilter(frame.request, null, frame.chain));
    assertThrows(
        NullPointerException.class, () -> filter.doFilter(frame.request, frame.response, null));
    assertEquals(List.of(), frame.events);
  }

  @Test
  void nonHttpRequestOrResponseFailsWithoutRunningCaller() {
    var frame = new Frame(DispatcherType.REQUEST, false);
    var plainRequest = port(ServletRequest.class);
    var plainResponse = port(ServletResponse.class);
    assertEquals(
        "HTTP failure boundary required",
        assertThrows(
                ServletException.class,
                () -> filter.doFilter(plainRequest, frame.response, frame.chain))
            .getMessage());
    assertEquals(
        "HTTP failure boundary required",
        assertThrows(
                ServletException.class,
                () -> filter.doFilter(frame.request, plainResponse, frame.chain))
            .getMessage());
    assertThrows(
        ServletException.class, () -> filter.doFilter(plainRequest, plainResponse, frame.chain));
    assertEquals(List.of(), frame.events);
  }

  @Test
  void successfulCallerIsUnchangedAndNeverQueriesFailureMetadata() throws Exception {
    for (DispatcherType kind : DispatcherType.values()) {
      for (boolean committed : new boolean[] {false, true}) {
        var frame = new Frame(kind, committed);
        filter.doFilter(frame.request, frame.response, frame.chain);
        assertEquals(List.of(CHAIN), frame.events);
      }
    }
  }

  @Test
  void typedStorageFailureMapsExactly503OutsideErrorDispatch() throws Exception {
    for (DispatcherType kind :
        List.of(
            DispatcherType.REQUEST,
            DispatcherType.ASYNC,
            DispatcherType.FORWARD,
            DispatcherType.INCLUDE)) {
      var frame = new Frame(kind, false);
      frame.chainFailure = new SessionStoreException();
      filter.doFilter(frame.request, frame.response, frame.chain);
      assertEquals(List.of(CHAIN, COMMITTED, DISPATCH, "send:503"), frame.events);
    }
  }

  @Test
  void committedOutputRethrowsSameTypedFailureWithoutReadingDispatcher() {
    for (DispatcherType kind : DispatcherType.values()) {
      var frame = new Frame(kind, true);
      var failure = new SessionStoreException();
      frame.chainFailure = failure;
      assertSame(
          failure,
          assertThrows(
              SessionStoreException.class,
              () -> filter.doFilter(frame.request, frame.response, frame.chain)));
      assertEquals(List.of(CHAIN, COMMITTED), frame.events);
    }
  }

  @Test
  void errorDispatchRethrowsSameTypedFailureWithoutSecondErrorSignal() {
    var frame = new Frame(DispatcherType.ERROR, false);
    var failure = new SessionStoreException();
    frame.chainFailure = failure;
    assertSame(
        failure,
        assertThrows(
            SessionStoreException.class,
            () -> filter.doFilter(frame.request, frame.response, frame.chain)));
    assertEquals(List.of(CHAIN, COMMITTED, DISPATCH), frame.events);
  }

  @Test
  void otherFailuresAndErrorCallbackFailuresPreserveIdentityWithoutRetry() {
    for (Throwable failure :
        List.of(
            new IOException("public IO"),
            new ServletException("public servlet"),
            new IllegalArgumentException("public argument"),
            new AssertionError("public error"),
            new ServletException(new SessionStoreException()))) {
      var frame = new Frame(DispatcherType.REQUEST, false);
      frame.chainFailure = failure;
      assertSame(
          failure,
          assertThrows(
              failure.getClass(),
              () -> filter.doFilter(frame.request, frame.response, frame.chain)));
      assertEquals(List.of(CHAIN), frame.events);
    }
    for (Throwable failure :
        List.of(
            new IOException("public response IO"),
            new IllegalStateException("public state"),
            new AssertionError("public response error"))) {
      var frame = new Frame(DispatcherType.REQUEST, false);
      frame.chainFailure = new SessionStoreException();
      frame.responseFailure = failure;
      assertSame(
          failure,
          assertThrows(
              failure.getClass(),
              () -> filter.doFilter(frame.request, frame.response, frame.chain)));
      assertEquals(List.of(CHAIN, COMMITTED, DISPATCH, "send:503"), frame.events);
    }
  }

  @Test
  void sharedFilterKeepsEightConcurrentFailuresAndSuccessesRequestLocal() throws Exception {
    try (var workers = Executors.newFixedThreadPool(2)) {
      var jobs = new ArrayList<java.util.concurrent.Future<?>>();
      for (int index = 0; index < 8; index++) {
        boolean failing = index % 2 == 0;
        jobs.add(
            workers.submit(
                () -> {
                  var frame = new Frame(DispatcherType.REQUEST, false);
                  if (failing) frame.chainFailure = new SessionStoreException();
                  filter.doFilter(frame.request, frame.response, frame.chain);
                  assertEquals(
                      failing ? List.of(CHAIN, COMMITTED, DISPATCH, "send:503") : List.of(CHAIN),
                      frame.events);
                  return null;
                }));
      }
      for (var job : jobs) job.get(10, java.util.concurrent.TimeUnit.SECONDS);
    }
  }

  private static <T> T port(Class<T> type) {
    return type.cast(
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (proxy, method, args) -> {
              throw new AssertionError("unexpected generic Servlet access: " + method.getName());
            }));
  }

  private static void raise(Throwable failure) throws IOException, ServletException {
    if (failure == null) return;
    if (failure instanceof IOException typed) throw typed;
    if (failure instanceof ServletException typed) throw typed;
    if (failure instanceof RuntimeException typed) throw typed;
    if (failure instanceof Error typed) throw typed;
    throw new AssertionError("fixture accepts only declared or unchecked failures");
  }

  private static final class Frame {
    final List<String> events = new ArrayList<>();
    final HttpServletRequest request;
    final HttpServletResponse response;
    final FilterChain chain;
    Throwable chainFailure;
    Throwable responseFailure;

    Frame(DispatcherType dispatcher, boolean committed) {
      request =
          (HttpServletRequest)
              Proxy.newProxyInstance(
                  HttpServletRequest.class.getClassLoader(),
                  new Class<?>[] {HttpServletRequest.class},
                  (proxy, method, args) -> {
                    if (method.getName().equals("getDispatcherType")) {
                      events.add(DISPATCH);
                      return dispatcher;
                    }
                    throw new AssertionError("unexpected request access: " + method.getName());
                  });
      response =
          (HttpServletResponse)
              Proxy.newProxyInstance(
                  HttpServletResponse.class.getClassLoader(),
                  new Class<?>[] {HttpServletResponse.class},
                  (proxy, method, args) -> {
                    if (method.getName().equals("isCommitted")) {
                      events.add(COMMITTED);
                      return committed;
                    }
                    if (method.getName().equals("sendError") && args.length == 1) {
                      events.add("send:" + args[0]);
                      raise(responseFailure);
                      return null;
                    }
                    throw new AssertionError("unexpected response access: " + method.getName());
                  });
      chain =
          (suppliedRequest, suppliedResponse) -> {
            assertSame(request, suppliedRequest);
            assertSame(response, suppliedResponse);
            events.add(CHAIN);
            raise(chainFailure);
          };
    }
  }
}
