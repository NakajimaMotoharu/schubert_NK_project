import java.util.Map;

/** Two original entire in-memory search display suites, no live web or data access. */
public final class OriginalScenarioSearchViewJunitLauncher {
  private OriginalScenarioSearchViewJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.view.ScenarioSearchViewModelTest", 8,
        "dev.codex.schubert.nk.web.view.ScenarioSearchResultsViewModelTest", 8));
  }
}
