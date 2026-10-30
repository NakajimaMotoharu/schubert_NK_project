import java.util.Map;

/** Original API metric handler whole23 with memory exchanges; no server/socket operation. */
public final class OriginalApiMetricHttpJunitLauncher {
  private OriginalApiMetricHttpJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.monitoring.ApiMetricHttpHandlerTest", 23));
  }
}
