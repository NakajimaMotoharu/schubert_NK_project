import java.util.Map;

/** Original valid public-interface SQL contracts plus whole plain contracts, one exec. */
public final class OriginalUserLogSqlJointJunitLauncher {
  private OriginalUserLogSqlJointJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.application.admin.UserQueryCanonicalCoreTest", 4,
        "dev.codex.schubert.nk.api.application.admin.UserQueryResponseBoundaryTest", 4,
        "dev.codex.schubert.nk.api.application.log.LogPlainContractTest", 8,
        "dev.codex.schubert.nk.api.application.admin.UserQuerySqlContractTest", 9,
        "dev.codex.schubert.nk.api.application.log.LogSqlContractTest", 9));
  }
}
