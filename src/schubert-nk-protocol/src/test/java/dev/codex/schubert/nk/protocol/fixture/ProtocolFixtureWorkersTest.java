package dev.codex.schubert.nk.protocol.fixture;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.AbstractExecutorService;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.opentest4j.AssertionFailedError;

final class ProtocolFixtureWorkersTest {
  @Test // PT-PRO-WORKER001
  void timeoutIsSuppressedAfterAnAssertionAndSurfacedOnItsOwn() {
    var executor = new StalledExecutor(false);
    var primary = new AssertionError("independent wire expectation failed");
    var actual =
        assertThrows(
            AssertionError.class,
            () -> {
              try (var workers = new ProtocolFixtureWorkers(executor)) {
                assertSame(executor, workers.executor());
                throw primary;
              }
            });
    assertSame(primary, actual);
    assertEquals(1, actual.getSuppressed().length);
    assertEquals(AssertionFailedError.class, actual.getSuppressed()[0].getClass());
    assertEquals(List.of("cancel", "10 SECONDS"), executor.calls);

    var stalled = new StalledExecutor(false);
    assertThrows(AssertionFailedError.class, new ProtocolFixtureWorkers(stalled)::close);
    assertEquals(List.of("cancel", "10 SECONDS"), stalled.calls);
  }

  @Test // PT-PRO-WORKER002
  void interruptedCleanupRetainsTheCauseAndRestoresTheThreadFlag() {
    var executor = new StalledExecutor(true);
    var primary = new AssertionError("independent catalog expectation failed");
    try {
      var actual =
          assertThrows(
              AssertionError.class,
              () -> {
                try (var workers = new ProtocolFixtureWorkers(executor)) {
                  assertSame(executor, workers.executor());
                  throw primary;
                }
              });
      assertSame(primary, actual);
      assertEquals(1, actual.getSuppressed().length);
      assertEquals(IllegalStateException.class, actual.getSuppressed()[0].getClass());
      assertSame(executor.interruption, actual.getSuppressed()[0].getCause());
      assertTrue(Thread.currentThread().isInterrupted());
      assertEquals(List.of("cancel", "10 SECONDS"), executor.calls);
    } finally {
      Thread.interrupted();
    }
  }

  private static final class StalledExecutor extends AbstractExecutorService {
    private final List<String> calls = new ArrayList<>();
    private final InterruptedException interruption = new InterruptedException("test interruption");
    private final boolean interrupt;

    StalledExecutor(boolean interrupt) {
      this.interrupt = interrupt;
    }

    @Override
    public List<Runnable> shutdownNow() {
      calls.add("cancel");
      return List.of();
    }

    @Override
    public boolean awaitTermination(long timeout, TimeUnit unit) throws InterruptedException {
      calls.add(timeout + " " + unit);
      if (interrupt) throw interruption;
      return false;
    }

    @Override
    public void execute(Runnable command) {
      throw new AssertionError("this fixture only controls cleanup");
    }

    @Override
    public void shutdown() {
      throw new AssertionError("expected immediate cancellation");
    }

    @Override
    public boolean isShutdown() {
      throw new AssertionError("expected a bounded wait");
    }

    @Override
    public boolean isTerminated() {
      throw new AssertionError("expected a bounded wait");
    }
  }
}
