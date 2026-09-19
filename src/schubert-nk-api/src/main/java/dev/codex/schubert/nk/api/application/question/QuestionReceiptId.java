package dev.codex.schubert.nk.api.application.question;

import java.util.Objects;
import java.util.regex.Pattern;

/**
 * Public identifier, not authorization. NK-QST-001; RD QST002/ASY001; UI224/236; SS331;
 * RID001..008.
 */
public record QuestionReceiptId(String value) {
  private static final Pattern FORMAT = Pattern.compile("[0-9A-HJKMNP-TV-Z]{26}");

  public QuestionReceiptId {
    Objects.requireNonNull(value, "receiptId");
    if (!FORMAT.matcher(value).matches()) {
      throw new IllegalArgumentException("invalid receipt ID");
    }
  }

  @Override
  public String toString() {
    return "QuestionReceiptId[REDACTED]";
  }
}
