import java.util.Map;

/** Original standard SDK owners; exclusively new own-JVM resources, no external recovery. */
public final class OriginalApiWebStandardSourceJunitLauncher {
  private OriginalApiWebStandardSourceJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.monitoring.ApiStandardMetricSourceTest", 16,
        "dev.codex.schubert.nk.web.monitoring.WebStandardMetricSourceTest", 16));
  }
}
