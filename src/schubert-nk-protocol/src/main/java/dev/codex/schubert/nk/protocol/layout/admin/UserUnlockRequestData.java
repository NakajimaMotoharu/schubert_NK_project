package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts ULKREQ01. */
public record UserUnlockRequestData(FieldValue.Numeric userId,
    FieldValue.Numeric expectedVersion,
    FieldValue.Text operationToken) implements PayloadData {
  public UserUnlockRequestData {
    Objects.requireNonNull(userId, "userId");
    Objects.requireNonNull(expectedVersion, "expectedVersion");
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static UserUnlockRequestData from(FieldValueSet fields) {
    return new UserUnlockRequestData(
        TypedFieldValues.requiredNumeric(fields, "User ID"),
        TypedFieldValues.requiredNumeric(fields, "Expected version"),
        TypedFieldValues.requiredText(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("User ID", userId),
            Map.entry("Expected version", expectedVersion),
            Map.entry("Operation token", operationToken)));
  }
}
