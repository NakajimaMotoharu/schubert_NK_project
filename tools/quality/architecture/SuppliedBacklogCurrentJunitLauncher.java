import java.util.Map;

/** Original whole33 supplied backlog and Backup health, not actual operations. */
public final class SuppliedBacklogCurrentJunitLauncher {
  private SuppliedBacklogCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.monitoring.AsyncQueueMonitorTest", 9,
            "dev.codex.schubert.nk.batch.monitoring.WebLogBacklogMonitorTest", 8,
            "dev.codex.schubert.nk.batch.monitoring.ExpiryBacklogMonitorTest", 8,
            "dev.codex.schubert.nk.batch.monitoring.BackupHealthMonitorTest", 8));
  }
}
