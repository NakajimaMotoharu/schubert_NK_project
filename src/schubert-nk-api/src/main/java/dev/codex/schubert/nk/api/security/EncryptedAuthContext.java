package dev.codex.schubert.nk.api.security;

import java.util.Objects;

/** Bounded ciphertext, not a validated plaintext. NK-AUT-001; SS314/352; PT-AUT-005-C01..04. */
public record EncryptedAuthContext(String keyVersion, byte[] ciphertext) {
  public EncryptedAuthContext {
    Objects.requireNonNull(keyVersion, "keyVersion");
    Objects.requireNonNull(ciphertext, "ciphertext");
    if (!keyVersion.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}")) {
      throw new IllegalArgumentException("auth context key version is invalid");
    }
    if (ciphertext.length < 101 || ciphertext.length > 116) {
      throw new IllegalArgumentException("auth context ciphertext length is invalid");
    }
    ciphertext = ciphertext.clone();
  }

  @Override
  public byte[] ciphertext() {
    return ciphertext.clone();
  }

  @Override
  public String toString() {
    return "EncryptedAuthContext[keyVersion/ciphertext=<redacted>]";
  }
}
