package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.BatchStepResult;
import dev.codex.schubert.nk.batch.repository.CleanupTerminalRepository;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * ISSSTEP003/YKT292. Handwritten seven terminals and receipt gate fixture, not native authority.
 */
final class MorningCleanupCompletionTest {
  @Test
  void immutableCurrentReceiptAndSeparatePriorSlots() throws Exception {
    var run =
        new BatchRun(
            UUID.fromString("11111111-1111-4111-8111-111111111111"),
            Instant.parse("2026-09-27T15:00:00Z"));
    var steps =
        List.of(
            BatchStep.CLEAN_NOTIFICATION,
            BatchStep.CLEAN_QUESTION,
            BatchStep.CLEAN_SESSION,
            BatchStep.CLEAN_INBOX_OUTBOX,
            BatchStep.CLEAN_LOG,
            BatchStep.CLEAN_BATCH_RUN,
            BatchStep.CLEAN_TRANSFER);
    var entries = new ArrayList<CleanupTerminalRepository.Entry>();
    for (int i = 0; i < 7; i++)
      entries.add(
          new CleanupTerminalRepository.Entry(
              new BatchStepAttempt(100 + i, run, steps.get(i), 1, run.cutoff(), false),
              run.cutoff().plusSeconds(1),
              new BatchStepResult(
                  BatchStepResult.Status.SUCCESS, 1, 1, 0, 0, BatchStepResult.Reason.NONE)));
    var snapshot = new CleanupTerminalRepository.Snapshot(entries);
    var receipt = ExpiryReceiptFixture.cleanupReceipt(0);
    var references =
        new ArrayList<Optional<CleanupTerminalRepository.Entry>>(
            Collections.nCopies(7, Optional.empty()));
    var value = new MorningCleanupExecution.Completion(snapshot, receipt, references);
    references.clear();
    entries.clear();
    assertSame(receipt, value.receipt());
    assertSame(snapshot, value.terminal());
    assertEquals(Collections.nCopies(7, Optional.empty()), value.references());
    assertThrows(UnsupportedOperationException.class, () -> value.references().clear());
    assertEquals("CleanupCompletion[actual=<redacted>]", value.toString());
    assertThrows(
        IllegalArgumentException.class,
        () -> new MorningCleanupExecution.Completion(snapshot, receipt, List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningCleanupExecution.Completion(
                snapshot, ExpiryReceiptFixture.cleanupReceipt(10), value.references()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningCleanupExecution.Completion(
                snapshot, ExpiryReceiptFixture.receipt(0), value.references()));
    assertThrows(
        NullPointerException.class,
        () -> new MorningCleanupExecution.Completion(null, receipt, value.references()));
    assertThrows(
        NullPointerException.class,
        () -> new MorningCleanupExecution.Completion(snapshot, null, value.references()));
    assertThrows(
        NullPointerException.class,
        () -> new MorningCleanupExecution.Completion(snapshot, receipt, null));
    var nullSlot = new ArrayList<>(value.references());
    nullSlot.set(3, null);
    assertThrows(
        NullPointerException.class,
        () -> new MorningCleanupExecution.Completion(snapshot, receipt, nullSlot));
  }
}
