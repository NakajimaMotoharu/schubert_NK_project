import java.util.Map;

/** Whole original seven public-synthetic-key tests; no real authentication or external services. */
public final class AuthContextCodecCurrentJunitLauncher {
  private AuthContextCodecCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of("dev.codex.schubert.nk.api.security.AuthContextCodecTest", 7));
  }
}
