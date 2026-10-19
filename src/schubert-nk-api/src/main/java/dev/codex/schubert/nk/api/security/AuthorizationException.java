package dev.codex.schubert.nk.api.security;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.util.Objects;

/** Bounded denial, without target identity/existence detail. NK-AUT-001; SS314 §9; PT-AUT-008. */
public final class AuthorizationException extends RuntimeException {
  private static final long serialVersionUID = 1L;
  private final ResultCode denialCode;

  AuthorizationException(ResultCode resultCode) {
    super("operation is not available");
    this.denialCode = Objects.requireNonNull(resultCode, "resultCode");
    if (resultCode != ResultCode.FORBIDDEN && resultCode != ResultCode.NOT_FOUND) {
      throw new IllegalArgumentException("unsupported authorization denial code");
    }
  }

  public ResultCode resultCode() {
    return denialCode;
  }
}
