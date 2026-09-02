package dev.codex.schubert.nk.protocol.layout.semantic;

/** Scenario response delivery mode. Trace: SCNRSP01, UI 234, PT-PRO-001-T04. */
public enum DeliveryMode implements WireEnum {
  INLINE("I"),
  FILE("F");

  private final String wireValue;

  DeliveryMode(String wireValue) {
    this.wireValue = wireValue;
  }

  @Override
  public String wireValue() {
    return wireValue;
  }
}
