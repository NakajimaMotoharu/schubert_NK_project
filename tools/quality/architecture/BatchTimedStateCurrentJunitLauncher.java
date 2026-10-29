import java.util.Map;

/** Three original whole supplied-value monitor suites, no real observation/control. */
public final class BatchTimedStateCurrentJunitLauncher {
  private BatchTimedStateCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.monitoring.TimedDbPoolMonitorTest", 8,
            "dev.codex.schubert.nk.batch.monitoring.TimedJvmHeapMonitorTest", 8,
            "dev.codex.schubert.nk.batch.monitoring.TimedSyncLatencyMonitorTest", 8));
  }
}
