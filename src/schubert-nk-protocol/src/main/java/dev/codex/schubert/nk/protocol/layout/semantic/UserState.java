package dev.codex.schubert.nk.protocol.layout.semantic;

/** User lifecycle state. Trace: USR/UDT layouts, UI 236, PT-PRO-001-T04. */
public enum UserState implements WireEnum {
  ACTIVE("ACTIVE"),
  DISABLED("DISABLED"),
  LOCKED("LOCKED");

  private final String encodedValue;

  UserState(String wireValue) {
    this.encodedValue = wireValue;
  }

  @Override
  public String wireValue() {
    return encodedValue;
  }
}
