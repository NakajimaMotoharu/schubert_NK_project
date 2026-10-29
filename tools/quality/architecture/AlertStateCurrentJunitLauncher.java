import java.util.Map;

/** Original whole36 pure alert/window state tests, no actual observation/control. */
public final class AlertStateCurrentJunitLauncher {
  private AlertStateCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.monitoring.AlertThresholdsTest", 14,
            "dev.codex.schubert.nk.batch.monitoring.AlertLifecycleTest", 12,
            "dev.codex.schubert.nk.batch.monitoring.ContinuousConditionWindowTest", 8,
            "dev.codex.schubert.nk.batch.monitoring.AlertContinuityTest", 2));
  }
}
