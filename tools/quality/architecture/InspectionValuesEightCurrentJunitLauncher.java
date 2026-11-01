import java.util.Map;
/** Eight independent immutable inspection values; no executor or database. */
public final class InspectionValuesEightCurrentJunitLauncher {
  private InspectionValuesEightCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.maintenance.InspectionValueContractTest", 8));
  }
}
