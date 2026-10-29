import java.util.Map;

/** Original whole eighteen fixed-clock API budget tests; no actual stop or hooks. */
public final class ApiStopBudgetCurrentJunitLauncher {
  private ApiStopBudgetCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of("dev.codex.schubert.nk.api.bootstrap.ApiStopBudgetTest", 18));
  }
}
