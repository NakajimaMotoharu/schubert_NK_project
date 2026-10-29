import java.util.Map;

/** Original whole24 supplied logical keys; never actual protected-resource or service operations. */
public final class SuppliedProtectedHealthCurrentJunitLauncher {
  private SuppliedProtectedHealthCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.monitoring.DlqHealthMonitorTest", 8,
            "dev.codex.schubert.nk.batch.monitoring.IntegrityHealthMonitorTest", 8,
            "dev.codex.schubert.nk.batch.monitoring.RestartHealthMonitorTest", 8));
  }
}
