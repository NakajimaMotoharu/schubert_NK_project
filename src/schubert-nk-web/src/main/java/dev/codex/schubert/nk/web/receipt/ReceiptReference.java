package dev.codex.schubert.nk.web.receipt;

import java.time.Instant;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Immutable technical locator, never an authorization or acceptance proof. NK-WEB-002;
 * FUN001/AUT004/DAT009; UI241/242; SS313/331§9.4; QA048; RCPT001.
 */
@NullMarked
public record ReceiptReference(String receiptId, long questionId, Instant submittedAt) {
  public ReceiptReference {
    requireReceiptId(receiptId);
    Objects.requireNonNull(submittedAt, "submittedAt");
    if (questionId < 1 || questionId > 999999999999L || submittedAt.getNano() % 1000000 != 0)
      throw new IllegalArgumentException("receipt reference is invalid");
  }

  /** HTTP path validation only; this never authenticates an owner or proves acceptance. */
  public static void requireReceiptId(String value) {
    Objects.requireNonNull(value, "receiptId");
    if (!value.matches("[0-9A-HJKMNP-TV-Z]{26}"))
      throw new IllegalArgumentException("receipt identifier is invalid");
  }

  @Override
  public String toString() {
    return "ReceiptReference[redacted]";
  }
}
