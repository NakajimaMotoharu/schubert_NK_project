package dev.codex.schubert.nk.api.idempotency;

import dev.codex.schubert.nk.api.domain.Role;
import java.util.Arrays;
import java.util.Objects;

/**
 * Authenticated plaintext scope for new QSS/QSD snapshots, not a current authorization grant.
 * NK-QRY-001/NK-DAT-001; AUT002/QST008/MQ008; UI224236; SS324/352/SSC157;
 * PG-D-330/PT-QRY-SCOPE-001..004. The existing snapshot codec owns encryption/AAD. Every returned
 * buffer is caller-owned and must be erased. Old raw wire is inspection-only.
 */
public final class QuestionQueryScopeFrame {
  private static final byte[] MAGIC = {'N', 'K', 'Q', 'R', 'Y', '1', 0};

  private QuestionQueryScopeFrame() {
    throw new AssertionError("static namespace");
  }

  public static byte[] wrap(Role capturedScope, byte[] wire) {
    Objects.requireNonNull(capturedScope, "captured scope");
    Objects.requireNonNull(wire, "wire");
    require(wire.length >= 256);
    byte[] frame = new byte[8 + wire.length];
    System.arraycopy(MAGIC, 0, frame, 0, MAGIC.length);
    frame[7] = (byte) (capturedScope == Role.USER ? 'U' : 'A');
    System.arraycopy(wire, 0, frame, 8, wire.length);
    return frame;
  }

  /** Normal replay requires this prefix; it never infers scope from legacy wire or live rows. */
  public static Role capturedScope(byte[] frame) {
    Objects.requireNonNull(frame, "frame");
    require(frame.length >= 264 && prefixed(frame));
    return switch (frame[7]) {
      case 'U' -> Role.USER;
      case 'A' -> Role.ADMIN;
      default -> throw new IllegalArgumentException("query snapshot scope is invalid");
    };
  }

  /**
   * Structural inspection permits old raw wire, but a new prefix only on the two declared routes.
   * No current actor/role/DB comparison is performed. The caller validates the returned full wire.
   */
  public static byte[] wireForInspection(ResponseSnapshotIdentity identity, byte[] plaintext) {
    Objects.requireNonNull(identity, "identity");
    Objects.requireNonNull(plaintext, "plaintext");
    if (!prefixed(plaintext)) return plaintext.clone();
    require(
        identity.responseVersion().equals("001")
            && (identity.responseLayoutId().equals("QSSRSP01")
                || identity.responseLayoutId().equals("QSDRSP01")));
    capturedScope(plaintext);
    return Arrays.copyOfRange(plaintext, 8, plaintext.length);
  }

  private static boolean prefixed(byte[] value) {
    return Arrays.equals(MAGIC, 0, MAGIC.length, value, 0, Math.min(value.length, MAGIC.length));
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("query snapshot scope frame is invalid");
  }
}
