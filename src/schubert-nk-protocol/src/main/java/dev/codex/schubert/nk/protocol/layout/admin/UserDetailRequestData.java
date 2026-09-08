package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts UDTREQ01. */
public record UserDetailRequestData(UserId userId) implements PayloadData {
  public UserDetailRequestData {
    Objects.requireNonNull(userId, "userId");
  }

  public static UserDetailRequestData from(FieldValueSet fields) {
    return new UserDetailRequestData(TypedFieldValues.requiredId(fields, "User ID", UserId::new));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(Map.ofEntries(Map.entry("User ID", TypedFieldValues.id(userId))));
  }

  @Override
  public String toString() {
    return "UserDetailRequestData[REDACTED]";
  }
}
