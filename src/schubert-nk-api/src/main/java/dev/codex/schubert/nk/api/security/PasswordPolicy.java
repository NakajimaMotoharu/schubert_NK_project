package dev.codex.schubert.nk.api.security;

import java.nio.CharBuffer;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.Arrays;
import java.util.Objects;

/**
 * Password normalization with distinct login and creation policies; consumes caller char arrays.
 * Trace: NK-AUT-001, FUN-001/009, AUT-001; UI225/226 §4; SS314 §4; PT-AUT-001.
 */
public final class PasswordPolicy {
  /**
   * UI226 permits existing-password login at 1..256 UTF-8 bytes, not creation's 12-char minimum.
   */
  public char[] normalizeForLogin(char[] password) {
    Objects.requireNonNull(password, "password");
    try {
      String normalized = Normalizer.normalize(CharBuffer.wrap(password), Normalizer.Form.NFC);
      validateWire(normalized);
      return normalized.toCharArray();
    } finally {
      Arrays.fill(password, '\0');
    }
  }

  /**
   * SS314 creation policy counts Unicode code points after NFC; does not force character classes.
   */
  public char[] normalizeForCreation(char[] password, String username) {
    char[] normalized = normalizeForLogin(password);
    try {
      Objects.requireNonNull(username, "username");
      String value = new String(normalized);
      int count = value.codePointCount(0, value.length());
      if (count < 12 || count > 128) {
        throw new IllegalArgumentException("password creation length is invalid");
      }
      String account = Normalizer.normalize(username.trim(), Normalizer.Form.NFC);
      if (value.equalsIgnoreCase(account)) {
        throw new IllegalArgumentException("password must differ from username");
      }
      return normalized.clone();
    } finally {
      Arrays.fill(normalized, '\0');
    }
  }

  private static void validateWire(String value) {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    try {
      if (bytes.length < 1 || bytes.length > 256 || value.endsWith(" ")) {
        throw new IllegalArgumentException("password wire length or trailing space is invalid");
      }
      if (value.codePoints().anyMatch(PasswordPolicy::invalidCodePoint)) {
        throw new IllegalArgumentException("password contains an invalid character");
      }
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  private static boolean invalidCodePoint(int codePoint) {
    return Character.isISOControl(codePoint)
        || (codePoint >= Character.MIN_SURROGATE && codePoint <= Character.MAX_SURROGATE);
  }
}
