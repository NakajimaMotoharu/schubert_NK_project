package dev.codex.schubert.nk.api.monitoring;

import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;
import java.util.function.Supplier;

/**
 * NK-OPS-001/RD171/UI252/SS351/1800 APIPAY: pure legacy-ready plus approved custom text, no
 * HTTP/health authority.
 */
public final class ApiCustomMetricPayload {
  private static final String STANDARD_MODE = "STANDARD";
  private static final String READY_PREFIX =
      "# TYPE schubert_nk_api_ready gauge\nschubert_nk_api_ready ";

  public ApiCustomMetricPayload() {}

  /** SS351/1812/PG-D616: pure full view; both sources remain caller-owned, no HTTP authority. */
  public String render(
      boolean ready,
      String mode,
      Supplier<? extends MeterRegistry> source,
      ApiStandardMetricSource standard) {
    Objects.requireNonNull(standard, "standard metric owner");
    if (STANDARD_MODE.equals(mode)) return render(ready, mode, source);
    return render(ready, mode, source)
        + Objects.requireNonNull(standard.scrape(mode), "standard metric text");
  }

  /** Supplied ready state is not recomputed. Source is borrowed, not acquired or closed here. */
  public String render(boolean ready, String mode, Supplier<? extends MeterRegistry> source) {
    Objects.requireNonNull(source, "metric source supplier");
    boolean detailed =
        switch (Objects.requireNonNull(mode, "monitoring mode")) {
          case "DEBUG" -> true;
          case "STANDARD" -> false;
          default -> throw new IllegalArgumentException("CONFIG_INVALID");
        };
    String prefix = READY_PREFIX + (ready ? "1\n" : "0\n");
    if (!detailed) return prefix;
    return prefix
        + new ApiMetricScrape()
            .scrape(Objects.requireNonNull(source.get(), "borrowed metric source"), mode);
  }
}
