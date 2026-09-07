package dev.codex.schubert.nk.quality.canary;

import java.util.List;
import org.jspecify.annotations.Nullable;

/** PT-QUALITY-001 negative oracle: each of these contracts must fail compilation. */
final class InvalidContracts {
  static int nullableDereference(@Nullable String value) {
    return value.length();
  }

  static String nullableReturn() {
    return null;
  }

  static int nullableElement(List<@Nullable String> values) {
    return values.getFirst().length();
  }

  static int nullableArgument() {
    return nonNullLength(null);
  }

  private static int nonNullLength(String value) {
    return value.length();
  }
}
