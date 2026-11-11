package dev.codex.schubert.nk.protocol.layout.semantic;

import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.Objects;
import org.jspecify.annotations.Nullable;

/**
 * Root-relative logical path; it is data only and never performs file-system resolution. Trace:
 * NK-PRO-001, UI 243, SS 323/333, PT-PRO-001-T03, BUG-004/YKT-004.
 */
public final class RelativePath {
  private static final int MAXIMUM_WIRE_BYTES = 512;
  private static final int MAXIMUM_SEGMENT_BYTES = 255;
  private final String value;

  private RelativePath(String value) {
    this.value = value;
  }

  public static RelativePath of(String input) {
    Objects.requireNonNull(input, "input");
    String value = Normalizer.normalize(input, Normalizer.Form.NFC);
    validate(value);
    return new RelativePath(value);
  }

  private static void validate(String value) {
    if (value.isEmpty()
        || !StandardCharsets.UTF_8.newEncoder().canEncode(value)
        || PathSyntax.isAbsoluteOrDriveQualified(value)
        || value.endsWith("/")
        || value.indexOf('\\') >= 0
        || value.getBytes(StandardCharsets.UTF_8).length > MAXIMUM_WIRE_BYTES) {
      throw new IllegalArgumentException("relative path has an invalid root, separator, or length");
    }
    for (String segment : value.split("/", -1)) {
      if (segment.isEmpty()
          || segment.equals(".")
          || segment.equals("..")
          || segment.getBytes(StandardCharsets.UTF_8).length > MAXIMUM_SEGMENT_BYTES
          || PathSyntax.containsControl(segment)) {
        throw new IllegalArgumentException("relative path contains an invalid segment");
      }
    }
  }

  public String wireValue() {
    return value;
  }

  @Override
  public boolean equals(@Nullable Object other) {
    return other instanceof RelativePath path && value.equals(path.value);
  }

  @Override
  public int hashCode() {
    return value.hashCode();
  }

  @Override
  public String toString() {
    return "RelativePath[REDACTED]";
  }
}
