import java.util.Map;
/** Six independent memory Servlet boundaries, not actual Caddy/HTTP/session acceptance. */
public final class CaddyAddressBoundarySixCurrentJunitLauncher {
  private CaddyAddressBoundarySixCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.security.CaddyAddressBoundaryContractTest", 6));
  }
}
