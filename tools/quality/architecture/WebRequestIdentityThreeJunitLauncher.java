import java.util.Map;

/** Whole original Mock request-identity contracts, no real HTTP/session/credential operation. */
public final class WebRequestIdentityThreeJunitLauncher {
  private WebRequestIdentityThreeJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.security.WebRequestIdentityConsistencyTest", 3));
  }
}
