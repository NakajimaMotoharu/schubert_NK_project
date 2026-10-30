import java.util.Map;

/** Three whole Web pool/context suites; fake borrowed getters and owned child SDK only. */
public final class OriginalWebPoolContextJunitLauncher {
  private OriginalWebPoolContextJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.monitoring.WebDbPoolMetricRecorderTest", 8,
        "dev.codex.schubert.nk.web.monitoring.WebDbPoolMetricBindingTest", 15,
        "dev.codex.schubert.nk.web.monitoring.WebMetricContextTest", 33));
  }
}
