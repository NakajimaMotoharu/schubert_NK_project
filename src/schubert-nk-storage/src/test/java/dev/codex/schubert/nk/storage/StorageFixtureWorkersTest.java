package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

final class StorageFixtureWorkersTest {
  private static final List<String> TERMINATION_ORDER = List.of("shutdownNow", "awaitTermination");

  @Test // PT-DAT-STORAGE-WORKER001
  void timeoutPreservesThePrimaryAndAlsoFailsWhenAlone() {
    var calls = new ArrayList<String>();
    var executor = executor(calls, () -> false);
    var primary = new AssertionError("independent ownership assertion failed");
    var observed =
        assertThrows(
            AssertionError.class,
            () -> {
              try (var workers = new StorageFixtureWorkers(executor)) {
                assertSame(executor, workers.executor());
                throw primary;
              }
            });
    assertSame(primary, observed);
    assertEquals(1, observed.getSuppressed().length);
    assertEquals(
        "storage fixture workers did not terminate", observed.getSuppressed()[0].getMessage());
    assertEquals(TERMINATION_ORDER, calls);

    var otherCalls = new ArrayList<String>();
    var stalled = executor(otherCalls, () -> false);
    assertThrows(
        AssertionError.class,
        () -> {
          try (var workers = new StorageFixtureWorkers(stalled)) {
            assertSame(stalled, workers.executor());
          }
        });
    assertEquals(TERMINATION_ORDER, otherCalls);
  }

  @Test // PT-DAT-STORAGE-WORKER002
  void interruptedTerminationPreservesTheOriginalCauseAndFlag() {
    var calls = new ArrayList<String>();
    var interruption = new InterruptedException("fixture interrupt");
    var executor =
        executor(
            calls,
            () -> {
              throw interruption;
            });
    try {
      var observed =
          assertThrows(
              IllegalStateException.class,
              () -> {
                try (var workers = new StorageFixtureWorkers(executor)) {
                  assertSame(executor, workers.executor());
                }
              });
      assertSame(interruption, observed.getCause());
      assertTrue(Thread.currentThread().isInterrupted());
      assertEquals(TERMINATION_ORDER, calls);
    } finally {
      Thread.interrupted();
    }
  }

  private static ExecutorService executor(List<String> calls, Termination termination) {
    return (ExecutorService)
        Proxy.newProxyInstance(
            StorageFixtureWorkersTest.class.getClassLoader(),
            new Class<?>[] {ExecutorService.class},
            (ignored, method, args) -> {
              calls.add(method.getName());
              return switch (method.getName()) {
                case "shutdownNow" -> List.of();
                case "awaitTermination" -> {
                  assertEquals(10L, args[0]);
                  assertEquals(TimeUnit.SECONDS, args[1]);
                  yield termination.await();
                }
                default -> throw new AssertionError("unexpected executor call");
              };
            });
  }

  @FunctionalInterface
  private interface Termination {
    boolean await() throws InterruptedException;
  }
}
