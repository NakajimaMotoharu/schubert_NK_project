import java.util.Map;
/** Original configuration-map values only, no configuration-file or database access. */
public final class InspectorConfigFourCurrentJunitLauncher {
  private InspectorConfigFourCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.maintenance.InspectorLaunchConfigurationTest", 4));
  }
}
