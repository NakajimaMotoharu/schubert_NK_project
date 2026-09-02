package dev.codex.schubert.nk.protocol.layout.semantic;

/** Notification identifier. Trace: NTS/NTD/NTC layouts, SS 323, PT-PRO-001-T04. */
public record NotificationId(long value) implements ProtocolId {
  public NotificationId {
    IdValue.validate(value);
  }
}
