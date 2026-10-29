import java.util.Map;

/** Whole21 pure metric/mode/retention value tests, never actual service/retention control. */
public final class MetricModeCurrentJunitLauncher {
  private MetricModeCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.monitoring.MetricContractTest", 6,
            "dev.codex.schubert.nk.batch.monitoring.MonitoringModePolicyTest", 7,
            "dev.codex.schubert.nk.batch.monitoring.MonitoringRetentionConfigurationTest", 8));
  }
}
