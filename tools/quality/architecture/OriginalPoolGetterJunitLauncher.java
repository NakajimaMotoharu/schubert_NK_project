import java.util.Map;

/** Original pool getter/collector suites, own proxy interfaces and memory SDK only. */
public final class OriginalPoolGetterJunitLauncher {
  private OriginalPoolGetterJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.api.monitoring.DbPoolMetricCollectorTest", 8,
            "dev.codex.schubert.nk.api.monitoring.DbPoolMetricObservationTest", 8,
            "dev.codex.schubert.nk.web.monitoring.WebDbPoolMetricCollectorTest", 8,
            "dev.codex.schubert.nk.web.monitoring.WebDbPoolMetricObservationTest", 8));
  }
}
