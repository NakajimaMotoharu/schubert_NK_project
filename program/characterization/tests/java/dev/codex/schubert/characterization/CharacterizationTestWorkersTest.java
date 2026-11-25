package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

final class CharacterizationTestWorkersTest {
  @Test
  @DisplayName("PT-CHR-WORKER001 preserves the first failure and bounded cleanup diagnostics")
  void preservesPrimaryFailureWhenCleanupCannotFinish() {
    assertFalse(Thread.currentThread().isInterrupted());
    for (boolean interruptCleanup : List.of(false, true)) {
      var calls = new ArrayList<String>();
      var interrupted = new InterruptedException("synthetic cleanup interruption");
      var executor =
          (ExecutorService)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {ExecutorService.class},
                  (proxy, method, args) ->
                      switch (method.getName()) {
                        case "shutdownNow" -> {
                          calls.add("cancel");
                          yield List.of();
                        }
                        case "awaitTermination" -> {
                          assertEquals(10L, args[0]);
                          assertSame(TimeUnit.SECONDS, args[1]);
                          calls.add("wait");
                          if (interruptCleanup) throw interrupted;
                          yield false;
                        }
                        default -> throw new AssertionError(method.getName());
                      });
      var primary = new AssertionError("independent first assertion");
      try {
        var observed =
            assertThrows(
                AssertionError.class,
                () -> {
                  try (var workers = new CharacterizationTestWorkers(executor)) {
                    assertSame(executor, workers.executor());
                    throw primary;
                  }
                });
        assertSame(primary, observed);
        assertEquals(List.of("cancel", "wait"), calls);
        assertEquals(1, observed.getSuppressed().length);
        var cleanup = observed.getSuppressed()[0];
        assertEquals(
            interruptCleanup
                ? "characterization test worker cleanup was interrupted"
                : "characterization test workers did not terminate",
            cleanup.getMessage());
        assertSame(interruptCleanup ? interrupted : null, cleanup.getCause());
        assertEquals(interruptCleanup, Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
    }
  }
}
