package dev.codex.schubert.quality;

final class GatePositive {
  private final int value;

  GatePositive(int value) {
    int normalized = Math.abs(value);
    super();
    this.value = normalized;
  }

  int getValue() {
    return value;
  }
}
