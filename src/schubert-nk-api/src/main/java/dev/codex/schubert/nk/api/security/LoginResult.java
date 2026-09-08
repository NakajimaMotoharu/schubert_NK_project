package dev.codex.schubert.nk.api.security;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.util.Objects;

/**
 * Disjoint success/failure shape, no dummy success fields. NK-AUT-001; UI234; SS312/314;
 * PT-AUT-004.
 */
public sealed interface LoginResult permits LoginResult.Success, LoginResult.Failure {
  ResultCode resultCode();

  int retryAfterSeconds();

  record Success(AuthenticatedActor actor, IssuedContext issued) implements LoginResult {
    public Success {
      Objects.requireNonNull(actor, "actor");
      Objects.requireNonNull(issued, "issued");
      if (actor.userId() != issued.identity().userId())
        throw new IllegalArgumentException("login result owner differs");
    }

    @Override
    public ResultCode resultCode() {
      return ResultCode.SUCCESS;
    }

    @Override
    public int retryAfterSeconds() {
      return 0;
    }

    @Override
    public String toString() {
      return "LoginSuccess[REDACTED]";
    }
  }

  record Failure(ResultCode resultCode, int retryAfterSeconds) implements LoginResult {
    public Failure {
      Objects.requireNonNull(resultCode, "resultCode");
      if (resultCode != ResultCode.AUTHENTICATION_FAILED && resultCode != ResultCode.LOCKED) {
        throw new IllegalArgumentException("login failure code is invalid");
      }
      if (resultCode == ResultCode.AUTHENTICATION_FAILED) {
        if (retryAfterSeconds != 0)
          throw new IllegalArgumentException("unlocked failure has no retry delay");
      } else if (retryAfterSeconds < 1 || retryAfterSeconds > 900) {
        throw new IllegalArgumentException("login lock delay is outside 1..900");
      }
    }

    @Override
    public String toString() {
      return "LoginFailure[code="
          + resultCode.wireValue()
          + ", retryAfterSeconds="
          + retryAfterSeconds
          + "]";
    }
  }
}
