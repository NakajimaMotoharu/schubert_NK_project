package dev.codex.schubert.nk.api.idempotency;

import java.text.Normalizer;
import java.util.List;
import java.util.Objects;

/**
 * Redacted NKOP1 request input, immutable during use; owner closes secret fields after all lookups.
 *
 * <p>Trace: NK-MSG-002, SS 324 §3, SS351/SSC-458, PT-IDEM-001/002.
 */
public record CanonicalRequest(
    String ownerScope,
    String layoutId,
    String layoutVersion,
    String target,
    List<CanonicalField> fields)
    implements AutoCloseable {
  public CanonicalRequest {
    ownerScope = normalizeRequired(ownerScope, "ownerScope");
    target = normalizeRequired(target, "target");
    Objects.requireNonNull(layoutId, "layoutId");
    Objects.requireNonNull(layoutVersion, "layoutVersion");
    Objects.requireNonNull(fields, "fields");
    if (!layoutId.matches("[A-Z0-9]{8}") || !layoutVersion.matches("[0-9]{3}")) {
      throw new IllegalArgumentException("layout identity is invalid");
    }
    fields = List.copyOf(fields);
  }

  private static String normalizeRequired(String value, String name) {
    Objects.requireNonNull(value, name);
    String normalized = Normalizer.normalize(value, Normalizer.Form.NFC);
    if (normalized.isEmpty()) {
      throw new IllegalArgumentException(name + " must not be empty");
    }
    // SS3243/BUG2669: validate scalars without allocating an unwipeable encoded secret copy.
    if (normalized
        .codePoints()
        .anyMatch(
            codePoint ->
                codePoint >= Character.MIN_SURROGATE && codePoint <= Character.MAX_SURROGATE)) {
      throw new IllegalArgumentException("canonical text contains malformed UTF-16");
    }
    return normalized;
  }

  /** Terminal caller-scope cleanup, including retry/failure exits. BUG-027/YKT-024. */
  @Override
  public void close() {
    fields.forEach(CanonicalField::close);
  }

  @Override
  public String toString() {
    return "CanonicalRequest[<redacted>]";
  }
}
