package dev.codex.schubert.nk.web.security;

import org.springframework.security.core.AuthenticationException;

/** Fixed proxy rejection, mapped to403 by the HTTP boundary. PG-D-105/PT-WEB-082..089. */
public final class CaddyRequestRejectedException extends AuthenticationException {
  private static final long serialVersionUID = 1L;

  public CaddyRequestRejectedException() {
    // BUG-066/YKT-058/PT082..089: Spring's cause overload is non-null; no cause is retained.
    super("request proxy is invalid");
  }
}
