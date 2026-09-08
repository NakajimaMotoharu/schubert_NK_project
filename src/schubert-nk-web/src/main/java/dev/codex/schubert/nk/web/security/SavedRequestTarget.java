package dev.codex.schubert.nk.web.security;

import java.net.URI;
import java.net.URISyntaxException;
import java.nio.charset.StandardCharsets;
import java.util.Objects;
import java.util.regex.Pattern;

/**
 * Bounded same-origin GET location only; caller must additionally apply the controller allowlist.
 * NK-WEB-001/NK-AUT-001; FUN-001/AUT-001..004; UI221/226; SS314 §7/352 §3;
 * PG-D-093/PT-WEB-005..008. Preserves query values; contains no body or authentication grant.
 */
public final class SavedRequestTarget {
  private static final Pattern ENCODED_PATH_DELIMITER =
      Pattern.compile("%(?:2e|2f|5c)", Pattern.CASE_INSENSITIVE);
  // BUG-059/YKT-054/PT-WEB-006/045: URI.normalize retains leading parent segments.
  private static final Pattern DOT_SEGMENT = Pattern.compile("(?:^|/)\\.{1,2}(?:/|$)");
  private final String location;

  private SavedRequestTarget(String location) {
    this.location = location;
  }

  public static SavedRequestTarget fromGet(String method, String target) {
    Objects.requireNonNull(method, "method");
    Objects.requireNonNull(target, "target");
    require(method.equals("GET"));
    require(StandardCharsets.UTF_8.newEncoder().canEncode(target));
    require(target.getBytes(StandardCharsets.UTF_8).length <= 2048);
    require(!target.contains("\u2028"));
    require(!target.contains("\u2029"));
    URI uri;
    try {
      uri = new URI(target);
    } catch (URISyntaxException invalid) {
      throw invalid();
    }
    String path = uri.getRawPath();
    if (path == null) throw invalid();
    require(!uri.isAbsolute());
    require(path.startsWith("/") && !target.startsWith("//"));
    require(uri.getRawFragment() == null);
    require(!DOT_SEGMENT.matcher(path).find());
    require(path.equals(uri.normalize().getRawPath()));
    require(!ENCODED_PATH_DELIMITER.matcher(path).find());
    return new SavedRequestTarget(target);
  }

  /** Only for validated redirect/session persistence; never concatenate into HTML or logs. */
  public String location() {
    return location;
  }

  private static void require(boolean valid) {
    if (!valid) throw invalid();
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("saved GET target is invalid");
  }

  @Override
  public String toString() {
    return "SavedRequestTarget[REDACTED]";
  }
}
