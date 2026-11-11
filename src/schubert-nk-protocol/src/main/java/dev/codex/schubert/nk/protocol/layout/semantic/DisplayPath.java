package dev.codex.schubert.nk.protocol.layout.semantic;

import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.Objects;
import org.jspecify.annotations.Nullable;

/**
 * NFC display-only path that must never be passed to a file-system resolver. Trace: NK-PRO-001, UI
 * 243, SS 323/333, PT-PRO-001-T03, BUG-004/YKT-004.
 */
public final class DisplayPath {
  private static final int MAXIMUM_WIRE_BYTES = 512;
  private final String value;

  private DisplayPath(String value) {
    this.value = value;
  }

  public static DisplayPath of(String input) {
    Objects.requireNonNull(input, "input");
    String value = Normalizer.normalize(input, Normalizer.Form.NFC);
    if (value.isEmpty()
        || !StandardCharsets.UTF_8.newEncoder().canEncode(value)
        || PathSyntax.isAbsoluteOrDriveQualified(value)
        || value.getBytes(StandardCharsets.UTF_8).length > MAXIMUM_WIRE_BYTES
        || PathSyntax.containsControl(value)
        || PathSyntax.containsParentSegment(value)) {
      throw new IllegalArgumentException(
          "display path is empty, absolute, traversing, too long, or contains control data");
    }
    return new DisplayPath(value);
  }

  public String wireValue() {
    return value;
  }

  @Override
  public boolean equals(@Nullable Object other) {
    return other instanceof DisplayPath path && value.equals(path.value);
  }

  @Override
  public int hashCode() {
    return value.hashCode();
  }

  @Override
  public String toString() {
    return "DisplayPath[REDACTED]";
  }
}
