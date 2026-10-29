import java.util.Map;

/** Four original API Outbox suites; own JDBC doubles/SDK/finite threads only. */
public final class OriginalApiOutboxSuppliedMetricJunitLauncher {
  private OriginalApiOutboxSuppliedMetricJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.monitoring.OutboxMetricCollectorTest", 8,
        "dev.codex.schubert.nk.api.monitoring.OutboxObservationRepositoryTest", 10,
        "dev.codex.schubert.nk.api.monitoring.OutboxRowsMetricRecorderTest", 8,
        "dev.codex.schubert.nk.api.monitoring.OutboxAgeMetricRecorderTest", 8));
  }
}
