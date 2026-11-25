package dev.codex.schubert.nk.protocol.fixture;

import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.Objects;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

/** Bounded cleanup for test-owned Protocol workers (BUG-3911/YKT-2997). */
public final class ProtocolFixtureWorkers implements AutoCloseable {
  private final ExecutorService executor;

  public ProtocolFixtureWorkers(ExecutorService executor) {
    this.executor = Objects.requireNonNull(executor, "executor");
  }

  public ExecutorService executor() {
    return executor;
  }

  @Override
  public void close() {
    executor.shutdownNow();
    try {
      assertTrue(
          executor.awaitTermination(10, TimeUnit.SECONDS), "Protocol fixture workers did not stop");
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new IllegalStateException(
          "Protocol fixture worker termination interrupted", interrupted);
    }
  }
}
