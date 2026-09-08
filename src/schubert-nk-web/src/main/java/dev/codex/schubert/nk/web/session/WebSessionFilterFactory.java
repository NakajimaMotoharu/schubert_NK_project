package dev.codex.schubert.nk.web.session;

import java.util.Objects;
import org.springframework.session.web.http.CookieHttpSessionIdResolver;
import org.springframework.session.web.http.DefaultCookieSerializer;
import org.springframework.session.web.http.SessionRepositoryFilter;

/** NK-WEB-001; FUN-001/AUT-001..004; UI226; SS314 §7.1/7.2.5; PT-WEB-048/049. */
public final class WebSessionFilterFactory {
  public SessionRepositoryFilter<SpringWebSession> create(
      SpringEncryptedSessionRepository repository) {
    Objects.requireNonNull(repository, "repository");
    var serializer = new DefaultCookieSerializer();
    serializer.setCookieName("SCHUBERT_NK_SESSION");
    serializer.setUseSecureCookie(true);
    serializer.setUseHttpOnlyCookie(true);
    serializer.setSameSite("Lax");
    serializer.setCookiePath("/");
    serializer.setUseBase64Encoding(false);
    serializer.setCookieMaxAge(-1);
    var resolver = new CookieHttpSessionIdResolver();
    resolver.setCookieSerializer(serializer);
    var filter = new SessionRepositoryFilter<>(repository);
    filter.setHttpSessionIdResolver(resolver);
    return filter;
  }
}
