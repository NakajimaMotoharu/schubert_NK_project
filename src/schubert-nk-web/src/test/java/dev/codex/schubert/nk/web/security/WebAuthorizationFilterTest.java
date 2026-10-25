package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import jakarta.servlet.DispatcherType;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.authentication.AuthenticationCredentialsNotFoundException;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.access.intercept.AuthorizationFilter;
import org.springframework.security.web.firewall.RequestRejectedException;
import org.springframework.security.web.firewall.StrictHttpFirewall;

/** NK-WEB-001/PT-WEB-121..124; FUN-001..013/AUT-001..004; UI221/226; SS313/314/352; PG-D-111. */
class WebAuthorizationFilterTest {
  private static final List<String> PUBLIC =
      List.of(
          "/login",
          "/error",
          "/styles.css",
          "/favicon.ico",
          "/css/schubert.css",
          "/js/search-speaker-submit.js",
          "/js/log-search-validation.js");
  private static final List<String> ADMIN =
      List.of(
          "/admin",
          "/admin/",
          "/admin/users",
          "/admin/users/new",
          "/admin/users/1/status",
          "/admin/users/1/role",
          "/admin/users/1/password",
          "/admin/users/1/unlock",
          "/logs");
  private static final List<String> USER =
      List.of(
          "/",
          "/search",
          "/scenarios",
          "/scenarios/game",
          "/scenarios/game/file",
          "/animation/main",
          "/animation/ova",
          "/animation/opening",
          "/animation/videos/1",
          "/animation/media/1",
          "/music",
          "/music/1",
          "/music/media/1",
          "/audio/1",
          "/audio/1/download",
          "/questions",
          "/questions/1",
          "/questions/accepted/receipt",
          "/notifications",
          "/notifications/1",
          "/logout",
          "/unknown");

  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  @Test
  void web121OnlyExplicitPublicResourcesAreAnonymous() throws Exception {
    var filter = new WebAuthorizationFilterFactory().create();
    for (String method : List.of("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")) {
      for (String path : PUBLIC) {
        SecurityContextHolder.clearContext();
        var request = request(method, path);
        request.addHeader("role", "ADMIN");
        request.addParameter("role", "ADMIN");
        // SS352 §3.1 explicit method table; the initial all-method oracle was BUG-072.
        boolean allowed =
            path.equals("/login")
                ? method.equals("GET") || method.equals("POST")
                : method.equals("GET") || method.equals("HEAD");
        if (allowed) assertEquals(1, invoke(filter, request));
        else
          assertThrows(
              AuthenticationCredentialsNotFoundException.class, () -> invoke(filter, request));
        assertNull(SecurityContextHolder.getContext().getAuthentication());
      }
    }
    for (String path :
        List.of(
            "/css/private.css",
            "/js/private.js",
            "/login/extra",
            "/login.css",
            "/error/extra",
            "/styles.css/extra",
            "/favicon.ico/extra",
            "/static/styles.css",
            "/Login")) {
      var request = request("GET", path);
      request.addHeader("role", "ADMIN");
      request.addParameter("role", "ADMIN");
      assertThrows(AuthenticationCredentialsNotFoundException.class, () -> invoke(filter, request));
    }
    SecurityContextHolder.getContext()
        .setAuthentication(
            new AnonymousAuthenticationToken(
                "synthetic", "anonymous", List.of(new SimpleGrantedAuthority("ROLE_ANONYMOUS"))));
    assertThrows(AccessDeniedException.class, () -> invoke(filter, request("GET", "/search")));
    assertEquals(1, invoke(filter, request("GET", "/login")));
  }

  @Test
  void web122RoleMatrixProtectsAdminAndLogs() throws Exception {
    var filter = new WebAuthorizationFilterFactory().create();
    for (String role : List.of("USER", "ADMIN")) {
      setRole(role, "reader");
      for (String method : List.of("GET", "HEAD", "POST")) {
        for (String path : ADMIN) {
          var request = request(method, path);
          request.setQueryString("role=ADMIN&path=/login");
          request.addHeader("role", "ADMIN");
          if (role.equals("USER"))
            assertThrows(AccessDeniedException.class, () -> invoke(filter, request));
          else assertEquals(1, invoke(filter, request));
        }
        for (String path : USER) assertEquals(1, invoke(filter, request(method, path)));
        for (String path : PUBLIC) assertEquals(1, invoke(filter, request(method, path)));
      }
    }
    SecurityContextHolder.clearContext();
    for (String path : ADMIN)
      assertThrows(
          AuthenticationCredentialsNotFoundException.class,
          () -> invoke(filter, request("GET", path)));
    for (String path : USER)
      assertThrows(
          AuthenticationCredentialsNotFoundException.class,
          () -> invoke(filter, request("GET", path)));
  }

  @Test
  void web123FirewallAndRedispatchCannotBypassRole() throws Exception {
    var filter = new WebAuthorizationFilterFactory().create();
    assertFalse(filter.isObserveOncePerRequest());
    setRole("USER", "reader");
    for (String path :
        List.of(
            "/admin;v=1/users",
            "/admin/../search",
            "//admin/users",
            "/admin%2fusers",
            "/admin%2Fusers",
            "/admin/%2e%2e/search",
            "/admin%5cusers",
            "/admin/%25",
            "/logs%00")) {
      assertThrows(RequestRejectedException.class, () -> invoke(filter, request("GET", path)));
    }
    assertThrows(RequestRejectedException.class, () -> invoke(filter, request("TRACE", "/login")));
    for (String path : List.of("/%61dmin/users", "/%6cogs")) {
      assertThrows(AccessDeniedException.class, () -> invoke(filter, request("GET", path)));
    }
    var request = request("GET", "/admin/users");
    for (DispatcherType dispatcher : DispatcherType.values()) {
      request.setDispatcherType(dispatcher);
      setRole("USER", "reader");
      assertThrows(AccessDeniedException.class, () -> invoke(filter, request));
      setRole("ADMIN", "administrator");
      assertEquals(1, invoke(filter, request));
    }
    setRole("USER", "reader");
    var query = request("GET", "/search");
    query.setQueryString("path=/admin/users&role=ADMIN");
    assertEquals(1, invoke(filter, query));
    SecurityContextHolder.clearContext();
    for (DispatcherType dispatcher : DispatcherType.values()) {
      for (String method : List.of("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")) {
        var error = request(method, "/error");
        error.setDispatcherType(dispatcher);
        if (dispatcher == DispatcherType.ERROR || method.equals("GET") || method.equals("HEAD"))
          assertEquals(1, invoke(filter, error));
        else
          assertThrows(
              AuthenticationCredentialsNotFoundException.class, () -> invoke(filter, error));
        var secret = request(method, "/admin/users");
        secret.setDispatcherType(dispatcher);
        assertThrows(
            AuthenticationCredentialsNotFoundException.class, () -> invoke(filter, secret));
      }
    }
  }

  @Test
  void web124ConcurrentPoliciesHaveNoCrossRequestIdentity() throws Exception {
    var factory = new WebAuthorizationFilterFactory();
    var filter = factory.create();
    assertNotSame(filter, factory.create());
    assertNotSame(filter.getAuthorizationManager(), factory.create().getAuthorizationManager());
    try (var pool = Executors.newFixedThreadPool(8)) {
      var jobs = new ArrayList<Callable<Void>>();
      for (int i = 0; i < 100; i++) {
        int n = i;
        jobs.add(
            () -> {
              try {
                assertNull(SecurityContextHolder.getContext().getAuthentication());
                setRole(n % 2 == 0 ? "USER" : "ADMIN", "reader" + n);
                var request = request("GET", "/admin/users");
                if (n % 2 == 0)
                  assertThrows(AccessDeniedException.class, () -> invoke(filter, request));
                else assertEquals(1, invoke(filter, request));
                assertEquals(
                    "reader" + n, SecurityContextHolder.getContext().getAuthentication().getName());
                assertEquals(1, invoke(filter, request("GET", "/search")));
              } finally {
                SecurityContextHolder.clearContext();
              }
              assertNull(SecurityContextHolder.getContext().getAuthentication());
              SecurityContextHolder.clearContext();
              return null;
            });
      }
      synchronized (filter) {
        for (var future : pool.invokeAll(jobs)) future.get(30, TimeUnit.SECONDS);
      }
    }
    assertNull(SecurityContextHolder.getContext().getAuthentication());
  }

  private static void setRole(String role, String name) {
    var p =
        new SessionPrincipal(
            name,
            UserRole.valueOf(role),
            AuthenticationContext.of("a".repeat(64)),
            Instant.parse("2026-09-09T00:00:00Z"));
    SecurityContextHolder.getContext().setAuthentication(ClosedWebAuthentication.authenticated(p));
  }

  private static MockHttpServletRequest request(String method, String path) {
    return new MockHttpServletRequest(method, path);
  }

  private static int invoke(AuthorizationFilter filter, MockHttpServletRequest request)
      throws Exception {
    var firewall = new StrictHttpFirewall();
    var wrapped = firewall.getFirewalledRequest(request);
    var calls = new AtomicInteger();
    try {
      filter.doFilter(wrapped, new MockHttpServletResponse(), (r, s) -> calls.incrementAndGet());
      return calls.get();
    } catch (AccessDeniedException | AuthenticationCredentialsNotFoundException denied) {
      assertEquals(0, calls.get());
      throw denied;
    } finally {
      wrapped.reset();
    }
  }
}
