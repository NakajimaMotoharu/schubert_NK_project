import java.util.Map;

/** Whole original borrowed typed observation20; no actual JDBC driver or database. */
public final class OriginalApiOutboxSourceJunitLauncher {
  private OriginalApiOutboxSourceJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.monitoring.ApiOutboxObservationSourceTest", 20));
  }
}
