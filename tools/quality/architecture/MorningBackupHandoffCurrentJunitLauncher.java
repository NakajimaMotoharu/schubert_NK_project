import java.util.Map;

/** Original whole memory backup handoff/completion, never real backup execution. */
public final class MorningBackupHandoffCurrentJunitLauncher {
  private MorningBackupHandoffCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.file.MorningBackupPreparationTest", 6,
            "dev.codex.schubert.nk.batch.file.MorningBackupCompletionTest", 2));
  }
}
