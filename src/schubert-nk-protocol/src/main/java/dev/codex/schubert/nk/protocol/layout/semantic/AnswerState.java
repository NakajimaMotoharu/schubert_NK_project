package dev.codex.schubert.nk.protocol.layout.semantic;

/** Question answer state. Trace: QSS/QSD layouts, UI 236, PT-PRO-001-T04. */
public enum AnswerState implements WireEnum {
  ANSWERED("ANSWERED"),
  UNANSWERED("UNANSWERED"),
  ERROR("ERROR");

  private final String encodedValue;

  AnswerState(String wireValue) {
    this.encodedValue = wireValue;
  }

  @Override
  public String wireValue() {
    return encodedValue;
  }
}
