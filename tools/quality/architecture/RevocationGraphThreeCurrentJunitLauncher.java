import java.util.Map;
/** Original local memory graph only; never invokes transaction/combine or actual Logout. */
public final class RevocationGraphThreeCurrentJunitLauncher {
  private RevocationGraphThreeCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.revocation.RevocationJdbcGraph328Test", 3));
  }
}
