package dev.codex.schubert.nk.web.security;

import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.Objects;
import java.util.Set;
import java.util.regex.Pattern;

/**
 * Screen-family allowlist, not authorization or business ID validation. NK-WEB-001;
 * FUN-001/AUT-001..004; UI221/226; SS313 §4/9,314 §3/7.2,352; PG-D-104/PT-WEB-076..081.
 */
public final class SavedScreenTarget {
  private static final Pattern SCREEN =
      Pattern.compile(
          "/(?:|search|logs|scenarios(?:/[^/]+(?:/[^/]+)?)?|animation(?:/(?:main|ova|opening|videos/[^/]+))?|music(?:/(?!media(?:/|$)|download(?:/|$))[^/]+(?:/[^/]+)?)?|admin/users(?:/[^/]+)?|questions(?:/[^/]+|/accepted/[^/]+)?|notifications(?:/[^/]+)?)");
  private static final Set<String> SECRET_NAMES =
      Set.of(
          "password",
          "passwordconfirmation",
          "confirmpassword",
          "_csrf",
          "csrf",
          "csrftoken",
          "operationtoken",
          "authenticationcontext",
          "authenticationcontextid",
          "session",
          "sessionid",
          "token",
          "jsessionid",
          "schubert_nk_session");
  // BUG-065/PT077/080: servlet path-parameter session IDs are not approved screen identifiers.
  private static final Pattern PATH_PARAMETER = Pattern.compile(";|%3b", Pattern.CASE_INSENSITIVE);
  private final String location;

  private SavedScreenTarget(String location) {
    this.location = location;
  }

  /** Preserves the approved relative URL; invalid methods/URLs throw a fixed value-free error. */
  public static SavedScreenTarget fromGet(String method, String location) {
    Objects.requireNonNull(method, "method");
    Objects.requireNonNull(location, "location");
    try {
      String safe = SavedRequestTarget.fromGet(method, location).location();
      // BUG-063/YKT-057: safe is already a validated relative URL. Preserve its raw spelling
      // without losing the non-null path contract by parsing it into a second URI object.
      int separator = safe.indexOf('?');
      String path = separator < 0 ? safe : safe.substring(0, separator);
      if (PATH_PARAMETER.matcher(path).find()) throw invalid();
      if (!SCREEN.matcher(path).matches()) throw invalid();
      if (separator >= 0) {
        String query = safe.substring(separator + 1);
        for (String field : query.split("&", -1)) {
          String name = field.split("=", 2)[0];
          String decoded = URLDecoder.decode(name, StandardCharsets.UTF_8).toLowerCase(Locale.ROOT);
          if (SECRET_NAMES.contains(decoded)) throw invalid();
        }
      }
      return new SavedScreenTarget(safe);
    } catch (IllegalArgumentException failure) {
      throw invalid();
    }
  }

  /** For redirect/session persistence only; never interpolate into HTML or diagnostics. */
  public String location() {
    return location;
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("saved screen target is invalid");
  }

  @Override
  public String toString() {
    return "SavedScreenTarget[REDACTED]";
  }
}
