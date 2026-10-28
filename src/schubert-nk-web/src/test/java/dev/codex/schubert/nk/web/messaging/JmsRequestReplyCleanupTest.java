package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.JMSException;
import java.time.Clock;
import java.time.DateTimeException;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** PT-JMS-RECOVERY-001..004; SS321 sections6/9, independent memory-only failure recovery. */
final class JmsRequestReplyCleanupTest {
  private static final Instant NOW = Instant.parse("2026-10-28T00:00:00Z");
  private static final UUID FIRST = new UUID(0, 1);
  private static final UUID SECOND = new UUID(0, 2);
  private static final Duration WAIT = Duration.ofSeconds(2);

  @Test
  void everySendFailureKeepsIdentityAndReturnsBothCapacities() throws Exception {
    ReplyCorrelationRegistry registry = new ReplyCorrelationRegistry(1);
    JmsRequestReplyClient client =
        new JmsRequestReplyClient(registry, Clock.fixed(NOW, ZoneOffset.UTC), 1);
    for (Throwable failure :
        List.of(
            new JMSException("synthetic"),
            new IllegalStateException("synthetic"),
            new AssertionError("synthetic"))) {
      AtomicInteger sends = new AtomicInteger();
      Throwable actual =
          assertThrows(
              failure.getClass(),
              () ->
                  client.exchange(
                      FIRST,
                      new byte[256],
                      WAIT,
                      (id, body) -> {
                        sends.incrementAndGet();
                        if (failure instanceof JMSException checked) {
                          throw checked;
                        }
                        if (failure instanceof RuntimeException unchecked) {
                          throw unchecked;
                        }
                        throw (AssertionError) failure;
                      }));
      assertSame(failure, actual);
      assertEquals(1, sends.get());
      assertEquals(0, registry.pendingCount());
      assertEquals(0, client.pendingCount());
      assertRecovered(client);
    }
    assertEquals(0L, client.lateReplyCount());
  }

  @Test
  void registryFullDoesNotCancelAnotherWaiterAndRecovers() throws Exception {
    ReplyCorrelationRegistry registry = new ReplyCorrelationRegistry(1);
    PendingReply borrowed = registry.register(SECOND, NOW.plusSeconds(2), NOW).orElseThrow();
    JmsRequestReplyClient client =
        new JmsRequestReplyClient(registry, Clock.fixed(NOW, ZoneOffset.UTC), 1);
    AtomicInteger sends = new AtomicInteger();
    JmsRequestReplyException failure =
        assertThrows(
            JmsRequestReplyException.class,
            () ->
                client.exchange(FIRST, new byte[256], WAIT, (id, body) -> sends.incrementAndGet()));
    assertEquals(JmsRequestReplyException.Reason.CAPACITY, failure.reason());
    assertEquals(0, sends.get());
    assertEquals(1, registry.pendingCount());
    assertEquals(SECOND, borrowed.correlationId());
    assertFalse(borrowed.completion().toCompletableFuture().isDone());
    assertTrue(registry.cancel(SECOND));
    assertRecovered(client);
    assertEquals(0, registry.pendingCount());
  }

  @Test
  void clockFailureAndDeadlineOverflowReturnTheWaitPermit() throws Exception {
    IllegalStateException clockFailure = new IllegalStateException("synthetic clock");
    for (boolean overflow : List.of(false, true)) {
      Clock clock =
          firstThenNow(
              () -> {
                if (overflow) {
                  return Instant.MAX;
                }
                throw clockFailure;
              });
      JmsRequestReplyClient client =
          new JmsRequestReplyClient(new ReplyCorrelationRegistry(1), clock, 1);
      AtomicInteger sends = new AtomicInteger();
      if (overflow) {
        assertThrows(
            DateTimeException.class,
            () ->
                client.exchange(FIRST, new byte[256], WAIT, (id, body) -> sends.incrementAndGet()));
      } else {
        assertSame(
            clockFailure,
            assertThrows(
                IllegalStateException.class,
                () ->
                    client.exchange(
                        FIRST, new byte[256], WAIT, (id, body) -> sends.incrementAndGet())));
      }
      assertEquals(0, sends.get());
      assertEquals(0, client.pendingCount());
      assertRecovered(client);
    }
  }

  @Test
  void suppliedRequestAndReplyBuffersRemainBorrowed() throws Exception {
    JmsRequestReplyClient client =
        new JmsRequestReplyClient(
            new ReplyCorrelationRegistry(1), Clock.fixed(NOW, ZoneOffset.UTC), 1);
    byte[] request = new byte[256];
    request[0] = 11;
    request[255] = 22;
    byte[] expectedRequest = new byte[256];
    expectedRequest[0] = 11;
    expectedRequest[255] = 22;
    byte[] reply = {31, 32};
    AtomicInteger sends = new AtomicInteger();
    byte[] actual =
        client.exchange(
            FIRST,
            request,
            WAIT,
            (id, sent) -> {
              sends.incrementAndGet();
              assertNotSame(request, sent);
              assertArrayEquals(expectedRequest, sent);
              sent[0] = 99;
              sent[255] = 99;
              assertTrue(client.onReply(id, reply));
            });
    assertNotSame(reply, actual);
    reply[0] = 99;
    assertArrayEquals(new byte[] {31, 32}, actual);
    assertArrayEquals(expectedRequest, request);
    assertEquals(1, sends.get());
    assertEquals(0, client.pendingCount());
  }

  private static void assertRecovered(JmsRequestReplyClient client) throws JMSException {
    AtomicInteger sends = new AtomicInteger();
    byte[] actual =
        client.exchange(
            FIRST,
            new byte[256],
            WAIT,
            (id, body) -> {
              sends.incrementAndGet();
              assertTrue(client.onReply(id, new byte[] {31, 32}));
            });
    assertArrayEquals(new byte[] {31, 32}, actual);
    assertEquals(1, sends.get());
    assertEquals(0, client.pendingCount());
  }

  private static Clock firstThenNow(Supplier<Instant> first) {
    AtomicInteger calls = new AtomicInteger();
    return new Clock() {
      @Override
      public ZoneId getZone() {
        return ZoneOffset.UTC;
      }

      @Override
      public Clock withZone(ZoneId zone) {
        return Clock.fixed(NOW, zone);
      }

      @Override
      public Instant instant() {
        return calls.getAndIncrement() == 0 ? first.get() : NOW;
      }
    };
  }
}
