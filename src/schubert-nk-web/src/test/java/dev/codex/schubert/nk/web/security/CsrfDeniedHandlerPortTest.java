package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.lang.System.Logger;
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
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.authentication.TestingAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;

/** PT-WEB-CSRF403001..008 / UI222226252 SS313314351352. Isolated child JVM ThreadLocal only. */
final class CsrfDeniedHandlerPortTest {
  private static final String MARKER = "public-uninspected-denial-marker";
  private static final String PUBLIC_ACTOR = "public-actor";
  private static final String DISPLAY = WebDisplayContext.class.getName();
  private static final String TOKEN_ATTRIBUTE = CsrfToken.class.getName();
  private static final String STATUS = "status";
  private static final String REMOVE = "remove";
  private static final String AUDIT = "audit";
  private static final String SEND = "send";
  private static final List<String> ORDER = List.of(STATUS, REMOVE, AUDIT, SEND);
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-01-02T03:04:05Z"), ZoneOffset.UTC);

  @BeforeEach
  void ownThreadLocalOnly() {
    assertEquals("MODE_THREADLOCAL", System.getProperty("spring.security.strategy"));
    assertEquals(
        "org.springframework.security.core.context.ThreadLocalSecurityContextHolderStrategy",
        SecurityContextHolder.getContextHolderStrategy().getClass().getName());
    SecurityContextHolder.clearContext();
  }

  @AfterEach
  void clearOnlyChildThreadContext() {
    SecurityContextHolder.clearContext();
  }

  @Test
  void nullBoundariesRejectBeforeRequestResponseOrAuditCallbacks() {
    assertThrows(NullPointerException.class, () -> new WebCsrfDeniedHandler(null));
    var frame = new Frame(1);
    assertThrows(
        NullPointerException.class, () -> frame.handler.handle(null, frame.response, denial()));
    assertThrows(
        NullPointerException.class, () -> frame.handler.handle(frame.request, null, denial()));
    assertThrows(
        NullPointerException.class,
        () -> frame.handler.handle(frame.request, frame.response, null));
    assertEquals(List.of(), frame.events);
    assertTrue(frame.log.rows.isEmpty());
  }

  @Test
  void unauthenticatedDenialReturns403AndOneClosedAuditWithoutInspectingException()
      throws Exception {
    var frame = new Frame(2);
    frame.attributes.put(DISPLAY, new Object());
    frame.handler.handle(frame.request, frame.response, denial());
    assertEquals(ORDER, frame.events);
    assertEquals(403, frame.status);
    assertFalse(frame.attributes.containsKey(DISPLAY));
    assertAudit(frame, null);
  }

  @Test
  void authenticatedDenialWithoutSuppliedCsrfKeepsNoDisplaySnapshot() throws Exception {
    setActor(PUBLIC_ACTOR);
    var frame = new Frame(3);
    frame.attributes.put(DISPLAY, new Object());
    frame.handler.handle(frame.request, frame.response, denial());
    assertEquals(ORDER, frame.events);
    assertFalse(frame.attributes.containsKey(DISPLAY));
    assertAudit(frame, PUBLIC_ACTOR);
  }

  @Test
  void authenticatedSuppliedCsrfCapturesDisplayStringsWithoutLoggingSecretCanary()
      throws Exception {
    setActor(PUBLIC_ACTOR);
    var frame = new Frame(4);
    frame.attributes.put(
        TOKEN_ATTRIBUTE, new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", "A".repeat(64)));
    frame.handler.handle(frame.request, frame.response, denial());
    var snapshot = WebDisplayContext.existing(frame.request).orElseThrow();
    assertEquals("schubert NK", snapshot.topBar().getBrand());
    assertEquals(PUBLIC_ACTOR, snapshot.topBar().getUsername());
    assertEquals("ADMIN", snapshot.topBar().getRole());
    assertEquals("WebDisplayContext[REDACTED]", snapshot.toString());
    assertAudit(frame, PUBLIC_ACTOR);
    assertEquals(ORDER, frame.events);
  }

  @Test
  void missingOrWrongTrustedRequestContextStopsBeforeAnyTerminalCallback() {
    for (Object context : new Object[] {null, new Object()}) {
      var frame = new Frame(5);
      if (context == null) frame.attributes.remove(WebRequestContext.ATTRIBUTE);
      else frame.attributes.put(WebRequestContext.ATTRIBUTE, context);
      assertThrows(
          IllegalStateException.class,
          () -> frame.handler.handle(frame.request, frame.response, denial()));
      assertEquals(List.of(), frame.events);
      assertTrue(frame.log.rows.isEmpty());
    }
  }

  @Test
  void untrustedAuthenticationAndMalformedDisplayInputFailBeforeAudit() {
    SecurityContextHolder.getContext()
        .setAuthentication(new TestingAuthenticationToken(PUBLIC_ACTOR, null));
    var untrusted = new Frame(6);
    assertThrows(
        SessionStoreException.class,
        () -> untrusted.handler.handle(untrusted.request, untrusted.response, denial()));
    assertEquals(List.of(), untrusted.events);
    setActor(PUBLIC_ACTOR);
    for (Object bad :
        List.of(new Object(), new DefaultCsrfToken("X-CSRF-TOKEN", "wrong", "A".repeat(64)))) {
      var frame = new Frame(7);
      frame.attributes.put(TOKEN_ATTRIBUTE, bad);
      assertThrows(
          SessionStoreException.class,
          () -> frame.handler.handle(frame.request, frame.response, denial()));
      assertEquals(List.of(STATUS, REMOVE), frame.events);
      assertTrue(frame.log.rows.isEmpty());
    }
  }

  @Test
  void terminalCallbackFailuresPreserveIdentityAndDoNotRetryOrContinue() {
    for (String stage : ORDER) {
      for (Throwable failure :
          List.of(new IllegalStateException(MARKER), new AssertionError(MARKER))) {
        var frame = new Frame(8);
        frame.failedStage = stage;
        frame.failure = failure;
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> frame.handler.handle(frame.request, frame.response, denial())));
        assertEquals(ORDER.subList(0, ORDER.indexOf(stage) + 1), frame.events);
      }
    }
    var frame = new Frame(9);
    frame.failedStage = SEND;
    frame.failure = new IOException(MARKER);
    assertSame(
        frame.failure,
        assertThrows(
            IOException.class,
            () -> frame.handler.handle(frame.request, frame.response, denial())));
    assertEquals(ORDER, frame.events);
  }

  @Test
  void twoWorkerThreadLocalActorsAndRequestAuditsRemainIndependent() throws Exception {
    try (var workers = Executors.newFixedThreadPool(2)) {
      var jobs = new ArrayList<java.util.concurrent.Future<String>>();
      for (int index = 0; index < 8; index++) {
        int item = index;
        jobs.add(
            workers.submit(
                () -> {
                  try {
                    String name = "public-actor-" + item;
                    setActor(name);
                    var frame = new Frame(100 + item);
                    frame.handler.handle(frame.request, frame.response, denial());
                    assertAudit(frame, name);
                    return frame.id.toString();
                  } finally {
                    SecurityContextHolder.clearContext();
                  }
                }));
      }
      var ids = new HashSet<String>();
      for (var job : jobs) assertTrue(ids.add(job.get()));
      assertEquals(8, ids.size());
    }
    assertNull(SecurityContextHolder.getContext().getAuthentication());
  }

  private static void setActor(String name) {
    var actor =
        new SessionPrincipal(
            name, UserRole.ADMIN, AuthenticationContext.of("0".repeat(64)), CLOCK.instant());
    SecurityContextHolder.getContext()
        .setAuthentication(ClosedWebAuthentication.authenticated(actor));
  }

  private static AccessDeniedException denial() {
    return new AccessDeniedException(MARKER) {
      private static final long serialVersionUID = 1L;

      @Override
      public String getMessage() {
        throw new AssertionError("denial text must not be inspected");
      }

      @Override
      public Throwable getCause() {
        throw new AssertionError("denial cause must not be inspected");
      }
    };
  }

  private static void assertAudit(Frame frame, String actor) {
    assertEquals(1, frame.log.rows.size());
    var row = frame.log.rows.element();
    assertEquals("2026-01-02T03:04:05.000Z", row.get("timestamp").getAsString());
    assertEquals("WARN", row.get("level").getAsString());
    assertEquals("WEB", row.get("service").getAsString());
    assertEquals("pt-public", row.get("appVersion").getAsString());
    assertEquals("pt-config", row.get("configVersion").getAsString());
    assertEquals("SECURITY", row.get("category").getAsString());
    assertEquals("AUTHORIZATION_DENIED", row.get("action").getAsString());
    assertEquals("DENIED", row.get("outcome").getAsString());
    assertEquals(frame.id.toString(), row.get("requestId").getAsString());
    assertEquals("192.0.2.1", row.get("remoteAddress").getAsString());
    assertEquals(
        JsonParser.parseString(
            "{\"reason\":\"CSRF\",\"route\":\"/**\",\"targetType\":\"HTTP_REQUEST\"}"),
        row.get("details"));
    var keys =
        new HashSet<>(
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
                "remoteAddress",
                "details"));
    if (actor != null) {
      keys.add("actorUsername");
      keys.add("actorRole");
      assertEquals(actor, row.get("actorUsername").getAsString());
      assertEquals("ADMIN", row.get("actorRole").getAsString());
    }
    assertEquals(keys, row.keySet());
    assertFalse(row.toString().contains(MARKER));
    assertFalse(row.toString().contains("A".repeat(64)));
    assertFalse(row.toString().contains("0".repeat(64)));
  }

  private static final class MemoryLog implements Logger {
    private final ConcurrentLinkedQueue<JsonObject> rows = new ConcurrentLinkedQueue<>();
    private final Frame owner;

    MemoryLog(Frame owner) {
      this.owner = owner;
    }

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
      throw new AssertionError("Throwable must not reach audit sink");
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Object... parameters) {
      assertEquals(Level.WARNING, level);
      assertNull(bundle);
      assertTrue(parameters == null || parameters.length == 0);
      owner.markAudit();
      rows.add(JsonParser.parseString(message).getAsJsonObject());
    }
  }

  private static final class Frame {
    private final UUID id;
    private final List<String> events = new ArrayList<>();
    private final Map<String, Object> attributes = new HashMap<>();
    private final MemoryLog log = new MemoryLog(this);
    private final WebCsrfDeniedHandler handler =
        new WebCsrfDeniedHandler(new WebSecurityAudit(log, CLOCK, "pt-public", "pt-config"));
    private final HttpServletRequest request;
    private final HttpServletResponse response;
    private String failedStage = "";
    private Throwable failure;
    private int status;

    Frame(long value) {
      id = new UUID(0, value);
      attributes.put(
          WebRequestContext.ATTRIBUTE,
          new WebRequestContext(id, new LoginClientAddress("192.0.2.1")));
      request =
          (HttpServletRequest)
              Proxy.newProxyInstance(
                  HttpServletRequest.class.getClassLoader(),
                  new Class<?>[] {HttpServletRequest.class},
                  (proxy, method, args) -> {
                    switch (method.getName()) {
                      case "getAttribute" -> {
                        return attributes.get(args[0]);
                      }
                      case "removeAttribute" -> {
                        assertEquals(DISPLAY, args[0]);
                        mark(REMOVE);
                        attributes.remove(args[0]);
                        return null;
                      }
                      case "setAttribute" -> {
                        assertEquals(DISPLAY, args[0]);
                        attributes.put((String) args[0], args[1]);
                        return null;
                      }
                      default -> throw new AssertionError("unapproved request operation");
                    }
                  });
      response =
          (HttpServletResponse)
              Proxy.newProxyInstance(
                  HttpServletResponse.class.getClassLoader(),
                  new Class<?>[] {HttpServletResponse.class},
                  (proxy, method, args) -> {
                    assertEquals(403, args[0]);
                    assertEquals(1, args.length);
                    switch (method.getName()) {
                      case "setStatus" -> {
                        mark(STATUS);
                        status = (Integer) args[0];
                        return null;
                      }
                      case "sendError" -> {
                        mark(SEND);
                        return null;
                      }
                      default -> throw new AssertionError("unapproved response operation");
                    }
                  });
    }

    private void markAudit() {
      events.add(AUDIT);
      if (AUDIT.equals(failedStage)) {
        if (failure instanceof RuntimeException runtime) throw runtime;
        if (failure instanceof Error fatal) throw fatal;
        throw new AssertionError("Logger fixture accepts only unchecked failures");
      }
    }

    private void mark(String stage) throws Throwable {
      events.add(stage);
      if (stage.equals(failedStage)) throw failure;
    }
  }
}
