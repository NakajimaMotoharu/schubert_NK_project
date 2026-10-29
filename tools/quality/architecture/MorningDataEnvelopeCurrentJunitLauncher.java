import java.util.Map;

/** Existing whole data-envelope tests; no Root entry, native clock or database fixture instance. */
public final class MorningDataEnvelopeCurrentJunitLauncher {
  private MorningDataEnvelopeCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.file.MorningPrestartEvidenceTest", 5,
            "dev.codex.schubert.nk.batch.file.MorningCompletionEvidenceTest", 11,
            "dev.codex.schubert.nk.batch.file.StoppedBackupCompletionTest", 4));
  }
}
