import java.util.Map;

/** Original whole17 getter-only synthetic heap observation, no actual management. */
public final class HeapObservationCurrentJunitLauncher {
  private HeapObservationCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.monitoring.JvmHeapHealthObservationTest", 9,
            "dev.codex.schubert.nk.batch.monitoring.JvmHeapHealthMonitorTest", 8));
  }
}
