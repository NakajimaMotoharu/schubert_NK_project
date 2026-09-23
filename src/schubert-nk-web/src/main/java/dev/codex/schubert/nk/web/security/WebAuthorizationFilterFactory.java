package dev.codex.schubert.nk.web.security;

import static org.springframework.security.web.servlet.util.matcher.PathPatternRequestMatcher.pathPattern;

import jakarta.servlet.DispatcherType;
import org.springframework.http.HttpMethod;
import org.springframework.security.web.access.intercept.AuthorizationFilter;
import org.springframework.security.web.access.intercept.RequestMatcherDelegatingAuthorizationManager;
import org.springframework.security.web.util.matcher.AndRequestMatcher;
import org.springframework.security.web.util.matcher.DispatcherTypeRequestMatcher;
import org.springframework.security.web.util.matcher.OrRequestMatcher;
import org.springframework.security.web.util.matcher.RequestMatcher;

/**
 * Explicit URL policy inside StrictHttpFirewall and after encrypted Session/Holder/CSRF/Login. Only
 * the closed session/provider supplies Authentication; API still rechecks role/owner. NK-WEB-001;
 * FUN-001..013/AUT-001..004; UI221/226; SS313/314/352; PG-D-111/PT-WEB-121..124. Entry-point/error
 * views and runtime chain are separate components.
 */
public final class WebAuthorizationFilterFactory {
  public AuthorizationFilter create() {
    var manager =
        RequestMatcherDelegatingAuthorizationManager.builder()
            .requestMatchers(
                pathPattern(HttpMethod.GET, "/login"),
                pathPattern(HttpMethod.POST, "/login"),
                readResource("/error"),
                new AndRequestMatcher(
                    pathPattern("/error"), new DispatcherTypeRequestMatcher(DispatcherType.ERROR)),
                readResource("/styles.css"),
                readResource("/favicon.ico"),
                readResource("/css/schubert.css"),
                readResource("/js/search-speaker-submit.js"),
                readResource("/js/log-search-validation.js"))
            .permitAll()
            .requestMatchers(pathPattern("/admin/**"), pathPattern("/logs"))
            .hasRole("ADMIN")
            .anyRequest()
            .authenticated()
            .build();
    // Spring7.1.1 defaults authorize every ERROR/ASYNC/forward/include as well as REQUEST.
    return new AuthorizationFilter(manager);
  }

  // BUG-072/YKT-064: public assets are read-only, not a wildcard method permission.
  private static RequestMatcher readResource(String path) {
    return new OrRequestMatcher(
        pathPattern(HttpMethod.GET, path), pathPattern(HttpMethod.HEAD, path));
  }
}
