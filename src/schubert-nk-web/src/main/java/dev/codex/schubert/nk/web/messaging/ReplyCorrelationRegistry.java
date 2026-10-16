package dev.codex.schubert.nk.web.messaging;

import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CancellationException;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.atomic.LongAdder;

/**
 * Bounded, atomic correlation registry for one Web process.
 *
 * <p>Trace: NK-MSG-001; RD MQ-004/MQ-005; UI 231; SS 312 §3.2 and 321 §9.
 */
public final class ReplyCorrelationRegistry {
  private static final java.lang.String LITERAL_CORRELATIONID = "correlationId";

  public static final int STANDARD_CAPACITY = 20;

  private final ConcurrentMap<UUID, PendingReply> pending = new ConcurrentHashMap<>();
  private final Semaphore capacity;
  private final LongAdder lateResponses = new LongAdder();

  public ReplyCorrelationRegistry() {
    this(STANDARD_CAPACITY);
  }

  public ReplyCorrelationRegistry(int maximumPending) {
    if (maximumPending < 1 || maximumPending > STANDARD_CAPACITY) {
      throw new IllegalArgumentException("maximum pending replies must be between 1 and 20");
    }
    capacity = new Semaphore(maximumPending);
  }

  /** Registers before send. Empty means the bounded registry is full. */
  public Optional<PendingReply> register(UUID correlationId, Instant deadline, Instant now) {
    Objects.requireNonNull(correlationId, LITERAL_CORRELATIONID);
    Objects.requireNonNull(deadline, "deadline");
    Objects.requireNonNull(now, "now");
    if (!now.isBefore(deadline)) {
      throw new IllegalArgumentException("reply deadline must be in the future");
    }
    if (!capacity.tryAcquire()) {
      if (pending.containsKey(correlationId)) {
        throw new IllegalStateException("duplicate reply correlation ID");
      }
      return Optional.empty();
    }
    PendingReply registration = new PendingReply(correlationId, deadline);
    PendingReply existing = pending.putIfAbsent(correlationId, registration);
    if (existing != null) {
      capacity.release();
      throw new IllegalStateException("duplicate reply correlation ID");
    }
    return Optional.of(registration);
  }

  /** Completes at most one waiter; late and unknown responses are counted and ignored. */
  public boolean complete(UUID correlationId, byte[] body, Instant now) {
    Objects.requireNonNull(correlationId, LITERAL_CORRELATIONID);
    Objects.requireNonNull(body, "body");
    Objects.requireNonNull(now, "now");
    PendingReply registration = pending.remove(correlationId);
    if (registration == null) {
      lateResponses.increment();
      return false;
    }
    capacity.release();
    if (!now.isBefore(registration.deadline())) {
      registration.fail(new TimeoutException("reply arrived after its deadline"));
      lateResponses.increment();
      return false;
    }
    registration.complete(body);
    return true;
  }

  /**
   * Removes a due waiter. Calling before its deadline or after another terminal action is a no-op.
   */
  public boolean expire(UUID correlationId, Instant now) {
    Objects.requireNonNull(correlationId, LITERAL_CORRELATIONID);
    Objects.requireNonNull(now, "now");
    AtomicReference<PendingReply> expired = new AtomicReference<>();
    pending.computeIfPresent(
        correlationId,
        (ignored, registration) -> {
          if (now.isBefore(registration.deadline())) {
            return registration;
          }
          expired.set(registration);
          return null;
        });
    PendingReply registration = expired.get();
    if (registration == null) {
      return false;
    }
    capacity.release();
    registration.fail(new TimeoutException("reply wait expired"));
    return true;
  }

  /** Removes a waiter after send failure or request cancellation. */
  public boolean cancel(UUID correlationId) {
    Objects.requireNonNull(correlationId, LITERAL_CORRELATIONID);
    PendingReply registration = pending.remove(correlationId);
    if (registration == null) {
      return false;
    }
    capacity.release();
    registration.fail(new CancellationException("reply wait was cancelled"));
    return true;
  }

  public int pendingCount() {
    return pending.size();
  }

  public long lateResponseCount() {
    return lateResponses.sum();
  }
}
