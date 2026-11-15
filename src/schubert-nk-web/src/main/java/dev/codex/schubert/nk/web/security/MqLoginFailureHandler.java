package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit.Event;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit.Route;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.authentication.AuthenticationFailureHandler;

/**
 * Current-compatible form redirects; transport/storage failure is not bad credentials. Transiently
 * checks fatal exception graphs, never logs or stores exception diagnostics and never reads form
 * data or session. NK-WEB-001; FUN-001/AUT-001..004/MON-004; UI226/232; SS313/314/351/352;
 * SSC-046/PG-D-110/PT-WEB-113..120. Common SYSTEM/MQ logging belongs to the outer error boundary.
 */
public final class MqLoginFailureHandler implements AuthenticationFailureHandler {
  private final WebSecurityAudit audit;

  public MqLoginFailureHandler(WebSecurityAudit audit) {
    this.audit = Objects.requireNonNull(audit, "audit");
  }

  @Override
  public void onAuthenticationFailure(
      HttpServletRequest request, HttpServletResponse response, AuthenticationException failure)
      throws IOException {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Objects.requireNonNull(failure, "failure");
    var transport = WebRequestContext.require(request);
    JmsRequestReplyException.preserveFatal(failure);
    if (failure instanceof MqLoginLockedException locked) {
      audit.record(
          transport.requestId(),
          Event.LOGIN_LOCKED,
          Optional.of(transport.clientAddress().value()),
          Optional.empty(),
          locked.retryAfterSeconds(),
          Route.LOGIN);
      response.setHeader("Retry-After", Integer.toString(locked.retryAfterSeconds()));
      response.setHeader("Location", "/login?locked");
      response.setStatus(302);
    } else if (failure instanceof BadCredentialsException) {
      audit.record(
          transport.requestId(),
          Event.LOGIN_FAILED,
          Optional.of(transport.clientAddress().value()),
          Optional.empty(),
          0,
          Route.LOGIN);
      response.setHeader("Location", "/login?error");
      response.setStatus(302);
    } else if (failure instanceof LoginFormRejectedException) {
      response.sendError(400);
    } else if (failure instanceof CaddyRequestRejectedException) {
      response.setStatus(403);
      audit.record(
          transport.requestId(),
          Event.PROXY_DENIED,
          Optional.empty(),
          Optional.empty(),
          0,
          Route.LOGIN);
      // Transport trust was lost after the initial guard: do not error-redispatch (BUG-070).
    } else {
      response.sendError(503);
    }
  }
}
