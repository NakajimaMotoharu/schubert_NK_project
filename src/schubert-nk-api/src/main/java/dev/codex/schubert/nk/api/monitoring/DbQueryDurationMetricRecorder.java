package dev.codex.schubert.nk.api.monitoring;

import io.micrometer.core.instrument.DistributionSummary;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.EnumMap;
import java.util.Map;
import java.util.Objects;

/**
 * Supplied durations for two monitoring-reader queries only, never SQL or clock authority.
 * SS351;1712.
 */
public final class DbQueryDurationMetricRecorder {
  public enum Query {
    ASYNC_JOB_STATE_COUNTS,
    OUTBOX_STATUS_COUNTS_OLDEST;

    public static Query parse(String value) {
      Objects.requireNonNull(value, "DB metric query");
      for (var candidate : values()) if (candidate.name().equals(value)) return candidate;
      throw new IllegalArgumentException("invalid DB metric query");
    }
  }

  public enum Outcome {
    SUCCESS,
    FAILURE;

    public static Outcome parse(String value) {
      Objects.requireNonNull(value, "DB metric outcome");
      for (var candidate : values()) if (candidate.name().equals(value)) return candidate;
      throw new IllegalArgumentException("invalid DB metric outcome");
    }
  }

  private final boolean detailed;
  private final Map<Query, Map<Outcome, DistributionSummary>> observations;

  /**
   * Borrowed registry; histogram buckets are observations, never latency acceptance/alert gates.
   */
  public DbQueryDurationMetricRecorder(MeterRegistry registry, String mode) {
    Objects.requireNonNull(registry, "meter registry");
    detailed =
        switch (Objects.requireNonNull(mode, "monitoring mode")) {
          case "DEBUG" -> true;
          case "STANDARD" -> false;
          default -> throw new IllegalArgumentException("CONFIG_INVALID");
        };
    var queries = new EnumMap<Query, Map<Outcome, DistributionSummary>>(Query.class);
    if (detailed) ExactDurationMeterRegistry.requireCompatible(registry);
    if (detailed)
      for (var query : Query.values()) {
        var outcomes = new EnumMap<Outcome, DistributionSummary>(Outcome.class);
        for (var outcome : Outcome.values())
          outcomes.put(
              outcome,
              DistributionSummary.builder("nk_db_query_duration_seconds")
                  .baseUnit("seconds")
                  .tags("query_id", query.name(), "outcome", outcome.name())
                  .publishPercentileHistogram()
                  .publishPercentiles()
                  // Finite exact buckets are provided by the required duration-capable registry.
                  .serviceLevelObjectives(.001, .01, .1, 1., 1.5)
                  .register(registry));
        queries.put(query, Map.copyOf(outcomes));
      }
    observations = Map.copyOf(queries);
  }

  /**
   * Nonnegative scalar nanoseconds to finite binary64 seconds; no overflowing long sum/conversion.
   */
  public void record(Query query, Outcome outcome, long elapsedNanoseconds) {
    Objects.requireNonNull(query, "DB metric query");
    Objects.requireNonNull(outcome, "DB metric outcome");
    if (elapsedNanoseconds < 0) throw new IllegalArgumentException("invalid DB metric duration");
    if (detailed) {
      var outcomes = Objects.requireNonNull(observations.get(query), "registered DB query");
      Objects.requireNonNull(outcomes.get(outcome), "registered DB outcome")
          .record(elapsedNanoseconds / 1_000_000_000.0);
    }
  }

  public boolean detailedMetricsRequested() {
    return detailed;
  }
}
