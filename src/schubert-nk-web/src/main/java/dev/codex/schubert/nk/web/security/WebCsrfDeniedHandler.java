package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit.Event;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit.Route;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.access.AccessDeniedHandler;

/**
 * CSRF local audit/403 only: no API/outbox, no exception inspection, no session rotation.
 * NK-WEB-001; FUN-001/AUT-004/MON-004; UI222/226/252; SS313/314/351/352; PG-D-108/PT-WEB-105..108.
 * Requires request context/Holder filters and CsrfFilter logger WARN.
 */
public final class WebCsrfDeniedHandler implements AccessDeniedHandler {
  private final WebSecurityAudit audit;

  public WebCsrfDeniedHandler(WebSecurityAudit audit) {
    this.audit = Objects.requireNonNull(audit, "audit");
  }

  @Override
  public void handle(
      HttpServletRequest request, HttpServletResponse response, AccessDeniedException exception)
      throws IOException {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Objects.requireNonNull(exception, "exception");
    var context = WebRequestContext.require(request);
    var actor =
        ClosedWebAuthentication.principal(SecurityContextHolder.getContext().getAuthentication());
    response.setStatus(403);
    // SSC-047/PG-D-116/PT-WEB-155: keep only already resolved display data for error rendering.
    WebDisplayContext.captureDenied(request, actor);
    audit.record(
        context.requestId(),
        Event.CSRF_DENIED,
        Optional.of(context.clientAddress().value()),
        actor,
        0,
        Route.ALL_WEB);
    response.sendError(403);
  }
}
