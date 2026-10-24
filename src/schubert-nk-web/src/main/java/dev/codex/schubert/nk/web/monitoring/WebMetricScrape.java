package dev.codex.schubert.nk.web.monitoring;

import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;

/** NK-OPS-001/RD171/UI252/SS351/1769 SCRAPE001..014: pure borrowed-source mode policy. */
public final class WebMetricScrape {
  private final WebGaugeMetricExporter gauges = new WebGaugeMetricExporter();
  private final WebCounterMetricExporter counters = new WebCounterMetricExporter();
  private final WebDurationMetricExporter timers = new WebDurationMetricExporter();

  /** No registry, connection, process or configuration source is acquired/retained. */
  public WebMetricScrape() {}

  /**
   * STANDARD never reads the detailed source. DEBUG returns only fixed approved Web families, with
   * per-point snapshots, not a whole-scrape transaction. A later failure returns no partial success
   * and is not swallowed. The caller retains all source lifetime responsibilities.
   */
  public String scrape(MeterRegistry source, String mode) {
    Objects.requireNonNull(source, "meter registry");
    if (!new HttpMetricContract().detailedMetricsEnabled(mode)) return "";
    OverflowSafeHttpMeterRegistry.requireCompatible(source);
    return gauges.scrapeApprovedGauges(source)
        + counters.scrapeApprovedCounters(source)
        + timers.scrapeApprovedTimers(source);
  }
}
