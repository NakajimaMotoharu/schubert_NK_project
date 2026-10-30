import java.util.Map;

/** Entire valid public-interface Question/Notification SQL and original plain contracts. */
public final class OriginalQuestionSqlJointJunitLauncher {
  private OriginalQuestionSqlJointJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.application.question.QuestionQueryPlainContractTest", 8,
        "dev.codex.schubert.nk.api.application.question.QuestionSqlContractTest", 10));
  }
}
