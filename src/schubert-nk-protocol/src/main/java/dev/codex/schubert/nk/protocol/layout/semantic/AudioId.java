package dev.codex.schubert.nk.protocol.layout.semantic;

/** Audio identifier. Trace: AUDREQ01/SRCRSP01/SCNRSP01, SS 323, PT-PRO-001-T04. */
public record AudioId(long value) implements ProtocolId {
  public AudioId {
    IdValue.validate(value);
  }
}
