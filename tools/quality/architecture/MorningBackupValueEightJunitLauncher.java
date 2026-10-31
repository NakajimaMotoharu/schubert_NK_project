import java.util.Map;

/** Unchanged original public catalog and synthetic metadata only, never a Backup operation. */
public final class MorningBackupValueEightJunitLauncher {
  private MorningBackupValueEightJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.file.MorningBackupMetadataTest", 4,
        "dev.codex.schubert.nk.batch.file.MorningBackupCatalogTest", 1,
        "dev.codex.schubert.nk.batch.file.MorningBackupInputModeTest", 3));
  }
}
