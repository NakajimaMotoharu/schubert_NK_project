import java.util.Map;

/** Original public-config parser and a pinned public template; no service or Root invocation. */
public final class OriginalCaddyConfigThreeJunitLauncher {
  private OriginalCaddyConfigThreeJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of("dev.codex.schubert.nk.batch.file.CaddyPublicConfigurationTest", 3));
  }
}
