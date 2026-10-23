package dev.codex.schubert.nk.batch.monitoring;

import java.util.Map;
import java.util.Objects;

/**
 * Closed persisted-step terminal labels, not an admission or true terminal proof.
 * RD171/UI252/SS341351; PG-D536/BATCHMET001..005/spec1611.
 */
public final class BatchMetricContract {
  public enum Step {
    BACKUP_DB,
    BACKUP_CONFIG,
    CLEAN_NOTIFICATION,
    CLEAN_QUESTION,
    CLEAN_SESSION,
    CLEAN_INBOX_OUTBOX,
    CLEAN_LOG,
    CLEAN_BATCH_RUN,
    CLEAN_TRANSFER,
    CLEAN_EXPIRY
  }

  public enum Status {
    SUCCESS,
    WARNING,
    FAILED,
    SKIPPED
  }

  public String runsName() {
    return "nk_batch_runs_total";
  }

  public String lastSuccessName() {
    return "nk_batch_last_success_timestamp_seconds";
  }

  public Step step(String value) {
    Objects.requireNonNull(value, "batch metric step");
    for (var step : Step.values()) if (step.name().equals(value)) return step;
    throw new IllegalArgumentException("CONFIG_INVALID");
  }

  public Status status(String value) {
    Objects.requireNonNull(value, "batch metric status");
    for (var status : Status.values()) if (status.name().equals(value)) return status;
    throw new IllegalArgumentException("CONFIG_INVALID");
  }

  public Map<String, String> runLabels(Step step, Status status) {
    return Map.of(
        "step",
        Objects.requireNonNull(step, "batch step").name(),
        "status",
        Objects.requireNonNull(status, "batch status").name());
  }

  public Map<String, String> successLabels(Step step) {
    return Map.of("step", Objects.requireNonNull(step, "batch step").name());
  }

  public boolean detailedMetricsEnabled(String mode) {
    return MonitoringModePolicy.parse(mode) == MonitoringModePolicy.DEBUG;
  }
}
