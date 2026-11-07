package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.session.SessionStoreException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;

/** PT-WEB-CSRFPORT001..008 / UI226 SS314 8.1/352. Only owned Servlet interface callbacks. */
final class EncryptedSessionCsrfPortTest {
  private static final String VALUE = "A".repeat(64);
  private static final String OTHER = "B".repeat(64);
  private static final String HEADER = "X-CSRF-TOKEN";
  private static final String PARAMETER = "_csrf";
  private static final String ATTRIBUTE = "csrfToken";
  private static final String BEFORE = "public-before";
  private static final String AFTER = "public-after";
  private static final String READ = "session:false";
  private static final String CREATE = "session:true";
  private static final String ROTATE = "rotate";
  private static final String FAULT = "synthetic callback failure";
  private final EncryptedSessionCsrfTokenRepository repository =
      new EncryptedSessionCsrfTokenRepository();

  @Test
  void generatesFromSuppliedAttributeWithoutRandomnessOrExistingSessionRotation() {
    var created = new Session(AFTER, VALUE);
    var fixture = new Fixture(null, created, AFTER);
    CsrfToken token = repository.generateToken(fixture.request);
    assertEquals(HEADER, token.getHeaderName());
    assertEquals(PARAMETER, token.getParameterName());
    assertEquals(VALUE, token.getToken());
    assertEquals(List.of(READ, CREATE), fixture.events);
    assertEquals(List.of(ATTRIBUTE), created.reads);
    assertFalse(created.invalidated);
  }

  @Test
  void existingSessionRequiresObservedNewIdentityAndUsesOnlyRotatedAttribute() {
    var old = new Session(BEFORE, OTHER);
    var next = new Session(AFTER, VALUE);
    var fixture = new Fixture(old, next, AFTER);
    assertEquals(VALUE, repository.generateToken(fixture.request).getToken());
    assertEquals(List.of(READ, ROTATE, READ, CREATE), fixture.events);
    assertEquals(List.of(), old.reads);
    assertEquals(List.of(ATTRIBUTE), next.reads);
    assertFalse(old.invalidated);
    assertFalse(next.invalidated);
    var same = new Session(BEFORE, VALUE);
    for (Fixture invalid :
        List.of(
            new Fixture(old, next, null),
            new Fixture(old, null, AFTER),
            new Fixture(old, next, "public-unobserved"),
            new Fixture(old, same, BEFORE))) {
      assertThrows(SessionStoreException.class, () -> repository.generateToken(invalid.request));
      assertEquals(List.of(READ, ROTATE, READ), invalid.events);
    }
  }

  @Test
  void loadNeverCreatesSessionAndRejectsMalformedOrNonStringAttributes() {
    var absent = new Fixture(null, null, null);
    assertEquals(null, repository.loadToken(absent.request));
    assertEquals(List.of(READ), absent.events);
    var missing = new Session(AFTER, null);
    assertEquals(null, repository.loadToken(new Fixture(missing, missing, AFTER).request));
    for (Object malformed :
        List.of(Integer.valueOf(1), "", "A".repeat(63), "A".repeat(129), " ".repeat(64))) {
      var session = new Session(AFTER, malformed);
      assertThrows(
          SessionStoreException.class,
          () -> repository.loadToken(new Fixture(session, session, AFTER).request));
      assertFalse(session.invalidated);
    }
    var stored = new Session(AFTER, VALUE);
    var fixture = new Fixture(stored, stored, AFTER);
    assertEquals(VALUE, repository.loadToken(fixture.request).getToken());
    assertEquals(List.of(READ), fixture.events);
  }

  @Test
  void nullSaveInvalidatesOnlySuppliedExistingSessionAndNeverCreatesOne() {
    var session = new Session(AFTER, VALUE);
    var existing = new Fixture(session, session, AFTER);
    repository.saveToken(null, existing.request, existing.response);
    assertTrue(session.invalidated);
    assertEquals(1, session.invalidations);
    assertEquals(List.of(READ), existing.events);
    var missing = new Fixture(null, null, null);
    repository.saveToken(null, missing.request, missing.response);
    assertEquals(List.of(READ), missing.events);
  }

  @Test
  void saveRequiresExactHeaderParameterAndPersistedValueWithoutWritingState() {
    var absent = new Fixture(null, null, null);
    assertThrows(
        SessionStoreException.class,
        () ->
            repository.saveToken(token(HEADER, PARAMETER, VALUE), absent.request, absent.response));
    for (CsrfToken invalid :
        List.of(
            token("wrong-header", PARAMETER, VALUE),
            token(HEADER, "wrong-parameter", VALUE),
            token(HEADER, PARAMETER, OTHER),
            token(HEADER, PARAMETER, "bad"))) {
      var session = new Session(AFTER, VALUE);
      var fixture = new Fixture(session, session, AFTER);
      assertThrows(
          SessionStoreException.class,
          () -> repository.saveToken(invalid, fixture.request, fixture.response));
      assertFalse(session.invalidated);
      assertEquals(List.of(READ), fixture.events);
    }
    var session = new Session(AFTER, VALUE);
    var fixture = new Fixture(session, session, AFTER);
    repository.saveToken(token(HEADER, PARAMETER, VALUE), fixture.request, fixture.response);
    assertFalse(session.invalidated);
    assertEquals(VALUE, session.attribute);
    assertEquals(List.of(ATTRIBUTE), session.reads);
    assertEquals(List.of(READ), fixture.events);
  }

  @Test
  void nullBoundariesAndMissingGeneratedAttributeHaveExplicitFailureSignals() {
    var fixture = new Fixture(null, null, null);
    assertThrows(NullPointerException.class, () -> repository.generateToken(null));
    assertThrows(NullPointerException.class, () -> repository.loadToken(null));
    assertThrows(
        NullPointerException.class, () -> repository.saveToken(null, null, fixture.response));
    assertThrows(
        NullPointerException.class, () -> repository.saveToken(null, fixture.request, null));
    assertThrows(NullPointerException.class, () -> repository.generateToken(fixture.request));
    var absent = new Session(AFTER, null);
    assertThrows(
        SessionStoreException.class,
        () -> repository.generateToken(new Fixture(null, absent, AFTER).request));
  }

  @Test
  void callbackFailuresPreserveIdentityWithoutRetryOrCleanupAuthority() {
    for (Throwable failure : List.of(new IllegalStateException(FAULT), new AssertionError(FAULT))) {
      var session = new Session(AFTER, VALUE);
      var fixture = new Fixture(session, session, AFTER);
      fixture.failure = failure;
      assertSame(
          failure,
          assertThrows(failure.getClass(), () -> repository.generateToken(fixture.request)));
      assertEquals(List.of(READ), fixture.events);
      assertFalse(session.invalidated);
      session.failure = failure;
      assertSame(
          failure,
          assertThrows(
              failure.getClass(),
              () -> repository.loadToken(new Fixture(session, session, AFTER).request)));
      assertFalse(session.invalidated);
    }
  }

  @Test
  void concurrentSuppliedFramesKeepMaterializedValuesAndCallbacksSeparate() throws Exception {
    try (var workers = Executors.newFixedThreadPool(2)) {
      var jobs = new ArrayList<java.util.concurrent.Future<String>>();
      for (int index = 0; index < 8; index++) {
        String expected = index % 2 == 0 ? VALUE : OTHER;
        jobs.add(
            workers.submit(
                () -> {
                  var session = new Session(AFTER, expected);
                  var fixture = new Fixture(null, session, AFTER);
                  var token = repository.generateToken(fixture.request);
                  repository.saveToken(
                      token, new Fixture(session, session, AFTER).request, fixture.response);
                  assertEquals(List.of(READ, CREATE), fixture.events);
                  assertFalse(session.invalidated);
                  return token.getToken();
                }));
      }
      for (int index = 0; index < jobs.size(); index++)
        assertEquals(
            index % 2 == 0 ? VALUE : OTHER,
            jobs.get(index).get(10, java.util.concurrent.TimeUnit.SECONDS));
    }
  }

  private static CsrfToken token(String header, String parameter, String value) {
    return new DefaultCsrfToken(header, parameter, value);
  }

  private static final class Session {
    private final String id;
    private final Object attribute;
    private final List<String> reads = new ArrayList<>();
    private final HttpSession port;
    private boolean invalidated;
    private int invalidations;
    private Throwable failure;

    Session(String id, Object attribute) {
      this.id = id;
      this.attribute = attribute;
      port =
          (HttpSession)
              Proxy.newProxyInstance(
                  HttpSession.class.getClassLoader(),
                  new Class<?>[] {HttpSession.class},
                  (proxy, method, args) -> {
                    if (failure != null) throw failure;
                    return switch (method.getName()) {
                      case "getId" -> this.id;
                      case "getAttribute" -> {
                        assertNotNull(args);
                        assertEquals(ATTRIBUTE, args[0]);
                        reads.add((String) args[0]);
                        yield this.attribute;
                      }
                      case "invalidate" -> {
                        invalidated = true;
                        invalidations++;
                        yield null;
                      }
                      default ->
                          throw new AssertionError(
                              "unapproved session operation: " + method.getName());
                    };
                  });
    }
  }

  private static final class Fixture {
    private final List<String> events = new ArrayList<>();
    private final HttpServletRequest request;
    private final HttpServletResponse response;
    private Session current;
    private Throwable failure;

    Fixture(Session current, Session next, String returnedId) {
      this.current = current;
      request =
          (HttpServletRequest)
              Proxy.newProxyInstance(
                  HttpServletRequest.class.getClassLoader(),
                  new Class<?>[] {HttpServletRequest.class},
                  (proxy, method, args) -> {
                    switch (method.getName()) {
                      case "getSession" -> {
                        assertNotNull(args);
                        boolean create = (Boolean) args[0];
                        events.add(create ? CREATE : READ);
                        if (failure != null) throw failure;
                        if (create && this.current == null) this.current = next;
                        return this.current == null ? null : this.current.port;
                      }
                      case "changeSessionId" -> {
                        events.add(ROTATE);
                        this.current = next;
                        return returnedId;
                      }
                      default ->
                          throw new AssertionError(
                              "unapproved request operation: " + method.getName());
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
