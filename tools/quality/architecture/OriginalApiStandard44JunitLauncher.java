import java.util.Map;

/** Three API whole suites; own child SDK, no external process or services. */
public final class OriginalApiStandard44JunitLauncher {
  private OriginalApiStandard44JunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.monitoring.ApiGcMetricRegistrationTest", 16,
        "dev.codex.schubert.nk.api.monitoring.ApiJvmMetricsTest", 14,
        "dev.codex.schubert.nk.api.monitoring.ApiSystemMetricsTest", 14));
  }
}
