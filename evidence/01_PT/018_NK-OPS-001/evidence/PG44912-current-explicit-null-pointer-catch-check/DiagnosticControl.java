final class DiagnosticControl {
  void simple() {
    try { } catch (NullPointerException failure) { throw failure; }
  }
  void qualified() {
    try { } catch (java.lang.NullPointerException failure) { throw failure; }
  }
  void combined() {
    try { } catch (IllegalArgumentException | NullPointerException failure) { throw failure; }
  }
  void ordinary() {
    try { } catch (IllegalStateException failure) { throw failure; }
  }
}
