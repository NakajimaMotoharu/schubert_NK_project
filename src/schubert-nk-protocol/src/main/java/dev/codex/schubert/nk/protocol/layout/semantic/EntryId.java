package dev.codex.schubert.nk.protocol.layout.semantic;

/** Scenario entry identifier. Trace: SRCRSP01/SCNRSP01, SS 323, PT-PRO-001-T04. */
public record EntryId(long value) implements ProtocolId {
  public EntryId {
    IdValue.validate(value);
  }
}
