package dev.codex.schubert.nk.api.security;

import java.util.Objects;

/** Bounded crypto error with no provider cause/value. NK-AUT-001; SS352; PT-AUT-005-C02/04. */
public final class AuthContextCryptoException extends RuntimeException {
  private static final long serialVersionUID = 1L;

  public enum Reason {
    INVALID,
    KEY_UNAVAILABLE,
    CRYPTO_UNAVAILABLE
  }

  private final Reason reason;

  AuthContextCryptoException(Reason reason) {
    super("authentication context cryptography failed");
    this.reason = Objects.requireNonNull(reason, "reason");
  }

  public Reason reason() {
    return reason;
  }
}
