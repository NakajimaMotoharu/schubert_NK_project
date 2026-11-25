package dev.codex.schubert.nk.api.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

final class TransferFixtureWorkersTest {
  private static final List<String> STOP_CALLS = List.of("shutdownNow", "awaitTermination");

  @Test // PT-SCN-FIXTURE-WORKER001
  void timeoutKeepsTheFirstFailureAndFailsWhenAlone() {
    var calls = new ArrayList<String>();
    var stalled = executor(calls, 10, () -> false);
    var primary = new AssertionError("fixture expectation failed");
    var observed =
        assertThrows(
            AssertionError.class,
            () -> {
              try (var workers = new TransferFixtureWorkers(stalled)) {
                assertSame(stalled, workers.executor());
                throw primary;
              }
            });
    assertSame(primary, observed);
    assertEquals(1, observed.getSuppressed().length);
    assertInstanceOfTimeout(observed.getSuppressed()[0]);
    assertEquals(STOP_CALLS, calls);

    calls.clear();
    var timeout =
        assertThrows(
            AssertionError.class,
            () -> {
              try (var workers = new TransferFixtureWorkers(stalled)) {
                assertSame(stalled, workers.executor());
              }
            });
    assertInstanceOfTimeout(timeout);
    assertEquals(STOP_CALLS, calls);
  }

  @Test // PT-SCN-FIXTURE-WORKER002
  void interruptionKeepsTheOriginalExceptionAndRestoresTheFlag() {
    var calls = new ArrayList<String>();
    var interrupted = new InterruptedException("fixture stop interrupted");
    var worker =
        executor(
            calls,
            5,
            () -> {
              throw interrupted;
            });
    try {
      var observed =
          assertThrows(
              IllegalStateException.class,
              () -> {
                try (var workers = new TransferFixtureWorkers(worker, 5)) {
                  assertSame(worker, workers.executor());
                }
              });
      assertSame(interrupted, observed.getCause());
      assertTrue(Thread.currentThread().isInterrupted());
      assertEquals(STOP_CALLS, calls);
    } finally {
      Thread.interrupted();
    }
  }

  private static void assertInstanceOfTimeout(Throwable failure) {
    assertInstanceOf(AssertionError.class, failure);
    assertEquals("transfer fixture workers did not terminate", failure.getMessage());
  }

  private static ExecutorService executor(
      List<String> calls, long expectedSeconds, Termination termination) {
    return (ExecutorService)
        Proxy.newProxyInstance(
            ExecutorService.class.getClassLoader(),
            new Class<?>[] {ExecutorService.class},
            (ignored, method, args) -> {
              calls.add(method.getName());
              return switch (method.getName()) {
                case "shutdownNow" -> List.of();
                case "awaitTermination" -> {
                  assertEquals(expectedSeconds, args[0]);
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
