package dev.codex.schubert.nk.api.idempotency;

import java.sql.SQLException;

/** PG-D380/PT-QST-ASUB012/NK-QST-001/SS312324: test-only typed failure, no Production override. */
public final class InboxBoundaryFailureFixture {
  private InboxBoundaryFailureFixture() {}

  public static SQLException create(String reason, boolean secondary) {
    var failure = new InboxException(InboxException.Reason.valueOf(reason), "literal provider");
    if (secondary) failure.addSuppressed(new SQLException("literal secondary"));
    return failure;
  }
}
