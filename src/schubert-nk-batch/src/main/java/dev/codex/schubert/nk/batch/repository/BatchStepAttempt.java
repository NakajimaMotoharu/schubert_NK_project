package dev.codex.schubert.nk.batch.repository;

import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Identity for one DB step, never a substitute for the immutable root run or caller's commit.
 * NK-BAT-001/OPS009/UI251/SS331 8.3/341; SSC055/PG163; BAT130..137.
 */
@NullMarked
public record BatchStepAttempt(
    long id, BatchRun run, BatchStep step, int attempt, Instant startedAt, boolean skipped) {
  public BatchStepAttempt {
    Objects.requireNonNull(run, "fixed run");
    Objects.requireNonNull(step, "step");
    Objects.requireNonNull(startedAt, "step time");
    if (id < 1 || id > 999999999999L || attempt < 1 || attempt > 99)
      throw new IllegalArgumentException("invalid batch step identity");
    time(run, startedAt);
  }

  public LocalDate businessDate() {
    return run.cutoff().atZone(ZoneId.of("Asia/Tokyo")).toLocalDate();
  }

  static void time(BatchRun run, Instant value) {
    if (value.isBefore(run.cutoff())
        || value.isAfter(Instant.parse("9999-12-31T23:59:59.999999Z"))
        || value.getNano() % 1000 != 0)
      throw new IllegalArgumentException("invalid batch step time");
  }

  @Override
  public String toString() {
    return "BatchStepAttempt[identity/time=<redacted>]";
  }
}
