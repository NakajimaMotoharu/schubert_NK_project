import java.util.Map;

/** Whole original static data-only config8/readiness3; never Main/run/native. */
public final class OriginalApiConfigReadinessJunitLauncher {
  private OriginalApiConfigReadinessJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.bootstrap.ApiAdmittedConfigurationTest", 8,
        "dev.codex.schubert.nk.api.bootstrap.ApiReadinessPredicateTest", 3));
  }
}
