import java.util.Map;

/** Whole Media/Scenario boundary originals only; any JDBC proxy invocation fails. */
public final class MediaScenarioPreSqlJunitLauncher {
  private MediaScenarioPreSqlJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.persistence.MediaPreSqlBoundaryTest", 13,
        "dev.codex.schubert.nk.api.persistence.ScenarioPreSqlBoundaryTest", 9));
  }
}
