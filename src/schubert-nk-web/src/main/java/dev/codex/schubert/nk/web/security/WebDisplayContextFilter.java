package dev.codex.schubert.nk.web.security;

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
 * Snapshot after closed Servlet identity, before authorization/downstream failures. NK-WEB-001;
 * AUT/TST; UI222/226; SS313/314/352; SSC-047/PG-D-116/PT-WEB-149..157.
 */
public final class WebDisplayContextFilter implements Filter {
  @Override
  public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
      throws IOException, ServletException {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Objects.requireNonNull(chain, "chain");
    if (!(request instanceof HttpServletRequest http) || !(response instanceof HttpServletResponse))
      throw new ServletException("HTTP display boundary required");
    WebDisplayContext.capture(http);
    chain.doFilter(request, response);
  }
}
