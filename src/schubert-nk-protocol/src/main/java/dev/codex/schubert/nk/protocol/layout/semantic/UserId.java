package dev.codex.schubert.nk.protocol.layout.semantic;

/** User identifier. Trace: USR/UCR/UDT/UST/URL/UPW/ULK layouts, SS 323, PT-PRO-001-T04. */
public record UserId(long value) implements ProtocolId {
  public UserId {
    IdValue.validate(value);
  }
}
