package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.session.SessionStoreException;
import java.security.MessageDigest;
import java.security.ProviderException;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.Objects;
import java.util.regex.Pattern;
import org.jspecify.annotations.Nullable;

/**
 * Immutable synchronizer secret; no HTTP decision or operation-token substitution.
 * NK-WEB-001/NK-AUT-001; FUN-001/AUT-004; UI226; SS314 §7.2.1/8.1/352 §3; PG-D-097/PT-WEB-032..035.
 * Nonnull factories, nullable submitted value explicitly means missing.
 */
public final class WebCsrfToken {
  private static final Pattern ALPHABET = Pattern.compile("[A-Za-z0-9_-]{64,128}");
  private final String value;

  private WebCsrfToken(String value) {
    this.value = value;
  }

  /** Accepts only the approved persisted token schema; malformed values never become empty. */
  public static WebCsrfToken parse(String value) {
    Objects.requireNonNull(value, "value");
    if (!ALPHABET.matcher(value).matches())
      throw new IllegalArgumentException("CSRF token is invalid");
    return new WebCsrfToken(value);
  }

  /** Generates32 CSPRNG bytes as64 lowercase hex, erasing the temporary bytes even on failure. */
  public static WebCsrfToken generate(SecureRandom random) {
    Objects.requireNonNull(random, "random");
    byte[] bytes = new byte[32];
    try {
      random.nextBytes(bytes);
      return parse(HexFormat.of().formatHex(bytes));
    } catch (ProviderException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new IllegalStateException("CSRF generation is unavailable");
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  /** For the hidden form synchronizer field only, never URL/log/metric or an operation token. */
  public String formValue() {
    return value;
  }

  /** Missing/malformed is false; all valid representations compare in fixed129-byte buffers. */
  public boolean matches(@Nullable String submitted) {
    if (submitted == null || !ALPHABET.matcher(submitted).matches()) return false;
    byte[] expected = padded(value);
    byte[] actual = padded(submitted);
    try {
      return MessageDigest.isEqual(expected, actual);
    } finally {
      Arrays.fill(expected, (byte) 0);
      Arrays.fill(actual, (byte) 0);
    }
  }

  private static byte[] padded(String value) {
    byte[] result = new byte[129];
    result[0] = (byte) value.length();
    for (int i = 0; i < value.length(); i++) result[i + 1] = (byte) value.charAt(i);
    return result;
  }

  @Override
  public String toString() {
    return "WebCsrfToken[REDACTED]";
  }
}
