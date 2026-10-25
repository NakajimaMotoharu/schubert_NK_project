package dev.codex.schubert.nk.api.messaging.outbound;

/** Bounded batch counters; identifiers and bodies are intentionally absent. */
public record OutboxDispatchReport(int claimed, int sent, int failed, int leaseLost) {
  public OutboxDispatchReport {
    if (claimed < 0
        || sent < 0
        || failed < 0
        || leaseLost < 0
        || claimed != (long) sent + failed + leaseLost) {
      throw new IllegalArgumentException("outbox dispatch counters are inconsistent");
    }
  }
}
