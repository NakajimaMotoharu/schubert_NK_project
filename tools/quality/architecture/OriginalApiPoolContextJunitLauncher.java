import java.util.Map;

/** Three whole API pool/context suites; fake borrowed getters and owned child SDK only. */
public final class OriginalApiPoolContextJunitLauncher {
  private OriginalApiPoolContextJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.monitoring.DbPoolMetricRecorderTest", 8,
        "dev.codex.schubert.nk.api.monitoring.ApiDbPoolMetricBindingTest", 15,
        "dev.codex.schubert.nk.api.monitoring.ApiMetricContextTest", 33));
  }
}
