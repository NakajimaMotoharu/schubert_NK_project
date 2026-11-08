package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CancellationException;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.junit.jupiter.api.Test;

/** PT-JMS-TERM-001..004; SS321 section9 independent memory-only terminal/permit oracles. */
final class ReplyCorrelationTerminalRaceTest {
  private static final Instant NOW = Instant.parse("2026-10-28T00:00:00Z");
  private static final Instant DEADLINE = NOW.plusSeconds(2);
  private static final UUID FIRST = new UUID(0, 1);
  private static final UUID SECOND = new UUID(0, 2);
  private static final UUID THIRD = new UUID(0, 3);

  @Test
  void terminalRaceHasOneWinnerAndReturnsThePermit() throws Exception {
    try (ExecutorService workers = Executors.newFixedThreadPool(3)) {
      for (int iteration = 0; iteration < 64; iteration++) {
        ReplyCorrelationRegistry registry = new ReplyCorrelationRegistry(1);
        PendingReply pending = registry.register(FIRST, DEADLINE, NOW).orElseThrow();
        CountDownLatch start = new CountDownLatch(1);
        List<Future<Boolean>> terminals = new ArrayList<>();
        try {
          terminals.add(
              workers.submit(
                  () -> {
                    assertTrue(start.await(5, TimeUnit.SECONDS));
                    return registry.complete(FIRST, new byte[] {7, 8, 9}, DEADLINE.minusNanos(1));
                  }));
          terminals.add(
              workers.submit(
                  () -> {
                    assertTrue(start.await(5, TimeUnit.SECONDS));
                    return registry.cancel(FIRST);
                  }));
          terminals.add(
              workers.submit(
                  () -> {
                    assertTrue(start.await(5, TimeUnit.SECONDS));
                    return registry.expire(FIRST, DEADLINE);
                  }));
        } finally {
          start.countDown();
        }
        boolean completed = terminals.get(0).get(10, TimeUnit.SECONDS);
        boolean cancelled = terminals.get(1).get(10, TimeUnit.SECONDS);
        boolean expired = terminals.get(2).get(10, TimeUnit.SECONDS);
        assertEquals(1, (completed ? 1 : 0) + (cancelled ? 1 : 0) + (expired ? 1 : 0));
        assertEquals(0, registry.pendingCount());
        assertEquals(completed ? 0L : 1L, registry.lateResponseCount());
        if (completed) {
          assertArrayEquals(
              new byte[] {7, 8, 9}, pending.completion().toCompletableFuture().join());
        } else {
          CompletionException failure =
              assertThrows(
                  CompletionException.class,
                  () -> pending.completion().toCompletableFuture().join());
          if (cancelled) {
            assertInstanceOf(CancellationException.class, failure.getCause());
          } else {
            assertInstanceOf(TimeoutException.class, failure.getCause());
          }
        }
        assertTrue(registry.register(SECOND, DEADLINE, NOW).isPresent());
        assertTrue(registry.register(THIRD, DEADLINE, NOW).isEmpty());
        assertTrue(registry.cancel(SECOND));
        assertEquals(0, registry.pendingCount());
      }
    }
  }

  @Test
  void concurrentRegistrationsRespectCapacityAndReuseAllSlots() throws Exception {
    ReplyCorrelationRegistry registry = new ReplyCorrelationRegistry(2);
    CountDownLatch start = new CountDownLatch(1);
    List<Future<Optional<PendingReply>>> calls = new ArrayList<>();
    List<PendingReply> accepted = new ArrayList<>();
    try (ExecutorService workers = Executors.newFixedThreadPool(20)) {
      try {
        for (int index = 1; index <= 20; index++) {
          UUID id = new UUID(0, index);
          calls.add(
              workers.submit(
                  () -> {
                    assertTrue(start.await(5, TimeUnit.SECONDS));
                    return registry.register(id, DEADLINE, NOW);
                  }));
        }
      } finally {
        start.countDown();
      }
      int rejected = 0;
      for (Future<Optional<PendingReply>> call : calls) {
        Optional<PendingReply> value = call.get(10, TimeUnit.SECONDS);
        if (value.isPresent()) {
          accepted.add(value.orElseThrow());
        } else {
          rejected++;
        }
      }
      assertEquals(2, accepted.size());
      assertEquals(18, rejected);
      assertEquals(2, registry.pendingCount());
      for (PendingReply pending : accepted) {
        assertTrue(registry.cancel(pending.correlationId()));
      }
    }
    assertEquals(0, registry.pendingCount());
    assertTrue(registry.register(FIRST, DEADLINE, NOW).isPresent());
    assertTrue(registry.register(SECOND, DEADLINE, NOW).isPresent());
    assertTrue(registry.register(THIRD, DEADLINE, NOW).isEmpty());
    assertTrue(registry.cancel(FIRST));
    assertTrue(registry.cancel(SECOND));
    assertEquals(0, registry.pendingCount());
  }

  @Test
  void nanosecondDeadlineAndCopiesStayIndependent() {
    ReplyCorrelationRegistry registry = new ReplyCorrelationRegistry(1);
    PendingReply timely = registry.register(FIRST, DEADLINE, NOW).orElseThrow();
    byte[] supplied = {7, 8, 9};
    assertTrue(registry.complete(FIRST, supplied, DEADLINE.minusNanos(1)));
    supplied[0] = 42;
    byte[] received = timely.completion().toCompletableFuture().join();
    received[1] = 42;
    assertArrayEquals(new byte[] {7, 8, 9}, timely.completion().toCompletableFuture().join());
    for (Instant arrival : List.of(DEADLINE, DEADLINE.plusNanos(1))) {
      PendingReply late = registry.register(SECOND, DEADLINE, NOW).orElseThrow();
      assertFalse(registry.complete(SECOND, new byte[] {7, 8, 9}, arrival));
      CompletionException failure =
          assertThrows(
              CompletionException.class, () -> late.completion().toCompletableFuture().join());
      assertInstanceOf(TimeoutException.class, failure.getCause());
    }
    assertEquals(2L, registry.lateResponseCount());
    assertEquals(0, registry.pendingCount());
  }

  @Test
  void callerCompletionViewCannotSetOrCancelTheRegistryPromise() {
    ReplyCorrelationRegistry registry = new ReplyCorrelationRegistry(1);
    for (boolean cancelView : List.of(false, true)) {
      PendingReply pending = registry.register(FIRST, DEADLINE, NOW).orElseThrow();
      CompletableFuture<byte[]> caller = pending.completion().toCompletableFuture();
      CompletableFuture<byte[]> independent = pending.completion().toCompletableFuture();
      if (cancelView) {
        assertTrue(caller.cancel(false));
      } else {
        assertTrue(caller.complete(new byte[] {42}));
      }
      assertFalse(independent.isDone());
      assertEquals(1, registry.pendingCount());
      assertTrue(registry.complete(FIRST, new byte[] {7, 8, 9}, NOW));
      assertArrayEquals(new byte[] {7, 8, 9}, independent.join());
      assertArrayEquals(new byte[] {7, 8, 9}, pending.completion().toCompletableFuture().join());
      assertEquals(0, registry.pendingCount());
    }
    assertEquals(0L, registry.lateResponseCount());
  }
}
