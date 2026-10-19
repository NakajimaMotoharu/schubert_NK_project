package dev.codex.schubert.nk.protocol.layout.semantic;

/** Media delivery disposition. Trace: AUD/MED/VID layouts, UI 235, PT-PRO-001-T04. */
public enum ContentDisposition implements WireEnum {
  INLINE("I"),
  ATTACHMENT("A");

  private final String encodedValue;

  ContentDisposition(String wireValue) {
    this.encodedValue = wireValue;
  }

  @Override
  public String wireValue() {
    return encodedValue;
  }
}
