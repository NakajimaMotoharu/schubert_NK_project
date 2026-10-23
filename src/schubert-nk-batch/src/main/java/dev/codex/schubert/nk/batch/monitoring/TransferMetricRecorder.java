package dev.codex.schubert.nk.batch.monitoring;

import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;

/**
 * Supplied immutable transfer counts, not secure-walk/owner or cleanup authority.
 * RD171/UI252/SS341351; PG-D537/TRANSFERMET001..008/spec1615.
 */
public final class TransferMetricRecorder {
  public record Counts(long files, long bytes) {
    public Counts {
      if (files < 0 || bytes < 0)
        throw new IllegalArgumentException("invalid transfer metric counts");
    }
  }

  public static final class Usage {
    private final Counts part;
    private final Counts ready;
    private final long files;
    private final long bytes;

    public Usage(Counts part, Counts ready) {
      this.part = Objects.requireNonNull(part, "part counts");
      this.ready = Objects.requireNonNull(ready, "ready counts");
      files = Math.addExact(part.files(), ready.files());
      bytes = Math.addExact(part.bytes(), ready.bytes());
    }

    public Counts part() {
      return part;
    }

    public Counts ready() {
      return ready;
    }

    public long totalFiles() {
      return files;
    }

    public long totalBytes() {
      return bytes;
    }
  }

  public enum Suffix {
    PART(".part"),
    READY(".ready");
    private final String label;

    Suffix(String label) {
      this.label = label;
    }

    public String label() {
      return label;
    }
  }

  private final boolean collectDetailed;
  private final AtomicReference<Optional<Usage>> observed = new AtomicReference<>(Optional.empty());

  /** Registry lifetime remains with the caller even after a partial registration failure. */
  public TransferMetricRecorder(MeterRegistry registry, String mode) {
    Objects.requireNonNull(registry, "meter registry");
    collectDetailed = MonitoringModePolicy.parse(mode) == MonitoringModePolicy.DEBUG;
    if (collectDetailed) {
      for (var suffix : Suffix.values()) {
        Gauge.builder(
                MetricContract.FILE_TRANSFER_FILES.externalName(),
                observed,
                state -> value(state, suffix, false))
            .tag("suffix", suffix.label())
            .register(registry);
        Gauge.builder(
                MetricContract.FILE_TRANSFER_BYTES.externalName(),
                observed,
                state -> value(state, suffix, true))
            .tag("suffix", suffix.label())
            .register(registry);
      }
    }
  }

  /** Last caller observation wins; separate gauge scrapes are not a multi-meter transaction. */
  public void record(Usage usage) {
    Objects.requireNonNull(usage, "transfer usage");
    if (collectDetailed) observed.set(Optional.of(usage));
  }

  /** Explicit missing observation, never zero files/bytes. */
  public void missing() {
    observed.set(Optional.empty());
  }

  public Optional<Usage> snapshot() {
    return observed.get();
  }

  public boolean detailedMetricsRequested() {
    return collectDetailed;
  }

  private static double value(
      AtomicReference<Optional<Usage>> state, Suffix suffix, boolean bytes) {
    return state
        .get()
        .map(
            usage -> {
              Counts counts = suffix == Suffix.PART ? usage.part() : usage.ready();
              return bytes ? (double) counts.bytes() : (double) counts.files();
            })
        .orElse(Double.NaN);
  }
}
