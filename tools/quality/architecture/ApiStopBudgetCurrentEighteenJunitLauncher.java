import java.util.Map;

/** Whole primitive-stop-budget tests, injected finite memory clocks and own workers only. */
public final class ApiStopBudgetCurrentEighteenJunitLauncher {
  private ApiStopBudgetCurrentEighteenJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.bootstrap.ApiStopBudgetTest", 18));
  }
}
