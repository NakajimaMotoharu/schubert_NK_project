import java.util.Map;

/** Whole immutable cleanup counts and step values; no cleanup service or SQL execution. */
public final class OriginalBatchCleanupStepJunitLauncher {
  private OriginalBatchCleanupStepJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.repository.CleanupValueBoundaryTest", 2,
        "dev.codex.schubert.nk.batch.repository.CleanupStepValuesTest", 8));
  }
}
