package dev.codex.schubert.nk.web.security;

import jakarta.servlet.http.HttpServletRequest;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/**
 * Request-lifetime server identity and verified transport address; no session or body. NK-WEB-001;
 * FUN-001/AUT-004/MON-004; UI222/226/252; SS313/314/342/351/352; PG-D-108/PT-WEB-101..108. The
 * attribute is internal, not an HTTP header or form field.
 */
public final class WebRequestContext {
  static final String ATTRIBUTE = WebRequestContext.class.getName();
  private final UUID requestId;
  private final LoginClientAddress clientAddress;

  WebRequestContext(UUID requestId, LoginClientAddress clientAddress) {
    this.requestId = Objects.requireNonNull(requestId, "requestId");
    this.clientAddress = Objects.requireNonNull(clientAddress, "clientAddress");
  }

  public UUID requestId() {
    return requestId;
  }

  public LoginClientAddress clientAddress() {
    return clientAddress;
  }

  /** Missing/mistyped server context is a wiring failure, never an untrusted fallback. */
  public static WebRequestContext require(HttpServletRequest request) {
    return existing(request)
        .orElseThrow(() -> new IllegalStateException("web request context is unavailable"));
  }

  static Optional<WebRequestContext> existing(HttpServletRequest request) {
    Objects.requireNonNull(request, "request");
    try {
      Object value = request.getAttribute(ATTRIBUTE);
      if (value == null) return Optional.empty();
      if (value instanceof WebRequestContext context) return Optional.of(context);
      throw new IllegalStateException("web request context is unavailable");
    } catch (IllegalArgumentException | IllegalStateException failure) {
      throw new IllegalStateException("web request context is unavailable");
    }
  }

  @Override
  public String toString() {
    return "WebRequestContext[REDACTED]";
  }
}
