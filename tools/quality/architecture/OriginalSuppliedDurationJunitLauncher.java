import java.util.Map;

/** Four original duration suites; own SDK/finite callbacks, no real business DB/JMS source. */
public final class OriginalSuppliedDurationJunitLauncher {
  private OriginalSuppliedDurationJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.monitoring.MqProcessingDurationMetricRecorderTest", 9,
        "dev.codex.schubert.nk.api.monitoring.DbQueryDurationMetricRecorderTest", 9,
        "dev.codex.schubert.nk.api.monitoring.DbQueryDurationMetricCollectorTest", 8,
        "dev.codex.schubert.nk.api.monitoring.ExactDurationMeterRegistryTest", 10));
  }
}
