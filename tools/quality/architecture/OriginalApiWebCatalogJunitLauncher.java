import java.util.Map;

/** Original API/Web catalog pair; pure tag/label fixtures and bounded owned threads. */
public final class OriginalApiWebCatalogJunitLauncher {
  private OriginalApiWebCatalogJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.monitoring.ApiMetricCatalogTest", 14,
        "dev.codex.schubert.nk.web.monitoring.WebMetricCatalogTest", 14));
  }
}
