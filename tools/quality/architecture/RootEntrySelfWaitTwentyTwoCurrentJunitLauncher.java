import java.util.Map;

public final class RootEntrySelfWaitTwentyTwoCurrentJunitLauncher {
  private RootEntrySelfWaitTwentyTwoCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
      "dev.codex.schubert.nk.batch.file.RootServiceLauncherTest", 6,
      "dev.codex.schubert.nk.batch.file.RootStartupPendingTest", 3,
      "dev.codex.schubert.nk.batch.file.RootPendingWaitTest", 12,
      "dev.codex.schubert.nk.batch.file.StartupLaunchBoundaryTest", 1));
  }
}
