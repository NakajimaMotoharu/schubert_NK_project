package dev.codex.schubert.nk.web.logging;

import java.util.Objects;

/**
 * Defensive database ciphertext plus the independently stored key version.
 *
 * <p>Trace: NK-MSG-002; RD MON-003; UI 242; SS 331 §9.3/352 §11.2; PT-IDEM-012/015. The database
 * minimum is not a claim that the envelope is authentic; the codec verifies it.
 */
public record EncryptedWebLogPayload(String keyVersion, byte[] ciphertext) {
  public static final int MINIMUM_CIPHERTEXT_BYTES = 29;
  public static final int MAXIMUM_CIPHERTEXT_BYTES = 2_388;

  public EncryptedWebLogPayload {
    Objects.requireNonNull(keyVersion, "keyVersion");
    Objects.requireNonNull(ciphertext, "ciphertext");
    if (!keyVersion.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}")) {
      throw new IllegalArgumentException("web log key version is invalid");
    }
    if (ciphertext.length < MINIMUM_CIPHERTEXT_BYTES
        || ciphertext.length > MAXIMUM_CIPHERTEXT_BYTES) {
      throw new IllegalArgumentException("web log ciphertext length is invalid");
    }
    ciphertext = ciphertext.clone();
  }

  @Override
  public byte[] ciphertext() {
    return ciphertext.clone();
  }

  @Override
  public String toString() {
    return "EncryptedWebLogPayload[keyVersion/ciphertext=<redacted>]";
  }
}
