package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.session.SessionStoreException;
import jakarta.servlet.*;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Objects;

/**
 * Only typed storage failures map to503; never retries error dispatch or committed output.
 * NK-WEB-001; AUT/TST; UI221/222/226; SS313/314/351/352; SSC-047/PG-D-116/PT-WEB-150..157.
 */
public final class WebInfrastructureFailureFilter implements Filter {
  @Override
  public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
      throws IOException, ServletException {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Objects.requireNonNull(chain, "chain");
    if (!(request instanceof HttpServletRequest http)
        || !(response instanceof HttpServletResponse output))
      throw new ServletException("HTTP failure boundary required");
    try {
      chain.doFilter(request, response);
    } catch (SessionStoreException failure) {
      if (output.isCommitted() || http.getDispatcherType() == DispatcherType.ERROR) throw failure;
      output.sendError(503);
    }
  }
}
