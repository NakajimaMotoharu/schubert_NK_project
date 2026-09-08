package dev.codex.schubert.nk.web.session;

import java.util.Objects;

/**
 * Defensive DB ciphertext and independently stored key ID; construction does not authenticate.
 * NK-WEB-001; FUN-001/AUT-001..004; UI226/242; SS314 §7.2.2/331 §9.1/352 §11.2;
 * SSC-039/PG-D-095/PT-WEB-016..023. Both arguments nonnull; SQL minimum29 and bounded maximum16436.
 */
public record EncryptedSessionPayload(String keyVersion, byte[] ciphertext) {
  public EncryptedSessionPayload {
    validateVersion(keyVersion);
    Objects.requireNonNull(ciphertext, "ciphertext");
    if (ciphertext.length < 29 || ciphertext.length > 16436)
      throw new IllegalArgumentException("session ciphertext length is invalid");
    ciphertext = ciphertext.clone();
  }

  static String validateVersion(String version) {
    Objects.requireNonNull(version, "version");
    if (!version.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}"))
      throw new IllegalArgumentException("session key version is invalid");
    return version;
  }

  @Override
  public byte[] ciphertext() {
    return ciphertext.clone();
  }

  @Override
  public String toString() {
    return "EncryptedSessionPayload[REDACTED]";
  }
}
