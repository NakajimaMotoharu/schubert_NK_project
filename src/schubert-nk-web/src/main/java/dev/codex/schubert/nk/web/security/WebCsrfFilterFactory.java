package dev.codex.schubert.nk.web.security;

import java.util.Objects;
import org.springframework.security.web.access.AccessDeniedHandler;
import org.springframework.security.web.csrf.CsrfFilter;

/**
 * NK-WEB-001; FUN-001/AUT-004; UI226; SS314 §8.1/351/352; PG-D-100/PT-WEB-052/053. Caller must
 * supply a redacting audit/403 handler and pin CsrfFilter logging to WARN.
 */
public final class WebCsrfFilterFactory {
  public CsrfFilter create(
      EncryptedSessionCsrfTokenRepository repository, AccessDeniedHandler denied) {
    Objects.requireNonNull(repository, "repository");
    Objects.requireNonNull(denied, "denied");
    var filter = new CsrfFilter(repository);
    filter.setRequestHandler(new FormCsrfTokenRequestHandler());
    filter.setAccessDeniedHandler(denied);
    return filter;
  }
}
