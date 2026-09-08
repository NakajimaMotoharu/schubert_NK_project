package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.session.SpringWebSession;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import java.util.Objects;
import org.jspecify.annotations.Nullable;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.CsrfTokenRepository;
import org.springframework.security.web.csrf.DefaultCsrfToken;

/**
 * Uses only the already encrypted session token; never serializes Spring objects. NK-WEB-001;
 * FUN-001/AUT-001..004; UI226; SS314 §8.1/352; PG-D-100/PT-WEB-050..053. Null save invalidates the
 * entire session: call only after Logout coordination.
 */
public final class EncryptedSessionCsrfTokenRepository implements CsrfTokenRepository {
  @Override
  public CsrfToken generateToken(HttpServletRequest request) {
    Objects.requireNonNull(request, "request");
    HttpSession existing = request.getSession(false);
    if (existing != null) request.changeSessionId();
    return materialize(Objects.requireNonNull(request.getSession(true), "session"));
  }

  @Override
  public @Nullable CsrfToken loadToken(HttpServletRequest request) {
    Objects.requireNonNull(request, "request");
    HttpSession session = request.getSession(false);
    if (session == null || session.getAttribute(SpringWebSession.CSRF) == null) return null;
    return materialize(session);
  }

  @Override
  public void saveToken(
      @Nullable CsrfToken token, HttpServletRequest request, HttpServletResponse response) {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    HttpSession session = request.getSession(false);
    if (token == null) {
      if (session != null) session.invalidate();
      return;
    }
    if (session == null) throw new SessionStoreException();
    var current = materialize(session);
    if (!"_csrf".equals(token.getParameterName())
        || !"X-CSRF-TOKEN".equals(token.getHeaderName())
        || !WebCsrfToken.parse(current.getToken()).matches(token.getToken())) {
      throw new SessionStoreException();
    }
  }

  private static CsrfToken materialize(HttpSession session) {
    Object stored = session.getAttribute(SpringWebSession.CSRF);
    if (!(stored instanceof String value)) throw new SessionStoreException();
    try {
      return new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", WebCsrfToken.parse(value).formValue());
    } catch (IllegalArgumentException invalid) {
      throw new SessionStoreException();
    }
  }
}
