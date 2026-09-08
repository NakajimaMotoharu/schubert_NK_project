package dev.codex.schubert.nk.web.security;

import static org.springframework.security.web.servlet.util.matcher.PathPatternRequestMatcher.pathPattern;

import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit.Event;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit.Route;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.security.web.access.AccessDeniedHandler;
import org.springframework.security.web.util.matcher.OrRequestMatcher;
import org.springframework.security.web.util.matcher.RequestMatcher;

/**
 * UI221 Login navigation versus non-replayable POST/AJAX/media and role403. Requires trusted
 * request context and encrypted Session/Holder; no API invalidation or exception inspection.
 * NK-WEB-001; FUN-001..013/AUT-001..004/MON-004; UI221/226; SS313/314/351/352;
 * PG-D-112/PT-WEB-125..130.
 */
public final class WebAccessFailureHandler
    implements AuthenticationEntryPoint, AccessDeniedHandler {
  private static final RequestMatcher MEDIA =
      new OrRequestMatcher(
          pathPattern("/audio/**"), pathPattern("/animation/media/**"),
          pathPattern("/music/media/**"), pathPattern("/music/download/**"));
  private final EncryptedSessionRequestCache cache;
  private final WebSecurityAudit audit;

  public WebAccessFailureHandler(EncryptedSessionRequestCache cache, WebSecurityAudit audit) {
    this.cache = Objects.requireNonNull(cache, "cache");
    this.audit = Objects.requireNonNull(audit, "audit");
  }

  @Override
  public void commence(
      HttpServletRequest request, HttpServletResponse response, AuthenticationException exception)
      throws IOException {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Objects.requireNonNull(exception, "exception");
    var context = WebRequestContext.require(request);
    boolean navigate =
        "GET".equals(request.getMethod())
            && !"XMLHttpRequest".equalsIgnoreCase(request.getHeader("X-Requested-With"))
            && !MEDIA.matches(request);
    response.setStatus(403);
    if (navigate) cache.saveRequest(request, response);
    audit.record(
        context.requestId(),
        Event.AUTHENTICATION_REQUIRED,
        Optional.of(context.clientAddress().value()),
        Optional.empty(),
        0,
        Route.ALL_WEB);
    if (navigate) {
      response.setHeader("Location", "/login");
      response.setStatus(302);
    } else {
      response.sendError(403);
    }
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
    audit.record(
        context.requestId(),
        Event.ROLE_DENIED,
        Optional.of(context.clientAddress().value()),
        actor,
        0,
        Route.ALL_WEB);
    response.sendError(403);
  }
}
