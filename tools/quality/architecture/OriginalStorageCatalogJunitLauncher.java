import java.util.Map;

/** Original fixed identifier catalog suites; no secret IO, config factory or external service. */
public final class OriginalStorageCatalogJunitLauncher {
  private OriginalStorageCatalogJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.storage.ServiceCredentialIdTest", 4,
        "dev.codex.schubert.nk.storage.EnumValueCatalogCompatibilityTest", 1));
  }
}
