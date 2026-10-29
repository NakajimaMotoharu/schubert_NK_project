import java.util.Map;

/** Three original HTTP metric suites; own SDK/MockClock, no HTTP server or network. */
public final class OriginalHttpMetricWholeJunitLauncher {
  private OriginalHttpMetricWholeJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.monitoring.HttpMetricContractTest", 6,
        "dev.codex.schubert.nk.web.monitoring.HttpMetricRecorderTest", 10,
        "dev.codex.schubert.nk.web.monitoring.OverflowSafeHttpMeterRegistryTest", 12));
  }
}
