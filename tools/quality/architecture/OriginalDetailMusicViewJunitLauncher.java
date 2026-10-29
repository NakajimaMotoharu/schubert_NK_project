import java.util.Map;

/** Whole original detail and music display suites, metadata only; no real file or live web. */
public final class OriginalDetailMusicViewJunitLauncher {
  private OriginalDetailMusicViewJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.view.ScenarioDetailViewModelTest", 12,
        "dev.codex.schubert.nk.web.view.MusicHierarchyViewModelTest", 8));
  }
}
