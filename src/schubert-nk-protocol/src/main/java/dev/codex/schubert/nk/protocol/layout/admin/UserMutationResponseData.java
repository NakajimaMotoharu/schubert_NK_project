package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import java.util.Map;
import java.util.Objects;

/**
 * Generated named wire record. Trace: SS 323; layouts UCRRSP01, USTRSP01, URLRSP01, UPWRSP01,
 * ULKRSP01.
 */
public record UserMutationResponseData(UserId userId, long updatedVersion) implements PayloadData {
  public UserMutationResponseData {
    Objects.requireNonNull(userId, "userId");
    TypedFieldValues.requireUnsignedRange("updatedVersion", updatedVersion, 9);
  }

  public static UserMutationResponseData from(FieldValueSet fields) {
    return new UserMutationResponseData(
        TypedFieldValues.requiredId(fields, "User ID", UserId::new),
        TypedFieldValues.requiredLong(fields, "更新後version"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("User ID", TypedFieldValues.id(userId)),
            Map.entry("更新後version", TypedFieldValues.numeric(updatedVersion))));
  }

  @Override
  public String toString() {
    return "UserMutationResponseData[REDACTED]";
  }
}
