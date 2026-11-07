package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.JmsRequestSender;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.session.SecurityContextOwnerPortFixture;
import jakarta.servlet.http.HttpSession;
import java.lang.System.Logger;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.ResourceBundle;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.CompositeFilter;

/** PT-WEB-SECCONSTRUCT001..004. Public constructor and reject-before-backend path only. */
final class WebSecurityFactoryGuardPortTest {
  private static final String LOCATION_HEADER = "Location";
  private static final String COOKIE_HEADER = "Set-Cookie";
  private static final String GET = "GET";
  private static final String PATH = "/scenarios";
  private static final String FIXTURE = "public factory fixture";
  private static final UUID ID = new UUID(0, 44);
  private static final Clock CLOCK = Clock.fixed(Instant.EPOCH, ZoneOffset.UTC);
  private static final Map<String, String> EXPECTED_HEADERS =
      Map.of(
          "Content-Security-Policy",
          "default-src 'self'; style-src 'self'; img-src 'self' data:; media-src 'self';"
              + " form-action 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'",
          "Strict-Transport-Security",
          "max-age=31536000",
          "X-Content-Type-Options",
          "nosniff",
          "X-Frame-Options",
          "DENY",
          "Referrer-Policy",
          "same-origin",
          "Permissions-Policy",
          "camera=(), microphone=(), geolocation=(), payment=()",
          "Cache-Control",
          "no-store");

  @BeforeEach
  void ownEmptyContext() {
    assertEquals("MODE_THREADLOCAL", System.getProperty("spring.security.strategy"));
    SecurityContextHolder.clearContext();
  }

  @AfterEach
  void clearOwnedContext() {
    SecurityContextHolder.clearContext();
  }

  @Test
  void missingDependenciesAreRejectedWithoutRequestIdsOrBackendWork() {
    try (var f = new Ports()) {
      var factory = new WebSecurityFilterFactory();
      assertEquals(
          "sessions",
          assertThrows(
                  NullPointerException.class,
                  () -> factory.create(null, f.provider, f.audit, f.ids))
              .getMessage());
      assertEquals(
          "provider",
          assertThrows(
                  NullPointerException.class,
                  () -> factory.create(f.owner.sessions(), null, f.audit, f.ids))
              .getMessage());
      assertEquals(
          "audit",
          assertThrows(
                  NullPointerException.class,
                  () -> factory.create(f.owner.sessions(), f.provider, null, f.ids))
              .getMessage());
      assertEquals(
          "ids",
          assertThrows(
                  NullPointerException.class,
                  () -> factory.create(f.owner.sessions(), f.provider, f.audit, null))
              .getMessage());
      assertEquals(0, f.idCalls);
      assertTrue(f.logger.rows.isEmpty());
    }
  }

  @Test
  void fullyConstructedCompositesAreFreshAndDoNotIssueAnyIdentifier() {
    try (var f = new Ports()) {
      var factory = new WebSecurityFilterFactory();
      var first = factory.create(f.owner.sessions(), f.provider, f.audit, f.ids);
      var second = factory.create(f.owner.sessions(), f.provider, f.audit, f.ids);
      assertEquals(CompositeFilter.class, first.getClass());
      assertEquals(CompositeFilter.class, second.getClass());
      assertNotSame(first, second);
      assertEquals(0, f.idCalls);
      assertTrue(f.logger.rows.isEmpty());
    }
  }

  @Test
  void untrustedPeerGets403AndExactHeadersBeforeSessionFormOrBusinessAccess() throws Exception {
    for (String method : List.of(GET, "POST")) {
      try (var f = new Ports()) {
        var filter =
            new WebSecurityFilterFactory().create(f.owner.sessions(), f.provider, f.audit, f.ids);
        var request = new Request(method);
        var response = new MockHttpServletResponse();
        filter.doFilter(
            request,
            response,
            (incoming, outgoing) -> {
              throw new AssertionError("business chain forbidden on rejected transport");
            });
        assertEquals(403, response.getStatus());
        assertEquals(0, response.getContentAsByteArray().length);
        assertNull(response.getHeader(LOCATION_HEADER));
        assertNull(response.getHeader(COOKIE_HEADER));
        assertEquals(EXPECTED_HEADERS.keySet(), response.getHeaderNames());
        EXPECTED_HEADERS.forEach(
            (name, value) -> assertEquals(List.of(value), response.getHeaders(name)));
        assertEquals(1, f.idCalls);
        assertEquals(ID, request.getAttribute(WebRequestContext.class.getName() + ".requestId"));
        assertNull(request.getAttribute(WebRequestContext.class.getName()));
        assertEquals(1, f.logger.rows.size());
        var json = f.logger.rows.getFirst();
        assertEquals("AUTHORIZATION_DENIED", json.get("action").getAsString());
        assertEquals("PROXY", json.getAsJsonObject("details").get("reason").getAsString());
        assertFalse(json.has("actorUsername"));
        assertFalse(json.has("remoteAddr"));
        assertNull(SecurityContextHolder.getContext().getAuthentication());
      }
    }
  }

  @Test
  void ownedRequestIdFailurePropagatesWithoutAuditSessionOrBusinessCallbacks() {
    try (var f = new Ports()) {
      var failure = new IllegalStateException(FIXTURE);
      Supplier<UUID> unavailable =
          () -> {
            throw failure;
          };
      var filter =
          new WebSecurityFilterFactory()
              .create(f.owner.sessions(), f.provider, f.audit, unavailable);
      var request = new Request(GET);
      var response = new MockHttpServletResponse();
      assertSame(
          failure,
          assertThrows(
              IllegalStateException.class,
              () ->
                  filter.doFilter(
                      request,
                      response,
                      (incoming, outgoing) -> {
                        throw new AssertionError("business chain forbidden after ID failure");
                      })));
      assertEquals(0, f.idCalls);
      assertTrue(f.logger.rows.isEmpty());
      assertNull(request.getAttribute(WebRequestContext.class.getName()));
      assertNull(response.getHeader(LOCATION_HEADER));
      assertNull(response.getHeader(COOKIE_HEADER));
      EXPECTED_HEADERS.forEach(
          (name, value) -> assertEquals(List.of(value), response.getHeaders(name)));
    }
  }

  private static final class Ports implements AutoCloseable {
    final SecurityContextOwnerPortFixture owner = new SecurityContextOwnerPortFixture();
    final AuditLog logger = new AuditLog();
    final WebSecurityAudit audit = new WebSecurityAudit(logger, CLOCK, "pt", "pt");
    final MqAuthenticationProvider provider;
    int idCalls;
    final Supplier<UUID> ids =
        () -> {
          idCalls++;
          return ID;
        };

    Ports() {
      var requester = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 1);
      JmsRequestSender sender =
          (id, bytes) -> {
            throw new AssertionError("JMS send forbidden");
          };
      Supplier<UUID> messageIds =
          () -> {
            throw new AssertionError("message IDs forbidden");
          };
      provider =
          new MqAuthenticationProvider(
              new MqLoginClient(requester, sender, CLOCK, messageIds, Duration.ofNanos(1)),
              new MqLoginContextProbe(requester, sender, CLOCK, messageIds, Duration.ofNanos(1)));
    }

    @Override
    public void close() {
      owner.close();
    }
  }

  private static final class Request extends MockHttpServletRequest {
    Request(String method) {
      super(method, PATH);
      setServletPath(PATH);
      setRemoteAddr("192.0.2.44");
    }

    @Override
    public HttpSession getSession() {
      throw new AssertionError("session forbidden");
    }

    @Override
    public HttpSession getSession(boolean create) {
      throw new AssertionError("session forbidden");
    }

    @Override
    public String getParameter(String name) {
      throw new AssertionError("form forbidden");
    }

    @Override
    public Map<String, String[]> getParameterMap() {
      throw new AssertionError("form forbidden");
    }
  }

  private static final class AuditLog implements Logger {
    final List<JsonObject> rows = new ArrayList<>();

    @Override
    public String getName() {
      return "own-security-factory-audit";
    }

    @Override
    public boolean isLoggable(Level level) {
      return true;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Throwable thrown) {
      throw new AssertionError("throwable logging forbidden");
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Object... parameters) {
      assertTrue(parameters == null || parameters.length == 0);
      rows.add(JsonParser.parseString(message).getAsJsonObject());
    }
  }
}
