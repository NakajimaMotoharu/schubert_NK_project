package dev.codex.schubert.nk.protocol.layout.log;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.LogLevel;
import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts LGSREQ01. */
public record LogSearchRequestData(Optional<String> keyword,
    Optional<LogType> logType,
    Optional<String> action,
    Optional<String> path,
    Optional<LogLevel> level,
    Optional<Instant> fromAt,
    Optional<Instant> toAt,
    int page,
    int pageSize) implements PayloadData {
  public LogSearchRequestData {
    Objects.requireNonNull(keyword, "keyword");
    Objects.requireNonNull(logType, "logType");
    Objects.requireNonNull(action, "action");
    Objects.requireNonNull(path, "path");
    Objects.requireNonNull(level, "level");
    Objects.requireNonNull(fromAt, "fromAt");
    Objects.requireNonNull(toAt, "toAt");
  }

  public static LogSearchRequestData from(FieldValueSet fields) {
    return new LogSearchRequestData(
        TypedFieldValues.optionalString(fields, "Keyword"),
        TypedFieldValues.optionalEnum(fields, "Log type", LogType.class),
        TypedFieldValues.optionalString(fields, "Action"),
        TypedFieldValues.optionalString(fields, "Path"),
        TypedFieldValues.optionalEnum(fields, "Level", LogLevel.class),
        TypedFieldValues.optionalInstant(fields, "From日時"),
        TypedFieldValues.optionalInstant(fields, "To日時"),
        TypedFieldValues.requiredInt(fields, "Page"),
        TypedFieldValues.requiredInt(fields, "Page size"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Keyword", TypedFieldValues.optionalStringValue(keyword)),
            Map.entry("Log type", TypedFieldValues.optionalEnumValue(logType)),
            Map.entry("Action", TypedFieldValues.optionalStringValue(action)),
            Map.entry("Path", TypedFieldValues.optionalStringValue(path)),
            Map.entry("Level", TypedFieldValues.optionalEnumValue(level)),
            Map.entry("From日時", TypedFieldValues.optionalInstantValue(fromAt)),
            Map.entry("To日時", TypedFieldValues.optionalInstantValue(toAt)),
            Map.entry("Page", TypedFieldValues.numeric(page)),
            Map.entry("Page size", TypedFieldValues.numeric(pageSize))));
  }

  @Override
  public String toString() {
    return "LogSearchRequestData[REDACTED]";
  }
}
