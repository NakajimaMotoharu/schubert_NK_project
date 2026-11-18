package dev.codex.schubert.nk.api.idempotency;

import java.util.Objects;

/**
 * Versioned redacted Inbox response ciphertext.
 *
 * <p>Trace: DAT-009, UI 241/242, SS 324 §6/§15, SS 352 §11.2 and PT-IDEM-007/008.
 */
public record EncryptedResponseSnapshot(String keyVersion, byte[] ciphertext) {
  public static final int MINIMUM_CIPHERTEXT_BYTES = 29;
  public static final int MAXIMUM_CIPHERTEXT_BYTES = 1_050_000;

  public EncryptedResponseSnapshot {
    Objects.requireNonNull(keyVersion, "keyVersion");
    Objects.requireNonNull(ciphertext, "ciphertext");
    if (!keyVersion.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}")) {
      throw new IllegalArgumentException("response snapshot key version is invalid");
    }
    if (ciphertext.length < MINIMUM_CIPHERTEXT_BYTES
        || ciphertext.length > MAXIMUM_CIPHERTEXT_BYTES) {
      throw new IllegalArgumentException("response snapshot ciphertext length is invalid");
    }
    ciphertext = ciphertext.clone();
  }

  @Override
  public byte[] ciphertext() {
    return ciphertext.clone();
  }

  @Override
  public String toString() {
    return "EncryptedResponseSnapshot[keyVersion/ciphertext=<redacted>]";
  }
}
