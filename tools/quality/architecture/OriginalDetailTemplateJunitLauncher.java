import java.util.Map;

/** Entire original mock MVC scenario template suite; no server or actual large-result file. */
public final class OriginalDetailTemplateJunitLauncher {
  private OriginalDetailTemplateJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.view.ScenarioDetailTemplateTest", 8));
  }
}
