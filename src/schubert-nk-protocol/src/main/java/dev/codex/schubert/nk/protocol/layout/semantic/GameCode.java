package dev.codex.schubert.nk.protocol.layout.semantic;

/** Fixed scenario game code. Trace: UI 223/234, SS 323, PT-PRO-001-T04. */
public enum GameCode implements WireEnum {
  NUKITASHI_1("NUKITASHI1"),
  NUKITASHI_2("NUKITASHI2");

  private final String wireValue;

  GameCode(String wireValue) {
    this.wireValue = wireValue;
  }

  @Override
  public String wireValue() {
    return wireValue;
  }
}
