import java.util.Map;

/** Original pure supplied-value/state suites; no actual filesystem/heap/pool/endpoint sampling. */
public final class OriginalTimedThresholdJunitLauncher {
  private OriginalTimedThresholdJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.monitoring.TimedFilesystemMonitorTest", 6,
        "dev.codex.schubert.nk.batch.monitoring.TimedJvmHeapMonitorTest", 8,
        "dev.codex.schubert.nk.batch.monitoring.TimedDbPoolMonitorTest", 8,
        "dev.codex.schubert.nk.batch.monitoring.TimedSyncLatencyMonitorTest", 8,
        "dev.codex.schubert.nk.batch.monitoring.AlertThresholdsTest", 14));
  }
}
