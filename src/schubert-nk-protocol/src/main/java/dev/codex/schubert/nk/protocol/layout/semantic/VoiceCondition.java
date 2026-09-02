package dev.codex.schubert.nk.protocol.layout.semantic;

/** Optional scenario voice filter. Trace: SRCREQ01, UI 234, PT-PRO-001-T04. */
public enum VoiceCondition implements WireEnum {
  PRESENT("1"),
  ABSENT("0");

  private final String wireValue;

  VoiceCondition(String wireValue) {
    this.wireValue = wireValue;
  }

  @Override
  public String wireValue() {
    return wireValue;
  }
}
