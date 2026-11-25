package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.Collection;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

/** Finite cleanup for local Web test workers. See BUG-3846 and YKT-2997. */
public final class ViewFixtureWorkers implements AutoCloseable {
  private final ExecutorService executor;
  private final long terminationSeconds;

  public ViewFixtureWorkers(ExecutorService executor) {
    this(executor, 10);
  }

  public ViewFixtureWorkers(ExecutorService executor, long terminationSeconds) {
    this.executor = Objects.requireNonNull(executor, "fixture executor");
    if (terminationSeconds <= 0) {
      throw new IllegalArgumentException("fixture worker termination must be bounded and positive");
    }
    this.terminationSeconds = terminationSeconds;
  }

  public <T> Future<T> submit(Callable<T> task) {
    return executor.submit(task);
  }

  public Future<?> submit(Runnable task) {
    return executor.submit(task);
  }

  public <T> List<Future<T>> invokeAll(
      Collection<? extends Callable<T>> tasks, long timeout, TimeUnit unit)
      throws InterruptedException {
    return executor.invokeAll(tasks, timeout, unit);
  }

  @Override
  public void close() {
    executor.shutdownNow();
    try {
      assertTrue(
          executor.awaitTermination(terminationSeconds, TimeUnit.SECONDS),
          "view fixture workers did not stop");
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new IllegalStateException("Web fixture worker termination interrupted", interrupted);
    }
  }
}
