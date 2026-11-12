package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.session.SpringEncryptedSessionRepository;
import dev.codex.schubert.nk.web.session.SpringWebSession;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import java.util.Objects;
import java.util.Optional;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.DeferredSecurityContext;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextImpl;
import org.springframework.security.web.context.HttpRequestResponseHolder;
import org.springframework.security.web.context.SecurityContextRepository;
import org.springframework.session.web.http.SessionRepositoryFilter;

/**
 * Maps only the encrypted closed principal, never serializes a Spring SecurityContext. Normal save
 * validates identity without writing; Login fixation and coordinated Logout own mutations.
 * NK-WEB-001; FUN-001/AUT-001..004; UI226; SS314 §7.2.6/331/352; SSC-044/PG-D-103/PT-WEB-068..075.
 * Requires the configured encrypted Session filter first.
 */
public final class EncryptedSessionSecurityContextRepository implements SecurityContextRepository {
  private final SpringEncryptedSessionRepository sessions;

  public EncryptedSessionSecurityContextRepository(SpringEncryptedSessionRepository sessions) {
    this.sessions = Objects.requireNonNull(sessions, "sessions");
  }

  /** Compatibility required by the7.1.1 interface; owner NK-WEB-001, recheck on upgrade. PT069. */
  @Deprecated
  @Override
  public SecurityContext loadContext(HttpRequestResponseHolder holder) {
    Objects.requireNonNull(holder, "holder");
    return loadDeferredContext(holder.getRequest()).get();
  }

  @Override
  public DeferredSecurityContext loadDeferredContext(HttpServletRequest request) {
    requireConfigured(request);
    return new Deferred(request);
  }

  @Override
  public boolean containsContext(HttpServletRequest request) {
    return stored(request).isPresent();
  }

  /** Same closed identity only. Empty may not silently invalidate an authenticated session. */
  @Override
  public void saveContext(
      SecurityContext context, HttpServletRequest request, HttpServletResponse response) {
    Objects.requireNonNull(context, "context");
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    var desired = ClosedWebAuthentication.principal(context.getAuthentication());
    if (!stored(request).equals(desired)) throw new SessionStoreException();
  }

  /** Internal authenticated strategy boundary; never exposed to request parameter binding. */
  void fixate(Authentication authentication, HttpServletRequest request) {
    SessionPrincipal principal =
        ClosedWebAuthentication.principal(authentication).orElseThrow(SessionStoreException::new);
    requireConfigured(request);
    try {
      HttpSession session = request.getSession(false);
      if (session == null) throw new SessionStoreException();
      // Exactly one atomic authenticate/ID+CSRF rotation; no second set during saveContext.
      session.setAttribute(SpringWebSession.PRINCIPAL, principal);
    } catch (IllegalArgumentException | IllegalStateException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new SessionStoreException();
    }
  }

  private Optional<SessionPrincipal> stored(HttpServletRequest request) {
    requireConfigured(request);
    try {
      HttpSession session = request.getSession(false);
      if (session == null) return Optional.empty();
      Object value = session.getAttribute(SpringWebSession.PRINCIPAL);
      if (value == null) return Optional.empty();
      if (!(value instanceof SessionPrincipal principal)) throw new SessionStoreException();
      return Optional.of(principal);
    } catch (IllegalArgumentException | IllegalStateException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new SessionStoreException();
    }
  }

  private void requireConfigured(HttpServletRequest request) {
    Objects.requireNonNull(request, "request");
    if (request.getAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR) != sessions)
      throw new SessionStoreException();
  }

  /** Request-scoped cache, private monitor, stable initial generated flag. Never shared by bean. */
  private final class Deferred implements DeferredSecurityContext {
    private final java.util.concurrent.locks.ReentrantLock lock =
        new java.util.concurrent.locks.ReentrantLock();
    private final HttpServletRequest request;
    private Optional<SecurityContext> context = Optional.empty();
    private boolean generated;

    private Deferred(HttpServletRequest request) {
      this.request = request;
    }

    @Override
    public SecurityContext get() {
      lock.lock();
      try {
        if (context.isEmpty()) {
          var principal = stored(request);
          generated = principal.isEmpty();
          SecurityContext value = new SecurityContextImpl();
          principal.ifPresent(
              p -> value.setAuthentication(ClosedWebAuthentication.authenticated(p)));
          context = Optional.of(value);
        }
        return context.orElseThrow();
      } finally {
        lock.unlock();
      }
    }

    @Override
    public boolean isGenerated() {
      lock.lock();
      try {
        get();
        return generated;
      } finally {
        lock.unlock();
      }
    }
  }
}
