import java.util.Map;
/** Whole original literal catalogs only; never invokes outer Unit or SQL operations. */
public final class BatchEnumCatalogTwoCurrentJunitLauncher {
  private BatchEnumCatalogTwoCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
      "dev.codex.schubert.nk.batch.repository.EnumValueCatalogCompatibilityTest",1,
      "dev.codex.schubert.nk.batch.platform.EnumValueCatalogCompatibilityTest",1));
  }
}

