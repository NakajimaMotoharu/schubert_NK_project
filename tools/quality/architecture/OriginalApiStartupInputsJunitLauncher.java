import java.util.Map;

/** Whole original four input-composition tests; supplied in-memory source and synthetic environment. */
public final class OriginalApiStartupInputsJunitLauncher {
  private OriginalApiStartupInputsJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.bootstrap.ApiStartupInputsTest", 4));
  }
}
