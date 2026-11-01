package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Test;

/** SS313/342/352 and SIGNAL-VALUE001..004. No actual service lifecycle or authority. */
final class WebTerminalFlagContractTest {
  @Test
  void signalValue001MissingCapturedFlagRejects() {
    assertThrows(NullPointerException.class, () -> new WebRuntimeFailureSignal<Throwable>(null));
  }
  @Test
  void signalValue002RunnableMutatesTheSameCallerFlagAndIsIdempotent() {
    var captured = new AtomicBoolean();
    var signal = new WebRuntimeFailureSignal<Throwable>(captured);
    assertFalse(captured.get());
    signal.run();
    assertTrue(captured.get());
    signal.run();
    assertTrue(captured.get());
    captured.set(false);
    signal.run();
    assertTrue(captured.get());
  }
  @Test
  void signalValue003ConsumerSignalsWithoutMutatingThrowableValues() {
    var captured = new AtomicBoolean();
    var signal = new WebRuntimeFailureSignal<Throwable>(captured);
    var ordinary = new IllegalArgumentException("PUBLIC_FLAG");
    signal.accept(ordinary);
    assertTrue(captured.get());
    assertEquals("PUBLIC_FLAG", ordinary.getMessage());
    assertNull(ordinary.getCause());
    assertEquals(0, ordinary.getSuppressed().length);
    captured.set(false);
    var fatal = new AssertionError("PUBLIC_FLAG");
    signal.accept(fatal);
    assertTrue(captured.get());
    assertEquals("PUBLIC_FLAG", fatal.getMessage());
    assertNull(fatal.getCause());
    assertEquals(0, fatal.getSuppressed().length);
  }
  @Test
  void signalValue004ConcurrentNotificationsFinishBeforeOwnedPoolIsClosed() throws Exception {
    var captured = new AtomicBoolean();
    var signal = new WebRuntimeFailureSignal<Throwable>(captured);
    var workers = ConcurrentHashMap.<Long>newKeySet();
    var jobs = new ArrayList<Callable<Void>>();
    var publicCause = new IllegalStateException("PUBLIC_FLAG");
    for (int i = 0; i < 64; i++) {
      final boolean consumer = i % 2 != 0;
      jobs.add(() -> {
        workers.add(Thread.currentThread().threadId());
        if (consumer) signal.accept(publicCause);
        else signal.run();
        return null;
      });
    }
    var pool = Executors.newFixedThreadPool(4);
    try (pool) {
      var futures = pool.invokeAll(jobs, 5, TimeUnit.SECONDS);
      assertEquals(64, futures.size());
      for (var future : futures) {
        assertNull(future.get());
        assertTrue(future.isDone());
        assertFalse(future.isCancelled());
      }
    }
    assertTrue(captured.get());
    assertTrue(pool.isTerminated());
    assertTrue(workers.size() >= 1 && workers.size() <= 4);
    assertNull(publicCause.getCause());
    assertEquals(0, publicCause.getSuppressed().length);
    System.out.println("SIGNAL_OWNED_WORKERS=" + workers.size());
  }
}
