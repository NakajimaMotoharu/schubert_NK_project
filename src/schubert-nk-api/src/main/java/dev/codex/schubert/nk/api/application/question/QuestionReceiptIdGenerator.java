package dev.codex.schubert.nk.api.application.question;

import java.security.SecureRandom;
import java.util.Objects;
import java.util.function.IntUnaryOperator;

/**
 * 130 random bits, no owner/time data. NK-QST-001; RD QST002/ASY001; UI224/236; SS312/331;
 * RID004..008.
 */
public final class QuestionReceiptIdGenerator {
  private static final String ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ";
  private final Object stateLock = new Object();
  private final IntUnaryOperator randomIndex;

  QuestionReceiptIdGenerator(IntUnaryOperator randomIndex) {
    this.randomIndex = Objects.requireNonNull(randomIndex, "randomIndex");
  }

  /**
   * Production factory: cryptographic randomness only; never falls back after a provider failure.
   */
  public static QuestionReceiptIdGenerator create() {
    return new QuestionReceiptIdGenerator(new SecureRandom()::nextInt);
  }

  /**
   * Creates a candidate. Caller must enforce database uniqueness and reuse existing IDs on replay.
   */
  public QuestionReceiptId generate() {
    synchronized (stateLock) {
      StringBuilder value = new StringBuilder(26);
      for (int i = 0; i < 26; i++) {
        int index = randomIndex.applyAsInt(32);
        if (index < 0 || index >= 32) {
          throw new IllegalStateException("receipt randomness is unavailable");
        }
        value.append(ALPHABET.charAt(index));
      }
      return new QuestionReceiptId(value.toString());
    }
  }
}
