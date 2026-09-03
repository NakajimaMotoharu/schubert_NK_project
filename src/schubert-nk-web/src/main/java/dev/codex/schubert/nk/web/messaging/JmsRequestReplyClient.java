package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.protocol.layout.LayoutDefinition;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.JMSException;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

/**
 * Bounded synchronous Web request/reply wait coordinator; it never retries a request automatically.
 *
 * <p>Trace: NK-MSG-001; RD MQ-003～005; UI 212/231; SS 312 §3.2 and 321 §6/§9.
 */
public final class JmsRequestReplyClient {
  public static final int STANDARD_CONCURRENCY = 12;
  public static final Duration MAXIMUM_WAIT = Duration.ofSeconds(2);

  private final ReplyCorrelationRegistry registry;
  private final Clock clock;
  private final Semaphore concurrentWaits;

  public JmsRequestReplyClient() {
    this(new ReplyCorrelationRegistry(), Clock.systemUTC(), STANDARD_CONCURRENCY);
  }

  public JmsRequestReplyClient(
      ReplyCorrelationRegistry registry, Clock clock, int maximumConcurrent) {
    this.registry = Objects.requireNonNull(registry, "registry");
    this.clock = Objects.requireNonNull(clock, "clock");
    if (maximumConcurrent < 1 || maximumConcurrent > STANDARD_CONCURRENCY) {
      throw new IllegalArgumentException("maximum concurrent JMS waits must be between 1 and 12");
    }
    concurrentWaits = new Semaphore(maximumConcurrent);
  }

  /** Registers, sends exactly once, then returns one defensively copied reply body. */
  public byte[] exchange(
      UUID correlationId, byte[] encodedRequest, Duration timeout, JmsRequestSender sender)
      throws JMSException {
    Objects.requireNonNull(correlationId, "correlationId");
    Objects.requireNonNull(encodedRequest, "encodedRequest");
    Objects.requireNonNull(timeout, "timeout");
    Objects.requireNonNull(sender, "sender");
    validateRequest(encodedRequest, timeout);
    if (!concurrentWaits.tryAcquire()) {
      throw failure(
          JmsRequestReplyException.Reason.CAPACITY, "synchronous JMS wait capacity is exhausted");
    }

    try {
      Instant now = clock.instant();
      Instant deadline = now.plus(timeout);
      Optional<PendingReply> registration = registry.register(correlationId, deadline, now);
      if (registration.isEmpty()) {
        throw failure(
            JmsRequestReplyException.Reason.CAPACITY, "reply correlation registry is exhausted");
      }
      PendingReply pending = registration.orElseThrow();
      try {
        sender.send(correlationId, encodedRequest.clone());
        return pending
            .completion()
            .toCompletableFuture()
            .get(timeout.toNanos(), TimeUnit.NANOSECONDS);
      } catch (TimeoutException exception) {
        registry.expire(correlationId, deadline);
        throw failure(
            JmsRequestReplyException.Reason.TIMEOUT, "synchronous JMS reply timed out", exception);
      } catch (InterruptedException exception) {
        registry.cancel(correlationId);
        Thread.currentThread().interrupt();
        throw failure(
            JmsRequestReplyException.Reason.INTERRUPTED,
            "synchronous JMS reply wait was interrupted",
            exception);
      } catch (ExecutionException exception) {
        throw failure(
            JmsRequestReplyException.Reason.TIMEOUT,
            "synchronous JMS reply arrived after its deadline",
            exception.getCause());
      } finally {
        registry.cancel(correlationId);
      }
    } finally {
      concurrentWaits.release();
    }
  }

  /** Called by the single reply consumer after protocol validation. */
  public boolean onReply(UUID correlationId, byte[] encodedReply) {
    return registry.complete(correlationId, encodedReply, clock.instant());
  }

  public int pendingCount() {
    return registry.pendingCount();
  }

  public long lateReplyCount() {
    return registry.lateResponseCount();
  }

  private static void validateRequest(byte[] body, Duration timeout) {
    if (body.length < LayoutDefinition.HEADER_LENGTH
        || body.length > BrokerTopology.SYNC_REQUEST.maximumBodyLength()) {
      throw new IllegalArgumentException("encoded JMS request body length is outside its range");
    }
    if (timeout.isZero() || timeout.isNegative() || timeout.compareTo(MAXIMUM_WAIT) > 0) {
      throw new IllegalArgumentException("JMS request timeout must be between 1ns and 2s");
    }
  }

  private static JmsRequestReplyException failure(
      JmsRequestReplyException.Reason reason, String message) {
    return new JmsRequestReplyException(reason, message);
  }

  private static JmsRequestReplyException failure(
      JmsRequestReplyException.Reason reason, String message, Throwable cause) {
    return new JmsRequestReplyException(reason, message, cause);
  }
}
