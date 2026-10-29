import java.util.Map;

/** Exactly three original value-form suites, no HTTP/server/session or graph classifier. */
public final class OriginalWebThreeFormsJunitLauncher {
  private OriginalWebThreeFormsJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.web.form.ScenarioSearchFormTest", 8,
            "dev.codex.schubert.nk.web.form.LogSearchFormTest", 8,
            "dev.codex.schubert.nk.web.form.QuestionSubmitFormTest", 8));
  }
}
