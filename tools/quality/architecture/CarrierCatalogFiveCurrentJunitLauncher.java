import java.util.Map;
public final class CarrierCatalogFiveCurrentJunitLauncher {
  private CarrierCatalogFiveCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.application.scenario.ScenarioCarrierSuccessContractTest", 2,
        "dev.codex.schubert.nk.api.logging.ProjectionFailureValueContractTest", 1,
        "dev.codex.schubert.nk.api.maintenance.InboxFailureValueContractTest", 1,
        "dev.codex.schubert.nk.web.config.CompositeMvcDeclarationContractTest", 1));
  }
}
