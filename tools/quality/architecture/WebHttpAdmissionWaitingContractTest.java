package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.time.Duration;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** Real own-JDK wait transitions, not an OS stop/native qualification. SS313/342/352. */
final class WebHttpAdmissionWaitingContractTest {
  @Test
  void admissionWait001CompletionAfterActualTimedWaitIsConfirmed() throws Exception {
    exercise(false);
  }

  @Test
  void admissionWait002InterruptDuringActualTimedWaitIsUnconfirmedAndRestored() throws Exception {
    exercise(true);
  }

  private static void exercise(boolean interrupt) throws Exception {
    var gate = new WebHttpAdmission();
    gate.admit();
    assertTrue(gate.acquire());
    var entered = new CountDownLatch(1);
    var worker = new AtomicReference<Thread>();
    var executor = Executors.newSingleThreadExecutor();
    boolean completed = false;
    var result =
        executor.submit(
            () -> {
              worker.set(Thread.currentThread());
              entered.countDown();
              try {
                gate.drain(Duration.ofSeconds(5));
                return new Outcome(true, null, Thread.currentThread().isInterrupted());
              } catch (IOException failure) {
                return new Outcome(false, failure, Thread.currentThread().isInterrupted());
              } finally {
                Thread.interrupted();
              }
            });
    try {
      assertTrue(entered.await(3, TimeUnit.SECONDS));
      long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(3);
      // Observation establishes this worker entered wait; it is not a termination witness.
      while (worker.get().getState() != Thread.State.TIMED_WAITING) {
        assertFalse(result.isDone(), "owned drain must still hold one active request");
        assertTrue(System.nanoTime() < deadline, "owned worker must enter bounded wait");
        Thread.onSpinWait();
      }
      if (interrupt) {
        worker.get().interrupt();
      } else {
        gate.completed();
        completed = true;
      }
      var outcome = result.get(3, TimeUnit.SECONDS);
      assertEquals(!interrupt, outcome.confirmed());
      assertEquals(interrupt, outcome.interrupted());
      if (interrupt) {
        assertEquals("Web HTTP drain unconfirmed", outcome.failure().getMessage());
        assertNull(outcome.failure().getCause());
        assertEquals(0, outcome.failure().getSuppressed().length);
      } else {
        assertNull(outcome.failure());
      }
      assertFalse(gate.accepting());
    } finally {
      if (!completed) gate.completed();
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(3, TimeUnit.SECONDS));
    }
  }

  private record Outcome(boolean confirmed, IOException failure, boolean interrupted) {}
}
