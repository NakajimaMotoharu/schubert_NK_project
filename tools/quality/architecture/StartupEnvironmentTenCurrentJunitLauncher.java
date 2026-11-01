import java.util.Map;
/** Two independent Map guards and necessary original eight; no native or service startup. */
public final class StartupEnvironmentTenCurrentJunitLauncher {
  private StartupEnvironmentTenCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.bootstrap.ApiStartupInputsTest", 4,
        "dev.codex.schubert.nk.web.bootstrap.WebStartupInputsTest", 4,
        "dev.codex.schubert.nk.api.bootstrap.ApiEnvironmentGateContractTest", 1,
        "dev.codex.schubert.nk.web.bootstrap.WebEnvironmentGateContractTest", 1));
  }
}
