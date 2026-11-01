import java.util.Map;
/** SS342/343 SSC193: original public metadata/provider only, never real native export. */
public final class CheckpointPublicProviderTwelveCurrentJunitLauncher {
  private CheckpointPublicProviderTwelveCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.bootstrap.FixedNativeCoverageCheckpointTest", 12));
  }
}
