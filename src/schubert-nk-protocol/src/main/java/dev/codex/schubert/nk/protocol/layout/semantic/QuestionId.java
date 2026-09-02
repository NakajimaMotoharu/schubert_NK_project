package dev.codex.schubert.nk.protocol.layout.semantic;

/** Question identifier. Trace: QSB/QSS/QSD/QDL/QWK layouts, SS 323, PT-PRO-001-T04. */
public record QuestionId(long value) implements ProtocolId {
  public QuestionId {
    IdValue.validate(value);
  }
}
