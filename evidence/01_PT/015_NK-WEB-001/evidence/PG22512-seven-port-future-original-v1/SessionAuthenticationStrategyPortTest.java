package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SecurityContextOwnerPortFixture;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import java.lang.reflect.Proxy;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.session.SessionAuthenticationException;

/** PT-WEB-SSTRATEGY001..006 / UI226 SS314 7.2.6/331/352. No actual login or session. */
final class SessionAuthenticationStrategyPortTest {
  private static final String REPOSITORY = "org.springframework.session.SessionRepository";
  private static final String OWNER = "owner";
  private static final String SESSION = "session";
  private static final String WRITE = "write";
  private static final String FIXED_FAILURE = "login session is unavailable";
  private static final String PUBLIC_FAILURE = "public-untrusted-diagnostic";
  private SecurityContextOwnerPortFixture owner;
  private EncryptedSessionAuthenticationStrategy strategy;

  @BeforeEach
  void prepare() {
    owner = new SecurityContextOwnerPortFixture();
    strategy =
        new EncryptedSessionAuthenticationStrategy(
            new EncryptedSessionSecurityContextRepository(owner.sessions()));
  }

  @AfterEach
  void eraseOwnCanaryCopies() {
    owner.close();
  }

  @Test
  void constructorAndMethodNullBoundariesDoNotReachAnyCallback() {
    assertThrows(
        NullPointerException.class, () -> new EncryptedSessionAuthenticationStrategy(null));
    var frame = new Frame();
    assertThrows(
        NullPointerException.class,
        () -> strategy.onAuthentication(null, frame.request, frame.response));
    assertThrows(
        NullPointerException.class,
        () -> strategy.onAuthentication(authentication(), null, frame.response));
    assertThrows(
        NullPointerException.class,
        () -> strategy.onAuthentication(authentication(), frame.request, null));
    assertEquals(List.of(), frame.events);
  }

  @Test
  void validClosedAuthenticationDelegatesOnePrincipalWriteWithoutExtraRotation() {
    var frame = new Frame();
    var authentication = authentication();
    strategy.onAuthentication(authentication, frame.request, frame.response);
    assertEquals(List.of(OWNER, SESSION, WRITE), frame.events);
    assertSame(authentication.getPrincipal(), frame.assigned);
  }

  @Test
  void untrustedAuthenticationMapsOnlyClosedSessionFailureToFixedMessage() {
    var frame = new Frame();
    var untrusted = UsernamePasswordAuthenticationToken.unauthenticated(actor(), null);
    assertFixed(
        assertThrows(
            SessionAuthenticationException.class,
            () -> strategy.onAuthentication(untrusted, frame.request, frame.response)));
    assertEquals(List.of(), frame.events);
  }

  @Test
  void missingOwnerSessionAndInvalidSessionMetadataAreMappedWithoutRetry() {
    var wrongOwner = new Frame();
    wrongOwner.configured = new Object();
    var missingSession = new Frame();
    missingSession.sessionPresent = false;
    for (Frame frame : List.of(wrongOwner, missingSession)) {
      assertFixed(
          assertThrows(
              SessionAuthenticationException.class,
              () -> strategy.onAuthentication(authentication(), frame.request, frame.response)));
      assertNull(frame.assigned);
    }
    assertEquals(List.of(OWNER), wrongOwner.events);
    assertEquals(List.of(OWNER, SESSION), missingSession.events);
    for (String stage : List.of(SESSION, WRITE)) {
      for (Throwable failure :
          List.of(
              new IllegalArgumentException(PUBLIC_FAILURE),
              new IllegalStateException(PUBLIC_FAILURE))) {
        var frame = new Frame();
        frame.failedStage = stage;
        frame.failure = failure;
        assertFixed(
            assertThrows(
                SessionAuthenticationException.class,
                () -> strategy.onAuthentication(authentication(), frame.request, frame.response)));
        assertEquals(
            stage.equals(SESSION) ? List.of(OWNER, SESSION) : List.of(OWNER, SESSION, WRITE),
            frame.events);
        assertNull(frame.assigned);
      }
    }
  }

  @Test
  void unrelatedRuntimeAndErrorIdentitiesAreNotCaughtOrCleanedUp() {
    for (String stage : List.of(OWNER, SESSION, WRITE)) {
      for (Throwable failure :
          List.of(
              new UnsupportedOperationException(PUBLIC_FAILURE),
              new AssertionError(PUBLIC_FAILURE))) {
        var frame = new Frame();
        frame.failedStage = stage;
        frame.failure = failure;
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> strategy.onAuthentication(authentication(), frame.request, frame.response)));
        assertEquals(
            List.of(OWNER, SESSION, WRITE)
                .subList(0, List.of(OWNER, SESSION, WRITE).indexOf(stage) + 1),
            frame.events);
        assertNull(frame.assigned);
      }
    }
  }

  @Test
  void concurrentIndependentSuppliedFramesShareNoMutableStrategyState() throws Exception {
    try (var workers = Executors.newFixedThreadPool(2)) {
      var jobs = new ArrayList<java.util.concurrent.Future<?>>();
      for (int index = 0; index < 8; index++)
        jobs.add(
            workers.submit(
                () -> {
                  var frame = new Frame();
                  var authentication = authentication();
                  strategy.onAuthentication(authentication, frame.request, frame.response);
                  assertSame(authentication.getPrincipal(), frame.assigned);
                  assertEquals(List.of(OWNER, SESSION, WRITE), frame.events);
                }));
      for (var job : jobs) job.get();
    }
  }

  private static SessionPrincipal actor() {
    return new SessionPrincipal(
        "public-actor",
        UserRole.ADMIN,
        AuthenticationContext.of("0".repeat(64)),
        Instant.parse("2026-01-01T00:00:00Z"));
  }

  private static Authentication authentication() {
    return ClosedWebAuthentication.authenticated(actor());
  }

  private static void assertFixed(SessionAuthenticationException failure) {
    assertEquals(FIXED_FAILURE, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private final class Frame {
    private final List<String> events = new ArrayList<>();
    private Object configured = owner.sessions();
    private boolean sessionPresent = true;
    private String failedStage = "";
    private Throwable failure;
    private Object assigned;
    private final HttpServletRequest request;
    private final HttpServletResponse response;

    Frame() {
      HttpSession session =
          (HttpSession)
              Proxy.newProxyInstance(
                  HttpSession.class.getClassLoader(),
                  new Class<?>[] {HttpSession.class},
                  (proxy, method, args) -> {
                    assertEquals("setAttribute", method.getName());
                    assertEquals("principal", args[0]);
                    mark(WRITE);
                    assigned = args[1];
                    return null;
                  });
      request =
          (HttpServletRequest)
              Proxy.newProxyInstance(
                  HttpServletRequest.class.getClassLoader(),
                  new Class<?>[] {HttpServletRequest.class},
                  (proxy, method, args) -> {
                    switch (method.getName()) {
                      case "getAttribute" -> {
                        assertEquals(REPOSITORY, args[0]);
                        mark(OWNER);
                        return configured;
                      }
                      case "getSession" -> {
                        assertEquals(Boolean.FALSE, args[0]);
                        mark(SESSION);
                        return sessionPresent ? session : null;
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
                    throw new AssertionError("response must be untouched");
                  });
    }

    private void mark(String stage) throws Throwable {
      events.add(stage);
      if (stage.equals(failedStage)) throw failure;
    }
  }
}
