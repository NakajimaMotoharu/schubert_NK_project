package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.security.Principal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;

/** WEB-DISPLAY-PORT-001..012; SS313SSC047, request-only memory snapshot/filter, no real session. */
final class DisplaySnapshotPortTest {
  private static final String PRINCIPAL_CALL = "principal";
  private static final String UNRELATED = "unrelated";
  private static final String KEEP = "keep";

  private static final String DISPLAY = WebDisplayContext.class.getName();
  private static final String TOKEN = CsrfToken.class.getName();
  private static final String ALIAS = "_csrf";
  private static final String HEADER = "X-CSRF-TOKEN";
  private static final String VIEWER = "public-view";
  private static final String PUBLIC_FAULT = "public fixture";
  private static final String DUMMY = HexFormat.of().formatHex(new byte[32]);
  private static final WebDisplayContextFilter FILTER = new WebDisplayContextFilter();

  @Test
  void closedPrincipalAndParsedCsrfCreateOnlyImmutableDisplayData() {
    for (UserRole role : List.of(UserRole.USER, UserRole.ADMIN)) {
      Fixture f = new Fixture();
      f.principal = actor(role);
      f.token(DUMMY);
      WebDisplayContext.capture(f.request);
      var snapshot = WebDisplayContext.existing(f.request).orElseThrow();
      assertEquals("WebDisplayContext[REDACTED]", snapshot.toString());
      assertEquals("schubert NK", snapshot.topBar().getBrand());
      assertEquals(VIEWER, snapshot.topBar().getUsername());
      assertEquals(role == UserRole.USER ? "USER" : "ADMIN", snapshot.topBar().getRole());
      f.principal = null;
      f.attributes.remove(TOKEN);
      assertEquals(VIEWER, snapshot.topBar().getUsername());
    }
  }

  @Test
  void anonymousCaptureClearsPriorSnapshotWithoutReadingTokenProperties() {
    Fixture f = captured();
    f.principal = null;
    f.attributes.put(TOKEN, new ThrowingToken(new AssertionError("anonymous token must not read")));
    WebDisplayContext.capture(f.request);
    assertTrue(WebDisplayContext.existing(f.request).isEmpty());
  }

  @Test
  void foreignPrincipalMissingTokenWrongTypeAndParameterNeverCreateSnapshot() {
    Fixture foreign = new Fixture();
    foreign.principal =
        () -> {
          throw new AssertionError("untrusted name must not read");
        };
    storeFailure(() -> WebDisplayContext.capture(foreign.request));
    assertTrue(WebDisplayContext.existing(foreign.request).isEmpty());
    for (Object token :
        Arrays.asList(
            null, "public fixture object", new Token("wrong", DUMMY), new Token(null, DUMMY))) {
      Fixture f = new Fixture();
      f.principal = actor(UserRole.USER);
      f.attributes.put(TOKEN, token);
      storeFailure(() -> WebDisplayContext.capture(f.request));
      assertTrue(WebDisplayContext.existing(f.request).isEmpty());
    }
  }

  @Test
  void deniedCaptureClearsOldSnapshotAndUsesOnlyExplicitActorWhenTokenPresent() {
    Fixture empty = captured();
    WebDisplayContext.captureDenied(empty.request, Optional.empty());
    assertTrue(WebDisplayContext.existing(empty.request).isEmpty());
    Fixture absent = captured();
    absent.attributes.remove(TOKEN);
    WebDisplayContext.captureDenied(absent.request, Optional.of(actor(UserRole.USER)));
    assertTrue(WebDisplayContext.existing(absent.request).isEmpty());
    Fixture present = new Fixture();
    present.token(DUMMY);
    present.faults.put(
        PRINCIPAL_CALL, new AssertionError("denied capture must use explicit actor"));
    WebDisplayContext.captureDenied(present.request, Optional.of(actor(UserRole.ADMIN)));
    assertEquals(
        "ADMIN", WebDisplayContext.existing(present.request).orElseThrow().topBar().getRole());
    Fixture invalid = captured();
    invalid.attributes.put(TOKEN, PUBLIC_FAULT);
    storeFailure(
        () -> WebDisplayContext.captureDenied(invalid.request, Optional.of(actor(UserRole.USER))));
    assertTrue(WebDisplayContext.existing(invalid.request).isEmpty());
  }

  @Test
  void allNullEntriesAndMistypedExistingContextAreExplicitFailures() {
    Fixture f = new Fixture();
    assertThrows(NullPointerException.class, () -> WebDisplayContext.capture(null));
    assertThrows(
        NullPointerException.class, () -> WebDisplayContext.captureDenied(null, Optional.empty()));
    assertThrows(
        NullPointerException.class, () -> WebDisplayContext.captureDenied(f.request, null));
    assertThrows(NullPointerException.class, () -> WebDisplayContext.existing(null));
    assertThrows(NullPointerException.class, () -> WebDisplayContext.clear(null));
    assertThrows(NullPointerException.class, () -> WebDisplayContext.restore(null));
    assertEquals(Optional.empty(), WebDisplayContext.existing(f.request));
    f.attributes.put(DISPLAY, PUBLIC_FAULT);
    storeFailure(() -> WebDisplayContext.existing(f.request));
    storeFailure(() -> WebDisplayContext.restore(f.request));
  }

  @Test
  void clearRemovesExactlyDisplayAndBothCsrfAliasesAndIsIdempotent() {
    Fixture f = captured();
    f.attributes.put(ALIAS, PUBLIC_FAULT);
    f.attributes.put(UNRELATED, KEEP);
    WebDisplayContext.clear(f.request);
    assertEquals(Map.of(UNRELATED, KEEP), f.attributes);
    WebDisplayContext.clear(f.request);
    assertEquals(Map.of(UNRELATED, KEEP), f.attributes);
  }

  @Test
  void restoreWithoutSnapshotRemovesForeignTokensAndCreatesNothing() {
    Fixture f = new Fixture();
    f.attributes.put(TOKEN, new ThrowingToken(new AssertionError("foreign token must not read")));
    f.attributes.put(ALIAS, PUBLIC_FAULT);
    f.attributes.put(UNRELATED, KEEP);
    WebDisplayContext.restore(f.request);
    assertEquals(Map.of(UNRELATED, KEEP), f.attributes);
  }

  @Test
  void restoreUsesRetainedValueAndFixedHeaderParameterDespiteReplacedForeignAttributes() {
    Fixture f = captured();
    f.principal = null;
    f.attributes.put(TOKEN, new ThrowingToken(new AssertionError("replacement must not read")));
    f.attributes.put(ALIAS, PUBLIC_FAULT);
    f.faults.put(PRINCIPAL_CALL, new AssertionError("restore must not read principal"));
    WebDisplayContext.restore(f.request);
    var restored = (CsrfToken) f.attributes.get(TOKEN);
    assertSame(restored, f.attributes.get(ALIAS));
    assertEquals(HEADER, restored.getHeaderName());
    assertEquals(ALIAS, restored.getParameterName());
    assertEquals(DUMMY, restored.getToken());
    assertEquals(
        VIEWER, WebDisplayContext.existing(f.request).orElseThrow().topBar().getUsername());
  }

  @Test
  void nullMalformedAndBoundaryTokenValuesRemainClosedFormatContracts() {
    Fixture missing = new Fixture();
    missing.principal = actor(UserRole.USER);
    missing.attributes.put(TOKEN, new Token(ALIAS, null));
    var failure =
        assertThrows(NullPointerException.class, () -> WebDisplayContext.capture(missing.request));
    assertEquals("csrf", failure.getMessage());
    assertTrue(WebDisplayContext.existing(missing.request).isEmpty());
    for (String value : List.of("p".repeat(63), "p".repeat(129), "=".repeat(64))) {
      Fixture f = new Fixture();
      f.principal = actor(UserRole.USER);
      f.token(value);
      var rejected =
          assertThrows(IllegalArgumentException.class, () -> WebDisplayContext.capture(f.request));
      assertEquals("CSRF token is invalid", rejected.getMessage());
      assertTrue(WebDisplayContext.existing(f.request).isEmpty());
    }
    for (String value : List.of("p".repeat(64), "p".repeat(128))) {
      Fixture f = new Fixture();
      f.principal = actor(UserRole.USER);
      f.token(value);
      WebDisplayContext.capture(f.request);
      WebDisplayContext.restore(f.request);
      assertEquals(value, ((CsrfToken) f.attributes.get(TOKEN)).getToken());
    }
  }

  @Test
  void unknownPortRuntimeAndErrorPreserveIdentityAcrossCaptureExistingClearAndRestore() {
    for (Throwable fault :
        List.of(
            new UnsupportedOperationException(PUBLIC_FAULT), new AssertionError(PUBLIC_FAULT))) {
      for (String point : List.of(PRINCIPAL_CALL, "get:" + TOKEN, "set:" + DISPLAY)) {
        Fixture f = new Fixture();
        f.principal = actor(UserRole.USER);
        f.token(DUMMY);
        f.faults.put(point, fault);
        assertSame(
            fault, assertThrows(fault.getClass(), () -> WebDisplayContext.capture(f.request)));
      }
      for (boolean parameter : List.of(true, false)) {
        Fixture tokenFault = new Fixture();
        tokenFault.principal = actor(UserRole.USER);
        tokenFault.attributes.put(TOKEN, new ThrowingToken(fault, parameter));
        assertSame(
            fault,
            assertThrows(fault.getClass(), () -> WebDisplayContext.capture(tokenFault.request)));
      }
      Fixture getter = captured();
      getter.faults.put("get:" + DISPLAY, fault);
      assertSame(
          fault, assertThrows(fault.getClass(), () -> WebDisplayContext.existing(getter.request)));
      Fixture clear = captured();
      clear.faults.put("remove:" + DISPLAY, fault);
      assertSame(
          fault, assertThrows(fault.getClass(), () -> WebDisplayContext.clear(clear.request)));
      Fixture restore = captured();
      restore.faults.put("set:" + TOKEN, fault);
      assertSame(
          fault, assertThrows(fault.getClass(), () -> WebDisplayContext.restore(restore.request)));
    }
  }

  @Test
  void filterRejectsNullAndEveryNonHttpPairBeforePrincipalOrChain() {
    Fixture f = new Fixture();
    var calls = new AtomicInteger();
    FilterChain chain = (request, response) -> calls.incrementAndGet();
    assertThrows(NullPointerException.class, () -> FILTER.doFilter(null, f.response, chain));
    assertThrows(NullPointerException.class, () -> FILTER.doFilter(f.request, null, chain));
    assertThrows(NullPointerException.class, () -> FILTER.doFilter(f.request, f.response, null));
    ServletRequest raw =
        proxy(
            ServletRequest.class,
            (name, args) -> {
              throw new AssertionError("nonHTTP must not operate");
            });
    ServletResponse response =
        proxy(
            ServletResponse.class,
            (name, args) -> {
              throw new AssertionError("nonHTTP must not operate");
            });
    ServletRequest[] inputs = {raw, raw, f.request};
    ServletResponse[] outputs = {response, f.response, response};
    for (int i = 0; i < inputs.length; i++) {
      ServletRequest input = inputs[i];
      ServletResponse output = outputs[i];
      var failure =
          assertThrows(ServletException.class, () -> FILTER.doFilter(input, output, chain));
      assertEquals("HTTP display boundary required", failure.getMessage());
    }
    assertEquals(0, calls.get());
    assertEquals(List.of(), f.operations);
  }

  @Test
  void filterCapturesBeforeChainAndKeepsVerifiedDisplayAcrossDownstreamFailures() throws Exception {
    Fixture success = new Fixture();
    success.principal = actor(UserRole.ADMIN);
    success.token(DUMMY);
    var calls = new AtomicInteger();
    FILTER.doFilter(
        success.request,
        success.response,
        (request, response) -> {
          assertSame(success.request, request);
          assertSame(success.response, response);
          assertEquals(
              "ADMIN",
              WebDisplayContext.existing(success.request).orElseThrow().topBar().getRole());
          calls.incrementAndGet();
        });
    assertEquals(1, calls.get());
    Fixture anonymous = new Fixture();
    FILTER.doFilter(
        anonymous.request,
        anonymous.response,
        (request, response) -> {
          assertTrue(WebDisplayContext.existing(anonymous.request).isEmpty());
          calls.incrementAndGet();
        });
    assertEquals(2, calls.get());
    Fixture invalid = new Fixture();
    invalid.principal = () -> VIEWER;
    storeFailure(
        () ->
            FILTER.doFilter(
                invalid.request, invalid.response, (request, response) -> calls.incrementAndGet()));
    assertEquals(2, calls.get());
    for (Throwable fault :
        List.of(
            new IOException(PUBLIC_FAULT),
            new ServletException(PUBLIC_FAULT),
            new UnsupportedOperationException(PUBLIC_FAULT),
            new AssertionError(PUBLIC_FAULT))) {
      Fixture f = new Fixture();
      f.principal = actor(UserRole.USER);
      f.token(DUMMY);
      assertSame(
          fault,
          assertThrows(
              fault.getClass(),
              () ->
                  FILTER.doFilter(
                      f.request, f.response, (request, response) -> downstream(fault))));
      assertEquals(
          VIEWER, WebDisplayContext.existing(f.request).orElseThrow().topBar().getUsername());
    }
  }

  private static Fixture captured() {
    Fixture f = new Fixture();
    f.principal = actor(UserRole.USER);
    f.token(DUMMY);
    WebDisplayContext.capture(f.request);
    return f;
  }

  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(VIEWER, role, AuthenticationContext.of(DUMMY), Instant.EPOCH);
  }

  private static void storeFailure(Executable action) {
    var failure = assertThrows(SessionStoreException.class, action);
    assertEquals("session storage is unavailable", failure.getMessage());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void downstream(Throwable failure) throws IOException, ServletException {
    if (failure instanceof IOException io) throw io;
    if (failure instanceof ServletException servlet) throw servlet;
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  private record Token(String parameterName, String token) implements CsrfToken {
    @Override
    public String getHeaderName() {
      return HEADER;
    }

    @Override
    public String getParameterName() {
      return parameterName;
    }

    @Override
    public String getToken() {
      return token;
    }
  }

  private static final class ThrowingToken implements CsrfToken {
    private static final long serialVersionUID = 1L;
    private final Throwable failure;
    private final boolean atParameter;

    ThrowingToken(Throwable failure) {
      this(failure, true);
    }

    ThrowingToken(Throwable failure, boolean atParameter) {
      this.failure = failure;
      this.atParameter = atParameter;
    }

    @Override
    public String getHeaderName() {
      throw new AssertionError("not used");
    }

    @Override
    public String getParameterName() {
      if (!atParameter) return ALIAS;
      if (failure instanceof RuntimeException runtime) throw runtime;
      throw (Error) failure;
    }

    @Override
    public String getToken() {
      if (failure instanceof RuntimeException runtime) throw runtime;
      throw (Error) failure;
    }
  }

  private static final class Fixture {
    final Map<String, Object> attributes = new HashMap<>();
    final Map<String, Throwable> faults = new HashMap<>();
    final List<String> operations = new ArrayList<>();
    Principal principal;
    final HttpServletRequest request =
        proxy(
            HttpServletRequest.class,
            (name, args) -> {
              String point =
                  switch (name) {
                    case "getUserPrincipal" -> PRINCIPAL_CALL;
                    case "getAttribute" -> "get:" + args[0];
                    case "setAttribute" -> "set:" + args[0];
                    case "removeAttribute" -> "remove:" + args[0];
                    default -> throw new AssertionError("forbidden request operation " + name);
                  };
              operations.add(point);
              Throwable fault = faults.get(point);
              if (fault != null) throw fault;
              return switch (name) {
                case "getUserPrincipal" -> principal;
                case "getAttribute" -> attributes.get((String) args[0]);
                case "setAttribute" -> {
                  attributes.put((String) args[0], args[1]);
                  yield null;
                }
                case "removeAttribute" -> {
                  attributes.remove((String) args[0]);
                  yield null;
                }
                default -> throw new AssertionError("unreachable fixture operation");
              };
            });
    final HttpServletResponse response =
        proxy(
            HttpServletResponse.class,
            (name, args) -> {
              throw new AssertionError("display filter must not operate response");
            });

    void token(String value) {
      attributes.put(TOKEN, new DefaultCsrfToken(HEADER, ALIAS, value));
    }
  }

  @FunctionalInterface
  private interface Call {
    Object invoke(String name, Object[] args) throws Throwable;
  }

  private static <T> T proxy(Class<T> type, Call call) {
    return type.cast(
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (object, method, args) ->
                call.invoke(method.getName(), args == null ? new Object[0] : args)));
  }
}
