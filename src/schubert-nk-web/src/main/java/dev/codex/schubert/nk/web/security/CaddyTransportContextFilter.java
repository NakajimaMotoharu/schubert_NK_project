package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit.Event;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit.Route;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import jakarta.servlet.Filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * Run inside security headers and before forwarded wrappers/session access on every dispatch. IP
 * transport trust only; Host/origin and final dispatch registration remain separate gates.
 * NK-WEB-001; FUN-001/AUT-004/MON-004; UI222/226/252; SS313/314/342/351/352;
 * PG-D-108/PT-WEB-101..108.
 */
public final class CaddyTransportContextFilter implements Filter {
  private final Supplier<UUID> ids;
  private final CaddyClientAddressResolver addresses;
  private final WebSecurityAudit audit;

  public CaddyTransportContextFilter(
      Supplier<UUID> ids, CaddyClientAddressResolver addresses, WebSecurityAudit audit) {
    this.ids = Objects.requireNonNull(ids, "ids");
    this.addresses = Objects.requireNonNull(addresses, "addresses");
    this.audit = Objects.requireNonNull(audit, "audit");
  }

  @Override
  public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
      throws IOException, ServletException {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Objects.requireNonNull(chain, "chain");
    if (!(request instanceof HttpServletRequest http)
        || !(response instanceof HttpServletResponse result))
      throw new ServletException("HTTP transport is required");
    var existing = WebRequestContext.existing(http);
    UUID requestId = WebRequestContext.identify(http, ids);
    LoginClientAddress address;
    try {
      address = addresses.resolve(http);
      if (existing.isPresent() && !existing.orElseThrow().clientAddress().equals(address))
        throw new CaddyRequestRejectedException();
    } catch (CaddyRequestRejectedException rejected) {
      result.setStatus(403);
      audit.record(
          requestId, Event.PROXY_DENIED, Optional.empty(), Optional.empty(), 0, Route.ALL_WEB);
      // BUG-070/YKT-062/PT-WEB-110: no trusted context exists on this rejection path.
      // sendError redispatches through this guard and duplicates identity/audit. End here;
      // trusted CSRF failures still dispatch to their error view in WebCsrfDeniedHandler.
      return;
    }
    var context =
        existing.isPresent() ? existing.orElseThrow() : new WebRequestContext(requestId, address);
    try {
      http.setAttribute(WebRequestContext.ATTRIBUTE, context);
    } catch (IllegalArgumentException | IllegalStateException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new IllegalStateException("web request context is unavailable");
    }
    chain.doFilter(request, response);
  }
}
