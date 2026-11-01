import java.util.Map;
/** Whole original Web own loopback management and deadline tests; never a live Unit admission. */
public final class WebManagementThirteenCurrentJunitLauncher {
  private WebManagementThirteenCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.bootstrap.WebManagementServerTest", 10,
        "dev.codex.schubert.nk.web.bootstrap.WebManagementDeadlineTest", 3));
  }
}
