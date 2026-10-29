import java.util.Map;

/** Original payload suites; exclusively new own JVM SDK/metrics/GC handles, never external runtime. */
public final class OriginalApiWebPayloadJunitLauncher {
  private OriginalApiWebPayloadJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.monitoring.ApiCustomMetricPayloadTest", 26,
        "dev.codex.schubert.nk.web.monitoring.WebCustomMetricPayloadTest", 26));
  }
}
