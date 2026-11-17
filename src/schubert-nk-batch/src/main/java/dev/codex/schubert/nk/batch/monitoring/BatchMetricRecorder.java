package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.BatchMetricContract.Status;
import dev.codex.schubert.nk.batch.monitoring.BatchMetricContract.Step;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tags;
import java.time.Instant;
import java.util.EnumMap;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Borrowed dedicated registry, no actual Batch/DB/persistent-source operations. RD171/UI252/SS351;
 * PG-D536/BATCHREC001..008/spec1611.
 */
public final class BatchMetricRecorder {
  private static final int NANOS_PER_MICROSECOND = 1000;
  private static final Instant MIN = Instant.parse("0001-01-01T00:00:00Z");
  private static final Instant MAX = Instant.parse("9999-12-31T23:59:59.999999Z");
  private final ReentrantLock lock = new ReentrantLock();
  private final boolean collectDetailed;
  private final Map<Step, Map<Status, Counter>> counters;
  private final Map<Step, AtomicReference<Optional<Instant>>> lastSuccess;

  /** Caller owns registry cleanup, even on a partial constructor failure. No provider retry. */
  public BatchMetricRecorder(MeterRegistry registry, String mode) {
    Objects.requireNonNull(registry, "meter registry");
    var contract = new BatchMetricContract();
    collectDetailed = contract.detailedMetricsEnabled(mode);
    var counts = new EnumMap<Step, Map<Status, Counter>>(Step.class);
    var success = new EnumMap<Step, AtomicReference<Optional<Instant>>>(Step.class);
    if (collectDetailed) {
      for (var step : Step.values()) {
        var statuses = new EnumMap<Status, Counter>(Status.class);
        for (var status : Status.values())
          statuses.put(
              status,
              Counter.builder(contract.runsName())
                  .tags(tags(contract.runLabels(step, status)))
                  .register(registry));
        counts.put(step, Map.copyOf(statuses));
        var observed = new AtomicReference<Optional<Instant>>(Optional.empty());
        Gauge.builder(contract.lastSuccessName(), observed, BatchMetricRecorder::seconds)
            .tags(tags(contract.successLabels(step)))
            .register(registry);
        success.put(step, observed);
      }
    }
    counters = Map.copyOf(counts);
    lastSuccess = Map.copyOf(success);
  }

  /** One caller-proven terminal observation, not deduplication or business SUCCESS authority. */
  public void record(Step step, Status status, Instant endedAt) {
    Objects.requireNonNull(step, "batch step");
    Objects.requireNonNull(status, "batch status");
    Objects.requireNonNull(endedAt, "batch end timestamp");
    if (endedAt.isBefore(MIN)
        || endedAt.isAfter(MAX)
        || endedAt.getNano() % NANOS_PER_MICROSECOND != 0)
      throw new IllegalArgumentException("invalid batch metric timestamp");
    if (!collectDetailed) return;
    lock.lock();
    try {
      Objects.requireNonNull(
              Objects.requireNonNull(counters.get(step), "closed batch step").get(status),
              "closed batch status")
          .increment();
      if (status == Status.SUCCESS) {
        var state = Objects.requireNonNull(lastSuccess.get(step), "closed batch success state");
        var previous = state.get();
        if (previous.isEmpty() || endedAt.isAfter(previous.orElseThrow()))
          state.set(Optional.of(endedAt));
      }
    } finally {
      lock.unlock();
    }
  }

  public boolean detailedMetricsRequested() {
    return collectDetailed;
  }

  private static double seconds(AtomicReference<Optional<Instant>> observed) {
    return observed
        .get()
        .map(at -> at.getEpochSecond() + at.getNano() / 1_000_000_000.0)
        .orElse(Double.NaN);
  }

  private static Tags tags(Map<String, String> labels) {
    Tags tags = Tags.empty();
    for (var entry : labels.entrySet()) tags = tags.and(entry.getKey(), entry.getValue());
    return tags;
  }
}
