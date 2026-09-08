package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.session.SessionStoreException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.util.Objects;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.session.SessionAuthenticationException;
import org.springframework.security.web.authentication.session.SessionAuthenticationStrategy;

/**
 * API-validated Login result to one encrypted session fixation, before successful HTTP handling.
 * NK-WEB-001; FUN-001/AUT-001..004; UI226; SS314 §7.2.6/331/352; SSC-044/PG-D-103/PT-WEB-068..075.
 * Do not compose with default CSRF null-save/extra rotation.
 */
public final class EncryptedSessionAuthenticationStrategy implements SessionAuthenticationStrategy {
  private final EncryptedSessionSecurityContextRepository contexts;

  public EncryptedSessionAuthenticationStrategy(
      EncryptedSessionSecurityContextRepository contexts) {
    this.contexts = Objects.requireNonNull(contexts, "contexts");
  }

  @Override
  public void onAuthentication(
      Authentication authentication, HttpServletRequest request, HttpServletResponse response) {
    Objects.requireNonNull(authentication, "authentication");
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    try {
      contexts.fixate(authentication, request);
    } catch (SessionStoreException failure) {
      throw new SessionAuthenticationException("login session is unavailable");
    }
  }
}
