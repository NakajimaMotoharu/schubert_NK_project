package dev.codex.schubert.nk.protocol.layout.semantic;

/** Application user role. Trace: LGN/USR/UCR/UDT/URL/WLG layouts, UI 234/236, PT-PRO-001-T04. */
public enum UserRole implements WireEnum {
  USER("USER"),
  ADMIN("ADMIN");

  private final String encodedValue;

  UserRole(String wireValue) {
    this.encodedValue = wireValue;
  }

  @Override
  public String wireValue() {
    return encodedValue;
  }
}
