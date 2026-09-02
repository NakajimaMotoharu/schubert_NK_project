package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts QSSREQ01. */
public record QuestionSearchRequestData(Optional<FieldValue.Text> keyword,
    Optional<FieldValue.Text> username,
    Optional<FieldValue.Text> answerState,
    Optional<FieldValue.Text> submittedFrom,
    Optional<FieldValue.Text> submittedTo,
    FieldValue.Numeric page,
    FieldValue.Numeric pageSize) implements PayloadData {
  public QuestionSearchRequestData {
    Objects.requireNonNull(keyword, "keyword");
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(answerState, "answerState");
    Objects.requireNonNull(submittedFrom, "submittedFrom");
    Objects.requireNonNull(submittedTo, "submittedTo");
    Objects.requireNonNull(page, "page");
    Objects.requireNonNull(pageSize, "pageSize");
  }

  public static QuestionSearchRequestData from(FieldValueSet fields) {
    return new QuestionSearchRequestData(
        TypedFieldValues.optionalText(fields, "Keyword"),
        TypedFieldValues.optionalText(fields, "Username"),
        TypedFieldValues.optionalText(fields, "回答状態"),
        TypedFieldValues.optionalText(fields, "受付日時From"),
        TypedFieldValues.optionalText(fields, "受付日時To"),
        TypedFieldValues.requiredNumeric(fields, "Page"),
        TypedFieldValues.requiredNumeric(fields, "Page size"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Keyword", TypedFieldValues.orUnset(keyword)),
            Map.entry("Username", TypedFieldValues.orUnset(username)),
            Map.entry("回答状態", TypedFieldValues.orUnset(answerState)),
            Map.entry("受付日時From", TypedFieldValues.orUnset(submittedFrom)),
            Map.entry("受付日時To", TypedFieldValues.orUnset(submittedTo)),
            Map.entry("Page", page),
            Map.entry("Page size", pageSize)));
  }
}
