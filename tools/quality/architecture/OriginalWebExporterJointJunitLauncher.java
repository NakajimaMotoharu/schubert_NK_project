import java.util.Map;

/** Three original exporter suites plus necessary whole approved-scrape dependency, no actual endpoint. */
public final class OriginalWebExporterJointJunitLauncher {
  private OriginalWebExporterJointJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.monitoring.WebCounterMetricExporterTest", 16,
        "dev.codex.schubert.nk.web.monitoring.WebGaugeMetricExporterTest", 16,
        "dev.codex.schubert.nk.web.monitoring.WebDurationMetricExporterTest", 16,
        "dev.codex.schubert.nk.web.monitoring.WebMetricScrapeTest", 14));
  }
}
