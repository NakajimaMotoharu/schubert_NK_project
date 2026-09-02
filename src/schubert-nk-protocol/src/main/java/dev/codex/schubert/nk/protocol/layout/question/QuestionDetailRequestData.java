package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;

/** Generated named wire record. Trace: SS 323; layouts QSDREQ01. */
public record QuestionDetailRequestData(long questionId) implements PayloadData {
  public QuestionDetailRequestData {
  }

  public static QuestionDetailRequestData from(FieldValueSet fields) {
    return new QuestionDetailRequestData(
        TypedFieldValues.requiredLong(fields, "Question ID"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Question ID", TypedFieldValues.numeric(questionId))));
  }

  @Override
  public String toString() {
    return "QuestionDetailRequestData[REDACTED]";
  }
}
