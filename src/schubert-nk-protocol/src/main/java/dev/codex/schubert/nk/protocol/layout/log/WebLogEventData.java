package dev.codex.schubert.nk.protocol.layout.log;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.LogLevel;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/** Generated named wire record. Trace: SS 323; layouts WLGEVT01. */
public record WebLogEventData(Instant occurredAt,
    LogLevel level,
    Optional<String> action,
    String message,
    UUID httpRequestId,
    String httpMethod,
    String path,
    String httpStatus,
    String elapsedMs,
    String remoteAddress,
    Optional<String> username,
    Optional<UserRole> role,
    Optional<String> details) implements PayloadData {
  public WebLogEventData {
    Objects.requireNonNull(occurredAt, "occurredAt");
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

  public static WebLogEventData from(FieldValueSet fields) {
    return new WebLogEventData(
        TypedFieldValues.requiredInstant(fields, "発生日時"),
        TypedFieldValues.requiredEnum(fields, "Level", LogLevel.class),
        TypedFieldValues.optionalString(fields, "Action"),
        TypedFieldValues.requiredString(fields, "Message"),
        TypedFieldValues.requiredUuid(fields, "HTTP request ID"),
        TypedFieldValues.requiredString(fields, "HTTP method"),
        TypedFieldValues.requiredString(fields, "Path"),
        TypedFieldValues.requiredString(fields, "HTTP status"),
        TypedFieldValues.requiredString(fields, "Elapsed ms"),
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
            Map.entry("Level", TypedFieldValues.enumValue(level)),
            Map.entry("Action", TypedFieldValues.optionalStringValue(action)),
            Map.entry("Message", TypedFieldValues.text(message)),
            Map.entry("HTTP request ID", TypedFieldValues.uuid(httpRequestId)),
            Map.entry("HTTP method", TypedFieldValues.text(httpMethod)),
            Map.entry("Path", TypedFieldValues.text(path)),
            Map.entry("HTTP status", TypedFieldValues.text(httpStatus)),
            Map.entry("Elapsed ms", TypedFieldValues.text(elapsedMs)),
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
