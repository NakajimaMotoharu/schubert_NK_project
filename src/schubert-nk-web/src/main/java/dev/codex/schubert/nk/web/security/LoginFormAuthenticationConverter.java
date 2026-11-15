package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.session.SessionStoreException;
import jakarta.servlet.http.HttpServletRequest;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.NoSuchElementException;
import java.util.Objects;
import java.util.Set;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.AuthenticationConverter;

/**
 * Bounded form structure to an untrusted token, not authentication. Provider consumes/erases
 * char[]. Servlet temporary Strings are never persisted. NK-WEB-001; FUN-001/AUT-001..004;
 * UI226/234; SS313 §5,314 §3/4,352; PG-D-105/PT-WEB-084..089.
 */
public final class LoginFormAuthenticationConverter implements AuthenticationConverter {
  private static final Set<String> FORM_KEYS = Set.of("username", "password", "_csrf");
  private final CaddyClientAddressResolver addresses;

  public LoginFormAuthenticationConverter(CaddyClientAddressResolver addresses) {
    this.addresses = Objects.requireNonNull(addresses, "addresses");
  }

  @Override
  public Authentication convert(HttpServletRequest request) {
    Objects.requireNonNull(request, "request");
    try {
      if (!"POST".equals(request.getMethod())
          || !"/login".equals(request.getRequestURI())
          || !"UTF-8".equalsIgnoreCase(request.getCharacterEncoding()))
        throw new LoginFormRejectedException();
      String rawType = request.getContentType();
      if (rawType == null) throw new LoginFormRejectedException();
      MediaType type = MediaType.parseMediaType(rawType);
      if (!type.getType().equals("application")
          || !type.getSubtype().equals("x-www-form-urlencoded"))
        throw new LoginFormRejectedException();
      var charset = type.getCharset();
      if (charset != null && !charset.equals(StandardCharsets.UTF_8))
        throw new LoginFormRejectedException();
      String query = request.getQueryString();
      if (query != null) {
        for (String field : query.split("&", -1)) {
          String name = field.split("=", 2)[0];
          if (FORM_KEYS.contains(
              URLDecoder.decode(name, StandardCharsets.UTF_8).toLowerCase(Locale.ROOT)))
            throw new LoginFormRejectedException();
        }
      }
      var names = request.getParameterNames();
      if (names == null) throw new LoginFormRejectedException();
      while (names.hasMoreElements()) {
        String name = names.nextElement();
        if (name == null || !FORM_KEYS.contains(name)) throw new LoginFormRejectedException();
      }
      String username = single(request, "username");
      String password = single(request, "password");
      LoginClientAddress address = addresses.resolve(request);
      var token =
          UsernamePasswordAuthenticationToken.unauthenticated(username, password.toCharArray());
      token.setDetails(address);
      return token;
    } catch (IllegalArgumentException | IllegalStateException | NoSuchElementException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new LoginFormRejectedException();
    }
  }

  private static String single(HttpServletRequest request, String name) {
    String[] values = request.getParameterValues(name);
    if (values == null || values.length != 1 || values[0] == null || values[0].isEmpty())
      throw new LoginFormRejectedException();
    return values[0];
  }
}
