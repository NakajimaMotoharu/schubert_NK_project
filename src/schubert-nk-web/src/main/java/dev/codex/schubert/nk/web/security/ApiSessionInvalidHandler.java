package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit.Event;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit.Route;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.session.SpringEncryptedSessionRepository;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.session.web.http.SessionRepositoryFilter;

/**
 * Terminal controller boundary for an already validated business API0102, never an HTTP-bound
 * result parameter. Clears only the current encrypted local session; no API Logout/retry work.
 * NK-WEB-001; FUN-001/AUT-001..004/MON-004/TST; UI221/226; SS313/314/351/352;
 * SSC-048/PG-D-117/PT-WEB-159..165.
 */
public final class ApiSessionInvalidHandler {
  private final SpringEncryptedSessionRepository sessions;
  private final WebSecurityAudit audit;

  public ApiSessionInvalidHandler(
      SpringEncryptedSessionRepository sessions, WebSecurityAudit audit) {
    this.sessions = Objects.requireNonNull(sessions, "sessions");
    this.audit = Objects.requireNonNull(audit, "audit");
  }

  /** Caller must return immediately after this method; never render or continue business work. */
  public void handle(HttpServletRequest request, HttpServletResponse response) throws IOException {
    terminate(request, response, false);
  }

  /** SSC177: only after verified self UPW0000/0200; no synthetic API0102 or second Logout. */
  public void handleVerifiedSelfReset(HttpServletRequest request, HttpServletResponse response)
      throws IOException {
    terminate(request, response, true);
  }

  private void terminate(
      HttpServletRequest request, HttpServletResponse response, boolean verifiedSelfReset)
      throws IOException {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    try {
      var actor =
          ClosedWebAuthentication.principal(SecurityContextHolder.getContext().getAuthentication());
      var context = WebRequestContext.require(request);
      WebDisplayContext.clear(request);
      SecurityContextHolder.clearContext();
      if (verifiedSelfReset && actor.isEmpty()) throw new SessionStoreException();
      if (request.getAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR) != sessions)
        throw new SessionStoreException();
      response.setStatus(401);
      try {
        var session = request.getSession(false);
        if (verifiedSelfReset && session == null) throw new SessionStoreException();
        if (session != null) session.invalidate();
      } catch (IllegalArgumentException | IllegalStateException failure) {
        SessionStoreException.preserveFatal(failure);
        throw new SessionStoreException();
      }
      if (!verifiedSelfReset) {
        audit.record(
            context.requestId(),
            Event.API_SESSION_INVALID,
            Optional.of(context.clientAddress().value()),
            actor,
            0,
            Route.ALL_WEB);
      }
      if (response.isCommitted())
        throw new IOException("session-invalid response already committed");
      if (verifiedSelfReset || WebAccessFailureHandler.isNavigation(request)) {
        response.setHeader("Location", verifiedSelfReset ? "/login" : "/login?session-expired");
        response.setStatus(302);
      } else {
        response.sendError(401);
      }
    } finally {
      SecurityContextHolder.clearContext();
    }
  }
}
