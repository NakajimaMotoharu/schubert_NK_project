import java.util.Map;
/** Six independent DTO/catalog contracts; no admin actions, auth grants or provider calls. */
public final class AdminValuesSixCurrentJunitLauncher {
  private AdminValuesSixCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.application.admin.AdminValueCatalogContractTest", 6));
  }
}
