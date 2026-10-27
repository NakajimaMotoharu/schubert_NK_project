package dev.codex.schubert.nk.batch.monitoring;

import java.util.EnumSet;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/**
 * Non-I/O mode contract. NK-OPS-001/P018-09; MON010..013; UI252 §5; SS351 §8;
 * PG-D517/PT-OPS-MONMODE-001..007. This policy never starts/stops services or changes log level.
 */
public enum MonitoringModePolicy {
  DEBUG(true, 15, 5_000_000_000L),
  STANDARD(false, 0, 0);

  /**
   * Only detailed monitoring components; basic health/journal/DB/disk monitoring is not included.
   */
  public enum DetailService {
    ACTUATOR,
    PROMETHEUS,
    GRAFANA,
    EXPORTERS
  }

  /** Supplied configured limits, never observed data age/usage or permission to delete. */
  public record RetentionConfiguration(int days, long bytes) {
    public RetentionConfiguration {
      if (days < 0 || bytes < 0) throw new IllegalArgumentException("CONFIG_INVALID");
    }
  }

  private static final String DRIFT_CODE = "CONFIG_DRIFT";

  private final boolean configuredDetailMetrics;
  private final int configuredRetentionDays;
  private final long configuredRetentionBytes;

  MonitoringModePolicy(boolean detailedMetricsEnabled, int retentionDays, long retentionBytes) {
    this.configuredDetailMetrics = detailedMetricsEnabled;
    this.configuredRetentionDays = retentionDays;
    this.configuredRetentionBytes = retentionBytes;
  }

  /** Strict external value; malformed values are never echoed into a diagnostic. */
  public static MonitoringModePolicy parse(String value) {
    Objects.requireNonNull(value, "monitoring mode");
    return switch (value) {
      case "DEBUG" -> DEBUG;
      case "STANDARD" -> STANDARD;
      default -> throw new IllegalArgumentException("CONFIG_INVALID");
    };
  }

  public boolean detailedMetricsEnabled() {
    return configuredDetailMetrics;
  }

  public int retentionDays() {
    return configuredRetentionDays;
  }

  /** Decimal GB, not GiB. Zero disables only detailed metric retention. */
  public long retentionBytes() {
    return configuredRetentionBytes;
  }

  /**
   * Verify a caller-provided complete observation, not target ownership or an actual mode switch.
   * Null inputs/elements violate the programming contract; absent/mismatched observations fail
   * closed.
   */
  public void verifyObserved(Map<DetailService, Boolean> observed) {
    var snapshot = Map.copyOf(Objects.requireNonNull(observed, "monitoring observation"));
    if (!snapshot.keySet().equals(EnumSet.allOf(DetailService.class)))
      throw new IllegalStateException(DRIFT_CODE);
    for (boolean enabled : snapshot.values()) {
      if (enabled != configuredDetailMetrics) throw new IllegalStateException(DRIFT_CODE);
    }
  }

  /** Complete caller observation only; missing must not become STANDARD's legitimate zero. 1700. */
  public void verifyObservedRetention(Optional<RetentionConfiguration> observed) {
    Objects.requireNonNull(observed, "retention configuration observation");
    if (observed.isEmpty()) throw new IllegalStateException(DRIFT_CODE);
    var configuration = observed.orElseThrow();
    if (configuration.days() != configuredRetentionDays
        || configuration.bytes() != configuredRetentionBytes)
      throw new IllegalStateException(DRIFT_CODE);
  }
}
