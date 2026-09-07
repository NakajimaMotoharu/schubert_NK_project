package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts QDLRSP01. */
public record QuestionDeleteResponseData(Instant deletedAt) implements PayloadData {
  public QuestionDeleteResponseData {
    Objects.requireNonNull(deletedAt, "deletedAt");
  }

  public static QuestionDeleteResponseData from(FieldValueSet fields) {
    return new QuestionDeleteResponseData(TypedFieldValues.requiredInstant(fields, "削除日時"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(Map.ofEntries(Map.entry("削除日時", TypedFieldValues.instant(deletedAt))));
  }

  @Override
  public String toString() {
    return "QuestionDeleteResponseData[REDACTED]";
  }
}
