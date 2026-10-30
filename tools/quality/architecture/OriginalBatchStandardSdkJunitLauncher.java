import java.util.Map;

/** Six whole Batch standard SDK suites, owned child JVM and explicit GC handle lifetime only. */
public final class OriginalBatchStandardSdkJunitLauncher {
  private OriginalBatchStandardSdkJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.monitoring.BatchMetricTextTest", 37,
        "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricSourceTest", 16,
        "dev.codex.schubert.nk.batch.monitoring.BatchJvmMetricsTest", 14,
        "dev.codex.schubert.nk.batch.monitoring.BatchSystemMetricsTest", 14,
        "dev.codex.schubert.nk.batch.monitoring.BatchGcMetricRegistrationTest", 16,
        "dev.codex.schubert.nk.batch.monitoring.BatchStandardMetricsTest", 13));
  }
}
