import java.util.Map;

/** Entire original log display suites with synthetic records only, no actual log access. */
public final class OriginalLogSearchViewJunitLauncher {
  private OriginalLogSearchViewJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.view.LogSearchViewModelTest", 8,
        "dev.codex.schubert.nk.web.view.LogSearchResultsViewModelTest", 8));
  }
}
