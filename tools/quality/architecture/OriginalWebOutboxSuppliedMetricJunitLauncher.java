import java.util.Map;

/** Three original Web Outbox metric suites; owned JDBC doubles and memory SDK only. */
public final class OriginalWebOutboxSuppliedMetricJunitLauncher {
  private OriginalWebOutboxSuppliedMetricJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.web.monitoring.WebOutboxMetricCollectorTest", 8,
            "dev.codex.schubert.nk.web.monitoring.WebOutboxMetricRecorderTest", 8,
            "dev.codex.schubert.nk.web.monitoring.WebOutboxObservationRepositoryTest", 10));
  }
}
