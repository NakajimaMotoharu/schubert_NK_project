package dev.codex.schubert.nk.protocol.layout;

import java.util.Objects;
import java.util.regex.Pattern;

/** Eight-byte ASCII data-layout identifier. Trace: NK-PRO-001, UI 232 §3. */
public record LayoutId(String value) implements Comparable<LayoutId> {
  private static final Pattern FORMAT = Pattern.compile("[A-Z0-9]{8}");

  public LayoutId {
    Objects.requireNonNull(value, "value");
    if (!FORMAT.matcher(value).matches()) {
      throw new LayoutValidationException("layout ID must be eight uppercase ASCII letters/digits");
    }
  }

  @Override
  public int compareTo(LayoutId other) {
    Objects.requireNonNull(other, "other");
    return value.compareTo(other.value);
  }

  @Override
  public String toString() {
    return value;
  }
}
