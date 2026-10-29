import java.util.Map;

/** Original API/Web scrape policy; owned registry/MockClock and finite callbacks only. */
public final class OriginalApiWebScrapeJunitLauncher {
  private OriginalApiWebScrapeJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.monitoring.ApiMetricScrapeTest", 14,
        "dev.codex.schubert.nk.web.monitoring.WebMetricScrapeTest", 14));
  }
}
