import java.util.Map;

/** Whole original child-local ContextHash suite; no synthetic product tests. */
public final class ContextHashCurrentJunitLauncher {
  private ContextHashCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of("dev.codex.schubert.nk.api.security.ContextHashTest", 3));
  }
}
