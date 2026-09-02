package dev.codex.schubert.nk.protocol.layout.semantic;

/** Media delivery disposition. Trace: AUD/MED/VID layouts, UI 235, PT-PRO-001-T04. */
public enum ContentDisposition implements WireEnum {
  INLINE("I"),
  ATTACHMENT("A");

  private final String wireValue;

  ContentDisposition(String wireValue) {
    this.wireValue = wireValue;
  }

  @Override
  public String wireValue() {
    return wireValue;
  }
}
