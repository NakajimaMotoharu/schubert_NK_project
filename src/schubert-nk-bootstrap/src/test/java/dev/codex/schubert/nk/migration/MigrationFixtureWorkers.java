package dev.codex.schubert.nk.migration;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

/** Cancels owned fixture workers with a finite wait and preserves the primary test failure. */
public record MigrationFixtureWorkers(ExecutorService executor, long terminationSeconds)
    implements AutoCloseable {
  @Override
  public void close() {
    executor.shutdownNow();
    try {
      if (!executor.awaitTermination(terminationSeconds, TimeUnit.SECONDS)) {
        throw new AssertionError("migration fixture workers did not terminate");
      }
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new AssertionError("migration fixture cleanup was interrupted", interrupted);
    }
  }
}
