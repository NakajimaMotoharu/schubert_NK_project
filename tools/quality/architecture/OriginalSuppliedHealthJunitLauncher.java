import java.util.Map;

/** Ten whole supplied-health suites; no actual source or service operations. */
public final class OriginalSuppliedHealthJunitLauncher {
  private OriginalSuppliedHealthJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.monitoring.AsyncQueueMonitorTest", 9,
        "dev.codex.schubert.nk.batch.monitoring.BackupHealthMonitorTest", 8,
        "dev.codex.schubert.nk.batch.monitoring.DlqHealthMonitorTest", 8,
        "dev.codex.schubert.nk.batch.monitoring.ExpiryBacklogMonitorTest", 8,
        "dev.codex.schubert.nk.batch.monitoring.IntegrityHealthMonitorTest", 8,
        "dev.codex.schubert.nk.batch.monitoring.JvmHeapHealthMonitorTest", 8,
        "dev.codex.schubert.nk.batch.monitoring.RestartHealthMonitorTest", 8,
        "dev.codex.schubert.nk.batch.monitoring.TransferHealthMonitorTest", 8,
        "dev.codex.schubert.nk.batch.monitoring.WebLogBacklogMonitorTest", 8,
        "dev.codex.schubert.nk.batch.monitoring.TransferMetricRecorderTest", 8));
  }
}
