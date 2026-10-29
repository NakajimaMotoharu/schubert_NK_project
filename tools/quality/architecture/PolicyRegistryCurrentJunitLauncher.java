import java.util.Map;

/** Original whole22 closed enum policy/status values, not actual runtime health. */
public final class PolicyRegistryCurrentJunitLauncher {
  private PolicyRegistryCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.monitoring.MonitoringPolicyEngineTest", 9,
            "dev.codex.schubert.nk.batch.monitoring.AlertRegistryTest", 4,
            "dev.codex.schubert.nk.batch.monitoring.MonitoringStatusTextTest", 6,
            "dev.codex.schubert.nk.batch.monitoring.MonitoringMissingObservationTest", 3));
  }
}
