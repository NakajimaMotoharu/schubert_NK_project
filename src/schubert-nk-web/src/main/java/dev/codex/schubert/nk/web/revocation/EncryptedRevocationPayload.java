package dev.codex.schubert.nk.web.revocation;

import java.util.Objects;

/** Unauthenticated DB bytes; defensive copies only. NK-WEB-002/SS331352/PG-D359/RERUN003. */
public record EncryptedRevocationPayload(String keyVersion, byte[] ciphertext) {
  public EncryptedRevocationPayload {
    validateVersion(keyVersion);
    Objects.requireNonNull(ciphertext, "revocation ciphertext");
    // Permit DB-valid malformed envelopes for closed validation; true envelope is 101..116 bytes.
    if (ciphertext.length < 29 || ciphertext.length > 116)
      throw new IllegalArgumentException("revocation ciphertext length is invalid");
    ciphertext = ciphertext.clone();
  }

  static String validateVersion(String version) {
    Objects.requireNonNull(version, "revocation key version");
    if (!version.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}"))
      throw new IllegalArgumentException("revocation key version is invalid");
    return version;
  }

  @Override
  public byte[] ciphertext() {
    return ciphertext.clone();
  }

  @Override
  public String toString() {
    return "EncryptedRevocationPayload[REDACTED]";
  }
}
