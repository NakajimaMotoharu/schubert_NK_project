import java.util.Map;

/** Whole original clock-only18; no actual stop or external resources. */
public final class OriginalApiStopBudgetJunitLauncher {
  private OriginalApiStopBudgetJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.bootstrap.ApiStopBudgetTest", 18));
  }
}
