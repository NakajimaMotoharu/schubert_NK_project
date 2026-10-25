package dev.codex.schubert.nk.api.application.scenario;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.MessageStageGuard;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.FutureTask;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-SCN-009-G01..G03: latch-controlled side effects and lifetime, not timing/sleep assertions. */
final class ScenarioMessageGuardTest {
  @Test
  void sameMessageAndHashCollisionSerializeButNeverShareResults() throws Exception {
    var guard = new MessageStageGuard();
    UUID message = new UUID(0, 1);
    assertThrows(NullPointerException.class, () -> guard.execute(null, () -> 1));
    assertThrows(NullPointerException.class, () -> guard.execute(message, null));
    try (var workers = Executors.newVirtualThreadPerTaskExecutor()) {
      var start = new CountDownLatch(1);
      var entered = new AtomicInteger();
      Map<UUID, Integer> persisted =
          new HashMap<>(); // Guard is the sole mutual-exclusion mechanism.
      var writes = new AtomicInteger();
      List<Future<Integer>> calls = new ArrayList<>();
      for (int i = 0; i < 100; i++) {
        final int expected = i;
        calls.add(
            workers.submit(
                () -> {
                  await(start);
                  return guard.execute(
                      message,
                      () -> {
                        assertEquals(1, entered.incrementAndGet());
                        if (!persisted.containsKey(message)) {
                          persisted.put(message, 37);
                          writes.incrementAndGet();
                        }
                        assertEquals(37, persisted.get(message));
                        assertEquals(0, entered.decrementAndGet());
                        return expected;
                      });
                }));
      }
      start.countDown();
      for (int i = 0; i < calls.size(); i++)
        assertEquals(i, calls.get(i).get(10, TimeUnit.SECONDS));
      assertEquals(1, writes.get());
      assertEquals(Map.of(message, 37), persisted);
      // SS324 lower 8 bits: 1 and 257 intentionally collide without being the same UUID.
      UUID collision = new UUID(0, 257);
      var held = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      var owner =
          workers.submit(
              () ->
                  guard.execute(
                      message,
                      () -> {
                        held.countDown();
                        await(release);
                        return "first";
                      }));
      await(held);
      var second =
          workers.submit(
              () ->
                  guard.execute(
                      collision,
                      () -> {
                        assertEquals(0, release.getCount());
                        return "second";
                      }));
      release.countDown();
      assertEquals("first", owner.get(10, TimeUnit.SECONDS));
      assertEquals("second", second.get(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void differentStripesRunTogetherAndCallerMonitorDoesNotBlock() throws Exception {
    var guard = new MessageStageGuard();
    try (var workers = Executors.newVirtualThreadPerTaskExecutor()) {
      var allEntered = new CountDownLatch(8);
      var release = new CountDownLatch(1);
      List<Future<Integer>> calls = new ArrayList<>();
      synchronized (guard) {
        for (int i = 0; i < 8; i++) {
          final int index = i;
          calls.add(
              workers.submit(
                  () ->
                      guard.execute(
                          new UUID(0, index),
                          () -> {
                            allEntered.countDown();
                            await(release);
                            return index;
                          })));
        }
        try {
          await(allEntered);
        } finally {
          release.countDown();
        }
        for (int i = 0; i < calls.size(); i++)
          assertEquals(i, calls.get(i).get(10, TimeUnit.SECONDS));
      }
      // Negative UUID hash still selects a valid stripe, and does not conflate its result.
      assertEquals("negative", guard.execute(new UUID(Long.MIN_VALUE, -1), () -> "negative"));
    }
  }

  @Test
  void interruptAndCallbackFailuresReleaseOnlyOwnedLocks() throws Exception {
    var guard = new MessageStageGuard();
    UUID message = new UUID(0, 1);
    try (var workers = Executors.newVirtualThreadPerTaskExecutor()) {
      var held = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      var owner =
          workers.submit(
              () ->
                  guard.execute(
                      message,
                      () -> {
                        held.countDown();
                        await(release);
                        return 17;
                      }));
      await(held);
      var attempted = new CountDownLatch(1);
      var interrupted =
          new FutureTask<Boolean>(
              () -> {
                attempted.countDown();
                var failure =
                    assertThrows(
                        TemporaryInfrastructureException.class,
                        () -> guard.execute(message, () -> fail("interrupted callback ran")));
                assertEquals("request transaction is unavailable", failure.getMessage());
                assertNull(failure.getCause());
                assertEquals(0, failure.getSuppressed().length);
                return Thread.currentThread().isInterrupted();
              });
      Thread waiter = Thread.ofVirtual().unstarted(interrupted);
      waiter.start();
      try {
        await(attempted);
        waiter.interrupt();
        assertTrue(interrupted.get(10, TimeUnit.SECONDS));
      } finally {
        release.countDown();
      }
      assertEquals(17, owner.get(10, TimeUnit.SECONDS));
      for (boolean nullResult : List.of(false, true)) {
        var failure =
            workers.submit(
                () -> {
                  if (nullResult)
                    assertThrows(
                        NullPointerException.class, () -> guard.execute(message, () -> null));
                  else
                    assertThrows(
                        IllegalArgumentException.class,
                        () ->
                            guard.execute(
                                message,
                                () -> {
                                  throw new IllegalArgumentException("synthetic stage failure");
                                }));
                  return 1;
                });
        assertEquals(1, failure.get(10, TimeUnit.SECONDS));
        // A fresh thread, not a reentrant acquisition by the failed owner.
        assertEquals(
            29, workers.submit(() -> guard.execute(message, () -> 29)).get(10, TimeUnit.SECONDS));
      }
    }
  }

  private static void await(CountDownLatch latch) {
    try {
      assertTrue(latch.await(10, TimeUnit.SECONDS), "fixture coordination did not complete");
    } catch (InterruptedException failure) {
      Thread.currentThread().interrupt();
      throw new AssertionError(failure);
    }
  }
}
