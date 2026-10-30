import java.util.Map;

/** Entire immutable Backup manifest value contracts; never performs a Backup. */
public final class OriginalBackupManifestValuesJunitLauncher {
  private OriginalBackupManifestValuesJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.backup.BackupManifestValuesTest", 8));
  }
}
