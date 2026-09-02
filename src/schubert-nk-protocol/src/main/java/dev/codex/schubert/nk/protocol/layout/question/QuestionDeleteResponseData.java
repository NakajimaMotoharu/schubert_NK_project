package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts QDLRSP01. */
public record QuestionDeleteResponseData(FieldValue.Numeric deletedAt) implements PayloadData {
  public QuestionDeleteResponseData {
    Objects.requireNonNull(deletedAt, "deletedAt");
  }

  public static QuestionDeleteResponseData from(FieldValueSet fields) {
    return new QuestionDeleteResponseData(
        TypedFieldValues.requiredNumeric(fields, "削除日時"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("削除日時", deletedAt)));
  }
}
