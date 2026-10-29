import java.util.Map;

/** Three entire original plain API suites: no receiver, DB fixture or fingerprint operation. */
public final class OriginalApiPlainJunitLauncher {
  private OriginalApiPlainJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.application.admin.UserQueryCanonicalCoreTest", 4,
        "dev.codex.schubert.nk.api.application.admin.UserQueryResponseBoundaryTest", 4,
        "dev.codex.schubert.nk.api.application.log.LogPlainContractTest", 8));
  }
}
