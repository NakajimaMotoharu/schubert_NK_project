import java.util.Map;

/** Original whole32 with supplied ticks/UTC and fixed FileStore, no actual filesystem. */
public final class ClockFilesystemCurrentJunitLauncher {
  private ClockFilesystemCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.monitoring.MonitoringObservationClockTest", 8,
            "dev.codex.schubert.nk.batch.monitoring.FilesystemHealthObservationTest", 10,
            "dev.codex.schubert.nk.batch.monitoring.TimedFilesystemMonitorTest", 6,
            "dev.codex.schubert.nk.batch.monitoring.MonitoringPollerTest", 8));
  }
}
