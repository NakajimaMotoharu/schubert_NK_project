package dev.codex.schubert.nk.web.session;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.Base64;
import java.util.HexFormat;
import java.util.Objects;

/**
 * Canonical opaque cookie identity, never an authentication grant or database raw value.
 * NK-WEB-001/NK-AUT-001; FUN-001/AUT-001..004; UI226; SS314 §7/352 §3; PG-D-093/PT-WEB-001..004.
 * Nonnull arguments; invalid input has a fixed, secret-free error.
 */
public final class WebSessionId {
  private final String raw;

  private WebSessionId(String raw) {
    this.raw = raw;
  }

  public static WebSessionId parse(String raw) {
    Objects.requireNonNull(raw, "raw");
    require(raw.matches("[A-Za-z0-9_-]{43}"));
    byte[] decoded = Base64.getUrlDecoder().decode(raw);
    try {
      require(Base64.getUrlEncoder().withoutPadding().encodeToString(decoded).equals(raw));
      return new WebSessionId(raw);
    } finally {
      Arrays.fill(decoded, (byte) 0);
    }
  }

  /** Caller supplies CSPRNG; ownership stays with caller, temporary output is erased on failure. */
  public static WebSessionId generate(SecureRandom random) {
    Objects.requireNonNull(random, "random");
    byte[] bytes = new byte[32];
    try {
      random.nextBytes(bytes);
      return parse(Base64.getUrlEncoder().withoutPadding().encodeToString(bytes));
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  /** Only for the configured Secure/HttpOnly cookie. Never use in HTML, SQL or logs. */
  public String cookieValue() {
    return raw;
  }

  /** Per-call digest avoids shared mutable crypto state; SHA-256 is a required JDK algorithm. */
  public String lookupHash() throws NoSuchAlgorithmException {
    byte[] bytes = raw.getBytes(StandardCharsets.US_ASCII);
    try {
      byte[] digest = MessageDigest.getInstance("SHA-256").digest(bytes);
      try {
        return HexFormat.of().formatHex(digest);
      } finally {
        Arrays.fill(digest, (byte) 0);
      }
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("web session identity is invalid");
  }

  @Override
  public String toString() {
    return "WebSessionId[REDACTED]";
  }
}
