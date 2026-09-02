package dev.codex.schubert.nk.protocol.layout.auth;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;

/** Generated named wire record. Trace: SS 323; layouts LOGREQ01. */
public record LogoutRequestData() implements PayloadData {

  public static LogoutRequestData from(FieldValueSet fields) {
    TypedFieldValues.requireEmpty(fields);
    return new LogoutRequestData();
  }

  @Override
  public FieldValueSet fields() {
    return FieldValueSet.empty();
  }

  @Override
  public String toString() {
    return "LogoutRequestData[REDACTED]";
  }
}
