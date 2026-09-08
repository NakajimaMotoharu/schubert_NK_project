package dev.codex.schubert.nk.api.application.admin;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.admin.UserMutationResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;

/** Closed definite outcomes only. NK-ADM-001; UI236/SS312/323/332; PT-ADM-019/021/023. */
public record UserMutationResult(ResultCode resultCode, Optional<UserMutationResponseData> data) {
  public UserMutationResult {
    Objects.requireNonNull(resultCode, "resultCode");
    Objects.requireNonNull(data, "data");
    if (resultCode.usesSuccessProfile() != data.isPresent())
      throw new IllegalArgumentException("user mutation result payload is inconsistent");
    if (!resultCode.usesSuccessProfile()
        && !Set.of(
                ResultCode.VALIDATION_ERROR,
                ResultCode.NOT_FOUND,
                ResultCode.CONFLICT,
                ResultCode.RESOURCE_LIMIT)
            .contains(resultCode))
      throw new IllegalArgumentException("user mutation result code is invalid");
  }

  static UserMutationResult accepted(UserId id, long version, ResultCode code) {
    return new UserMutationResult(code, Optional.of(new UserMutationResponseData(id, version)));
  }

  static UserMutationResult rejected(ResultCode code) {
    return new UserMutationResult(code, Optional.empty());
  }

  @Override
  public String toString() {
    return "UserMutationResult[REDACTED]";
  }
}
