package dev.codex.schubert.nk.api.idempotency;

import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.Arrays;
import java.util.Objects;
import org.jspecify.annotations.Nullable;

/**
 * One layout-ordered field in the NKOP1 fingerprint input.
 *
 * <p>Trace: NK-MSG-002, SS 324 §3, PT-IDEM-001/002.
 */
public record CanonicalField(String name, String typeVersion, byte @Nullable [] value)
    implements AutoCloseable {
  public CanonicalField {
    Objects.requireNonNull(name, "name");
    Objects.requireNonNull(typeVersion, "typeVersion");
    if (!name.matches("[A-Za-z0-9._-]{1,64}") || !typeVersion.matches("[A-Za-z0-9._-]{1,32}")) {
      throw new IllegalArgumentException("canonical field metadata is invalid");
    }
    value = value == null ? null : value.clone();
  }

  @Override
  public byte @Nullable [] value() {
    return value == null ? null : value.clone();
  }

  /** Required NFC UTF-8 X1 field. SSC-025/029; PT-MED-033/034 and Scenario Q01..Q04. */
  public static CanonicalField text(String name, String value) {
    Objects.requireNonNull(value, "value");
    return encoded(name, "X1", Normalizer.normalize(value, Normalizer.Form.NFC));
  }

  /** Required N1 decimal field, without wire padding. Same trace as text(). */
  public static CanonicalField number(String name, long value) {
    return encoded(name, "N1", Long.toString(value));
  }

  private static CanonicalField encoded(String name, String type, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    try {
      return new CanonicalField(name, type, bytes);
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  @Override
  public String toString() {
    return "CanonicalField[name=" + name + ", typeVersion=" + typeVersion + ", value=<redacted>]";
  }

  /** Terminal owner cleanup; do not use this field in a new fingerprint after close. BUG-027. */
  @Override
  public void close() {
    if (value != null) Arrays.fill(value, (byte) 0);
  }
}
