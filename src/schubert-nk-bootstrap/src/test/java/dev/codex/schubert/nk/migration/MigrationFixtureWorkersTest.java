package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-BOOT-MIG-WORKER001..004; SS354; YKT-2997; synthetic executor termination outcomes. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class MigrationFixtureWorkersTest {
  @Test
  void worker001CancelsBeforeOneBoundedWaitAndReturnsWhenTerminated() {
    var calls = new ArrayList<String>();
    var workers = new MigrationFixtureWorkers(executor(calls, () -> true), 7);

    workers.close();

    assertEquals(List.of("cancel", "wait"), calls);
  }

  @Test
  void worker002TimeoutFailsWithoutRetryOrFurtherWait() {
    var calls = new ArrayList<String>();
    var workers = new MigrationFixtureWorkers(executor(calls, () -> false), 7);

    var failure = assertThrows(AssertionError.class, workers::close);

    assertEquals("migration fixture workers did not terminate", failure.getMessage());
    assertEquals(List.of("cancel", "wait"), calls);
  }

  @Test
  void worker003InterruptionRestoresTheFlagAndRetainsTheOriginalCause() {
    var calls = new ArrayList<String>();
    var interrupted = new InterruptedException("synthetic termination interruption");
    var workers =
        new MigrationFixtureWorkers(
            executor(
                calls,
                () -> {
                  throw interrupted;
                }),
            7);
    assertFalse(Thread.currentThread().isInterrupted());
    try {
      var failure = assertThrows(AssertionError.class, workers::close);
      assertSame(interrupted, failure.getCause());
      assertTrue(Thread.currentThread().isInterrupted());
      assertEquals("migration fixture cleanup was interrupted", failure.getMessage());
      assertEquals(List.of("cancel", "wait"), calls);
    } finally {
      Thread.interrupted();
    }
  }

  @Test
  void worker004TerminationFailureIsSuppressedUnderThePrimaryFailure() {
    var calls = new ArrayList<String>();
    var executor = executor(calls, () -> false);
    var primary = new AssertionError("synthetic worker body failure");

    var observed =
        assertThrows(
            AssertionError.class,
            () -> {
              try (var workers = new MigrationFixtureWorkers(executor, 7)) {
                assertSame(executor, workers.executor());
                throw primary;
              }
            });

    assertSame(primary, observed);
    assertEquals(1, observed.getSuppressed().length);
    assertTrue(observed.getSuppressed()[0] instanceof AssertionError);
    assertEquals(
        "migration fixture workers did not terminate", observed.getSuppressed()[0].getMessage());
    assertEquals(List.of("cancel", "wait"), calls);
  }

  @FunctionalInterface
  private interface Termination {
    boolean await() throws InterruptedException;
  }

  private static ExecutorService executor(List<String> calls, Termination termination) {
    return (ExecutorService)
        Proxy.newProxyInstance(
            ExecutorService.class.getClassLoader(),
            new Class<?>[] {ExecutorService.class},
            (ignored, method, args) ->
                switch (method.getName()) {
                  case "shutdownNow" -> {
                    calls.add("cancel");
                    yield List.of();
                  }
                  case "awaitTermination" -> {
                    assertEquals(7L, args[0]);
                    assertSame(TimeUnit.SECONDS, args[1]);
                    calls.add("wait");
                    yield termination.await();
                  }
                  default ->
                      throw new AssertionError(
                          "unexpected executor operation: " + method.getName());
                });
  }
}
