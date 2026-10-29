import java.util.Map;

/** Existing whole memory tests; no native capture or real service stop. */
public final class ApiWebTerminalStopMemoryJunitLauncher {
  private ApiWebTerminalStopMemoryJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.api.bootstrap.ApiTerminalCaptureTest", 3,
            "dev.codex.schubert.nk.web.bootstrap.WebTerminalCaptureTest", 3,
            "dev.codex.schubert.nk.web.bootstrap.WebRuntimeStopTest", 5));
  }
}
