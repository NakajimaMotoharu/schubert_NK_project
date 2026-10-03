package dev.codex.schubert.nk.web.logging;

import jakarta.servlet.DispatcherType;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.springframework.web.servlet.HandlerInterceptor;
import org.springframework.web.servlet.HandlerMapping;

/** Only a real registered MVC mapping can be considered; SS312351/REQ004/BUG574/YKT414. */
@NullMarked
public final class WebRequestRouteInterceptor implements HandlerInterceptor {
  @Override
  public boolean preHandle(
      HttpServletRequest request, HttpServletResponse response, Object handler) {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Objects.requireNonNull(handler, "handler");
    if (request.getDispatcherType() != DispatcherType.ERROR) {
      Object pattern = request.getAttribute(HandlerMapping.BEST_MATCHING_PATTERN_ATTRIBUTE);
      if (pattern instanceof String registered)
        WebRequestTrace.existing(request).ifPresent(trace -> trace.captureRoute(registered));
    }
    return true;
  }
}
