import java.util.Map;

/** Entire original tests with own Spring Mock Servlet values, never a live server. */
public final class OriginalMockServletSecurityJunitLauncher {
  private OriginalMockServletSecurityJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.security.WebSecurityHeaderTest", 4,
        "dev.codex.schubert.nk.web.security.ClosedServletSecurityFilterTest", 4,
        "dev.codex.schubert.nk.web.security.WebAuthorizationFilterTest", 4));
  }
}
