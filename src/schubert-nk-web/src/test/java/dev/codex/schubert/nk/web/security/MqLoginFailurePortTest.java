package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.lang.System.Logger;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.ResourceBundle;
import java.util.UUID;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.springframework.security.authentication.AuthenticationServiceException;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.core.AuthenticationException;

/** PT-LOGIN-FAIL001..006; UI226/SS314351352/QA055; own interface/logger callbacks only. */
final class MqLoginFailurePortTest {
  private static final int PROXY_FAILURE_INDEX = 2;
  private static final String RETRY = "Retry-After";
  private static final String LOCATION = "Location";
  private static final String LOCKED_URL = "/login?locked";
  private static final String ERROR_URL = "/login?error";
  private static final String ACTION = "action";
  private static final String DETAILS = "details";
  private static final String REQUEST_ID = "requestId";
  private static final String MARKER = "public-unissued-diagnostic-marker";
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-01-02T03:04:05Z"), ZoneOffset.UTC);

  private static <T> T port(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }

  private static final class MemoryLog implements Logger {
    private final ConcurrentLinkedQueue<String> events = new ConcurrentLinkedQueue<>();
    private RuntimeException failure;

    @Override
    public String getName() {
      return "owned-memory-only";
    }

    @Override
    public boolean isLoggable(Level level) {
      return true;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Throwable thrown) {
      throw new AssertionError("diagnostics must not be passed to the audit sink");
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Object... parameters) {
      assertNull(bundle);
      assertTrue(parameters == null || parameters.length == 0);
      if (failure != null) {
        throw failure;
      }
      assertEquals(Level.WARNING, level);
      assertFalse(message.contains(MARKER));
      events.add(message);
    }

    private List<JsonObject> json() {
      return events.stream().map(v -> JsonParser.parseString(v).getAsJsonObject()).toList();
    }
  }

  private static MqLoginFailureHandler handler(MemoryLog log) {
    return new MqLoginFailureHandler(new WebSecurityAudit(log, CLOCK, "pt-public", "pt-config"));
  }

  private static final class Fixture {
    private final UUID id;
    private final List<String> calls = new ArrayList<>();
    private final Map<String, String> headers = new HashMap<>();
    private Object context;
    private int status;
    private String failPoint = "";
    private final RuntimeException responseFailure =
        new IllegalStateException("public response failure");
    private final IOException ioFailure = new IOException("public sendError failure");

    private Fixture(long identifier) {
      id = new UUID(0, identifier);
      context = new WebRequestContext(id, new LoginClientAddress("192.0.2.1"));
    }

    private HttpServletRequest request() {
      return port(
          HttpServletRequest.class,
          (proxy, method, args) -> {
            calls.add("request." + method.getName());
            assertEquals(
                "getAttribute", method.getName(), "no credential/body/session/header access");
            assertEquals(WebRequestContext.class.getName(), args[0]);
            return context;
          });
    }

    private HttpServletResponse response() {
      return port(
          HttpServletResponse.class,
          (proxy, method, args) -> {
            String operation = method.getName();
            String point = operation.equals("setHeader") ? operation + ":" + args[0] : operation;
            calls.add("response." + point);
            if (point.equals(failPoint)) {
              if (operation.equals("sendError")) {
                throw ioFailure;
              }
              throw responseFailure;
            }
            switch (operation) {
              case "setHeader" -> headers.put((String) args[0], (String) args[1]);
              case "setStatus", "sendError" -> status = (Integer) args[0];
              default -> throw new AssertionError("unexpected response operation " + operation);
            }
            return null;
          });
    }
  }

  @Test
  void lockedApiDelayIsExactHeaderWithCurrentRedirectAndOneRedactedAudit() throws Exception {
    for (int delay : List.of(0, 1, 899, 900)) {
      var f = new Fixture(delay + 1);
      var log = new MemoryLog();
      handler(log)
          .onAuthenticationFailure(f.request(), f.response(), new MqLoginLockedException(delay));
      assertEquals(302, f.status);
      assertEquals(Map.of(RETRY, Integer.toString(delay), LOCATION, LOCKED_URL), f.headers);
      assertEquals(
          List.of(
              "request.getAttribute",
              "response.setHeader:" + RETRY,
              "response.setHeader:" + LOCATION,
              "response.setStatus"),
          f.calls);
      var event = log.json().getFirst();
      assertEquals(1, log.json().size());
      assertEquals("LOGIN_LOCKED", event.get(ACTION).getAsString());
      assertEquals(f.id.toString(), event.get(REQUEST_ID).getAsString());
      assertEquals(delay, event.getAsJsonObject(DETAILS).get("retryAfterSeconds").getAsInt());
      assertEquals("/login", event.getAsJsonObject(DETAILS).get("route").getAsString());
      assertFalse(event.has("actorUsername"));
    }
    assertThrows(IllegalArgumentException.class, () -> new MqLoginLockedException(-1));
    assertThrows(IllegalArgumentException.class, () -> new MqLoginLockedException(901));
  }

  @Test
  void badFormProxyAndServiceFailuresRemainDistinctClosedHttpOutcomes() throws Exception {
    List<AuthenticationException> failures =
        List.of(
            new BadCredentialsException(MARKER),
            new LoginFormRejectedException(),
            new CaddyRequestRejectedException(),
            new AuthenticationServiceException(MARKER));
    List<Integer> expected = List.of(302, 400, 403, 503);
    for (int index = 0; index < failures.size(); index++) {
      var f = new Fixture(index + 1);
      var log = new MemoryLog();
      handler(log).onAuthenticationFailure(f.request(), f.response(), failures.get(index));
      assertEquals(expected.get(index), f.status);
      assertEquals(index == 0 ? Map.of(LOCATION, ERROR_URL) : Map.of(), f.headers);
      assertFalse(f.headers.containsKey(RETRY));
      assertEquals(index == 0 || index == PROXY_FAILURE_INDEX ? 1 : 0, log.events.size());
      if (index == 0) {
        assertEquals("LOGIN_FAILED", log.json().getFirst().get(ACTION).getAsString());
        assertFalse(log.json().getFirst().getAsJsonObject(DETAILS).has("retryAfterSeconds"));
      }
      if (index == PROXY_FAILURE_INDEX) {
        var event = log.json().getFirst();
        assertEquals("AUTHORIZATION_DENIED", event.get(ACTION).getAsString());
        assertEquals("PROXY", event.getAsJsonObject(DETAILS).get("reason").getAsString());
        assertFalse(event.has("remoteAddress"));
      }
    }
  }

  @Test
  void nullAndMissingInternalContextNeverProduceSuccessfulResponseOrAudit() {
    var log = new MemoryLog();
    var f = new Fixture(1);
    var failure = new BadCredentialsException(MARKER);
    assertThrows(NullPointerException.class, () -> new MqLoginFailureHandler(null));
    assertThrows(
        NullPointerException.class,
        () -> handler(log).onAuthenticationFailure(null, f.response(), failure));
    assertThrows(
        NullPointerException.class,
        () -> handler(log).onAuthenticationFailure(f.request(), null, failure));
    assertThrows(
        NullPointerException.class,
        () -> handler(log).onAuthenticationFailure(f.request(), f.response(), null));
    for (Object value : new Object[] {null, "public-wrong-type"}) {
      f.context = value;
      assertThrows(
          IllegalStateException.class,
          () -> handler(log).onAuthenticationFailure(f.request(), f.response(), failure));
    }
    assertEquals(0, f.status);
    assertTrue(f.headers.isEmpty());
    assertTrue(log.events.isEmpty());
  }

  @Test
  void memoryAuditFailurePropagatesBeforeLockedOrBadCredentialResponse() {
    for (AuthenticationException failure :
        List.of(new MqLoginLockedException(900), new BadCredentialsException(MARKER))) {
      var f = new Fixture(1);
      var log = new MemoryLog();
      log.failure = new IllegalStateException("public audit sink failure");
      assertSame(
          log.failure,
          assertThrows(
              IllegalStateException.class,
              () -> handler(log).onAuthenticationFailure(f.request(), f.response(), failure)));
      assertEquals(0, f.status);
      assertTrue(f.headers.isEmpty());
      assertTrue(log.events.isEmpty());
    }
  }

  @Test
  void responseCallbackFailuresKeepTheirIdentityAndDoNotBecomeCompletedRedirects() {
    for (String point : List.of("setHeader:" + RETRY, "setHeader:" + LOCATION, "setStatus")) {
      var f = new Fixture(1);
      f.failPoint = point;
      var log = new MemoryLog();
      assertSame(
          f.responseFailure,
          assertThrows(
              IllegalStateException.class,
              () ->
                  handler(log)
                      .onAuthenticationFailure(
                          f.request(), f.response(), new MqLoginLockedException(1))));
      assertEquals(1, log.events.size());
      assertEquals(0, f.status);
    }
    for (AuthenticationException failure :
        List.of(new LoginFormRejectedException(), new AuthenticationServiceException(MARKER))) {
      var f = new Fixture(1);
      f.failPoint = "sendError";
      var log = new MemoryLog();
      assertSame(
          f.ioFailure,
          assertThrows(
              IOException.class,
              () -> handler(log).onAuthenticationFailure(f.request(), f.response(), failure)));
      assertTrue(log.events.isEmpty());
      assertEquals(0, f.status);
    }
  }

  @Test
  void sharedHandlerParallelCallsKeepOwnDelayHeadersAndRequestAudit() throws Exception {
    var log = new MemoryLog();
    var shared = handler(log);
    try (var pool = Executors.newFixedThreadPool(2)) {
      var jobs = new ArrayList<java.util.concurrent.Future<UUID>>();
      for (int index = 0; index < 16; index++) {
        int delay = index;
        jobs.add(
            pool.submit(
                () -> {
                  var f = new Fixture(delay + 1);
                  shared.onAuthenticationFailure(
                      f.request(), f.response(), new MqLoginLockedException(delay));
                  assertEquals(302, f.status);
                  assertEquals(
                      Map.of(RETRY, Integer.toString(delay), LOCATION, LOCKED_URL), f.headers);
                  return f.id;
                }));
      }
      var expected = new HashSet<String>();
      for (var job : jobs) {
        expected.add(job.get(10, TimeUnit.SECONDS).toString());
      }
      assertEquals(
          expected,
          new HashSet<>(log.json().stream().map(v -> v.get(REQUEST_ID).getAsString()).toList()));
      assertEquals(16, log.events.size());
    }
  }
}
