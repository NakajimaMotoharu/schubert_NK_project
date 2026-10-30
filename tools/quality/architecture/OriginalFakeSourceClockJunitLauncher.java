import java.util.Map;

/** Eight whole suites using only caller-owned fake clock/store/bean and pure local state. */
public final class OriginalFakeSourceClockJunitLauncher {
  private OriginalFakeSourceClockJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.monitoring.MonitoringPolicyEngineTest", 9,
        "dev.codex.schubert.nk.batch.monitoring.MonitoringStatusTextTest", 6,
        "dev.codex.schubert.nk.batch.monitoring.MonitoringPollerTest", 8,
        "dev.codex.schubert.nk.batch.monitoring.MonitoringObservationClockTest", 8,
        "dev.codex.schubert.nk.batch.monitoring.FilesystemHealthObservationTest", 10,
        "dev.codex.schubert.nk.batch.monitoring.JvmHeapHealthObservationTest", 9,
        "dev.codex.schubert.nk.batch.monitoring.MonitoringMissingObservationTest", 3,
        "dev.codex.schubert.nk.batch.monitoring.AlertRegistryTest", 4));
  }
}
