import java.util.Map;

/** Entire original synthetic Page and Scenario hierarchy presentation suites. */
public final class OriginalPageHierarchyJunitLauncher {
  private OriginalPageHierarchyJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.view.PageViewModelTest", 8,
        "dev.codex.schubert.nk.web.view.ScenarioHierarchyViewModelTest", 12));
  }
}
