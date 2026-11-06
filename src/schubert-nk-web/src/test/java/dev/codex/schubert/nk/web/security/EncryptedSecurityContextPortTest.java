package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SecurityContextOwnerPortFixture;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
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
import org.springframework.security.core.context.SecurityContextImpl;
import org.springframework.security.web.context.HttpRequestResponseHolder;

/** PT-WEB-SCTXPORT001..012 / UI226 SS314 7.2.6/352. Own interfaces, no actual session/DB. */
final class EncryptedSecurityContextPortTest {
  private static final String BAD_METADATA = "public bad";
  private static final String REPOSITORY = "org.springframework.session.SessionRepository";
  private static final String PRINCIPAL = "principal";
  private static final String FIXED_FAILURE = "session storage is unavailable";
  private SecurityContextOwnerPortFixture owner;
  private EncryptedSessionSecurityContextRepository repository;

  @BeforeEach
  void prepareOwnerIdentity() {
    owner = new SecurityContextOwnerPortFixture();
    repository = new EncryptedSessionSecurityContextRepository(owner.sessions());
  }

  @AfterEach
  void eraseOnlyOwnCanaryCopies() {
    owner.close();
  }

  @Test
  void nonnullBoundariesRejectBeforeAnySessionCallback() {
    var frame = new Frame(null);
    assertThrows(
        NullPointerException.class, () -> new EncryptedSessionSecurityContextRepository(null));
    assertThrows(NullPointerException.class, () -> repository.containsContext(null));
    assertThrows(NullPointerException.class, () -> repository.loadDeferredContext(null));
    assertThrows(
        NullPointerException.class,
        () -> repository.saveContext(null, frame.request, frame.response));
    assertThrows(
        NullPointerException.class,
        () -> repository.saveContext(new SecurityContextImpl(), null, frame.response));
    assertThrows(
        NullPointerException.class,
        () -> repository.saveContext(new SecurityContextImpl(), frame.request, null));
    assertThrows(
        NullPointerException.class, () -> repository.fixate(authentication(actor()), null));
    assertEquals(0, frame.sessionReads);
  }

  @Test
  void requiresExactConfiguredOwnerBeforeLazyOrImmediateReads() {
    for (Object wrong : new Object[] {null, new Object()}) {
      var frame = new Frame(null);
      frame.configured = wrong;
      assertThrows(
          SessionStoreException.class, () -> repository.loadDeferredContext(frame.request));
      assertThrows(SessionStoreException.class, () -> repository.containsContext(frame.request));
      assertThrows(
          SessionStoreException.class,
          () -> repository.saveContext(new SecurityContextImpl(), frame.request, frame.response));
      assertThrows(
          SessionStoreException.class,
          () -> repository.fixate(authentication(actor()), frame.request));
      assertEquals(0, frame.sessionReads);
    }
  }

  @Test
  void emptyDeferredFrameIsLazyStableAndNeverCreatesSession() {
    var frame = new Frame(null);
    var deferred = repository.loadDeferredContext(frame.request);
    assertEquals(0, frame.sessionReads);
    assertTrue(deferred.isGenerated());
    var context = deferred.get();
    assertNull(context.getAuthentication());
    frame.session = new Session(actor());
    assertSame(context, deferred.get());
    assertTrue(deferred.isGenerated());
    assertEquals(1, frame.sessionReads);
  }

  @Test
  void principalDeferredFrameUsesInitialClosedIdentityAndOneRead() {
    var principal = actor();
    var session = new Session(principal);
    var frame = new Frame(session);
    var deferred = repository.loadDeferredContext(frame.request);
    var context = deferred.get();
    assertFalse(deferred.isGenerated());
    assertSame(principal, context.getAuthentication().getPrincipal());
    assertNull(context.getAuthentication().getCredentials());
    assertEquals(
        List.of("ROLE_ADMIN"),
        context.getAuthentication().getAuthorities().stream().map(a -> a.getAuthority()).toList());
    session.value = "now-invalid";
    assertSame(context, deferred.get());
    assertEquals(1, frame.sessionReads);
    assertEquals(1, session.reads);
  }

  @Test
  void containsDistinguishesAbsentMissingWrongTypeAndValidPrincipal() {
    assertFalse(repository.containsContext(new Frame(null).request));
    assertFalse(repository.containsContext(new Frame(new Session(null)).request));
    assertThrows(
        SessionStoreException.class,
        () -> repository.containsContext(new Frame(new Session("untrusted")).request));
    assertTrue(repository.containsContext(new Frame(new Session(actor())).request));
  }

  @Test
  void storedMetadataArgumentAndStateFailuresUseFixedNonSensitiveSignal() {
    for (RuntimeException failure :
        List.of(
            new IllegalArgumentException(BAD_METADATA), new IllegalStateException(BAD_METADATA))) {
      var frame = new Frame(new Session(actor()));
      frame.readFailure = failure;
      var caught =
          assertThrows(
              SessionStoreException.class, () -> repository.containsContext(frame.request));
      assertEquals(FIXED_FAILURE, caught.getMessage());
      assertNull(caught.getCause());
      frame.readFailure = null;
      frame.session.failure = failure;
      assertEquals(
          FIXED_FAILURE,
          assertThrows(SessionStoreException.class, () -> repository.containsContext(frame.request))
              .getMessage());
    }
  }

  @Test
  void saveAcceptsEqualClosedIdentityAndEmptyOnlyWithoutStoredPrincipal() {
    var session = new Session(actor());
    var frame = new Frame(session);
    var equivalent =
        new SessionPrincipal(
            "public-actor",
            UserRole.ADMIN,
            AuthenticationContext.of("0".repeat(64)),
            Instant.parse("2026-01-01T00:00:00Z"));
    repository.saveContext(
        new SecurityContextImpl(authentication(equivalent)), frame.request, frame.response);
    assertEquals(0, session.writes);
    assertEquals(actor(), session.value);
    var absent = new Frame(null);
    repository.saveContext(new SecurityContextImpl(), absent.request, absent.response);
    assertEquals(1, absent.sessionReads);
  }

  @Test
  void saveRejectsChangedOrRemovedPrincipalWithoutMutationOrInvalidation() {
    var session = new Session(actor());
    var frame = new Frame(session);
    assertThrows(
        SessionStoreException.class,
        () -> repository.saveContext(new SecurityContextImpl(), frame.request, frame.response));
    var changed =
        new SessionPrincipal(
            "public-other", UserRole.ADMIN, actor().authenticationContext(), actor().loginAt());
    assertThrows(
        SessionStoreException.class,
        () ->
            repository.saveContext(
                new SecurityContextImpl(authentication(changed)), frame.request, frame.response));
    assertThrows(
        SessionStoreException.class,
        () ->
            repository.saveContext(
                new SecurityContextImpl(authentication(actor())),
                new Frame(null).request,
                frame.response));
    assertEquals(0, session.writes);
    assertEquals(actor(), session.value);
  }

  @Test
  void fixateWritesPrincipalExactlyOnceOnlyInSuppliedExistingSession() {
    var principal = actor();
    var session = new Session(null);
    var frame = new Frame(session);
    repository.fixate(authentication(principal), frame.request);
    assertSame(principal, session.value);
    assertEquals(1, session.writes);
    assertEquals(0, session.reads);
    assertThrows(SessionStoreException.class, () -> repository.fixate(null, frame.request));
    assertThrows(
        SessionStoreException.class,
        () -> repository.fixate(authentication(principal), new Frame(null).request));
    for (RuntimeException failure :
        List.of(
            new IllegalArgumentException(BAD_METADATA), new IllegalStateException(BAD_METADATA))) {
      var invalid = new Frame(new Session(null));
      invalid.session.failure = failure;
      assertThrows(
          SessionStoreException.class,
          () -> repository.fixate(authentication(principal), invalid.request));
    }
  }

  @SuppressWarnings("deprecation") // Required7.1.1 compatibility method, not a quality exclusion.
  @Test
  void compatibilityLoadDelegatesToFreshDeferredContext() {
    var frame = new Frame(new Session(actor()));
    var holder = new HttpRequestResponseHolder(frame.request, frame.response);
    var first = repository.loadContext(holder);
    var second = repository.loadContext(holder);
    assertEquals(actor(), first.getAuthentication().getPrincipal());
    assertNotSame(first, second);
    assertEquals(2, frame.sessionReads);
    assertThrows(NullPointerException.class, () -> repository.loadContext(null));
  }

  @Test
  void failedInitialReadUnlocksAndNeverCachesPartialContext() {
    var frame = new Frame(new Session(actor()));
    var deferred = repository.loadDeferredContext(frame.request);
    frame.readFailure = new IllegalStateException("public unavailable");
    assertThrows(SessionStoreException.class, deferred::get);
    frame.readFailure = null;
    assertFalse(deferred.isGenerated());
    assertEquals(actor(), deferred.get().getAuthentication().getPrincipal());
    assertEquals(2, frame.sessionReads);
  }

  @Test
  void concurrentSharedDeferredAndSeparateRequestCachesRemainOwned() throws Exception {
    var frame = new Frame(new Session(actor()));
    var deferred = repository.loadDeferredContext(frame.request);
    try (var workers = Executors.newFixedThreadPool(2)) {
      var jobs =
          new ArrayList<
              java.util.concurrent.Future<
                  org.springframework.security.core.context.SecurityContext>>();
      for (int index = 0; index < 16; index++) jobs.add(workers.submit(deferred::get));
      var expected = jobs.getFirst().get();
      for (var job : jobs) assertSame(expected, job.get());
      assertEquals(actor(), expected.getAuthentication().getPrincipal());
    }
    assertEquals(1, frame.sessionReads);
    var missing = repository.loadDeferredContext(new Frame(null).request);
    assertTrue(missing.isGenerated());
    assertNull(missing.get().getAuthentication());
    assertFalse(deferred.isGenerated());
  }

  private static SessionPrincipal actor() {
    return new SessionPrincipal(
        "public-actor",
        UserRole.ADMIN,
        AuthenticationContext.of("0".repeat(64)),
        Instant.parse("2026-01-01T00:00:00Z"));
  }

  private static org.springframework.security.core.Authentication authentication(
      SessionPrincipal value) {
    return ClosedWebAuthentication.authenticated(value);
  }

  private static final class Session {
    private Object value;
    private int reads;
    private int writes;
    private RuntimeException failure;
    private final HttpSession port;

    Session(Object value) {
      this.value = value;
      port =
          (HttpSession)
              Proxy.newProxyInstance(
                  HttpSession.class.getClassLoader(),
                  new Class<?>[] {HttpSession.class},
                  (proxy, method, args) -> {
                    if (failure != null) throw failure;
                    assertEquals(PRINCIPAL, args[0]);
                    switch (method.getName()) {
                      case "getAttribute" -> {
                        reads++;
                        return this.value;
                      }
                      case "setAttribute" -> {
                        writes++;
                        this.value = args[1];
                        return null;
                      }
                      default -> throw new AssertionError("unapproved session operation");
                    }
                  });
    }
  }

  private final class Frame {
    private Object configured = owner.sessions();
    private Session session;
    private int sessionReads;
    private RuntimeException readFailure;
    private final HttpServletRequest request;
    private final HttpServletResponse response;

    Frame(Session session) {
      this.session = session;
      request =
          (HttpServletRequest)
              Proxy.newProxyInstance(
                  HttpServletRequest.class.getClassLoader(),
                  new Class<?>[] {HttpServletRequest.class},
                  (proxy, method, args) -> {
                    switch (method.getName()) {
                      case "getAttribute" -> {
                        assertEquals(REPOSITORY, args[0]);
                        return configured;
                      }
                      case "getSession" -> {
                        assertEquals(Boolean.FALSE, args[0]);
                        sessionReads++;
                        if (readFailure != null) throw readFailure;
                        return this.session == null ? null : this.session.port;
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
  }
}
