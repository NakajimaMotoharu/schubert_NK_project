import java.util.Map;

/** Original callback ownership suites, no real storage port or resource factory. */
public final class OriginalStorageResourceJunitLauncher {
  private OriginalStorageResourceJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.storage.ResourceScopeTest", 8,
        "dev.codex.schubert.nk.storage.FactoryResourceScopeTest", 18));
  }
}
