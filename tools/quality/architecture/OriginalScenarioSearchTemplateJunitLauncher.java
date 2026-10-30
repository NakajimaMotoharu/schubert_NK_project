import java.util.Map;

/** Whole synthetic Search template/resource test; media URLs are DOM strings only. */
public final class OriginalScenarioSearchTemplateJunitLauncher {
  private OriginalScenarioSearchTemplateJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.view.ScenarioSearchTemplateTest", 8));
  }
}
