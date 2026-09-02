package dev.codex.schubert.nk.protocol.layout.semantic;

/** Question answer state. Trace: QSS/QSD layouts, UI 236, PT-PRO-001-T04. */
public enum AnswerState implements WireEnum {
  ANSWERED("ANSWERED"),
  UNANSWERED("UNANSWERED"),
  ERROR("ERROR");

  private final String wireValue;

  AnswerState(String wireValue) {
    this.wireValue = wireValue;
  }

  @Override
  public String wireValue() {
    return wireValue;
  }
}
