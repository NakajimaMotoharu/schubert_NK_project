import java.util.Map;
public final class CarrierCatalogFiveV2CurrentJunitLauncher {
  private CarrierCatalogFiveV2CurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.application.scenario.ScenarioCarrierSuccessContractTest", 2,
        "dev.codex.schubert.nk.api.logging.ProjectionFailureValueContractTest", 1,
        "dev.codex.schubert.nk.api.maintenance.InboxFailureValueContractTest", 1,
        "dev.codex.schubert.nk.web.config.CompositeMvcBeanDeclarationContractTestV2", 1));
  }
}
