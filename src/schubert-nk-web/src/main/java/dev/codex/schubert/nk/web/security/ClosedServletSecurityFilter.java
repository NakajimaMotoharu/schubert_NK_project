package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.logging.WebRequestTrace;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import jakarta.servlet.Filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletRequestWrapper;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.security.Principal;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.Nullable;
import org.springframework.security.core.context.SecurityContextHolder;

/**
 * Immutable Servlet identity projection; authentication mutations require the dedicated
 * coordinators. NK-WEB-001; FUN-001/AUT-001..004; UI226; SS313/314/352; BUG-073/YKT-065;
 * PG-D-114/PT-WEB-137..141.
 */
public final class ClosedServletSecurityFilter implements Filter {
  @Override
  public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
      throws IOException, ServletException {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Objects.requireNonNull(chain, "chain");
    if (!(request instanceof HttpServletRequest http) || !(response instanceof HttpServletResponse))
      throw new ServletException("HTTP security boundary required");
    var principal =
        ClosedWebAuthentication.principal(SecurityContextHolder.getContext().getAuthentication());
    WebRequestTrace.captureActor(http, principal);
    chain.doFilter(new ClosedServletRequest(http, principal), response);
  }

  private static final class ClosedServletRequest extends HttpServletRequestWrapper {
    private final Optional<SessionPrincipal> principal;

    private ClosedServletRequest(HttpServletRequest request, Optional<SessionPrincipal> principal) {
      super(request);
      this.principal = principal;
    }

    @Override
    public @Nullable Principal getUserPrincipal() {
      return principal.orElse(null);
    }

    @Override
    public @Nullable String getRemoteUser() {
      return principal.map(SessionPrincipal::username).orElse(null);
    }

    @Override
    public @Nullable String getAuthType() {
      return principal.isPresent() ? HttpServletRequest.FORM_AUTH : null;
    }

    @Override
    public boolean isUserInRole(@Nullable String role) {
      if (role == null || principal.isEmpty()) return false;
      String name = role.startsWith("ROLE_") ? role.substring(5) : role;
      return principal.orElseThrow().role().wireValue().equals(name);
    }

    @Override
    public boolean authenticate(HttpServletResponse response) throws ServletException {
      Objects.requireNonNull(response, "response");
      throw new ServletException("programmatic authentication is prohibited");
    }

    @Override
    public void login(String username, String password) throws ServletException {
      Objects.requireNonNull(username, "username");
      Objects.requireNonNull(password, "password");
      throw new ServletException("programmatic authentication is prohibited");
    }

    @Override
    public void logout() throws ServletException {
      throw new ServletException("programmatic authentication is prohibited");
    }

    @Override
    public String toString() {
      return "ClosedServletRequest[REDACTED]";
    }
  }
}
