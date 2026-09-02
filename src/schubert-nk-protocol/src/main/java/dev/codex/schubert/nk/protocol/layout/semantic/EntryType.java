package dev.codex.schubert.nk.protocol.layout.semantic;

/** Scenario entry type. Trace: SRC/SCN layouts, UI 234, PT-PRO-001-T04. */
public enum EntryType implements WireEnum {
  DIALOGUE("dialogue"),
  NARRATION("narration");

  private final String wireValue;

  EntryType(String wireValue) {
    this.wireValue = wireValue;
  }

  @Override
  public String wireValue() {
    return wireValue;
  }
}
