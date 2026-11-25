package dev.codex.schubert.nk.api.application.question;

import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

/** Finite cleanup for self-owned question test workers. BUG-3877/3878, YKT-2997. */
record QuestionFixtureWorkers(ExecutorService executor) implements AutoCloseable {
  <T> Future<T> submit(Callable<T> task) {
    return executor.submit(task);
  }

  @Override
  public void close() {
    executor.shutdownNow();
    try {
      if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
        throw new AssertionError("question receipt workers did not stop");
      }
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new IllegalStateException(
          "question receipt worker termination interrupted", interrupted);
    }
  }
}
