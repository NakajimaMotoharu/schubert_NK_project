import java.util.Map;

/** Whole immutable run/activation and fixed diagnostic tests, not runtime admission or stop. */
public final class OriginalBatchRunDiagnosticJunitLauncher {
  private OriginalBatchRunDiagnosticJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.repository.BatchRunValueBoundaryTest", 2,
        "dev.codex.schubert.nk.batch.platform.ExceptionValueContractTest", 1));
  }
}
