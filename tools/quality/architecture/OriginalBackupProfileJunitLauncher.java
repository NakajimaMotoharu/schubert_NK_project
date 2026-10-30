import java.util.Map;

/** Whole public pure claims4, not release/tool authentication or execution. */
public final class OriginalBackupProfileJunitLauncher {
  private OriginalBackupProfileJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.backup.BackupProfileTest", 4));
  }
}
