package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.util.Arrays;
import java.util.Objects;
import org.jspecify.annotations.Nullable;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.authentication.AuthenticationServiceException;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;

/**
 * API-only authentication with consumed credentials and current-context verification for0200. No
 * DB/HTTP/session writes. NK-WEB-001; FUN-001/AUT-001..004/MQ-004; UI226/232/234; SS314 §3.1/324
 * §6.1/352; SSC-043/PG-D-102/PT-WEB-063..067. Fixation is a later strategy.
 */
public final class MqAuthenticationProvider implements AuthenticationProvider {
  private final MqLoginClient login;
  private final MqLoginContextProbe probe;

  public MqAuthenticationProvider(MqLoginClient login, MqLoginContextProbe probe) {
    this.login = Objects.requireNonNull(login, "login");
    this.probe = Objects.requireNonNull(probe, "probe");
  }

  /** Only the exact standard token is accepted, with char[] credentials and trusted IP details. */
  @Override
  public Authentication authenticate(Authentication authentication) {
    Objects.requireNonNull(authentication, "authentication");
    Object credentials = authentication.getCredentials();
    try {
      if (!supports(authentication.getClass())
          || authentication.isAuthenticated()
          || !(authentication.getPrincipal() instanceof String username)
          || !(credentials instanceof char[] password)
          || !(authentication.getDetails() instanceof LoginClientAddress address))
        throw unavailable();
      MqLoginClient.Reply reply = login.exchange(username, password, address.value());
      if (reply.code() == ResultCode.AUTHENTICATION_FAILED) throw badCredentials();
      if (reply.code() == ResultCode.LOCKED)
        throw new MqLoginLockedException(reply.data().retryAfterSeconds());
      if (reply.code() == ResultCode.TEMPORARY_FAILURE) throw unavailable();
      var data = reply.data();
      var context = data.authenticationContextId().orElseThrow();
      if (reply.code() == ResultCode.IDEMPOTENT_SUCCESS && !probe.isActive(context))
        throw badCredentials();
      SessionPrincipal principal =
          new SessionPrincipal(
              data.username().orElseThrow(),
              data.role().orElseThrow(),
              context,
              data.issuedAt().orElseThrow());
      return ClosedWebAuthentication.authenticated(principal);
    } catch (MqLoginExchangeException failure) {
      if (failure.reason() == MqLoginExchangeException.Reason.INVALID_INPUT) throw badCredentials();
      throw unavailable();
    } finally {
      consumeCredentials(authentication, credentials);
    }
  }

  @Override
  public boolean supports(Class<?> authentication) {
    return Objects.requireNonNull(authentication, "authentication")
        == UsernamePasswordAuthenticationToken.class;
  }

  private static void consumeCredentials(
      Authentication authentication, @Nullable Object credentials) {
    if (credentials instanceof char[] password) Arrays.fill(password, '\0');
    if (authentication instanceof UsernamePasswordAuthenticationToken token)
      token.eraseCredentials();
  }

  private static BadCredentialsException badCredentials() {
    return new BadCredentialsException("login authentication failed");
  }

  private static AuthenticationServiceException unavailable() {
    return new AuthenticationServiceException("login service is unavailable");
  }
}
