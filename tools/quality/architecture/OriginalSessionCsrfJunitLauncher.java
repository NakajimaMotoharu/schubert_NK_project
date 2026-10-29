import java.util.Map;

/** Entire original synthetic sessionID and CSRF suites; no deployed session data. */
public final class OriginalSessionCsrfJunitLauncher {
  private OriginalSessionCsrfJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.session.WebSessionIdTest", 4,
        "dev.codex.schubert.nk.web.security.WebCsrfTokenTest", 4));
  }
}
