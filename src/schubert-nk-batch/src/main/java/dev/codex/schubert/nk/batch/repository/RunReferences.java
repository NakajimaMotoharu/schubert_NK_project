package dev.codex.schubert.nk.batch.repository;

import org.jspecify.annotations.NullMarked;

/** NK-BAT-001; DAT-009/OPS-009/UI251/SS331 3.12/343; PG-D-159; PT-BAT-082. */
@NullMarked
public record RunReferences(
    boolean hasBatchHistory,
    boolean hasInboxProgress,
    boolean hasLogProgress,
    boolean identityConsistent) {
  public RunReferences {
    if (!hasBatchHistory && !hasInboxProgress && !hasLogProgress && !identityConsistent)
      throw new IllegalArgumentException("inconsistent run reference projection");
  }

  public boolean anyReference() {
    return hasBatchHistory || hasInboxProgress || hasLogProgress;
  }

  @Override
  public String toString() {
    return "RunReferences[observation=<redacted>]";
  }
}
