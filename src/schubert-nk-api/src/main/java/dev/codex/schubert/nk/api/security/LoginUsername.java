package dev.codex.schubert.nk.api.security;

import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.Locale;
import java.util.Objects;

/**
 * Display/input is 64 UTF-8 bytes; its Locale.ROOT lowercase comparison key may be 96 bytes.
 * NK-AUT-001; FUN-001/009/AUT-001; UI226/242; SS314/331; SSC-014/BUG-028/YKT-025;
 * PT-AUT-NAME-001..003. The display value, not its expanded key, is used for audit/wire text.
 */
public record LoginUsername(String value) {
  public LoginUsername {
    Objects.requireNonNull(value, "value");
    value = Normalizer.normalize(value, Normalizer.Form.NFC).trim();
    int bytes = value.getBytes(StandardCharsets.UTF_8).length;
    if (bytes < 1 || bytes > 64 || value.isBlank()) {
      throw new IllegalArgumentException("username display length is invalid");
    }
    if (value.codePoints().anyMatch(LoginUsername::invalidCodePoint)) {
      throw new IllegalArgumentException("username contains an invalid character");
    }
  }

  public String key() {
    return value.toLowerCase(Locale.ROOT);
  }

  private static boolean invalidCodePoint(int point) {
    return Character.isISOControl(point)
        || (point >= Character.MIN_SURROGATE && point <= Character.MAX_SURROGATE);
  }

  @Override
  public String toString() {
    return "LoginUsername[REDACTED]";
  }
}
