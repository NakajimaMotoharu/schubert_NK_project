package dev.codex.schubert.nk.protocol.layout.semantic;

/** Stable asynchronous notification error code. Trace: SS 351 section 5.3, PT-PRO-001-T04. */
public enum NotificationErrorCode implements WireEnum {
  PROCESS_FAILED("PROCESS_FAILED"),
  SYSTEM_UNAVAILABLE("SYSTEM_UNAVAIL"),
  RESOURCE_LIMIT("RESOURCE_LIMIT"),
  DATA_INTEGRITY("DATA_INTEGRITY"),
  PROTOCOL_ERROR("PROTOCOL_ERROR");

  private final String encodedValue;

  NotificationErrorCode(String wireValue) {
    this.encodedValue = wireValue;
  }

  @Override
  public String wireValue() {
    return encodedValue;
  }
}
