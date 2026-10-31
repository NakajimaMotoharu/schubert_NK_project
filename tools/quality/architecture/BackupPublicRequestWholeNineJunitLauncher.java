import java.util.Map;

/** Original nonsecret request bytes and directory-name values only; no actual Backup. */
public final class BackupPublicRequestWholeNineJunitLauncher {
  private BackupPublicRequestWholeNineJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.platform.BackupWorkerRequestTest", 9));
  }
}
