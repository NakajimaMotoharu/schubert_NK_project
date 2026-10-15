package dev.codex.schubert.nk.web.security;

import jakarta.servlet.DispatcherType;
import jakarta.servlet.Filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Objects;

/**
 * No session/identity/token generation during internal error rendering. NK-WEB-001; AUT/TST;
 * UI222/226; SS313/314/352; SSC-047/PG-D-116/PT-WEB-149..157.
 */
public final class WebErrorDispatchFilter implements Filter {
  @Override
  public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
      throws IOException, ServletException {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Objects.requireNonNull(chain, "chain");
    if (!(request instanceof HttpServletRequest http) || !(response instanceof HttpServletResponse))
      throw new ServletException("HTTP error boundary required");
    if (http.getDispatcherType() != DispatcherType.ERROR || !"/error".equals(http.getRequestURI()))
      throw new ServletException("internal error dispatch required");
    WebDisplayContext.restore(http);
    chain.doFilter(request, response);
  }
}
