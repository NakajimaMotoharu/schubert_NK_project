import java.util.Map;
/** Original four public-template source contracts; no Product Main or runtime configuration. */
public final class ConfigSourceFourCurrentJunitLauncher {
  private ConfigSourceFourCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.platform.ConfigurationTemplateContractTest", 4));
  }
}
