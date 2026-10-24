package dev.codex.schubert.nk.api.monitoring;

import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;

/** NK-OPS-001/RD171/UI252/SS351/1773 APIPOL: pure borrowed-source mode policy, no endpoint. */
public final class ApiMetricScrape {
  private final ApiScalarMetricExporter scalars = new ApiScalarMetricExporter();
  private final ApiDurationMetricExporter durations = new ApiDurationMetricExporter();

  public ApiMetricScrape() {}

  /** STD reads no detailed provider; DEBUG is not a whole-scrape transaction or resource owner. */
  public String scrape(MeterRegistry source, String mode) {
    Objects.requireNonNull(source, "meter registry");
    Objects.requireNonNull(mode, "monitoring mode");
    if ("STANDARD".equals(mode)) return "";
    if (!"DEBUG".equals(mode)) throw new IllegalArgumentException("CONFIG_INVALID");
    ExactDurationMeterRegistry.requireCompatible(source);
    return scalars.scrapeApprovedGauges(source)
        + scalars.scrapeApprovedCounters(source)
        + durations.scrapeApproved(source);
  }
}
