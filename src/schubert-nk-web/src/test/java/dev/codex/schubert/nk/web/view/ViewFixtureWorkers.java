package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.Objects;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

/** Finite cleanup for local Web test workers. See BUG-3846 and YKT-2997. */
public final class ViewFixtureWorkers implements AutoCloseable {
  private final ExecutorService executor;

  public ViewFixtureWorkers(ExecutorService executor) {
    this.executor = Objects.requireNonNull(executor, "fixture executor");
  }

  public <T> Future<T> submit(Callable<T> task) {
    return executor.submit(task);
  }

  public Future<?> submit(Runnable task) {
    return executor.submit(task);
  }

  @Override
  public void close() {
    executor.shutdownNow();
    try {
      assertTrue(
          executor.awaitTermination(10, TimeUnit.SECONDS), "view fixture workers did not stop");
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new IllegalStateException("Web fixture worker termination interrupted", interrupted);
    }
  }
}
