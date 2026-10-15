package dev.codex.schubert.quality;

final class GateField {
  private static Object instance;

  static Object instance() {
    if (instance == null) instance = new Object();
    return instance;
  }
}
