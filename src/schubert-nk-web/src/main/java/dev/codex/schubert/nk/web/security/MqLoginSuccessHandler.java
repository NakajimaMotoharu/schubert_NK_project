package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit.Event;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit.Route;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.util.Objects;
import java.util.Optional;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextImpl;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;

/**
 * Redirect only after the custom strategy persisted the identical closed principal. No second
 * fixation or API call. NK-WEB-001; FUN-001/AUT-001..004/MON-004; UI226/232; SS313/314/351/352;
 * SSC-046/PG-D-110/PT-WEB-113..120.
 */
public final class MqLoginSuccessHandler implements AuthenticationSuccessHandler {
  private final EncryptedSessionSecurityContextRepository contexts;
  private final EncryptedSessionRequestCache cache;
  private final WebSecurityAudit audit;

  public MqLoginSuccessHandler(
      EncryptedSessionSecurityContextRepository contexts,
      EncryptedSessionRequestCache cache,
      WebSecurityAudit audit) {
    this.contexts = Objects.requireNonNull(contexts, "contexts");
    this.cache = Objects.requireNonNull(cache, "cache");
    this.audit = Objects.requireNonNull(audit, "audit");
  }

  @Override
  public void onAuthenticationSuccess(
      HttpServletRequest request, HttpServletResponse response, Authentication authentication) {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Objects.requireNonNull(authentication, "authentication");
    var transport = WebRequestContext.require(request);
    var principal =
        ClosedWebAuthentication.principal(authentication).orElseThrow(SessionStoreException::new);
    // This repository's save is a read-only equality guard, not a write or fixation.
    contexts.saveContext(new SecurityContextImpl(authentication), request, response);
    var saved = cache.getRequest(request, response);
    String location = saved == null ? "/" : saved.getRedirectUrl();
    audit.record(
        transport.requestId(),
        Event.LOGIN_SUCCEEDED,
        Optional.of(transport.clientAddress().value()),
        Optional.of(principal),
        0,
        Route.LOGIN);
    // Do not encodeRedirectURL: a cookie identifier must never be rewritten into the URL.
    response.setHeader("Location", location);
    response.setStatus(302);
  }
}
