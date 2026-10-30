import java.util.Map;

/** Whole original value binding tests; helper JUnit methods and keyring paths are not selected. */
public final class RequestBindingsCurrentJunitLauncher {
  private RequestBindingsCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of(
            "dev.codex.schubert.nk.api.application.media.MediaRequestDescriptorBindingTest", 4,
            "dev.codex.schubert.nk.api.application.scenario.ScenarioScriptFileBindingTest", 2,
            "dev.codex.schubert.nk.api.application.question.QuestionQueryResponseBindingTest", 4));
  }
}
