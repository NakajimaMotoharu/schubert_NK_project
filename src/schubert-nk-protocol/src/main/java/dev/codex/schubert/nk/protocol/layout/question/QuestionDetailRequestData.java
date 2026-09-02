package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts QSDREQ01. */
public record QuestionDetailRequestData(FieldValue.Numeric questionId) implements PayloadData {
  public QuestionDetailRequestData {
    Objects.requireNonNull(questionId, "questionId");
  }

  public static QuestionDetailRequestData from(FieldValueSet fields) {
    return new QuestionDetailRequestData(
        TypedFieldValues.requiredNumeric(fields, "Question ID"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Question ID", questionId)));
  }
}
