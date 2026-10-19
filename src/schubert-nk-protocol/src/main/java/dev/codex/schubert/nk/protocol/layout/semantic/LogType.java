package dev.codex.schubert.nk.protocol.layout.semantic;

/** Allowlisted log category. Trace: LGS/WLG layouts, UI 235, PT-PRO-001-T04. */
public enum LogType implements WireEnum {
  ACTION("ACTION"),
  REQUEST("REQUEST"),
  SECURITY("SECURITY"),
  MQ("MQ"),
  SYSTEM("SYSTEM"),
  BATCH("BATCH");

  private final String encodedValue;

  LogType(String wireValue) {
    this.encodedValue = wireValue;
  }

  @Override
  public String wireValue() {
    return encodedValue;
  }
}
