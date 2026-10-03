package dev.codex.schubert.nk.web.security;

import jakarta.servlet.http.HttpServletRequest;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * Request-lifetime server identity and verified transport address; no session or body. NK-WEB-001;
 * FUN-001/AUT-004/MON-004; UI222/226/252; SS313/314/342/351/352; PG-D-108/PT-WEB-101..108. The
 * attribute is internal, not an HTTP header or form field.
 */
public final class WebRequestContext {
  static final String ATTRIBUTE = WebRequestContext.class.getName();
  private static final String ID_ATTRIBUTE = WebRequestContext.class.getName() + ".requestId";
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

  public static Optional<WebRequestContext> existing(HttpServletRequest request) {
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

  /** Server identity before transport validation is not an authenticated client address. SSC172. */
  public static UUID identify(HttpServletRequest request, Supplier<UUID> identifiers) {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(identifiers, "identifiers");
    var context = existing(request);
    Object value;
    try {
      value = request.getAttribute(ID_ATTRIBUTE);
    } catch (IllegalArgumentException | IllegalStateException attributeFailure) {
      throw new IllegalStateException("web request context is unavailable");
    }
    UUID id;
    if (value == null) {
      id =
          context.isPresent()
              ? context.orElseThrow().requestId()
              : Objects.requireNonNull(identifiers.get(), "requestId");
      try {
        request.setAttribute(ID_ATTRIBUTE, id);
      } catch (IllegalArgumentException | IllegalStateException attributeFailure) {
        throw new IllegalStateException("web request context is unavailable");
      }
    } else if (value instanceof UUID typed) id = typed;
    else throw new IllegalStateException("web request identity is unavailable");
    if (context.isPresent() && !context.orElseThrow().requestId().equals(id))
      throw new IllegalStateException("web request identity is unavailable");
    return id;
  }

  @Override
  public String toString() {
    return "WebRequestContext[REDACTED]";
  }
}
