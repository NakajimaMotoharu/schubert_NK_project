package dev.codex.schubert.nk.batch.fixture;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

/** Cancels fixture workers and bounds the wait while retaining the test's primary failure. */
public record BoundedBatchFixtureWorkers(
    ExecutorService executor, long terminationSeconds, String description)
    implements AutoCloseable {
  @Override
  public void close() {
    executor.shutdownNow();
    try {
      if (!executor.awaitTermination(terminationSeconds, TimeUnit.SECONDS)) {
        throw new AssertionError(description + " workers did not terminate");
      }
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new AssertionError(description + " worker cleanup was interrupted", interrupted);
    }
  }
}
