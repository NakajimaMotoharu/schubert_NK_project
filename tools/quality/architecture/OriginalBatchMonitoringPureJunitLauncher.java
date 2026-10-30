import java.util.Map;

/** Eight whole pure policy/value suites; no real monitoring source, process or service operations. */
public final class OriginalBatchMonitoringPureJunitLauncher {
  private OriginalBatchMonitoringPureJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.monitoring.AlertLifecycleTest", 12,
        "dev.codex.schubert.nk.batch.monitoring.ContinuousConditionWindowTest", 8,
        "dev.codex.schubert.nk.batch.monitoring.MetricContractTest", 6,
        "dev.codex.schubert.nk.batch.monitoring.BatchMetricContractTest", 5,
        "dev.codex.schubert.nk.batch.monitoring.MonitoringModePolicyTest", 7,
        "dev.codex.schubert.nk.batch.monitoring.GeneratedBatchValueContractTest", 7,
        "dev.codex.schubert.nk.batch.monitoring.AlertContinuityTest", 2,
        "dev.codex.schubert.nk.batch.monitoring.MonitoringRetentionConfigurationTest", 8));
  }
}
