import java.util.Map;

/** Fixed public identifier catalogs and JDK enum serialization schema, not credential access. */
public final class BootstrapEnumOneJunitLauncher {
  private BootstrapEnumOneJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.file.EnumValueCatalogCompatibilityTest", 1));
  }
}
