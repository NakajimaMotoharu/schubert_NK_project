import java.util.Map;

/** Original independent whole four and one framing boundary, no parent-authentication operation. */
public final class PublicLaunchFiveJunitLauncher {
  private PublicLaunchFiveJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.file.StartupLaunchRecordTest", 4,
        "dev.codex.schubert.nk.batch.file.PublicLaunchFramingBoundaryTest", 1));
  }
}
