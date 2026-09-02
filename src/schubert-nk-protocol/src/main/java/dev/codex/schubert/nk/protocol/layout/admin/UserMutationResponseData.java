package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts UCRRSP01, USTRSP01, URLRSP01, UPWRSP01, ULKRSP01. */
public record UserMutationResponseData(FieldValue.Numeric userId,
    FieldValue.Numeric updatedVersion) implements PayloadData {
  public UserMutationResponseData {
    Objects.requireNonNull(userId, "userId");
    Objects.requireNonNull(updatedVersion, "updatedVersion");
  }

  public static UserMutationResponseData from(FieldValueSet fields) {
    return new UserMutationResponseData(
        TypedFieldValues.requiredNumeric(fields, "User ID"),
        TypedFieldValues.requiredNumeric(fields, "更新後version"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("User ID", userId),
            Map.entry("更新後version", updatedVersion)));
  }
}
