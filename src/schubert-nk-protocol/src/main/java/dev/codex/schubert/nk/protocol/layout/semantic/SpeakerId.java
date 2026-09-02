package dev.codex.schubert.nk.protocol.layout.semantic;

/** Speaker identifier. Trace: SPKRSP01, SS 323, PT-PRO-001-T04. */
public record SpeakerId(long value) implements ProtocolId {
  public SpeakerId {
    IdValue.validate(value);
  }
}
