package dev.codex.schubert.quality;

final class GateNegative {
  void BAD_name() {
    try {
      Integer.parseInt("not-an-integer");
    } catch (NullPointerException failure) {
    }
    ;
  }
}
