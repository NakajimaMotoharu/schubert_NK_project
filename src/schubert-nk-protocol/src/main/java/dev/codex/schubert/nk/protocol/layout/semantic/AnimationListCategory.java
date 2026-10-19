package dev.codex.schubert.nk.protocol.layout.semantic;

/** Animation list request category. Trace: ANLREQ01, UI 235, PT-PRO-001-T04. */
public enum AnimationListCategory implements WireEnum {
  MAIN("MAIN"),
  OVA("OVA");

  private final String encodedValue;

  AnimationListCategory(String wireValue) {
    this.encodedValue = wireValue;
  }

  @Override
  public String wireValue() {
    return encodedValue;
  }
}
