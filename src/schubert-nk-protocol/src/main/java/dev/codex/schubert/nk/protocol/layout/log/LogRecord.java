package dev.codex.schubert.nk.protocol.layout.log;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.ElapsedMilliseconds;
import dev.codex.schubert.nk.protocol.layout.semantic.HttpStatusCode;
import dev.codex.schubert.nk.protocol.layout.semantic.LogId;
import dev.codex.schubert.nk.protocol.layout.semantic.LogLevel;
import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/** Generated named wire record. Trace: SS 323; layouts LGSRSP01. */
public record LogRecord(LogId logId,
    Instant occurredAt,
    LogType logType,
    LogLevel level,
    Optional<String> action,
    String message,
    Optional<UUID> httpRequestId,
    Optional<UUID> businessMessageId,
    Optional<UUID> correlationId,
    Optional<String> httpMethod,
    Optional<String> path,
    Optional<HttpStatusCode> httpStatus,
    Optional<ElapsedMilliseconds> elapsedMs,
    Optional<String> remoteAddress,
    Optional<String> details) implements PayloadRecord {
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
        TypedFieldValues.requiredId(fields, "Log ID", LogId::new),
        TypedFieldValues.requiredInstant(fields, "発生日時"),
        TypedFieldValues.requiredEnum(fields, "Log type", LogType.class),
        TypedFieldValues.requiredEnum(fields, "Level", LogLevel.class),
        TypedFieldValues.optionalString(fields, "Action"),
        TypedFieldValues.requiredString(fields, "Message"),
        TypedFieldValues.optionalUuid(fields, "HTTP request ID"),
        TypedFieldValues.optionalUuid(fields, "業務Message ID"),
        TypedFieldValues.optionalUuid(fields, "Correlation ID"),
        TypedFieldValues.optionalString(fields, "HTTP method"),
        TypedFieldValues.optionalString(fields, "Path"),
        TypedFieldValues.optionalHttpStatusCode(fields, "HTTP status"),
        TypedFieldValues.optionalElapsedMilliseconds(fields, "Elapsed ms"),
        TypedFieldValues.optionalString(fields, "Remote address"),
        TypedFieldValues.optionalString(fields, "Details"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Log ID", TypedFieldValues.id(logId)),
            Map.entry("発生日時", TypedFieldValues.instant(occurredAt)),
            Map.entry("Log type", TypedFieldValues.enumValue(logType)),
            Map.entry("Level", TypedFieldValues.enumValue(level)),
            Map.entry("Action", TypedFieldValues.optionalStringValue(action)),
            Map.entry("Message", TypedFieldValues.text(message)),
            Map.entry("HTTP request ID", TypedFieldValues.optionalUuidValue(httpRequestId)),
            Map.entry("業務Message ID", TypedFieldValues.optionalUuidValue(businessMessageId)),
            Map.entry("Correlation ID", TypedFieldValues.optionalUuidValue(correlationId)),
            Map.entry("HTTP method", TypedFieldValues.optionalStringValue(httpMethod)),
            Map.entry("Path", TypedFieldValues.optionalStringValue(path)),
            Map.entry("HTTP status", TypedFieldValues.optionalHttpStatusCodeValue(httpStatus)),
            Map.entry("Elapsed ms", TypedFieldValues.optionalElapsedMillisecondsValue(elapsedMs)),
            Map.entry("Remote address", TypedFieldValues.optionalStringValue(remoteAddress)),
            Map.entry("Details", TypedFieldValues.optionalStringValue(details))));
  }

  @Override
  public String toString() {
    return "LogRecord[REDACTED]";
  }
}
