package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CompletionException;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-JMS-008 bounded, timeout, late and concurrent terminal-state matrix. */
final class ReplyCorrelationRegistryTest {
  private static final Instant NOW = Instant.parse("2026-09-03T00:00:00Z");
  private static final Instant DEADLINE = NOW.plusSeconds(2);
  private static final UUID ID_1 = UUID.fromString("00000000-0000-0000-0000-000000000001");
  private static final UUID ID_2 = UUID.fromString("00000000-0000-0000-0000-000000000002");
  private static final UUID ID_3 = UUID.fromString("00000000-0000-0000-0000-000000000003");

  @Test
  void registrationIsBoundedDuplicateSafeAndReleasesCapacityOnCancel() {
    ReplyCorrelationRegistry registry = new ReplyCorrelationRegistry(2);
    PendingReply first = registry.register(ID_1, DEADLINE, NOW).orElseThrow();
    assertThrows(IllegalStateException.class, () -> registry.register(ID_1, DEADLINE, NOW));
    registry.register(ID_2, DEADLINE, NOW).orElseThrow();

    assertEquals(2, registry.pendingCount());
    assertTrue(registry.register(ID_3, DEADLINE, NOW).isEmpty());
    assertThrows(IllegalStateException.class, () -> registry.register(ID_1, DEADLINE, NOW));
    assertTrue(registry.cancel(ID_1));
    assertEquals(1, registry.pendingCount());
    assertTrue(registry.register(ID_3, DEADLINE, NOW).isPresent());
    assertFalse(registry.cancel(ID_1));
    assertTrue(first.toString().contains("body=<redacted>"));
    assertExceptional(first, java.util.concurrent.CancellationException.class);
  }

  @Test
  void successfulCompletionIsAtomicAndDefensivelyCopiesBody() {
    ReplyCorrelationRegistry registry = new ReplyCorrelationRegistry();
    PendingReply pending = registry.register(ID_1, DEADLINE, NOW).orElseThrow();
    byte[] body = {1, 2, 3};
    assertTrue(registry.complete(ID_1, body, NOW.plusSeconds(1)));
    body[0] = 9;
    var firstCompletion = pending.completion().toCompletableFuture();
    assertTrue(firstCompletion.isDone());
    byte[] received = firstCompletion.join();
    received[1] = 9;

    assertEquals(ID_1, pending.correlationId());
    assertEquals(DEADLINE, pending.deadline());
    var secondCompletion = pending.completion().toCompletableFuture();
    assertTrue(secondCompletion.isDone());
    assertArrayEquals(new byte[] {1, 2, 3}, secondCompletion.join());
    assertEquals(0, registry.pendingCount());
    assertFalse(registry.complete(ID_1, new byte[0], NOW));
    assertEquals(1L, registry.lateResponseCount());
  }

  @Test
  void lateCompletionAndExplicitExpiryFailTheWaiterWithoutDelivery() {
    ReplyCorrelationRegistry registry = new ReplyCorrelationRegistry();
    PendingReply late = registry.register(ID_1, DEADLINE, NOW).orElseThrow();
    assertFalse(registry.complete(ID_1, new byte[] {1}, DEADLINE));
    assertExceptional(late, java.util.concurrent.TimeoutException.class);
    assertEquals(1L, registry.lateResponseCount());

    PendingReply due = registry.register(ID_2, DEADLINE, NOW).orElseThrow();
    assertFalse(registry.expire(ID_2, NOW.plusSeconds(1)));
    assertTrue(registry.expire(ID_2, DEADLINE));
    assertFalse(registry.expire(ID_2, DEADLINE));
    assertExceptional(due, java.util.concurrent.TimeoutException.class);
  }

  @Test
  void nullDeadlineAndCapacityContractsFailBeforeMutation() {
    ReplyCorrelationRegistry registry = new ReplyCorrelationRegistry();
    assertEquals(20, ReplyCorrelationRegistry.STANDARD_CAPACITY);
    assertThrows(IllegalArgumentException.class, () -> new ReplyCorrelationRegistry(0));
    assertThrows(IllegalArgumentException.class, () -> new ReplyCorrelationRegistry(21));
    assertThrows(NullPointerException.class, () -> registry.register(null, DEADLINE, NOW));
    assertThrows(NullPointerException.class, () -> registry.register(ID_1, null, NOW));
    assertThrows(NullPointerException.class, () -> registry.register(ID_1, DEADLINE, null));
    assertThrows(IllegalArgumentException.class, () -> registry.register(ID_1, NOW, NOW));
    assertThrows(NullPointerException.class, () -> registry.complete(null, new byte[0], NOW));
    assertThrows(NullPointerException.class, () -> registry.complete(ID_1, null, NOW));
    assertThrows(NullPointerException.class, () -> registry.complete(ID_1, new byte[0], null));
    assertThrows(NullPointerException.class, () -> registry.expire(null, NOW));
    assertThrows(NullPointerException.class, () -> registry.expire(ID_1, null));
    assertThrows(NullPointerException.class, () -> registry.cancel(null));
    assertEquals(0, registry.pendingCount());
  }

  @Test
  void oneOfOneHundredSimultaneousResponsesWins() throws Exception {
    ReplyCorrelationRegistry registry = new ReplyCorrelationRegistry();
    PendingReply pending = registry.register(ID_1, DEADLINE, NOW).orElseThrow();
    CountDownLatch start = new CountDownLatch(1);
    AtomicInteger winners = new AtomicInteger();
    List<Future<?>> tasks = new ArrayList<>();
    try (ExecutorService executor = Executors.newFixedThreadPool(16)) {
      for (int index = 0; index < 100; index++) {
        int marker = index;
        tasks.add(
            executor.submit(
                () -> {
                  assertTrue(start.await(5, TimeUnit.SECONDS));
                  if (registry.complete(ID_1, new byte[] {(byte) marker}, NOW.plusSeconds(1))) {
                    winners.incrementAndGet();
                  }
                  return null;
                }));
      }
      start.countDown();
      for (Future<?> task : tasks) {
        task.get(5, TimeUnit.SECONDS);
      }
    }
    assertEquals(1, winners.get());
    assertEquals(99L, registry.lateResponseCount());
    var completion = pending.completion().toCompletableFuture();
    assertTrue(completion.isDone());
    assertEquals(1, completion.join().length);
  }

  private static void assertExceptional(PendingReply pending, Class<? extends Throwable> cause) {
    var completion = pending.completion().toCompletableFuture();
    assertTrue(completion.isDone());
    RuntimeException exception = assertThrows(RuntimeException.class, completion::join);
    Throwable actual = exception instanceof CompletionException ? exception.getCause() : exception;
    assertTrue(cause.isInstance(actual));
  }
}
