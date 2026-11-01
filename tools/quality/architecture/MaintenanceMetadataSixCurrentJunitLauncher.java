import java.util.Map;
/** Six plain immutable metadata contracts; no actual run, DB or filesystem operations. */
public final class MaintenanceMetadataSixCurrentJunitLauncher {
  private MaintenanceMetadataSixCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.repository.MaintenanceMetadataContractTest", 6));
  }
}
