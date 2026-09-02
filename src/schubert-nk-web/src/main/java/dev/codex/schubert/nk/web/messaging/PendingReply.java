package dev.codex.schubert.nk.web.messaging;

import java.time.Instant;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;

/** One redacted in-flight response promise owned by {@link ReplyCorrelationRegistry}. */
public final class PendingReply {
  private final UUID correlationId;
  private final Instant deadline;
  private final CompletableFuture<byte[]> future = new CompletableFuture<>();

  PendingReply(UUID correlationId, Instant deadline) {
    this.correlationId = Objects.requireNonNull(correlationId, "correlationId");
    this.deadline = Objects.requireNonNull(deadline, "deadline");
  }

  public UUID correlationId() {
    return correlationId;
  }

  public Instant deadline() {
    return deadline;
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
    return "PendingReply[correlationId=" + correlationId + ", deadline=" + deadline + ", body=<redacted>]";
  }
}
