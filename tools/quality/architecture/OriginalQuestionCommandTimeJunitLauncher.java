import java.util.Map;

/** Whole original three pure UTC boundary tests; no service/DB helper. */
public final class OriginalQuestionCommandTimeJunitLauncher {
  private OriginalQuestionCommandTimeJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.application.question.QuestionCommandTimeBoundaryTest", 3));
  }
}
