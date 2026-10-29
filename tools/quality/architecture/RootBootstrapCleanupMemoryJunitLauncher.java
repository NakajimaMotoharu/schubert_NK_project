import java.util.Map;

/** Whole original boundary tests, never real Root/ADMIN/Cleanup operations. */
public final class RootBootstrapCleanupMemoryJunitLauncher {
  private RootBootstrapCleanupMemoryJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.file.RootServiceAdmissionScopeTest", 6,
            "dev.codex.schubert.nk.api.bootstrap.BootstrapEntryBoundaryTest", 5,
            "dev.codex.schubert.nk.batch.file.CleanupPreflightTest", 5));
  }
}
