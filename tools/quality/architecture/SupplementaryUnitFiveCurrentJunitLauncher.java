import java.util.Map;

/** Original whole public Unit text tests only; directives are never executed. */
public final class SupplementaryUnitFiveCurrentJunitLauncher {
  private SupplementaryUnitFiveCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of("dev.codex.schubert.nk.batch.platform.SupplementaryUnitTemplateTest", 5));
  }
}
