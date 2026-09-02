package dev.codex.schubert.nk.protocol.layout.semantic;

/** Scenario script-file identifier. Trace: SCF/SCN/SRC layouts, SS 323, PT-PRO-001-T04. */
public record ScriptFileId(long value) implements ProtocolId {
  public ScriptFileId {
    IdValue.validate(value);
  }
}
