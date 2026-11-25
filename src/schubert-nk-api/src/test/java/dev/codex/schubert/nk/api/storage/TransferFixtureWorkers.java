package dev.codex.schubert.nk.api.storage;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

/** Bounded shutdown for a worker pool owned by a transfer or media file test. YKT-2997. */
public record TransferFixtureWorkers(ExecutorService executor) implements AutoCloseable {
  @Override
  public void close() {
    executor.shutdownNow();
    try {
      if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
        throw new AssertionError("transfer fixture workers did not terminate");
      }
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new IllegalStateException(
          "transfer fixture worker termination interrupted", interrupted);
    }
  }
}
