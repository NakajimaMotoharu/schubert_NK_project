package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.lang.System.Logger;
import java.lang.System.Logger.Level;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.ResourceBundle;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-WEB-TRANSPORTPORT001..005. Memory Servlet interfaces and logger only; no HTTP container. */
final class CaddyTransportPortTest {
  private static final UUID EXPECTED_ID = new UUID(0, 31);
  private static final String FIRST_CLIENT = "203.0.113.1";
  private static final String SECOND_CLIENT = "203.0.113.2";
  private static final String FORWARDED_FOR = "X-Forwarded-For";
  private static final String ID_ATTRIBUTE = WebRequestContext.class.getName() + ".requestId";
  private static final String SYNTHETIC_DETAIL = "synthetic detail";
  private static final String UNAVAILABLE = "web request context is unavailable";
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-09T00:00:00Z"), ZoneOffset.UTC);

  @Test
  void trustedDispatchAndRedispatchKeepOneIdentityAndSameContext() throws Exception {
    Fixture fixture = new Fixture();
    fixture.dispatch();
    WebRequestContext context = WebRequestContext.require(fixture.request);
    assertEquals(EXPECTED_ID, context.requestId());
    assertEquals(FIRST_CLIENT, context.clientAddress().value());
    assertEquals(EXPECTED_ID, fixture.attributes.get(ID_ATTRIBUTE));
    fixture.dispatch();
    assertSame(context, WebRequestContext.require(fixture.request));
    assertEquals(1, fixture.generated);
    assertEquals(2, fixture.downstream);
    assertEquals(200, fixture.status);
    assertEquals(0, fixture.sendErrorCalls);
    assertTrue(fixture.logger.entries.isEmpty());
  }

  @Test
  void nonHttpRequestAndResponseAreRejectedBeforeAnyDispatchOrAudit() {
    Fixture fixture = new Fixture();
    ServletRequest nonHttpRequest = emptyProxy(ServletRequest.class);
    ServletResponse nonHttpResponse = emptyProxy(ServletResponse.class);
    for (boolean badRequest : new boolean[] {true, false}) {
      ServletException failure =
          assertThrows(
              ServletException.class,
              () ->
                  fixture.filter.doFilter(
                      badRequest ? nonHttpRequest : fixture.request,
                      badRequest ? fixture.response : nonHttpResponse,
                      (in, out) -> fail("non-HTTP transport must not dispatch")));
      assertEquals("HTTP transport is required", failure.getMessage());
    }
    assertEquals(0, fixture.generated);
    assertTrue(fixture.attributes.isEmpty());
    assertTrue(fixture.logger.entries.isEmpty());
  }

  @Test
  void deniedPeerEnds403OncePerDispatchWithoutErrorRedispatchOrTrustedContext() throws Exception {
    for (boolean nonLoopback : new boolean[] {true, false}) {
      Fixture fixture = new Fixture();
      if (nonLoopback) fixture.peer = SECOND_CLIENT;
      else fixture.headers.put("Forwarded", List.of("for=203.0.113.9"));
      fixture.dispatch();
      assertEquals(403, fixture.status);
      assertEquals(0, fixture.downstream);
      assertEquals(0, fixture.sendErrorCalls);
      assertNull(fixture.attributes.get(WebRequestContext.ATTRIBUTE));
      assertEquals(EXPECTED_ID, fixture.attributes.get(ID_ATTRIBUTE));
      assertEquals(1, fixture.logger.entries.size());
      verifyDenied(fixture.logger.entries.getFirst());
      fixture.dispatch();
      assertEquals(1, fixture.generated);
      assertEquals(2, fixture.logger.entries.size());
      verifyDenied(fixture.logger.entries.getLast());
    }
  }

  @Test
  void existingContextCannotBeReboundToAnotherClientEvenWithSameServerId() throws Exception {
    Fixture fixture = new Fixture();
    WebRequestContext original =
        new WebRequestContext(EXPECTED_ID, new LoginClientAddress(FIRST_CLIENT));
    fixture.attributes.put(WebRequestContext.ATTRIBUTE, original);
    fixture.headers.put(FORWARDED_FOR, List.of(SECOND_CLIENT));
    fixture.dispatch();
    assertEquals(403, fixture.status);
    assertEquals(0, fixture.generated);
    assertEquals(0, fixture.downstream);
    assertSame(original, fixture.attributes.get(WebRequestContext.ATTRIBUTE));
    assertEquals(EXPECTED_ID, fixture.attributes.get(ID_ATTRIBUTE));
    assertEquals(1, fixture.logger.entries.size());
    verifyDenied(fixture.logger.entries.getFirst());
  }

  @Test
  void contextSaveFailuresAndNullContractsStopBeforeDownstreamWithoutUnsafeFallback() {
    Fixture fixture = new Fixture();
    assertThrows(
        NullPointerException.class,
        () ->
            new CaddyTransportContextFilter(null, new CaddyClientAddressResolver(), fixture.audit));
    assertThrows(
        NullPointerException.class,
        () -> new CaddyTransportContextFilter(() -> EXPECTED_ID, null, fixture.audit));
    assertThrows(
        NullPointerException.class,
        () ->
            new CaddyTransportContextFilter(
                () -> EXPECTED_ID, new CaddyClientAddressResolver(), null));
    assertThrows(
        NullPointerException.class,
        () -> fixture.filter.doFilter(null, fixture.response, (in, out) -> fail("null request")));
    assertThrows(
        NullPointerException.class,
        () -> fixture.filter.doFilter(fixture.request, null, (in, out) -> fail("null response")));
    assertThrows(
        NullPointerException.class,
        () -> fixture.filter.doFilter(fixture.request, fixture.response, null));
    assertEquals(0, fixture.generated);
    for (boolean stateFailure : new boolean[] {false, true}) {
      Fixture failed = new Fixture();
      failed.contextSaveFault = stateFailure ? "state" : "argument";
      IllegalStateException failure = assertThrows(IllegalStateException.class, failed::dispatch);
      assertEquals(UNAVAILABLE, failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
      assertEquals(EXPECTED_ID, failed.attributes.get(ID_ATTRIBUTE));
      assertNull(failed.attributes.get(WebRequestContext.ATTRIBUTE));
      assertEquals(0, failed.downstream);
      assertTrue(failed.logger.entries.isEmpty());
    }
  }

  private static void verifyDenied(JsonObject event) {
    assertEquals(
        Set.of(
            "timestamp",
            "level",
            "service",
            "appVersion",
            "configVersion",
            "category",
            "action",
            "outcome",
            "requestId",
            "details"),
        event.keySet());
    assertEquals("2026-09-09T00:00:00.000Z", event.get("timestamp").getAsString());
    assertEquals("WARN", event.get("level").getAsString());
    assertEquals("WEB", event.get("service").getAsString());
    assertEquals("fixture", event.get("appVersion").getAsString());
    assertEquals("1", event.get("configVersion").getAsString());
    assertEquals("SECURITY", event.get("category").getAsString());
    assertEquals("AUTHORIZATION_DENIED", event.get("action").getAsString());
    assertEquals("DENIED", event.get("outcome").getAsString());
    assertEquals(EXPECTED_ID.toString(), event.get("requestId").getAsString());
    assertEquals(
        JsonParser.parseString(
            "{\"reason\":\"PROXY\",\"route\":\"/**\",\"targetType\":\"HTTP_REQUEST\"}"),
        event.getAsJsonObject("details"));
    assertFalse(event.has("actorUsername"));
    assertFalse(event.has("remoteAddress"));
  }

  private static <T> T emptyProxy(Class<T> type) {
    return type.cast(
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (proxy, method, args) -> {
              throw new AssertionError("unexpected non-HTTP method");
            }));
  }

  private static final class Fixture {
    final Map<String, Object> attributes = new HashMap<>();
    final Map<String, List<String>> headers = new HashMap<>();
    final RecordingLogger logger = new RecordingLogger();
    final WebSecurityAudit audit = new WebSecurityAudit(logger, CLOCK, "fixture", "1");
    final HttpServletRequest request;
    final HttpServletResponse response;
    final CaddyTransportContextFilter filter;
    String peer = "127.0.0.1";
    String contextSaveFault = "none";
    int generated;
    int downstream;
    int status = 200;
    int sendErrorCalls;

    Fixture() {
      headers.put(FORWARDED_FOR, List.of(FIRST_CLIENT));
      headers.put("X-Forwarded-Proto", List.of("https"));
      request =
          (HttpServletRequest)
              Proxy.newProxyInstance(
                  HttpServletRequest.class.getClassLoader(),
                  new Class<?>[] {HttpServletRequest.class},
                  (proxy, method, args) ->
                      switch (method.getName()) {
                        case "getRemoteAddr" -> peer;
                        case "getHeaders" ->
                            Collections.enumeration(
                                headers.getOrDefault((String) args[0], List.of()));
                        case "getAttribute" -> attributes.get((String) args[0]);
                        case "setAttribute" -> {
                          if (args[0].equals(WebRequestContext.ATTRIBUTE)) {
                            if (contextSaveFault.equals("state"))
                              throw new IllegalStateException(SYNTHETIC_DETAIL);
                            if (contextSaveFault.equals("argument"))
                              throw new IllegalArgumentException(SYNTHETIC_DETAIL);
                          }
                          attributes.put((String) args[0], args[1]);
                          yield null;
                        }
                        case "toString" -> "OwnSyntheticHttpRequest";
                        case "hashCode" -> System.identityHashCode(proxy);
                        case "equals" -> proxy == args[0];
                        default ->
                            throw new AssertionError(
                                "unexpected request method: " + method.getName());
                      });
      response =
          (HttpServletResponse)
              Proxy.newProxyInstance(
                  HttpServletResponse.class.getClassLoader(),
                  new Class<?>[] {HttpServletResponse.class},
                  (proxy, method, args) ->
                      switch (method.getName()) {
                        case "setStatus" -> {
                          status = (Integer) args[0];
                          yield null;
                        }
                        case "sendError" -> {
                          sendErrorCalls++;
                          throw new AssertionError("must not redispatch error");
                        }
                        case "getStatus" -> status;
                        case "toString" -> "OwnSyntheticHttpResponse";
                        case "hashCode" -> System.identityHashCode(proxy);
                        case "equals" -> proxy == args[0];
                        default ->
                            throw new AssertionError(
                                "unexpected response method: " + method.getName());
                      });
      filter =
          new CaddyTransportContextFilter(
              () -> {
                generated++;
                return EXPECTED_ID;
              },
              new CaddyClientAddressResolver(),
              audit);
    }

    void dispatch() throws Exception {
      filter.doFilter(
          request,
          response,
          (in, out) -> {
            assertSame(request, in);
            assertSame(response, out);
            downstream++;
          });
    }
  }

  private static final class RecordingLogger implements Logger {
    final List<JsonObject> entries = new ArrayList<>();

    @Override
    public String getName() {
      return "own-transport-fixture";
    }

    @Override
    public boolean isLoggable(Level level) {
      return true;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Throwable thrown) {
      fail("must not log Throwable or private detail");
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String format, Object... params) {
      assertEquals(Level.WARNING, level);
      assertNull(bundle);
      assertNull(params);
      entries.add(JsonParser.parseString(format).getAsJsonObject());
    }
  }
}
