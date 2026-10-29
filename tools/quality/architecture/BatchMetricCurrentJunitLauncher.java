import java.util.Map;

/** Original whole contract5 and recorder8 with owned in-memory SDK, no exporter. */
public final class BatchMetricCurrentJunitLauncher {
  private BatchMetricCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricContractTest", 5,
            "dev.codex.schubert.nk.batch.monitoring.BatchMetricRecorderTest", 8));
  }
}
