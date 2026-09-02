package dev.codex.schubert.nk.protocol.layout.log;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts LGSRSP01. */
public record LogRecord(FieldValue.Numeric logId,
    FieldValue.Numeric occurredAt,
    FieldValue.Text logType,
    FieldValue.Text level,
    Optional<FieldValue.Text> action,
    FieldValue.Text message,
    Optional<FieldValue.Text> httpRequestId,
    Optional<FieldValue.Text> businessMessageId,
    Optional<FieldValue.Text> correlationId,
    Optional<FieldValue.Text> httpMethod,
    Optional<FieldValue.Text> path,
    Optional<FieldValue.Text> httpStatus,
    Optional<FieldValue.Text> elapsedMs,
    Optional<FieldValue.Text> remoteAddress,
    Optional<FieldValue.Text> details) implements PayloadRecord {
  public LogRecord {
    Objects.requireNonNull(logId, "logId");
    Objects.requireNonNull(occurredAt, "occurredAt");
    Objects.requireNonNull(logType, "logType");
    Objects.requireNonNull(level, "level");
    Objects.requireNonNull(action, "action");
    Objects.requireNonNull(message, "message");
    Objects.requireNonNull(httpRequestId, "httpRequestId");
    Objects.requireNonNull(businessMessageId, "businessMessageId");
    Objects.requireNonNull(correlationId, "correlationId");
    Objects.requireNonNull(httpMethod, "httpMethod");
    Objects.requireNonNull(path, "path");
    Objects.requireNonNull(httpStatus, "httpStatus");
    Objects.requireNonNull(elapsedMs, "elapsedMs");
    Objects.requireNonNull(remoteAddress, "remoteAddress");
    Objects.requireNonNull(details, "details");
  }

  public static LogRecord from(FieldValueSet fields) {
    return new LogRecord(
        TypedFieldValues.requiredNumeric(fields, "Log ID"),
        TypedFieldValues.requiredNumeric(fields, "発生日時"),
        TypedFieldValues.requiredText(fields, "Log type"),
        TypedFieldValues.requiredText(fields, "Level"),
        TypedFieldValues.optionalText(fields, "Action"),
        TypedFieldValues.requiredText(fields, "Message"),
        TypedFieldValues.optionalText(fields, "HTTP request ID"),
        TypedFieldValues.optionalText(fields, "業務Message ID"),
        TypedFieldValues.optionalText(fields, "Correlation ID"),
        TypedFieldValues.optionalText(fields, "HTTP method"),
        TypedFieldValues.optionalText(fields, "Path"),
        TypedFieldValues.optionalText(fields, "HTTP status"),
        TypedFieldValues.optionalText(fields, "Elapsed ms"),
        TypedFieldValues.optionalText(fields, "Remote address"),
        TypedFieldValues.optionalText(fields, "Details"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Log ID", logId),
            Map.entry("発生日時", occurredAt),
            Map.entry("Log type", logType),
            Map.entry("Level", level),
            Map.entry("Action", TypedFieldValues.orUnset(action)),
            Map.entry("Message", message),
            Map.entry("HTTP request ID", TypedFieldValues.orUnset(httpRequestId)),
            Map.entry("業務Message ID", TypedFieldValues.orUnset(businessMessageId)),
            Map.entry("Correlation ID", TypedFieldValues.orUnset(correlationId)),
            Map.entry("HTTP method", TypedFieldValues.orUnset(httpMethod)),
            Map.entry("Path", TypedFieldValues.orUnset(path)),
            Map.entry("HTTP status", TypedFieldValues.orUnset(httpStatus)),
            Map.entry("Elapsed ms", TypedFieldValues.orUnset(elapsedMs)),
            Map.entry("Remote address", TypedFieldValues.orUnset(remoteAddress)),
            Map.entry("Details", TypedFieldValues.orUnset(details))));
  }
}
