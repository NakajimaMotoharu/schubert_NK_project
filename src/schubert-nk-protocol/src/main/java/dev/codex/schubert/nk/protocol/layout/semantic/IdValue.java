package dev.codex.schubert.nk.protocol.layout.semantic;

/** Shared N12 identifier invariant. Trace: NK-PRO-001, SS 323 section 2. */
interface IdValue {
  long MAXIMUM = 999_999_999_999L;

  static void validate(long value) {
    if (value < 1 || value > MAXIMUM) {
      throw new IllegalArgumentException("protocol ID must be between 1 and 999999999999");
    }
  }
}
