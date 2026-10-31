import java.util.Map;

/** Original immutable failure profile and literal state data; no recovery or actual Unit access. */
public final class FailedProfileWholeSixJunitLauncher {
  private FailedProfileWholeSixJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.platform.CleanupFailedBackupRequestTest", 4,
        "dev.codex.schubert.nk.batch.platform.FailedProfileBoundaryTest", 2));
  }
}
