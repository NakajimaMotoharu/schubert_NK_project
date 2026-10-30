import java.util.Map;

/** Four whole Batch meter contract suites, supplied values and owned registries only. */
public final class OriginalBatchMeterContractsJunitLauncher {
  private OriginalBatchMeterContractsJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.monitoring.BatchMetricLabelPolicyTest", 14,
        "dev.codex.schubert.nk.batch.monitoring.BatchMetricRecorderTest", 8,
        "dev.codex.schubert.nk.batch.monitoring.IntegrityFailureMetricRecorderTest", 8,
        "dev.codex.schubert.nk.batch.monitoring.ProcessRestartMetricRecorderTest", 8));
  }
}
