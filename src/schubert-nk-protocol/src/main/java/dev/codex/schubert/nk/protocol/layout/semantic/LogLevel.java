package dev.codex.schubert.nk.protocol.layout.semantic;

/** Allowlisted log level. Trace: LGS/WLG layouts, UI 235, PT-PRO-001-T04. */
public enum LogLevel implements WireEnum {
  INFO("INFO"),
  WARN("WARN"),
  ERROR("ERROR");

  private final String wireValue;

  LogLevel(String wireValue) {
    this.wireValue = wireValue;
  }

  @Override
  public String wireValue() {
    return wireValue;
  }
}
