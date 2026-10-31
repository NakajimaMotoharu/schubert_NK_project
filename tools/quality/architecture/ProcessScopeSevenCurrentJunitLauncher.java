import java.util.Map;
/** Original whole seven; existing fake Process and own threads only. */
public final class ProcessScopeSevenCurrentJunitLauncher {
  private ProcessScopeSevenCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.platform.ProcessResourceScopeTest", 7));
  }
}
