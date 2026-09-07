package dev.codex.schubert.nk.api.security;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.Objects;

/** SHA-256 of raw ASCII, not hex-decoded bytes. NK-AUT-001; UI226 §5; SS314 §6; PT-AUT-005/007. */
public final class ContextHash {
  private final MessageDigest digest;

  /** Missing mandatory JCA algorithm prevents startup, not an authentication success fallback. */
  public ContextHash() throws NoSuchAlgorithmException {
    digest = MessageDigest.getInstance("SHA-256");
  }

  /** Only the repository lookup receives this secret-derived value; never log it. */
  public synchronized String calculate(AuthenticationContext context) {
    Objects.requireNonNull(context, "context");
    byte[] raw = context.wireValue().getBytes(StandardCharsets.US_ASCII);
    try {
      byte[] hashed = digest.digest(raw);
      try {
        return HexFormat.of().formatHex(hashed);
      } finally {
        Arrays.fill(hashed, (byte) 0);
      }
    } finally {
      Arrays.fill(raw, (byte) 0);
    }
  }
}
