package dev.codex.schubert.nk.protocol.layout.log;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts WLGEVT01. */
public record WebLogEventData(FieldValue.Numeric occurredAt,
    FieldValue.Text level,
    Optional<FieldValue.Text> action,
    FieldValue.Text message,
    FieldValue.Text httpRequestId,
    FieldValue.Text httpMethod,
    FieldValue.Text path,
    FieldValue.Text httpStatus,
    FieldValue.Text elapsedMs,
    FieldValue.Text remoteAddress,
    Optional<FieldValue.Text> username,
    Optional<FieldValue.Text> role,
    Optional<FieldValue.Text> details) implements PayloadData {
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
        TypedFieldValues.requiredNumeric(fields, "発生日時"),
        TypedFieldValues.requiredText(fields, "Level"),
        TypedFieldValues.optionalText(fields, "Action"),
        TypedFieldValues.requiredText(fields, "Message"),
        TypedFieldValues.requiredText(fields, "HTTP request ID"),
        TypedFieldValues.requiredText(fields, "HTTP method"),
        TypedFieldValues.requiredText(fields, "Path"),
        TypedFieldValues.requiredText(fields, "HTTP status"),
        TypedFieldValues.requiredText(fields, "Elapsed ms"),
        TypedFieldValues.requiredText(fields, "Remote address"),
        TypedFieldValues.optionalText(fields, "Username"),
        TypedFieldValues.optionalText(fields, "Role"),
        TypedFieldValues.optionalText(fields, "Details"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("発生日時", occurredAt),
            Map.entry("Level", level),
            Map.entry("Action", TypedFieldValues.orUnset(action)),
            Map.entry("Message", message),
            Map.entry("HTTP request ID", httpRequestId),
            Map.entry("HTTP method", httpMethod),
            Map.entry("Path", path),
            Map.entry("HTTP status", httpStatus),
            Map.entry("Elapsed ms", elapsedMs),
            Map.entry("Remote address", remoteAddress),
            Map.entry("Username", TypedFieldValues.orUnset(username)),
            Map.entry("Role", TypedFieldValues.orUnset(role)),
            Map.entry("Details", TypedFieldValues.orUnset(details))));
  }
}
