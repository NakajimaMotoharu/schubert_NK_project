import java.util.Map;

/** Two new API exporter Sources: original48 plus required same-exec approved-branch14. */
public final class OriginalApiExporterJointJunitLauncher {
  private OriginalApiExporterJointJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.monitoring.ApiScalarMetricExporterTest", 24,
        "dev.codex.schubert.nk.api.monitoring.ApiDurationMetricExporterTest", 24,
        "dev.codex.schubert.nk.api.monitoring.ApiMetricScrapeTest", 14));
  }
}
