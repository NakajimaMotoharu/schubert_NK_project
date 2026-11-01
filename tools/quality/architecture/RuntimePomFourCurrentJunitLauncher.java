import java.util.Map;
/** Whole original fixed POM text contracts; no Production Main or external runtime. */
public final class RuntimePomFourCurrentJunitLauncher {
  private RuntimePomFourCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.bootstrap.BatchRuntimeDependencyTest", 3,
        "dev.codex.schubert.nk.web.bootstrap.WebRuntimeDependencyTest", 1));
  }
}
