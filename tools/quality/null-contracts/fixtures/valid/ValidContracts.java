package dev.codex.schubert.nk.quality.canary;

import java.util.List;
import org.jspecify.annotations.Nullable;

/** PT-QUALITY-001 positive oracle: explicit null handling and non-null collection elements. */
final class ValidContracts {
  static int length(@Nullable String value) {
    return value == null ? 0 : value.length();
  }

  static int firstLength(List<String> values) {
    return values.getFirst().length();
  }
}
