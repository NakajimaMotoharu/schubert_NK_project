package dev.codex.schubert.nk.protocol.header;

import java.util.Objects;
import java.util.regex.Pattern;
import org.jspecify.annotations.Nullable;

/** Redacted 64-byte authentication context. Trace: NK-PRO-001, UI 232 §3, SS 323 §2. */
public final class AuthenticationContext {
  private static final Pattern FORMAT = Pattern.compile("[0-9a-f]{64}");
  private final String retainedWireValue;

  private AuthenticationContext(String wireValue) {
    this.retainedWireValue = wireValue;
  }

  public static AuthenticationContext of(String wireValue) {
    Objects.requireNonNull(wireValue, "wireValue");
    if (!FORMAT.matcher(wireValue).matches()) {
      throw new IllegalArgumentException(
          "authentication context must be 64 lowercase hexadecimal bytes");
    }
    return new AuthenticationContext(wireValue);
  }

  /** Intended only for wire encoding; never log or persist this value. */
  public String wireValue() {
    return retainedWireValue;
  }

  @Override
  public boolean equals(@Nullable Object other) {
    return other instanceof AuthenticationContext context
        && retainedWireValue.equals(context.retainedWireValue);
  }

  @Override
  public int hashCode() {
    return retainedWireValue.hashCode();
  }

  @Override
  public String toString() {
    return "AuthenticationContext[REDACTED]";
  }
}
