package dev.codex.schubert.nk.api.idempotency;

import java.util.Objects;
import org.jspecify.annotations.Nullable;

/**
 * One layout-ordered field in the NKOP1 fingerprint input.
 *
 * <p>Trace: NK-MSG-002, SS 324 §3, PT-IDEM-001/002.
 */
public record CanonicalField(String name, String typeVersion, byte @Nullable [] value) {
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

  @Override
  public String toString() {
    return "CanonicalField[name=" + name + ", typeVersion=" + typeVersion + ", value=<redacted>]";
  }
}
