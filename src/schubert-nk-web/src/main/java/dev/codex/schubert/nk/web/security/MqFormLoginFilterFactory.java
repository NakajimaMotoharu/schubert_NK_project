package dev.codex.schubert.nk.web.security;

import java.util.Objects;
import org.springframework.security.web.authentication.AbstractAuthenticationProcessingFilter;
import org.springframework.security.web.authentication.AuthenticationFailureHandler;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;

/**
 * Login filter only; requires configured Session/Holder/CSRF filters before it. Explicit handlers
 * must not persist authentication exceptions. NK-WEB-001; FUN-001/AUT-001..004; UI226;
 * SS313/314/352; PG-D-105/PT-WEB-084..089.
 */
public final class MqFormLoginFilterFactory {
  public AbstractAuthenticationProcessingFilter create(
      MqAuthenticationProvider provider,
      EncryptedSessionSecurityContextRepository contexts,
      AuthenticationSuccessHandler success,
      AuthenticationFailureHandler failure) {
    Objects.requireNonNull(provider, "provider");
    Objects.requireNonNull(contexts, "contexts");
    Objects.requireNonNull(success, "success");
    Objects.requireNonNull(failure, "failure");
    var filter =
        new AbstractAuthenticationProcessingFilter(
            request ->
                "POST".equals(request.getMethod()) && "/login".equals(request.getRequestURI()),
            provider::authenticate) {};
    filter.setAuthenticationConverter(
        new LoginFormAuthenticationConverter(new CaddyClientAddressResolver()));
    filter.setSessionAuthenticationStrategy(new EncryptedSessionAuthenticationStrategy(contexts));
    filter.setSecurityContextRepository(contexts);
    filter.setAuthenticationSuccessHandler(success);
    filter.setAuthenticationFailureHandler(failure);
    filter.setMfaEnabled(false);
    filter.setAllowSessionCreation(false);
    return filter;
  }
}
