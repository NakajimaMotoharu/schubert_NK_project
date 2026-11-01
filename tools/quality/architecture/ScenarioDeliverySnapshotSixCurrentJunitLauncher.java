import java.util.Map;
/** Whole original six memory/typed wire cases; no real publisher, database or native services. */
public final class ScenarioDeliverySnapshotSixCurrentJunitLauncher {
  private ScenarioDeliverySnapshotSixCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.application.scenario.ScenarioDetailDeliveryTest", 3,
        "dev.codex.schubert.nk.api.persistence.ScenarioDetailSnapshotBoundaryTest", 3));
  }
}
