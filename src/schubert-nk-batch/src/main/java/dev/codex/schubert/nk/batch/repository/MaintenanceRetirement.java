package dev.codex.schubert.nk.batch.repository;

import java.time.Duration;
import java.time.Instant;
import java.util.Objects;
import java.util.regex.Pattern;
import org.jspecify.annotations.NullMarked;

/**
 * Sealed full-plan identity, not independent permission to delete files. NK-BAT-001;
 * OPS-009/UI251/SS343 6.16; SSC-055/PG-D-161; PT-BAT-090..113.
 */
@NullMarked
public record MaintenanceRetirement(
    BatchRun run, Instant latestEnded, Instant preparedAt, int count, String digest) {
  private static final Instant MAXIMUM = Instant.parse("9999-12-31T23:59:59.999999Z");
  private static final Pattern HASH = Pattern.compile("[0-9a-f]{64}");

  public MaintenanceRetirement {
    Objects.requireNonNull(run, "retiring run");
    Objects.requireNonNull(latestEnded, "latest completion");
    Objects.requireNonNull(preparedAt, "retirement time");
    Objects.requireNonNull(digest, "plan digest");
    if (latestEnded.isBefore(run.cutoff())
        || latestEnded.isAfter(MAXIMUM)
        || latestEnded.getNano() % 1000 != 0
        || preparedAt.isAfter(MAXIMUM)
        || preparedAt.getNano() % 1000 != 0
        || Duration.between(latestEnded, preparedAt).compareTo(Duration.ofDays(400)) <= 0
        || count <= 0
        || !HASH.matcher(digest).matches())
      throw new IllegalArgumentException("invalid maintenance retirement");
  }

  @Override
  public String toString() {
    return "MaintenanceRetirement[identity/time/plan=<redacted>]";
  }
}
