import java.util.Map;
/** Pure DTO/catalog tests with public synthetic values, not authentication/session issuance. */
public final class AuthValuesTwelveCurrentJunitLauncher {
  private AuthValuesTwelveCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.security.AuthImmutableValueContractTest", 12));
  }
}
