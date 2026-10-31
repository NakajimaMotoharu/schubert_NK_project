import java.util.Map;

/** Whole original generated-value contracts, no registry, DB, exporter or HTTP operations. */
public final class GeneratedMetricValueTwelveJunitLauncher {
  private GeneratedMetricValueTwelveJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.monitoring.GeneratedMetricValueContractTest", 8,
        "dev.codex.schubert.nk.web.monitoring.GeneratedWebValueContractTest", 4));
  }
}
