package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.session.SessionStoreException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.Objects;
import java.util.function.Supplier;
import org.jspecify.annotations.Nullable;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.CsrfTokenRequestAttributeHandler;
import org.springframework.security.web.csrf.CsrfTokenRequestHandler;

/** NK-WEB-001; FUN-001/AUT-004; UI226; SS313/314 §8.1/352; PG-D-100/PT-WEB-051/052. */
public final class FormCsrfTokenRequestHandler implements CsrfTokenRequestHandler {
  private static final String CSRF_QUERY_PARAMETER = "_csrf";

  @Override
  public void handle(
      HttpServletRequest request, HttpServletResponse response, Supplier<CsrfToken> deferred) {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Objects.requireNonNull(deferred, "deferred");
    new CsrfTokenRequestAttributeHandler().handle(request, response, deferred);
  }

  @Override
  public @Nullable String resolveCsrfTokenValue(HttpServletRequest request, CsrfToken token) {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(token, "token");
    String query = request.getQueryString();
    try {
      if (query != null) {
        for (String parameter : query.split("&", -1)) {
          String key = parameter.split("=", 2)[0];
          if (CSRF_QUERY_PARAMETER.equals(URLDecoder.decode(key, StandardCharsets.UTF_8)))
            return null;
        }
      }
      String[] values = request.getParameterValues("_csrf");
      if (values == null || values.length != 1 || values[0] == null) return null;
      return WebCsrfToken.parse(values[0]).formValue();
    } catch (IllegalArgumentException malformed) {
      SessionStoreException.preserveFatal(malformed);
      return null;
    }
  }
}
