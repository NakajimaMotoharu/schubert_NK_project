package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.revocation.LocalLogoutCoordinator;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.session.SpringEncryptedSessionRepository;
import dev.codex.schubert.nk.web.session.WebSessionId;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.Nullable;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.session.web.http.SessionRepositoryFilter;

/**
 * Terminal authenticated POST Logout; no HTTP-bound context, redirect, or new session.
 * NK-WEB-002/AUT004/UI226/SS313314351352/QA050/SSC171/PG-D363/RERUN007A..H. MVC registration and
 * the existing security chain own method, authentication and CSRF gates.
 */
public final class LocalLogoutHandler {
  private final SpringEncryptedSessionRepository sessions;
  private final LocalLogoutCoordinator logout;
  private final WebSecurityAudit audit;

  public LocalLogoutHandler(
      SpringEncryptedSessionRepository sessions,
      LocalLogoutCoordinator logout,
      WebSecurityAudit audit) {
    this.sessions = Objects.requireNonNull(sessions, "sessions");
    this.logout = Objects.requireNonNull(logout, "Logout coordinator");
    this.audit = Objects.requireNonNull(audit, "audit");
  }

  public void handle(HttpServletRequest request, HttpServletResponse response) throws IOException {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    try {
      execute(request, response);
    } catch (RuntimeException | Error primary) {
      clear(request, primary);
      SessionStoreException.preserveFatal(primary);
      throw new SessionStoreException();
    } catch (IOException primary) {
      clear(request, primary);
      throw primary;
    }
    clear(request, null);
  }

  private void execute(HttpServletRequest request, HttpServletResponse response)
      throws IOException {
    var actor =
        ClosedWebAuthentication.principal(SecurityContextHolder.getContext().getAuthentication())
            .orElseThrow(SessionStoreException::new);
    var transport = WebRequestContext.require(request);
    if (request.getAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR) != sessions)
      throw new SessionStoreException();
    var session = request.getSession(false);
    if (session == null) throw new SessionStoreException();
    final LocalLogoutCoordinator.Outcome outcome;
    try {
      outcome = logout.logout(WebSessionId.parse(session.getId()), actor.authenticationContext());
    } catch (RuntimeException | Error primary) {
      // Even a failed durable enqueue must attempt the owned Servlet session invalidation.
      // Preserve primary fatal identity if the independent local cleanup also fails.
      try {
        session.invalidate();
      } catch (RuntimeException | Error secondary) {
        if (primary != secondary) primary.addSuppressed(secondary);
      }
      SessionStoreException.preserveFatal(primary);
      throw new SessionStoreException();
    }
    invalidate(session);
    audit.record(
        transport.requestId(),
        outcome == LocalLogoutCoordinator.Outcome.CONFIRMED
            ? WebSecurityAudit.Event.LOGOUT_SUCCEEDED
            : WebSecurityAudit.Event.LOGOUT_REVOCATION_QUEUED,
        Optional.of(transport.clientAddress().value()),
        Optional.of(actor),
        0,
        WebSecurityAudit.Route.LOGOUT);
    if (response.isCommitted()) throw new IOException("Logout response already committed");
    response.setHeader("Location", "/login?logout");
    response.setStatus(302);
  }

  private static void clear(HttpServletRequest request, @Nullable Throwable primary) {
    try {
      WebDisplayContext.clear(request);
    } catch (RuntimeException | Error secondary) {
      if (primary != null) {
        if (primary != secondary) primary.addSuppressed(secondary);
        SessionStoreException.preserveFatal(primary);
      }
      SessionStoreException.preserveFatal(secondary);
      throw new SessionStoreException();
    } finally {
      SecurityContextHolder.clearContext();
    }
  }

  private static void invalidate(HttpSession session) {
    try {
      session.invalidate();
    } catch (RuntimeException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new SessionStoreException();
    }
  }
}
