import java.util.Map;

/** Original phase composition and own-JVM registry/GC ownership only. */
public final class OriginalApiWebStandardAssemblyJunitLauncher {
  private OriginalApiWebStandardAssemblyJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.monitoring.ApiStandardMetricsTest", 13,
        "dev.codex.schubert.nk.web.monitoring.WebStandardMetricsTest", 13));
  }
}
