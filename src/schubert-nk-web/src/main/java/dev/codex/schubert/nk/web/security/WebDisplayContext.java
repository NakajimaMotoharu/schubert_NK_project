package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.view.TopBarViewModel;
import jakarta.servlet.http.HttpServletRequest;
import java.util.Objects;
import java.util.Optional;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;

/**
 * Request-only display snapshot; no principal/context/session ID. NK-WEB-001; AUT-001..004/TST;
 * UI222/226; SS313/314/352; SSC-047/PG-D-116/PT-WEB-148..157.
 */
public final class WebDisplayContext {
  private static final String ATTRIBUTE = WebDisplayContext.class.getName();
  private final TopBarViewModel topBar;
  private final WebCsrfToken csrf;

  private WebDisplayContext(TopBarViewModel topBar, WebCsrfToken csrf) {
    this.topBar = topBar;
    this.csrf = csrf;
  }

  static void capture(HttpServletRequest request) {
    Objects.requireNonNull(request, "request");
    var principal = request.getUserPrincipal();
    if (principal == null) {
      request.removeAttribute(ATTRIBUTE);
      return;
    }
    if (!(principal instanceof SessionPrincipal closed)) throw new SessionStoreException();
    capture(request, closed);
  }

  static void captureDenied(HttpServletRequest request, Optional<SessionPrincipal> actor) {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(actor, "actor");
    request.removeAttribute(ATTRIBUTE);
    if (actor.isPresent() && request.getAttribute(CsrfToken.class.getName()) != null)
      capture(request, actor.orElseThrow());
  }

  private static void capture(HttpServletRequest request, SessionPrincipal closed) {
    Object token = request.getAttribute(CsrfToken.class.getName());
    if (!(token instanceof CsrfToken supplied) || !"_csrf".equals(supplied.getParameterName()))
      throw new SessionStoreException();
    var csrf = WebCsrfToken.parse(Objects.requireNonNull(supplied.getToken(), "csrf"));
    request.setAttribute(ATTRIBUTE, new WebDisplayContext(TopBarViewModel.from(closed), csrf));
  }

  public static Optional<WebDisplayContext> existing(HttpServletRequest request) {
    Objects.requireNonNull(request, "request");
    Object value = request.getAttribute(ATTRIBUTE);
    if (value == null) return Optional.empty();
    if (value instanceof WebDisplayContext context) return Optional.of(context);
    throw new SessionStoreException();
  }

  /** Mandatory after API0102/local identity invalidation, before rendering or redirecting. */
  public static void clear(HttpServletRequest request) {
    Objects.requireNonNull(request, "request");
    request.removeAttribute(ATTRIBUTE);
    request.removeAttribute(CsrfToken.class.getName());
    request.removeAttribute("_csrf");
  }

  static void restore(HttpServletRequest request) {
    var snapshot = existing(request);
    request.removeAttribute(CsrfToken.class.getName());
    request.removeAttribute("_csrf");
    if (snapshot.isPresent()) {
      var token =
          new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", snapshot.orElseThrow().csrf.formValue());
      request.setAttribute(CsrfToken.class.getName(), token);
      request.setAttribute("_csrf", token);
    }
  }

  public TopBarViewModel topBar() {
    return topBar;
  }

  @Override
  public String toString() {
    return "WebDisplayContext[REDACTED]";
  }
}
