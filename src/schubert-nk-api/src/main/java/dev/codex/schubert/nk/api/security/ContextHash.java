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
  // BUG-036/YKT-032: caller monitors must not control internal state/resource lifetime.
  private final Object stateLock = new Object();
  private final DigestOperations operations;

  /**
   * SSC423: trusted package-local calculation boundary; public assembly always uses JDK SHA-256.
   */
  interface DigestOperations {
    byte[] digest(byte[] raw);

    String format(byte[] hashed);
  }

  private static final class JdkOperations implements DigestOperations {
    private final MessageDigest sha256;

    private JdkOperations(MessageDigest sha256) {
      this.sha256 = sha256;
    }

    @Override
    public byte[] digest(byte[] raw) {
      return sha256.digest(raw);
    }

    @Override
    public String format(byte[] hashed) {
      return HexFormat.of().formatHex(hashed);
    }
  }

  /** Missing mandatory JCA algorithm prevents startup, not an authentication success fallback. */
  public ContextHash() throws NoSuchAlgorithmException {
    this(new JdkOperations(MessageDigest.getInstance("SHA-256")));
  }

  ContextHash(DigestOperations operations) {
    this.operations = Objects.requireNonNull(operations, "operations");
  }

  /** Only the repository lookup receives this secret-derived value; never log it. */
  public String calculate(AuthenticationContext context) {
    synchronized (stateLock) {
      Objects.requireNonNull(context, "context");
      byte[] raw = context.wireValue().getBytes(StandardCharsets.US_ASCII);
      try {
        byte[] hashed = operations.digest(raw);
        try {
          return operations.format(hashed);
        } finally {
          Arrays.fill(hashed, (byte) 0);
        }
      } finally {
        Arrays.fill(raw, (byte) 0);
      }
    }
  }
}
