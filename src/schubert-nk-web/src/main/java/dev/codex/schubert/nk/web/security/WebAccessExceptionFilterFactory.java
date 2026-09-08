package dev.codex.schubert.nk.web.security;

import java.util.Objects;
import org.springframework.security.web.access.ExceptionTranslationFilter;
import org.springframework.security.web.savedrequest.NullRequestCache;

/**
 * The entry point alone owns conditional saved GET persistence; no unconditional double save. Place
 * before AuthorizationFilter; pin framework diagnostic logging at WARN in runtime. NK-WEB-001;
 * FUN-001..013/AUT-001..004; UI221/226; SS313/314/351/352; PG-D-112/PT-WEB-125..130.
 */
public final class WebAccessExceptionFilterFactory {
  public ExceptionTranslationFilter create(WebAccessFailureHandler handler) {
    Objects.requireNonNull(handler, "handler");
    var filter = new ExceptionTranslationFilter(handler, new NullRequestCache());
    filter.setAccessDeniedHandler(handler);
    return filter;
  }
}
