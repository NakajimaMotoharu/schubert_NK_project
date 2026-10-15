package dev.codex.schubert.nk.web.security;

import jakarta.servlet.DispatcherType;
import jakarta.servlet.Filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.FilterConfig;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Objects;
import org.springframework.security.core.context.SecurityContextHolder;

/**
 * Internal error rendering is not business authorization. NK-WEB-001; AUT/TST; UI221/222/226;
 * SS313/314/352; SSC-047/PG-D-116/PT-WEB-148..157; BUG-074/YKT-066.
 */
public final class InternalErrorDispatchRouter implements Filter {
  private final Filter business;
  private final Filter errors;

  public InternalErrorDispatchRouter(Filter business, Filter errors) {
    this.business = Objects.requireNonNull(business, "business");
    this.errors = Objects.requireNonNull(errors, "errors");
  }

  @Override
  public void init(FilterConfig config) throws ServletException {
    Objects.requireNonNull(config, "config");
    business.init(config);
    try {
      errors.init(config);
    } catch (ServletException | RuntimeException failure) {
      // Cleanup only: no exception is interpreted as success, no diagnostics are retained.
      try {
        errors.destroy();
      } finally {
        business.destroy();
      }
      throw failure;
    }
  }

  @Override
  public void destroy() {
    try {
      errors.destroy();
    } finally {
      business.destroy();
    }
  }

  @Override
  public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
      throws IOException, ServletException {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Objects.requireNonNull(chain, "chain");
    if (!(request instanceof HttpServletRequest http) || !(response instanceof HttpServletResponse))
      throw new ServletException("HTTP routing boundary required");
    try {
      if (http.getDispatcherType() == DispatcherType.ERROR
          && "/error".equals(http.getRequestURI())) {
        WebRequestContext.require(http);
        errors.doFilter(request, response, chain);
      } else business.doFilter(request, response, chain);
    } finally {
      SecurityContextHolder.clearContext();
    }
  }
}
