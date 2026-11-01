package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import org.junit.jupiter.api.Test;

/** SS341; FIXED-INBOX001. No resume/DB/Root operation. */
final class InboxFailureValueContractTest {
  @Test
  void inboxFailure001FixedFailureRequiresSameRunWithoutProviderDiagnostics() {
    var failure = new InboxMaintenanceException();
    assertEquals("Inbox maintenance did not complete; resume the same run", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
