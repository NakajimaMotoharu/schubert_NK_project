package dev.codex.schubert.nk.web.security;

import org.springframework.security.core.AuthenticationException;

/** Fixed structural form rejection, mapped to400 without MQ. PG-D-105/PT-WEB-084..089. */
public final class LoginFormRejectedException extends AuthenticationException {
  private static final long serialVersionUID = 1L;

  public LoginFormRejectedException() {
    // BUG-066/YKT-058/PT084..089: use the cause-free Spring constructor without suppression.
    super("login form is invalid");
  }
}
