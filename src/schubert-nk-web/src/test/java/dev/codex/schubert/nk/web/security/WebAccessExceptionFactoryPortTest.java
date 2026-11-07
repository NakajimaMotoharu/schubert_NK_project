package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.session.SecurityContextOwnerPortFixture;
import dev.codex.schubert.nk.web.session.SpringWebSession;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpSession;
import java.io.IOException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.ResourceBundle;
import java.util.UUID;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.mock.web.MockServletContext;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.authentication.AuthenticationCredentialsNotFoundException;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.access.ExceptionTranslationFilter;
import org.springframework.session.web.http.SessionRepositoryFilter;

/** PT-WEB-EXCFACT001..004; UI221226/SS313314351352; mock Servlet only, no backend or auth grant. */
final class WebAccessExceptionFactoryPortTest {
  private static final String FIXTURE = "public-fixture";
  private static final String SCENARIOS = "/scenarios";
  private static final String LOCATION = "Location";
  private static final String ROLE_CASE = "ROLE";
  private static final String UNAUTHENTICATED = "UNAUTHENTICATED";

  @BeforeEach
  @AfterEach
  void clearOwnedThreadContext() {
    SecurityContextHolder.clearContext();
  }

  @Test
  void factoryRejectsMissingHandlerAndRetainsTheExactEntryPointInFreshFilters() {
    try (var fixture = new Fixture()) {
      var factory = new WebAccessExceptionFilterFactory();
      assertEquals(
          "handler",
          assertThrows(NullPointerException.class, () -> factory.create(null)).getMessage());
      var first = factory.create(fixture.handler);
      var second = factory.create(fixture.handler);
      assertNotSame(first, second);
      assertEquals(ExceptionTranslationFilter.class, first.getClass());
      assertSame(fixture.handler, first.getAuthenticationEntryPoint());
      assertSame(fixture.handler, second.getAuthenticationEntryPoint());
      first.afterPropertiesSet();
      second.afterPropertiesSet();
      assertTrue(fixture.logger.entries.isEmpty());
    }
  }

  @Test
  void navigationAuthenticationFailureSavesExactlyOneRelativeStringAndRedirects() throws Exception {
    try (var fixture = new Fixture()) {
      var request = fixture.request("GET", SCENARIOS);
      request.setQueryString("page=2");
      var response = new MockHttpServletResponse();
      fixture
          .filter()
          .doFilter(
              request,
              response,
              (incoming, outgoing) -> {
                throw new ServletException(new AuthenticationCredentialsNotFoundException(FIXTURE));
              });
      assertEquals(302, response.getStatus());
      assertEquals("/login", response.getHeader(LOCATION));
      assertEquals(1, request.sessionCreates);
      assertEquals(1, request.retainedSession.writes);
      assertEquals(
          "/scenarios?page=2",
          request.retainedSession.getAttribute(SpringWebSession.SAVED_REQUEST));
      assertTrue(response.getHeaders("Set-Cookie").isEmpty());
      assertAudit(fixture.logger, UNAUTHENTICATED);
      assertNull(SecurityContextHolder.getContext().getAuthentication());
    }
  }

  @Test
  void nonnavigationAndAccessDeniedUseConfiguredHandlersWithoutCreatingAServletSession()
      throws Exception {
    for (String kind : List.of("POST", "AJAX", "MEDIA", ROLE_CASE)) {
      try (var fixture = new Fixture()) {
        var request =
            fixture.request(
                kind.equals("POST") ? "POST" : "GET",
                kind.equals("MEDIA") ? "/audio/1" : SCENARIOS);
        if (kind.equals("AJAX")) request.addHeader("X-Requested-With", "XMLHttpRequest");
        var response = new MockHttpServletResponse();
        fixture
            .filter()
            .doFilter(
                request,
                response,
                (incoming, outgoing) -> {
                  if (kind.equals(ROLE_CASE)) throw new AccessDeniedException(FIXTURE);
                  throw new AuthenticationCredentialsNotFoundException(FIXTURE);
                });
        assertEquals(403, response.getStatus());
        assertNull(response.getHeader(LOCATION));
        assertEquals(0, request.sessionCreates);
        assertEquals(0, request.retainedSession.writes);
        assertTrue(response.getHeaders("Set-Cookie").isEmpty());
        assertAudit(fixture.logger, kind.equals(ROLE_CASE) ? ROLE_CASE : UNAUTHENTICATED);
        assertNull(SecurityContextHolder.getContext().getAuthentication());
      } finally {
        SecurityContextHolder.clearContext();
      }
    }
  }

  @Test
  void ordinaryAndNonsecurityFailureKeepOriginalObjectsAndNeverUseSessionOrAudit()
      throws Exception {
    try (var fixture = new Fixture()) {
      var request = fixture.request("GET", SCENARIOS);
      var response = new MockHttpServletResponse();
      var calls = new ArrayList<String>();
      fixture
          .filter()
          .doFilter(
              request,
              response,
              (incoming, outgoing) -> {
                assertSame(request, incoming);
                assertSame(response, outgoing);
                calls.add("chain");
                response.setStatus(201);
              });
      assertEquals(List.of("chain"), calls);
      assertEquals(201, response.getStatus());
      var original = new IOException(FIXTURE);
      assertSame(
          original,
          assertThrows(
              IOException.class,
              () ->
                  fixture
                      .filter()
                      .doFilter(
                          request,
                          response,
                          (incoming, outgoing) -> {
                            throw original;
                          })));
      assertEquals(0, request.sessionCreates);
      assertEquals(0, request.retainedSession.writes);
      assertTrue(fixture.logger.entries.isEmpty());
    }
  }

  private static void assertAudit(CapturingLogger logger, String reason) {
    assertEquals(1, logger.entries.size());
    var entry = logger.entries.getFirst();
    assertEquals("AUTHORIZATION_DENIED", entry.get("action").getAsString());
    assertEquals("DENIED", entry.get("outcome").getAsString());
    assertEquals(reason, entry.getAsJsonObject("details").get("reason").getAsString());
    assertFalse(entry.has("actorUsername"));
  }

  private static final class Fixture implements AutoCloseable {
    final SecurityContextOwnerPortFixture owners = new SecurityContextOwnerPortFixture();
    final CapturingLogger logger = new CapturingLogger();
    final WebAccessFailureHandler handler =
        new WebAccessFailureHandler(
            new EncryptedSessionRequestCache(owners.sessions()),
            new WebSecurityAudit(
                logger, Clock.fixed(Instant.EPOCH, ZoneOffset.UTC), FIXTURE, FIXTURE));

    ExceptionTranslationFilter filter() {
      var filter = new WebAccessExceptionFilterFactory().create(handler);
      filter.afterPropertiesSet();
      return filter;
    }

    RequestSpy request(String method, String path) {
      var request = new RequestSpy(method, path);
      request.setAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR, owners.sessions());
      request.setAttribute(
          WebRequestContext.ATTRIBUTE,
          new WebRequestContext(new UUID(0, 1), new LoginClientAddress("203.0.113.1")));
      return request;
    }

    @Override
    public void close() {
      owners.close();
    }
  }

  private static final class RequestSpy extends MockHttpServletRequest {
    final SessionSpy retainedSession = new SessionSpy();
    int sessionCreates;
    boolean attached;

    RequestSpy(String method, String path) {
      super(method, path);
      setServletPath(path);
    }

    @Override
    public HttpSession getSession() {
      return Objects.requireNonNull(getSession(true));
    }

    @Override
    public @Nullable HttpSession getSession(boolean create) {
      if (create) {
        sessionCreates++;
        attached = true;
      }
      return attached ? retainedSession : null;
    }
  }

  private static final class SessionSpy extends MockHttpSession {
    int writes;

    SessionSpy() {
      super(new MockServletContext(), FIXTURE);
    }

    @Override
    public void setAttribute(String name, @Nullable Object value) {
      assertEquals(SpringWebSession.SAVED_REQUEST, name);
      assertInstanceOf(String.class, value);
      writes++;
      super.setAttribute(name, value);
    }
  }

  private static final class CapturingLogger implements System.Logger {
    final List<JsonObject> entries = new ArrayList<>();

    @Override
    public String getName() {
      return FIXTURE;
    }

    @Override
    public boolean isLoggable(Level level) {
      return true;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Throwable thrown) {
      assertNull(thrown);
      entries.add(JsonParser.parseString(message).getAsJsonObject());
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String format, Object... parameters) {
      assertTrue(parameters == null || parameters.length == 0);
      entries.add(JsonParser.parseString(format).getAsJsonObject());
    }
  }
}
