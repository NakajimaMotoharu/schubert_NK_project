package dev.codex.schubert.nk.api.monitoring;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

/** Finite cleanup for workers owned by an in-memory metric fixture. */
record MetricFixtureWorkers(ExecutorService executor) implements AutoCloseable {
  @Override
  public void close() {
    executor.shutdownNow();
    try {
      if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
        throw new AssertionError("async metric fixture workers did not stop");
      }
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new IllegalStateException(
          "async metric fixture worker termination interrupted", interrupted);
    }
  }
}
