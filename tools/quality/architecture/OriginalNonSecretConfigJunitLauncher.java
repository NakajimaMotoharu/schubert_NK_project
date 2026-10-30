import java.util.Map;

/** Two original whole non-secret parser suites; public frozen templates only, no runtime admission. */
public final class OriginalNonSecretConfigJunitLauncher {
  private OriginalNonSecretConfigJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigTest", 7,
        "dev.codex.schubert.nk.web.bootstrap.WebNonSecretConfigTest", 7));
  }
}
