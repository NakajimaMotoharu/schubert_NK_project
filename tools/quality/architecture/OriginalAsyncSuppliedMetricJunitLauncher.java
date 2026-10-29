import java.util.Map;

/** Three original Async metric suites, owned JDBC doubles/SDK and finite threads only. */
public final class OriginalAsyncSuppliedMetricJunitLauncher {
  private OriginalAsyncSuppliedMetricJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.api.monitoring.AsyncJobMetricCollectorTest", 8,
            "dev.codex.schubert.nk.api.monitoring.AsyncJobMetricRecorderTest", 8,
            "dev.codex.schubert.nk.api.monitoring.AsyncJobCountRepositoryTest", 8));
  }
}
