import java.util.Map;

/** Five original whole Web standard suites; own child SDK only, no external actions. */
public final class OriginalWebStandardJunitLauncher {
  private OriginalWebStandardJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.monitoring.WebGcMetricRegistrationTest", 16,
        "dev.codex.schubert.nk.web.monitoring.WebJvmMetricsTest", 14,
        "dev.codex.schubert.nk.web.monitoring.WebSystemMetricsTest", 14,
        "dev.codex.schubert.nk.web.monitoring.WebStandardMetricSourceTest", 16,
        "dev.codex.schubert.nk.web.monitoring.WebStandardMetricsTest", 13));
  }
}
