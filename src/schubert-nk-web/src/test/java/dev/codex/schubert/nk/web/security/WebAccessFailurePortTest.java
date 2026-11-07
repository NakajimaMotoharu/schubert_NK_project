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
import dev.codex.schubert.nk.web.session.SecurityContextOwnerPortFixture;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import jakarta.servlet.http.HttpSession;
import java.io.IOException;
import java.lang.System.Logger;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.ResourceBundle;
import java.util.UUID;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.session.web.http.SessionRepositoryFilter;

/** PT-WEB-ACCESSPORT001..006; SS314351. Own heap ports and empty ThreadLocal, no auth grant. */
final class WebAccessFailurePortTest {
  private static final String STATUS403 = "status403";
  private static final String STATUS302 = "status302";
  private static final String SAVE = "save";
  private static final String AUDIT = "audit";
  private static final String HEADER = "header";
  private static final String SEND403 = "send403";
  private static final String LOCATION_HEADER = "Location";
  private static final String GET = "GET";
  private static final String POST = "POST";
  private static final String PATH = "/scenarios";
  private static final String FIXTURE = "public-local-failure";
  private static final String SAVED = "savedRequest";
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-01-02T03:04:05Z"), ZoneOffset.UTC);
  private static final UUID ID = new UUID(0, 42);

  @BeforeEach
  void emptyOwnedThreadContext() {
    assertEquals("MODE_THREADLOCAL", System.getProperty("spring.security.strategy"));
    SecurityContextHolder.clearContext();
  }

  @AfterEach
  void clearOnlyOwnedThreadContext() {
    SecurityContextHolder.clearContext();
  }

  @Test
  void constructorAndAllNullArgumentsRejectBeforeCallbacks() {
    try (var f = new Frame(GET, PATH)) {
      assertThrows(NullPointerException.class, () -> new WebAccessFailureHandler(null, f.audit));
      assertThrows(NullPointerException.class, () -> new WebAccessFailureHandler(f.cache, null));
      assertThrows(
          NullPointerException.class, () -> f.handler.commence(null, f.response, required()));
      assertThrows(
          NullPointerException.class, () -> f.handler.commence(f.request, null, required()));
      assertThrows(
          NullPointerException.class, () -> f.handler.commence(f.request, f.response, null));
      assertThrows(NullPointerException.class, () -> f.handler.handle(null, f.response, denied()));
      assertThrows(NullPointerException.class, () -> f.handler.handle(f.request, null, denied()));
      assertThrows(NullPointerException.class, () -> f.handler.handle(f.request, f.response, null));
      assertTrue(f.events.isEmpty());
      assertTrue(f.logger.entries.isEmpty());
      assertEquals(0, f.request.sessionLookups);
    }
  }

  @Test
  void navigationSavesOneStringThenAuditsThenRedirects() throws Exception {
    try (var f = new Frame(GET, PATH)) {
      f.request.setQueryString("page=2");
      assertTrue(WebAccessFailureHandler.isNavigation(f.request));
      f.handler.commence(f.request, f.response, required());
      assertEquals(List.of(STATUS403, SAVE, AUDIT, HEADER, STATUS302), f.events);
      assertEquals(302, f.response.getStatus());
      assertEquals("/login", f.response.getHeader(LOCATION_HEADER));
      assertEquals("/scenarios?page=2", f.request.session.getAttribute(SAVED));
      assertEquals(1, f.request.session.writes);
      assertEquals(1, f.request.sessionLookups);
      assertAudit(f, "UNAUTHENTICATED");
    }
  }

  @Test
  void postHeadAjaxAndEveryMediaPrefixAreDeniedWithoutSessionOrRedirect() throws Exception {
    for (String[] vector :
        List.of(
            new String[] {POST, PATH, ""},
            new String[] {"HEAD", PATH, ""},
            new String[] {GET, PATH, "xmlhttprequest"},
            new String[] {GET, "/audio/7", ""},
            new String[] {GET, "/animation/media/7", ""},
            new String[] {GET, "/music/media/7", ""},
            new String[] {GET, "/music/download/7", ""})) {
      try (var f = new Frame(vector[0], vector[1])) {
        if (!vector[2].isEmpty()) f.request.addHeader("X-Requested-With", vector[2]);
        assertFalse(WebAccessFailureHandler.isNavigation(f.request));
        f.handler.commence(f.request, f.response, required());
        assertEquals(List.of(STATUS403, AUDIT, SEND403), f.events);
        assertEquals(403, f.response.getStatus());
        assertNull(f.response.getHeader(LOCATION_HEADER));
        assertEquals(0, f.request.sessionLookups);
        assertEquals(0, f.request.session.writes);
        assertAudit(f, "UNAUTHENTICATED");
      }
    }
  }

  @Test
  void emptyContextAccessDenialIsOneRoleAuditAnd403WithoutSaving() throws Exception {
    for (String method : List.of(GET, POST)) {
      try (var f = new Frame(method, PATH)) {
        f.handler.handle(f.request, f.response, denied());
        assertEquals(List.of(STATUS403, AUDIT, SEND403), f.events);
        assertEquals(403, f.response.getStatus());
        assertNull(f.response.getHeader(LOCATION_HEADER));
        assertEquals(0, f.request.sessionLookups);
        assertAudit(f, "ROLE");
        assertNull(SecurityContextHolder.getContext().getAuthentication());
      }
    }
  }

  @Test
  void missingOrForeignContextAndWrongCacheOwnerFailBeforeLaterEffects() {
    for (boolean foreign : new boolean[] {false, true}) {
      try (var f = new Frame(GET, PATH)) {
        f.request.removeAttribute(WebRequestContext.ATTRIBUTE);
        if (foreign) f.request.setAttribute(WebRequestContext.ATTRIBUTE, new Object());
        assertThrows(
            IllegalStateException.class,
            () -> f.handler.commence(f.request, f.response, required()));
        assertThrows(
            IllegalStateException.class, () -> f.handler.handle(f.request, f.response, denied()));
        assertTrue(f.events.isEmpty());
        assertEquals(0, f.request.sessionLookups);
      }
    }
    try (var f = new Frame(GET, PATH)) {
      f.request.removeAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR);
      assertThrows(
          SessionStoreException.class, () -> f.handler.commence(f.request, f.response, required()));
      assertEquals(List.of(STATUS403), f.events);
      assertTrue(f.logger.entries.isEmpty());
      assertNull(f.response.getHeader(LOCATION_HEADER));
      assertEquals(0, f.request.sessionLookups);
    }
  }

  @Test
  void auditAndResponseFailuresPreserveIdentityWithoutRetryOrSuccessfulRedirect() {
    for (String method : List.of(GET, POST)) {
      try (var f = new Frame(method, PATH)) {
        var failure = new IllegalStateException(FIXTURE);
        f.logger.failure = failure;
        assertSame(
            failure,
            assertThrows(
                IllegalStateException.class,
                () -> f.handler.commence(f.request, f.response, required())));
        assertEquals(
            GET.equals(method) ? List.of(STATUS403, SAVE, AUDIT) : List.of(STATUS403, AUDIT),
            f.events);
        assertEquals(403, f.response.getStatus());
        assertNull(f.response.getHeader(LOCATION_HEADER));
        assertTrue(f.logger.entries.isEmpty());
      }
    }
    for (boolean role : new boolean[] {false, true}) {
      try (var f = new Frame(POST, PATH)) {
        var failure = new IOException(FIXTURE);
        f.response.sendFailure = failure;
        assertSame(
            failure,
            assertThrows(
                IOException.class,
                () -> {
                  if (role) f.handler.handle(f.request, f.response, denied());
                  else f.handler.commence(f.request, f.response, required());
                }));
        assertEquals(List.of(STATUS403, AUDIT, SEND403), f.events);
        assertEquals(1, f.logger.entries.size());
      }
    }
    try (var f = new Frame(GET, PATH)) {
      var failure = new IllegalArgumentException(FIXTURE);
      f.response.headerFailure = failure;
      assertSame(
          failure,
          assertThrows(
              IllegalArgumentException.class,
              () -> f.handler.commence(f.request, f.response, required())));
      assertEquals(List.of(STATUS403, SAVE, AUDIT, HEADER), f.events);
      assertEquals(403, f.response.getStatus());
      assertNull(f.response.getHeader(LOCATION_HEADER));
      assertEquals(1, f.logger.entries.size());
    }
  }

  private static void assertAudit(Frame f, String reason) {
    assertEquals(1, f.logger.entries.size());
    var json = f.logger.entries.getFirst();
    assertEquals("AUTHORIZATION_DENIED", json.get("action").getAsString());
    assertEquals("DENIED", json.get("outcome").getAsString());
    assertEquals(reason, json.getAsJsonObject("details").get("reason").getAsString());
    assertEquals(ID.toString(), json.get("requestId").getAsString());
    assertFalse(json.has("actorUsername"));
  }

  private static AuthenticationException required() {
    return new AuthenticationException(FIXTURE) {
      private static final long serialVersionUID = 1L;
    };
  }

  private static AccessDeniedException denied() {
    return new AccessDeniedException(FIXTURE);
  }

  private static final class Frame implements AutoCloseable {
    final List<String> events = new ArrayList<>();
    final SecurityContextOwnerPortFixture owner = new SecurityContextOwnerPortFixture();
    final AuditLog logger = new AuditLog(events);
    final WebSecurityAudit audit = new WebSecurityAudit(logger, CLOCK, "pt", "pt");
    final EncryptedSessionRequestCache cache = new EncryptedSessionRequestCache(owner.sessions());
    final WebAccessFailureHandler handler = new WebAccessFailureHandler(cache, audit);
    final Request request;
    final Response response = new Response(events);

    Frame(String method, String path) {
      request = new Request(method, path, events);
      request.setAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR, owner.sessions());
      request.setAttribute(
          WebRequestContext.ATTRIBUTE,
          new WebRequestContext(ID, new LoginClientAddress("192.0.2.20")));
    }

    @Override
    public void close() {
      owner.close();
    }
  }

  private static final class Request extends MockHttpServletRequest {
    final Session session;
    int sessionLookups;

    Request(String method, String path, List<String> events) {
      super(method, path);
      setServletPath(path);
      session = new Session(events);
    }

    @Override
    public HttpSession getSession() {
      return getSession(true);
    }

    @Override
    public HttpSession getSession(boolean create) {
      sessionLookups++;
      assertTrue(create);
      return session;
    }
  }

  private static final class Session extends MockHttpSession {
    final List<String> events;
    int writes;

    Session(List<String> events) {
      super(null, "public-access-fixture");
      this.events = events;
    }

    @Override
    public void setAttribute(String name, @Nullable Object value) {
      assertEquals(SAVED, name);
      assertTrue(value instanceof String);
      writes++;
      events.add(SAVE);
      super.setAttribute(name, value);
    }
  }

  private static final class Response extends MockHttpServletResponse {
    final List<String> events;
    @Nullable IOException sendFailure;
    @Nullable RuntimeException headerFailure;

    Response(List<String> events) {
      this.events = events;
    }

    @Override
    public void setStatus(int status) {
      events.add("status" + status);
      super.setStatus(status);
    }

    @Override
    public void sendError(int status) throws IOException {
      events.add("send" + status);
      if (sendFailure != null) throw sendFailure;
      super.sendError(status);
    }

    @Override
    public void setHeader(String name, String value) {
      assertEquals(LOCATION_HEADER, name);
      events.add(HEADER);
      if (headerFailure != null) throw headerFailure;
      super.setHeader(name, value);
    }
  }

  private static final class AuditLog implements Logger {
    final List<String> events;
    final List<JsonObject> entries = new ArrayList<>();
    @Nullable RuntimeException failure;

    AuditLog(List<String> events) {
      this.events = events;
    }

    @Override
    public String getName() {
      return "own-access-audit";
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
      events.add(AUDIT);
      if (failure != null) throw failure;
      entries.add(JsonParser.parseString(message).getAsJsonObject());
    }
  }
}
