package dev.codex.schubert.nk.api.security;

import java.nio.CharBuffer;
import java.util.Arrays;
import java.util.Map;
import java.util.Objects;
import org.springframework.security.crypto.password.DelegatingPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.crypto.password.Pbkdf2PasswordEncoder;

/**
 * Generation-pinned password hash; raw arrays are consumed and never retained in fields/errors.
 * Trace: NK-AUT-001, AUT-001, DAT-009; UI226 §3; SS314 §4; PT-AUT-002.
 */
public final class PasswordHasher {
  private final PasswordEncoder encoder;
  private final PasswordPolicy policy = new PasswordPolicy();

  public PasswordHasher() {
    this(defaultEncoder());
  }

  /** SSC412/PT-AUT-HASHFAULT001: internal fault port; production noarg remains algorithm-pinned. */
  PasswordHasher(PasswordEncoder encoder) {
    this.encoder = Objects.requireNonNull(encoder, "encoder");
  }

  private static PasswordEncoder defaultEncoder() {
    Pbkdf2PasswordEncoder v1 = Pbkdf2PasswordEncoder.defaultsForSpringSecurity_v5_8();
    v1.setEncodeHashAsBase64(false);
    return new DelegatingPasswordEncoder("pbkdf2-v1", Map.of("pbkdf2-v1", v1));
  }

  /**
   * Caller must apply creation policy for new/reset passwords; consumes even on validation error.
   */
  public String encode(char[] password) {
    char[] normalized = policy.normalizeForLogin(password);
    try {
      return encoder.encode(CharBuffer.wrap(normalized));
    } finally {
      Arrays.fill(normalized, '\0');
    }
  }

  /** Unknown/malformed stored generations fail closed without echoing the stored or raw value. */
  public boolean matches(char[] password, String storedHash) {
    char[] normalized = policy.normalizeForLogin(password);
    try {
      requireHash(storedHash);
      return encoder.matches(CharBuffer.wrap(normalized), storedHash);
    } finally {
      Arrays.fill(normalized, '\0');
    }
  }

  /** The initial release has only v1. Future approved IDs must retain old readers in the map. */
  public boolean needsUpgrade(String storedHash) {
    requireHash(storedHash);
    return encoder.upgradeEncoding(storedHash);
  }

  private static void requireHash(String storedHash) {
    Objects.requireNonNull(storedHash, "storedHash");
    if (!storedHash.matches("\\{pbkdf2-v1}[0-9a-f]{96}")) {
      throw new IllegalArgumentException("stored password encoding is invalid or unsupported");
    }
  }
}
