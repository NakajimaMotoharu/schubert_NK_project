package dev.codex.schubert.nk.protocol.layout.auth;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts LOGRSP01. */
public record LogoutResponseData(FieldValue.Numeric sessionRevokedAt) implements PayloadData {
  public LogoutResponseData {
    Objects.requireNonNull(sessionRevokedAt, "sessionRevokedAt");
  }

  public static LogoutResponseData from(FieldValueSet fields) {
    return new LogoutResponseData(
        TypedFieldValues.requiredNumeric(fields, "Session失効日時"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Session失効日時", sessionRevokedAt)));
  }
}
