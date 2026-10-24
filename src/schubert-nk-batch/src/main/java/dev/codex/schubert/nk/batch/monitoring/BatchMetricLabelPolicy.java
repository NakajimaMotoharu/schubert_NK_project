package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.repository.BatchStep;
import io.micrometer.core.instrument.Tag;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.stream.Collectors;

/** NK-OPS-001/RD171/UI252/SS341351/1775 BATCHLABEL: Batch-only values, no writer/resource owner. */
public final class BatchMetricLabelPolicy {
  private static final String RUNS = "nk_batch_runs_total";
  private static final String SUCCESS = "nk_batch_last_success_timestamp_seconds";
  private static final String FILES = "nk_file_transfer_files";
  private static final String BYTES = "nk_file_transfer_bytes";
  private static final String INTEGRITY = "nk_integrity_failures_total";
  private static final String RESTARTS = "nk_process_restarts_total";
  private static final Set<String> BATCH_STEPS =
      Arrays.stream(BatchMetricContract.Step.values())
          .map(Enum::name)
          .collect(Collectors.toUnmodifiableSet());
  private static final Set<String> INTEGRITY_STEPS =
      Arrays.stream(BatchStep.values()).map(Enum::name).collect(Collectors.toUnmodifiableSet());
  private static final Map<String, MetricContract.Kind> TYPES =
      Map.of(
          RUNS,
          MetricContract.Kind.COUNTER,
          SUCCESS,
          MetricContract.Kind.GAUGE,
          FILES,
          MetricContract.Kind.GAUGE,
          BYTES,
          MetricContract.Kind.GAUGE,
          INTEGRITY,
          MetricContract.Kind.COUNTER,
          RESTARTS,
          MetricContract.Kind.COUNTER);
  private static final Map<String, Map<String, Set<String>>> VALUES =
      Map.of(
          RUNS,
          Map.of("step", BATCH_STEPS, "status", Set.of("SUCCESS", "WARNING", "FAILED", "SKIPPED")),
          SUCCESS,
          Map.of("step", BATCH_STEPS),
          FILES,
          Map.of("suffix", Set.of(".part", ".ready")),
          BYTES,
          Map.of("suffix", Set.of(".part", ".ready")),
          INTEGRITY,
          Map.of("area", Set.of("HASH", "PATH", "CONFIG"), "step", INTEGRITY_STEPS),
          RESTARTS,
          Map.of(
              "service",
              Set.of("WEB", "API", "BATCH", "BROKER", "DB", "CADDY"),
              "reason",
              Set.of("NONZERO_EXIT", "SIGNAL_EXIT", "OOM", "UNKNOWN")));

  public BatchMetricLabelPolicy() {}

  /** Immutable names/keys for these six Batch-owned families, not the global26 metadata catalog. */
  public Map<String, Set<String>> names(MetricContract.Kind kind) {
    Objects.requireNonNull(kind, "metric kind");
    var result = new HashMap<String, Set<String>>();
    TYPES.forEach(
        (name, type) -> {
          if (type == kind)
            result.put(
                name,
                Set.copyOf(Objects.requireNonNull(VALUES.get(name), "metric domain").keySet()));
        });
    return Map.copyOf(result);
  }

  /**
   * A detached immutable value copy for the same future model, never approval of a later reread.
   */
  public Map<String, String> labels(String name, List<Tag> tags) {
    var allowed = VALUES.get(Objects.requireNonNull(name, "metric name"));
    if (allowed == null) throw new IllegalArgumentException("unknown Batch metric");
    var result = new TreeMap<String, String>();
    for (var tag : Objects.requireNonNull(tags, "metric tags")) {
      Objects.requireNonNull(tag, "metric tag");
      String key = Objects.requireNonNull(tag.getKey(), "metric label key");
      String value = Objects.requireNonNull(tag.getValue(), "metric label value");
      var choices = allowed.get(key);
      if (choices == null || !choices.contains(value))
        throw new IllegalArgumentException("invalid Batch metric label");
      if (result.put(key, value) != null)
        throw new IllegalArgumentException("duplicate Batch metric label");
    }
    if (!result.keySet().equals(allowed.keySet()))
      throw new IllegalArgumentException("missing Batch metric label");
    return Map.copyOf(result);
  }
}
