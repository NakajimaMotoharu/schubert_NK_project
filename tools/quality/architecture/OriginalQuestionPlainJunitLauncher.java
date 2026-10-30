import java.util.Map;

/** Entire original plain question/notification contracts; no actual backend or key operation. */
public final class OriginalQuestionPlainJunitLauncher {
  private OriginalQuestionPlainJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.application.question.QuestionQueryPlainContractTest", 8));
  }
}
