package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.AbstractExecutorService;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.opentest4j.AssertionFailedError;

/** Independent test of cleanup order and primary failure identity for BUG-3846. */
final class ViewFixtureWorkersTest {
  @Test // PT-WEB-VIEW-WORKER001
  void timeoutIsSuppressedBehindTheFirstFailure() {
    var executor = new ObservedExecutor(false, null);
    var firstFailure = new IllegalStateException("render check failed");
    var observed =
        assertThrows(
            IllegalStateException.class,
            () -> {
              try (var workers = new ViewFixtureWorkers(executor)) {
                assertEquals("isolated", workers.submit(() -> "isolated").get(1, TimeUnit.SECONDS));
                throw firstFailure;
              }
            });

    assertSame(firstFailure, observed);
    assertEquals(1, observed.getSuppressed().length);
    assertInstanceOf(AssertionFailedError.class, observed.getSuppressed()[0]);
    assertEquals(List.of("execute", "cancel", "10 SECONDS"), executor.calls);
  }

  @Test // PT-WEB-VIEW-WORKER002
  void successfulWorkAndStandaloneTimeoutBothRequireFiniteCleanup() throws InterruptedException {
    var successful = new ObservedExecutor(true, null);
    new ViewFixtureWorkers(successful).close();
    assertEquals(List.of("cancel", "10 SECONDS"), successful.calls);

    var stalled = new ObservedExecutor(false, null);
    var timeout =
        assertThrows(AssertionFailedError.class, () -> new ViewFixtureWorkers(stalled).close());
    assertTrue(timeout.getMessage().contains("view fixture workers did not stop"));
    assertEquals(List.of("cancel", "10 SECONDS"), stalled.calls);
  }

  @Test // PT-WEB-VIEW-WORKER003
  void cleanupInterruptSurvivesAsSuppressedAndRestoresTheThreadFlag() {
    var cleanup = new InterruptedException("fixture stop interrupted");
    var executor = new ObservedExecutor(false, cleanup);
    var firstFailure = new IllegalStateException("first render failure");
    try {
      var observed =
          assertThrows(
              IllegalStateException.class,
              () -> {
                try (var workers = new ViewFixtureWorkers(executor)) {
                  assertEquals(3, workers.submit(() -> 3).get(1, TimeUnit.SECONDS));
                  throw firstFailure;
                }
              });
      assertSame(firstFailure, observed);
      assertArrayEquals(new Throwable[] {cleanup}, observed.getSuppressed());
      assertTrue(Thread.currentThread().isInterrupted());
      assertEquals(List.of("execute", "cancel", "10 SECONDS"), executor.calls);
    } finally {
      Thread.interrupted();
    }
  }

  private static final class ObservedExecutor extends AbstractExecutorService {
    private final List<String> calls = new ArrayList<>();
    private final boolean finished;
    private final @Nullable InterruptedException interruption;

    ObservedExecutor(boolean finished, @Nullable InterruptedException interruption) {
      this.finished = finished;
      this.interruption = interruption;
    }

    @Override
    public void execute(Runnable command) {
      calls.add("execute");
      command.run();
    }

    @Override
    public List<Runnable> shutdownNow() {
      calls.add("cancel");
      return List.of();
    }

    @Override
    public boolean awaitTermination(long timeout, TimeUnit unit) throws InterruptedException {
      calls.add(timeout + " " + unit);
      if (interruption != null) throw interruption;
      return finished;
    }

    @Override
    public void shutdown() {
      throw new AssertionError("use the cancellation boundary");
    }

    @Override
    public boolean isShutdown() {
      throw new AssertionError("use the bounded wait");
    }

    @Override
    public boolean isTerminated() {
      throw new AssertionError("use the bounded wait");
    }
  }
}
