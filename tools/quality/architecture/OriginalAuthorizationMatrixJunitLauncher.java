import java.util.Map;

/** Whole original two policy matrix tests; synthetic identities, no authentication/DB/Graph. */
public final class OriginalAuthorizationMatrixJunitLauncher {
  private OriginalAuthorizationMatrixJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.security.AuthorizationServiceTest", 2));
  }
}
