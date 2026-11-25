package dev.codex.schubert.nk.api.storage;

import java.util.Objects;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

/** Bounded shutdown for an executor owned by a local API fixture. YKT-2997. */
public record TransferFixtureWorkers(ExecutorService executor, long terminationSeconds)
    implements AutoCloseable {
  public TransferFixtureWorkers {
    Objects.requireNonNull(executor, "fixture executor");
    if (terminationSeconds <= 0) {
      throw new IllegalArgumentException("fixture worker termination must be bounded and positive");
    }
  }

  public TransferFixtureWorkers(ExecutorService executor) {
    this(executor, 10);
  }

  @Override
  public void close() {
    executor.shutdownNow();
    try {
      if (!executor.awaitTermination(terminationSeconds, TimeUnit.SECONDS)) {
        throw new AssertionError("transfer fixture workers did not terminate");
      }
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new IllegalStateException(
          "transfer fixture worker termination interrupted", interrupted);
    }
  }
}
