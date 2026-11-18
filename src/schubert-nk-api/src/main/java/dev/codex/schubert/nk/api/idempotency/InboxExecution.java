package dev.codex.schubert.nk.api.idempotency;

import java.util.Objects;
import java.util.Optional;

/** Redacted Inbox outcome returned to the API request dispatcher. */
public record InboxExecution(InboxExecutionStatus status, Optional<InboxCompletion> completion) {
  public InboxExecution {
    Objects.requireNonNull(status, "status");
    Objects.requireNonNull(completion, "completion");
    boolean terminal = status != InboxExecutionStatus.IN_PROGRESS;
    if (terminal != completion.isPresent()) {
      throw new IllegalArgumentException("Inbox outcome and completion presence do not match");
    }
  }

  public static InboxExecution executed(InboxCompletion completion) {
    return new InboxExecution(
        InboxExecutionStatus.EXECUTED,
        Optional.of(Objects.requireNonNull(completion, "completion")));
  }

  public static InboxExecution replay(InboxCompletion completion) {
    return new InboxExecution(
        InboxExecutionStatus.REPLAY, Optional.of(Objects.requireNonNull(completion, "completion")));
  }

  public static InboxExecution inProgress() {
    return new InboxExecution(InboxExecutionStatus.IN_PROGRESS, Optional.empty());
  }

  @Override
  public String toString() {
    return "InboxExecution[<redacted>]";
  }
}
