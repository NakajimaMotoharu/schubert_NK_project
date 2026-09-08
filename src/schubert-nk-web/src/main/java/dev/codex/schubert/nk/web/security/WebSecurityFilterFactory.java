package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.session.SpringEncryptedSessionRepository;
import dev.codex.schubert.nk.web.session.WebSessionFilterFactory;
import jakarta.servlet.Filter;
import java.util.List;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Supplier;
import org.springframework.security.web.DefaultSecurityFilterChain;
import org.springframework.security.web.FilterChainProxy;
import org.springframework.security.web.context.SecurityContextHolderFilter;
import org.springframework.security.web.firewall.HttpStatusRequestRejectedHandler;
import org.springframework.security.web.firewall.StrictHttpFirewall;
import org.springframework.security.web.savedrequest.RequestCacheAwareFilter;
import org.springframework.security.web.util.matcher.AnyRequestMatcher;
import org.springframework.web.filter.CharacterEncodingFilter;
import org.springframework.web.filter.CompositeFilter;

/**
 * One business security chain with explicit dependencies, not a production server/bootstrap.
 * Downstream MVC/Logout/API expiry and runtime logger policy remain application responsibilities.
 * NK-WEB-001; FUN-001..013/AUT-001..004/MON-004; UI221/226; SS311/313/314/342/351/352;
 * PG-D-113/114/116/PT-WEB-131..157; SSC-047; BUG-073/074/YKT-065/066.
 */
public final class WebSecurityFilterFactory {
  public Filter create(
      SpringEncryptedSessionRepository sessions,
      MqAuthenticationProvider provider,
      WebSecurityAudit audit,
      Supplier<UUID> ids) {
    Objects.requireNonNull(sessions, "sessions");
    Objects.requireNonNull(provider, "provider");
    Objects.requireNonNull(audit, "audit");
    Objects.requireNonNull(ids, "ids");
    var contexts = new EncryptedSessionSecurityContextRepository(sessions);
    var cache = new EncryptedSessionRequestCache(sessions);
    var access = new WebAccessFailureHandler(cache, audit);
    var chain =
        new DefaultSecurityFilterChain(
            AnyRequestMatcher.INSTANCE,
            List.of(
                new CharacterEncodingFilter("UTF-8", true, false),
                new WebSessionFilterFactory().create(sessions),
                new SecurityContextHolderFilter(contexts),
                new WebCsrfFilterFactory()
                    .create(
                        new EncryptedSessionCsrfTokenRepository(), new WebCsrfDeniedHandler(audit)),
                new MqFormLoginFilterFactory()
                    .create(
                        provider,
                        contexts,
                        new MqLoginSuccessHandler(contexts, cache, audit),
                        new MqLoginFailureHandler(audit)),
                new RequestCacheAwareFilter(cache),
                new ClosedServletSecurityFilter(),
                new WebDisplayContextFilter(),
                new WebAccessExceptionFilterFactory().create(access),
                new WebAuthorizationFilterFactory().create()));
    var errors = new CompositeFilter();
    errors.setFilters(
        List.of(new CharacterEncodingFilter("UTF-8", true, true), new WebErrorDispatchFilter()));
    var security = new FilterChainProxy(chain);
    security.setFirewall(new StrictHttpFirewall());
    security.setRequestRejectedHandler(new HttpStatusRequestRejectedHandler(400));
    var composite = new CompositeFilter();
    composite.setFilters(
        List.of(
            new WebSecurityHeaderFilterFactory().create(),
            new CaddyTransportContextFilter(ids, new CaddyClientAddressResolver(), audit),
            new WebInfrastructureFailureFilter(),
            new InternalErrorDispatchRouter(security, errors)));
    return composite;
  }
}
