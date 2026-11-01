import java.util.Map;
/** Five fixed query catalog contracts, no repository/query execution. */
public final class QueryCatalogFiveCurrentJunitLauncher {
  private QueryCatalogFiveCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.persistence.QueryCatalogContractTest", 5));
  }
}
