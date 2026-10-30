import java.util.Map;

/** Original whole suites18; only own public test evidence files, no real DB/native/resources. */
public final class PublicValueCurrentJunitLauncher {
  private PublicValueCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
            "dev.codex.schubert.nk.api.maintenance.InspectorSettingsTest", 3,
            "dev.codex.schubert.nk.api.logging.RequestLogDetailsTest", 2,
            "dev.codex.schubert.nk.api.application.question.QuestionReceiptIdTest", 8,
            "dev.codex.schubert.nk.api.application.question.StubAnswerProviderTest", 5));
  }
}
