package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;

/** Generated named wire record. Trace: SS 323; layouts UDTREQ01. */
public record UserDetailRequestData(long userId) implements PayloadData {
  public UserDetailRequestData {
  }

  public static UserDetailRequestData from(FieldValueSet fields) {
    return new UserDetailRequestData(
        TypedFieldValues.requiredLong(fields, "User ID"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("User ID", TypedFieldValues.numeric(userId))));
  }

  @Override
  public String toString() {
    return "UserDetailRequestData[REDACTED]";
  }
}
