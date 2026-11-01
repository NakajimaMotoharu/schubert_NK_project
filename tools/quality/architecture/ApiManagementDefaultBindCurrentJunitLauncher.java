import java.util.Map;
/** SS342 / PT-API-MGMT-NORM-001: original own fixed loopback, no business/native start. */
public final class ApiManagementDefaultBindCurrentJunitLauncher {
  private ApiManagementDefaultBindCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.bootstrap.ApiManagementDefaultBindTest", 1));
  }
}
