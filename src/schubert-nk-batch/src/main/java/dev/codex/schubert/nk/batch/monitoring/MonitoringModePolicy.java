package dev.codex.schubert.nk.batch.monitoring;

import java.util.EnumSet;
import java.util.Map;
import java.util.Objects;

/**
 * Non-I/O mode contract. NK-OPS-001/P018-09; MON010..013; UI252 §5; SS351 §8;
 * PG-D517/PT-OPS-MONMODE-001..007. This policy never starts/stops services or changes log level.
 */
public enum MonitoringModePolicy {
  DEBUG(true, 15, 5_000_000_000L),
  STANDARD(false, 0, 0);

  /** Only detailed monitoring components; basic health/journal/DB/disk monitoring is not included. */
  public enum DetailService {
    ACTUATOR,
    PROMETHEUS,
    GRAFANA,
    EXPORTERS
  }

  private final boolean detailedMetricsEnabled;
  private final int retentionDays;
  private final long retentionBytes;

  MonitoringModePolicy(boolean detailedMetricsEnabled, int retentionDays, long retentionBytes) {
    this.detailedMetricsEnabled = detailedMetricsEnabled;
    this.retentionDays = retentionDays;
    this.retentionBytes = retentionBytes;
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
    return detailedMetricsEnabled;
  }

  public int retentionDays() {
    return retentionDays;
  }

  /** Decimal GB, not GiB. Zero disables only detailed metric retention. */
  public long retentionBytes() {
    return retentionBytes;
  }

  /**
   * Verify a caller-provided complete observation, not target ownership or an actual mode switch.
   * Null inputs/elements violate the programming contract; absent/mismatched observations fail closed.
   */
  public void verifyObserved(Map<DetailService, Boolean> observed) {
    var snapshot = Map.copyOf(Objects.requireNonNull(observed, "monitoring observation"));
    if (!snapshot.keySet().equals(EnumSet.allOf(DetailService.class)))
      throw new IllegalStateException("CONFIG_DRIFT");
    for (boolean enabled : snapshot.values()) {
      if (enabled != detailedMetricsEnabled) throw new IllegalStateException("CONFIG_DRIFT");
    }
  }
}
