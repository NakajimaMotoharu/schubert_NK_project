import java.util.Map;

/** Whole original eight immutable value cases; no repository instance or DB is constructed. */
public final class OriginalBatchStepValuesJunitLauncher {
  private OriginalBatchStepValuesJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.repository.BatchStepValuesTest", 8));
  }
}
