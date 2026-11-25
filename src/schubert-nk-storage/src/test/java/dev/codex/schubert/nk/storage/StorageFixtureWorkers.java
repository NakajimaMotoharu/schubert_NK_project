package dev.codex.schubert.nk.storage;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

/** Keeps test-owned shutdown finite while preserving the primary assertion or task failure. */
record StorageFixtureWorkers(ExecutorService executor) implements AutoCloseable {
  @Override
  public void close() {
    executor.shutdownNow();
    try {
      if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
        throw new AssertionError("storage fixture workers did not terminate");
      }
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new IllegalStateException("storage fixture termination interrupted", interrupted);
    }
  }
}
