import java.util.Map;
/** Original deployment wrapper tests with self-owned script tools and a rejected unadmitted CLI. */
public final class InspectorDeploymentEightCurrentJunitLauncher {
  private InspectorDeploymentEightCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.maintenance.InspectorDeploymentTest", 8));
  }
}
