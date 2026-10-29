import java.util.Map;

/** Public claims value tests only; no approval issuance, signature or authority. */
public final class ReleaseApprovalValueCurrentJunitLauncher {
  private ReleaseApprovalValueCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of("dev.codex.schubert.nk.bootstrap.ReleaseApprovalTest", 8));
  }
}
