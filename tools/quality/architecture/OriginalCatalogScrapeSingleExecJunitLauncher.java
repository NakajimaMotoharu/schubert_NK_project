import java.util.Map;

/** Full existing Catalog and Scrape suites in one exec, not an exec union. */
public final class OriginalCatalogScrapeSingleExecJunitLauncher {
  private OriginalCatalogScrapeSingleExecJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.monitoring.ApiMetricCatalogTest", 14,
        "dev.codex.schubert.nk.web.monitoring.WebMetricCatalogTest", 14,
        "dev.codex.schubert.nk.api.monitoring.ApiMetricScrapeTest", 14,
        "dev.codex.schubert.nk.web.monitoring.WebMetricScrapeTest", 14));
  }
}
