package dev.codex.schubert.nk.protocol.layout.semantic;

/** Application log identifier. Trace: LGSRSP01, SS 323, PT-PRO-001-T04. */
public record LogId(long value) implements ProtocolId {
  public LogId {
    IdValue.validate(value);
  }
}
