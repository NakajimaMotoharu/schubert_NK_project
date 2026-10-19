package dev.codex.schubert.nk.protocol.layout.semantic;

/** Video descriptor category. Trace: VIDRSP01, UI 235, PT-PRO-001-T04. */
public enum VideoCategory implements WireEnum {
  MAIN("MAIN"),
  SUBTRACK("SUBTRACK"),
  OVA("OVA"),
  OPENING("OPENING");

  private final String encodedValue;

  VideoCategory(String wireValue) {
    this.encodedValue = wireValue;
  }

  @Override
  public String wireValue() {
    return encodedValue;
  }
}
