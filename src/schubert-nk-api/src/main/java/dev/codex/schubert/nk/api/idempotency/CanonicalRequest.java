package dev.codex.schubert.nk.api.idempotency;

import java.text.Normalizer;
import java.util.List;
import java.util.Objects;

/**
 * Redacted NKOP1 request input, immutable during use; owner closes secret fields after all lookups.
 *
 * <p>Trace: NK-MSG-002, SS 324 §3, PT-IDEM-001/002.
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
    return normalized;
  }

  /** Terminal caller-scope cleanup, including retry/failure exits. BUG-027/YKT-024. */
  @Override
  public void close() {
    fields.forEach(CanonicalField::close);
  }

  @Override
  public String toString() {
    return "CanonicalRequest[layoutId="
        + layoutId
        + ", layoutVersion="
        + layoutVersion
        + ", owner/target/fields=<redacted>]";
  }
}
