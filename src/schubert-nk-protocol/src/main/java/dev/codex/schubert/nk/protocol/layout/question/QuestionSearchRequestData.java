package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts QSSREQ01. */
public record QuestionSearchRequestData(Optional<String> keyword,
    Optional<String> username,
    Optional<String> answerState,
    Optional<Instant> submittedFrom,
    Optional<Instant> submittedTo,
    long page,
    long pageSize) implements PayloadData {
  public QuestionSearchRequestData {
    Objects.requireNonNull(keyword, "keyword");
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(answerState, "answerState");
    Objects.requireNonNull(submittedFrom, "submittedFrom");
    Objects.requireNonNull(submittedTo, "submittedTo");
  }

  public static QuestionSearchRequestData from(FieldValueSet fields) {
    return new QuestionSearchRequestData(
        TypedFieldValues.optionalString(fields, "Keyword"),
        TypedFieldValues.optionalString(fields, "Username"),
        TypedFieldValues.optionalString(fields, "回答状態"),
        TypedFieldValues.optionalInstant(fields, "受付日時From"),
        TypedFieldValues.optionalInstant(fields, "受付日時To"),
        TypedFieldValues.requiredLong(fields, "Page"),
        TypedFieldValues.requiredLong(fields, "Page size"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Keyword", TypedFieldValues.optionalStringValue(keyword)),
            Map.entry("Username", TypedFieldValues.optionalStringValue(username)),
            Map.entry("回答状態", TypedFieldValues.optionalStringValue(answerState)),
            Map.entry("受付日時From", TypedFieldValues.optionalInstantValue(submittedFrom)),
            Map.entry("受付日時To", TypedFieldValues.optionalInstantValue(submittedTo)),
            Map.entry("Page", TypedFieldValues.numeric(page)),
            Map.entry("Page size", TypedFieldValues.numeric(pageSize))));
  }

  @Override
  public String toString() {
    return "QuestionSearchRequestData[REDACTED]";
  }
}
