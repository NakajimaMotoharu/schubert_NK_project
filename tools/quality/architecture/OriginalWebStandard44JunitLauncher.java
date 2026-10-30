import java.util.Map;

/** Three original whole Web GC/JVM/System suites; own child SDK only. */
public final class OriginalWebStandard44JunitLauncher {
  private OriginalWebStandard44JunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.monitoring.WebGcMetricRegistrationTest", 16,
        "dev.codex.schubert.nk.web.monitoring.WebJvmMetricsTest", 14,
        "dev.codex.schubert.nk.web.monitoring.WebSystemMetricsTest", 14));
  }
}
