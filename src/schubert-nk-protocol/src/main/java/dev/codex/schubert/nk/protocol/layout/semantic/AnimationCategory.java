package dev.codex.schubert.nk.protocol.layout.semantic;

/** Animation record category. Trace: ANLRSP01, UI 235, PT-PRO-001-T04. */
public enum AnimationCategory implements WireEnum {
  MAIN("MAIN"),
  SUBTRACK("SUBTRACK"),
  OVA("OVA");

  private final String encodedValue;

  AnimationCategory(String wireValue) {
    this.encodedValue = wireValue;
  }

  @Override
  public String wireValue() {
    return encodedValue;
  }
}
