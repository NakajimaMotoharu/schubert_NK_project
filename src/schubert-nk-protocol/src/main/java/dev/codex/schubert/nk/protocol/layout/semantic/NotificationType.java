package dev.codex.schubert.nk.protocol.layout.semantic;

/** Notification type. Trace: NTS/NTD layouts, UI 236, PT-PRO-001-T04. */
public enum NotificationType implements WireEnum {
  ACCEPTED("ACCEPTED"),
  COMPLETED("COMPLETED"),
  ERROR("ERROR");

  private final String encodedValue;

  NotificationType(String wireValue) {
    this.encodedValue = wireValue;
  }

  @Override
  public String wireValue() {
    return encodedValue;
  }
}
