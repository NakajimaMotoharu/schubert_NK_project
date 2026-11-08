import java.util.Map;

/** Original whole five cases; memory clock and own public trace only. */
public final class StubOwnerWholeLauncher {
  private StubOwnerWholeLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of("dev.codex.schubert.nk.api.application.question.StubAnswerProviderTest", 5));
  }
}
