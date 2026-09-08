package dev.codex.schubert.nk.api.idempotency;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Objects;

/**
 * Exact saved completion check across DB-free file stages, not a decrypt/owner/HMAC gate.
 * NK-SCN-001/NK-MED-001/NK-MSG-002; DAT-009/MQ-006..010; UI241; SS324/333; PG-D-080;
 * PT-SCN-009-T06/T07 and PT-MED-059/061. No caller-owned bytes are retained.
 */
public final class InboxCompletionConsistency {
  private InboxCompletionConsistency() {}

  public static boolean sameSaved(InboxCompletion expected, InboxCompletion current) {
    Objects.requireNonNull(expected, "expected");
    Objects.requireNonNull(current, "current");
    if (expected.state() != current.state()
        || !expected.resultReference().equals(current.resultReference())
        || !expected.responseLayoutId().equals(current.responseLayoutId())
        || !expected.responseVersion().equals(current.responseVersion())
        || !expected.completedAt().equals(current.completedAt())) return false;
    var a = expected.responseSnapshot().orElseThrow(TemporaryInfrastructureException::new);
    var b = current.responseSnapshot().orElseThrow(TemporaryInfrastructureException::new);
    if (!a.keyVersion().equals(b.keyVersion())) return false;
    byte[] left = a.ciphertext(), right = b.ciphertext();
    try {
      return MessageDigest.isEqual(left, right);
    } finally {
      Arrays.fill(left, (byte) 0);
      Arrays.fill(right, (byte) 0);
    }
  }
}
