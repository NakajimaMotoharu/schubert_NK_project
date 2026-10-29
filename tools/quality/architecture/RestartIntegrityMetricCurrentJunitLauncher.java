import java.util.Map;

/** Original whole16 supplied event counters and owned SDK, not process/probe/control. */
public final class RestartIntegrityMetricCurrentJunitLauncher {
  private RestartIntegrityMetricCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.monitoring.ProcessRestartMetricRecorderTest", 8,
            "dev.codex.schubert.nk.batch.monitoring.IntegrityFailureMetricRecorderTest", 8));
  }
}
