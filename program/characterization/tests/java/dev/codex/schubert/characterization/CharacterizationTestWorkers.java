package dev.codex.schubert.characterization;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

/** Owns the finite lifetime of a characterization test's workers. */
record CharacterizationTestWorkers(ExecutorService executor) implements AutoCloseable {
  @Override
  public void close() {
    executor.shutdownNow();
    try {
      if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
        throw new AssertionError("characterization test workers did not terminate");
      }
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new AssertionError("characterization test worker cleanup was interrupted", interrupted);
    }
  }
}
