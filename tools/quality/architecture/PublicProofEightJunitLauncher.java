import java.util.Map;

/** Public immutable text snapshot only; no operating-system admission or proof emission. */
public final class PublicProofEightJunitLauncher {
  private PublicProofEightJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.bootstrap.StartupProofFrameTest", 8));
  }
}
