package dev.codex.schubert.nk.protocol.layout.log;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts LGSREQ01. */
public record LogSearchRequestData(Optional<FieldValue.Text> keyword,
    Optional<FieldValue.Text> logType,
    Optional<FieldValue.Text> action,
    Optional<FieldValue.Text> path,
    Optional<FieldValue.Text> level,
    Optional<FieldValue.Text> fromAt,
    Optional<FieldValue.Text> toAt,
    FieldValue.Numeric page,
    FieldValue.Numeric pageSize) implements PayloadData {
  public LogSearchRequestData {
    Objects.requireNonNull(keyword, "keyword");
    Objects.requireNonNull(logType, "logType");
    Objects.requireNonNull(action, "action");
    Objects.requireNonNull(path, "path");
    Objects.requireNonNull(level, "level");
    Objects.requireNonNull(fromAt, "fromAt");
    Objects.requireNonNull(toAt, "toAt");
    Objects.requireNonNull(page, "page");
    Objects.requireNonNull(pageSize, "pageSize");
  }

  public static LogSearchRequestData from(FieldValueSet fields) {
    return new LogSearchRequestData(
        TypedFieldValues.optionalText(fields, "Keyword"),
        TypedFieldValues.optionalText(fields, "Log type"),
        TypedFieldValues.optionalText(fields, "Action"),
        TypedFieldValues.optionalText(fields, "Path"),
        TypedFieldValues.optionalText(fields, "Level"),
        TypedFieldValues.optionalText(fields, "From日時"),
        TypedFieldValues.optionalText(fields, "To日時"),
        TypedFieldValues.requiredNumeric(fields, "Page"),
        TypedFieldValues.requiredNumeric(fields, "Page size"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Keyword", TypedFieldValues.orUnset(keyword)),
            Map.entry("Log type", TypedFieldValues.orUnset(logType)),
            Map.entry("Action", TypedFieldValues.orUnset(action)),
            Map.entry("Path", TypedFieldValues.orUnset(path)),
            Map.entry("Level", TypedFieldValues.orUnset(level)),
            Map.entry("From日時", TypedFieldValues.orUnset(fromAt)),
            Map.entry("To日時", TypedFieldValues.orUnset(toAt)),
            Map.entry("Page", page),
            Map.entry("Page size", pageSize)));
  }
}
