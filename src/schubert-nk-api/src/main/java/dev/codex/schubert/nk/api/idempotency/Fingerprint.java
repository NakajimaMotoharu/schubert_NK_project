package dev.codex.schubert.nk.api.idempotency;

import java.util.Objects;

/** Versioned redacted HMAC value. Trace: NK-MSG-002, SS 324 §3.2. */
public record Fingerprint(String keyVersion, byte[] digest) {
  public Fingerprint {
    Objects.requireNonNull(keyVersion, "keyVersion");
    Objects.requireNonNull(digest, "digest");
    if (!keyVersion.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}") || digest.length != 32) {
      throw new IllegalArgumentException("fingerprint metadata is invalid");
    }
    digest = digest.clone();
  }

  @Override
  public byte[] digest() {
    return digest.clone();
  }

  @Override
  public String toString() {
    return "Fingerprint[<redacted>]";
  }
}
