import java.util.Map;

/** In-memory lifecycle callbacks only; no actual Web or service stop operations. */
public final class WebRuntimeExecutionCurrentJunitLauncher {
  private WebRuntimeExecutionCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of("dev.codex.schubert.nk.web.bootstrap.WebRuntimeExecutionTest", 2));
  }
}
