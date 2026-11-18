package dev.codex.schubert.nk.web.messaging;

import java.time.Instant;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;

/**
 * One redacted in-flight response promise owned by {@link ReplyCorrelationRegistry}.
 * NK-MSG-001, SS321/351, SSC-459, PT-JMS-008/PT-P01810-CATALOG-038.
 */
public final class PendingReply {
  private final UUID retainedCorrelationId;
  private final Instant retainedDeadline;
  private final CompletableFuture<byte[]> future = new CompletableFuture<>();

  PendingReply(UUID correlationId, Instant deadline) {
    this.retainedCorrelationId = Objects.requireNonNull(correlationId, "correlationId");
    this.retainedDeadline = Objects.requireNonNull(deadline, "deadline");
  }

  public UUID correlationId() {
    return retainedCorrelationId;
  }

  public Instant deadline() {
    return retainedDeadline;
  }

  /** Returns a view that defensively copies the response body for each caller. */
  public CompletionStage<byte[]> completion() {
    return future.thenApply(byte[]::clone);
  }

  void complete(byte[] body) {
    future.complete(body.clone());
  }

  void fail(Throwable failure) {
    future.completeExceptionally(failure);
  }

  @Override
  public String toString() {
    return "PendingReply[correlationId/deadline/body=<redacted>]";
  }
}
