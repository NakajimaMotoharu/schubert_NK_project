import java.util.Map;
/** Four original independent module-local graph suites, no held classifier or database. */
public final class SessionAuthGraphEightCurrentJunitLauncher {
  private SessionAuthGraphEightCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.session.SessionFailureGraphTest", 1,
        "dev.codex.schubert.nk.web.session.SessionJdbcGraph328Test", 3,
        "dev.codex.schubert.nk.api.security.AuthenticationFailureGraphTest", 1,
        "dev.codex.schubert.nk.api.security.AuthenticationJdbcGraph328Test", 3));
  }
}
