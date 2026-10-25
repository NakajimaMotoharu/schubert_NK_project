package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.logging.WebRequestTrace;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequestWrapper;
import jakarta.servlet.ServletResponseWrapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.security.Principal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.security.authentication.TestingAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;

/**
 * NK-WEB-001/PT-WEB-138..141; FUN-001/AUT-001..004; UI226; SS313/314/352; PG-D-114;
 * BUG-073/YKT-065.
 */
class ClosedServletSecurityFilterTest {
  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  @Test
  void web138ClosedPrincipalImplementsServletContract() throws Exception {
    var filter = new ClosedServletSecurityFilter();
    for (String role : List.of("ANONYMOUS", "USER", "ADMIN")) {
      SecurityContextHolder.clearContext();
      SessionPrincipal p = null;
      if (!role.equals("ANONYMOUS")) {
        p = principal("reader", role);
        set(p);
      }
      var nativeRequest = hostile();
      var trace = WebRequestTrace.ensure(nativeRequest, UUID::randomUUID);
      var request = capture(filter, nativeRequest);
      assertEquals(p == null, trace.actor().isEmpty());
      if (p != null) {
        assertEquals("reader", trace.actor().orElseThrow().getUsername());
        assertEquals(role, trace.actor().orElseThrow().getRole());
      }
      assertSame(p, request.getUserPrincipal());
      assertEquals(p == null ? null : "reader", request.getRemoteUser());
      assertEquals(p == null ? null : "FORM", request.getAuthType());
      assertFalse(request.isUserInRole(null));
      for (String candidate :
          List.of(
              "",
              "USER",
              "ADMIN",
              "ROLE_USER",
              "ROLE_ADMIN",
              "user",
              " ADMIN",
              "ROLE_ROLE_USER",
              "ANONYMOUS",
              "ROLE_",
              "UNKNOWN")) {
        boolean expected =
            p != null && (candidate.equals(role) || candidate.equals("ROLE_" + role));
        assertEquals(expected, request.isUserInRole(candidate), candidate);
      }
      assertEquals("ClosedServletRequest[REDACTED]", request.toString());
    }
  }

  @Test
  void web139ProgrammaticAuthenticationCannotBypassCoordination() throws Exception {
    for (boolean authenticated : List.of(false, true)) {
      SecurityContextHolder.clearContext();
      var p = principal("reader", "USER");
      if (authenticated) set(p);
      var nativeRequest = hostile();
      var session = nativeRequest.getSession();
      assertNotNull(session);
      session.setAttribute("csrfToken", "synthetic-csrf-canary");
      var request = capture(new ClosedServletSecurityFilter(), nativeRequest);
      var response = new MockHttpServletResponse();
      for (ServletException denied :
          List.of(
              assertThrows(ServletException.class, () -> request.authenticate(response)),
              assertThrows(
                  ServletException.class,
                  () -> request.login("private-user-canary", "private-password-canary")),
              assertThrows(ServletException.class, request::logout))) {
        assertEquals("programmatic authentication is prohibited", denied.getMessage());
        assertNull(denied.getCause());
        assertEquals(0, denied.getSuppressed().length);
      }
      assertThrows(NullPointerException.class, () -> request.authenticate(null));
      assertThrows(NullPointerException.class, () -> request.login(null, "p"));
      assertThrows(NullPointerException.class, () -> request.login("u", null));
      assertSame(session, request.getSession(false));
      assertEquals("synthetic-csrf-canary", session.getAttribute("csrfToken"));
      assertSame(authenticated ? p : null, request.getUserPrincipal());
      assertEquals(
          authenticated ? Optional.of(p) : Optional.empty(),
          ClosedWebAuthentication.principal(
              SecurityContextHolder.getContext().getAuthentication()));
      assertEquals(200, response.getStatus());
      assertFalse(response.isCommitted());
      assertEquals("", response.getContentAsString());
    }
  }

  @Test
  void web140NullForeignAndDownstreamFaultsStayClosed() throws Exception {
    var filter = new ClosedServletSecurityFilter();
    var request = hostile();
    var response = new MockHttpServletResponse();
    FilterChain forbidden = (r, s) -> fail("invalid boundary reached downstream");
    assertThrows(NullPointerException.class, () -> filter.doFilter(null, response, forbidden));
    assertThrows(NullPointerException.class, () -> filter.doFilter(request, null, forbidden));
    assertThrows(NullPointerException.class, () -> filter.doFilter(request, response, null));
    for (ServletException denied :
        List.of(
            assertThrows(
                ServletException.class,
                () -> filter.doFilter(new ServletRequestWrapper(request), response, forbidden)),
            assertThrows(
                ServletException.class,
                () -> filter.doFilter(request, new ServletResponseWrapper(response), forbidden)))) {
      assertEquals("HTTP security boundary required", denied.getMessage());
      assertNull(denied.getCause());
    }
    SecurityContextHolder.getContext()
        .setAuthentication(new TestingAuthenticationToken("foreign", "secret", "ROLE_ADMIN"));
    assertThrows(SessionStoreException.class, () -> filter.doFilter(request, response, forbidden));
    SecurityContextHolder.clearContext();
    var io = new IOException("synthetic downstream fault");
    assertSame(
        io,
        assertThrows(
            IOException.class,
            () ->
                filter.doFilter(
                    request,
                    response,
                    (r, s) -> {
                      throw io;
                    })));
    var servlet = new ServletException("synthetic downstream fault");
    assertSame(
        servlet,
        assertThrows(
            ServletException.class,
            () ->
                filter.doFilter(
                    request,
                    response,
                    (r, s) -> {
                      throw servlet;
                    })));
    assertNull(request.getSession(false));
  }

  @Test
  void web141ConcurrentAndCrossThreadSnapshotsKeepOriginalActor() throws Exception {
    var filter = new ClosedServletSecurityFilter();
    try (var workers = Executors.newFixedThreadPool(8);
        var readers = Executors.newFixedThreadPool(4)) {
      var futures = new ArrayList<Future<Void>>();
      // No externally accessible filter monitor may serialize or deadlock independent requests.
      synchronized (filter) {
        for (int i = 0; i < 100; i++) {
          int n = i;
          futures.add(
              workers.submit(
                  () -> {
                    try {
                      var p = principal("user" + n, n % 2 == 0 ? "USER" : "ADMIN");
                      set(p);
                      var snapshot = capture(filter, hostile());
                      set(principal("other" + n, "ADMIN"));
                      assertSame(p, snapshot.getUserPrincipal());
                      SecurityContextHolder.clearContext();
                      assertSame(p, snapshot.getUserPrincipal());
                      readers
                          .submit(
                              () -> {
                                try {
                                  set(principal("foreign-reader", "ADMIN"));
                                  assertSame(p, snapshot.getUserPrincipal());
                                  assertEquals("user" + n, snapshot.getRemoteUser());
                                  assertTrue(snapshot.isUserInRole(n % 2 == 0 ? "USER" : "ADMIN"));
                                  assertFalse(snapshot.isUserInRole(n % 2 == 0 ? "ADMIN" : "USER"));
                                } finally {
                                  SecurityContextHolder.clearContext();
                                }
                              })
                          .get(10, TimeUnit.SECONDS);
                      assertNull(capture(filter, hostile()).getUserPrincipal());
                      return null;
                    } finally {
                      SecurityContextHolder.clearContext();
                    }
                  }));
        }
        for (var future : futures) future.get(30, TimeUnit.SECONDS);
      }
    }
    assertNull(SecurityContextHolder.getContext().getAuthentication());
  }

  private static SessionPrincipal principal(String name, String role) {
    return new SessionPrincipal(
        name,
        UserRole.valueOf(role),
        AuthenticationContext.of("a".repeat(64)),
        Instant.parse("2026-09-09T00:00:00Z"));
  }

  private static void set(SessionPrincipal p) {
    SecurityContextHolder.getContext().setAuthentication(ClosedWebAuthentication.authenticated(p));
  }

  private static HttpServletRequest capture(
      ClosedServletSecurityFilter filter, HttpServletRequest input) throws Exception {
    var captured = new AtomicReference<HttpServletRequest>();
    var response = new MockHttpServletResponse();
    filter.doFilter(
        input,
        response,
        (r, s) -> {
          assertSame(response, s);
          captured.set((HttpServletRequest) r);
        });
    return Objects.requireNonNull(captured.get());
  }

  private static MockHttpServletRequest hostile() {
    return new MockHttpServletRequest("GET", "/search") {
      @Override
      public Principal getUserPrincipal() {
        throw new AssertionError("native principal read");
      }

      @Override
      public String getRemoteUser() {
        throw new AssertionError("native username read");
      }

      @Override
      public String getAuthType() {
        throw new AssertionError("native auth type read");
      }

      @Override
      public boolean isUserInRole(String role) {
        throw new AssertionError("native role read");
      }

      @Override
      public boolean authenticate(HttpServletResponse response) {
        throw new AssertionError("native authenticate called");
      }

      @Override
      public void login(String username, String password) {
        throw new AssertionError("native login called");
      }

      @Override
      public void logout() {
        throw new AssertionError("native logout called");
      }

      @Override
      public String toString() {
        throw new AssertionError("native request diagnostic read");
      }
    };
  }
}
