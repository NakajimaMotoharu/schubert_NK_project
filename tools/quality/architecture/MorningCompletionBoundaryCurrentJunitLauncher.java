import java.util.Map;

/** Whole existing memory boundary tests, not real intent retirement or borrowed DB execution. */
public final class MorningCompletionBoundaryCurrentJunitLauncher {
  private MorningCompletionBoundaryCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.file.MorningCompletionChecksTest", 5,
            "dev.codex.schubert.nk.batch.file.MorningBackupObservedCompletionTest", 2,
            "dev.codex.schubert.nk.batch.file.MorningCompletionRetirementTest", 6));
  }
}
