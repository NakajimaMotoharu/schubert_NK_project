package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.session.SessionStoreException;
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
  private static final java.lang.String LITERAL_WEB_REQUEST_CONTEXT_IS_UNAVAILABLE =
      "web request context is unavailable";

  static final String ATTRIBUTE = WebRequestContext.class.getName();
  private static final String ID_ATTRIBUTE = WebRequestContext.class.getName() + ".requestId";
  private final UUID retainedRequestId;
  private final LoginClientAddress retainedClientAddress;

  WebRequestContext(UUID requestId, LoginClientAddress clientAddress) {
    this.retainedRequestId = Objects.requireNonNull(requestId, "requestId");
    this.retainedClientAddress = Objects.requireNonNull(clientAddress, "clientAddress");
  }

  public UUID requestId() {
    return retainedRequestId;
  }

  public LoginClientAddress clientAddress() {
    return retainedClientAddress;
  }

  /** Missing/mistyped server context is a wiring failure, never an untrusted fallback. */
  public static WebRequestContext require(HttpServletRequest request) {
    return existing(request)
        .orElseThrow(() -> new IllegalStateException(LITERAL_WEB_REQUEST_CONTEXT_IS_UNAVAILABLE));
  }

  public static Optional<WebRequestContext> existing(HttpServletRequest request) {
    Objects.requireNonNull(request, "request");
    try {
      Object value = request.getAttribute(ATTRIBUTE);
      if (value == null) return Optional.empty();
      if (value instanceof WebRequestContext context) return Optional.of(context);
      throw new IllegalStateException(LITERAL_WEB_REQUEST_CONTEXT_IS_UNAVAILABLE);
    } catch (IllegalArgumentException | IllegalStateException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new IllegalStateException(LITERAL_WEB_REQUEST_CONTEXT_IS_UNAVAILABLE);
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
      SessionStoreException.preserveFatal(attributeFailure);
      throw new IllegalStateException(LITERAL_WEB_REQUEST_CONTEXT_IS_UNAVAILABLE);
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
        SessionStoreException.preserveFatal(attributeFailure);
        throw new IllegalStateException(LITERAL_WEB_REQUEST_CONTEXT_IS_UNAVAILABLE);
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
