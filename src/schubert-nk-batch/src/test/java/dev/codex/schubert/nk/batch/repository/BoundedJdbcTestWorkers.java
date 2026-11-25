package dev.codex.schubert.nk.batch.repository;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

/** Cancels fixture workers and bounds the wait while retaining the test's primary failure. */
record BoundedJdbcTestWorkers(ExecutorService executor, long terminationSeconds)
    implements AutoCloseable {
  @Override
  public void close() {
    executor.shutdownNow();
    try {
      if (!executor.awaitTermination(terminationSeconds, TimeUnit.SECONDS)) {
        throw new AssertionError("JDBC fixture workers did not terminate");
      }
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new AssertionError("JDBC fixture worker cleanup was interrupted", interrupted);
    }
  }
}
