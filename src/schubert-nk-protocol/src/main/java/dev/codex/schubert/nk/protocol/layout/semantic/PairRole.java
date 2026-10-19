package dev.codex.schubert.nk.protocol.layout.semantic;

/** Music pair role. Trace: MTRRSP01, UI 235, PT-PRO-001-T04. */
public enum PairRole implements WireEnum {
  MAIN("M"),
  INSTRUMENTAL("I"),
  NONE("N");

  private final String encodedValue;

  PairRole(String wireValue) {
    this.encodedValue = wireValue;
  }

  @Override
  public String wireValue() {
    return encodedValue;
  }
}
