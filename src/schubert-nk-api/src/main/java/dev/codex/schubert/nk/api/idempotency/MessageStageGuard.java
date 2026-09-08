package dev.codex.schubert.nk.api.idempotency;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Supplier;

/**
 * Single-service, single-API-process guard across DB/file stages, never a distributed Inbox lock.
 * NK-SCN-001/NK-MED-001/NK-MSG-002; MQ-006..010/FIL-001..009; UI211/237/241; SS324 §7.1;
 * SSC-027/PG-D-069/080; PT-SCN-009-G01..G03/PT-MED-058/061. Startup must enforce one instance per
 * service before registration.
 */
public final class MessageStageGuard {
  private final ReentrantLock[] stripes = new ReentrantLock[256];

  public MessageStageGuard() {
    for (int i = 0; i < stripes.length; i++) stripes[i] = new ReentrantLock(true);
  }

  /** No connection may be owned while waiting; callback still must enforce DB Inbox identity. */
  public <T> T execute(UUID messageId, Supplier<T> operation) {
    Objects.requireNonNull(messageId, "messageId");
    Objects.requireNonNull(operation, "operation");
    ReentrantLock lock = stripes[messageId.hashCode() & 255];
    try {
      lock.lockInterruptibly();
    } catch (InterruptedException failure) {
      Thread.currentThread().interrupt();
      throw new TemporaryInfrastructureException();
    }
    try {
      return Objects.requireNonNull(operation.get(), "stage result");
    } finally {
      lock.unlock();
    }
  }
}
