package dev.codex.schubert.nk.protocol.layout.semantic;

/** Notification processing state. Trace: NTS/NTD/NTC layouts, UI 236, PT-PRO-001-T04. */
public enum NotificationState implements WireEnum {
  RECEIVED("RECEIVED"),
  PROCESSING("PROCESSING"),
  COMPLETED("COMPLETED"),
  ERROR("ERROR"),
  CANCELLED("CANCELLED");

  private final String wireValue;

  NotificationState(String wireValue) {
    this.wireValue = wireValue;
  }

  @Override
  public String wireValue() {
    return wireValue;
  }
}
