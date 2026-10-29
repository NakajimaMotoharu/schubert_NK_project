import java.util.Map;

/** Original whole16 supplied transfer counts and caller-owned SDK, no actual file operations. */
public final class TransferMetricCurrentJunitLauncher {
  private TransferMetricCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.monitoring.TransferMetricRecorderTest", 8,
            "dev.codex.schubert.nk.batch.monitoring.TransferHealthMonitorTest", 8));
  }
}
