import java.util.Map;

/** Whole original14; no native output/agent/NSS or real process service actions. */
public final class OriginalProfileTerminalJunitLauncher {
  private OriginalProfileTerminalJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.bootstrap.FixedNativeCoverageProfileTest", 5,
        "dev.codex.schubert.nk.bootstrap.TerminalNativeCoverageProfileTest", 4,
        "dev.codex.schubert.nk.bootstrap.FixedNativeCoverageTerminalTest", 5));
  }
}
