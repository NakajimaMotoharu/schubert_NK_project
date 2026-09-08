package dev.codex.schubert.nk.web.security;

import static org.springframework.security.web.servlet.util.matcher.PathPatternRequestMatcher.pathPattern;

import org.springframework.security.web.access.intercept.AuthorizationFilter;
import org.springframework.security.web.access.intercept.RequestMatcherDelegatingAuthorizationManager;

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
                pathPattern("/login"),
                pathPattern("/error"),
                pathPattern("/styles.css"),
                pathPattern("/favicon.ico"),
                pathPattern("/css/schubert.css"),
                pathPattern("/js/search-speaker-submit.js"))
            .permitAll()
            .requestMatchers(pathPattern("/admin/**"), pathPattern("/logs"))
            .hasRole("ADMIN")
            .anyRequest()
            .authenticated()
            .build();
    // Spring7.1.1 defaults authorize every ERROR/ASYNC/forward/include as well as REQUEST.
    return new AuthorizationFilter(manager);
  }
}
