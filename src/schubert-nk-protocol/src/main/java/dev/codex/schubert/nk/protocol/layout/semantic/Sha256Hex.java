package dev.codex.schubert.nk.protocol.layout.semantic;

import java.util.Objects;
import java.util.regex.Pattern;
import org.jspecify.annotations.Nullable;

/**
 * Lowercase SHA-256 hexadecimal value whose textual rendering is always redacted. Trace:
 * NK-PRO-001, SS 323 section 2, PT-PRO-001-T03.
 */
public final class Sha256Hex {
  private static final Pattern FORMAT = Pattern.compile("[0-9a-f]{64}");
  private final String value;

  private Sha256Hex(String value) {
    this.value = value;
  }

  public static Sha256Hex of(String value) {
    Objects.requireNonNull(value, "value");
    if (!FORMAT.matcher(value).matches()) {
      throw new IllegalArgumentException("SHA-256 must be 64 lowercase hexadecimal characters");
    }
    return new Sha256Hex(value);
  }

  public String wireValue() {
    return value;
  }

  @Override
  public boolean equals(@Nullable Object other) {
    return other instanceof Sha256Hex sha256 && value.equals(sha256.value);
  }

  @Override
  public int hashCode() {
    return value.hashCode();
  }

  @Override
  public String toString() {
    return "Sha256Hex[REDACTED]";
  }
}
