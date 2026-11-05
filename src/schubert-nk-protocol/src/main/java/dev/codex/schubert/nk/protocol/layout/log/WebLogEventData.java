package dev.codex.schubert.nk.protocol.layout.log;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.ElapsedMilliseconds;
import dev.codex.schubert.nk.protocol.layout.semantic.HttpStatusCode;
import dev.codex.schubert.nk.protocol.layout.semantic.LogLevel;
import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/** Named wire record. Trace: UI235 §12.2; SS323/351; QA054/SSC336; PT-PRO-QA054. */
public record WebLogEventData(
    Instant occurredAt,
    LogType logType,
    LogLevel level,
    Optional<String> action,
    String message,
    UUID httpRequestId,
    String httpMethod,
    String path,
    HttpStatusCode httpStatus,
    ElapsedMilliseconds elapsedMs,
    String remoteAddress,
    Optional<String> username,
    Optional<UserRole> role,
    Optional<String> details)
    implements PayloadData {
  public WebLogEventData {
    Objects.requireNonNull(occurredAt, "occurredAt");
    Objects.requireNonNull(logType, "logType");
    Objects.requireNonNull(level, "level");
    Objects.requireNonNull(action, "action");
    Objects.requireNonNull(message, "message");
    Objects.requireNonNull(httpRequestId, "httpRequestId");
    Objects.requireNonNull(httpMethod, "httpMethod");
    Objects.requireNonNull(path, "path");
    Objects.requireNonNull(httpStatus, "httpStatus");
    Objects.requireNonNull(elapsedMs, "elapsedMs");
    Objects.requireNonNull(remoteAddress, "remoteAddress");
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(role, "role");
    Objects.requireNonNull(details, "details");
  }

  /** Existing REQUEST callers retain exactly the approved pre-QA054 wire category. */
  public WebLogEventData(
      Instant occurredAt,
      LogLevel level,
      Optional<String> action,
      String message,
      UUID httpRequestId,
      String httpMethod,
      String path,
      HttpStatusCode httpStatus,
      ElapsedMilliseconds elapsedMs,
      String remoteAddress,
      Optional<String> username,
      Optional<UserRole> role,
      Optional<String> details) {
    this(
        occurredAt,
        LogType.REQUEST,
        level,
        action,
        message,
        httpRequestId,
        httpMethod,
        path,
        httpStatus,
        elapsedMs,
        remoteAddress,
        username,
        role,
        details);
  }

  public static WebLogEventData from(FieldValueSet fields) {
    return new WebLogEventData(
        TypedFieldValues.requiredInstant(fields, "発生日時"),
        TypedFieldValues.requiredEnum(fields, "Log type", LogType.class),
        TypedFieldValues.requiredEnum(fields, "Level", LogLevel.class),
        TypedFieldValues.optionalString(fields, "Action"),
        TypedFieldValues.requiredString(fields, "Message"),
        TypedFieldValues.requiredUuid(fields, "HTTP request ID"),
        TypedFieldValues.requiredString(fields, "HTTP method"),
        TypedFieldValues.requiredString(fields, "Path"),
        TypedFieldValues.requiredHttpStatusCode(fields, "HTTP status"),
        TypedFieldValues.requiredElapsedMilliseconds(fields, "Elapsed ms"),
        TypedFieldValues.requiredString(fields, "Remote address"),
        TypedFieldValues.optionalString(fields, "Username"),
        TypedFieldValues.optionalEnum(fields, "Role", UserRole.class),
        TypedFieldValues.optionalString(fields, "Details"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("発生日時", TypedFieldValues.instant(occurredAt)),
            Map.entry("Log type", TypedFieldValues.enumValue(logType)),
            Map.entry("Level", TypedFieldValues.enumValue(level)),
            Map.entry("Action", TypedFieldValues.optionalStringValue(action)),
            Map.entry("Message", TypedFieldValues.text(message)),
            Map.entry("HTTP request ID", TypedFieldValues.uuid(httpRequestId)),
            Map.entry("HTTP method", TypedFieldValues.text(httpMethod)),
            Map.entry("Path", TypedFieldValues.text(path)),
            Map.entry("HTTP status", TypedFieldValues.httpStatusCode(httpStatus)),
            Map.entry("Elapsed ms", TypedFieldValues.elapsedMilliseconds(elapsedMs)),
            Map.entry("Remote address", TypedFieldValues.text(remoteAddress)),
            Map.entry("Username", TypedFieldValues.optionalStringValue(username)),
            Map.entry("Role", TypedFieldValues.optionalEnumValue(role)),
            Map.entry("Details", TypedFieldValues.optionalStringValue(details))));
  }

  @Override
  public String toString() {
    return "WebLogEventData[REDACTED]";
  }
}
