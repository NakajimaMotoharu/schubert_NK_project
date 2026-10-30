import java.util.Map;

/** Whole synthetic Logs DOM/resource test only, no real log backend or endpoint. */
public final class OriginalLogSearchTemplateJunitLauncher {
  private OriginalLogSearchTemplateJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.view.LogSearchTemplateTest", 8));
  }
}
